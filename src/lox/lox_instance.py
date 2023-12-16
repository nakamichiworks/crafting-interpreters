from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lox.lox_class import LoxClass


class LoxInstance:
    def __init__(self, klass: LoxClass):
        self.klass = klass

    def __str__(self) -> str:
        return f"{self.klass.name} instance"
