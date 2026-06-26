from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence, Union


@dataclass(frozen=True)
class Num:
    value: int


@dataclass(frozen=True)
class Add:
    left: "Expr"
    right: "Expr"


@dataclass(frozen=True)
class Sub:
    left: "Expr"
    right: "Expr"


@dataclass(frozen=True)
class Mul:
    left: "Expr"
    right: "Expr"


@dataclass(frozen=True)
class Neg:
    value: "Expr"


Expr = Union[Num, Add, Sub, Mul, Neg]


@dataclass(frozen=True)
class Push:
    value: int


@dataclass(frozen=True)
class IAdd:
    pass


@dataclass(frozen=True)
class ISub:
    pass


@dataclass(frozen=True)
class IMul:
    pass


@dataclass(frozen=True)
class INeg:
    pass


Instr = Union[Push, IAdd, ISub, IMul, INeg]


def eval_expr(expr: Expr) -> int:
    if isinstance(expr, Num):
        return expr.value
    if isinstance(expr, Add):
        return eval_expr(expr.left) + eval_expr(expr.right)
    if isinstance(expr, Sub):
        return eval_expr(expr.left) - eval_expr(expr.right)
    if isinstance(expr, Mul):
        return eval_expr(expr.left) * eval_expr(expr.right)
    if isinstance(expr, Neg):
        return -eval_expr(expr.value)
    raise TypeError(f"Unknown expression node: {expr!r}")


def compile_expr(expr: Expr) -> List[Instr]:
    if isinstance(expr, Num):
        return [Push(expr.value)]
    if isinstance(expr, Add):
        return compile_expr(expr.left) + compile_expr(expr.right) + [IAdd()]
    if isinstance(expr, Sub):
        return compile_expr(expr.left) + compile_expr(expr.right) + [ISub()]
    if isinstance(expr, Mul):
        return compile_expr(expr.left) + compile_expr(expr.right) + [IMul()]
    if isinstance(expr, Neg):
        return compile_expr(expr.value) + [INeg()]
    raise TypeError(f"Unknown expression node: {expr!r}")


def run_program(program: Sequence[Instr]) -> List[int]:
    stack: List[int] = []
    for instr in program:
        if isinstance(instr, Push):
            stack.append(instr.value)
        elif isinstance(instr, IAdd):
            if len(stack) < 2:
                raise ValueError("Malformed program: IAdd needs two operands")
            right = stack.pop()
            left = stack.pop()
            stack.append(left + right)
        elif isinstance(instr, ISub):
            if len(stack) < 2:
                raise ValueError("Malformed program: ISub needs two operands")
            right = stack.pop()
            left = stack.pop()
            stack.append(left - right)
        elif isinstance(instr, IMul):
            if len(stack) < 2:
                raise ValueError("Malformed program: IMul needs two operands")
            right = stack.pop()
            left = stack.pop()
            stack.append(left * right)
        elif isinstance(instr, INeg):
            if not stack:
                raise ValueError("Malformed program: INeg needs one operand")
            value = stack.pop()
            stack.append(-value)
        else:
            raise TypeError(f"Unknown instruction: {instr!r}")
    return stack


def check_semantic_preservation(expr: Expr) -> bool:
    source = eval_expr(expr)
    target_stack = run_program(compile_expr(expr))
    return target_stack == [source]


def parse_expr(node: object) -> Expr:
    if isinstance(node, int):
        return Num(node)
    if isinstance(node, list):
        if not node:
            raise ValueError("Expression list cannot be empty")
        op = node[0]
        if op in {"add", "sub", "mul"}:
            if len(node) != 3:
                raise ValueError(f"{op} expects [\"{op}\", lhs, rhs]")
            left = parse_expr(node[1])
            right = parse_expr(node[2])
            if op == "add":
                return Add(left, right)
            if op == "sub":
                return Sub(left, right)
            return Mul(left, right)
        if op == "neg":
            if len(node) != 2:
                raise ValueError("neg expects [\"neg\", value]")
            return Neg(parse_expr(node[1]))
        raise ValueError("Only add/sub/mul/neg expression forms are supported")
    raise ValueError(f"Unsupported expression encoding: {node!r}")


def render_program(program: Sequence[Instr]) -> List[str]:
    rendered: List[str] = []
    for instr in program:
        if isinstance(instr, Push):
            rendered.append(f"PUSH {instr.value}")
        elif isinstance(instr, IAdd):
            rendered.append("IADD")
        elif isinstance(instr, ISub):
            rendered.append("ISUB")
        elif isinstance(instr, IMul):
            rendered.append("IMUL")
        elif isinstance(instr, INeg):
            rendered.append("INEG")
        else:
            raise TypeError(f"Unknown instruction: {instr!r}")
    return rendered

