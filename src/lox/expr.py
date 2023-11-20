# Generated by generate_ast.py
from dataclasses import dataclass

from lox.token_type import Token


@dataclass(frozen=True)
class Expr:
    pass


@dataclass(frozen=True)
class Binary(Expr):
    left: Expr
    operator: Token
    right: Expr


@dataclass(frozen=True)
class Grouping(Expr):
    expression: Expr


@dataclass(frozen=True)
class Literal(Expr):
    value: str | float | None


@dataclass(frozen=True)
class Unary(Expr):
    operator: Token
    right: Expr
