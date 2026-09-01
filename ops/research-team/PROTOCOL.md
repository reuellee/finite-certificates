# Exact research-cycle protocol

This is the mandatory control-plane protocol for every theorem-oriented
research cycle in this repository.  Its purpose is to optimize honest claim
advancement rather than activity, artifact count, or local coverage.

## 1. Canonical grounding

Before discovery work begins, the coordinator must record:

- the exact immutable base revision and tree;
- the canonical theorem/claim ledger and its current score;
- the live obligation graph, with each node classified as `proved`,
  `finite-exact`, `disproved`, `inconclusive`, or `heuristic`;
- pinned source and input digests;
- unfinished or concurrent cycles that could duplicate or invalidate work.

No worker may infer canonical state from chat history.  Conflicting state is a
stop condition until reconciled.

## 2. Mandatory pre-cycle strategy evaluation

Every cycle must begin with a written comparison of the live target against
credible alternatives.  The comparison must score at least:

1. **ledger leverage** -- whether success can change a theorem or claim;
2. **quantifier readiness** -- whether the tested objects already satisfy the
   theorem's global domain, properness, incomparability, and boundary clauses;
3. **coverage burden** -- the remaining gap between local evidence and the
   asserted domain;
4. **terminality** -- whether positive and negative outcomes both settle or
   sharply retire a route;
5. **structural compression** -- whether one lemma can replace a large census;
6. **independence cost** -- whether the result admits a genuinely independent
   verifier;
7. **resource-to-information ratio** -- useful information returned under the
   stated resource ceiling, including null and timeout outcomes;
8. **stagnation risk** -- whether the previous cycle left the same load-bearing
   blocker unchanged.

The coordinator records one of `CONTINUE`, `PIVOT`, `RETIRE`, or `STOP`, with a
specific reason.  Local examples, additional sampled coverage, or proof
infrastructure cannot by themselves justify `CONTINUE` when the theorem's
global quantifiers remain unattached.

The selected target must have explicit quantifiers, a falsifiable success
condition, a resource ceiling, a stop rule, and useful positive, negative,
null, and timeout handoffs.  It must also carry the solution-convergence
contract in section 3; a target without a measurable theorem-level decrease
is not ready to open.

## 3. Mandatory solution-convergence gate

Every cycle must measure distance to the requested theorem outcome, not only
distance to its local artifact.  The opening record must include a
**proof-distance vector** with:

1. the theorem-ledger score and the score deficit to the user's stated goal;
2. the named theorem-level invariant or global quantifier being attacked;
3. the number of open load-bearing obligations on the selected dependency
   path;
4. a certified exhaustive residual size, or the literal value `UNKNOWN` when
   no finite denominator is proved;
5. exact global coverage as a numerator/denominator, or `UNKNOWN`;
6. the number of consecutive cycles with the same load-bearing blocker; and
7. the number of consecutive cycles with zero theorem-ledger delta.

The coordinator must show the corresponding closing vectors from the last
three comparable cycles (or every available comparable cycle when fewer than
three exist), state a **convergence hypothesis**, and preregister the minimum
acceptable decrease for the new cycle.  A larger artifact, more samples, more
runtime, a smaller local chart, or a local residual with an unknown global
denominator does not by itself decrease proof distance.

At the first of the half-budget point, a preregistered intermediate endpoint,
or discovery of a null/negative result, the coordinator must record a
mid-cycle convergence check.  If the promised decrease is no longer reachable
inside the remaining ceiling, discovery stops and the cycle moves to a
fail-closed handoff; resource bounds may not be enlarged merely to avoid a
`STALLED` verdict.

The closing record must classify the trajectory as exactly one of:

- `CONVERGING`: the ledger advanced, a load-bearing theorem obligation closed,
  or a certified finite exhaustive residual strictly decreased while its
  global attachment and a bounded path to the theorem remained intact;
- `INFORMATIONAL`: exact reusable knowledge was added, but the declared
  proof-distance vector did not strictly decrease;
- `STALLED`: the promised decrease failed or the same load-bearing blocker
  survived; or
- `DIVERGING`: the route introduced an unbounded or unproved replacement
  burden, lost global attachment, or moved farther from the theorem.

`INFORMATIONAL`, `STALLED`, and `DIVERGING` results cannot justify
same-route `CONTINUE`.  An exact counterexample may justify `RETIRE`; otherwise
they require `PIVOT` or `STOP`.  A same-route `CONTINUE` is permitted only when
the closing vector strictly decreases under the preregistered measure and the
remaining successor chain is still theorem-capable.

The following automatic strategy-reset rules are mandatory:

- two consecutive comparable cycles with no ledger delta and no strict
  proof-distance decrease force `PIVOT`;
- three consecutive zero-ledger cycles on one route force a fresh
  theorem-level strategy tournament, even when local residuals shrink, unless
  the opening record had a certified finite end-to-end measure and that same
  measure strictly decreased in every cycle;
