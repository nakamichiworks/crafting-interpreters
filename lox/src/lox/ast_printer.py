from functools import singledispatch

import lox.expr as expr


@singledispatch
def print_ast(expr: expr.Expr) -> str:
    raise NotImplementedError(f"print_ast() is not implemented for {type(expr)}")


@print_ast.register
def _(expr: expr.Binary) -> str:
    return f"({expr.operator.lexeme} {print_ast(expr.left)} {print_ast(expr.right)})"


@print_ast.register
def _(expr: expr.Grouping) -> str:
    return f"(group {print_ast(expr.expression)})"


@print_ast.register
def _(expr: expr.Literal) -> str:
    if expr.value is None:
        return "nil"
    else:
        return f"{expr.value}"


@print_ast.register
def _(expr: expr.Unary) -> str:
    return f"({expr.operator.lexeme} {print_ast(expr.right)})"
