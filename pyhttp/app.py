from __future__ import annotations
from io import TextIOWrapper
import os
import socket
import threading
from typing import Generic, TypeVar

T = TypeVar("T")



class HttpMethods:
    GET = "GET"

class ListNode(Generic[T]):
    def __init__(self, val: T, next: ListNode[T]|None):
        self.val = val
        self.next = next

class Stack(Generic[T]):
    def __init__(self) -> None:
        self._stack: ListNode[T]|None = None

    def push(self, val: T) -> None:
        self._stack = ListNode(val, self._stack)

    def pop(self) -> T:
        if self._stack is None:
            raise RuntimeError("Stack is empty")
        else:
            val: T = self._stack.val
            self._stack = self._stack.next
            return val



def handle_connection(conn: socket.socket, source_addr: str, source_port: int, directory_root: str) -> None:
    handle_http_req(conn, directory_root)
    conn.close()


def handle_http_req(conn: socket.socket, directory_root: str) -> None:
    MAX_MSG_SIZE: int = 8192 # 8192 bytes
    encoded_msg: bytes = conn.recv(MAX_MSG_SIZE)
    decoded_msg: str = encoded_msg.decode()

    lines: list[str] = decoded_msg.split("\r\n")

    if len(lines) == 0:
        return

    request_header: list[str] = lines[0].split(" ")

    if len(request_header) != 3:
        return

    request_method: str = request_header[0]
    request_uri: str = request_header[1]
    request_version: str = request_header[2]

    data: bytes
    if request_method == HttpMethods.GET:
        data = handle_get(request_uri, directory_root)
    else:
        data = not_found()

    conn.send(data)


def handle_get(request_uri: str, directory_root: str) -> bytes:
    data: tuple[str, str]|None = read_file(request_uri, directory_root)
    if data is None:
        return not_found()
    
    file_str, file_extension = data
    return ok(file_str, file_extension)


def read_file(uri: str, directory_root: str) -> tuple[str, str]|None:
    # check that the path stays within http root
    stack: Stack[str] = Stack()
    try:
        for string in uri.split("/"):
            if string == "." or string == "":
                continue
            elif string == "..":
                stack.pop()
            else:
                stack.push(string)
    except RuntimeError:
        return None

    path: str = directory_root + uri

    if not os.path.exists(path):
        return None

    if os.path.isdir(path):
        return read_file(uri + "/index.html", directory_root)

    file_extension: str
    file: TextIOWrapper = open(path, "r")
    result: str = "".join(file.readlines())
    _, file_extension = os.path.splitext("./" + uri)
    file.close()

    return (result, file_extension)

def ok(data: str, file_extension: str) -> bytes:
    content_types: dict[str, str] = {
        ".html": "text/html",
        ".css": "text/css",
        ".js": "text/javascript",
        ".txt": "text/plain",
        ".gif": "image/gif",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".mp3": "audio/mpeg",
        ".mp4": "video/mp4",
        "": "text/plain",
        ".xml": "application/xml",
        ".json": "application/json",
    }

    response_header: bytes = b"HTTP/1.1 200 OK\r\n"
    content_type: bytes = f"Content-Type: {content_types.get(file_extension, 'text/plain')}\r\n".encode()

    body: bytes = data.encode()
    content_length: bytes = f"Content-Length: {len(body)}\r\n\r\n".encode()

    response: bytes = response_header + content_type + content_length + body
    return response


def not_found() -> bytes:
    response_header: bytes = b"HTTP/1.1 404 File not found\r\n"
    content_type: bytes = b"Content-Type: text/html; charset=UTF-8\r\n"
    body: bytes = b"<h1>404 NOT FOUND</h1>"
    content_length: bytes = (f"Content-Length: {len(body)}\r\n\r\n").encode()

    return response_header + content_type + content_length + body


def run(listen_addr: str, listen_port: int, directory_root: str) -> None:
    print(f"Listening on {listen_addr}:{listen_port}")
    print(f"Serving files at '{os.path.abspath(directory_root)}'")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((listen_addr, listen_port))
    server.listen()

    try:
        while True:
            conn, client = server.accept()
            thread = threading.Thread(target=handle_connection, args=(conn, client[0], client[1], directory_root))
            thread.start()
            print(f"Received request from {client[0]}:{client[1]}")
    except KeyboardInterrupt:
        server.close()


if __name__ == "__main__":
    run("127.0.0.1", 3000, ".")
