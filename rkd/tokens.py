from enum import Enum, auto
from dataclasses import dataclass
from typing import Any


class TT(Enum):
    # Literals
    INT        = auto()
    FLOAT      = auto()
    STRING     = auto()
    TRUE       = auto()
    FALSE      = auto()
    NULL       = auto()

    # Identifiers & keywords
    IDENT      = auto()
    LET        = auto()
    FN         = auto()
    RETURN     = auto()
    IF         = auto()
    ELSE       = auto()
    WHILE      = auto()
    FOR        = auto()
    IN         = auto()
    PRINT      = auto()

    # Operators
    PLUS       = auto()
    MINUS      = auto()
    STAR       = auto()
    SLASH      = auto()
    PERCENT    = auto()
    BANG       = auto()
    ASSIGN     = auto()

    # Comparison
    EQ         = auto()   # ==
    NEQ        = auto()   # !=
    LT         = auto()   # <
    GT         = auto()   # >
    LTE        = auto()   # <=
    GTE        = auto()   # >=

    # Logical
    AND        = auto()   # &&
    OR         = auto()   # ||

    # Delimiters
    LPAREN     = auto()   # (
    RPAREN     = auto()   # )
    LBRACE     = auto()   # {
    RBRACE     = auto()   # }
    LBRACKET   = auto()   # [
    RBRACKET   = auto()   # ]
    COMMA      = auto()   # ,
    SEMICOLON  = auto()   # ;
    COLON      = auto()   # :
    DOT        = auto()   # .

    # Control
    EOF        = auto()
    ILLEGAL    = auto()


KEYWORDS: dict[str, TT] = {
    "let":    TT.LET,
    "fn":     TT.FN,
    "return": TT.RETURN,
    "if":     TT.IF,
    "else":   TT.ELSE,
    "while":  TT.WHILE,
    "for":    TT.FOR,
    "in":     TT.IN,
    "true":   TT.TRUE,
    "false":  TT.FALSE,
    "null":   TT.NULL,
    "print":  TT.PRINT,
}


@dataclass
class Token:
    type: TT
    value: Any = None
    line: int = 0       # for error messages later

    def __repr__(self):
        if self.value is not None:
            return f"Token({self.type.name}, {self.value!r})"
        return f"Token({self.type.name})"