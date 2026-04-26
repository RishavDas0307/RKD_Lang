from .tokens import Token, TT
from .ast_nodes import *


class ParseError(Exception):
    def __init__(self, msg: str, line: int):
        super().__init__(f"[line {line}] Parse error: {msg}")


class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.pos    = 0

    # ── helpers ──────────────────────────────────────────────────────────

    def peek(self) -> Token:
        return self.tokens[self.pos]

    def peek_type(self) -> TT:
        return self.tokens[self.pos].type

    def at_end(self) -> bool:
        return self.peek_type() == TT.EOF

    def advance(self) -> Token:
        t = self.tokens[self.pos]
        if not self.at_end():
            self.pos += 1
        return t

    def eat(self, tt: TT) -> Token:
        t = self.peek()
        if t.type != tt:
            raise ParseError(f"Expected {tt.name}, got {t.type.name!r}", t.line)
        return self.advance()

    def match(self, *types: TT) -> bool:
        if self.peek_type() in types:
            self.advance()
            return True
        return False

    def check(self, *types: TT) -> bool:
        return self.peek_type() in types

    # ── entry point ───────────────────────────────────────────────────────

    def parse(self) -> Program:
        stmts = []
        while not self.at_end():
            stmts.append(self.parse_statement())
        return Program(stmts)

    # ── statements ────────────────────────────────────────────────────────

    def parse_statement(self) -> Node:
        match self.peek_type():
            case TT.LET:    return self.parse_let()
            case TT.RETURN: return self.parse_return()
            case TT.WHILE:  return self.parse_while()
            case TT.FOR:    return self.parse_for()
            case TT.PRINT:  return self.parse_print()
            case _:         return self.parse_expr_stmt()

    def parse_let(self) -> LetStmt:
        self.eat(TT.LET)
        name = self.eat(TT.IDENT).value
        self.eat(TT.ASSIGN)
        val = self.parse_expr()
        self.match(TT.SEMICOLON)
        return LetStmt(name, val)

    def parse_return(self) -> ReturnStmt:
        self.eat(TT.RETURN)
        if self.check(TT.SEMICOLON, TT.RBRACE):
            self.match(TT.SEMICOLON)
            return ReturnStmt(NullLit())
        val = self.parse_expr()
        self.match(TT.SEMICOLON)
        return ReturnStmt(val)

    def parse_while(self) -> WhileStmt:
        self.eat(TT.WHILE)
        cond = self.parse_expr()
        body = self.parse_block()
        return WhileStmt(cond, body)

    def parse_for(self) -> ForStmt:
        self.eat(TT.FOR)
        var = self.eat(TT.IDENT).value
        self.eat(TT.IN)
        iterable = self.parse_expr()
        body = self.parse_block()
        return ForStmt(var, iterable, body)

    def parse_print(self) -> PrintStmt:
        self.eat(TT.PRINT)
        self.eat(TT.LPAREN)
        val = self.parse_expr()
        self.eat(TT.RPAREN)
        self.match(TT.SEMICOLON)
        return PrintStmt(val)

    def parse_expr_stmt(self) -> ExprStmt:
        expr = self.parse_expr()
        self.match(TT.SEMICOLON)
        return ExprStmt(expr)

    # ── block  { stmt* } ─────────────────────────────────────────────────

    def parse_block(self) -> list[Node]:
        self.eat(TT.LBRACE)
        stmts = []
        while not self.check(TT.RBRACE) and not self.at_end():
            stmts.append(self.parse_statement())
        self.eat(TT.RBRACE)
        return stmts

    # ── expressions (precedence climbing) ────────────────────────────────
    #
    #   parse_expr          → assignment (lowest)
    #   parse_logical_or    → ||
    #   parse_logical_and   → &&
    #   parse_equality      → == !=
    #   parse_comparison    → < > <= >=
    #   parse_addition      → + -
    #   parse_term          → * / %
    #   parse_unary         → ! -
    #   parse_call          → postfix () []
    #   parse_primary       → literals, grouping, if, fn, array

    def parse_expr(self) -> Node:
        # Check for assignment: IDENT = expr
        if self.check(TT.IDENT) and self.pos + 1 < len(self.tokens):
            if self.tokens[self.pos + 1].type == TT.ASSIGN:
                name = self.advance().value
                self.advance()              # consume =
                val = self.parse_expr()
                return AssignExpr(name, val)
        return self.parse_logical_or()

    def parse_logical_or(self) -> Node:
        left = self.parse_logical_and()
        while self.check(TT.OR):
            self.advance()
            right = self.parse_logical_and()
            left = LogicalOp("||", left, right)
        return left

    def parse_logical_and(self) -> Node:
        left = self.parse_equality()
        while self.check(TT.AND):
            self.advance()
            right = self.parse_equality()
            left = LogicalOp("&&", left, right)
        return left

    def parse_equality(self) -> Node:
        left = self.parse_comparison()
        while self.check(TT.EQ, TT.NEQ):
            op = self.advance().type
            right = self.parse_comparison()
            left = BinOp("==" if op == TT.EQ else "!=", left, right)
        return left

    def parse_comparison(self) -> Node:
        left = self.parse_addition()
        MAP = {TT.LT: "<", TT.GT: ">", TT.LTE: "<=", TT.GTE: ">="}
        while self.peek_type() in MAP:
            op = MAP[self.advance().type]
            right = self.parse_addition()
            left = BinOp(op, left, right)
        return left

    def parse_addition(self) -> Node:
        left = self.parse_term()
        while self.check(TT.PLUS, TT.MINUS):
            op = "+" if self.advance().type == TT.PLUS else "-"
            right = self.parse_term()
            left = BinOp(op, left, right)
        return left

    def parse_term(self) -> Node:
        left = self.parse_unary()
        MAP = {TT.STAR: "*", TT.SLASH: "/", TT.PERCENT: "%"}
        while self.peek_type() in MAP:
            op = MAP[self.advance().type]
            right = self.parse_unary()
            left = BinOp(op, left, right)
        return left

    def parse_unary(self) -> Node:
        if self.check(TT.BANG):
            self.advance(); return UnaryOp("!", self.parse_unary())
        if self.check(TT.MINUS):
            self.advance(); return UnaryOp("-", self.parse_unary())
        return self.parse_call()

    def parse_call(self) -> Node:
        expr = self.parse_primary()
        while True:
            if self.check(TT.LPAREN):       # function call
                self.advance()
                args = []
                if not self.check(TT.RPAREN):
                    args.append(self.parse_expr())
                    while self.match(TT.COMMA):
                        args.append(self.parse_expr())
                self.eat(TT.RPAREN)
                expr = CallExpr(expr, args)
            elif self.check(TT.LBRACKET):   # index access
                self.advance()
                idx = self.parse_expr()
                self.eat(TT.RBRACKET)
                expr = IndexExpr(expr, idx)
            else:
                break
        return expr

    def parse_primary(self) -> Node:
        t = self.peek()

        match t.type:
            case TT.INT:    self.advance(); return IntLit(t.value)
            case TT.FLOAT:  self.advance(); return FloatLit(t.value)
            case TT.STRING: self.advance(); return StringLit(t.value)
            case TT.TRUE:   self.advance(); return BoolLit(True)
            case TT.FALSE:  self.advance(); return BoolLit(False)
            case TT.NULL:   self.advance(); return NullLit()
            case TT.IDENT:  self.advance(); return Ident(t.value)

            case TT.LPAREN:
                self.advance()
                expr = self.parse_expr()
                self.eat(TT.RPAREN)
                return expr

            case TT.LBRACKET:               # array literal
                self.advance()
                elems = []
                if not self.check(TT.RBRACKET):
                    elems.append(self.parse_expr())
                    while self.match(TT.COMMA):
                        elems.append(self.parse_expr())
                self.eat(TT.RBRACKET)
                return ArrayLit(elems)

            case TT.IF:
                self.advance()
                cond = self.parse_expr()
                then = self.parse_block()
                else_ = []
                if self.check(TT.ELSE):
                    self.advance()
                    else_ = self.parse_block()
                return IfExpr(cond, then, else_)

            case TT.FN:
                self.advance()
                self.eat(TT.LPAREN)
                params = []
                if not self.check(TT.RPAREN):
                    params.append(self.eat(TT.IDENT).value)
                    while self.match(TT.COMMA):
                        params.append(self.eat(TT.IDENT).value)
                self.eat(TT.RPAREN)
                body = self.parse_block()
                return FnExpr(params, body)

            case _:
                raise ParseError(f"Unexpected token: {t.type.name!r}", t.line)