from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from .ast_nodes import *


class RKDError(Exception):
    pass


class ReturnSignal(Exception):
    """Used to unwind the call stack on `return`."""
    def __init__(self, value: Any):
        self.value = value


@dataclass
class RKDFunction:
    params: list[str]
    body: list[Node]
    closure: "Environment"     

    def __repr__(self):
        return f"<fn({', '.join(self.params)})>"


class Environment:
    def __init__(self, parent: Environment | None = None):
        self.store:  dict[str, Any] = {}
        self.parent: Environment | None = parent

    def get(self, name: str) -> Any:
        if name in self.store:
            return self.store[name]
        if self.parent:
            return self.parent.get(name)
        raise RKDError(f"Undefined variable '{name}'")

    def set(self, name: str, value: Any) -> None:
        """Define or overwrite in the *current* scope."""
        self.store[name] = value

    def assign(self, name: str, value: Any) -> None:
        """Walk up the chain to find the scope that owns `name`."""
        if name in self.store:
            self.store[name] = value
            return
        if self.parent:
            self.parent.assign(name, value)
            return
        raise RKDError(f"Undefined variable '{name}' (cannot assign)")

    def child(self) -> "Environment":
        return Environment(parent=self)


# ── Evaluator ─────────────────────────────────────────────────────────────────

