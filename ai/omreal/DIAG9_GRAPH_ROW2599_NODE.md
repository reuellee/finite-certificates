# Diagonal 9: an exact transverse two-wall disk in parent 2599

## Status

This artifact proves a complete local statement, not the ninth diagonal:

> In an explicitly embedded rational two-disk in the realization space of
> catalog parent 2599, the residual arrangement consists of exactly two
> transverse smooth wall arcs.  Exact labels on its four chambers, four open
> wall rays, and central node show that the common feasibility locus of every
> finite family of signatures is connected or empty within this disk.

The disk is the first certified row-2599 roadmap containing two **distinct
global residual walls** and a genuine codimension-two crossing.  It exercises
the local gluing and graph-certificate machinery that a global roadmap would
need.

The exact replay is

```bash
python ai/omreal/DIAG9_GRAPH_verify_row2599_node.py
python ai/omreal/DIAG9_GRAPH_verify_tree_certificate.py \
  ai/omreal/data/DIAG9_GRAPH_row2599_node_graph.npz
python ai/omreal/DIAG9_GRAPH_cut_sat.py \
  ai/omreal/data/DIAG9_GRAPH_row2599_node_graph.npz
```

No floating point calculation is used for a verdict.

## The embedded disk

Start with exact chart 0 in the 178-chart bank for parent 2599.  Let `s` be
the increment in matrix position `(2,7)` and `u` the increment in `(1,7)`,
using zero-based indices.  The node is

\[
 s_0=
 \frac{5455638564396767806348493946599}
      {3394705968860801647269075678720},\qquad
 u_0=
 \frac{1631359879664336977038655284413}
      {1697352984430400823634537839360}.
\]

The closed disk used here is the coordinate square

\[
  D=\{(s,u): |s-s_0|\le 10^{-3},\ |u-u_0|\le 10^{-3}\}.
\]

It embeds in projective moduli.  The first four columns form a fixed
projective frame, the fifth fixed column kills the diagonal frame torus, and
the fixed nonzero row-zero entry of column eight fixes its proportionality
scale.  Consequently two points of `D` cannot be projectively equivalent
unless their `(s,u)` coordinates agree.

## The two exact walls

Exactly 130 of the 84,840 labeled residual determinants vanish at the node.
They split into two disjoint groups of 65.  After exact division, their
primitive branch factors are

\[
\begin{aligned}
 q_0(s,u)&=-8406719710014481
 +5934554455910656s-1176454877277824u,\\
 q_1(s,u)&=-30838233534021888
 +9738264925739162s+15802240330472297u.
\end{aligned}
\]

Both vanish exactly at `(s_0,u_0)`.  Their coefficient determinant

\[
\det\begin{pmatrix}
5934554455910656&-1176454877277824\\
9738264925739162&15802240330472297
\end{pmatrix}
\]

is a nonzero integer, so the branches are coprime and transverse.  Neither
line passes through a corner of `D`.

For each branch, exact polynomial division gives 32 constant quotients and
33 affine quotients.  Centered monomial bounds certify all required
nonvanishing statements on the whole closed disk:

| Polynomial family | Number | Minimum exact dominance ratio |
|---|---:|---:|
| Residuals not through the node | 84,710 | `59660984923497009863930871344289908850373956705025 / 11076265907589991762853491013495358778478172987792` |
| Quotients along `q_0` | 65 | `31070614434869202946595039532555983225 / 13821290749269089346732496445232576` |
| Quotients along `q_1` | 65 | `55464724498960225839079342532405821625 / 22131106622794224179041285072279296` |
| 70 parent brackets | 70 | `31070614434869202946595039532555983225 / 13821290749269089346732496445232576` |

Every displayed ratio is strictly larger than one.  Thus no other residual
wall enters `D`, neither branch gains an extra component, and the entire
disk stays inside the strict parent-2599 realization cell.  The arrangement
on `D` is therefore exactly a transverse pair of line segments.

## Complete labels and adjacency

The exact central-arrangement recursion enumerates all extension signatures
at rational samples on every stratum:

| Stratum | Count | Signatures per stratum |
|---|---:|---:|
| Open chambers | 4 | 26,112 |
| Open wall rays | 4 | 26,040 |
| Transverse node | 1 | 25,968 |

Each open wall label set is exactly the intersection of its two adjacent
chamber label sets.  The node label set is both the intersection of all four
chambers and the intersection of every pair of open-wall label sets.  This
is an exact verification of the generic wall-gluing rule at a transverse
codimension-two stratum.

Number the chambers cyclically so their `(q_0,q_1)` signs are

\[
 (+,+),\quad (+,-),\quad (-,-),\quad (-,+).
\]

Among the 26,256 signatures appearing somewhere in `D`, exact support masks
have multiplicities

| Chamber mask | Multiplicity |
|---:|---:|
| `1111` | 25,968 |
| `0011` | 72 |
| `0110` | 72 |
| `1100` | 72 |
| `1001` | 72 |

Thus every non-full signature occupies one edge of the chamber four-cycle.
The closure under arbitrary intersections is exactly

```text
0000, 0001, 0010, 0011, 0100, 0110, 1000, 1001, 1100, 1111.
```

Every nonzero mask in this list induces a connected subgraph of the
four-cycle.  This proves the stated local theorem for **every finite family**,
not only for nine-element antichains.

The exported graph uses cycle edges

```text
(0,1), (1,2), (2,3), (0,3)
```

and spanning-tree edges `(0,1),(1,2),(2,3)`.  Both the sharp pairwise tree
verifier and the complete cut-SAT verifier pass.  For the literal
ninth-diagonal test the graph has only four proper support patterns, so a
proper nine-antichain cannot be chosen locally; the direct intersection
closure is the stronger nonvacuous conclusion.

## Exact data

The roadmap certificate is
`data/DIAG9_GRAPH_row2599_node_roadmap.npz` with SHA-256

```text
ddec96b052b305d279b543be2af27e12f380f0dedc79ea434616c64b40cd8cea
```

The labeled graph certificate is
`data/DIAG9_GRAPH_row2599_node_graph.npz` with SHA-256

```text
b7f48c4f4f421ba88cf551a2ba16cbd024d63d0910ada701118c88e2e2b7e19f
```

The NPZ stores the two occurrence groups, quotient-degree census, exact
Jacobian, every stratum label, signature support masks, full intersection
closure, and all exact dominance margins.

## Global scope

This disk certifies a local normal-crossing model and the correctness of the
label-gluing/cut machinery.  It does **not** prove that the four local
chambers exhaust parent 2599, that every global residual intersection is
normal crossing, or that a global common-feasibility locus cannot leave the
disk and return in another component.  The missing ninth-diagonal input is
still a geometrically complete master roadmap (or an equivalent global
connectivity certificate) for every parent cell.
