# D9 row-2599 factor-19069 factored critical equidimensional decomposition gate 1

Date opened: 2026-09-01 UTC

Canonical base revision: `f196f949b2a2981ea1b21019e4a2bf56302a683a`

Canonical base tree: `7a5eaa91d1448defed2e77363b5e97cf93b97489`

Opening theorem ledger: `2/9`

Selected target:
`D9_ROW2599_FACTOR19069_FACTORED_CRITICAL_EQUIDIMENSIONAL_DECOMPOSITION_GATE1`

## Mandatory opening strategy evaluation

The frozen predecessor accepted one exact fail-closed factored-barrier
frontier and made this structural decomposition gate its sole successor.  The
unfiltered sampler has zero component samples and is retired; this cycle asks
the prior algebraic question of whether the saturated strict critical locus
has any positive-dimensional pieces.

Scores use 1--5 favorable values except that coverage burden, resource cost,
and stagnation risk are costs and are subtracted.

| Candidate | Ledger leverage | Quantifier readiness | Coverage burden | Terminality | Structural compression | Independent verification | Resource / information | Resource cost | Stagnation risk | Net | Verdict |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| saturated exact equidimensional decomposition | 4 | 4 | 3 | 5 | 5 | 4 | 5 | 4 | 1 | **25** | **PIVOT / SELECT** |
| enlarge blind component-sampler budget | 2 | 2 | 5 | 1 | 1 | 3 | 1 | 5 | 5 | -5 | `RETIRE` |
| active-margin subset or sampled CEGAR retry | 2 | 1 | 5 | 1 | 1 | 3 | 1 | 4 | 5 | -5 | `RETIRE` |
| projection, symmetry, or ambient-orbit retry | 2 | 1 | 5 | 2 | 3 | 2 | 2 | 3 | 5 | -1 | prohibited |
| unfiltered multiwall enumeration | 4 | 1 | 5 | 2 | 1 | 2 | 1 | 5 | 5 | -4 | prohibited |

Opening verdict: **`PIVOT`** to the one referee-approved saturated
equidimensional decomposition.  `CONTINUE`, `RETIRE`, and `STOP` remain the
required closing alternatives.  No sampler-only expansion is admissible.

## Bounded target

Let `f=f_19069` and let `H_0,...,H_69` be the ordered, sign-normalized parent
factors for the compactified connected row-2599 parent component containing
the pinned source sample.  Preserve the degree-90 barrier only as the circuit
`B=product_I H_I` and each derivative only as
`sum_I dH_I product_(J!=I) H_J`.  Let `W_ab` be the 36 exact coefficients of
`dB wedge df` and

`Icrit = <f, W_ab : 0<=a<b<9> : (product_I H_I)^infinity`.

The cycle must reconstruct the ideal from source, preserve all 70 factor
provenances, and compute an exact equidimensional decomposition of `Icrit`
without a geometric coordinate projection.  Any circuit auxiliaries must be
eliminationally faithful and their nonzero/saturation equations explicit.
The output must give exact dimensions and degrees/multiplicities for every
resolved branch, or hash-pin the first unresolved saturation/decomposition
obligation with exact generator, variable, monomial-order, and resource
accounting.  A complex positive-dimensional branch is not a real critical
component unless an exact real point and the strict 70-sign parent-component
selector are certified.  Singular pieces, the ten retained true-boundary
strata, source-derived parent-component tags, and the existing edge-39/null
frontier must remain in scope and distinct from the saturated interior ideal.

- Positive endpoint:
  `PROVE_STRICT_CRITICAL_LOCUS_ZERO_DIMENSIONAL_WITH_COMPLETE_REAL_ROOT_COUNT_FRONTIER`.
- Negative endpoint:
  `EXHIBIT_EXACT_POSITIVE_DIMENSIONAL_REAL_CRITICAL_COMPONENT`.
- Null endpoint:
  `HASH_PIN_FIRST_UNRESOLVED_SATURATED_IDEAL_BRANCH`.
- Timeout endpoint:
  `HASH_PIN_COMPLETED_AND_PENDING_EQUIDIMENSIONAL_DECOMPOSITION_FRONTIER`.

This gate classifies dimension before further component sampling.  It cannot
alone promote `2/9`; promotion still requires an independently replayed
universal diagonal certificate.  An exact theorem-level counterexample would
supersede the promotion objective.

## Obligation graph

