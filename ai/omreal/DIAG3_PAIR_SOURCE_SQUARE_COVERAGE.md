# Diagonal three: exact source-square wall-component coverage

## Result

The labelled row-2599 source complex now contains a complete two-parameter
component-coverage object.  Start at stored chart `0`, replace normalized
moving-column blocks `6` and `7` independently by their chart-`152` values,
and keep block `8` at its chart-`0` value.  The resulting closed unit square
lies entirely in the strict parent cell.

Every one of the `17,824` full-support residual candidates is classified
exactly on this square:

| class | count |
|---|---:|
| zero-free by constant or adaptive Bernstein certificate | `14,061` |
| occurs by an exact rational sign-changing box | `3,763` |
| unresolved | `0` |

More strongly, every connected component of every occurring wall meets the
boundary of the square.  This is the first source-to-source component-coverage
certificate in the project.  It is not a decomposition of the full wall
arrangement and is not global coverage of the nine-dimensional parent cell,
so the honest 9DVL score remains `2/9`.

## Exact parent coverage

Each of the `70` signed parent brackets restricts to a polynomial of degree at
most one in each square parameter.  Its tensor Bernstein coefficients are
therefore exactly its four corner values.  All four are strictly positive for
all `70` brackets.  The bidegree census is

```text
(0,0): 17,  (0,1): 19,  (1,0): 19,  (1,1): 15.
```

The smallest signed corner value belongs to `[1268]` and equals

```text
1066724866772451496969732096
------------------------------------- .
1456676456613330116338348238405
```

Thus the entire square, not only its four corners or boundary paths, lies in
the strict row-2599 parent cell.

## Exact wall feasibility

Every residual restriction has bidegree at most `(2,2)`.  Tensor Bernstein
coefficients certify `14,051` walls zero-free on the whole square.  Six more
become sign-definite after one dyadic subdivision, and four restrictions are
nonzero constants.  Exact rational corner signs prove the remaining `3,763`
walls nonempty.  Only fifteen require any subdivision, and the deepest
sign-changing witness occurs at depth three.

The active and zero-free factor-ID digests are respectively

```text
77d71cfc487a370c349d1277714ba033b2e60887a7df50e3518ec367ca49f02a
0a567014f5f59c950a3b48470e712b3b6e8f046a558b288fbeb948ad9fd32df5
```

## Why no wall component is missed

Of the `3,763` occurring restrictions, `2,531` have degree at most one in one
parameter.  Their zero sets are rational graph components, with any
coefficient-drop fiber extending to the square boundary; they cannot contain
an interior compact component.

For each of the remaining `1,232` biquadratics write

```text
p(s,t) = a(s)t^2 + b(s)t + c(s)
```

and form the exact projection discriminant

```text
D(s) = b(s)^2 - 4a(s)c(s).
```

All `1,232` discriminants are squarefree and nonzero at `s=0,1`.  Their
numbers of distinct roots in `(0,1)` are

```text
0 roots: 1,009,  1 root: 181,  2 roots: 42.
```

There is no interval bounded by two interior discriminant roots on which
`D>0`.  A compact interior component would attain both its minimum and
maximum `s` values at projection-critical points, and squarefreeness would
make `D` strictly positive between those two roots.  The exact census rules
this out.  It also rules out isolated singular points: a singular point of a
quadratic fiber forces a repeated discriminant root.  Consequently every
wall component meets the square boundary.

## Why the full arrangement is subordinated

The four square edges have complete exact Sturm root censuses.  All isolated
single-root boxes are pairwise disjoint and every root used below is simple.
Two especially clean arc families give a rigorous arrangement-complexity
lower bound:

| arc family | walls | reversed endpoint pairs forced to intersect |
|---|---:|---:|
| left-to-right, no top/bottom roots | `220` | `11,060` |
| bottom-to-top, no left/right roots | `1,903` | `607,060` |
| **disjoint total** |  | **`618,120`** |

For two arcs in the same family, reversed boundary order forces an interior
intersection.  The count is a lower bound on distinct **curve pairs** that
intersect, not on distinct intersection points or CW zero-cells: several
curves may meet at one point.

This result makes a complete sign-invariant arrangement on the square the
wrong next object.  The useful quotient is component coverage itself: it
certifies that no wall component is missed without materializing hundreds of
thousands of forced pair incidences.

## Replay and scope

Build the compact record with

```bash
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/build_diag3_pair_source_square_coverage.py
```

and run the independent hostile replay with

```bash
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/verify_diag3_pair_source_square_coverage.py
```

The certificate proves complete parent residence and wall-component coverage
on this one source square.  It does not prove that every component in the
full nine-dimensional parent cell meets the current source complex, does not
construct the global pair-to-triple incidence complex, and does not address
the independent `1,162,302`-row triple compact-component residue.
