# Exact research-team cycle: skeleton coverage or counterexample

## Control plane

- Coordinator base: `ec362dba8a912bc4749c004641aee2da0a88dc05`
- Canonical branch at cycle start: `main`, after merged PR #38
- Canonical ledger SHA-256: `7922d769aa30a84c5d208dec92d2e78d5c7744cc6184ea1d42aaeadf947761b3`
- Optimal segment-cover SHA-256: `19248dd148d1fd002931ed5f48197869dd42c68a513376e1a4d6941389bda307`
- Candidate-factor input SHA-256: `adb2e7257457f158e809450683c46fe7ecafdbdd4a7efdf9ac630e8a4f0fb03f`
- Global-closure open-object SHA-256: `fb73899be7ff4aed5739b7f6a999d623db2a0504f212d5fe5aba35e1df1b1465`
- External source-map SHA-256: `659a2818f409f01100bcb9886248c23767e65791fe1827ba29ab3a8a4ae093e1`

The honest theorem score at cycle start is `2/9`. Diagonal three advances only
if both `diag3_triple_hc0` and `diag3_pair_hc1` pass independent exact replay.
No worker may update the canonical claim ledger or promote the score.

## Strategy correction

The previous cycle compiled two of the forty retained full-support source
edges. Exact graph replay shows that the complete retained bank is a forest:

| datum | exact value |
|---|---:|
| selected edges | 40 |
| selected vertices | 48 |
| connected components | 8 |
| cycle rank | 0 |
| degree census | `1:43, 2:2, 6:1, 9:1, 18:1` |

Consequently compiling the other 38 edges would still produce no source
two-cells or strict closure three-chains. Edge compilation remains necessary
infrastructure, but it is not by itself a coverage certificate or a route to
the required pair middle-rank replay.

The primary target is therefore a bounded **coverage-or-counterexample gate**:
turn any connected component of a primitive full-support residual wall that
avoids the retained skeleton into a finite exact critical-point or
boundary-stratified witness. An infeasible witness system would certify
coverage on its declared factor family; a feasible system would produce a
missed-component counterexample and retire the skeleton-coverage route in its
current form.

## Work orders

| Track | Role | Target | Positive / null stop |
|---|---|---|---|
| `cycle-20260828-prover-coverage-critical` | constructive prover | exact missed-component critical-point theorem with singular and true-boundary strata | theorem or first invalid quantifier |
| `cycle-20260828-falsifier-missed-component` | falsifier | smallest exact factor/component avoiding all retained edges | first exact miss or complete bounded subfamily |
| `cycle-20260828-certificate-generic-edges` | certificate engineer | parameterized exact edge compiler and all-edge degeneracy frontier | one pending-edge pilot plus manifest, or first incompatibility |
| `cycle-20260828-prover-triple-frontier` | constructive triple prover | deterministic bounded advance on the `1,162,302` unresolved triple rows | certified subfamily, exact no-go, or preserved frontier |
| `cycle-20260828-verifier-strategy` | independent referee | reconstruct and rank edge completion, critical coverage, and direct master-roadmap routes | acceptance/rejection with hostile canaries |

Each discovery track is capped at 50 minutes, 12 GiB RAM, and no paid external
compute. The referee is capped at 40 minutes and 8 GiB. Tracks own disjoint
files, may not merge or publish, and must return useful negative, null, and
timeout artifacts. Constructive and verification logic remain separate.

## Publication gates

This cycle may publish only a result classified as `proved`, `finite exact`,
or `disproved`, with pinned artifacts, deterministic replay, explicit
coverage/nonconsequences, hostile canaries, independent review, clean
repository checks, and an unchanged `2/9` ledger unless both invariant
obligations are actually closed. Heuristic searches may guide the next cycle
but are not publication claims.

## Track outcomes

| Track | Classification | Exact outcome |
|---|---|---|
| coverage prover | `PROVED_REDUCTION` | the true-parent barrier critical locus meets every connected component of one residual wall; exact component sampling makes the coverage test finite |
| coverage falsifier | `BOUNDED_NULL` | 4,450 strict-half-cube walls add no new miss; 123 full-cube candidates are root-free on the skeleton but their opposite signs occur only at parent-infeasible masks 4 and 6 |
| generic edge compiler | `FINITE_EXACT_GENERATOR_SIDE` | all-40 phase-A census, 168,680 ordered events, 9,264 compound events, and a full 1,856-event edge-17 pilot; independent checker remained silent through the 180-second cap |
| triple frontier | `PROVED_LOCAL_BOUNDARY_COVERAGE` | 20 macroboxes, 35 certificate boxes, 1,400 strict parent intervals, and an exact first `[3468]=0` parent-wall frontier |
| independent referee | `ACCEPT_WITH_SCOPE_GUARDS` | accepted the barrier theorem and triple corridor; rejected bulk completion of the source forest as the main theorem route |

The coverage proof's amended SHA-256 is
`9e4ba87acf73c1ca556e830fd687c9ca0ebad52366b82484c302ae4b282684e0`.
The referee performed a signed delta review and found no claim drift. The
triple verifier independently reconstructs all intervals and rejects `10/10`
hostile mutations. The generic compiler is retained as generator-side
infrastructure only: the engineer and coordinator checker attempts were interrupted at the
declared 180-second ceiling without a PASS summary.

## Coordinator decision and innovative execution plan

The finite source skeleton is retained as an anchor set, not asserted to be a
deformation retract. The next proof object is a **lazy order-two master
roadmap driven by exact barrier-critical incidence oracles**:

1. Preregister factor `19069` and implement the active-parent-margin version
   of the one-wall critical sampler on the whole compactified row-2599 parent
   cell. It must recover a representative attaching to the certified edge-39
   collar and fail closed on every additional critical component.
2. Extend the construction to feasible simultaneous-wall strata `f=g=0`:
   sample the barrier-critical locus defined by the three simplex equations,
   both walls, and the barrier rank drop. Emit exact emptiness or component
   representatives, closure incidence, and genuine parent-frontier tags.
   Materialize only witnessed strata; use certificates for exclusions.
3. Feed those wall and wall-pair objects directly into the labelled order-two
   closure complex required by the pair differential. Continue all 97,224
   signatures only on witnessed attachments. This is the theorem-complete
   route to the middle-rank replay.
4. In parallel, replace rejected triple macrobox 20 by a rational terminal
   cell clipped at `[3468]=0`, preserve the fixed projection certificate, and
   attach its terminal face to the genuine parent-wall stratum.
5. Compile another source edge only when one of these incidence certificates
   needs it. If needed, first optimize and independently replay the generic
   checker, then use the deterministic chart-zero batch `[17,4,21,52]`.

The next falsification discriminator is exact ordering of the first residual
root against the first parent-wall crossing near infeasible masks 4 and 6. An
interior residual root before the parent wall would be the smallest useful
miss candidate; a parent wall first would close that bounded escape route.

## Status

`COMPLETED_AND_PUBLISHED_CANDIDATE`. Both diagonal-three invariant obligations
remain open, the unresolved triple residue remains `1,162,302`, and the honest
theorem score remains `2/9`. No canonical-ledger promotion is authorized by
this cycle.
