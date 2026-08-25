# Exact three-block source bridge from row-2599 chart 0 to chart 152

## Result

The exact row-2599 source-transition skeleton now reaches a germ that was
isolated in the straight-segment census.  Chart 152 has degree zero in the
105-edge graph on the 178 stored exact germs, but it is connected to chart 0
by replacing the three moving columns one at a time:

```text
chart 0
  -> replace column 6 by its chart-152 value
  -> replace column 7 by its chart-152 value
  -> replace column 8 by its chart-152 value
  = chart 152.
```

All four waypoints are strict row-2599 parent realizations.  Every segment
changes only one projective point, so each of the 70 parent brackets restricts
affinely.  Exact rational endpoint signs and an independent Bernstein replay
prove every bracket stays strict on every closed segment.

This embeds one formerly isolated germ and glues the bridge to the already
labelled chart-0-to-chart-89 path at their exact common chart-zero vertex and
raw 26,112-label set.  It is not a parameter-space cover and does not change
the honest 9DVL score from **2/9**.

## Objective selection

The old 105-edge straight graph is a forest with 73 components:

| component size | count |
|---:|---:|
| 105 | 1 |
| 2 | 1 |
| 1 | 71 |

For every straight-isolated germ, the verifier tests the eight vertices
obtained by independently choosing each moving-column block from chart 0 or
that germ.  A path through this three-cube gives a three-segment
one-column-at-a-time bridge.  Six isolated germs admit such a direct bridge.

The deterministic selection rule first minimizes the certified segment count,
then the exact endpoint factor-state Hamming distance, then the chart index.
Three segments are the minimum possible because all three moving columns
differ.  Chart 152 wins with Hamming distance **3,384**.

## Complete residual roadmap

Every one of the 17,824 candidate residual factors is restricted to all three
segments and screened by exact Sturm counts.  The census is:

| segment | zero roots | one root | two roots | ordered events |
|---:|---:|---:|---:|---:|
| replace column 6 | 15,059 | 2,756 | 9 | 2,774 |
| replace column 7 | 16,808 | 1,015 | 1 | 1,017 |
| replace column 8 | 16,008 | 1,811 | 5 | 1,821 |
| **total events** |  |  |  | **5,612** |

All four waypoints avoid every candidate residual wall.  All 5,612 roots are
simple sign crossings and have pairwise ordered rational isolating intervals
within their segment, each of width at most `2^-28`.  The event multiplicity
census is

```text
5,319 x 1,  66 x 2,  46 x 15,  181 x 65.
```

Applying the ordered flips reconstructs the independently stored chart-152
factor state exactly.  The induced regular-CW path has 5,616 zero-cells, 5,615
one-cells, 11,231 cells in total, and 11,230 strict closure pairs.  Its parent
infinity subcomplex is empty.

The event semantic digest is

```text
7a80560cfc7544f1d114b33c2c9205d35a09400d6385029f2a93e05fe6f50102
```

## Replay and trust separation

```bash
python ai/omreal/build_diag3_pair_parent_source_block_bridge.py
python ai/omreal/verify_diag3_pair_parent_source_block_bridge.py
```

The hostile verifier rebuilds the straight-component audit, objective bridge
selection, exact parent residence, chart-zero label overlap, all 53,472
factor-segment restrictions, all root boxes, the CW counts, and the endpoint
state.  It rejects 12 corruptions, including sampled coverage promoted to a
global claim, a dishonest target choice, a lost parent bracket, a corrupt
overlap label set, missing or noncrossing events, false parent infinity, and
incomplete closure.

## Consequence and completed successors

The straight forest was a coordinate artifact, not an obstruction: exact
one-column block moves connect chart zero directly to six of its 71
straight-isolated germs.  The selected bridge is the first certified edge of
that enlarged source complex.

Complete 26,112-label continuation across all 5,612 events is now certified in
`DIAG3_PAIR_PARENT_SOURCE_BLOCK_LABELS.md`. The source complex also now reaches
the genuine parent divisor `[1237]=0` through the fully labelled chart-89
attachment in `DIAG3_PAIR_PARENT_BOUNDARY_ATTACHMENT.md`.

These successors close the declared path-label and first-boundary-attachment
tasks. Neither a finite germ graph nor finitely many labelled paths supplies
global row-2599 coverage by itself. The remaining pair target is an exact
missed-component certificate or an equivalent coverage-certified global
master complex.
