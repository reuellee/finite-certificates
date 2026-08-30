# D3 residue-orbit global-exit opening review

Date: 2026-08-30 UTC

Track: `diag3-orbit5563-referee`

Opening verdict: **MODIFY**.

The proposed diagonal-three target is mathematically suitable for one bounded,
fail-closed cycle, but discovery must not start from the current control
plane. Four contract defects are blocking: the prior D4-S53 closing evidence
is not pinned in canonical/concurrency accounting, the first-gate failure
classification contradicts the declared null deliverable, and the work-order
authorization is not the standing authorization copied verbatim; the parent
type/frame census also lacks an explicit full-realization-space scope guard.

This review is independent of discovery. It uses only the frozen opening
control plane and canonical inputs, and it does not implement a component
search or accept any discovery-side flag.

## Frozen opening identities

| Object | Identity |
| --- | --- |
| canonical base | commit `aa784af939b55d3503e4782a9d65a9b06cf81ce0`, tree `6aa36a92c5e5d2e420ec660a1ad2c2be2b06a561` |
| local opening control plane | commit `20ca3c9631fcd50eafc5eb11106f01dd36aee20b`, tree `a8ecae19ec9e851f28fffe51d1bd0d4abc0d759f` |
| published opening control plane | commit `4d59201e84fd588b91a2a858ac4468c18b863544` on `research/diag3-orbit5563-global-exit-20260830` |
| ledger | `2/9`, diagonal-three triple residue `1,162,302` |

The local opening commit is a direct child of the canonical base. The
authenticated GitHub connector returned the named published coordinator
commit. Candidate publication and integration remain coordinator work.

## Independent replay

| Gate | Clean command or check | Result |
| --- | --- | --- |
| cycle protocol | `PYTHONDONTWRITEBYTECODE=1 python3 ops/research-team/verify_cycle_protocol.py` | PASS: two governed cycles, six authorized work orders under the current phrase-level checker |
| factor action / Burnside | `PYTHONDONTWRITEBYTECODE=1 python3 ai/omreal/verify_diag3_triple_factor_orbits.py` | PASS: `6`, `9,476`, `79,102,449`; semantic SHA-256 `9dc473537e87e509031d4843d960f5ea4bfefb8508262cd1ebb5d44e1a49913d` |
| global-exit kernel | `PYTHONDONTWRITEBYTECODE=1 python3 ai/omreal/verify_diag3_global_exit_criterion.py` | PASS: accepting component-faithful exit is sufficient; rejection is inconclusive; artificial-boundary and omitted-edge canaries reject |
| full-space feasibility | `PYTHONDONTWRITEBYTECODE=1 python3 ai/omreal/verify_diag3_triple_fullspace_feasibility_gate.py` | PASS replay of the expected `FAIL_CLOSED`; semantic SHA-256 `874c4895ae17843c6827c1c3a8d528eac0b45fc35dedc9159e4f447786ed2ace` |
| canonical completion object | `PYTHONDONTWRITEBYTECODE=1 python3 ai/omreal/verify_diag3_completion_open_object.py` | PASS: `77,940,147 / 79,102,449`, residue `1,162,302`, pair global closure open, ledger `2/9` |
| canonical decision ledger | `PYTHONDONTWRITEBYTECODE=1 python3 ai/omreal/verify_diag3_research_decision_ledger.py` | PASS; prior clipped-wall route is refuted and no invariant advances |
| parent/frame audit | `PYTHONDONTWRITEBYTECODE=1 python3 ai/omreal/verify_diag3_triple_rank_drop_parent_atlas.py` | PASS: `2,604` realizable types, `104,993,280 = 2,604 * 40,320` raw frame-parent presentations, hard-triple stabilizer trivial |
| boundary strata | `PYTHONDONTWRITEBYTECODE=1 python3 ai/omreal/verify_diag3_triple_boundary_stratification.py` | PASS at its stated scope; no primary decomposition or global closure claim |
| pinned raw inputs | independent `sha256sum` over all path-valued `canonical_inputs` | PASS: every listed raw digest matches |
| YAML and git identity | independent parse plus `git rev-parse` | PASS: three work orders; opening commit/tree/base identities match locally |

The full-space replay maps named presentation `(5563,16134,19284)` to the
canonical row `(5563,4373,23221)`. The global-exit replay independently pins
the starting count and the one-way theorem. These results authenticate the
target but do not supply any component coverage.

## Opening strategy audit

The strategic pivot is sound once its source is pinned.

- The D4-S53 closing review reconstructs the entire survivor equation
  `1,715,980 / 130 = 915,740 / 77 + 800,240 / 53`, finds zero survivor
  reduction, preserves the `2/9` ledger, and invokes its mandatory pivot.
  Its closing review has SHA-256
  `7eabc7700ea0a6e2dde0b05eab698b3bff98911c07aa11dc0a12250cacda7e4c`.
  The observed published heads are coordinator `1a3486a256e5a2e3ad7f2aed1953d3d1107f7cbf`,
  prover `a0ae3bee592c92b74856786078152f21638009c8`, falsifier
  `3428d26ecede8fd708b790b63efc1335fd2fb397`, and closing referee
  `f37bd7d58316453809921f2b968af07627713867`. These observations belong in
  the D3 control plane rather than only in this review.
