from __future__ import annotations

from typing import TYPE_CHECKING, Any

from lox.callable import LoxCallable
from lox.environment import Environment
from lox.return_class import Return
from lox.stmt import Function

if TYPE_CHECKING:
    from lox.interpreter import Interpreter


class LoxFunction(LoxCallable):
    def __init__(self, declaration: Function) -> None:
        self.declaration = declaration

    def __call__(self, interpreter: Interpreter, arguments: list[Any]) -> Any:
        environment = Environment(interpreter.global_env)
        for param, arg in zip(self.declaration.params, arguments):
            environment.define(param.lexeme, arg)
        try:
            interpreter.execute_block(self.declaration.body, environment)
        except Return as r:
            return r.value

    @property
    def arity(self) -> int:
        return len(self.declaration.params)

    def __str__(self) -> str:
        return f"<fn {self.declaration.name.lexeme}>"
