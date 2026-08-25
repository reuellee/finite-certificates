# Diagonal three: eight-box source staircase and exact yield gate

## Result

Let `u,v,w` independently interpolate normalized moving-column blocks 6, 7
and 8 from row-2599 chart 0 toward chart 152.  The following eight closed
boxes lie in the strict parent cell:

| box | `u` interval | `w` height | occurring | zero-free |
|---|---:|---:|---:|---:|
| `s00` | `[0,1/16]` | `9/512` | 1,320 | 16,504 |
| `s01` | `[1/16,2/16]` | `103/512` | 1,677 | 16,147 |
| `s02` | `[2/16,3/16]` | `379/1024` | 1,982 | 15,842 |
| `s03` | `[3/16,4/16]` | `539/1024` | 2,314 | 15,510 |
| `s04` | `[4/16,5/16]` | `343/512` | 2,637 | 15,187 |
| `s05` | `[5/16,6/16]` | `823/1024` | 2,956 | 14,868 |
| `s06` | `[6/16,7/16]` | `475/512` | 3,232 | 14,592 |
| `s07plus` | `[7/16,1]` | `1` | 4,610 | 13,214 |

The `v` interval is `[0,1]` in every box.  Their interiors are disjoint in
`u`, and their exact total normalized volume is

```text
12817/16384 = 0.78228759765625.
```

Exact height comparison on the common rational `u` partition proves that
this region contains the previous five-box staircase of volume `373/512`.
All `8 x 70 = 560` parent restrictions are trilinear and positive at all 64
box vertices.  Tensor Bernstein replay decides all
`8 x 17,824 = 142,592` box-factor restrictions with zero unresolved.

The union contains 5,139 distinct occurring factors, while 12,685 are
zero-free on every box.

## True outer-boundary coverage

The separate ambient full-hybrid-cube theorem proves that every connected
component of every occurring restricted wall on `[0,1]^3` meets the cube
boundary.  Its semialgebraic path-transfer lemma applies to this closed
parent-safe staircase.  Therefore every component inside the staircase meets
the staircase's true outer boundary.  Internal box seams are not part of the
conclusion and are not needed as a proof device.

This is still one three-parameter source family.  The certificate does not
show that every component of a wall in the full nine-dimensional row-2599
parent cell intersects this family.  The global missed-component theorem and
labelled relative master complex remain open, so the honest 9DVL score stays
`2/9`.

## Exact yield and stop rule

The exact volume increase over the five-box staircase is

```text
12817/16384 - 373/512 = 881/16384.
```

Because the new region contains the old one, its occurring factor set also
contains the old set.  The distinct occurring count rises only from 5,106 to
5,139: exactly 33 additional factors for about 5.38 percentage points of
normalized volume.

That triggers the predeclared strategic stop.  A 32- or 64-step height
refinement would spend substantially more exact replay on a local sufficient
reduction while the invariant obstruction remains unchanged.  Further
dyadic staircase refinement is subordinated until a new theorem makes source
volume—not global component incidence—the load-bearing quantity.

## Why eight boxes, not sixteen

Initial reconnaissance used sixteen `u` slabs.  It showed that the full `w`
interval is already parent-safe from `u=7/16` onward.  Since every parent
restriction is trilinear, the final nine full-height slabs can be replaced by
the single box `[7/16,1] x [0,1] x [0,1]`.  The consolidation preserves exact
volume and parent residence while cutting the factor-restriction workload in
half and deleting eight artificial seams.

## Replay

Build the record with

```bash
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/build_diag3_pair_source_staircase8_coverage.py
```

and run the independently coded hostile replay with

```bash
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/verify_diag3_pair_source_staircase8_coverage.py
```

The verifier reconstructs all parent restrictions, 142,592 factor pullbacks,
exact classifications, union accounting, containment, ambient-topology
dependency, and semantic digests without importing the producer core.  It
also rejects mutations that restore internal seams, inflate yield, revive the
stopped refinement, or claim global parent-cell coverage.
