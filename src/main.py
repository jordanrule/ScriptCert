from __future__ import annotations

import argparse
import json

from scriptcert import check_semantic_preservation, compile_expr, eval_expr, parse_expr, render_program, run_program


def main() -> None:
    parser = argparse.ArgumentParser(description="ScriptCert pearl runner")
    parser.add_argument(
        "--expr",
        required=True,
        help='Expression in JSON list form, e.g. ["add", 2, ["add", 3, 4]]',
    )
    args = parser.parse_args()

    node = json.loads(args.expr)
    expr = parse_expr(node)

    source_result = eval_expr(expr)
    program = compile_expr(expr)
    target_stack = run_program(program)
    preserved = check_semantic_preservation(expr)

    print(f"source result: {source_result}")
    print("compiled program:")
    for line in render_program(program):
        print(f"  {line}")
    print(f"target result stack: {target_stack}")
    print(f"semantic preservation: {preserved}")


if __name__ == "__main__":
    main()

