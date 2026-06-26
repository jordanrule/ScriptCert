# TC39 process notes reflected in this pearl

Source: [TC39 proposals](https://github.com/tc39/proposals/)

## Why TC39 matters here

A verified JavaScript compiler should track the way JavaScript evolves. TC39's proposal process gives a public, staged route for language changes.

## How this prototype aligns

1. **Explicit scope**
   - This pearl verifies only arithmetic expressions.
   - A narrow scope keeps proofs maintainable as the language grows.

2. **Traceable evolution**
   - New language fragments should cite the motivating TC39 proposal (when applicable), then introduce corresponding semantics and proof obligations.

3. **Stage-aware integration strategy**
   - Experimental features can live in separate modules while proposals mature.
   - Stable features can be promoted into the main verified pipeline.

4. **Spec-to-proof discipline**
   - For each feature: model spec behavior, implement translation, prove preservation.
   - This keeps verification work synchronized with standards work.

## TC39 feature-trace matrix

This table tracks how language features map into ScriptCert artifacts and proof obligations.

| Feature | TC39 link | Stage snapshot | ScriptCert status | Spec/code refs | Proof status | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| Arithmetic expressions (`Number`, `+`) | Baseline ECMAScript (no active proposal link) | Included in standard | Implemented | `coq/JsPearl.v`, `src/scriptcert.py` | `compile_correct` proved | Current verified core |
| Optional chaining (`?.`) | https://github.com/tc39/proposals/ | See tracker | Planned | TBD (`coq/js/`, `src/`) | Not started | Add short-circuit semantics first |
| Pattern matching | https://github.com/tc39/proposals/ | See tracker | Planned | TBD (`coq/js/`, `src/`) | Not started | Likely requires richer AST and match semantics |

Stages change over time; this matrix treats the TC39 repository as the source of truth.
