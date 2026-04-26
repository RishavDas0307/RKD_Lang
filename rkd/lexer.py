from .tokens import Token, TT, KEYWORDS


class LexError(Exception):
    def __init__(self, msg: str, line: int):
        super().__init__(f"[line {line}] Lex error: {msg}")


class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.pos    = 0
        self.line   = 1

    def at_end(self) -> bool:
        return self.pos >= len(self.source)

    def peek(self, offset: int = 0) -> str:
        idx = self.pos + offset
        return self.source[idx] if idx < len(self.source) else "\0"

    def advance(self) -> str:
        ch = self.source[self.pos]
        self.pos += 1
        if ch == "\n":
            self.line += 1
        return ch

    def match(self, expected: str) -> bool:
        """Consume next char if it matches; return True if it did."""
        if self.at_end() or self.peek() != expected:
            return False
        self.advance()
        return True

    def skip_whitespace_and_comments(self):
        while not self.at_end():
            ch = self.peek()
            if ch in " \t\r\n":
                self.advance()
            elif ch == "#":
                while not self.at_end() and self.peek() != "\n":
                    self.advance()
            else:
                break

    # ── readers ──────────────────────────────────────────────────────────

    def read_number(self) -> Token:
        start = self.pos
        line  = self.line
        while self.peek().isdigit():
            self.advance()
        if self.peek() == "." and self.peek(1).isdigit():
            self.advance()
            while self.peek().isdigit():
                self.advance()
            return Token(TT.FLOAT, float(self.source[start:self.pos]), line)
        return Token(TT.INT, int(self.source[start:self.pos]), line)

    def read_string(self) -> Token:
        line = self.line
        result = []
        while not self.at_end() and self.peek() != '"':
            ch = self.advance()
            if ch == "\\":
                esc = self.advance()
                result.append({"n": "\n", "t": "\t", '"': '"',
                               "\\": "\\"}.get(esc, esc))
            else:
                result.append(ch)
        if self.at_end():
            raise LexError("Unterminated string", line)
        self.advance()
        return Token(TT.STRING, "".join(result), line)

    def read_ident(self) -> Token:
        start = self.pos
        line  = self.line
        while self.peek().isalnum() or self.peek() == "_":
            self.advance()
        word = self.source[start:self.pos]
        tt   = KEYWORDS.get(word, TT.IDENT)
        val  = word if tt == TT.IDENT else None
        return Token(tt, val, line)


    def tokenize(self) -> list[Token]:
        tokens: list[Token] = []

        while True:
            self.skip_whitespace_and_comments()
            if self.at_end():
                tokens.append(Token(TT.EOF, None, self.line))
                break

            line = self.line
            ch   = self.advance()

            SIMPLE = {
                "+": TT.PLUS,  "-": TT.MINUS, "*": TT.STAR,
                "%": TT.PERCENT, "(": TT.LPAREN, ")": TT.RPAREN,
                "{": TT.LBRACE, "}": TT.RBRACE, "[": TT.LBRACKET,
                "]": TT.RBRACKET, ",": TT.COMMA, ";": TT.SEMICOLON,
                ":": TT.COLON, ".": TT.DOT,
            }
            if ch in SIMPLE:
                tokens.append(Token(SIMPLE[ch], None, line))
                continue

            if ch == "!":
                tokens.append(Token(TT.NEQ if self.match("=") else TT.BANG, None, line))
            elif ch == "=":
                tokens.append(Token(TT.EQ  if self.match("=") else TT.ASSIGN, None, line))
            elif ch == "<":
                tokens.append(Token(TT.LTE if self.match("=") else TT.LT, None, line))
            elif ch == ">":
                tokens.append(Token(TT.GTE if self.match("=") else TT.GT, None, line))
            elif ch == "&":
                if self.match("&"):
                    tokens.append(Token(TT.AND, None, line))
                else:
                    raise LexError("Expected '&&'", line)
            elif ch == "|":
                if self.match("|"):
                    tokens.append(Token(TT.OR, None, line))
                else:
                    raise LexError("Expected '||'", line)
            elif ch == "/":
                tokens.append(Token(TT.SLASH, None, line))

            # Literals
            elif ch == '"':
                tokens.append(self.read_string())
            elif ch.isdigit():
                self.pos -= 1
                tokens.append(self.read_number())
            elif ch.isalpha() or ch == "_":
                self.pos -= 1
                tokens.append(self.read_ident())
            else:
                raise LexError(f"Unexpected character: {ch!r}", line)

        return tokens