# Cycle: D9 row-2599 factor-19069 singular-df multihomogeneous gate 1

Canonical base revision: `9c9a78c4225a39803a0a5ac7e4e204d9b9f3773d`

Opening theorem ledger: `2/9`

## Canonical opening

- Base revision: `9c9a78c4225a39803a0a5ac7e4e204d9b9f3773d`
- Base tree: `af4bdbfc8f89e950936d59e6b0737b12eb5bdfb5`
- Base branch: `research/local-d9-factor19069-factored-critical-equidim-gate1-20260901`
- Successor branch: `research/local-d9-factor19069-singular-df-multihomogeneous-gate1-20260901`
- Opening ledger: `2/9`
- Selected target: `D9_ROW2599_FACTOR19069_SINGULAR_DF_MULTIHOMOGENEOUS_DECOMPOSITION_GATE1`
- Concurrent authoritative cycles: none.

The cycle operates first in the original ring `Q[a,b,c,d,e,f,g,h,i]` on
`J=<f_19069, df/da, ..., df/di>`.  It must exploit and verify the source
`(2,2,2)` three-block multihomogeneous and multiaffine structure before
testing every exact component against all 70 parent factors.  Localization by
70 inverse variables is prohibited as a discovery route.  Inverse relations
may appear only in a bounded, componentwise certificate that reconstructs
`P:(product H_I)^infinity` or proves that a component meets a parent factor.

## Mandatory opening strategy evaluation

| Route | Ledger leverage | Quantifier readiness | Coverage burden | Terminality | Structural compression | Independent verification | Resource / information | Stagnation risk | verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| original nine-variable multihomogeneous singular decomposition, then componentwise 70-factor saturation | high: removes or exhibits the singular obstruction before regular charts | exact source and all parent factors already pinned; connected real residence remains separate | finite component and factor incidence frontier | both emptiness and a strict real component are terminal for this branch | high: eliminates the 70 inverse variables from discovery | moderate; sparse derivatives and component equations can be independently rebuilt | bounded branchwise outputs survive null/timeout | low relative to predecessor | `PIVOT / SELECT` |
| retry the 79-variable localized Groebner basis | low | exact but algebraically undifferentiated | unchanged | null repeats predecessor | none | high | poor | certain | `RETIRE` |
| numerical or modular primary decomposition | heuristic only | cannot promote over `Q` or prove real residence | unchanged | nonterminal | exploratory only | high lift cost | poor for theorem claims | high | `RETIRE` |
| active-margin, sampled CEGAR, projection, symmetry, ambient-orbit, or unfiltered multiwall routes | low | missing global connected-parent quantifiers | enormous or previously unresolved | nonterminal | previously exhausted | high | poor | certain | `RETIRED / PROHIBITED` |

Opening verdict: **PIVOT** to the unique selected target.  The predecessor's
first unresolved branch is exact, but its 79-variable representation caused
the blocker.  This cycle differs by decomposing the nine-variable Jacobian
ideal before any parent-factor saturation.

The alternatives are explicitly `CONTINUE`, `PIVOT`, `RETIRE`, and `STOP`;
only `PIVOT` is selected, and exactly one target follows.

## Bounded target

### Quantified endpoints and stop rules

- Positive: prove exactly that every singular component is killed by strict
  parent-factor saturation or is disjoint from the connected row-2599 parent
  component, thereby removing the singular branch from the strict component.
- Negative: exhibit an exact positive-dimensional real singular component,
  with all 70 strict parent signs and an exact path/tag to the pinned connected
  row-2599 parent component.
- Null: hash-pin the first exact multihomogeneous singular component whose
  characteristic-zero decomposition, componentwise parent-factor saturation,
  real residence, or connected-parent tag remains unresolved.
- Timeout: hash-pin every completed branch, the first pending branch, exact
  equations, monomial/block order, and resource accounting.
- Stop on source drift, loss of any singular or boundary stratum, use of a
  modular/numerical probe as evidence, discovery through 70 inverse variables,
  ambiguity in component equations, or any resource-ceiling crossing.

## Obligation graph

The pinned machine-readable graph is `OBLIGATION_GRAPH.json`. Its load-bearing
path runs from exact source reconstruction through block structure, complete
characteristic-zero singular decomposition, component invariants,
componentwise 70-factor incidence, strict real residence, and the connected
parent tag. Boundary strata branch off without being discarded. Diagonal nine
remains downstream of all of these nodes.

## Canonical input accounting

`OPENING_AUDIT.json` pins the protocol, predecessor cycle report, predecessor
singular frontier, independent predecessor certificate, factor data, parent
component tags, compactification atlas, fixed collar/skeleton evidence, and
canonical ledger verifier. Every worker must rebuild derivatives from the
pinned sparse factor and must not infer source state from chat history.

## Concurrency and non-overlap

There are no concurrent authoritative cycles. The constructor, falsifier,
independent verifier, and closing referee own disjoint `ops/team` surfaces.
Only the coordinator edits this cycle directory, integrates evidence, freezes
the head, or changes the ledger.

## Roles

- Constructor: exact source reconstruction, original-ring decomposition, and
  componentwise saturation frontier.
- Falsifier: independent hostile tests for source, algebra, scope, strata,
  parent-factor incidence, real residence, and ledger overclaim.
- Independent verifier: producer-independent reconstruction and certificate.
- Closing referee: frozen-head replay only, after candidate freeze.

## Resource ceiling

- 120 wall-minutes for the governed cycle.
- 8 aggregate CPU-hours.
- 16 GiB per process.
- 500,000 exact algebra/component nodes.
- 250 MiB of new artifacts.
- No paid external compute, network algebra service, or connector.

## Publication authority

The saved local project `E:\Projects\9DVL Research` is the canonical working
home for this cycle. GitHub is read-only. Local bundles and manifests go under
`E:\Projects\9DVL Research\outputs`; a native, length/SHA-256 verified mirror
to `G:\My Drive\Projects\research-backups` is optional and any denial is
nonblocking. The Google Drive connector is never used.

## Closing requirements

The load-bearing sequence is: reconstruct the 108-term factor with exact
source tags; verify the `(a,b,c)|(d,e,f)|(g,h,i)` multidegree; reconstruct all
nine derivatives; compute or sharply branch the characteristic-zero singular
decomposition in nine variables; preserve every component including embedded,
boundary, and multiplicity data; test each component against each of the 70
parent factors; then separately determine strict real residence and the pinned
connected-parent tag.  Absence of an independently replayed universal
diagonal certificate forbids any theorem-ledger promotion.

Closure requires explicit positive, negative, null, and timeout accounting;
producer-independent replay; hostile mutations; a clean no-hardlink replay;
a frozen candidate revision/tree; a closing-referee verdict; exact ledger
delta and nonconsequences; and exactly one successor if the honest ledger is
still below `3/9` and no theorem-level counterexample obsoletes it.
