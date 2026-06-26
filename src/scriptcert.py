from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence, Tuple, Union


@dataclass(frozen=True)
class NumV:
    value: int


@dataclass(frozen=True)
class SomeV:
    value: "Value"


@dataclass(frozen=True)
class UndefV:
    pass


Value = Union[NumV, SomeV, UndefV]
UNDEF = UndefV()


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


@dataclass(frozen=True)
class SomeExpr:
    value: "Expr"


@dataclass(frozen=True)
class OptChain:
    receiver: "Expr"


@dataclass(frozen=True)
class PNum:
    value: int


@dataclass(frozen=True)
class PSome:
    pass


@dataclass(frozen=True)
class PUndef:
    pass


@dataclass(frozen=True)
class PWildcard:
    pass


Pattern = Union[PNum, PSome, PUndef, PWildcard]
MatchArm = Tuple[Pattern, Value]


@dataclass(frozen=True)
class MatchConst:
    scrutinee: "Expr"
    arms: List[MatchArm]
    default: Value


Expr = Union[Num, Add, Sub, Mul, Neg, SomeExpr, OptChain, MatchConst]


@dataclass(frozen=True)
class Push:
    value: Value


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


@dataclass(frozen=True)
class IMakeSome:
    pass


@dataclass(frozen=True)
class IOptChain:
    pass


@dataclass(frozen=True)
class IMatchConst:
    arms: List[MatchArm]
    default: Value


Instr = Union[Push, IAdd, ISub, IMul, INeg, IMakeSome, IOptChain, IMatchConst]


def render_value(value: Value) -> str:
    if isinstance(value, NumV):
        return str(value.value)
    if isinstance(value, SomeV):
        return f"some({render_value(value.value)})"
    if isinstance(value, UndefV):
        return "undef"
    raise TypeError(f"Unknown value node: {value!r}")


def _lift_binop(left: Value, right: Value, op: str) -> Value:
    if isinstance(left, NumV) and isinstance(right, NumV):
        if op == "add":
            return NumV(left.value + right.value)
        if op == "sub":
            return NumV(left.value - right.value)
        if op == "mul":
            return NumV(left.value * right.value)
    return UNDEF


def _lift_neg(value: Value) -> Value:
    if isinstance(value, NumV):
        return NumV(-value.value)
    return UNDEF


def _opt_chain_value(value: Value) -> Value:
    if isinstance(value, SomeV):
        return value.value
    return UNDEF


def pattern_matches(pattern: Pattern, value: Value) -> bool:
    if isinstance(pattern, PNum):
        return isinstance(value, NumV) and value.value == pattern.value
    if isinstance(pattern, PSome):
        return isinstance(value, SomeV)
    if isinstance(pattern, PUndef):
        return isinstance(value, UndefV)
    if isinstance(pattern, PWildcard):
        return True
    raise TypeError(f"Unknown pattern node: {pattern!r}")


def select_branch_value(value: Value, arms: Sequence[MatchArm], default: Value) -> Value:
    for pattern, rhs in arms:
        if pattern_matches(pattern, value):
            return rhs
    return default


def eval_expr(expr: Expr) -> Value:
    if isinstance(expr, Num):
        return NumV(expr.value)
    if isinstance(expr, Add):
        return _lift_binop(eval_expr(expr.left), eval_expr(expr.right), "add")
    if isinstance(expr, Sub):
        return _lift_binop(eval_expr(expr.left), eval_expr(expr.right), "sub")
    if isinstance(expr, Mul):
        return _lift_binop(eval_expr(expr.left), eval_expr(expr.right), "mul")
    if isinstance(expr, Neg):
        return _lift_neg(eval_expr(expr.value))
    if isinstance(expr, SomeExpr):
        return SomeV(eval_expr(expr.value))
    if isinstance(expr, OptChain):
        return _opt_chain_value(eval_expr(expr.receiver))
    if isinstance(expr, MatchConst):
        return select_branch_value(eval_expr(expr.scrutinee), expr.arms, expr.default)
    raise TypeError(f"Unknown expression node: {expr!r}")


def compile_expr(expr: Expr) -> List[Instr]:
    if isinstance(expr, Num):
        return [Push(NumV(expr.value))]
    if isinstance(expr, Add):
        return compile_expr(expr.left) + compile_expr(expr.right) + [IAdd()]
    if isinstance(expr, Sub):
        return compile_expr(expr.left) + compile_expr(expr.right) + [ISub()]
    if isinstance(expr, Mul):
        return compile_expr(expr.left) + compile_expr(expr.right) + [IMul()]
    if isinstance(expr, Neg):
        return compile_expr(expr.value) + [INeg()]
    if isinstance(expr, SomeExpr):
        return compile_expr(expr.value) + [IMakeSome()]
    if isinstance(expr, OptChain):
        return compile_expr(expr.receiver) + [IOptChain()]
    if isinstance(expr, MatchConst):
        return compile_expr(expr.scrutinee) + [IMatchConst(expr.arms, expr.default)]
    raise TypeError(f"Unknown expression node: {expr!r}")


