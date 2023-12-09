from dataclasses import dataclass

from lox.expr import Expr


@dataclass(frozen=True)
class Stmt:
    pass


@dataclass(frozen=True)
class Expression(Stmt):
    expression: Expr


@dataclass(frozen=True)
class Print(Stmt):
    expression: Expr
