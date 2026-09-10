# D8 mask-6 counterexample-guided discriminator: cycle report

Date: 2026-08-31 UTC

## Base and target

- canonical base revision:
  `6c7f52b43632072100b67e5f0a9b6221df14d620`
- canonical base tree:
  `60866cb78e8aea3259cf376a4420e5370ab8c010`
- opening and closing theorem ledger: `2/9`
- bounded target: `D8_M6_CEGAR1`
- parent and loop: parent `860`, `4-11-12-14-13-23-4`
- fixed chain grammar: the arithmetic-mean barycentric fan with six oriented
  triangles

## Outcome

The bounded cycle reaches its positive endpoint. It proves neither diagonal
eight nor 9DVL, whose honest ledger remains `2/9`. It does prove that the
named parent-860 mask-6 loop is nonvacuous for the diagonal-eight quantifier
and nevertheless bounds an explicit singular disk.

## Handoffs and publication gates

| Role / track | Frozen evidence | Classification |
| --- | --- | --- |
| coordinator and cross-domain opening scout | `CYCLE.md` and `WORK_ORDERS.yaml` | `CONTINUE_ONE_BOUNDED_DISCRIMINATOR`; CEGAR is method-only |
| independent opening falsifier | target contract | nonvacuity first; reject sampled, local-only, or graph-only promotion |
| independent opening referee | D8/D3/D9 eight-factor comparison | `CONTINUE` D8 only; `STOP` D9 and `PIVOT` away from D3 for this cycle |
| nonvacuity prover | `ops/team/diag8-mask6-nonvacuity/RESULT.yaml`, SHA-256 `6eac6a8c52a588f251acca63bdd72abc52344ff2aa18b675aee863fb5da36b5c` | `PROVED`; seven charts and all 56 ordered pairs |
| exact fan prover | `ops/team/diag8-mask6-fan/RESULT.yaml`, SHA-256 `18dfae842f9b7e73d958a00dbd376c9fe86a0c4d5f3cdaba7658fea9f692e610` | `PROVED_BOUNDED_FILLING` |
| independent closing referee | frozen integrated exact head after this report | `PENDING_EXACT_HEAD_REVIEW` |
| coordinator publication | PR #47 | `PENDING_REVIEWED_FINAL_HEAD` |

The integrated pre-report candidate is
`c3190b618cb23d4ca5bd2f6d28c0c1f34e0d1988`, tree
`3884f30c3c866ace2472d4366c78a12635586df9`. The report revision deliberately
does not claim its own acceptance: the independent referee must review the new
exact head after this report is published.

| Gate | Result |
| --- | --- |
| canonical base revision and tree | `PASS` |
| mandatory opening strategy evaluation | `PASS` |
| exact nonvacuity certificate | `PASS_8_SIGNATURES_7_CHARTS_56_ORDERED_PAIRS` |
| fixed-fan parent census | `PASS_70_OF_70` |
| fixed-fan primitive-factor census | `PASS_26740_OF_26740` |
| active-wall arc/node/sector reconstruction | `PASS_2_ARCS_1_NODE_4_SECTORS` |
| singular boundary and radial cancellation | `PASS` |
| cycle protocol | `PASS_5_CYCLES_19_AUTHORIZED_WORK_ORDERS` |
| cycle source manifest | `PASS_6_OF_6_HOSTILE_CANARIES` |
| canonical state v2 | `PASS_13_OF_13_HOSTILE_CANARIES` |
| theorem ledger delta | `NONE; 2/9 -> 2/9` |
| independent closing referee at final head | `PENDING_PUBLICATION_STAGE` |
| protected CI at reviewed final head | `PENDING_PUBLICATION_STAGE` |
| exact-head merge | `PENDING_PUBLICATION_STAGE` |
| durable recovery checkpoint | `PENDING_PUBLICATION_STAGE` |

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

## Ledger and route disposition

- no parent-860 coverage;
- no statement for every eight-family;
- no true-infinity or transport theorem;
- no proof of diagonal eight;
- no theorem-ledger change.

The mask-6 discriminator is **`RETIRED_AFTER_POSITIVE_FILLING`**. Repeating or
widening this local loop is prohibited. Current control returns to
`PIVOT_REQUIRED` with no selected target pending a fresh opening audit.

Obligation-graph delta:

- `diag8_mask6_nonvacuity`: closed for the one certified eight-family;
- `diag8_mask6_fixed_fan`: closed positively for the one fixed fan;
- `diag8_h1`: unchanged and open because parent coverage, universal-family,
  infinity, and transport inputs remain absent;
- `diag3_triple_hc0`, `diag3_pair_hc1`, `diag4_sp`, and `diag9_h0`: unchanged
  and open;
- theorem ledger: exactly `2/9`; promotion `NONE`.

The cycle reduces one local graph ambiguity and retires one discriminator. It
does not reduce the unresolved global quantifier burden enough to authorize a
second local mask-6 cycle.

## Replays

```console
PYTHONDONTWRITEBYTECODE=1 python \
  ops/team/diag8-mask6-nonvacuity/verify_diag8_mask6_nonvacuity.py
PYTHONDONTWRITEBYTECODE=1 python \
  ops/team/diag8-mask6-fan/verify_diag8_mask6_barycentric_fan.py
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/verify_canonical_research_state_v2.py
```

## Publication and recovery manifest

- publication branch: `research/diag8-mask6-cegar-20260831`
- pull request: `https://github.com/reuellee/finite-certificates/pull/47`
- integrated pre-report candidate:
  `c3190b618cb23d4ca5bd2f6d28c0c1f34e0d1988`, tree
  `3884f30c3c866ace2472d4366c78a12635586df9`
- final independently reviewed head and tree: `PENDING_PUBLICATION_STAGE`
- protected CI run and result: `PENDING_PUBLICATION_STAGE`
- merge revision: `PENDING_PUBLICATION_STAGE`
- Google Drive `Projects/research-backups` bundle and recovery manifest:
  `PENDING_PUBLICATION_STAGE`
- ledger promotion: `NONE`

## Next action

Post-cycle verdict: **`PIVOT_TO_FRESH_INDEPENDENT_OPENING_AUDIT`**.

After exact-head review, protected CI, merge, and recovery checkpointing, the
next cycle must independently compare the surviving D3, D8, and D9 global
obligations again. No mathematical target is selected here. The retired
mask-6 discriminator may not be repeated or widened without a new theorem-
ready global coverage input.