def run_program(program: Sequence[Instr]) -> List[Value]:
    stack: List[Value] = []
    for instr in program:
        if isinstance(instr, Push):
            stack.append(instr.value)
        elif isinstance(instr, IAdd):
            if len(stack) < 2:
                raise ValueError("Malformed program: IAdd needs two operands")
            right = stack.pop()
            left = stack.pop()
            stack.append(_lift_binop(left, right, "add"))
        elif isinstance(instr, ISub):
            if len(stack) < 2:
                raise ValueError("Malformed program: ISub needs two operands")
            right = stack.pop()
            left = stack.pop()
            stack.append(_lift_binop(left, right, "sub"))
        elif isinstance(instr, IMul):
            if len(stack) < 2:
                raise ValueError("Malformed program: IMul needs two operands")
            right = stack.pop()
            left = stack.pop()
            stack.append(_lift_binop(left, right, "mul"))
        elif isinstance(instr, INeg):
            if not stack:
                raise ValueError("Malformed program: INeg needs one operand")
            value = stack.pop()
            stack.append(_lift_neg(value))
        elif isinstance(instr, IMakeSome):
            if not stack:
                raise ValueError("Malformed program: IMakeSome needs one operand")
            value = stack.pop()
            stack.append(SomeV(value))
        elif isinstance(instr, IOptChain):
            if not stack:
                raise ValueError("Malformed program: IOptChain needs one operand")
            value = stack.pop()
            stack.append(_opt_chain_value(value))
        elif isinstance(instr, IMatchConst):
            if not stack:
                raise ValueError("Malformed program: IMatchConst needs one operand")
            value = stack.pop()
            stack.append(select_branch_value(value, instr.arms, instr.default))
        else:
            raise TypeError(f"Unknown instruction: {instr!r}")
    return stack


def check_semantic_preservation(expr: Expr) -> bool:
    source = eval_expr(expr)
    target_stack = run_program(compile_expr(expr))
    return target_stack == [source]


def parse_value(node: object) -> Value:
    if isinstance(node, int):
        return NumV(node)
    if isinstance(node, str) and node == "undef":
        return UNDEF
    if isinstance(node, list) and len(node) == 2 and node[0] == "some":
        return SomeV(parse_value(node[1]))
    raise ValueError(f"Unsupported value encoding: {node!r}")


def parse_pattern(node: object) -> Pattern:
    if isinstance(node, list) and len(node) == 2 and node[0] == "num" and isinstance(node[1], int):
        return PNum(node[1])
    if isinstance(node, str) and node == "some":
        return PSome()
    if isinstance(node, str) and node == "undef":
        return PUndef()
    if isinstance(node, str) and node == "_":
        return PWildcard()
    raise ValueError(f"Unsupported pattern encoding: {node!r}")


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
        if op == "some":
            if len(node) != 2:
                raise ValueError("some expects [\"some\", value]")
            return SomeExpr(parse_expr(node[1]))
        if op == "opt_chain":
            if len(node) != 2:
                raise ValueError("opt_chain expects [\"opt_chain\", receiver]")
            return OptChain(parse_expr(node[1]))
        if op == "match":
            if len(node) != 4 or not isinstance(node[2], list):
                raise ValueError("match expects [\"match\", scrutinee, arms, default]")
            scrutinee = parse_expr(node[1])
            arms: List[MatchArm] = []
            for arm in node[2]:
                if not isinstance(arm, list) or len(arm) != 2:
                    raise ValueError("Each match arm must be [pattern, value]")
                arms.append((parse_pattern(arm[0]), parse_value(arm[1])))
            return MatchConst(scrutinee, arms, parse_value(node[3]))
        raise ValueError("Only add/sub/mul/neg/some/opt_chain/match forms are supported")
    raise ValueError(f"Unsupported expression encoding: {node!r}")


def render_program(program: Sequence[Instr]) -> List[str]:
    rendered: List[str] = []
    for instr in program:
        if isinstance(instr, Push):
            rendered.append(f"PUSH {render_value(instr.value)}")
        elif isinstance(instr, IAdd):
            rendered.append("IADD")
        elif isinstance(instr, ISub):
            rendered.append("ISUB")
        elif isinstance(instr, IMul):
            rendered.append("IMUL")
        elif isinstance(instr, INeg):
            rendered.append("INEG")
        elif isinstance(instr, IMakeSome):
            rendered.append("IMAKE_SOME")
        elif isinstance(instr, IOptChain):
            rendered.append("IOPT_CHAIN")
        elif isinstance(instr, IMatchConst):
            rendered.append(f"IMATCH_CONST arms={len(instr.arms)} default={render_value(instr.default)}")
        else:
            raise TypeError(f"Unknown instruction: {instr!r}")
    return rendered

