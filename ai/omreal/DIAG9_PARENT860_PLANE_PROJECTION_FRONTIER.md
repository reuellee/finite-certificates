# Diagonal 9: exact parent-860 plane projection frontier

## Result

The exact transverse node has now been expanded to the first complete
coverage calculation on its selected `(h,i)` plane.  Holding the other seven
normalized parent coordinates fixed, all 70 parent brackets cut out the open
triangle

```text
L < i < h < U,
L = 12164/31931,
U = 1858210/2854579.
```

Its closure has vertices `(L,L)`, `(U,L)`, and `(U,U)`.  The 70 brackets
collapse to 31 distinct affine halfspaces; exact pairwise intersection and a
recession-cone check prove that no boundary edge or direction is missing.

Exact restriction of all 26,740 primitive global residual factors gives

```text
 1,990 constant restrictions
24,750 distinct nonconstant restrictions
12,405 irreducible lines
12,345 nonsingular irreducible conics
```

Every quadratic has nonzero projective conic determinant, so irreducibility
does not depend on heuristic factorization.  Exact quadratic optimization on
the triangle—vertices, edge stationary points, and the unique interior
stationary point when present—then gives

```text
23,005 nonconstant factors with a strict constant sign on the closed triangle
   192 factors meeting only the parent boundary
 1,553 factors meeting the open parent triangle
```

Together with the 1,990 constants, this proves that 24,995 of the 26,740
global factor walls do not meet the open selected slice.  The result is a
complete plane-factor classification, not a chamber atlas.

## Exact interaction prefilter

Every surviving restriction has degree at most two.  The parent triangle was
therefore subdivided into `4^8 = 65,536` exact dyadic subtriangles.  On every
leaf, the six degree-two triangular Bernstein control coefficients give a
complete constant-sign exclusion.  This produces

```text
1,553 open-triangle factors
1,205,128 possible unordered curve pairs
  727,317 pairs excluded by disjoint exact Bernstein covers
  477,811 candidate pairs
```

There are 455,093 factor/leaf incidences, 65,444 occupied leaves, and at most
71 factors in one leaf.  If two curves meet in the open triangle, they must
occur together in at least one stored leaf; thus the discarded 727,317 pairs
are rigorously impossible, not sampling misses.

## Pair-resultant frontier

Closed affine/quadratic formulas compute the exact resultant in `i` for all
477,811 candidate pairs.  A randomized 200-case SymPy comparison was used as
a development cross-check; the committed producer itself uses only integer
and rational arithmetic.  The exact census is

```text
     22 constant resultants
     38 vertical/vertical nonintersections
477,751 nonconstant resultant occurrences
396,369 distinct primitive resultants
```

The distinct degree profile is

| degree in `h` | distinct resultants |
|---:|---:|
| 1 | 69,508 |
| 2 | 179,473 |
| 3 | 88,962 |
| 4 | 58,426 |

Primitive coefficients need at most 188 bits.  Exact Sturm replay strips the
two horizontal endpoints and proves

```text
393,522 resultants with at least one root in L < h < U
385,034 with one root
  8,467 with two roots
     21 with three roots
402,031 total open horizontal roots counted per primitive polynomial
```

A horizontal resultant root is only a necessary condition for a common
`i`-coordinate in the triangle.  Common-`i` validation, cross-polynomial root
deduplication, isolation, chamber construction, labels, and connectivity all
remain open.

## Decision and proof boundary

The predeclared projection-growth stop rule is triggered.  A direct monolithic
plane CAD is no longer the next atomic target: the exact frontier contains
almost four hundred thousand root-bearing projection polynomials.  This does
not falsify the atlas strategy, but it requires deterministic shards and an
additional common-coordinate filter before cell construction.

The next bounded target is therefore:

1. shard the 393,522 root-bearing resultants deterministically;
2. isolate and deduplicate their algebraic `h` roots exactly;
3. validate whether each root carries a common `i` in `L<i<h`;
4. stop with an exact surviving event catalog before lifting any chambers.

The parent-860 plane still lacks a coverage-certified labeled chamber atlas,
genuine parent infinity attachments, and all-family connectivity.  No other
parent is covered.  The honest 9DVL score remains **2/9**.

## Verification

Build or replay the complete projection frontier:

```console
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/DIAG9_GRAPH_parent860_plane_resultant_frontier.py --build

PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/DIAG9_GRAPH_parent860_plane_resultant_frontier.py
```

Independently reconstruct the parent triangle, all factor restrictions,
irreducibility certificates, and exact range classification:

```console
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/verify_diag9_parent860_plane_projection.py
```

The independent verifier imports none of the three producer stages and
rejects hostile in-memory summary and factor-class mutations.  The semantic
certificate digest is

```text
cbcee4e0e7a7e757b9751f06349337d14206e102e4afaffd5abdd3833718a0fd
```

