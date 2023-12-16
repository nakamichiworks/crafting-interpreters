import sys

import lox.error as error
from lox.interpreter import Interpreter
from lox.parser import Parser
from lox.resolver import Resolver
from lox.scanner import Scanner


def main():
    if len(sys.argv) > 2:
        print("Usage: lox [script]")
        sys.exit(64)
    elif len(sys.argv) == 2:
        run_file(sys.argv[1])
    else:
        run_prompt()


def run_file(path: str):
    with open(path) as f:
        s = f.read()
        run(s)
    if error.had_error:
        sys.exit(65)
    if error.had_runtime_error:
        sys.exit(70)


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


interpreter = Interpreter()
resolver = Resolver(interpreter)


def run(source: str):
    scanner = Scanner(source)
    tokens = scanner.scan_tokens()
    parser = Parser(tokens)
    statements = parser.parse()
    if error.had_error:
        return
    resolver.resolve(statements)
    if error.had_error:
        return
    interpreter.interpret(statements)
