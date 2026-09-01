# D9 row-2599 factor-19069 active-margin component gate 1

Date opened: 2026-09-01 UTC

Canonical base revision: `b14e5bd0158752f96a9534b484ef2195626bd14c`

Canonical base tree: `b942da304007bb4d9437ec7575c420fc6073814b`

Opening theorem ledger: `2/9`

Selected target:
`D9_ROW2599_FACTOR19069_PROJECTION_FREE_ACTIVE_MARGIN_COMPONENT_GATE1`

## Mandatory opening strategy evaluation

The frozen predecessor accepted exactly one admissible successor and retired
sampled-separator CEGAR without a complete generator.  The comparison below
records the selected route against the only credible alternatives.  Scores
use the required 1--5 dimensions; coverage burden, resource cost, and
stagnation risk are costs and are subtracted.

| Candidate | Ledger leverage | Quantifier readiness | Coverage burden | Terminality | Structural compression | Independent verification | Resource / information | Resource cost | Stagnation risk | Net | Verdict |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| projection-free factor-19069 active-margin components | 4 | 4 | 4 | 5 | 5 | 4 | 4 | 4 | 2 | **20** | **PIVOT / SELECT** |
| sampled-separator CEGAR without complete generator | 2 | 1 | 5 | 1 | 1 | 4 | 1 | 2 | 5 | -2 | `RETIRE` |
| projection or ambient-orbit compression retry | 2 | 1 | 5 | 2 | 3 | 2 | 2 | 3 | 5 | -1 | prohibited |
| unfiltered pair-frontier roadmap | 4 | 2 | 5 | 3 | 2 | 3 | 1 | 5 | 4 | 1 | prohibited by ceiling |

The active-margin route is selected because the predecessor fixes it, it
retains parent-component membership rather than only ambient signs, and both
attachment and nonattachment are terminal for the one-wall coverage gate.
Exactly one route is selected.

## Quantified target and endpoints

Let `P` be the connected strict row-2599 parent component containing the
pinned source sample, `f_19069` the pinned primitive residual polynomial, and
`S` the fixed union of the forty retained parent-safe source segments.
Compute one exact real-algebraic representative in every connected component
of `P intersect {f_19069=0}` by a projection-free active-margin/barrier
construction.  Every representative and path record must retain all seventy
signed-parent inequalities and an exact path/roadmap tag to the pinned parent
sample.  The closure accounting must include every true-parent-boundary
stratum while keeping artificial box, collar, and skeleton boundaries
separate.  Classify every wall component by attachment or nonattachment to
`S` inside the wall.

- Positive endpoint:
  `EXACT_FACTOR19069_WALL_COMPONENT_DISJOINT_FROM_FIXED_40_EDGE_SKELETON`.
- Negative endpoint:
  `COMPLETE_EXACT_FACTOR19069_COMPONENT_TO_SKELETON_ATTACHMENT_CERTIFICATE`.
- Null endpoint:
  `HASH_PINNED_PARENT_RESIDENT_CRITICAL_COMPONENT_FRONTIER_WITH_FIRST_UNCLASSIFIED_STRATUM`.
- Timeout endpoint:
  `HASH_PINNED_COMPLETED_AND_PENDING_ACTIVE_MARGIN_STRATUM_FRONTIER`.

Neither a local collar attachment nor sampled points can satisfy the complete
endpoint.  A theorem-level diagonal-nine counterexample, if independently
verified, supersedes a ledger-promotion target.  Otherwise this one-wall gate
alone does not advance the `2/9` theorem ledger.

## Obligation graph

- canonical theorem ledger and diagonal-nine obligation: open at `2/9`;
- predecessor CEGAR frontier: finite-exact and closed;
- sampled-separator CEGAR without complete generator: retired;
- factor-19069 polynomial, 70 parent brackets, fixed 40-edge skeleton, and
  edge-39 collar attachment: finite-exact pinned inputs;
- complete active-margin singleton and tie-stratum enumeration: selected and
  open;
- all true-parent-boundary strata and artificial-boundary separation:
  selected and open;
- exact membership in the connected parent component, with path tags to the
  pinned source: selected and open;
- component-complete exact real-algebraic sample: downstream and open;
- attachment/nonattachment of every sampled wall component: downstream and
  open;
- all-factor, multiwall, all-parent, diagonal-nine, and ledger-promotion
  quantifiers: outside this gate and open.

## Roles and separation

- coordinator: cycle charter, integration, ledger, frozen checkpoint;
- constructor: source-derived active-margin frontier and endpoint candidate;
- falsifier: independent scope, boundary, component, and attachment attacks;
- certificate verifier: producer-independent semantic replay and hostile
  mutations;
- closing referee: frozen-head replay, exact ledger delta, and successor.

The phases use disjoint `ops/team` surfaces.  The independent verifier must
not import the producer.  Only the coordinator may integrate or update the
canonical ledger.

## Resource ceiling and stop rule

The opening ceiling is 90 wall-minutes, 4 aggregate CPU-hours, 16 GiB per
process, one target residual factor, seventy parent-tag families, at most
100,000 exact active/tie/boundary systems, 250 MB of new artifacts, and zero
paid or external compute.  Stop at source drift, a missing parent-component
path tag, an omitted true-boundary stratum, an unauthenticated algebraic
sample, an unclassified attachment, or any ceiling.  Such a stop is recorded
as null or timeout, never silently weakened to sampled evidence.

## Prohibited routes

Do not revive sampled-separator CEGAR without a complete generator, retry
coordinate projections or symmetry-only compression, use the ambient orbit
quotient as fixed-domain coverage, or enumerate the unfiltered pair frontier.

## Storage and publication authority

The user designates the saved local Codex project `E:\Projects\9DVL Research`
as the durable working folder for this research program.  At the next safe
frozen checkpoint the coordinator must place or reconstruct a verified
no-hardlink clone there, preserve unrelated contents, and record its exact
path, commit, and tree.  A Google Drive mirror is optional and must not block
the local checkpoint.  GitHub is read-only: no push, pull request, CI trigger,
or merge is authorized.

## Closing requirements

The referee must bind its decision to a frozen commit and tree, replay source
pins and the accepted endpoint without importing producer acceptance logic,
reject hostile component/boundary/path/ledger mutations, state the exact
ledger delta and nonconsequences, and issue `CONTINUE`, `PIVOT`, `RETIRE`, or
`STOP` with one precise successor if the ledger remains `2/9`.
