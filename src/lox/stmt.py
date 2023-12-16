from dataclasses import dataclass

from lox.expr import Expr
from lox.token_type import Token


@dataclass(frozen=True)
class Stmt:
    pass


@dataclass(frozen=True)
class Block(Stmt):
    statements: list[Stmt | None]


@dataclass(frozen=True)
class Expression(Stmt):
    expression: Expr


@dataclass(frozen=True)
class Function(Stmt):
    name: Token
    params: list[Token]
    body: list[Stmt | None]


@dataclass(frozen=True)
class If(Stmt):
    condition: Expr
    then_branch: Stmt
    else_branch: Stmt | None


@dataclass(frozen=True)
class Print(Stmt):
    expression: Expr


@dataclass(frozen=True)
class Return(Stmt):
    keyword: Token
    value: Expr | None


@dataclass(frozen=True)
class While(Stmt):
    condition: Expr
    body: Stmt


@dataclass(frozen=True)
class Var(Stmt):
    name: Token
    initializer: Expr | None
