import argparse
from pyhttp import app

def parse_args() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument("port", type=int, nargs="?", default=8000, help="specify alternate port (default 8000)")
    parser.add_argument("-b", "--bind", type=str, required=False, default="0.0.0.0", metavar="ADDRESS", help="specify alternate bind address (default: all interfaces)")

    args = parser.parse_args()

    if args.port < 0 or 2**16 - 1 < args.port:
        print(f"Port must be between 0 and {2**16 - 1}")
        exit(1)

    octets: list[str] = args.bind.split(".")
    if len(octets) != 4:
        print("Bind address must be a valid IPv4 address")
        exit(1)

    for octet in octets:
        try:
            byte = int(octet)
            if byte < 0 or 255 < byte:
                raise ValueError()
        except ValueError:
            print("Bind address must be a valid IPv4 address")
            exit(1)

    app.run(args.bind, args.port)



if __name__ == "__main__":
    parse_args()
