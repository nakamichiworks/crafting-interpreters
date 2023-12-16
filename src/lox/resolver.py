from functools import singledispatchmethod

import lox.error as error
import lox.expr as expr
import lox.stmt as stmt
from lox.interpreter import Interpreter
from lox.token_type import Token


class Resolver:
    def __init__(self, interpreter: Interpreter):
        self.interpreter = interpreter
        self.scopes: list[dict[str, bool]] = []

    def resolve(self, statements: list[stmt.Stmt | None]):
        for statement in statements:
            self.visit(statement)

    def resolve_function(self, function: stmt.Function):
        self.begin_scope()
        for param in function.params:
            self.declare(param)
            self.define(param)
        self.resolve(function.body)
        self.end_scope()

    @singledispatchmethod
    def visit(self, stmt: stmt.Stmt | expr.Expr) -> None:
        raise NotImplementedError

    @visit.register
    def _(self, stmt: stmt.Block):
        self.begin_scope()
        self.resolve(stmt.statements)
        self.end_scope()

    @visit.register
    def _(self, stmt: stmt.If):
        self.visit(stmt.condition)
        self.visit(stmt.then_branch)
        if stmt.else_branch is not None:
            self.visit(stmt.else_branch)

    @visit.register
    def _(self, stmt: stmt.Print):
        self.visit(stmt.expression)

    @visit.register
    def _(self, stmt: stmt.Return):
        if stmt.value is not None:
            self.visit(stmt.value)

    @visit.register
    def _(self, stmt: stmt.Expression):
        self.visit(stmt.expression)

    @visit.register
    def _(self, stmt: stmt.Function):
        self.declare(stmt.name)
        self.define(stmt.name)
        self.resolve_function(stmt)

    @visit.register
    def _(self, stmt: stmt.Var):
        self.declare(stmt.name)
        if stmt.initializer is not None:
            self.visit(stmt.initializer)
        self.define(stmt.name)

    @visit.register
    def _(self, stmt: stmt.While):
        self.visit(stmt.condition)
        self.visit(stmt.body)

    @visit.register
    def _(self, expr: expr.Assign):
        self.visit(expr.value)
        self.resolve_local(expr, expr.name)

    @visit.register
    def _(self, expr: expr.Binary):
        self.visit(expr.left)
        self.visit(expr.right)

    @visit.register
    def _(self, expr: expr.Call):
        self.visit(expr.callee)
        for arg in expr.arguments:
            self.visit(arg)

    @visit.register
    def _(self, expr: expr.Grouping):
        self.visit(expr.expression)

    @visit.register
    def _(self, expr: expr.Literal):
        pass

    @visit.register
    def _(self, expr: expr.Logical):
        self.visit(expr.left)
        self.visit(expr.right)

    @visit.register
    def _(self, expr: expr.Unary):
        self.visit(expr.right)

    @visit.register
    def _(self, expr: expr.Variable):
        if self.scopes and self.scopes[-1].get(expr.name.lexeme) is False:
            error.error_token(
                expr.name, "Can't read local variable in its own initializer."
            )
        self.resolve_local(expr, expr.name)

    def begin_scope(self):
        self.scopes.append({})

    def end_scope(self):
        self.scopes.pop()

    def declare(self, name: Token):
        if not self.scopes:
            return
        self.scopes[-1][name.lexeme] = False

    def define(self, name: Token):
        if not self.scopes:
            return
        self.scopes[-1][name.lexeme] = True

    def resolve_local(self, expr: expr.Expr, name: Token):
        for i in reversed(range(len(self.scopes))):
            if name.lexeme in self.scopes[i]:
                self.interpreter.resolve(expr, len(self.scopes) - 1 - i)
