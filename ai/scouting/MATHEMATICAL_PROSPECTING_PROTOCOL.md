# Mathematical prospecting protocol

## Purpose

This lane searches for useful mathematics without beginning from a theorem
that the main research program already knows it needs.  It is intentionally
different from the bottleneck-driven 9DVL work.  Exact objects are explored
for unexplained regularities; definitions are introduced only after a pattern
predicts held-out examples.

The lane is subordinate to the repository's claim discipline, not to its
current theorem targets.  Discovery may use CAS, finite-field experiments,
heuristics, and exhaustive search.  A durable claim still requires an exact
scope, a proof or finite certificate, independent replay, hostile mutations,
and a prior-art audit.

Nothing in this directory changes the honest 9DVL theorem score.  As of the
first expedition that score remains **2/9**.

## Resource split

The default research allocation is:

- 80 percent for the best proof-bearing 9DVL target;
- 20 percent for mathematical prospecting.

The split is measured over bounded research cycles rather than wall-clock
minutes.  A prospecting expedition must declare its object family, resource
ceiling, holdout, and stop rule before its exploratory computation is treated
as evidence.

## Expedition lifecycle

1. **Register objects, not conclusions.**  Name the exact object family and
   the permitted observables.  Do not specify the hoped-for theorem.
2. **Mine.**  Search for low-description-length invariants, extremal cases,
   forbidden local configurations, dualities, small witnesses, conservation
   laws, and unexpected compression.
3. **Withhold.**  Reserve a distinct path, parameter block, rank, size, or
   mathematical family before inspecting its candidate-defining aggregate as
   well as its underlying identities.  An already committed aggregate cannot
   be relabelled as a holdout merely because its maximizer identities were not
   stored.
4. **Try to kill it.**  Search first for a minimal counterexample and record
   the full failed scope.  A clean refutation is a valid result.
5. **Define last.**  Name a statistic or structure only after it separates or
   predicts held-out behavior.
6. **Promote carefully.**  Separate empirical regularity, exact finite fact,
   general theorem, novelty, and application.  None implies the others.
7. **Review.**  A separate agent performs an adversarial claim, code,
   certificate, and prior-art review before publication or merge.

## Status vocabulary

- `OBSERVATION`: exploratory pattern; may be numerical or heuristic.
- `EXACT_FINITE_FACT`: exhaustively proved for pinned finite inputs.
- `CONJECTURE`: quantified statement not yet proved.
- `PROVED`: mathematical theorem with independently replayable proof.
- `REFUTED`: a quantified candidate killed by an exact counterexample.
- `BOUNDED_NO_GO`: a declared search family was exhausted without a survivor.
- `PRIOR_ART`: correct but already known; retained only when its application is
  useful here.

No result may silently move between these statuses.

## Promotion gates

A candidate enters the repository's durable result index only if it has:

1. a machine-readable claim with explicit quantifiers and exclusions;
2. exact inputs with hashes and a deterministic producer when computation is
   involved;
3. an independent verifier that does not trust producer verdicts;
4. at least one negative canary aimed at the most tempting overclaim;
5. a holdout or transfer test not used to select the candidate;
6. a literature and novelty audit against the repository corpus and primary
   sources;
7. one concrete application, such as a proof reduction, certificate
   compression, algorithm, counterexample, or complexity bound;
8. an adversarial agent review with every blocking finding resolved.

## Stop and pivot rules

- Every expedition has a finite first-pass ceiling and preserves its exact
  frontier when that ceiling is reached.
- Three consecutive batches without a cross-validated candidate force a
  change of object family or observable, not a wider unbounded search.
- A pattern that merely restates an encoded construction is retired.
- A candidate that survives only on one chosen object remains an observation.
- A prospecting result never delays a proof-bearing 9DVL checkpoint solely to
  improve presentation or enlarge a census.

## Expedition 001: extension-path alternation

### Registered objects

Two exact, independently constructed labelled paths in the row-2599 parent
cell were compared retrospectively.  Their aggregate spectra, including the
matching count of 14 maximizers, were already committed before this
expedition; only the maximizer identities and histories had not been stored:

- the 1,237-event chart-0-to-chart-89 path;
- the 5,612-event, three-block chart-0-to-chart-152 path.

For a finite signature universe `X` and a labelled chamber path
`L_0,...,L_m`, define the **path alternation number**

