from typing import Any
from abc import abstractmethod, ABC

from lox.interpreter import Interpreter


class LoxCallable(ABC):
    @property
    @abstractmethod
    def arity(self) -> int:
        raise NotImplementedError

    @abstractmethod
    def __call__(self, interpreter: Interpreter, arguments: list[Any]) -> Any:
        raise NotImplementedError
