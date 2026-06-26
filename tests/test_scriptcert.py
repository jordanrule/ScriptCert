from __future__ import annotations

import unittest

from src.scriptcert import Add, Mul, Neg, Num, Sub, check_semantic_preservation, compile_expr, eval_expr, parse_expr, run_program


class ScriptCertTests(unittest.TestCase):
    def test_single_number(self) -> None:
        expr = Num(42)
        self.assertEqual(eval_expr(expr), 42)
        self.assertEqual(run_program(compile_expr(expr)), [42])
        self.assertTrue(check_semantic_preservation(expr))

    def test_nested_addition(self) -> None:
        expr = Add(Num(2), Add(Num(3), Num(4)))
        self.assertEqual(eval_expr(expr), 9)
        self.assertEqual(run_program(compile_expr(expr)), [9])
        self.assertTrue(check_semantic_preservation(expr))

    def test_sub_mul_neg(self) -> None:
        expr = Sub(Mul(Num(3), Num(5)), Neg(Num(2)))
        self.assertEqual(eval_expr(expr), 17)
        self.assertEqual(run_program(compile_expr(expr)), [17])
        self.assertTrue(check_semantic_preservation(expr))

    def test_parser_for_new_ops(self) -> None:
        expr = parse_expr(["sub", ["mul", 6, ["neg", 2]], ["add", 1, 1]])
        self.assertEqual(eval_expr(expr), -14)
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


if __name__ == "__main__":
    unittest.main()

