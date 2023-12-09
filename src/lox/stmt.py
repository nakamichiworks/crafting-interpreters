from dataclasses import dataclass

from lox.expr import Expr
from lox.token_type import Token


@dataclass(frozen=True)
class Stmt:
    pass


@dataclass(frozen=True)
class Expression(Stmt):
    expression: Expr


@dataclass(frozen=True)
class Print(Stmt):
    expression: Expr


@dataclass(frozen=True)
class Var(Stmt):
    name: Token
    initializer: Expr | None
