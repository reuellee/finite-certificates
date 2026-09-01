# D9 row-2599 factor-19069 factored-barrier component sampler gate 1

Date opened: 2026-09-01 UTC

Canonical base revision: `b71c139a3c64cde3442252f8f3d46f2d893978c5`

Canonical base tree: `7a9da9f02369831bd34bc22f39a0bbad57725522`

Opening theorem ledger: `2/9`

Selected target:
`D9_ROW2599_FACTOR19069_FACTORED_BARRIER_COMPONENT_SAMPLER_GATE1`

## Mandatory opening strategy evaluation

The frozen predecessor returned an exact fail-closed null: unfiltered
nonsmooth active supports cross the declared ceiling at support size four,
and weak-sign boundary witnesses lack paths into the closure of the pinned
connected parent component.  Its referee retired that enumeration and fixed
the present barrier sampler as the only admissible successor.

Scores use the required 1--5 dimensions; coverage burden, resource cost, and
stagnation risk are costs and are subtracted.

| Candidate | Ledger leverage | Quantifier readiness | Coverage burden | Terminality | Structural compression | Independent verification | Resource / information | Resource cost | Stagnation risk | Net | Verdict |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| single factored parent barrier for factor 19069 | 4 | 4 | 4 | 5 | 5 | 4 | 4 | 4 | 2 | **20** | **PIVOT / SELECT** |
| repeat unfiltered active-margin supports | 2 | 2 | 5 | 1 | 1 | 4 | 1 | 5 | 5 | -4 | `RETIRE` |
| sampled-separator CEGAR | 2 | 1 | 5 | 1 | 1 | 4 | 1 | 2 | 5 | -2 | `RETIRE` |
| projection, symmetry, or ambient-orbit retry | 2 | 1 | 5 | 2 | 3 | 2 | 2 | 3 | 5 | -1 | prohibited |
| unfiltered multiwall enumeration | 4 | 1 | 5 | 2 | 1 | 2 | 1 | 5 | 5 | -4 | prohibited |

The factored barrier is selected because one stationary system retains all
seventy parent inequalities without enumerating nonsmooth active supports.
Both a complete component attachment and an exact disjoint component are
terminal for this one-wall gate.  Exactly one route is selected.

## Bounded target

Let `P` be the connected strict row-2599 parent component containing the
pinned source sample.  Write its seventy signed parent factors as `H_I>0`,
let `B=product_I H_I` be represented as a factor circuit, let `f=f_19069`,
and let `S` be the fixed forty-edge parent-safe skeleton.

On the compactification of the closure of `P`, construct a projection-free
exact real-algebraic sample in every connected component of

`{f=0} intersect {dB wedge df=0}`

in the strict parent interior.  The derivative of `B` must remain in the
factored form `sum_I dH_I product_(J != I) H_J`; an expanded product is not an
accepted source object.  Singular wall pieces and positive-dimensional
critical pieces are included.  Separately enumerate every true parent-sign
and compactification-boundary stratum that can carry a wall component, with
exact paths placing it in the closure of the pinned component.  Artificial
solver, box, collar, and skeleton boundaries remain distinct from true
parent boundary.  Finally classify every resulting factor-19069 wall
component by an exact path inside the wall to `S` or by an exact certificate
of nonattachment.

- Positive endpoint:
  `EXACT_FACTOR19069_COMPONENT_DISJOINT_FROM_THE_FIXED_SKELETON`.
- Negative endpoint:
  `COMPLETE_FACTORED_BARRIER_COMPONENT_TO_SKELETON_ATTACHMENT_CERTIFICATE`.
- Null endpoint:
  `HASH_PINNED_FACTORED_BARRIER_CRITICAL_COMPONENT_FRONTIER_WITH_FIRST_UNSAMPLED_COMPONENT`.
- Timeout endpoint:
  `HASH_PINNED_COMPLETED_AND_PENDING_FACTORED_BARRIER_COMPONENT_FRONTIER`.

