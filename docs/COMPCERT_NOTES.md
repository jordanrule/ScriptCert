# CompCert best practices reflected in this pearl

Source: [CompCert](https://github.com/absint/compcert)

## What we borrowed

1. **Semantics-first design**
   - The project defines source and target meanings before discussing optimizations.

2. **Pass-local correctness theorem**
   - The pearl proves one concrete theorem (`compile_correct`) for one pass.
   - This mirrors CompCert's pass-by-pass proof architecture.

3. **Small trusted base**
   - The trusted part is just Coq's logic and extraction/runtime assumptions.
   - Compiler logic itself is proved, not hand-waved.

4. **Executable mirror for testing**
   - The Python model mirrors the Coq definitions for quick regression testing.
   - Tests are not a substitute for proof, but they aid iteration.

5. **Clear growth path**
   - Add syntax/semantics incrementally (variables, control flow, side effects),
     proving each extension as a local theorem before composing larger results.

