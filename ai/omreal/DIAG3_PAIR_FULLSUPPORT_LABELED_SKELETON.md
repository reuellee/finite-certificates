# Diagonal three: first labelled full-support source skeleton

## Result

The exact optimal 40-edge row-2599 source cover now has its first
face-compatible labelled regular subcomplex.  Selected edge 27, joining
stored strict-parent charts 0 and 89, is subdivided at all 1,237 exact
residual events into

| dimension | cells |
|---:|---:|
| 0 | 1,239 |
| 1 | 1,238 |

The certificate stores globally stable cell IDs, all 2,476 strict closure
pairs, the empty list of strict three-cell chains forced by dimension, and
the signed integral boundary of the oriented path.  Exact replay gives
`rank(d1)=1,238`, `H0=Z`, `H1=0`, and `d^2=0` trivially beyond dimension one.

This is a bounded partial success and a **fail-closed no-go for promoting the
40-edge cover as-is**.  The other 39 selected segments do not yet have
complete ordered residual roadmaps and exact compound-event label
continuations.  They remain individually listed in the certificate with
`label_compatible_regular_refinement: MISSING`.

## Complete extension-signature labels on edge 27

The accepted exact chart-0-to-chart-89 continuation tracks all 97,224 valid
row-2599 extension signatures through 1,179 simple and 58 compound events.
The new deterministic profile catalog materializes that semantic commitment:

- every signature, in canonical increasing 56-bit order, has a packed profile
  ID;
- the 2,458 distinct profiles store their complete feasible-one-cell bitmap;
- every profile stores the derived bad one-cell and bad zero-cell bitmaps;
- a zero-cell is bad exactly when at least one incident open one-cell is bad,
  so every bad locus is a closed subcomplex of the path.

This is the first artifact from the full-support source bank that simultaneously
exposes all five fields required by the component-cosheaf compiler:
`cells`, `strict_closure_pairs`, `strict_three_cell_chains`, true
`parent_infinity_subcomplex`, and a complete `signature_profile_source`.
It does so on one of forty source edges, not on the full source bank or parent
cell.

## Boundary classification

The whole closed segment remains strictly inside the row-2599 parent cell by
the accepted exact rational Bernstein certificate for all 70 signed parent
brackets.  Therefore

```text
parent_infinity_subcomplex = []
```

The two terminal chart vertices are ordinary interior cells and are retained
in the chain complex.  They are endpoints of the computed one-dimensional
scope, not points at parent infinity.

## Exact residue and next datum

For each of the remaining 39 selected edges, the minimal missing datum is:

1. the complete ordered exact residual-root roadmap, including coincident
   event groups; and
2. exact continuation of all 97,224 extension-signature labels across every
   compound event.

Endpoint sign crossings alone cannot supply this information.  In particular,
an unsubdivided source segment is not a label-compatible master cell whenever
its interior crosses residual walls.

Even completion of all 40 paths would prove only coverage of the finite
source skeleton.  It would not prove that every residual-wall component meets
that skeleton, cover the row-2599 parent cell, or supply the two-cells needed
for global first homology.  The independent triple compactness obligation is
also untouched.  The honest 9DVL score remains **2/9**.

## Replay and trust boundary

Build the exact profile materialization and closure certificate with

```console
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/build_diag3_pair_fullsupport_labeled_skeleton.py
```

Verify the generated object with

```console
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/verify_diag3_pair_fullsupport_labeled_skeleton.py
```

The verifier does not import the producer.  It independently rebuilds every
cell ID, strict face, orientation, chain rank, signature ordering, packed
profile assignment, and closed bad subcomplex, and rejects fourteen hostile
mutations.  The exact 1,237-root roadmap and 97,224-signature continuation are
authenticated accepted dependencies rather than rederived a third time; their
SHA-256 pins and semantic commitments are explicit in the new certificate.

The artifacts are

```text
data/DIAG3_PAIR_FULLSUPPORT_LABELED_SKELETON.json
data/DIAG3_PAIR_FULLSUPPORT_LABELED_SKELETON_PROFILES.json.gz
```
