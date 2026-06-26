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


Expr = Union[Num, Add]


@dataclass(frozen=True)
class Push:
    value: int


@dataclass(frozen=True)
class IAdd:
    pass


Instr = Union[Push, IAdd]


def eval_expr(expr: Expr) -> int:
    if isinstance(expr, Num):
        return expr.value
    if isinstance(expr, Add):
        return eval_expr(expr.left) + eval_expr(expr.right)
    raise TypeError(f"Unknown expression node: {expr!r}")


def compile_expr(expr: Expr) -> List[Instr]:
    if isinstance(expr, Num):
        return [Push(expr.value)]
    if isinstance(expr, Add):
        return compile_expr(expr.left) + compile_expr(expr.right) + [IAdd()]
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
        if len(node) != 3 or node[0] != "add":
            raise ValueError("Only [\"add\", lhs, rhs] is supported")
        return Add(parse_expr(node[1]), parse_expr(node[2]))
    raise ValueError(f"Unsupported expression encoding: {node!r}")


def render_program(program: Sequence[Instr]) -> List[str]:
    rendered: List[str] = []
    for instr in program:
        if isinstance(instr, Push):
            rendered.append(f"PUSH {instr.value}")
        elif isinstance(instr, IAdd):
            rendered.append("IADD")
        else:
            raise TypeError(f"Unknown instruction: {instr!r}")
    return rendered

