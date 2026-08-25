# Diagonal three: complete second projection for the four-support base

## Result

The 136 exact `(u,t)` polynomials from the first four-support fiber projection
have a bounded complete second projection. Exact factorization over the
rationals gives

```text
136 source polynomials
135 nonconstant source polynomials
170 factor occurrences
114 distinct base curve factors
```

Every stored factorization is replayed up to a nonzero rational scalar by a
standard-library verifier. No factorization claim is accepted from a sampled
zero set.

## Projection to the `t` axis

For the 114 base factors, the certificate constructs the complete
coefficient/discriminant/pair-resultant family with respect to `u`:

| obligation | nonconstant count |
|---|---:|
| coefficients | 128 |
| discriminants | 69 |
| pair resultants | 5,864 |
| total | **6,061** |

No pair resultant vanishes identically. After removing the true square
boundary factors `t` and `1-t`, taking squarefree parts, and identifying
scalar associates, the family has only **2,554 distinct univariate
polynomials**. Their stored exact factorizations use **2,333 distinct factor
polynomials**.

The factor-degree census is:

| degree | factors |
|---:|---:|
| 1 | 44 |
| 2 | 198 |
| 3 | 417 |
| 4 | 605 |
| 5 | 597 |
| 6 | 282 |
| 7 | 134 |
| 8 | 36 |
| 9 | 17 |
| 10 | 3 |

Thus the maximum univariate degree is ten. The primitive factor coefficients
need at most ten bits.

## Exact interior-root frontier

An independently written standard-library Sturm replay counts roots in
`0<t<1` for every stored factor:

| interior roots in one factor | factor count |
|---:|---:|
| 0 | 891 |
| 1 | 1,200 |
| 2 | 233 |
| 3 | 9 |

The sum is **1,693 factor-root incidences**. It is also an exact upper bound
on the number of distinct interior `t` sections; shared algebraic roots can
only lower the number of distinct sections. This checkpoint does not yet
claim those roots are isolated, ordered, or deduplicated.

## Trust boundary

The producer uses exact SymPy factorization and resultants to write a compact
factor catalog. The verifier does not import that producer or SymPy. It:

1. reconstructs the 136 first-projection polynomials;
2. multiplies the 114 stored base factors back to every source polynomial;
3. recomputes all coefficients, discriminants, and pair resultants with an
   exact fraction-free Sylvester determinant;
4. recomputes the 2,554 squarefree boundary-reduced projection polynomials;
5. multiplies the 2,333 stored univariate factors back to every projection
   polynomial; and
6. replays all 1,693 root incidences with rational Sturm sequences.

Twelve hostile semantic mutations must all be rejected.

## Consequence and next gate

The second projection remains far below the pinned ceiling:

```text
2,554 distinct squarefree projection polynomials < 100,000 ceiling
```

The next exact construction is to isolate and order the at-most-1,693
interior `t` sections, lift the 114 base factors in `u`, and then lift the 22
original walls in `v`. This certificate proves that the full projection
frontier is finite and tractable; it does not construct the base CAD, regular
cells, global closure data, or the diagonal-three invariant. The honest 9DVL
score remains `2/9`.

## Replay

```bash
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/build_diag3_pair_global_four_support_base_projection.py

PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/verify_diag3_pair_global_four_support_base_projection.py
```
