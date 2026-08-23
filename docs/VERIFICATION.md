# Verification policy

CI is an independent execution record for the repository's exact checks. It is not a
second research argument, and it does not need to replay every certificate after a
documentation-only change. The workflow therefore has three tiers.

## 1. Required gate on every pull request and main-branch push

The always-on gate checks repository navigation and archive policy, exercises
false-negative canaries for the CI router, and proves that the exhaustive verifier
shards are still a deterministic disjoint cover.

[`ops/ci/classify_changes.py`](../ops/ci/classify_changes.py) then routes changed proof
inputs:

- executable proof or certificate inputs run a pinned 94-verifier bounded suite with
  dedicated-job verifiers excluded;
- a directly changed slow verifier, or a slow verifier that directly imports a changed
  sibling module, is replayed explicitly;
- maxout capstone inputs run the independent 132,560-certificate audit;
- the expensive 9DVL atlas, labelled-pair, source-block, and parent-860 jobs run only
  when one of their declared inputs changes.

Markdown, logs, workflow prose, and other non-proof files do not start mathematical
replays. The final job, `verifier suite (complete)`, is stable for branch protection
and fails if any job required by the computed plan was skipped, cancelled, or failed.

## 2. Targeted exact audits

The path groups are conservative dependency declarations, not timing hints. Shared
modules such as `DIAG9_GRAPH_exact_topes.py` deliberately activate every expensive
audit known to depend on them. Routing changes ship with executable canaries in
[`ops/ci/check_ci_policy.py`](../ops/ci/check_ci_policy.py).

The bounded-suite manifest is pinned by the CI-policy canary. Its cost classification
was calibrated from a successful exhaustive run: replays taking at least ten seconds
join `run_all.py`'s `SLOW` set. When adding a verifier, make a conscious fast/slow
decision; if it needs special arguments or data, give it a named job and a routing
canary. The weekly full replay remains a backstop for undeclared or indirect
dependencies.

## 3. Full replay

A Monday schedule and every manual workflow dispatch run:

- all four exhaustive `run_all.py --ci-delegated` shards;
- every dedicated 9DVL audit;
- the maxout independent capstone audit; and
- the generator-coupled secondary maxout audit.

The shard-contract verifier proves the exact union and disjointness of the selected
suite before those jobs begin. The one verifier requiring a separately pinned external
artifact remains an explicit direct command documented with that result.

## Local use

```bash
# Always-on policy checks
python verify_repository_structure.py
python ops/ci/check_ci_policy.py
python ai/omreal/verify_run_all_ci_shards.py

# Local iteration and exhaustive replay
python run_all.py --fast
python run_all.py

# Inspect the route for a proposed diff
python ops/ci/classify_changes.py \
  --event pull_request --base origin/main --head HEAD --json
```

Some verifiers regenerate committed artifacts. Inspect any resulting diff; generation
need not be byte-stable, so CI reports drift without automatically treating it as a
failed proof.
