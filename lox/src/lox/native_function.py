from __future__ import annotations

import time
from typing import TYPE_CHECKING, Any

from lox.callable import LoxCallable

if TYPE_CHECKING:
    from lox.interpreter import Interpreter


class Clock(LoxCallable):
    @property
    def arity(self):
        return 0

    def __call__(
        self,
        interpreter: Interpreter,
        arguments: list[Any],
    ) -> float:
        return time.time()

    def __str__(self) -> str:
        return "<native fn>"
