# Cycle: D9 row-2599 factor-19069 homogenizer boundary-type stratification gate 1

Canonical base revision: `0ffb0295d74e6c50a3c198b67c9821d2fe2e2760`

Opening theorem ledger: `2/9`

## Canonical opening

- Base revision: `0ffb0295d74e6c50a3c198b67c9821d2fe2e2760`
- Base tree: `d01cfbbe04f721496a91d13f85d3688262869ac0`
- Base branch: `research/local-d9-factor19069-explicit-trihom-jacobian-chart-gate1-20260901`
- Successor branch: `research/local-d9-factor19069-homogenizer-boundary-type-stratification-gate1-20260901`
- Opening ledger: `2/9`
- Selected target: `D9_ROW2599_FACTOR19069_HOMOGENIZER_BOUNDARY_TYPE_STRATIFICATION_GATE1`
- Concurrent authoritative cycles: none.

The predecessor reconstructed the exact 108-term degree-`(2,2,2)`
trihomogenization `F in Q[a,b,c,u,d,e,f,v,g,h,i,w]`, proved its 64-chart
cover and 279 boundary-stratum incidences, and timed out before the first
whole-chart Groebner prerequisite. This cycle does not retry that route. It
restricts `F` and the relevant Jacobian data first to the seven nonempty
homogenizer boundary types and decomposes the resulting exact factored
branches in source-derived order, deepest type first.

## Mandatory opening strategy evaluation

| Route | Ledger leverage | Quantifier readiness | Coverage burden | Terminality | Structural compression | Independence cost | Resource / information | Stagnation risk | verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| exact seven-type homogenizer-boundary stratification, factored branch propagation, overlap-certified deduplication, affine pullback, and 70-parent-factor exclusion | high: attacks the pinned singular obstruction and boundary ambiguity | exact source, atlas, parent tags, and all seven types are pinned | finite seven-type frontier with explicit branch ledger | complete classification or an exact strict-parent affine survivor is terminal for this gate | high: begins with source factorization before any ideal decomposition | moderate: sparse restrictions and identities admit independent reconstruction | high under a bounded exact node ledger, including null/timeout | low: structurally different from the timed-out whole-chart attack | `PIVOT / SELECT` |
| retry the undifferentiated 64-chart Groebner basis | low | exact but uncompressed | unchanged | predecessor timed out before its first prerequisite | none | high | poor | certain | `RETIRE` |
| sampler-only, active-margin subset, sampled CEGAR, projection, symmetry, ambient-orbit, unfiltered multiwall, 70-inverse-variable, or falsely affine-multihomogeneous routes | low | fails the theorem quantifiers or a pinned premise | unbounded or already falsified | nonterminal | exhausted or heuristic | high | poor | certain | `RETIRED / PROHIBITED` |

Opening verdict: **PIVOT** to exactly one selected target. The deepest type
`u=v=w=0` is processed first, beginning from the independently verified exact
identity

`F|_{u=v=w=0} = -h*(a*f-c*d)*(a*e*i-a*f*h-b*d*i+b*f*g+c*d*h-c*e*g)`.

## Bounded target

### Quantified endpoints and stop rules

- Positive: for all seven nonempty types of `{u=0,v=0,w=0}`, reconstruct the
  exact restricted polynomial and restricted singular/Jacobian conditions;
  propagate every exact factor branch with equations and exact dimension,
  degree, and multiplicity when certified; deduplicate chart representatives
  only by explicit overlap units; and classify every branch as projective-
  infinity only, an exact pullback to the affine singular ideal, or excluded
  by at least one of the 70 pinned parent factors.
- Negative: exhibit an exact positive-dimensional branch that pulls back to
  the affine singular ideal, survives all 70 parent-factor exclusions, has an
  exact strict real point or cell, and is tagged to the connected row-2599
  parent component.
- Null: hash-pin the first type/factor/Jacobian/overlap/pullback/parent branch
  whose exact classification remains unresolved, with every completed branch
  retained and no completeness inference.
- Timeout: hash-pin all completed type and branch records, stable order, exact
  node ledger, elapsed accounting, first pending branch, and the distinction
  between projective boundary and solver timeout.
- Stop on source drift, omission of a nonempty type or its chart incidences,
  derivative-before-restriction errors, unsupported radicality or
  multiplicity, deduplication without an invertible overlap certificate,
  affine claims without exact contraction/pullback, incomplete 70-factor
  incidence, numerical/modular promotion, any retired route, or a ceiling.

## Obligation graph

`OBLIGATION_GRAPH.json` records the exact inherited source/atlas facts and the
load-bearing path through seven restricted sources, restricted Jacobian
ideals, exact factor branches, type closures, overlap certificates, affine
pullback, all 70 parent factors, strict real residence, and the connected
parent tag. Unresolved branches remain fail-closed.

## Canonical input accounting

`OPENING_AUDIT.json` pins the protocol, predecessor report and audit, the
21.4-MB projective frontier, producer-independent certificate, falsifier and
referee results, canonical state and verifier, factor data, compactification
and parent-face atlases, graph state, and theorem ledger. Every computational
lane reconstructs restricted polynomials and derivatives from the pinned
108-term source rather than importing another lane's acceptance.

## Concurrency and non-overlap

There are no concurrent authoritative cycles. Constructor, falsifier,
independent certificate, and closing referee own disjoint `ops/team` surfaces.
Only the coordinator owns this cycle directory, integrates evidence, freezes
the candidate, changes the ledger, or chooses a successor.

## Roles

- Constructor: exact seven-type restrictions, derivative/restriction
  transfer, factor and singular-branch propagation, overlap certificates,
  affine pullbacks, and parent-factor frontier.
- Falsifier: independent attacks on source, seven-type coverage, derivative
  transfer, factorization, branch equations, overlaps, pullbacks, parent
  exclusions, scope, and endpoint honesty.
- Independent verifier: producer-independent source reconstruction and exact
  certificate, including hostile mutations.
- Closing referee: frozen-head and clean no-hardlink replay only.

## Resource ceiling

- 120 wall-minutes for the governed cycle.
- 8 aggregate CPU-hours.
- 16 GiB per process.
- 500,000 exact algebra/branch nodes.
- 250 MiB of new artifacts.
- No paid external compute, network algebra service, or connector.

## Publication authority

The saved local project `E:\Projects\9DVL Research` is the canonical working
home. GitHub is read-only. Bundles and manifests go under
`E:\Projects\9DVL Research\outputs`; a native, byte-length and SHA-256 verified
mirror to `G:\My Drive\Projects\research-backups` is optional and nonblocking.
The Google Drive connector is never used.

## Closing requirements

Closure requires explicit positive, negative, null, and timeout accounting;
all seven nonempty boundary types and all 279 inherited type-chart incidences;
exact restrict-then-differentiate semantics; exact branch equations; explicit
overlap units for any deduplication; exact affine pullback before parent tests;
all 70 parent factors for every accepted affine branch; producer-independent
replay; hostile mutations; clean no-hardlink replay; a frozen candidate
revision/tree; a closing-referee verdict; exact ledger delta and
nonconsequences; and exactly one successor if the ledger remains below `3/9`
and no theorem-level counterexample intervenes.

