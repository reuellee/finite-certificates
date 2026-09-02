# D3 mixed-carrier falsifier: obstruction dossier

## Handoff

**`NULL` — `A_NULL / B_NULL / C_NULL`.**  The bounded exact audit found no
admissible counterexample to Target A, B, or C at its full quantified scope.
It did find three exact, reusable no-go results against narrower ansatzes and
pin the first missing global edge for each target.  Those results do not meet
the cycle definition of `NEGATIVE`.

This is the falsifier lane's first and final discovery pass under the stated
stop rule.  It makes no theorem, exactness, escape, D3, or ledger claim.  The
ledger remains `2/9`.

## Frozen scope and sources

The lane was clean at
`dd86907bebbfaaac9caee4e1d93dc77bc9f3ad8b` (tree
`a59d740c008ae04accf200a8373d16b4d9c70ae4`) on branch
`research/lane-d3-mixed-carrier-falsifier-20260901`.  The cycle's immutable
canonical predecessor remains
`9116771ba80ed3d033516d0dd666b34348aad348`, as declared in
`ops/research-team/cycles/2026-09-01-d3-mixed-carrier-theorem-feasibility-gate1/OPENING_STATE.json`.

The audit used the target definitions and limits in:

- `ai/omreal/data/CANONICAL_RESEARCH_STATE_V8.json`;
- `ai/omreal/9DVL_THEOREM_PROSPECTUS.md`;
- `ops/research-team/cycles/2026-09-01-d3-mixed-carrier-theorem-feasibility-gate1/CYCLE.md`;
- `ops/research-team/cycles/2026-09-01-d3-mixed-carrier-theorem-feasibility-gate1/OPENING_STATE.json`;
- `ops/research-team/cycles/2026-09-01-d3-mixed-carrier-theorem-feasibility-gate1/WORK_ORDERS.yaml`.

The exact mathematical replays came from
`ai/omreal/DIAG3_JOINED_FLOW_TRIANGLE.md`,
`ai/omreal/DIAG3_ARCHITECTURE_ADVERSARIAL_AUDIT.md`,
`ai/omreal/DIAG3_GLOBAL_EXIT_CRITERION.md`, and their exact verifiers named
below.  Some sources are opening-pinned; the remaining verifier hashes are
recorded by this lane.  The mandatory canary uses the pre-existing local source
`ai/omreal/data/seeat_parent2599_upper178.npz`; no new or global atlas, broad
sample, census, external solver, or network source was used.

## Quantifier and interface audit

| Required scope | Exact stress test | Finding |
|---|---|---|
| Proper antichain | The row-2599 replay checks three distinct complete GP-valid extension signings and chart-zero badness.  Their incomparability is automatic if the intended order is the ordinary sign-vector face order. | The verifier does not separately assert the cycle's named proper-extension predicate or construct a globally declared antichain source object across parent cells and compactification charts.  It is retained only as the mandated local diagnostic and cannot support a full-scope negative. |
| `1 <= r <= 3`, modulo active-block permutation but with every labeled instance | Within one labeled three-block family, direct enumeration gives ten shape orbits and 34 formal labeled placements: `r=1`: `(0),(1),(2),(3)` with 12 placements; `r=2`: `(0,0),(1,0),(2,0),(1,1)` with 18; `r=3`: `(0,0,0),(1,0,0)` with 4. | Exact formal face count passes.  It is not a source-cell count or end-to-end denominator.  V8 credits only `(0),(1),(2)` (`3/10`); the other seven universal clauses remain open.  An orbit-level name cannot replace its labeled placements. |
| One simultaneous subdivision | The joined-flow replay is one exact chart point; the first-exit model shows that pointwise acyclic fibers need not assemble to a closed proper strip. | No simultaneous subdivision covering all blocks, supports, zero weights, residual walls, charts, and boundary strata is supplied or refuted.  This is A's first global null seam. |
| Arbitrary composable face-chain coherence | None of the exact local replays defines specialization functors and higher coherence maps on all iterated faces. | Codimension-one compatibility, even if established, would not discharge this quantifier.  No universal coherence obstruction was found. |
| Complete source provenance and comparison | The current pair open object has zero certified global adjacencies, strict closure pairs, strict closure triples, and parent-infinity cells; the component-cosheaf inputs each miss required source fields.  This is replayed by `ai/omreal/verify_diag3_global_exit_criterion.py`. | `L_source`, its full joined complex, and a filtration-preserving comparison to the actual compactified bad union are not present.  This is a current-state null, not an impossibility theorem. |
| Parent rank versus witness/support rank | The first-exit model separates the triple-relative point `u=1` from true parent infinity `u=2`; the global-exit checker rejects artificial-scope endpoints. | Witness/support loss remains an internal specialization unless a separate attachment theorem places it in true parent infinity.  No replay proves such an attachment or proves it impossible. |
| Rational pair rank | The joined-flow matrix has local integral ranks `rank d1=3`, `rank d2=6`, and `rank C2=7`; the missing local `d3` column is explicit.  The filled/unfilled countermodel below has the same accepted exit graph but different `H1(F2)`. | Local rank and component escape do not imply the required rational pair-kernel exactness.  No complete source-derived rational matrix exists to test the global equality. |
| Semantic triple-source label and every actual component | V8 pins `79,102,449` source orbits, `77,940,147` settled, `1,162,302` residual, and source-order semantic digest `a76a7c2cd6631c2d9724b450540bec7f3be6c106a41ae41f1736bbd2755a5ca4`. | The digest authenticates source ordering/accounting; it is not a stable local-component identity, a component count, or a continuation edge.  C still needs a source-derived component denominator for every residual orbit. |
| True parent infinity | The exact exit criterion accepts only component-faithful paths ending in `I = Xbar - X`; clipped, chart, witness-rank, and artificial box boundaries do not count.  Its `44 -> 37 -> 44` wall-label replay is rejected because wall labels are not stable component identities and no true-infinity path is certified. | Rejection is deliberately inconclusive in the open-world graph model.  No compact actual triple component was found, and no universal obstruction to C follows. |

