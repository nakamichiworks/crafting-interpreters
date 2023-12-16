from lox.expr import Binary, Unary, Literal, Grouping
from lox.token_type import Token, TokenType
from lox.ast_printer import print_ast


def test_print_ast():
    expr = Binary(
        left=Unary(
            operator=Token(TokenType.MINUS, "-", None, 1),
            right=Literal(value=123),
        ),
        operator=Token(TokenType.STAR, "*", None, 1),
        right=Grouping(
            expression=Literal(value=45.67),
        ),
    )
    assert print_ast(expr) == "(* (- 123) (group 45.67))"
