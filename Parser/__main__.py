import sys

from . import ParseError, parse_code


def main():
    if len(sys.argv) > 1:
        with open(sys.argv[1], "r") as handle:
            try:
                result = parse_code(handle.read())
                print(result)
                print("Parsing succeeded.")
            except ParseError as error:
                print(error)
    else:
        data = "PROGRAM HELLO\nPRINT *, 'Ola, Mundo!'\nEND"
        try:
            result = parse_code(data)
            print(result)
            print("Parsing succeeded.")
        except ParseError as error:
            print(error)


if __name__ == "__main__":
    main()