class Evaluator:
    def eval(self, node: Node, env: Environment) -> Any:
        match node:

            case IntLit(v):     return v
            case FloatLit(v):   return v
            case StringLit(v):  return v
            case BoolLit(v):    return v
            case NullLit():     return None

            case Ident(name):
                return env.get(name)

            case ArrayLit(elems):
                return [self.eval(e, env) for e in elems]

            case IndexExpr(obj, idx):
                obj_val = self.eval(obj, env)
                idx_val = self.eval(idx, env)
                if isinstance(obj_val, list):
                    if not isinstance(idx_val, int):
                        raise RKDError("Array index must be an integer")
                    if idx_val < 0 or idx_val >= len(obj_val):
                        raise RKDError(f"Index {idx_val} out of bounds (len={len(obj_val)})")
                    return obj_val[idx_val]
                if isinstance(obj_val, str):
                    if not isinstance(idx_val, int):
                        raise RKDError("String index must be an integer")
                    return obj_val[idx_val]
                raise RKDError("Only arrays and strings are indexable")

            case UnaryOp(op, operand):
                val = self.eval(operand, env)
                if op == "-":
                    if not isinstance(val, (int, float)):
                        raise RKDError(f"Unary '-' requires a number, got {type(val).__name__}")
                    return -val
                if op == "!":
                    return not self._truthy(val)
                raise RKDError(f"Unknown unary op: {op!r}")

            case BinOp(op, left, right):
                lv = self.eval(left,  env)
                rv = self.eval(right, env)
                return self._apply_binop(op, lv, rv)

            case LogicalOp(op, left, right):
                lv = self.eval(left, env)
                if op == "||":
                    return lv if self._truthy(lv) else self.eval(right, env)
                if op == "&&":
                    return self.eval(right, env) if self._truthy(lv) else lv
                raise RKDError(f"Unknown logical op: {op!r}")

            case AssignExpr(name, value):
                val = self.eval(value, env)
                env.assign(name, val)
                return val

            case IfExpr(cond, then_body, else_body):
                if self._truthy(self.eval(cond, env)):
                    return self._exec_block(then_body, env.child())
                elif else_body:
                    return self._exec_block(else_body, env.child())
                return None

            case FnExpr(params, body):
                return RKDFunction(params, body, env)

            case CallExpr(callee, args):
                fn  = self.eval(callee, env)
                arg_vals = [self.eval(a, env) for a in args]
                return self._call(fn, arg_vals)

            case LetStmt(name, value):
                env.set(name, self.eval(value, env))
                return None

            case ReturnStmt(value):
                raise ReturnSignal(self.eval(value, env))

            case WhileStmt(cond, body):
                while self._truthy(self.eval(cond, env)):
                    self._exec_block(body, env.child())
                return None

            case ForStmt(var, iterable, body):
                items = self.eval(iterable, env)
                if not isinstance(items, (list, str)):
                    raise RKDError("'for … in' requires an array or string")
                for item in items:
                    loop_env = env.child()
                    loop_env.set(var, item)
                    self._exec_block(body, loop_env)
                return None

            case PrintStmt(value):
                print(self._display(self.eval(value, env)))
                return None

            case ExprStmt(expr):
                return self.eval(expr, env)

            case Program(stmts):
                result = None
                for stmt in stmts:
                    result = self.eval(stmt, env)
                return result

            case _:
                raise RKDError(f"Unknown AST node: {type(node).__name__}")

    def _exec_block(self, stmts: list[Node], env: Environment) -> Any:
        result = None
        for stmt in stmts:
            result = self.eval(stmt, env)
        return result

    def _truthy(self, val: Any) -> bool:
        if val is None or val is False:
            return False
        if val == 0 or val == 0.0:
            return False
        if isinstance(val, (str, list)) and len(val) == 0:
            return False
        return True

    def _display(self, val: Any) -> str:
        if val is None:     return "null"
        if val is True:     return "true"
        if val is False:    return "false"
        if isinstance(val, list):
            return "[" + ", ".join(self._display(v) for v in val) + "]"
        return str(val)

    def _apply_binop(self, op: str, lv: Any, rv: Any) -> Any:

        if op == "+":
            if isinstance(lv, (int, float)) and isinstance(rv, (int, float)):
                return lv + rv
            if isinstance(lv, str) or isinstance(rv, str):
                return self._display(lv) + self._display(rv)   # string concat
            raise RKDError(f"'+' requires numbers or strings")
        if op == "-": return self._num(lv, op) - self._num(rv, op)
        if op == "*": return self._num(lv, op) * self._num(rv, op)
        if op == "/":
            if rv == 0: raise RKDError("Division by zero")
            a, b = self._num(lv, op), self._num(rv, op)
            return a // b if isinstance(a, int) and isinstance(b, int) else a / b
        if op == "%":
            if rv == 0: raise RKDError("Modulo by zero")
            return self._num(lv, op) % self._num(rv, op)


        if op == "==": return lv == rv
        if op == "!=": return lv != rv
        if op in ("<", ">", "<=", ">="):
            if not isinstance(lv, (int, float)) or not isinstance(rv, (int, float)):
                raise RKDError(f"'{op}' requires numbers")
            return {"<": lv < rv, ">": lv > rv, "<=": lv <= rv, ">=": lv >= rv}[op]

        raise RKDError(f"Unknown binary op: {op!r}")

    def _num(self, val: Any, op: str) -> int | float:
        if not isinstance(val, (int, float)):
            raise RKDError(f"'{op}' requires numbers, got {type(val).__name__}")
        return val

    def _call(self, fn: Any, args: list[Any]) -> Any:

        if callable(fn):
            return fn(args)

        if not isinstance(fn, RKDFunction):
            raise RKDError(f"'{fn!r}' is not callable")

        if len(args) != len(fn.params):
            raise RKDError(
                f"Expected {len(fn.params)} args, got {len(args)}"
            )

        call_env = fn.closure.child()
        for param, arg in zip(fn.params, args):
            call_env.set(param, arg)

        try:
            return self._exec_block(fn.body, call_env)
        except ReturnSignal as r:
            return r.value

def make_stdlib() -> Environment:
    env = Environment()

    def builtin(name, fn):
        env.set(name, fn)

    builtin("len",    lambda a: len(a[0]) if a else (_ for _ in ()).throw(RKDError("len() takes 1 arg")))
    builtin("type",   lambda a: type(a[0]).__name__ if a else "null")
    builtin("int",    lambda a: int(a[0]) if a else 0)
    builtin("float",  lambda a: float(a[0]) if a else 0.0)
    builtin("str",    lambda a: str(a[0]) if a else "")
    builtin("push",   lambda a: (a[0].append(a[1]), a[0])[1])
    builtin("pop",    lambda a: a[0].pop() if a else None)
    builtin("range",  lambda a: list(range(*[int(x) for x in a])))
    builtin("input",  lambda a: input(a[0] if a else ""))
    builtin("sqrt",   lambda a: __import__("math").sqrt(a[0]))
    builtin("abs",    lambda a: abs(a[0]))
    builtin("max",    lambda a: max(a[0]) if len(a) == 1 and isinstance(a[0], list) else max(a))
    builtin("min",    lambda a: min(a[0]) if len(a) == 1 and isinstance(a[0], list) else min(a))

    return env