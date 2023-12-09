from lox.token_type import Token, TokenType

had_error = False
had_runtime_error = False


class LoxRuntimeError(Exception):
    def __init__(self, token: Token, *args: object) -> None:
        super().__init__(*args)
        self.token = token


def report(line: int, where: str, message: str):
    print(f"[line {line}] Error{where}: {message}")
    global had_error
    had_error = True


def error(line: int, message: str):
    report(line, "", message)


def error_token(token: Token, message: str):
    if token.type == TokenType.EOF:
        report(token.line, " at end", message)
    else:
        report(token.line, f" at '{token.lexeme}'", message)


def error_runtime(error: LoxRuntimeError):
    print(f"{error.args[0]}\n[line {error.token.line}]")
    global had_runtime_error
    had_runtime_error = True
