# Diagonal three: exact source-staircase boxwise component coverage

## Result

Let `u,v,w` independently interpolate normalized moving-column blocks 6, 7
and 8 from row-2599 chart 0 toward chart 152.  The following five closed
boxes lie in the strict parent cell:

| box | `u` interval | `v` interval | `w` interval | volume | occurring | zero-free | graph type | triquadratic |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `x0` | `[0,1/8]` | `[0,1]` | `[0,1/64]` | `1/512` | 1,546 | 16,278 | 1,317 | 229 |
| `x1` | `[1/8,1/4]` | `[0,1]` | `[0,5/16]` | `5/128` | 2,069 | 15,755 | 1,780 | 289 |
| `x2` | `[1/4,3/8]` | `[0,1]` | `[0,5/8]` | `5/64` | 2,770 | 15,054 | 2,407 | 363 |
| `x3` | `[3/8,1/2]` | `[0,1]` | `[0,7/8]` | `7/64` | 3,300 | 14,524 | 2,883 | 417 |
| `x4` | `[1/2,1]` | `[0,1]` | `[0,1]` | `1/2` | 4,450 | 13,374 | 3,889 | 561 |

Their interiors are disjoint in `u`, and their total normalized parameter
volume is

```text
1/512 + 5/128 + 5/64 + 7/64 + 1/2 = 373/512.
```

Thus this parent-safe staircase covers about 72.85 percent of the naïve
hybrid cube by volume, compared with 50 percent for the earlier half-cube.
It contains the full source square at `w=0`, and `x4` is exactly the existing
half-cube.

Every one of the `5 x 17,824 = 89,120` box-factor restrictions is decided
exactly.  There are zero unresolved restrictions.  The union contains 5,106
distinct factors that occur on at least one box, while 12,718 factors are
zero-free on every staircase box.  Their factor-ID digests are

```text
e51aea503481b62b028dbf94628cbb629ab493ad41b08aa0143c9d82708ee357
2e6693ec80ada175f1b534f2b4155735a8281a79c692e3f7bc294e60bd6a5089
```

For every occurrence on every box, each connected component meets that
box's boundary.  Consequently every boxwise component reaches the declared
source skeleton formed by the union of all five box boundaries.

This is not a claim that every component of the zero set on the whole
staircase reaches the staircase's outer topological boundary: an internal
seam remains part of the declared skeleton.  It is also not a missed-component
theorem for the full nine-dimensional parent cell.  The honest 9DVL score
therefore remains `2/9`.

## Exact parent residence

All 70 signed parent brackets restrict trilinearly on each box.  The producer
and independent verifier evaluate the eight exact vertex values of every
restriction, for `350` parent-box restrictions and `40` strict vertices in
total.  Every value is positive.  Since the tensor Bernstein coefficients of
a trilinear polynomial are its vertex values, each complete box is contained
in the strict row-2599 parent cell.

The step heights are deliberately asymmetric.  The full `[0,1]^3` hybrid
cube is invalid at two vertices, but small `w` collars are parent-safe near
`u=0`, and the admissible height grows until the full `w` interval is safe on
`u >= 1/2`.  The chosen rational steps retain exact dyadic replay throughout.

## Exact wall feasibility

Every restriction has tridegree at most `(2,2,2)`.  Tensor Bernstein signs
prove a restriction zero-free, while an exact corner sign change or corner
zero proves occurrence.  Dyadic tensor subdivision is used only when the
initial box is inconclusive.  No classification is inferred from numerical
sampling, and any depth-limit survivor would abort the producer before it
wrote a certificate.

The five classification semantic digests, in box order, are

```text
61a61fb2eb81fd1f69739bc6dcd000a8acffcf0025b7459f784f8939badbdc6b
5030b7cc03a3ec3da99f27a2c5421a4e733e625c3889c9b43c3f3e0ad861b095
a7bf40a18f916a8e0d81404b901de4fdd8657cbf05686d9bec72eea3962b938e
c0a9dc2f09640a0ad688202fb6ec93c1d9b94ebfc0a1d6069d9ded22b0afe6e7
152c16f19053901214c455aa4281cb20c8c5b4c91adde999e4d30bd5c3c21637
```

## Component theorem with adaptive critical axes

The graph-type argument from the half-cube applies unchanged.  If a
restriction is affine in one parameter, a coefficient-drop zero supplies a
full boundary-reaching fiber; otherwise projection along that parameter is
locally a graph.  A hypothetical compact interior component would have a
nonempty image that is both open and compact in `R^2`, which is impossible.

This covers 12,276 graph-type box occurrences.  The remaining 1,859 box
occurrences are fully triquadratic.  Let `C` be a compact component of one
such zero set in a box interior.  Every coordinate attains an extremum on
`C`.  At an extremum of one coordinate, the polynomial and its derivatives
in the other two coordinates vanish; at a singular point the same system
also vanishes.  It is therefore enough to prove one of

```text
p = partial_v p = partial_w p = 0,
p = partial_u p = partial_w p = 0,
p = partial_u p = partial_v p = 0
```

empty on the closed box.  The verifier tries these systems in the displayed
order and accepts a factor only after one is excluded by exact tensor
Bernstein subdivision.

The first system closes 1,858 of the 1,859 cases.  On box `x3`, factor 9,954
survives that system's declared depth-five subdivision, so the certificate
does not deepen the same inconclusive test.  The second system is exactly
sign-excluded at depth zero.  The record preserves both the failed attempt
and the successful axis pair.  No adaptive critical system remains
unresolved, and no factor requires more than 48 total visited critical
subboxes.

The five critical semantic digests are

```text
4ccf29178a0000d9d7e5b520c034b3c8e5638272ed9210536b9df7dbd856cdd5
03dd4e5ae288a36127fa7d89c3a800f7f9ded8d55d829c1a6597da2aefb4a5b5
e3c26fbfe2254a590b81a23fca668dea56f13073a9cea997c51a6ce1e3993fac
02f44a46d7a0f090bea63d3c1ca8d82ec1294c136695b4d5bff484c1eadc8ae6
23d4c04c8809405b2b8a204cc683e6faf3fb182d155709019d622f2bcae4835a
```

## Replay and next gate

Build the compact record with

```bash
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/build_diag3_pair_source_staircase_coverage.py
```

and run the independently coded hostile replay with

```bash
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/verify_diag3_pair_source_staircase_coverage.py
```

The verifier reconstructs the parent restrictions, all 89,120 factor
pullbacks, classifications, adaptive critical systems, union accounting and
digests without importing the producer core.  It rejects 14 corruptions,
including false full-parent and outer-boundary coverage, a full-cube endpoint
mutation, and deletion of the adaptive-axis witness.

The next pair-side gate is a missed-component theorem showing that every
full-parent wall component meets a certified source skeleton, or another
exact source-volume family that strictly enlarges this skeleton toward that
goal.  Only after global incidence coverage exists can the labelled relative
master complex and its middle-rank replay close the pair obligation.
