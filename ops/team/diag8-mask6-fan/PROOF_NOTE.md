# Diagonal eight mask-6 loop: exact barycentric singular disk

## Result

For the proper pairwise-incomparable eight-family proved by the nonvacuity
certificate, the parent-860 loop `4-11-12-14-13-23-4` bounds an exact singular
two-chain in the common feasibility locus `F_S`.

Let `c` be the arithmetic mean of the six exact rational loop vertices. The
chain is the sum of the six oriented affine triangles `[c,v_i,v_(i+1)]`.
Every one of the 70 parent brackets has a strict Bernstein sign on every
triangle. The complete 26,740-factor scan leaves exactly factors `16573` and
`19721` active; 13,712 factors are uniformly negative and 13,026 positive.

Exact derivative signs make each active branch regular. Exact edge Sturm
profiles reconstruct two boundary-to-boundary arc incidence paths with
alternating boundary endpoints. Exact resultants and rational interval
isolation prove one transverse intersection in triangle four and exclude the
triangle-five resultant root by its negative simplex coordinate. The arcs cut
the disk into four sectors, and all four sign pairs occur at loop vertices.

The byte-pinned all-strata theorem makes every lower-cell label the
intersection of incident generic chamber labels. All eight signatures label
each loop-represented sector, both walls, and their node. In the oriented
chain boundary every radial edge occurs twice with opposite coefficient; the
remaining boundary is exactly the six loop edges.

## Counterexample-guided transfer

CEGAR contributes only the control flow: treat graph homology as a possibly
spurious abstract counterexample and refine the fixed disk by predicates which
are not sign definite. The proof kernel remains rational coordinates,
Bernstein coefficients, Sturm counts, resultants, all-strata gluing, and
singular-chain algebra.

## Nonconsequences

The disk concerns one family and one loop. It proves no parent coverage, no
statement about every eight-family, no true-infinity or transport theorem,
and no diagonal-eight result. The 9DVL score remains `2/9`; the named route is
retired rather than widened.

## Replay

```bash
PYTHONDONTWRITEBYTECODE=1 python \
  ops/team/diag8-mask6-fan/verify_diag8_mask6_barycentric_fan.py
```

The verifier replays nonvacuity, rebuilds the complete fan pullback, both
global arc incidence paths, the node, sector count, and chain boundary, pins
the all-strata theorem source, and rejects eight hostile mutations.
