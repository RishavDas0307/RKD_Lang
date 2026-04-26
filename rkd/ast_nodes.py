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
class IntLit(Node):
    value: int

@dataclass
class FloatLit(Node):
    value: float

@dataclass
class StringLit(Node):
    value: str

@dataclass
class BoolLit(Node):
    value: bool

@dataclass
class NullLit(Node):
    pass

@dataclass
class Ident(Node):
    name: str

@dataclass
class ArrayLit(Node):
    elements: list[Node]

@dataclass
class IndexExpr(Node):
    """array[index]"""
    obj: Node
    index: Node

@dataclass
class BinOp(Node):
    op: str
    right: Node

@dataclass
class UnaryOp(Node):
    op: str
    operand: Node

@dataclass
class LogicalOp(Node):
    op: str
    left: Node
    right: Node

@dataclass
class IfExpr(Node):
    condition: Node
    then_body: list[Node]
    else_body: list[Node]

@dataclass
class FnExpr(Node):
    """fn(params) { body }  — anonymous function / lambda"""
    params: list[str]
    body: list[Node]

@dataclass
class CallExpr(Node):
    callee: Node
    args: list[Node]

@dataclass
class AssignExpr(Node):
    """x = value  (re-assignment, not let)"""
    name: str
    value: Node


@dataclass
class LetStmt(Node):
    name: str
    value: Node

@dataclass
class ReturnStmt(Node):
    value: Node

@dataclass
class WhileStmt(Node):
    condition: Node
    body: list[Node]

@dataclass
class ForStmt(Node):
    """for item in iterable { body }"""
    var: str
    iterable: Node
    body: list[Node]

@dataclass
class PrintStmt(Node):
    value: Node

@dataclass
class ExprStmt(Node):
    """A bare expression used as a statement (e.g. a function call)."""
    expr: Node

@dataclass
class Program(Node):
    statements: list[Node]