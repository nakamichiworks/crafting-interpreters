from typing import Any

from lox.error import LoxRuntimeError
from lox.token_type import Token


class Environment:
    def __init__(self) -> None:
        self.values: dict[str, Any] = {}

    def define(self, name: str, value: Any):
        self.values[name] = value

    def get(self, name: Token):
        if name.lexeme in self.values:
            return self.values[name.lexeme]
        raise LoxRuntimeError(name, f"Undefined variable '{name.lexeme}'.")