## Mandatory row-2599 canary replay

`ai/omreal/verify_diag3_joined_flow_triangle.py` was replayed exactly against
`ai/omreal/data/seeat_parent2599_upper178.npz`.

The parent/chart instance uses the three signings

```text
14988895318912
3405195891438080
40418075143643136
```

and reconstructs all `26,112` derived-arrangement topes.  It verifies GP
validity and chart-zero badness, elementary escape-set sizes `56,56,60`, and
empty triple elementary-root intersection.  The pair roots are

```text
d01 = (2 -> 8, -)
d12 = (1 -> 2, -)
d20 = (1 -> 3, +)
```

The direct-edge relative complex satisfies `d1*d2=0`, has ranks `3` and `6`,
unit nonzero Smith invariants for `d2`, and

```text
H0 = 0, H1 = 0, H2 = Z,
primitive relation = (-1,1,1,1,1,1,1).
```

The singleton-root Cech cocycle evaluates to `1` on the root-choice loop.
Therefore no chain assembled entirely from ordered higher-root cells that
transport one fixed bad block per simplex can fill this primitive class,
even after adjoining every singleton root simplex.  This is the precise
elementary-root singleton no-go of
`ai/omreal/DIAG3_JOINED_FLOW_TRIANGLE.md`, Section 5.

It does **not** obstruct a genuinely mixed-block chain, prove one exists,
provide a simultaneous subdivision, prove specialization or arbitrary-chain
coherence, construct B's source comparison, prove the rational pair kernel,
or prove C's all-component escape.  Thus the canary retires a singleton-only
architecture, not Target A.

## Three minimal obstruction models

These are the only obstruction models selected in this lane.  The other
fixtures exercised by pinned verifiers are control cases, not additional
retirement claims.

### M1 — fixed triangular label order

`ai/omreal/verify_diag3_pair_fixed_order_no_go.py` reconstructs canonical
type-49 wall support `(0,7,14,28)` and the GP-valid positive signings
`11880862721603236` and `4655783301794266`.  Their 22 common compatible
elementary roots all have source label greater than target label, so none
descends for `1 > 2 > ... > 8`.  Relabeling equivariance defeats every one
globally fixed triangular label order.

**Exact consequence:** a universal lower-skeleton receiver cannot choose all
pair roots from one globally fixed triangular system.

**Scope boundary:** the model has two active blocks and targets a fixed-order
selection ansatz.  Cell-dependent orders, dynamic atlases, and nontriangular
mixed carriers remain possible.  It is not an A counterexample.

### M2 — pointwise first exits do not form a proper strip

`ai/omreal/verify_diag3_tangential_first_exit_no_go.py` uses
`-1 <= s <= 1`, `0 <= u <= 2`, with the selected component

```text
u < 1  when s=0,
u < 2  when s!=0.
```

The points `(1/n,3/2)` lie in the selected union but converge to the feasible,
nonrelative, unselected point `(0,3/2)`.  Adding only pointwise terminal
endpoints therefore leaves a nonclosed set and a nonproper projection.
Ambient closure changes the central relative fiber to
`([0,2],{1,2})`, whose exact rational relative `H1` is `Q`.

**Exact consequence:** independently acyclic first-exit fibers do not imply a
proper relative strip.  A continuous exit/frontier theorem or a complete
two-parameter atlas is indispensable.

**Scope boundary:** this is an abstract semialgebraic topology model, not an
actual 9DVL bad locus.  It refutes pointwise assembly, not simultaneous Hardt
stratification with all frontiers.  Hardt triviality needs no properness
hypothesis, but it does not by itself supply the proper compact-support
boundary control or cross-stratum maps required here.

### M3 — the same exit graph does not determine pair `H1`

`ai/omreal/verify_diag3_global_exit_criterion.py` builds two relative CW
complexes with the same accepted component-faithful exit graph and the same
one-skeleton.  Relative to one true-infinity vertex, both have an interior
vertex `i`, a path `p` to infinity, a loop `l` at `i`, and
`d1=[1 0]`.  The unfilled complex has no two-cell and
`dim H1(F2)=1`; the filled complex has `d2=(0,1)^T` and
`dim H1(F2)=0`.  Both satisfy `d1*d2=0` and pass the exit predicate.

