# Diagonal three: optimal exact full-support segment cover

## Result

The 105 certified strict-parent row-2599 segments contain an exact minimum
40-edge subbank that retains every one of the 10,844 already certified
full-support residual-wall crossings.

This is a source-skeleton compression theorem, not a global component theorem.
It neither proves that every component of a known wall meets the skeleton nor
classifies the 5,803 factors whose full parent-interior feasibility remains
open.  The honest Nine-Diagonal Vanishing Lemma score remains **2/9**.

## Exact optimum

The packed chart signs and exact endpoint evaluations give a 105-by-17,824
edge/factor incidence matrix.  Its nonzero columns are the 10,844 factors
already known to meet the strict parent interior.

Forty-nine factors cross exactly one segment.  Their witnesses force 34
distinct edges in every cover.  Those mandatory edges already cover 10,815
factors and leave a residue of 29.

The nonempty incidence patterns of the remaining optional edges number 21.
Deleting patterns contained in another leaves seven inclusion-maximal
patterns.  Exhausting all subsets of these seven patterns gives:

| optional patterns | covers of the 29-factor residue |
|---:|---:|
| at most 5 | 0 |
| 6 | 3 |

Thus every cover needs at least `34 + 6 = 40` edges, and the emitted 40-edge
cover is optimal.  It removes 65 of 105 source edges, a reduction of `13/21`,
while preserving all known factor-zero witnesses.  The verifier evaluates an
exact opposite-sign endpoint pair for every retained factor; packed signs are
not the final trust boundary.

## Target-selection correction

The same checkpoint audits the latest component-cosheaf pilot against the
exact relative-boundary theorem.  Its proposed section-960 collision and
section-550 endpoint-tangency stars lie on supports `(3,1,15)` and `(3,3,7)`.
Both are proper product-simplex supports.  All 3,374 proper supports lie in the
parent-boundary relative subspace `K_infinity`; only `(15,15,15)` can meet the
nonrelative parent interior.

Consequently, subdividing those two stars contributes zero generators to
`C_*(K,K_infinity)`.  They remain valid compiler regressions for split/merge
and endpoint specialization, but scaling their 16,935,101 local cells cannot
by itself advance the relative middle-rank proof.  The proof-bearing pair
target returns to full support: attach labels and closure/component data to
the 40-edge cover, or replace the finite source skeleton with a directly
coverage-certified parent-cell roadmap.

## Trust separation

Build the deterministic certificate with

```console
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/build_diag3_pair_fullsupport_segment_cover.py
```

Replay it with

```console
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/verify_diag3_pair_fullsupport_segment_cover.py
```

The independent verifier recomputes all 105 parent-safe segments, the complete
edge/factor incidence matrix, the mandatory-edge lower bound, the seven-pattern
optional residue, the exhaustive no-five-edge result, and all 10,844 exact
endpoint sign crossings.  It independently reconstructs the compactification
support partition and rejects fourteen hostile semantic mutations.

The generated certificate is
`data/DIAG3_PAIR_FULLSUPPORT_SEGMENT_COVER.json`.

## Theorem effect

This checkpoint sharply reduces the exact full-support source object and
prevents a boundary-only diagnostic from being mistaken for a relative-chain
advance.  It does not establish global missed-component coverage, assemble the
global exclusive-pair complex, or address the independent 1,162,302-row triple
residue.  The score remains **2/9**.
