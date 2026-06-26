from __future__ import annotations

import unittest

from src.scriptcert import Add, Num, check_semantic_preservation, compile_expr, eval_expr, run_program


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

    def test_grid_of_small_values(self) -> None:
        # Lightweight property-style sweep for many small programs.
        for a in range(-3, 4):
            for b in range(-3, 4):
                for c in range(-3, 4):
                    expr = Add(Add(Num(a), Num(b)), Num(c))
                    self.assertTrue(check_semantic_preservation(expr))


if __name__ == "__main__":
    unittest.main()

