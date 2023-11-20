from functools import singledispatch

import lox.expr as expr


@singledispatch
def print_ast(expr: expr.Expr):
    raise NotImplementedError(f"print_ast() is not implemented for {type(expr)}")


@print_ast.register
def _(expr: expr.Binary):
    return f"({expr.operator.lexeme} {print_ast(expr.left)} {print_ast(expr.right)})"


@print_ast.register
def _(expr: expr.Grouping):
    return f"(group {print_ast(expr.expression)})"


@print_ast.register
def _(expr: expr.Literal):
    if expr.value is None:
        return "nil"
    else:
        return f"{expr.value}"


@print_ast.register
def _(expr: expr.Unary):
    return f"({expr.operator.lexeme} {print_ast(expr.right)})"
