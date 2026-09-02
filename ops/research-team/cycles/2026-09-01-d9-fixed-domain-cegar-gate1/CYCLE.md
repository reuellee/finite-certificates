# D9 exact fixed-domain counterexample CEGAR gate 1

Date opened: 2026-09-01 UTC

Canonical base revision: `a5990bff953432a49cfa186f78e25efdb7df280b`

Canonical base tree: `96e75f55512f6abbc09749509a45b63adebfa456`

Opening theorem ledger: `2/9`

Selected target: `D9_FIXED_DOMAIN_COUNTEREXAMPLE_CEGAR_GATE1`

## Mandatory opening strategy evaluation

The predecessor requires `PIVOT` and names a two-way tournament.  Neither
candidate is inherited as selected.  Scores use the repository's required
dimensions on a 1--5 scale; higher is better except that coverage burden,
resource cost, and stagnation risk are displayed as costs and subtracted.

| Candidate | Ledger leverage | Quantifier readiness | Coverage burden | Terminality | Structural compression | Independent verification | Resource / information | Resource cost | Stagnation risk | Net score | Verdict |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| exact fixed-domain counterexample CEGAR | 5 | 4 | 4 | 5 | 4 | 5 | 5 | 2 | 2 | **30** | **PIVOT / SELECT** |
| projection-free adaptive component decomposition | 4 | 3 | 5 | 4 | 5 | 4 | 3 | 5 | 3 | 20 | reserve `PIVOT` |

CEGAR wins because a source-realized disconnected common feasibility locus
would be a theorem-level counterexample, while an exact path repairs a false
separator and supplies a durable refinement.  The two committed stress
families already satisfy the global nonempty/proper/pairwise-incomparable
input quantifiers.  The adaptive challenger has a better eventual coverage
architecture, but its current smallest product is still a one-parent,
projection-free order-two component atlas and cannot change the ledger by
itself.  CEGAR is therefore selected explicitly, not silently.

The selected route is not another projection, symmetry-only compression,
ambient orbit quotient, or unfiltered pair enumeration.  `CONTINUE` is
forbidden after this bounded seed-frontier gate unless a new complete source-
derived candidate generator or exact separator contract is supplied.

## Bounded target

Replay the two committed exact row-2599 nine-family CEGAR seeds, charts
`12/37` and `37/176`.  For each seed independently verify all 63 exact
feasibility/Gordan witnesses, all 72 ordered incomparability clauses, and the
complete rational one-column path.  The positive endpoint is an exact source-
realized separator/disconnection certificate, which would make the requested
`3/9` promotion metric obsolete by disproving the relevant diagonal-nine
claim.  The negative/refinement endpoint is an exact path repairing a proposed
separator.  The null endpoint is complete repair of the two committed seeds
with no exhaustive fixed-domain candidate generator.  The timeout endpoint
is a hash-pinned completed/pending seed and segment frontier.

The seed frontier is exactly the two committed exact stress families at the
base revision.  It is not a census of all proper nine-families, all 97,224
signatures, all row-2599 chambers, all 2,604 parents, or the complete D9
domain.  No absence of a counterexample may be promoted beyond this frontier.

## Obligation graph

- theorem ledger and diagonal-nine `H_0` obligation: open at `2/9`;
- source-realized nonempty/proper/pairwise-incomparable nine-family gate for
  seed `12/37`: finite-exact;
- exact path-or-separator disposition for seed `12/37`: selected and open;
- source-realized nonempty/proper/pairwise-incomparable nine-family gate for
  seed `37/176`: finite-exact;
- exact path-or-separator disposition for seed `37/176`: selected and open;
- complete generator for all fixed-domain counterexample candidates: open;
- complete compactified component/separator certificate: open;
- all-parent quantifier coverage: open;
- projection-free adaptive component decomposition: unselected reserve;
- diagonal nine and theorem ledger promotion: downstream and open.

## Canonical input accounting

`OPENING_AUDIT.json` pins the frozen predecessor, protocol, canonical ledger,
both exact antichain certificates, both exact path certificates, and their
accepted exact verifiers.  `verify_opening_audit.py` rejects commit/tree,
strategy, source, scope, resource, or ledger drift.

## Concurrency and non-overlap

The constructor, falsifier, certificate verifier, and closing referee own
disjoint surfaces.  They execute as sequentially separated phases from the
immutable base.  The independent certificate verifier does not import the
new producer.  Only the coordinator may integrate evidence or change the
canonical ledger.

## Roles

- coordinator: tournament, cycle charter, integration, ledger, and recovery;
- constructor: exact two-seed CEGAR frontier and endpoint classification;
- falsifier: counterexample-claim attack by exact path replay and scope audit;
- independent verifier: producer-independent pins, semantics, and hostile
  mutations over the accepted exact arithmetic;
- closing referee: frozen-head replay, ledger gate, anti-stagnation verdict,
  and successor selection.

## Resource ceiling

Opening ceiling: 90 wall-minutes, 4 aggregate CPU-hours, 8 GiB per process,
exactly two committed seed families, 126 feasibility/Gordan entries, 144
ordered incomparability clauses, 45,522 rational path segments, 20 MB of new
artifacts, and zero paid or external compute.  Stop at source drift, a failed
exact determinant, a missing path/separator disposition, an undeclared seed,
an incomplete scope guard, or any ceiling.

## Publication authority

The ChatGPT Library remains the canonical durable working branch and Google
Drive `Projects/research-backups` remains the recovery mirror.  GitHub is
read-only until a new explicit user instruction.  No push, pull request, CI
trigger, merge, or external publication is authorized.

## Closing requirements

The closing referee must bind its verdict to a frozen commit and tree, replay
both antichain and path gates, replay all hostile mutations without importing
the producer, state the exact ledger delta and nonconsequences, and choose
`CONTINUE`, `PIVOT`, `RETIRE`, or `STOP`.  If both seeds are repaired and no
complete candidate generator exists, another sampled-separator CEGAR cycle is
`RETIRE`; the precise admissible successor is the projection-free adaptive
component decomposition with a complete parent-residence invariant.
