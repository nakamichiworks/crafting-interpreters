from functools import singledispatchmethod
from typing import Any

import lox.error as error
import lox.expr as expr
import lox.stmt as stmt
from lox.error import LoxRuntimeError
from lox.token_type import Token, TokenType


def is_truthy(object: Any) -> bool:
    if object is None:
        return False
    if isinstance(object, bool):
        return bool(object)
    return True


def is_equal(a: Any, b: Any) -> bool:
    if a is None and b is None:
        return True
    if a is None:
        return False
    return a == b


def stringify(object: Any) -> str:
    if object is None:
        return "nil"
    if isinstance(object, int | float):
        text = str(object)
        if text.endswith(".0"):
            text = str(int(object))
        return text
    return str(object)


class Interpreter:
    def interpret(self, statements: list[stmt.Stmt]):
        try:
            for statement in statements:
                self.execute(statement)
        except LoxRuntimeError as e:
            error.error_runtime(e)

    @singledispatchmethod
    def execute(self, stmt: stmt.Stmt) -> None:
        raise NotImplementedError(
            f"Interpreter.execute() is not implemented for {type(stmt)}"
        )

    @execute.register
    def _(self, stmt: stmt.Expression) -> None:
        self.evaluate(stmt.expression)

    @execute.register
    def _(self, stmt: stmt.Print) -> None:
        value = self.evaluate(stmt.expression)
        print(stringify(value))

    @singledispatchmethod
    def evaluate(self, expr: expr.Expr) -> str | float | bool | None:
        raise NotImplementedError(
            f"Interpreter.evaluate() is not implemented for {type(expr)}"
        )

    @evaluate.register
    def _(self, expr: expr.Literal) -> str | float | None:
        return expr.value

    @evaluate.register
    def _(self, expr: expr.Grouping) -> str | float | bool | None:
        return self.evaluate(expr.expression)

    @evaluate.register
    def _(self, expr: expr.Unary) -> float | bool:
        right = self.evaluate(expr.right)
        match expr.operator.type:
            case TokenType.MINUS:
                self.check_number_operand(expr.operator, right)
                return -right
            case TokenType.BANG:
                return not is_truthy(right)
            case _:
                raise Exception("Must not be reached")

    @evaluate.register
    def _(self, expr: expr.Binary) -> str | float | bool | None:
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)
        match expr.operator.type:
            case TokenType.BANG_EQUAL:
                return not is_equal(left, right)
            case TokenType.EQUAL_EQUAL:
                return is_equal(left, right)
            case TokenType.GREATER:
                self.check_number_operands(expr.operator, left, right)
                return left > right
            case TokenType.GREATER_EQUAL:
                self.check_number_operands(expr.operator, left, right)
                return left >= right
            case TokenType.LESS:
                self.check_number_operands(expr.operator, left, right)
                return left < right
            case TokenType.LESS_EQUAL:
                self.check_number_operands(expr.operator, left, right)
                return left <= right
            case TokenType.MINUS:
                self.check_number_operands(expr.operator, left, right)
                return left - right
            case TokenType.PLUS:
                self.check_number_or_string_operands(expr.operator, left, right)
                return left + right
            case TokenType.SLASH:
                self.check_number_operands(expr.operator, left, right)
                return left / right
            case TokenType.STAR:
                self.check_number_operands(expr.operator, left, right)
                return left * right
            case _:
                raise Exception("Must not be reached")

    # utility methods
    def check_number_operand(self, operator: Token, operand: Any):
        if isinstance(operand, int | float):
            return
        raise LoxRuntimeError(operator, "Operand must be a number.")

    def check_number_operands(self, operator: Token, left: Any, right: Any):
        if isinstance(left, int | float) and isinstance(right, int | float):
            return
        raise LoxRuntimeError(operator, "Operands must be numbers.")

    def check_number_or_string_operands(self, operator: Token, left: Any, right: Any):
        if isinstance(left, int | float) and isinstance(right, int | float):
            return
        if isinstance(left, str) and isinstance(right, str):
            return
        raise LoxRuntimeError(operator, "Operands must be two numbers or two strings.")
