from __future__ import annotations

from typing import TYPE_CHECKING, Any

from lox.callable import LoxCallable
from lox.environment import Environment
from lox.lox_instance import LoxInstance
from lox.return_class import Return
from lox.stmt import Function

if TYPE_CHECKING:
    from lox.interpreter import Interpreter


class LoxFunction(LoxCallable):
    def __init__(
        self, declaration: Function, closure: Environment, is_initializer: bool
    ) -> None:
        self.declaration = declaration
        self.closure = closure
        self.is_initializer = is_initializer

    def __call__(self, interpreter: Interpreter, arguments: list[Any]) -> Any:
        environment = Environment(self.closure)
        for param, arg in zip(self.declaration.params, arguments):
            environment.define(param.lexeme, arg)
        try:
            interpreter.execute_block(self.declaration.body, environment)
        except Return as r:
            if self.is_initializer:
                return self.closure.get_at(0, "this")
            return r.value

        if self.is_initializer:
            return self.closure.get_at(0, "this")

    def bind(self, instance: LoxInstance) -> LoxFunction:
        environment = Environment(self.closure)
        environment.define("this", instance)
        return LoxFunction(self.declaration, environment, self.is_initializer)

    @property
    def arity(self) -> int:
        return len(self.declaration.params)

    def __str__(self) -> str:
        return f"<fn {self.declaration.name.lexeme}>"