- two consecutive cycles whose claimed residual or coverage denominator is
  `UNKNOWN` cannot continue by further local refinement; and
- replacing one blocker with new obligations counts as progress only when an
  independent verifier proves the replacement strictly smaller under the
  same preregistered measure.

A forced strategy tournament must compare at least three credible
theorem-level choices, including the direct next-ledger diagonal when
applicable, a structural-compression route, and a counterexample or retirement
route.  The selected successor must maximize expected theorem convergence,
not continuity with the current implementation.

## 4. Independent execution

The default active roles are coordinator, constructive prover, falsifier, and
independent verifier/referee.  Add certificate engineering or formalization
only when required by the selected target.  Discovery, artifact generation,
and acceptance logic must remain separate.

Workers use isolated branches or worktrees and may edit only their assigned
surfaces.  Only the coordinator may integrate evidence or change the canonical
ledger.  A worker must not merge its own work or promote its own claim.

## 5. Mandatory post-cycle strategy evaluation

Before integration or a successor cycle, the coordinator must record:

- the exact theorem/claim-ledger delta;
- which obligation-graph edges were closed, narrowed, falsified, or unchanged;
- whether the result reduced the end-to-end proof burden rather than merely
  adding local evidence;
- the opening and closing proof-distance vectors, the preregistered minimum
  decrease, the mid-cycle check, and the final trajectory classification;
- the comparable-cycle history and whether an automatic strategy-reset rule
  fired;
- which starting assumptions or strategies were invalidated;
- whether the same blocker survived and why another cycle would differ;
- the next target comparison and `CONTINUE`, `PIVOT`, `RETIRE`, or `STOP`
  verdict.

A mandatory pivot is triggered when any section-3 strategy-reset rule fires,
or when either:

- two consecutive cycles leave the same load-bearing blocker and its complete
  obstruction class unchanged; or
- the current route cannot reach the theorem's quantifiers without a new
  global coverage theorem that the cycle did not address.

A mandatory retirement is triggered by an exact counterexample to a required
intermediate claim.  Negative and null results must be preserved in the
decision log so later cycles do not repeat them.

## 6. Evidence, storage, and publication gates

Claim advancement requires every applicable artifact, replay, independence,
coverage, transport, adversarial, repository, and ledger gate.  Missing
artifacts, moved revisions, ambiguous scope, incomplete global coverage, or
pending checks fail closed.

Authorization is cycle-specific and must reflect the user's latest explicit
instruction. Historical work orders are immutable evidence of the authority
that applied when those cycles opened; a later change of authority does not
rewrite them.

The historical publication authorization preserved verbatim for cycles dated
through 2026-08-31 is:

> The user explicitly authorizes this 9DVL cycle to publish research code and
> artifacts to the public GitHub repository `reuellee/finite-certificates`;
> create and update named research branches and pull requests; push commits;
> run or rerun CI; and merge only after required checks pass at the exact
> independently reviewed head.  The user also authorizes durable recovery
> checkpoints only in the Google Drive `Projects/research-backups` area.  This
> authorization does not permit publishing secrets or private unrelated files,
> modifying any other repository, using paid external compute or paid APIs,
> changing repository visibility or settings, force-pushing, deleting history
> or data, or taking other irreversible actions without separate approval.
> Use the authenticated GitHub connector for GitHub publication operations;
> do not substitute `gh`.

The current storage and publication authorization to copy verbatim into every
work order dated 2026-09-01 or later is:

> The user authorizes this 9DVL cycle to use the ChatGPT Library as the
> canonical durable working branch and to mirror recovery checkpoints only to
> the Google Drive `Projects/research-backups` area.  GitHub is read-only: do
> not push commits, publish branches, open or update pull requests, trigger or
> rerun CI, or merge until a new explicit user instruction.  Local scratch is
> ephemeral and is not an authority.  This authorization does not permit
> publishing secrets or private unrelated files, modifying any repository or
> service, using paid external compute or paid APIs, changing repository
> visibility or settings, force-pushing, deleting history or data, or taking
> other irreversible actions without separate approval.

For current cycles, workers may commit only to isolated local worktrees and
their assigned surfaces.  They may not push, open or update pull requests,
trigger CI, merge, or update the theorem ledger.  The coordinator owns local
integration and durable Library checkpoints; Google Drive is a recovery
mirror.  GitHub remains read-only until a new explicit user instruction.

## 7. Cycle report

Every cycle report must include the base revision, strategy evaluation, role
assignments, handoff classifications, gate table, exact ledger delta, surviving
blockers, opening and closing proof-distance vectors, mid-cycle convergence
check, trajectory classification, automatic-reset result, post-cycle strategy
verdict, publication revision, and backup manifest.  Activity is never
reported as theorem progress unless a publication gate actually changes claim
status.
