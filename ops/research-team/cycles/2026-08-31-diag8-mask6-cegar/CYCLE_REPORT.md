# D8 mask-6 counterexample-guided discriminator: cycle report

Date: 2026-08-31 UTC

## Outcome

The bounded cycle reaches its positive endpoint. It proves neither diagonal
eight nor 9DVL, whose honest ledger remains `2/9`. It does prove that the
named parent-860 mask-6 loop is nonvacuous for the diagonal-eight quantifier
and nevertheless bounds an explicit singular disk.

## Exact nonvacuity result

Eight extension signatures common to every vertex of
`4-11-12-14-13-23-4` are certified globally nonempty, proper, and pairwise
incomparable. Seven exact realizations of catalog parent 860 carry `56`
integer witnesses: strict extension rays for feasible entries and positive
support-at-most-five Gordan relations for infeasible entries. The seven
feasibility words distinguish all `56` directed pairs, proving every ordered
noncontainment.

This closes the opening red team's main objection. The local 24-chamber
support quotient still has width six, but global incomparability is witnessed
outside that training network by exact parent-860 charts.

## Exact fan result

Let `c` be the arithmetic mean of the six rational loop vertices and take the
six oriented triangles `[c,v_i,v_(i+1)]`.

- Every one of the `70` parent brackets has a strict Bernstein sign on every
  triangle: `37` negative and `33` positive.
- Of `26,740` primitive residual factors, `13,712` are uniformly negative and
  `13,026` uniformly positive on the fan.
- Exactly factors `16,573` and `19,721` remain active. Exact derivative
  Bernstein signs make every pullback branch monotone and nonsingular.
- Exact Sturm profiles join each active factor into one boundary-to-boundary
  arc. Their only interior intersection is one transverse node in triangle
  four; the sole triangle-five resultant root has negative simplex coordinate
  and is excluded.
- The two reconstructed arcs have alternating boundary endpoints and cut the
  disk into four sectors. All four active sign pairs occur at loop vertices.
  Since all other factors are sign-definite, every sector has a loop chamber
  representative, and the pinned all-strata theorem labels the walls and node.
- All eight certified signatures label all four sectors. Summing the six
  oriented triangles cancels every radial edge and leaves exactly the six-edge
  loop.

Therefore that loop is zero in `H_1(F_S; Q)` for this proper
pairwise-incomparable eight-family.

## What the cross-domain transfer contributed

CEGAR supplied the research control flow rather than the proof: treat graph
`H_1` as a possibly spurious counterexample, demand nonvacuity, test one fixed
concretization, and refine only the predicates which fail. The exact scan
compressed `26,740` predicates to two active walls, after which ordinary
resultants, Sturm counts, Bernstein monotonicity, all-strata gluing, and
singular-chain algebra closed the bounded claim.

The primal/dual homology idea remains the fail-closed alternative for a future
coverage-certified complex; computational (co)homology can return either a
boundary chain or a separating cocycle. This cycle needed the primal chain
only. See de Silva--Morozov--Vejdemo-Johansson,
[*Dualities in Persistent (Co)Homology*](https://arxiv.org/abs/1107.5665),
for the broader matrix-duality perspective.

## Nonconsequences and disposition

- no parent-860 coverage;
- no statement for every eight-family;
- no true-infinity or transport theorem;
- no proof of diagonal eight;
- no theorem-ledger change.

The mask-6 discriminator is **`RETIRED_AFTER_POSITIVE_FILLING`**. Repeating or
widening this local loop is prohibited. Current control returns to
`PIVOT_REQUIRED` with no selected target pending a fresh opening audit.

## Replays

```console
PYTHONDONTWRITEBYTECODE=1 python \
  ops/team/diag8-mask6-nonvacuity/verify_diag8_mask6_nonvacuity.py
PYTHONDONTWRITEBYTECODE=1 python \
  ops/team/diag8-mask6-fan/verify_diag8_mask6_barycentric_fan.py
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/verify_canonical_research_state_v2.py
```