A finite set of numerical roots, generic-only critical points, the known
edge-39 collar, an expanded-product claim without factor provenance, or a
boundary list without connected-parent path tags cannot satisfy a complete
endpoint.  This one-wall gate alone cannot promote the `2/9` ledger.  An
independently verified theorem-level counterexample supersedes the promotion
target.

## Obligation graph

- canonical theorem ledger and diagonal-nine obligation: open at `2/9`;
- predecessor factor-19069 active-margin gate: finite-exact null and closed;
- unfiltered active-margin subset frontier: retired;
- sampled-separator CEGAR, projections, symmetry-only compression, ambient
  orbit transfer, and unfiltered multiwall enumeration: retired/prohibited;
- factor 19069, seventy parent factors, compactification atlas, fixed
  forty-edge skeleton, and edge-39 collar: finite-exact pinned inputs;
- factored derivative circuit and exact barrier-critical equations: selected
  and open;
- zero- and positive-dimensional critical-component sampling: selected and
  open;
- true parent-sign/boundary strata with pinned-component closure paths:
  selected and open;
- complete factor-19069 wall-component coverage: downstream and open;
- exact attachment/nonattachment of every wall component to the fixed
  skeleton: downstream and open;
- all-factor, multiwall, all-parent, diagonal-nine, and ledger-promotion
  quantifiers: outside this gate and open.

## Canonical input accounting

`OPENING_AUDIT.json` pins the exact base commit and tree, canonical V6 state,
predecessor report/referee/frontier, factor/collar/skeleton sources,
compactification inputs, target endpoints, resource ceiling, storage
authority, and prohibited routes.  `verify_opening_audit.py` rejects source,
ledger, target, quantifier, resource, branch, or authority drift.

## Concurrency and non-overlap

Constructor, falsifier, certificate, and frozen-head referee use disjoint
`ops/team` surfaces and immutable handoffs.  Discovery and production cannot
share acceptance logic.  The certificate verifier must not import the
producer, and the referee reviews only a frozen commit/tree.  Only the
coordinator integrates evidence or changes the canonical ledger.

## Roles

- coordinator: opening audit, integration, exact ledger delta, frozen state;
- constructor: factor-circuit barrier equations and complete/null frontier;
- falsifier: independent algebraic, boundary, path, and scope attacks;
- certificate verifier: producer-independent replay and hostile mutations;
- closing referee: frozen-head replay, disposition, and exact successor.

## Resource ceiling and stop rule

The cycle ceiling is 120 wall-minutes, 8 aggregate CPU-hours, 16 GiB per
process, one residual factor, seventy retained parent factors, at most
500,000 exact solver/component nodes, 250 MB of new artifacts, and zero paid
or external compute.  Stop at source drift, loss of any barrier factor,
expanded-product dependence, an unauthenticated algebraic sample, a missing
positive-dimensional piece, a missing true boundary stratum or
parent-component path tag, an unclassified skeleton attachment, or any
ceiling.  Such a stop is null or timeout and never becomes sampled evidence.

## Prohibited routes

Do not repeat the unfiltered active-margin subset frontier or
sampled-separator CEGAR, retry projections or symmetry-only compression, use
ambient orbit transport as fixed-domain coverage, or enumerate multiple
walls without a proved complete compression.

## Storage and publication authority

The saved local Codex project `E:\Projects\9DVL Research` is the durable
working home.  At the frozen checkpoint record its exact path, commit, and
tree.  A native-filesystem recovery bundle may be written only under
`G:\My Drive\Projects\research-backups`, must be checked by byte length and
SHA-256, and is optional if `G:` is unavailable.  The Google Drive connector
must not be invoked.  GitHub is read-only: no push, pull request, CI trigger,
or merge is authorized.

## Closing requirements

The referee must bind its decision to a frozen commit and tree, replay all
pins and the accepted endpoint without importing producer acceptance logic,
reject hostile component/boundary/path/factor/ledger mutations, state the
exact ledger delta and nonconsequences, and issue `CONTINUE`, `PIVOT`,
`RETIRE`, or `STOP`.  If the ledger remains below `3/9`, it must name exactly
one admissible successor that does not revive a retired route.