```text
a_x = number of i for which membership of x differs in L_i and L_(i+1).
```

The multiset of all `a_x` is the **alternation spectrum**.  This first
comparison is discovery-only, not holdout validation.

### General identities

For every finite labelled path:

```text
sum_x a_x = sum_i |L_i symmetric_difference L_(i+1)|,
{x : a_x is odd} = L_0 symmetric_difference L_m.
```

Both follow by double-counting membership flips.  If every chamber label set
is closed under an involution, then `a_x = a_involution(x)`; in the oriented-
matroid application the involution is antipodal sign reversal.  The number of
feasible runs of signature `x` along the path is

```text
(a_x + 1[x in L_0] + 1[x in L_m]) / 2.
```

These identities turn a descriptive statistic into an internal certificate
audit and measure the runs in the discrete word of open-chamber memberships.
Interpreting those runs as connected pieces of a continuous feasibility trace
requires separate, explicit wall and waypoint semantics.

### Bounded question

Reconstruct the maximizer identities and their event histories on both paths.
Test whether the matching maximizer count of 14 is accidental, forced only by
antipodality, or supported by a common exceptional signature core.  Then
compare every parent-safe three-block column order joining chart 0 to chart
152; this order class is finite and selected because it provides same-endpoint
route variation, not because of a desired optimum.  The resource ceiling is
one exact replay per path.  Failure to recover either committed aggregate
spectrum is a hard stop.

### Claim boundary

Even a common core on these paths would be an `EXACT_FINITE_FACT`, not a global
invariant of the row-2599 parent cell and not a theorem about all oriented
matroids.  Generalization requires a future path registered before inspecting
its aggregate and a structural proof explaining the bound.  Until independent
replay and hostile canaries exist, all MP-001 results remain `OBSERVATION`.

### Prior-art boundary

For a fixed chamber order, the membership data are rows of a binary matrix.
Their alternation numbers are ordinary rowwise total variation, and the run
count is the fixed-order consecutive-ones/d-interval viewpoint: one run is the
consecutive-ones property and at most `d` runs is a discrete union of `d`
intervals.  Davenport--Schinzel sequences constrain pairwise alternation of
symbols and are not implied by the per-signature counts used here.  Optimizing
the maximum per-signature load over graph paths is also adjacent to bottleneck
labelled-path problems.  MP-001 therefore claims neither these basic notions
nor the double-counting identities as novel; the research question is their
exact use for oriented-matroid extension-feasibility path selection and
certificate compression.

### Retrospective outcome

The common-core candidate was exactly refuted: the source path and the three
valid chart-0-to-chart-152 block routes have pairwise disjoint maximizer sets.
Exact parent-bracket enumeration leaves precisely the orders `012`, `021`, and
`102`.  All have maximum alternation five, while `102` strictly minimizes the
number of signatures at every nonzero tail threshold and also has the fewest
events and smallest transition mass.  Thus the restricted block-order minimax
is five and `102` is the preferred certificate route in this pinned class.

The result, manifest, verifier, and application are recorded in
`MP001_EXTENSION_PATH_ALTERNATION.md`.  Because this was retrospective and no
holdout or transfer path was registered, MP-001 remains `OBSERVATION` rather
than entering the durable result index.

## Expedition 002: block-route event-count transfer

### Registered transfer

MP-002 mechanically selected the unused row-2599 chart-0-to-chart-66 endpoint
and its complete class of three parent-safe block orders before constructing
any new extension-label history.  The exact wall-event minimum, frozen in a
separate commit, predicted order `102` would weakly minimize every nonzero
alternation tail among orders `102`, `120`, and `210`.

### Held-out outcome

The candidate is `REFUTED`.  Order `102` uses 4,228 exact wall events and has
824 signatures with alternation at least three.  Order `120` uses 4,362 events
but has only 476 signatures in that tail.  The exact gap is 348.  Both routes
tail-dominate `210`, so the finite tail Pareto frontier is `{102, 120}` and the
restricted minimax alternation remains five.

The retained application is methodological and concrete: certificate-route
selection must keep wall-event count and the alternation-tail vector as
separate Pareto coordinates.  Full quantifiers, chronology, exact records,
prior-art boundary, hostile verifier, and replay commands are in
`MP002_BLOCK_ROUTE_TRANSFER.md`.  The result has no effect on the 9DVL theorem
score.
