from __future__ import annotations

from typing import TYPE_CHECKING, Any

from lox.error import LoxRuntimeError
from lox.token_type import Token

if TYPE_CHECKING:
    from lox.lox_class import LoxClass


class LoxInstance:
    def __init__(self, klass: LoxClass):
        self.klass = klass
        self.fields: dict[str, Any] = {}

    def __str__(self) -> str:
        return f"{self.klass.name} instance"

    def get(self, name: Token) -> Any:
        if name.lexeme in self.fields:
            return self.fields[name.lexeme]
        method = self.klass.find_method(name.lexeme)
        if method is not None:
            return method.bind(self)
        raise LoxRuntimeError(name, f"Undefined property '{name.lexeme}'.")

    def set(self, name: Token, value: Any):
        self.fields[name.lexeme] = value
