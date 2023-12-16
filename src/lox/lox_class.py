from __future__ import annotations

from typing import TYPE_CHECKING, Any

from lox.callable import LoxCallable
from lox.lox_function import LoxFunction
from lox.lox_instance import LoxInstance

if TYPE_CHECKING:
    from lox.interpreter import Interpreter


class LoxClass(LoxCallable):
    def __init__(self, name: str, methods: dict[str, LoxFunction]) -> None:
        self.name = name
        self.methods = methods

    def __str__(self):
        return self.name

    def __call__(self, interpreter: Interpreter, arguments: list[Any]) -> Any:
        instance = LoxInstance(self)
        initializer = self.find_method("init")
        if initializer is not None:
            initializer.bind(instance)(interpreter, arguments)
        return instance

    @property
    def arity(self) -> int:
        initializer = self.find_method("init")
        return initializer.arity if initializer is not None else 0

    def find_method(self, name: str) -> LoxFunction | None:
        return self.methods.get(name)
