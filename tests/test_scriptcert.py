from __future__ import annotations

import unittest

from src.scriptcert import (
    Add,
    MatchConst,
    Mul,
    Neg,
    Num,
    NumV,
    OptChain,
    PNum,
    PUndef,
    PWildcard,
    SomeExpr,
    SomeV,
    Sub,
    UNDEF,
    check_semantic_preservation,
    compile_expr,
    eval_expr,
    parse_expr,
    run_program,
)


class ScriptCertTests(unittest.TestCase):
    def test_single_number(self) -> None:
        expr = Num(42)
        self.assertEqual(eval_expr(expr), NumV(42))
        self.assertEqual(run_program(compile_expr(expr)), [NumV(42)])
        self.assertTrue(check_semantic_preservation(expr))

    def test_nested_addition(self) -> None:
        expr = Add(Num(2), Add(Num(3), Num(4)))
        self.assertEqual(eval_expr(expr), NumV(9))
        self.assertEqual(run_program(compile_expr(expr)), [NumV(9)])
        self.assertTrue(check_semantic_preservation(expr))

    def test_sub_mul_neg(self) -> None:
        expr = Sub(Mul(Num(3), Num(5)), Neg(Num(2)))
        self.assertEqual(eval_expr(expr), NumV(17))
        self.assertEqual(run_program(compile_expr(expr)), [NumV(17)])
        self.assertTrue(check_semantic_preservation(expr))

    def test_optional_chaining(self) -> None:
        expr = OptChain(SomeExpr(Add(Num(2), Num(5))))
        self.assertEqual(eval_expr(expr), NumV(7))
        self.assertTrue(check_semantic_preservation(expr))

        miss_expr = OptChain(Num(9))
        self.assertEqual(eval_expr(miss_expr), UNDEF)
        self.assertTrue(check_semantic_preservation(miss_expr))

    def test_pattern_matching(self) -> None:
        expr = MatchConst(
            OptChain(SomeExpr(Num(7))),
            [(PNum(7), NumV(1)), (PUndef(), NumV(0)), (PWildcard(), NumV(-1))],
            NumV(99),
        )
        self.assertEqual(eval_expr(expr), NumV(1))
        self.assertTrue(check_semantic_preservation(expr))

        undef_expr = MatchConst(OptChain(Num(3)), [(PNum(1), NumV(100))], NumV(-10))
        self.assertEqual(eval_expr(undef_expr), NumV(-10))
        self.assertTrue(check_semantic_preservation(undef_expr))

    def test_parser_for_new_ops(self) -> None:
        expr = parse_expr(["sub", ["mul", 6, ["neg", 2]], ["add", 1, 1]])
        self.assertEqual(eval_expr(expr), NumV(-14))
        self.assertTrue(check_semantic_preservation(expr))

    def test_parser_for_optional_chaining_and_match(self) -> None:
        expr = parse_expr(
            [
                "match",
                ["opt_chain", ["some", ["add", 3, 4]]],
                [[["num", 7], 10], ["undef", 20], ["_", -1]],
                0,
            ]
        )
        self.assertEqual(eval_expr(expr), NumV(10))
        self.assertTrue(check_semantic_preservation(expr))

    def test_grid_of_small_values(self) -> None:
        # Lightweight property-style sweep for many small programs.
        for a in range(-3, 4):
            for b in range(-3, 4):
                for c in range(-3, 4):
                    expr = Add(Add(Num(a), Num(b)), Num(c))
                    self.assertTrue(check_semantic_preservation(expr))

    def test_grid_mixed_ops(self) -> None:
        # Cover compiler stack behavior for mixed binary and unary ops.
        for a in range(-2, 3):
            for b in range(-2, 3):
                expr = Sub(Mul(Num(a), Num(b)), Neg(Num(a)))
                self.assertTrue(check_semantic_preservation(expr))

    def test_grid_optional_chain_match(self) -> None:
        for a in range(-2, 3):
            expr = MatchConst(
                OptChain(SomeExpr(Num(a))),
                [(PNum(a), NumV(a + 1)), (PUndef(), NumV(0))],
                NumV(-99),
            )
            self.assertEqual(eval_expr(expr), NumV(a + 1))
            self.assertTrue(check_semantic_preservation(expr))


if __name__ == "__main__":
    unittest.main()

