# Component-complete D9 roadmap opening cycle

Date opened: 2026-09-01 UTC

Canonical base revision: `a6cae1e774420a96ca0ba8b76ee990c3e0b11bdc`

Canonical base tree: `d99658f9ecde22fa3386d769a2fe72ea407a8ec1`

Opening theorem ledger: `2/9`

Selected target: `D9_COMPONENT_COMPLETE_ROADMAP_GATE1`

## Mandatory opening strategy evaluation

The preceding cycle proved that a memoryless local wall grammar cannot decide
global component cuts.  This cycle therefore compares only routes that add
actual global component information.  Scores use the standing formula
`4*criticality + 3*elimination + 2*readiness + 2*decisiveness - 2*cost - 2*risk`.

| Candidate | Ledger leverage | Quantifier readiness | Coverage burden | Terminality | Structural compression | Independent verification | Resource / information | Stagnation risk | Score | Verdict |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| fixed-domain component-complete roadmap | 5 | 4 | 4 | 5 | 4 | 5 | 4 | 3 | **36** | **PIVOT / SELECT** |
| exact global-cut CEGAR | 5 | 2 | 5 | 5 | 4 | 4 | 4 | 4 | 33 | reserve falsifier |
| Leray/nerve reduction | 5 | 2 | 5 | 4 | 5 | 4 | 3 | 4 | 33 | RETIRE as opening target |
| adaptive witness-space connectivity | 5 | 3 | 5 | 4 | 3 | 4 | 4 | 4 | 32 | reserve |

`CONTINUE` is rejected for the retired 13-type grammar.  `STOP` applies before
any main roadmap enumeration if a representation canary, exactness gate, or
resource ceiling fails.

The roadmap is selected as a bounded fixed-domain discriminator, not as a
diagonal-nine theorem.  Its value is that it must encode global attachment and
can fail decisively before an expensive construction begins.

## Bounded target

On the fixed row-2599 `S12,37` active-sector domain with 3,539 active factor
classes, define and test an exact, singularity-aware roadmap certificate whose
one-dimensional realization intersects every connected component and whose
certified paths preserve component connectivity.

The opening gate must pass all four hostile canaries before any critical-system
enumeration is authorized:

1. **Aliasing:** distinguish the 16-chamber counterpair despite identical
   memoryless local data.
2. **Projection closure:** retain the type-36 projection factor `c*d-c+f`
   without assuming the retired 13-type grammar is closed.
3. **Boundary residence:** classify factor 8552 as recursive-boundary-only and
   refuse to create a false strict-parent component.
4. **Singularity:** reject a roadmap that omits a split/merge or a
   positive-dimensional critical locus.

Positive endpoint: an exact, independently replayable component-complete
roadmap for the fixed domain, yielding either connected or disconnected for
that domain only.  Negative endpoint: an exact fixed-domain disconnection
certificate or a fatal counterexample to the roadmap contract.  Null endpoint:
the first unresolved singular stratum, attachment mode, or exact path witness
class.  Timeout endpoint: a hash-pinned processed/pending critical-system
frontier.  No fixed-domain endpoint changes the theorem ledger.

## Obligation graph

- diagonal-nine invariant `H_0` obligation: open;
- memoryless 13-type local grammar: RETIRE;
- fixed-domain source pins and 3,539-factor reduction: proved and replayable;
- component-faithful global attachment representation: selected and open;
- deterministic exact projection and critical-point systems: open;
- singular-stratum and recursive-boundary handling: open;
- exact algebraic points and certified path adjacency: open;
- component-completeness theorem for the fixed domain: downstream;
- all-parent/family coverage theorem: not in scope and still open;
- theorem ledger: fixed at `2/9`.

## Canonical input accounting

Every source used by the opening gate is SHA-256 pinned in
`OPENING_AUDIT.json`.  `verify_opening_audit.py` recomputes those digests and
rejects drift before any construction is trusted.

## Concurrency and non-overlap

The constructor, falsifier, certificate verifier, and closing referee have
disjoint owned surfaces.  In this local continuation they execute as separate
phases from the same immutable base; producer decisions are not imported into
verifier acceptance logic.  Only the coordinator may integrate evidence or
change the canonical ledger.

## Roles

- coordinator: this cycle directory, integration, ledger scope, and recovery;
- roadmap constructor: exact projection, critical systems, strata, and arcs;
- falsifier: aliasing, novel-factor, boundary, and singularity attacks;
- certificate verifier: endpoint-neutral schema and independent replay;
- closing referee: exact-head review after the candidate is frozen.

No role may edit another role's surface or write GitHub.

## Resource ceiling

Opening: 4 wall-hours, 24 aggregate CPU-hours, 16 GiB per process, one
deterministic perturbation/projection convention, at most 100,000 exact
critical systems, and at most 500 MB of certificate bytes.  Stop at the first
failed canary, non-exact witness, missing singular stratum, non-independent
replay, or resource ceiling.

## Publication authority

The ChatGPT Library remains the canonical durable branch and Google Drive
`Projects/research-backups` remains the recovery mirror.  GitHub is read-only
until a new explicit user instruction; no push, pull request, CI trigger, or
merge is permitted.

## Closing requirements

The closing referee must bind its verdict to a frozen commit and tree, replay
all source pins and hostile canaries without producer acceptance logic, state
the exact positive, negative, null, or timeout endpoint, and confirm that no
fixed-domain result was promoted to diagonal nine.  The mandatory closing
strategy evaluation must choose `CONTINUE`, `PIVOT`, `RETIRE`, or `STOP` from
the surviving obligation graph.

