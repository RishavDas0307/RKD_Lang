"""
AST node definitions for RKD_Lang.

Every node is a frozen dataclass so they're hashable and easy to print.
Nodes are split into:
  - Statements  (don't produce a value: let, return, while, for)
  - Expressions (produce a value: literals, binop, call, if, fn, ...)
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Any



class Node:
    """Marker base class for all AST nodes."""




@dataclass
class IntLit:
    value: int

@dataclass
class FloatLit:
    value: float

@dataclass
class StringLit:
    value: str

@dataclass
class BoolLit:
    value: bool

@dataclass
class NullLit:
    pass

@dataclass
class Ident:
    name: str

@dataclass
class ArrayLit:
    elements: list

@dataclass
class IndexExpr:
    """array[index]"""
    obj: object
    index: object

@dataclass
class BinOp:
    op: str          
    left: object
    right: object

@dataclass
class UnaryOp:
    op: str         
    operand: object

@dataclass
class LogicalOp:
    op: str        
    left: object
    right: object

@dataclass
class IfExpr:
    condition: object
    then_body: list
    else_body: list   

@dataclass
class FnExpr:
    """fn(params) { body }  — anonymous function / lambda"""
    params: list
    body: list

@dataclass
class CallExpr:
    callee: object
    args: list

@dataclass
class AssignExpr:
    """x = value  (re-assignment, not let)"""
    name: str
    value: object



@dataclass
class LetStmt:
    name: str
    value: object

@dataclass
class ReturnStmt:
    value: object

@dataclass
class WhileStmt:
    condition: object
    body: list

@dataclass
class ForStmt:
    """for item in iterable { body }"""
    var: str
    iterable: object
    body: list

@dataclass
class PrintStmt:
    value: object

@dataclass
class ExprStmt:
    """A bare expression used as a statement (e.g. a function call)."""
    expr: object

@dataclass
class Program:
    statements: list