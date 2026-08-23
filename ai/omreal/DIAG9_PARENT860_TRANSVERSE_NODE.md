# Diagonal 9: exact transverse node in parent 860

## Result

The first genuine codimension-two cell in the parent-860 roadmap program is
now exact.  In the normalized `(h,i)` coordinate plane, center the square at

```text
h = 3727672351519660 / 8405164123084547
i = 5135974949766124 / 12881287028869217
```

and give it `l_infinity` radius `1/1000000`.  Exact restriction of all
`26,740` primitive residual factors proves that precisely factors `15250` and
`19721` meet this whole square.  Exact restriction of all 70 parent brackets
proves that the square stays inside catalog parent 860.

At the center the two residual branches have primitive normals

```text
(16648, 60347)
(-145429401, 303924845)
```

and determinant `13835968881707`, so they cross transversely.  Their global
orbit types and labeled multiplicities are `(49,1)` and `(36,65)`.

The exact roadmap is therefore a four-cycle: four chambers, four wall rays,
and one node.  Complete derived-tope enumeration gives

| stratum | complete tope-label count |
|---|---:|
| each chamber | 26,112 |
| factor-15250 wall rays | 26,110, 26,110 |
| factor-19721 wall rays | 26,040, 26,040 |
| node | 26,038 |

Every wall label is exactly the intersection of its two adjacent chamber
labels.  The node label is exactly the intersection of all four chambers and
of every pair of wall rays.

Among the `26,186` labels visible in at least one chamber, the support-mask
multiplicities are

```text
0011 : 2
0110 : 72
1001 : 72
1100 : 2
1111 : 26038
```

Thus every proper individual support is one of the four affine half-disks.
The complete finite intersection closure is

```text
0000, 0001, 0010, 0011, 0100, 0110, 1000, 1001, 1100, 1111.
```

Every nonempty member is convex.  Hence every finite common-feasibility locus
on this disk is empty or convex, and is connected and contractible whenever
nonempty.  The sharp tree verifier and complete cut-SAT verifier independently
recover the diagonal-nine connectivity conclusion from the stored four-cycle.

## Isolation margins

The exact centered dominance ratio for the closest excluded residual factor
is

```text
299331911737904404062500 / 5709836426934645483233 > 52,
```

with factor `16249` the witness.  The closest parent-bracket ratio is

```text
197536235184241888000000 / 11116550705914134271 > 17769,
```

with bracket `2378` the witness.  A ratio above one proves the constant term
strictly dominates every nonconstant term on the whole square, so neither an
excluded factor nor a parent bracket can vanish there.

## Verification

The producer rederives the factor census, exact restrictions, labels, and
artifact:

```console
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/DIAG9_GRAPH_verify_parent860_node.py
```

The independent verifier imports no producer code.  It audits the rational
geometry, incidence identities, support census, intersection closure and
connectivity, and rejects four hostile in-memory corruptions:

```console
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/verify_diag9_parent860_node_topology.py
```

The semantic certificate digest is

```text
b7080a332d7b80127ae362bbfa2d5806fbe153d24245ef002d4867df6e1e274d
```

The graph-only regressions are

```console
python ai/omreal/DIAG9_GRAPH_verify_tree_certificate.py \
  ai/omreal/data/DIAG9_GRAPH_parent860_node_graph.npz
python ai/omreal/DIAG9_GRAPH_cut_sat.py \
  ai/omreal/data/DIAG9_GRAPH_parent860_node_graph.npz
```

## Proof boundary and next target

This theorem is complete on one exact two-dimensional disk.  It does not prove
that every component in parent 860 meets the disk, cover the selected plane,
attach genuine parent infinity, cover another parent, or advance the 9DVL
score beyond `2/9`.

The machine-checked decision ledger therefore selects a bounded next target:
expand this node into a coverage-certified two-dimensional parent-860 atlas,
classifying every residual component and every chamber/wall/node incidence in
the selected plane.  Stop at the first exact missed component, unresolved
projection factor, or loss of parent containment; preserve that frontier
instead of silently widening to a full nine-dimensional CAD.  See
`data/DIAG9_RESEARCH_DECISION_LEDGER.json`.
