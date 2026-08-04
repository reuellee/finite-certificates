# Diagonal 9: exact row-2599 residual-factor state sample

## Result

Evaluating the 26,740 localized residual factor classes on all 178 stored
exact row-2599 charts gives 178 distinct generic sign states.  Therefore the
residual arrangement inside parent 2599 has at least

\[
\boxed{178}
\]

open sign chambers.

This is an exact lower bound from certified points.  It is not a roadmap:
the artifact does not claim that the 178 points meet every chamber, determine
adjacency, or give paths between them.

Replay with

```bash
python ai/omreal/DIAG9_GRAPH_row2599_factor_states.py
```

## Why one representative per factor is enough

The global factor certificate writes each labeled residual determinant as

\[
D_E=c_E u_E q_j,
\]

where `q_j` is one of the 26,740 primitive factor fingerprints, `c_E` is a
nonzero rational scalar, and `u_E` is either `1` or one parent bracket.  In a
fixed UOM cell the sign of `c_E u_E` is fixed.  Hence the sign of one raw
determinant representative for class `j` differs from the sign of `q_j` by
one fixed coordinate reorientation.  It preserves equality of factor sign
states, sign variation, Hamming distances, and chamber separation.

The verifier chooses the lexically first labeled occurrence of every factor
class.  At each stored integer chart it recomputes all 56 derived normals and
then all 26,740 representative four-normal determinants in integer
arithmetic.  It also checks all 70 parent brackets have the row-2599 signs and
that no representative determinant vanishes.

## Exact sample statistics

| Quantity | Exact value |
|---|---:|
| Stored exact charts | 178 |
| Distinct factor sign states | 178 |
| Factor coordinates taking both signs | 10,844 |
| Distinct nonconstant traces across the 178 charts | 10,787 |
| Constant traces | 2 |
| Minimum pairwise factor-sign Hamming distance | 1,125 |
| Maximum pairwise factor-sign Hamming distance | 5,600 |

Thus no two stored charts lie in one generic residual sign chamber.  Every
pair is separated by at least 1,125 of the global factor coordinates.

The 10,844 varying coordinates show that both sides of that many distinct
global residual factors occur among exact row-2599 realizations.  Combined
with the already established path-connectedness of the parent realization
space, the intermediate value theorem says each of those 10,844 factor walls
meets parent 2599.  The point sample alone does not locate those crossings or
show how their chambers attach.

The 10,787 trace count is not a further factor identification.  Different
global polynomials can agree on all 178 sampled signs, and the complete
factor census keeps them distinct.  Conversely, the two constant traces
record factors that are positive at every sample versus negative at every
sample after the chosen representative reorientation; they may still change
sign elsewhere in the parent cell.

## Certificate

`data/DIAG9_GRAPH_row2599_factor_states.npz` stores:

- the representative occurrence and four-set for every global factor;
- the packed `178 x 26,740` exact sign matrix;
- factor-to-trace classes and their multiplicities;
- all 10,844 varying factor IDs;
- the exact `178 x 178` Hamming-distance matrix.

Its file SHA-256 is

```text
f44b1fccfb4e61273aeceb8796a18098d82c48473e257556ce3d2a22f99b0bcf
```

Its semantic array SHA-256 is

```text
ab4aeed6eab31d6f4bfa68894b52e8086910076a25d7c7416c806f0529df8f0b
```

The semantic digest is pinned in the exact verifier.

## Consequence for the global program

The sample already rules out a tiny row-2599 arrangement: a complete roadmap
has at least 178 generic vertices and must account for at least 10,844
two-sided factor coordinates.  The factor census still saves substantial
work—84,840 labeled equations reduce to 26,740 walls—but an exact global
roadmap will need aggressive sign-invariant decomposition, symmetry, and
antichain-aware pruning rather than direct enumeration of labeled
determinants.
