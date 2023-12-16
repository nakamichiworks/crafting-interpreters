from __future__ import annotations

from typing import TYPE_CHECKING, Any

from lox.callable import LoxCallable
from lox.lox_instance import LoxInstance

if TYPE_CHECKING:
    from lox.interpreter import Interpreter


class LoxClass(LoxCallable):
    def __init__(self, name: str) -> None:
        self.name = name

    def __str__(self):
        return self.name

    def __call__(self, interpreter: Interpreter, arguments: list[Any]) -> Any:
        instance = LoxInstance(self)
        return instance

    @property
    def arity(self) -> int:
        return 0
