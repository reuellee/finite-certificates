# Accepted scope of the generic countermodel

The frozen construction is commit `96d2cafda5c3588d0754780d18b92c694a843b54`.
The independent review is commit `0de26f6a6561705b37d59dfb5d3886857ab96bd3`,
integrated on the coordinator branch as `9aefa1d`.

The accepted result is the construction **together with** the proof supplement
in [the independent review](../ai-d3-reset-referee/REVIEW.md). It disproves the
implication from the listed generic common-matrix, finite-relative-source,
convexity, and lower-vanishing hypotheses to D3. It does not disprove D3 for
actual parent configurations. It changes no canonical obligation or theorem
score.

Two corrections apply when reading or running the frozen producer artifacts:

1. The producer checker computes relative boundary ranks over the rationals.
   Its output describing an integral check is too strong. Integral acyclicity
   is established by the written unit-differential argument and the referee's
   independent integer chain contraction, not by rational ranks alone.
2. The unpinned phrase "as in the source audit" is superseded by Section 5 of
   the frozen independent review. That section proves the proper filtered
   comparison explicitly, preserving block masses and block-support faces.
   It does not claim that the deformation preserves every individual witness
   coordinate face.

The producer files are retained verbatim so their original review hashes
remain reproducible. For the independent exact checks, run:

```text
py -3 ops/team/ai-d3-reset-referee/independent_check.py
```

That checker imports no producer code, verifies an integer chain contraction,
and rejects four hostile mutations. Its finite algebra certificates support
the mathematical proof; they are not a machine formalization of the global
topology.

The shared-label determinant obstruction excludes the specified labeled
parent interpretation only. No arbitrary relabeling search, actual-parent
counterexample, or pair-map injectivity failure is claimed by this model.
