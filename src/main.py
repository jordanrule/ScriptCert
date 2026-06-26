from __future__ import annotations

import argparse
import json

from scriptcert import check_semantic_preservation, compile_expr, eval_expr, parse_expr, render_program, render_value, run_program


def main() -> None:
    parser = argparse.ArgumentParser(description="ScriptCert pearl runner")
    parser.add_argument(
        "--expr",
        required=True,
        help='Expression JSON. Examples: ["opt_chain", ["some", ["add",2,3]]] or ["match", ["opt_chain", ["some", 7]], [[["num", 7], 1], ["_", 0]], -1]',
    )
    args = parser.parse_args()

    node = json.loads(args.expr)
    expr = parse_expr(node)

    source_result = eval_expr(expr)
    program = compile_expr(expr)
    target_stack = run_program(program)
    preserved = check_semantic_preservation(expr)

    print(f"source result: {render_value(source_result)}")
    print("compiled program:")
    for line in render_program(program):
        print(f"  {line}")
    rendered_stack = ", ".join(render_value(v) for v in target_stack)
    print(f"target result stack: [{rendered_stack}]")
    print(f"semantic preservation: {preserved}")


if __name__ == "__main__":
    main()

