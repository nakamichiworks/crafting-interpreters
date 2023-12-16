import sys

import lox.error as error
from lox.interpreter import Interpreter
from lox.parser import Parser
from lox.resolver import Resolver
from lox.scanner import Scanner


def main():
    lox = Lox()
    if len(sys.argv) > 2:
        print("Usage: lox [script]")
        sys.exit(64)
    elif len(sys.argv) == 2:
        lox.run_file(sys.argv[1])
    else:
        lox.run_prompt()


class Lox:
    def __init__(self):
        self.interpreter = Interpreter()
        self.resolver = Resolver(self.interpreter)
        error.had_error = False
        error.had_runtime_error = False

    def run_file(self, path: str):
        with open(path) as f:
            s = f.read()
            self.run(s)
        if error.had_error:
            sys.exit(65)
        if error.had_runtime_error:
            sys.exit(70)

    def run_prompt(self):
        while True:
            try:
                s = input("> ")
            except EOFError:
                print("exit")
                break
            if s == "":
                break
            self.run(s)
            error.had_error = False

    def run(self, source: str):
        scanner = Scanner(source)
        tokens = scanner.scan_tokens()
        parser = Parser(tokens)
        statements = parser.parse()
        if error.had_error:
            return
        self.resolver.resolve(statements)
        if error.had_error:
            return
        self.interpreter.interpret(statements)
