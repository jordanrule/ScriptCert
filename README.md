This is my nod to the excellent technical work being done at TC39 ([link](https://github.com/tc39/proposals/)). I am not aware of anything else like this being done stateside, so if you would like to set this repo up as a community hub, please reach out.

# ScriptCert Pearl

`ScriptCert` is a small, readable "pearl" that demonstrates the core idea behind a formally verified compiler for a JavaScript fragment.

It borrows its engineering shape from [CompCert](https://github.com/absint/compcert):
- define source and target semantics explicitly,
- implement a simple compiler pass,
- prove semantic preservation for that pass,
- keep the trusted base small and obvious.

It also mirrors the spirit of [TC39 proposals](https://github.com/tc39/proposals/):
- language behavior should be specified clearly,
- changes should be staged and reviewable,
- implementation artifacts should stay aligned with the specification.

## What this prototype verifies

The current pearl models a tiny JavaScript-like expression language:
- numbers (`42`)
- addition (`a + b`)

The compiler translates expressions into a stack-machine program.

In `coq/JsPearl.v`, we prove that running compiled code yields the same value as directly evaluating the source expression:

`run (compile e) [] = Some [eval e]`

This is the central semantic-preservation theorem for this miniature compiler.

## Repository layout

- `coq/JsPearl.v`: AST, source semantics, target machine, compiler, and correctness proof.
- `src/scriptcert.py`: executable mirror of the same definitions.
- `src/main.py`: small CLI for compiling and running sample expressions.
- `tests/test_scriptcert.py`: regression and property-style checks over sample trees.
- `docs/COMPCERT_NOTES.md`: CompCert best-practice notes used in this pearl.
- `docs/TC39_NOTES.md`: TC39 process notes plus the feature-trace matrix.

## TC39 feature-trace matrix

Canonical matrix: `docs/TC39_NOTES.md`

| Feature | ScriptCert status | Proof status |
| --- | --- | --- |
| Arithmetic expressions (`Number`, `+`) | Implemented | `compile_correct` proved |
| Optional chaining (`?.`) | Planned | Not started |
| Pattern matching | Planned | Not started |

## Quick start

Run the executable tests:

```bash
python3 -m unittest discover -s tests -v
```

Try the CLI:

```bash
python3 src/main.py --expr '["add", 2, ["add", 3, 4]]'
```

Expected output includes:
- source evaluation result,
- emitted stack instructions,
- target execution result,
- a semantic-preservation check.

## Coq proof check (optional)

If Coq is installed:

```bash
coqc coq/JsPearl.v
```

## Approach in plain language

This project starts from the behavior we want to preserve, not from optimization tricks.

1. We define exactly what source programs mean.
2. We define exactly what target code means.
3. We write a compiler that is simple enough to reason about structurally.
4. We prove, by induction on syntax, that the meanings agree.

That is the same high-level discipline used by CompCert, scaled down to a JavaScript-focused pearl that can evolve with TC39-driven language design.
