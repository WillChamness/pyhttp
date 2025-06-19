# PyHTTP

A simple HTTP server written in Python with no external dependencies

## Usage

```
usage: pyhttp [-h] [-b ADDRESS] [-d DIRECTORY] [port]

positional arguments:
  port                  specify alternate port (default 8000)

options:
  -h, --help            show this help message and exit
  -b ADDRESS, --bind ADDRESS
                        specify alternate bind address (default: all interfaces)
  -d DIRECTORY, --directory DIRECTORY
                        specify alternate directory (default: current directory)
```

## Linux Systemd Example Service File

Assuming this repository was cloned to `/usr/local/bin/` and you want to serve files at `/var/www/html/`,
create `/etc/systemd/system/pyhttp.service` and add the following lines:

```
[Unit]
Description=PyHTTP Server
After=multi-user.target

[Service]
Type=simple
WorkingDirectory=/usr/local/bin/pyhttp
ExecStart=/usr/bin/python3 -m pyhttp 8080 --bind 127.0.0.1 --directory /var/www/html

[Install]
WantedBy=multi-user.target
```

Note that some distributions name the Python executable `python` instead of `python3`.

## Known Limitations

1. Sending large files
    - This implementation loads the entire file into memory before sending it out. For multi-gigabyte files, this approach is unrealistic.
    - A better approach is to send the file in 1024 byte chunks.
2. Keeping connections alive
    - Browsers will often send a `Keep-Alive` request in the HTTP header. This implementation ignores this request and closes the connection after sending data.
3. Most MIME types will be reported incorrectly
    - This implementation only reports a small subsection of the different MIME types.
    - By default, it will report `text/plain` if the server encounters an unknown type.
