# Diagonal three: exact row-2599 compactification atlas

## Result

The ambient compactification atlas required before a global master-cell
generator is now fixed.

After normalizing the first five columns, the three moving columns `6,7,8`
are projective points with four positive homogeneous coordinates.  The exact
parent-2599 chirotope calculation gives

```text
column 6: + + + +
column 7: + + + +
column 8: + + + +
```

and exact Cramer normalization independently verifies this for all 178
stored parent-2599 sample matrices.  The closed positive projective orthant
of one column is a 3-simplex.  Therefore the chosen compactification is

```text
Delta^3 x Delta^3 x Delta^3.
```

## Finite chart cover

Choose one of the four positive homogeneous coordinates as gauge for each
moving column.  This gives `4^3=64` charts, each with nine affine ratio
coordinates.  On the overlap of gauges `r` and `s`, one column transforms by

```text
v_k = u_k/u_s.
```

The verifier enumerates all 4,096 ordered chart transitions and all 262,144
ordered product-chart triples.  Their Laurent exponent maps satisfy the
cocycle identities exactly.

The ambient face-support poset has `15^3=3,375` strata.  Relative to the
standard row-one gauge chart, 2,863 strata lie at affine infinity.

## Infinity is genuine parent boundary

Every homogeneous coordinate divisor is exactly a parent bracket, up to the
fixed determinant sign.  For example, the three standard-chart infinity
divisors are

```text
x_1(column 6)=0  <=>  [2346]=0,
x_1(column 7)=0  <=>  [2347]=0,
x_1(column 8)=0  <=>  [2348]=0.
```

All twelve coordinate divisors are checked.  Thus every escape from the
standard affine normalization lands on a genuine parent-wall face; this
compactification introduces no artificial local-scope infinity.

The machine-readable atlas is
`data/DIAG3_PAIR_GLOBAL_row2599_compactification_atlas.json`, with semantic
digest

```text
3ea49efc628a88fda99e4070cbf43317b78cc45813beaba753c4404e961fa769.
```

## Exact scope and next block

This closes the compactification-atlas choice and its overlap/infinity
coverage.  It does not yet subdivide the parent cell by the 17,824 candidate
residual factors.  The next generator input is now completely specified:

1. the 64 compactification charts and their genuine parent-boundary faces;
2. the independently verified 17,824-factor candidate list; and
3. the exact sparse factor polynomials already stored in the global census.

The first deterministic generator layer is now complete.  Exact
multihomogeneous Bernstein restrictions eliminate 42,547,692 of 60,156,000
candidate factor--face tasks on this atlas.  The next mathematical target is
parent-feasibility restriction of the face atlas.  That successor now proves
that only eleven support strata are nonempty and leaves 70,218 mixed
restrictions.  The next unresolved support dimension is four.  See
`DIAG3_PAIR_GLOBAL_FACE_BERNSTEIN_ATLAS.md` and
`DIAG3_PAIR_GLOBAL_PARENT_FACE_GATE.md`.

## Replay

```bash
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/verify_diag3_pair_global_compactification_atlas.py
```