- Diagonal eight still lacks a coverage-certified two-chain, infinity, and
  global dominance data. A graph-only continuation cannot decide its `H_1`
  target.
- Diagonal nine has only a 24-chamber training network and no
  full-dimensional parent roadmap or registered globally quantified family.
- The selected D3 row has a finite sufficient acceptance predicate, a
  decisive compact-component obstruction, a hard 30-minute domain gate, and
  a mandatory pivot if neither terminal outcome is reached.

This does not make the D3 route likely to succeed inside 90 minutes. Its value
is the bounded discriminator: exact domain compression or an immediate
fail-closed handoff, with no permission for another local box/collar loop.

## Quantifier and domain audit

The theorem quantifiers are correct if the following distinction is enforced.
The catalog contains `2,604` realizable unlabelled oriented-matroid types and
one exact representative matrix for each; it is not a finite set of sample
points that covers the full nine-dimensional realization spaces. The
contractibility input makes each normalized parent realization space the
theorem parent cell, while chirotope signs and label transport are constant
data on that cell.

Therefore the first gate must expose two different layers:

1. an exact type/frame/orbit quotient whose raw sanity census is
   `2,604 * 40,320 = 104,993,280`, with the selected triple's identity
   stabilizer and every quotient multiplicity checked; and
2. a proof contract explaining how sign and chart formulas range over every
   point and every required stratum of each complete normalized realization
   space.

A calculation only at the `2,604` stored matrices satisfies the first layer's
sign census but never proves component, rank-drop, closure, or infinity
coverage. The prover and falsifier must preserve that guard in every result.

The declared positive endpoint is otherwise exact: complete stable
local-component IDs, sound continuation, exhaustive components and strata,
sound membership in `I = Xbar \setminus X`, and every sink SCC meeting `I` remove
exactly the one canonical `S_8` orbit, changing `1,162,302` to `1,162,301`.
The negative endpoint correctly requires a complete closure certificate for
an actual component disjoint from all true parent infinity. Graph rejection
alone is never negative evidence.

## Blocking modifications

1. **Pin and inventory the D4-S53 close.** The canonical base is merged PR
   #42, whose own report permits one more D4 cycle. The later D4-S53 closing
   evidence is on unmerged/published research branches, yet the D3 control
   plane cites it without immutable identities. Add the D4-S53 control-plane,
   prover, falsifier, and closing-referee local/published commit and tree
   identities, closing handoff/review digests, and current integration status
   to canonical input and concurrency accounting. It need not be merged first,
   but it must be frozen and explicitly nonconcurrent before its pivot can be
   load-bearing.

2. **Make first-gate outcomes internally consistent.** At present, failure to
   produce the exact quotient manifest is classified `null`, while the null
   deliverable itself requires that exact manifest. Define separately:
   manifest complete but transport/attachment proof missing (`null`), and
   manifest incomplete at 30 minutes (`timeout`, with a reproducible partial
   frontier and every uncovered quantifier fail-closed). Apply the same rule
   to prover, falsifier, and `CYCLE.md`.

3. **Copy the authorization verbatim and test it.** The YAML anchor removes
   the backticks in the repository, Drive path, and `gh`, changes sentence
   spacing, and appends worker restrictions to the quoted text. Replace the
   anchor with the exact standing authorization from `PROTOCOL.md`; put worker
   restrictions in a separate field. The current protocol verifier checks
   only phrases and accepted this drift. Strengthen it to compare the
   canonical authorization text after only the documented Markdown
   blockquote-prefix removal.

4. **Lock the parent-space guard into the gate.** State explicitly that
   `2,604` counts oriented-matroid types, that the raw frame sanity census is
   `104,993,280`, and that representative-matrix evaluation cannot certify a
   complete realization cell. Require quotient multiplicities to sum to the
   raw census before any topology work begins.

After these four changes, rerun this opening audit at an exact corrected
commit and tree. Until then no prover or falsifier discovery should start.

## Resource, publication, and stagnation judgment

The 30-minute first gate, one-turn/90-minute/12-GiB discovery bounds, ordinary
local compute restriction, no-paid-service rule, and explicit timeout
frontiers are appropriate. The stagnation rule is also adequate: without an
exact row removal or exact compact component, no further local roadmap,
collar, macrobox, or clipped-wall continuation for this residue is allowed.

No ledger or row-count change is authorized at opening. Workers remain
restricted to their named branches and owned surfaces; only the coordinator
may integrate, open a pull request, merge after exact-head review/checks, or
change the theorem ledger.
