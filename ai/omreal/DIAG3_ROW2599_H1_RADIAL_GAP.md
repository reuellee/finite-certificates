# Diagonal three: exact row-2599 H1 radial-gap checkpoint

## Outcome

The literal copy of the certified `H2` construction does **not** produce the
missing `H1` comparison prism.  Its four trivariate patches satisfy every
parent sign condition and retain an exact positive block-one Gordan circuit,
but the second radial `p01` boundary stage is not contained in parent
infinity.  The construction therefore fails closed and the comparison count
remains `4/6`.

This is a sharper obstruction than a failed numerical search.  Two exact,
independently implemented verifiers agree on the four positive patches and
on the missing relative wall.

## Candidate construction

Use the same square of root amplitudes as the `H2` prism, now on roots `p01`
and `p12`.  The four patches are indexed by two frontier edges and two common-
parameter stages.  Exact tensor Bernstein coefficients prove:

* all 70 signed parent brackets are nonnegative on every patch;
* the block-one circuit on support `(2,9,27,30,35)` is nonnegative and not
  identically zero;
* the two internal common-parameter faces cancel literally;
* the two frontier-edge faces cancel literally; and
* the external faces are exactly the generic two-stage `p01` disk and the
  already certified two-stage `p12` disk.

The weak parent-wall censuses of the four candidate patches are

```text
edge 0, stage 0 : [1234] [1358]
edge 0, stage 1 : [1234] [2467] [1358]
edge 1, stage 0 : [1234] [2467] [1358]
edge 1, stage 1 : [1234] [2467] [1358]
```

These checks show that the interior algebra is not the obstruction.

## Literal relative-boundary failure

The generic radial `p01` collar has two stages.  Their identically-zero
parent-wall census is

```text
stage 0 : [1234]
stage 1 : none
```

Thus the second stage connects a `[1234]` endpoint to a `[2467]` endpoint
through the parent interior.  It is not a relative chain.

The actual certified `p01` disk uses the five-stage nonradial collar

```text
[1234], [1234], [1367], [2467], [2467].
```

Every one of those stages lies in a genuine parent wall, but that five-stage
disk is not the literal external face of the four-patch radial construction.
Replacing it silently would break the already fixed `Q(p01,block1)` gluing.
Consequently the hoped-for signed boundary

```text
+K(h1) - Q(p01,block1) + Q(p12,block1)
```

has not been constructed.

## Replay

```bash
PYTHONDONTWRITEBYTECODE=1 \
  python ai/omreal/verify_diag3_row2599_h1_radial_gap.py

PYTHONDONTWRITEBYTECODE=1 \
  python ai/omreal/review_scratch/DIAG3_HOSTILE_VERIFY_ROW2599_H1_RADIAL_GAP.py
```

The producer-side semantic digest is

```text
046e51a271bf169c499e3473d5bf399724f6e22a23612a7b2d31ef660c01cbcc
```

and the independent dense-polynomial replay digest is

```text
7f8b7ac35c9f6a7e5580ec40ccde6140b95814ac6a25b2051fb83f01a603eee7
```

## Honest status

No comparison incidence, mixed `d3` cell, triple orbit, or theorem ledger
entry changes.  A future `H1` certificate must provide a literal
compatibility homotopy from the five-stage `p01` disk, including the
`[1367]` detour, to the `p12` disk.  A second radial-copy attempt should not
be repeated.