**Exact consequence:** even sound, complete component reachability to true
infinity does not determine the pair middle rank.  B needs actual two- and
three-cell incidence and a source-derived comparison.

**Scope boundary:** this is a countermodel to a graph-only proof of B, not to
Target B itself and not to 9DVL.  Conversely, the same verifier proves a
component-faithful accepted graph is sufficient for C's noncompactness
conclusion; it does not construct such a graph for an unresolved source.

## Separate A/B/C findings

### A — `A_NULL`

The exact failures are ansatz-specific: singleton-only root fillers, one
fixed triangular order, and pointwise first-exit assembly.  None quantifies
over the exhaustive class of genuinely mixed chains permitted by A.

The decisive null boundary is the absence of a finite, source-bound rule that
assigns at least one valid genuinely mixed chain family to every quantified
input, together with one simultaneous subdivision and natural specialization
along every arbitrary face chain.  In the absence of a proposed exhaustive
ansatz, a surviving local cocycle could falsify only the chosen
parameterization, not all constructions permitted by A.  No universal A
obstruction was found.

### B — `B_NULL`

The formal face count within one labeled three-block family is exact—ten shape
orbits and 34 placements—but it is not a source-cell denominator.  Moreover,
seven universal shape clauses, stable source IDs, strict closures, true-
infinity tags, oriented incidence, and arbitrary-chain specialization remain
unconstructed.  More importantly, there is no verified `L_source` and no
filtration-preserving comparison from a complete joined relative complex to
the actual compactified bad union.  Consequently there is no source-derived
rational pair complex on which to prove

```text
rank_Q(N) + rank_Q(M) = dim_Q(C_pair^1),  with M*N=0.
```

M3 proves that C-style reachability cannot fill this gap.  It does not prove
that B is impossible.  No universal B obstruction was found.

### C — `C_NULL`

The finite exit/sink-SCC criterion is a sound sufficient endpoint once a
complete component-faithful graph exists.  C could instead be proved by a
universal theorem that bypasses component enumeration, but no such theorem is
present.  For the graph route, current sources provide an exact residual
source-orbit denominator but no complete stable-component IDs, same-component
continuation edges, or certified true-parent-infinity marks for any declared
unresolved family.  Artificial boundaries and witness rank drops are
correctly rejected; a rejected incomplete graph is not evidence of a compact
component.  No compact actual triple component and no universal C obstruction
were found.

The C obligation remains independent: neither an A filler nor B's rational
pair exactness can cancel a nonzero triple `H_c^0` summand.  Only B and C
together could prove D3, outside this no-promotion round.

## Falsification boundary and midpoint recommendation

The first complete falsifier audit has reached the cycle stop rule: every
exact negative is local or ansatz-specific, while the first unproved global
edge for each of A, B, and C is now explicit.  The recommendation is
`STOP_DISCOVERY_FREEZE_AND_SEND_TO_REFEREE` unless the topology and naturality
V8 outputs already provide, within the authorized single revision, all of:

1. A's finite proper-antichain, `r<=3`, simultaneous-subdivision and
   arbitrary-chain dependency list;
2. B's complete ten-shape source construction, comparison, and rational
   pair-kernel route; and
3. C's separate finite all-component route to certified true parent infinity.

Advancement would be a proof-program feasibility decision, not recognition
of an already proved theorem.  This lane does not authorize another search
round, a census, an atlas, or any theorem/ledger promotion.

## Machine replay

All commands returned exit code zero:

```console
python -B ops/research-team/cycles/2026-09-01-d3-mixed-carrier-theorem-feasibility-gate1/verify_opening_state.py
python -B ai/omreal/verify_diag3_joined_flow_triangle.py
python -B ai/omreal/verify_diag3_single_bad_two_skeleton.py
python -B ai/omreal/verify_diag3_pair_fixed_order_no_go.py
python -B ai/omreal/verify_diag3_tangential_first_exit_no_go.py
python -B ai/omreal/verify_diag3_global_exit_criterion.py
```

Verifier SHA-256 pins recorded by this lane, in the same order after the
opening verifier, are
`ac01851b53d4bed1c859f74bad2e71a5025825fe7accdac13263f5d6518a0944`,
`0ae6a9d54abcddbeb68be882083c52e1e6a9735941cea42eebacdf91ef77bda4`,
`3e8d8252ba81503a7b90af5cdf04571f7a96b06862a922ed82ea7e8e5e263b81`,
`71c4aba1858d21864a7dcd6f711b3e00450685420d45c447e65e72b700fc5115`,
and `c092930367e1f8129fdc6799427ff0dd9ae1aae385ddd9d44aa0452ed3d9b249`.
The opening verifier SHA-256 is
`ff676252c6db59cb1377463679a6fe79953bdf57fd79458f34875f4435d6e01c`.
