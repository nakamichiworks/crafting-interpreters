"""Lox grammer
program -> declaration* EOF ;
declaration -> varDecl | statement ;
varDecl -> "var" IDENTIFIER ( "=" expression )? ";" ;
statement -> exprStmt | ifStmt | printStmt | block ;
exprStmt -> expression ";" ;
ifStmt -> "if" "(" expression ")" statement ( "else" statement )? ;
printStmt -> "print" expression ";" ;
block -> "{" declaration* "}" ;
expression -> assignment ;
assignment -> IDENTIFIER "=" assignment | logic_or ;
logic_or -> logic_and ( "or" logic_and )* ;
logic_and -> equality ( "and" equality )* ;
equality -> comparison ( ( "!=" | "==" ) comparison )* ;
comparison -> term ( ( ">" | ">=" | "<" | "<=" ) term )* ;
term -> factor ( ( "-" | "+" ) factor )* ;
factor -> unary ( ( "/" | "*" ) unary )* ;
unary -> ( "!" | "-" ) unary | primary ;
primary -> NUMBER | STRING | "true" | "false" | "nil" | "(" expression ")" | IDENTIFIER ;
"""
import lox.error as error
import lox.stmt as stmt
from lox.expr import Assign, Binary, Expr, Grouping, Literal, Logical, Unary, Variable
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
    def parse(self) -> list[stmt.Stmt | None]:
        statements: list[stmt.Stmt | None] = []
        while not self.is_at_end():
            statements.append(self.declaration())
        return statements

    def declaration(self) -> stmt.Stmt | None:
        try:
            if self.match(TokenType.VAR):
                return self.var_declaration()
            return self.statement()
        except ParseError:
            self.synchronize()
            return None

    def var_declaration(self) -> stmt.Var:
        name = self.consume(TokenType.IDENTIFIER, "Expect variable name.")
        initializer = None
        if self.match(TokenType.EQUAL):
            initializer = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after variable declaration.")
        return stmt.Var(name, initializer)

    def statement(self) -> stmt.Stmt:
        if self.match(TokenType.IF):
            return self.if_statement()
        if self.match(TokenType.PRINT):
            return self.print_statement()
        if self.match(TokenType.LEFT_BRACE):
            return stmt.Block(self.block())
        return self.expression_statement()

    def if_statement(self) -> stmt.If:
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'if'.")
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after if condition.")
        then_branch = self.statement()
        else_branch = None
        if self.match(TokenType.ELSE):
            else_branch = self.statement()
        return stmt.If(condition, then_branch, else_branch)

    def print_statement(self) -> stmt.Print:
        value = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after value.")
        return stmt.Print(value)

    def block(self) -> list[stmt.Stmt | None]:
        statements: list[stmt.Stmt | None] = []
        while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end():
            statements.append(self.declaration())
        self.consume(TokenType.RIGHT_BRACE, "Expect '}' after block.")
        return statements

    def expression_statement(self) -> stmt.Expression:
        expr = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after value.")
        return stmt.Expression(expr)

    def expression(self) -> Expr:
        return self.assignment()

    def assignment(self) -> Expr:
        expr = self.logic_or()
        if self.match(TokenType.EQUAL):
            equals = self.previous()
            value = self.assignment()
            if isinstance(expr, Variable):
                name = expr.name
                return Assign(name, value)
            raise self.error(equals, "Invalid assignment target.")
        return expr

    def logic_or(self) -> Expr:
        expr = self.logic_and()
        while self.match(TokenType.OR):
            operator = self.previous()
            right = self.logic_and()
            expr = Logical(expr, operator, right)
        return expr

    def logic_and(self) -> Expr:
        expr = self.equality()
        while self.match(TokenType.AND):
            operator = self.previous()
            right = self.logic_and()
            expr = Logical(expr, operator, right)
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
        if self.match(TokenType.IDENTIFIER):
            return Variable(self.previous())
        if self.match(TokenType.LEFT_PAREN):
            expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expect ')' after expression.")
            return Grouping(expr)
        raise self.error(self.peek(), "Expect expression")
