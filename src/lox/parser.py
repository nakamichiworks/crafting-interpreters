"""Lox grammer
expression -> comma;
comma -> ternary ( ( "," ) ternary )*;
ternary -> equality "?" ternary ":" ternary | equality
equality -> comparison ( ( "!=" | "==" ) comparison )*;
comparison -> term ( ( ">" | ">=" | "<" | "<=" ) term )*;
term -> factor ( ( "-" | "+" ) factor )*;
factor -> unary ( ( "/" | "*" ) unary )*;
unary -> ( "!" | "-" ) unary | primary;
primary -> NUMBER | STRING | "true" | "false" | "nil" | "(" expression ")";
"""
import lox.error as error
from lox.expr import Binary, Expr, Grouping, Literal, Ternary, Unary
from lox.token_type import Token, TokenType


class ParseError(Exception):
    pass


class Parser:
    def __init__(self, tokens: list[Token]) -> None:
        self.tokens = tokens
        self.current = 0

    # utility methods
    def is_at_end(self) -> bool:
        return self.peek().type == TokenType.EOF

    def peek(self) -> Token:
        return self.tokens[self.current]

    def previous(self) -> Token:
        return self.tokens[self.current - 1]

    def advance(self) -> Token:
        if not self.is_at_end():
            self.current += 1
        return self.previous()

    def check(self, typ: TokenType) -> bool:
        if self.is_at_end():
            return False
        return self.peek().type == typ

    def match(self, *types: *tuple[TokenType, ...]) -> bool:
        for typ in types:
            if self.check(typ):
                self.advance()
                return True
        return False

    def consume(self, typ: TokenType, message: str):
        if self.check(typ):
            return self.advance()
        raise self.error(self.peek(), message)

    def error(self, token: Token, message: str) -> ParseError:
        error.error_token(token, message)
        return ParseError(message)

    def synchronize(self):
        self.advance()
        while not self.is_at_end():
            if self.previous().type == TokenType.SEMICOLON:
                return
            if self.peek().type in (
                TokenType.CLASS,
                TokenType.FOR,
                TokenType.FUN,
                TokenType.IF,
                TokenType.PRINT,
                TokenType.RETURN,
                TokenType.VAR,
                TokenType.WHILE,
            ):
                return
        self.advance()

    # parsing methods
    def parse(self) -> Expr | None:
        try:
            return self.expression()
        except ParseError:
            return

    def expression(self) -> Expr:
        return self.comma()

    def comma(self) -> Expr:
        expr = self.ternary()
        while self.match(TokenType.COMMA):
            operator = self.previous()
            right = self.ternary()
            expr = Binary(expr, operator, right)
        return expr

    def ternary(self) -> Expr:
        expr = self.equality()
        if self.match(TokenType.QUESTION):
            operator1 = self.previous()
            middle = self.ternary()
            self.consume(TokenType.COLON, "Expect ':' for ternary operator")
            operator2 = self.previous()
            right = self.ternary()
            expr = Ternary(expr, operator1, middle, operator2, right)
        return expr

    def equality(self) -> Expr:
        expr = self.comparison()
        while self.match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            operator = self.previous()
            right = self.comparison()
            expr = Binary(expr, operator, right)
        return expr

    def comparison(self) -> Expr:
        expr = self.term()
        while self.match(
            TokenType.GREATER,
            TokenType.GREATER_EQUAL,
            TokenType.LESS,
            TokenType.LESS_EQUAL,
        ):
            operator = self.previous()
            right = self.term()
            expr = Binary(expr, operator, right)
        return expr

    def term(self) -> Expr:
        expr = self.factor()
        while self.match(TokenType.PLUS, TokenType.MINUS):
            operator = self.previous()
            right = self.factor()
            expr = Binary(expr, operator, right)
        return expr

    def factor(self) -> Expr:
        expr = self.unary()
        while self.match(TokenType.SLASH, TokenType.STAR):
            operator = self.previous()
            right = self.unary()
            expr = Binary(expr, operator, right)
        return expr

    def unary(self) -> Expr:
        if self.match(TokenType.BANG, TokenType.MINUS):
            operator = self.previous()
            right = self.unary()
            return Unary(operator, right)
        return self.primary()

    def primary(self) -> Expr:
        if self.match(TokenType.FALSE):
            return Literal(False)
        if self.match(TokenType.TRUE):
            return Literal(True)
        if self.match(TokenType.NIL):
            return Literal(None)
        if self.match(TokenType.NUMBER, TokenType.STRING):
            return Literal(self.previous().literal)
        if self.match(TokenType.LEFT_PAREN):
            expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expect ')' after expression.")
            return Grouping(expr)
        raise self.error(self.peek(), "Expect expression")
