import sys

from lox.scanner import Scanner
import lox.error as error


def main():
    if len(sys.argv) > 2:
        print("Usage: lox [script]")
        sys.exit(64)
    elif len(sys.argv) == 2:
        run_file(sys.argv[0])
    else:
        run_prompt()


def run_file(path: str):
    with open(path) as f:
        s = f.read()
        run(s)
    if error.had_error:
        sys.exit(65)


def run_prompt():
    while True:
        try:
            s = input("> ")
        except EOFError:
            print("exit")
            break
        if s == "":
            break
        run(s)
        error.had_error = False


def run(source: str):
    scanner = Scanner(source)
    tokens = scanner.scan_tokens()

    for token in tokens:
        print(token)