- canonical theorem ledger and diagonal-nine theorem: open at `2/9`;
- predecessor factored-barrier circuit/frontier: `finite-exact` and closed;
- blind factored-barrier component-sampler escalation: retired;
- unfiltered active-margin, sampled CEGAR, projection, symmetry,
  ambient-orbit, and unfiltered multiwall routes: retired/prohibited;
- factor 19069, 70 ordered parent factors, 36 wedge nodes, ten boundary
  candidates, 40-edge skeleton, and edge-39 anchor: `finite-exact` pinned;
- exact saturated critical ideal with nonboundary witness: selected and open;
- equidimensional decomposition, dimensions, degrees, and multiplicities:
  selected and open;
- exact real-residence test for every positive-dimensional complex piece:
  downstream and open;
- connected-component sampling and complete skeleton attachment: downstream,
  blocked until this gate closes;
- all-factor, all-parent, multiwall, diagonal-nine, and ledger promotion
  quantifiers: outside this gate and open.

## Canonical input accounting

`OPENING_AUDIT.json` pins the exact base revision/tree, protocol, canonical V6
ledger, predecessor report/referee/frontier, factor/collar/skeleton and
compactification sources, target endpoints, resource ceiling, operational
storage authority, and prohibited routes.  `verify_opening_audit.py` rejects
pin, factor-count, saturation, endpoint, branch, ledger, authority, or scope
drift.  No unfinished independent cycle was authoritative at opening; the
four assigned lanes below are the only concurrent work for this target.

The inherited repository-wide protocol checker has one known pre-existing
false-negative: the frozen predecessor used heading `Storage and publication
authority` while that checker demands literal `Publication authority`.  This
cycle satisfies the literal form and records the inherited mismatch without
mutating frozen predecessor evidence.

## Concurrency and non-overlap

Constructor, falsifier, producer-independent certificate, and frozen-head
referee own disjoint `ops/team` surfaces.  Discovery code may not be imported
by acceptance logic.  Only the coordinator integrates evidence, freezes the
candidate, records the ledger delta, creates bundles, or names a successor.

## Roles

- coordinator: pins, strategy gate, integration, frozen state, ledger delta;
- constructor: exact ideal reconstruction and decomposition/frontier;
- falsifier: independent saturation, dimension, boundary, and scope attacks;
- certificate verifier: producer-independent reconstruction and hostile tests;
- closing referee: frozen-head replay, endpoint classification, disposition,
  and exactly one successor if the ledger remains below `3/9`.

## Resource ceiling

The cycle ceiling is 120 wall-minutes, 8 aggregate CPU-hours, 16 GiB per
process, one residual factor, 70 retained parent factors, 36 wedge equations,
at most 500,000 exact algebra/component nodes, 250 MB of new artifacts, and
zero paid or external compute.  Stop at source drift, factor loss, barrier
expansion, unauthenticated saturation, unexplained auxiliary elimination,
missing singular/boundary/parent tags, unsupported dimension/degree claims,
or any ceiling.  Preserve useful positive, negative, null, and timeout
handoffs; no ceiling event becomes sampled theorem evidence.

## Prohibited routes

Do not revive sampler-only escalation, unfiltered active-margin subsets,
sampled CEGAR, projection, symmetry-only or ambient-orbit transfer, or
unfiltered multiwall enumeration.

## Publication authority

The protocol-era authorization is copied verbatim in `WORK_ORDERS.yaml` for
auditability.  The user's latest cycle-specific instruction governs
operation: `E:\Projects\9DVL Research` is the durable working home; recovery
bundles may be mirrored by native filesystem operations only to
`G:\My Drive\Projects\research-backups` and must be verified by length and
SHA-256.  Never invoke the Google Drive connector and do not block on a denied
or absent `G:` mount.  GitHub is read-only; do not push, publish, trigger CI,
or merge.

## Closing requirements

The referee must bind its verdict to a frozen commit/tree, reconstruct pins
and the endpoint without producer acceptance logic, reject hostile source,
factor, saturation, branch, dimension, degree, multiplicity, boundary,
parent-tag, scope, and ledger mutations, and require a clean no-hardlink
replay.  It must state the exact ledger delta and nonconsequences and issue
`CONTINUE`, `PIVOT`, `RETIRE`, or `STOP`.  If the honest ledger remains below
`3/9`, it must name exactly one admissible successor and may not revive a
retired route.
