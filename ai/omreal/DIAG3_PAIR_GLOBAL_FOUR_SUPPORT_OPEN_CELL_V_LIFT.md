# Exact open-base-cell `v` lift for the first four-support domains

## Result

The complete base CAD for the first two surviving four-support domains has
527,533 cells.  This checkpoint performs the first part of the final fiber
lift: every one of the 133,828 full-dimensional base cells lying over an open
`t` sector and an open `u` strip is lifted through all 22 original walls.

The cube coordinates are

```text
a = t + (1-t)u
g = t
h = t + (1-t)v
```

with `0<u,t,v<1`.  The transformed family has one wall independent of `v`,
20 linear walls, and one quadratic wall.  At the rational sample in each open
base cell, exact rational arithmetic orders every linear root and compares the
quadratic roots without floating point or a radical approximation.

```text
  1,694 open t sectors
133,828 open (t,u) base cells
  2,082 distinct ordered fiber signatures

2,181,404 interior v-root sections
2,315,232 open v-strips
4,496,636 lifted cells
```

Every open base cell has between 11 and 20 interior `v` roots.  The exact
census is:

| roots | base cells |
|---:|---:|
| 11 | 15,985 |
| 12 | 3,540 |
| 13 | 14,049 |
| 14 | 10,989 |
| 15 | 1,233 |
| 16 | 7,457 |
| 17 | 14,002 |
| 18 | 29,026 |
| 19 | 22,643 |
| 20 | 14,904 |

The 2,082 signatures replace a raw per-cell root catalog.  Thirty-two
deterministic gzip shards assign one signature to each open base cell.

## Bounded-fiber audit

The first projection already contains every coefficient, discriminant, and
pair resultant required to keep the fiber root order invariant.  A separate
endpoint audit now factors all 44 wall evaluations at `v=0` and `v=1`.
Every nonboundary factor occurs in the existing 114-factor base catalog or in
the exact `t`-projection catalog.  The only nontrivial endpoint cut that is not
itself a base curve is `2t-1`; it is already univariate factor 557, so
`t=1/2` is an existing algebraic section.  No bounded-fiber cut is missing.

## Trust boundary

The producer uses SymPy only for the 44 endpoint factorizations.  The fiber
scan itself uses exact `Fraction` arithmetic.  The independent verifier
imports neither SymPy nor the producer.  It:

1. multiplies every stored endpoint factorization back to the original wall
   evaluation using the committed base and univariate factor catalogs;
2. reconstructs all 1,694 rational `t` samples and all 133,828 rational open
   `u`-strip samples from the prior Sturm-isolated base lift;
3. recomputes all linear roots and compares the quadratic roots by exact sign
   tests around the vertex;
4. validates exact filenames, floor partitions, embedded metadata, coverage,
   canonical JSON, and deterministic gzip bytes for both 32-shard manifests;
   and
5. rejects 40/40 hostile claim mutations.

Replay:

```bash
PYTHONDONTWRITEBYTECODE=1 python ai/omreal/verify_diag3_pair_global_four_support_open_cell_v_lift.py
```

## Honest scope

This is not the complete `v` lift.  The 132,134 algebraic `u`-section fibers
over open `t` sectors remain, followed by every base cell over the 1,693
algebraic `t` sections.  Global gluing, closure data, extension-signature
labels, middle-rank replay, and the triple obligation also remain open.  The
honest 9DVL score remains **2/9**.

The next proof-bearing target is the algebraic `u`-section lift.  Its event
labels are already contained in the coefficient/discriminant/resultant
projection, so the intended certificate collapses exact collision groups and
records vertical or boundary events rather than rerunning a general CAD.
