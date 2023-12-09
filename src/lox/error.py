from lox.token_type import Token, TokenType

had_error = False


def error(line: int, message: str):
    report(line, "", message)


def error_token(token: Token, message: str):
    if token.type == TokenType.EOF:
        report(token.line, " at end", message)
    else:
        report(token.line, f" at '{token.lexeme}'", message)


def report(line: int, where: str, message: str):
    print(f"[line {line}] Error{where}: {message}")
    global had_error
    had_error = True
