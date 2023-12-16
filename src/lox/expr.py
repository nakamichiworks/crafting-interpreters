# Generated by generate_ast.py
from dataclasses import dataclass

from lox.token_type import Token


@dataclass(frozen=True)
class Expr:
    pass


@dataclass(frozen=True)
class Assign(Expr):
    name: Token
    value: Expr


@dataclass(frozen=True)
class Binary(Expr):
    left: Expr
    operator: Token
    right: Expr


@dataclass(frozen=True)
class Call(Expr):
    callee: Expr
    paren: Token
    arguments: list[Expr]


@dataclass(frozen=True)
class Get(Expr):
    obj: Expr
    name: Token


@dataclass(frozen=True)
class Grouping(Expr):
    expression: Expr


@dataclass(frozen=True)
class Literal(Expr):
    value: str | float | bool | None


@dataclass(frozen=True)
class Logical(Expr):
    left: Expr
    operator: Token
    right: Expr


@dataclass(frozen=True)
class Set(Expr):
    obj: Expr
    name: Token
    value: Expr


@dataclass(frozen=True)
class Unary(Expr):
    operator: Token
    right: Expr


@dataclass(frozen=True)
class Variable(Expr):
    name: Token
