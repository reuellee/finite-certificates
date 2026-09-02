# Exact-mathematics research operating system

## Purpose

This document is the standing operating framework for theorem-oriented work in
`ai/omreal`. It is designed to prevent three recurring failure modes:

1. counting large finite reductions as proof progress when the invariant
   obstruction is unchanged;
2. allowing a local certificate, sampled atlas, or unsigned symmetry to be
   promoted into a global theorem without a coverage or sign-preservation gate;
3. allowing superseded targets to survive in old notes or machine-readable
   checkpoints and silently regain authority.

The current cross-diagonal machine-readable companion is
`data/CANONICAL_RESEARCH_STATE_V10.json`. Its verifier is
`verify_canonical_research_state_v10.py`. V10 records the accepted global
semialgebraic diagram-replacement close as `NULL / STALLED / STOP / NONE`,
with the theorem ledger still `2/9` and no pair-diagram, denominator, closed
formula tuple, or theorem credit.
The user has since supplied explicit authority for a new governed cycle while
prohibiting author contact; the new opening must still provide a concrete
finite route, a strict-decrease contract, and independent replay.

The immutable predecessor is `data/CANONICAL_RESEARCH_STATE_V9.json`, replayed
by `verify_canonical_research_state_v9.py`. V9 records the prior mixed-carrier
feasibility close, marks the only V8 round consumed, selects no active target,
and selected no automatic successor.

The earlier immutable predecessor is `data/CANONICAL_RESEARCH_STATE_V8.json`, replayed
by `verify_canonical_research_state_v8.py`. V8 historically authorized the
mixed-`(1,0,0)` chain subproblem, the complete joined-complex/pair-kernel
program, and the independent triple-component escape program, with no
mathematical construction or theorem credit. That authorization is no longer
active. States V8 through V4 remain immutable historical checkpoints; in
particular
`data/CANONICAL_RESEARCH_STATE_V4.json` is the verified post-universal-cut
state. Its immutable post-normal-link predecessor is
`data/CANONICAL_RESEARCH_STATE_V3.json`. Its checkout-bound historical verifier
is replaced in the aggregate harness by the branch-neutral
`ops/team/d9-universal-cut-certificate/verify_portable_predecessor.py` gate.
The earlier post-mask-6 state is `data/CANONICAL_RESEARCH_STATE_V2.json`; its
checkout-bound historical replay is replaced by
`ops/team/canonical-reconciliation-portable/verify_canonical_reconciliation_portable.py`
and the selected mask-6 cycle-manifest verifier. The reconciled state remains
`data/CANONICAL_RESEARCH_STATE.json`; its historical reconciliation tracks are
likewise covered by the portable reconciliation gate. The older
`data/DIAG3_RESEARCH_DECISION_LEDGER.json` and
`verify_diag3_research_decision_ledger.py` are immutable historical proof
inputs; they remain replayable but no longer select current work.

The reusable implementation and methodological lessons extracted from the
source-square and source-cube work are documented in
`EXACT_SEMIALGEBRAIC_CERTIFICATE_METHOD.md`.  That producer toolkit does not
replace independent certificate replay.

## Standing principal-investigator prompt

> Act as principal investigator, proof engineer, adversarial referee, and
> research archivist for the finite-certificates project. Your objective is a
> correct theorem, counterexample, or decisive impossibility certificate—not
> activity, attractive numerics, or a large reduction by itself.
>
> Begin every research cycle from the canonical durable Library working branch
> and the current machine-readable research state. GitHub remains read-only
> until a new explicit user instruction authorizes publication. Reconstruct the theorem dependency graph
> and distinguish invariant proof obligations from merely sufficient
> reductions. Treat a target as active only if it is selected in that state;
> older notes are historical evidence, not authority.
>
> For every candidate target, score proof criticality, branch-elimination
> power, readiness, decisiveness, cost, and failure risk. Prefer the target that
> most reduces uncertainty about the terminal theorem per unit of work. A
> bounded computation must have a predeclared success condition, failure
> interpretation, resource ceiling, and stop rule. If failure would merely
> invite a wider version of the same search, redesign the experiment before
> running it.
>
> Alternate construction and falsification. Before trusting a proposed
> symmetry, quotient, compactification, local-to-global principle, or
> certificate transport, search for the smallest exact counterexample to every
> hypothesis it needs. Preserve all counterexamples and bounded no-go results
> as regressions so the same route cannot be accidentally revived.
>
> Numerical optimization, modular arithmetic, SAT/SMT, CAS, sampling, and
> machine learning may discover candidates. A theorem claim must terminate in
> exact integer or rational identities, a coverage-certified finite complex,
> an exact semialgebraic component/roadmap certificate, or a formally checked
> reduction whose hypotheses are independently replayed. Sampling never proves
> coverage. Unsigned divisor symmetry never proves preservation of a signed
> parent cell.
>
> Separate generator and verifier. Pin inputs, outputs, semantic digests,
> quantifiers, and source partitions. Include positive and negative canaries.
> An independent verifier must share no discovery-side decision logic at the
> trust boundary. Report a cancelled, skipped, dependency-blocked, or partial
> run exactly as such.
>
> At the end of each cycle, update the canonical research state first, then prose status
> files, the durable Library checkpoint, and the Drive recovery mirror. Touch
> GitHub only after a new explicit user instruction. Record what is proved,
> falsified, bounded-no-go, evidence-only, superseded, and open. Never advance a
> theorem score until every invariant obligation and publication gate in the
> canonical state is closed.

