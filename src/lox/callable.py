from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from lox.interpreter import Interpreter


class LoxCallable(ABC):
    @property
    @abstractmethod
    def arity(self) -> int:
        raise NotImplementedError

    @abstractmethod
    def __call__(self, interpreter: Interpreter, arguments: list[Any]) -> Any:
        raise NotImplementedError
