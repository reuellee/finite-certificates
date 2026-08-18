# Diagonal three: exact Bernstein pruning on every compactification face

## Result

The first deterministic layer of the row-2599 regular-cell generator is now
complete.  It eliminates `42,547,692` of the `60,156,000` candidate
factor--face obligations before any recursive subdivision, leaving exactly
`17,608,308` mixed Bernstein restrictions.

This is a `70.7289%` proof-safe reduction.  It applies simultaneously to all
`17,824` candidate residual factors and all `3,375` support strata of the
pinned compactification

```text
(Delta^3)^3.
```

It is not a global regular-cell universe.  The remaining mixed restrictions
are precisely the face-level inputs on which an adaptive exact subdivision
or a stronger positivity certificate may spend effort.

## Canonical multihomogenization

In the standard chart the three moving columns are

```text
(1,a,b,c), (1,d,e,f), (1,g,h,i).
```

For a residual factor `F`, let `(r,s,t)` be its maximum degree in these three
variable blocks.  Every candidate has `0 <= r,s,t <= 2`.  Fill the degree
deficit of each affine monomial with the corresponding row-one homogeneous
coordinate.  This gives a canonical multihomogeneous polynomial of degree
`(r,s,t)` on the product of simplices.  Multiplication by the positive chart
gauges preserves its zero set and sign.

On a support face, discard each monomial using a homogeneous coordinate that
is zero there.  The surviving homogeneous monomials are the product-simplex
Bernstein basis up to positive multinomial factors.  Therefore exactly one
of three proof states holds:

1. no coefficient survives: `F` vanishes identically on the relative face;
2. only one coefficient sign survives: `F` is strictly sign-definite and its
   wall misses the relative face;
3. both signs survive: the restriction is mixed and remains active.

The third state is deliberately one-sided.  Mixed Bernstein coefficients do
not prove that a zero exists.  They only prohibit this first sign-definite
pruning rule from deleting the task.

## Exhaustive census

The exact state totals are

| state | factor--face pairs |
|---|---:|
| identically zero | 34,437,486 |
| sign-definite / wall-free | 8,110,206 |
| mixed / active | 17,608,308 |
| total | 60,156,000 |

All 64 vertices have zero active residual factors.  Across the full face
atlas, the active-factor count ranges from `0` to `17,824`.  The 3,375 faces
produce 3,240 distinct active-factor sets, so identical downstream inputs
may be shared without identifying geometrically distinct faces.

The calculation also proves that all 17,824 candidate polynomials have
distinct signed face profiles.  Thus factor identification is not a safe
compression at this layer.  The compression is instead the deletion of
zero and sign-definite factor--face pairs.

The canonical state stream has digest

```text
292b16a874914134657a6d09a26d5bdde239d2e6989fe7c23234b90ac698f82b.
```

The manifest semantic digest is

```text
1bd501a4a2b08eebd55d39c078fed07c526308a53bbefb21823531843ca0da8b.
```

## Consequence for the generator

The global generator must no longer treat the 17,824 factors as active on
every simplex face.  The parent-feasibility successor now eliminates 3,364
of the 3,375 support strata and reduces the mixed residue to 70,218.  See
`DIAG3_PAIR_GLOBAL_PARENT_FACE_GATE.md`.  On the remaining strata its next
deterministic block is:

1. inherit the exact three-state table on every support face;
2. recursively subdivide only mixed restrictions on parent-nonempty faces,
   using rational
   face-compatible Bernstein transformations;
3. stop a branch when every inherited factor is zero or sign-definite;
4. retain every structurally zero factor as a closed wall label;
5. independently verify that sibling cells cover their parent, share
   identical restricted data on common faces, and introduce no artificial
   infinity.

The eventual master-cell certificate still needs exact wall cells,
regular-ball closures, all strict closure pairs and triples, signature
labels, and the genuine infinity subcomplex.  None is inferred from the
pruning census alone.

## Replay

```bash
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/verify_diag3_pair_global_face_bernstein_atlas.py
```

The replay regenerates every multihomogeneous support restriction from the
hash-pinned factor census and candidate list; no sampled signs are used.