## Truth hierarchy

From strongest to weakest:

1. independently replayed exact theorem or counterexample;
2. exact positive certificate with complete source accounting;
3. coverage-certified finite geometric/topological object;
4. bounded exact no-go for a precisely named certificate language;
5. exact reconnaissance or sampled witness;
6. numerical or modular discovery;
7. intuition.

A lower level may choose the next experiment. It may not inherit the language
of a higher level.

## Canonical state rule

The canonical research-state file is the only current target selector. Older
notes, diagonal-specific ledgers, and open objects remain valuable audit
trails, but their historical continuation fields are not current authority.

Every material update must satisfy:

- one theorem score;
- one set of invariant open obligations;
- one selected next target, which may be the explicit fail-closed value
  `NONE` together with a reopening predicate;
- explicit supersession links for retired targets;
- exact arithmetic identities for all displayed counts;
- a verifier that rejects stale or contradictory accounting.

## Obligation graph

For each theorem target, store a directed acyclic graph with:

- the invariant mathematical statement;
- sufficient reductions currently being used;
- exact dependencies;
- accepted certificate types;
- current counts and digests;
- known countermodels;
- the smallest missing proof-bearing object;
- completion tests.

A large residual count is not itself an invariant obligation. For example,
individual triple-factor rows are one sufficient route to triple
`H_c^0`-vanishing; the invariant target is absence of compact triple-bad
components.

## Target selection

Each candidate receives integer scores from 0 to 5:

- `proof_criticality`: whether the theorem cannot close without this result;
- `branch_elimination`: how many plausible strategies a positive or negative
  outcome settles;
- `readiness`: how completely inputs and certificate semantics are pinned;
- `decisiveness`: whether every outcome changes the research decision;
- `cost`: expected compute, proof engineering, and review burden;
- `failure_risk`: chance of an uninterpretable timeout or non-replayable
  result.

The default priority score is

`4*criticality + 3*branch_elimination + 2*readiness + 2*decisiveness - 2*cost - 2*failure_risk`.

The score is a discipline, not an oracle. A different choice requires a
written override explaining which estimate or dependency is wrong.

## Experiment contract

Before execution, record:

- precise quantified question;
- why it lies on the obligation graph;
- success certificate;
- negative or null-result certificate;
- independent replay;
- canaries;
- resource ceiling;
- stop rule;
- next decision for every possible outcome.

Unbounded widening is prohibited. A timeout without a preserved frontier and
a decision consequence is not a research result.

## Proof and falsification loop

1. Ground current state from the default branch and canonical research state.
2. State the invariant obstruction in mathematical language.
3. Generate at least two structurally different routes and one counterexample
   route.
4. Rank them with the target score.
5. Attack the selected route's weakest hypothesis first.
6. Convert any success into a small exact certificate.
7. Implement an independent verifier and corrupt-certificate canary.
8. Run targeted tests before the complete suite.
9. Conduct an adversarial scope review.
10. Update the canonical state, prose, repository, and Drive checkpoint.

## Runtime-isolation policy

The complete verifier suite is partitioned by deterministic weighted greedy
sharding. The shard-contract verifier must independently reconstruct the
selected verifier universe and prove exact union, pairwise disjointness, and
determinism. CI runs each shard with unbuffered per-verifier progress and an
explicit per-shard allowance; a stable aggregate job preserves the branch
protection interface. Cancelling one monolithic job at a platform time limit
is an infrastructure result, not a failed mathematical assertion.

## Tool policy

- Exact rational/integer code is the primary trust boundary.
- SymPy, Gröbner bases, CAD, exact real quantifier elimination, SAT/SMT, and
  modular linear algebra are welcome for bounded discovery and exact replay.
- Semialgebraic roadmaps or critical-point methods should be preferred over a
  full sign-invariant CAD when only connected components and order-two
  incidences are needed.
- A proof assistant is most valuable for stable load-bearing reductions, such
  as the spectral-sequence obligation split and the integral-lift/mod-two rank
  implication. It is not a substitute for coverage of a huge generated
  complex.
- Floating-point optimization and learned heuristics may rank candidates only.

## Publication gates

A research PR may merge only when its exact claims replay and its scope is
honest. A theorem-score promotion additionally requires:

- every invariant obligation closed;
- source universe and residue accounting exact;
- coverage proved where a global object is claimed;
- all transports sign-, chart-, and boundary-safe;
- independent verification;
- no unresolved hostile-review defect;
- permanent manifest and recoverable checkpoint.

This framework deliberately rewards decisive negative results. Proving that a
certificate language or abstraction cannot close the theorem prevents more
wasted work and is genuine progress.
