# D9 fixed-domain incidence and projection gate 2

Date opened: 2026-09-01 UTC

Canonical base revision: `32e2b37bf54c53982cb58a3b8d026734f9ab1113`

Canonical base tree: `689d1a5fb981fd2d52f7adb88721d9c7d3a01228`

Opening theorem ledger: `2/9`

Selected target: `D9_FIXED_DOMAIN_INCIDENCE_GATE2`

## Mandatory opening strategy evaluation

The preceding roadmap preflight admitted 3,539 one-wall systems but denied
enumeration of the 6,260,491 unfiltered two-wall systems.  This successor is
allowed one bounded attempt to close that exact blocker.  It may `CONTINUE`
only because it tests a new, falsifiable compression mechanism: the exact
stabilizer of the full active factor set, followed by a source-pinned
low-degree projection-genericity screen.  It does not assume that the global
9,476 pair-orbit theorem preserves the fixed parent/family domain.

| Candidate | Ledger leverage | Quantifier readiness | Coverage burden | Terminality | Structural compression | Independent verification | Resource / information | Stagnation risk | Score | Verdict |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| fixed-domain stabilizer and exact projection gate | 4 | 4 | 3 | 5 | 5 | 5 | 5 | 3 | **37** | **CONTINUE / SELECT** |
| enumerate all 6,260,491 factor pairs | 4 | 4 | 2 | 3 | 1 | 3 | 1 | 5 | 20 | `STOP` above ceiling |
| reuse the global 9,476 pair quotient unchanged | 3 | 1 | 1 | 2 | 5 | 4 | 4 | 5 | 20 | `RETIRE` unless fixed-domain invariance is proved |
| abandon the roadmap for exact global-cut CEGAR | 5 | 2 | 4 | 5 | 3 | 4 | 3 | 3 | 33 | reserve `PIVOT` |

If the active-set stabilizer is trivial or leaves at least 96,461 pair-stratum
orbits, symmetry compression fails the 100,000-system gate.  If no complete
source-derived incidence certificate replaces the rejected quotient, the
same load-bearing blocker has survived two consecutive constructive cycles;
the closing verdict must be `PIVOT` or `STOP`, not another `CONTINUE`.

## Bounded target

For the fixed row-2599 `S12,37` active-sector domain, quantify every relabeling
that preserves the complete 3,539-factor active set, quotient all unordered
active-factor pairs only by that proved stabilizer, and independently screen
the two linear and 81 quadratic active factors for the deterministic
projection vector `(1,2,4,8,16,32,64,128,256)`.

Positive endpoint: a source-derived complete pair-incidence or symmetry
filter leaving at most 96,461 two-wall systems, together with an exact
genericity certificate covering all 3,539 one-wall systems.  Negative endpoint:
an exact non-generic source factor/vector or a proof that an advertised
fixed-domain quotient is invalid.  Null endpoint: exact symmetry and partial
projection data that quantify but do not close the blocker.  Timeout endpoint:
a hash-pinned checked/unchecked permutation and factor frontier.

No endpoint authorizes critical-system solving unless the total admitted
one-plus-two-wall frontier is at most 100,000 and the complete projection
specialization certificate exists.

## Obligation graph

- theorem ledger and diagonal-nine `H_0` obligation: open at `2/9`;
- component-faithful representation canaries: proved and replayable;
- one-wall polynomial census: finite-exact at 3,539;
- unfiltered two-wall census: finite-exact at 6,260,491;
- global `S_8` pair classification: proved for ambient pair equations;
- preservation of the fixed parent/family active domain by that quotient: open;
- fixed-domain active-set stabilizer: selected and open;
- low-degree projection specialization: selected and open;
- degree-three-through-six projection specialization: open;
- complete multiwall nonemptiness/incidence filter: open;
- fixed-domain roadmap and component completeness: downstream and open.

## Canonical input accounting

`OPENING_AUDIT.json` pins the predecessor endpoint, active factor inventory,
global factor action, complete ambient pair theorem, pair-classification
certificate, and canonical research state.  `verify_opening_audit.py` checks
all pins and rejects any base, scope, ceiling, or ledger drift.

## Concurrency and non-overlap

The constructor, falsifier, certificate verifier, and closing referee own
disjoint surfaces.  In this local continuation they run as sequentially
separated phases from the immutable base.  Producer acceptance logic is not
imported by the independent verifier, and only the coordinator may integrate
evidence or alter cycle disposition.

## Roles

- coordinator: cycle charter, integration, scope, and recovery record;
- constructor: exact active-set stabilizer and low-degree projection screen;
- falsifier: invalid-quotient and nongeneric-projection hostile cases;
- certificate verifier: producer-independent action, rank, and mutation replay;
- closing referee: frozen-head gate and mandatory anti-stagnation verdict.

## Resource ceiling

Opening: 2 wall-hours, 8 aggregate CPU-hours, 12 GiB per process, all 40,320
label permutations, 3,539 active factors, exactly 83 degree-at-most-two
projection systems, at most 100,000 admitted critical systems, and 100 MB of
new certificates.  Stop at source drift, an incomplete action, a non-exact
rank test, an invalid quotient, or any ceiling.

## Publication authority

The ChatGPT Library remains the canonical durable working branch and Google
Drive `Projects/research-backups` remains the recovery mirror.  GitHub is
read-only until a new explicit user instruction.  No push, pull request, CI
trigger, merge, or external publication is authorized.

## Closing requirements

The closing referee must bind its verdict to a frozen commit and tree, replay
the exact action and all hostile mutations without producer acceptance logic,
state the exact ledger delta and every nonconsequence, and choose `CONTINUE`,
`PIVOT`, `RETIRE`, or `STOP`.  If the complete incidence filter remains open,
anti-stagnation requires `PIVOT` or `STOP`.
