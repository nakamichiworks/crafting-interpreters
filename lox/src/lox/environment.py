from __future__ import annotations

from typing import Any, Self

from lox.error import LoxRuntimeError
from lox.token_type import Token


class Environment:
    def __init__(self, enclosing: Self | None = None) -> None:
        self.enclosing = enclosing
        self.values: dict[str, Any] = {}

    def define(self, name: str, value: Any):
        self.values[name] = value

    def assign(self, name: Token, value: Any):
        if name.lexeme in self.values:
            self.values[name.lexeme] = value
            return
        if self.enclosing is not None:
            self.enclosing.assign(name, value)
            return
        raise LoxRuntimeError(name, f"Undefined variable '{name.lexeme}'.")

    def assign_at(self, distance: int, name: Token, value: Any):
        self.ancestor(distance).values[name.lexeme] = value

    def get(self, name: Token) -> Any:
        if name.lexeme in self.values:
            return self.values[name.lexeme]
        if self.enclosing is not None:
            return self.enclosing.get(name)
        raise LoxRuntimeError(name, f"Undefined variable '{name.lexeme}'.")

    def get_at(self, distance: int, name: str):
        return self.ancestor(distance).values.get(name)

    def ancestor(self, distance: int) -> Environment:
        environment = self
        for _ in range(distance):
            environment = environment.enclosing
        return environment
