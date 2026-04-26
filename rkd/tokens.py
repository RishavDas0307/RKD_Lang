from enum import Enum, auto
from dataclasses import dataclass
from typing import Any


class TT(Enum):

    INT        = auto()
    FLOAT      = auto()
    STRING     = auto()
    TRUE       = auto()
    FALSE      = auto()
    NULL       = auto()

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

    PLUS       = auto()
    MINUS      = auto()
    STAR       = auto()
    SLASH      = auto()
    PERCENT    = auto()
    BANG       = auto()
    ASSIGN     = auto()

    EQ         = auto()   
    NEQ        = auto()   
    LT         = auto()
    GT         = auto()
    LTE        = auto()
    GTE        = auto()

    AND        = auto()
    OR         = auto()

    LPAREN     = auto()
    RPAREN     = auto()
    LBRACE     = auto()
    RBRACE     = auto()
    LBRACKET   = auto()
    RBRACKET   = auto()
    COMMA      = auto()
    SEMICOLON  = auto()
    COLON      = auto()
    DOT        = auto()

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
    line: int = 0

    def __repr__(self):
        if self.value is not None:
            return f"Token({self.type.name}, {self.value!r})"
        return f"Token({self.type.name})"