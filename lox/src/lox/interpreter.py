from functools import singledispatchmethod
from typing import Any

import lox.error as error
import lox.expr as expr
import lox.stmt as stmt
from lox.callable import LoxCallable
from lox.environment import Environment
from lox.error import LoxRuntimeError
from lox.lox_class import LoxClass
from lox.lox_function import LoxFunction
from lox.lox_instance import LoxInstance
from lox.native_function import Clock
from lox.return_class import Return
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
    def __init__(self) -> None:
        self.global_env = Environment()
        self.environment = self.global_env
        self.global_env.define("clock", Clock())
        self.locals: dict[int, int] = {}

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
    def _(self, stmt: stmt.Var) -> None:
        value = None
        if stmt.initializer is not None:
            value = self.evaluate(stmt.initializer)
        self.environment.define(stmt.name.lexeme, value)

    @execute.register
    def _(self, stmt: stmt.Expression) -> None:
        self.evaluate(stmt.expression)

    @execute.register
    def _(self, stmt: stmt.Function) -> None:
        function = LoxFunction(stmt, self.environment, False)
        self.environment.define(stmt.name.lexeme, function)

    @execute.register
    def _(self, stmt: stmt.If) -> None:
        if is_truthy(self.evaluate(stmt.condition)):
            self.execute(stmt.then_branch)
        elif stmt.else_branch is not None:
            self.execute(stmt.else_branch)

    @execute.register
    def _(self, stmt: stmt.Print) -> None:
        value = self.evaluate(stmt.expression)
        print(stringify(value))

    @execute.register
    def _(self, stmt: stmt.Return) -> None:
        value = None
        if stmt.value is not None:
            value = self.evaluate(stmt.value)
        raise Return(value)

    @execute.register
    def _(self, stmt: stmt.While) -> None:
        while is_truthy(self.evaluate(stmt.condition)):
            self.execute(stmt.body)

    @execute.register
    def _(self, stmt: stmt.Block) -> None:
        self.execute_block(stmt.statements, Environment(self.environment))

    def execute_block(
        self, statements: list[stmt.Stmt | None], environment: Environment
    ):
        previous = self.environment
        self.environment = environment
        try:
            for statement in statements:
                self.execute(statement)
        finally:
            self.environment = previous

    @execute.register
    def _(self, stmt: stmt.Class):
        superclass = None
        if stmt.superclass is not None:
            superclass = self.evaluate(stmt.superclass)
            if not isinstance(superclass, LoxClass):
                raise LoxRuntimeError(
                    stmt.superclass.name, "Superclass must be a class."
                )
        self.environment.define(stmt.name.lexeme, None)
        if stmt.superclass is not None:
            self.environment = Environment(self.environment)
            self.environment.define("super", superclass)
        methods: dict[str, LoxFunction] = {}
        for method in stmt.methods:
            methods[method.name.lexeme] = LoxFunction(
                method, self.environment, method.name.lexeme == "init"
            )
        klass = LoxClass(stmt.name.lexeme, superclass, methods)
        if superclass is not None:
            self.environment = self.environment.enclosing
        self.environment.assign(stmt.name, klass)

    def resolve(self, expr: expr.Expr, depth: int):
        self.locals[id(expr)] = depth

    @singledispatchmethod
    def evaluate(self, expr: expr.Expr) -> str | float | bool | LoxCallable | None:
        raise NotImplementedError(
            f"Interpreter.evaluate() is not implemented for {type(expr)}"
        )

    @evaluate.register
    def _(self, expr: expr.Assign) -> str | float | bool | LoxCallable | None:
        value = self.evaluate(expr.value)
        distance = self.locals.get(id(expr))
        if distance is not None:
            self.environment.assign_at(distance, expr.name, value)
        else:
            self.global_env.assign(expr.name, value)
        return value

    @evaluate.register
    def _(self, expr: expr.Literal) -> str | float | None:
        return expr.value

    @evaluate.register
    def _(self, expr: expr.Logical) -> str | float | bool | LoxCallable | None:
        left = self.evaluate(expr.left)
        if expr.operator.type == TokenType.OR:
            if is_truthy(left):
                return left
        else:  # TokenType.AND
            if not is_truthy(left):
                return left
        return self.evaluate(expr.right)

    @evaluate.register
    def _(self, expr: expr.Set) -> str | float | bool | LoxCallable | None:
        obj = self.evaluate(expr.obj)
        if not isinstance(obj, LoxInstance):
            raise LoxRuntimeError(expr.name, "Only instances have fields.")
        value = self.evaluate(expr.value)
        obj.set(expr.name, value)
        return value

    @evaluate.register
    def _(self, expr: expr.Super) -> LoxCallable:
        distance = self.locals.get(id(expr))
        superclass = self.environment.get_at(distance, "super")
        obj = self.environment.get_at(distance - 1, "this")
        method = superclass.find_method(expr.method.lexeme)
        if method is None:
            raise LoxRuntimeError(
                expr.method, f"Undefined property '{expr.method.lexeme}'."
            )
        return method.bind(obj)

    @evaluate.register
    def _(self, expr: expr.This) -> LoxInstance:
        return self.lookup_variable(expr.keyword, expr)

    @evaluate.register
    def _(self, expr: expr.Grouping) -> str | float | bool | LoxCallable | None:
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
    def _(self, expr: expr.Variable) -> str | float | bool | LoxCallable | None:
        return self.lookup_variable(expr.name, expr)

    def lookup_variable(self, name: Token, expr: expr.Expr):
        distance = self.locals.get(id(expr))
        if distance is not None:
            return self.environment.get_at(distance, name.lexeme)
        else:
            return self.global_env.get(name)

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

    @evaluate.register
    def _(self, expr: expr.Call) -> str | float | bool | LoxCallable | None:
        callee = self.evaluate(expr.callee)
        arguments: list[Any] = []
        for argument in expr.arguments:
            arguments.append(self.evaluate(argument))
        if not isinstance(callee, LoxCallable):
            raise LoxRuntimeError(expr.paren, "Can only call functions and classes.")
        function = callee
        if len(arguments) != function.arity:
            raise LoxRuntimeError(
                expr.paren,
                f"Expected {function.arity} arguments but got {len(arguments)}",
            )
        return function(self, arguments)

    @evaluate.register
    def _(self, expr: expr.Get) -> str | float | bool | LoxCallable | None:
        obj = self.evaluate(expr.obj)
        if isinstance(obj, LoxInstance):
            return obj.get(expr.name)
        raise LoxRuntimeError(expr.name, "Only instances have properties.")

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
