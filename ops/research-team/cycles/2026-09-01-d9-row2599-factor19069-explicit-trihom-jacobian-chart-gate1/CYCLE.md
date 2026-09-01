# Cycle: D9 row-2599 factor-19069 explicit trihomogenized Jacobian-chart gate 1

Canonical base revision: `4aee0aac6e80d053cf1751eac766280873656909`

Opening theorem ledger: `2/9`

## Canonical opening

- Base revision: `4aee0aac6e80d053cf1751eac766280873656909`
- Base tree: `bfaff6f29b032ef6f81fa11a97063b01d74db8f7`
- Base branch: `research/local-d9-factor19069-singular-df-multihomogeneous-gate1-20260901`
- Successor branch: `research/local-d9-factor19069-explicit-trihom-jacobian-chart-gate1-20260901`
- Opening ledger: `2/9`
- Selected target: `D9_ROW2599_FACTOR19069_EXPLICIT_TRIHOMOGENIZED_JACOBIAN_CHART_DECOMPOSITION_GATE1`
- Concurrent authoritative cycles: none.

The cycle starts from the predecessor's exact 108-term polynomial
`F in Q[a,b,c,u,d,e,f,v,g,h,i,w]`, multihomogeneous of degree `(2,2,2)`
for the four-coordinate blocks `(a,b,c,u)|(d,e,f,v)|(g,h,i,w)`, together
with the exact identity `F|_{u=v=w=1}=f_19069`.  It does not treat that
identity as a decomposition certificate.  It covers `(P^3)^3` by all 64
standard product charts, builds the correct chart Jacobian ideal on every
chart, preserves all charts at infinity, and contracts every accepted
affine-chart component to `Q[a,...,i]` before any of the 70 parent-factor
tests.

## Mandatory opening strategy evaluation

| Route | Ledger leverage | Quantifier readiness | Coverage burden | Terminality | Structural compression | Independent verification | Resource / information | Stagnation risk | verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| explicit 64-chart Jacobian cover of the pinned trihomogenization, affine contraction, then componentwise 70-factor tests | high: resolves or sharply exposes the singular obstruction | exact source, chart transfer, parent factors, and strata are pinned | finite 64-chart frontier with exact first-pending branch | exact strict-parent emptiness or an exact strict real singular component is terminal for this branch | high: uses the correct projective block structure without inverse-variable discovery | high: every chart and Euler transfer is reconstructible | bounded exact chart artifacts survive null/timeout | low relative to the falsified affine-homogeneous route | `PIVOT / SELECT` |
| retry affine multihomogeneous or multiaffine decomposition | none | source premise is exactly false | unchanged | exact rejection already terminal | none | already independently falsified | wasteful | certain | `RETIRE` |
| blind 79-variable localization or larger undifferentiated Groebner budget | low | exact but not structurally separated | unchanged | repeats prior null | none | expensive | poor | certain | `RETIRE` |
| sampler-only, active-margin-subset, sampled CEGAR, projection, symmetry, ambient-orbit, unfiltered multiwall, or numerical/modular promotion | low | misses global connected-parent quantifiers | enormous or previously unresolved | nonterminal | exhausted or heuristic | high lift | poor | certain | `RETIRED / PROHIBITED` |

Opening verdict: **PIVOT** to the exactly one selected target.  The route is
new because it uses the proven projective source, proves the chart transfer,
and accounts for every infinity chart rather than assuming false affine
homogeneity.

The alternatives are explicitly `CONTINUE`, `PIVOT`, `RETIRE`, and `STOP`;
only `PIVOT` is selected, and exactly one target follows.

## Bounded target

### Quantified endpoints and stop rules

- Positive: prove exactly, after producer-independent replay, that every
  affine singular component is killed by strict parent-factor saturation or
  excluded from the connected row-2599 parent component, with every infinity
  chart retained as boundary data.
- Negative: exhibit an exact positive-dimensional real affine singular
  component, contract it to the original affine ideal, certify all 70 strict
  signs, and pin an exact path/tag to the connected row-2599 parent component.
- Null: hash-pin the first source-pinned projective chart, chart Jacobian,
  decomposition, overlap, affine contraction, component-factor, real
  residence, or connected-parent branch that remains unresolved.
- Timeout: hash-pin all 64 chart records, every exact completed decomposition
  branch, the first pending branch, order, node count, elapsed accounting, and
  the distinction between solver timeout and genuine projective boundary.
- Stop on source drift, a missing chart or overlap, incorrect Euler transfer,
  loss of an embedded/infinity/boundary stratum, unsupported characteristic-
  zero inference, discovery through 70 inverse variables, ambiguity in a
  contraction or parent tag, numerical/modular promotion, or a ceiling.

## Obligation graph

`OBLIGATION_GRAPH.json` pins the load-bearing path from the exact
trihomogenized source through the 64-chart cover, Euler/dehomogenization
equivalence, complete chartwise characteristic-zero decomposition, chart
overlap/deduplication, affine contraction, component invariants, all 70
component-factor tests, strict real residence, and the connected-parent tag.
Infinity charts branch to boundary accounting and are never discarded.

## Canonical input accounting

`OPENING_AUDIT.json` pins the current protocol, the predecessor report and
opening audit, its exact trihomogenized frontier, independent certificate and
referee, factor data, compactification and parent-face atlases, graph state,
and canonical ledger verifier.  Every worker reconstructs `F`, its chart
specializations, derivatives, and the affine transfer from these pins rather
than from chat history or another worker's acceptance.

## Concurrency and non-overlap

There are no concurrent authoritative cycles.  Constructor, falsifier,
independent certificate, and closing referee own disjoint `ops/team` surfaces.
Only the coordinator owns this cycle directory, integrates evidence, freezes
the candidate, changes the ledger, or chooses a successor.

## Roles

- Constructor: exact source reconstruction, 64-chart cover, Jacobian ideals,
  bounded characteristic-zero decomposition frontier, affine contraction,
  and componentwise parent-factor frontier.
- Falsifier: independent source, chart-cover, Euler, overlap, contraction,
  component, parent-factor, boundary, scope, and ledger attacks.
- Independent verifier: producer-independent reconstruction and certificate.
- Closing referee: frozen-head and clean no-hardlink replay only.

## Resource ceiling

- 120 wall-minutes for the governed cycle.
- 8 aggregate CPU-hours.
- 16 GiB per process.
- 500,000 exact algebra/component nodes.
- 250 MiB of new artifacts.
- No paid external compute, network algebra service, or connector.

## Publication authority

The saved local project `E:\Projects\9DVL Research` is the canonical working
home.  GitHub is read-only.  Bundles and manifests go under
`E:\Projects\9DVL Research\outputs`; a native, byte-length and SHA-256
verified mirror to `G:\My Drive\Projects\research-backups` is optional and
denial is nonblocking.  The Google Drive connector is never used.

## Closing requirements

Closure requires explicit success, negative, null, and timeout accounting;
all 64 charts including infinity charts; the exact Euler/dehomogenization
proof; characteristic-zero component evidence or a first-pending exact
frontier; affine pullback before any componentwise 70-factor claim; complete
strata and source tags; producer-independent replay; hostile mutations; a
clean no-hardlink replay; a frozen candidate revision/tree; a closing-referee
verdict; exact ledger delta and nonconsequences; and exactly one successor if
the ledger remains below `3/9` and no theorem-level counterexample intervenes.

