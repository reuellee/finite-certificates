# Frozen canonical-reconciliation candidate review

Date: 2026-08-31 UTC

Track: `canonical-reconciliation-falsifier`

Frozen candidate: commit
`6e8fa4a74dbc9e0e130719f9c55df86d58a75707`, tree
`10fd994ccc89b722cd92118759cee65fc8a1906c`.

Verdict: **`REJECT_ACTIONABLE_ROUTE_OMISSION`**.

The candidate correctly represents every one of the eight enumerated bounded
endpoint facts under a schema different from the falsifier's independently
assumed schema. Those schema and prose differences are not authoritative and
are not rejection grounds. One distinct accepted PR #43 route disposition is
nevertheless absent from both current canonical surfaces and their verifier:
the complete alternating D4/total-complex route must remain retired until its
global input object exists. This is substantive under the work order's
quantifier over every route disposition, so the exact head rejects.

No theorem or count mismatch was found. The theorem delta is exactly `NONE`;
the score remains `2/9` with diagonals 1 and 2 only.

## Exact-head and artifact identity

| Object | Exact identity |
| --- | --- |
| reviewed head | commit `6e8fa4a74dbc9e0e130719f9c55df86d58a75707` |
| reviewed tree | `10fd994ccc89b722cd92118759cee65fc8a1906c` |
| reconciled candidate commit | `12f155c707366ab830252e7226e0030ddd1bd7e2` |
| canonical base | commit `e666990f5b0cf07fef4a639bbb6596ddc9c4515a`, tree `444f8a7e50ec58e4d97a71744090d7ed60330f19` |
| reconciliation opening | commit `e548a28832232a34ed9e408224f6e16a9ebc9e4b`, tree `99d7c10657088d6cebc7c80568f7224d1079af7c` |
| original falsifier verifier SHA-256 | `d482fa2337e0df542c9b550cd1b894aa7845d76200196071f8b51ad9d82cb840` |
| original falsifier manifest SHA-256 | `3a2bc113711dd27ab3145512655f2afc6a68216866790f09370fe285de801abf` |
| candidate status SHA-256 | `8e4070084805b812e03ccfea56ec23f2043f8e235857b75e5160ad69e426989e` |
| candidate ledger SHA-256 | `aaa4a59af8872154833fed38c7d97deccd4e4046514dedd91fb51692a01119f5` |
| candidate ledger verifier SHA-256 | `e894645cf67d7edbf53bbb52ccf78bf0e96c807df885566da4c03e2ae560a04c` |

The diff from the reconciliation opening contains 12 paths. Every path is one
of the three approved canonical files or lies below an approved prover,
falsifier, or referee prefix; there is no unauthorized-path defect.

## Untouched original verifier result

The original verifier was not edited or relaxed. At the frozen head this exact
command

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 python3 \
  ops/team/canonical-reconciliation-falsifier/verify_canonical_reconciliation_falsifier.py \
  --candidate
```

exits `1` and emits exactly:

```text
REJECT candidate status missing accepted fact: e666990f5b0cf07fef4a639bbb6596ddc9c4515a
```

That first failure is a non-authoritative prose assumption. The candidate
does bind the canonical commit, tree, and merged PR in
`repository.audited_commit`, `repository.audited_tree`, and
`repository.merged_pull_request`; neither the cycle's eight positive endpoint
items nor the status-document work order requires the commit hash to be
duplicated in status prose. The original fail-closed output is preserved, but
it is not the substantive rejection ground.

## Independent replay of the eight bounded endpoints

This comparison reads the candidate JSON and status directly; it does not
import the candidate verifier or the original falsifier's validation
functions.

| Endpoint from `CYCLE.md` | Candidate representation | Result |
| --- | --- | --- |
| unchanged `2/9`, diagonals 1 and 2 | current object, theorem object, and status agree | `PASS` |
| `1,715,980 / 130 = 915,740 / 77 + 800,240 / 53` | exact `d4_accounting` values and both sum identities | `PASS` |
| PR #43 survivor delta `0 / 0`; no further D4-S53 cycle | nested zero delta and `D4_S53_CONTINUATION` in `retired_continuations` | `PASS` |
| `100,086,840` quotient classes; `104,993,280` raw/multiplicity sum | exact `d3_accounting` values | `PASS` |
| D3 residue `1,162,302` | current object and open triple obligation agree | `PASS` |
| first missing `Q3_COMPLETE_PARENT_BOUNDARY_ATLAS` | current object has that ID with status `MISSING` | `PASS` |
| retire orbit-5563 roadmap, box, collar, macrobox, clipped-wall | five separate current retirement identifiers | `PASS` |
| `PIVOT_REQUIRED`; no selected mathematical target | ledger status and both current target pointers | `PASS` |

Additional exact checks pass:

- canonical repository commit/tree and merged PR #44;
- D3 universe arithmetic `79,102,449 - 77,940,147 = 1,162,302`;
- both diagonal-three obligations remain `OPEN`;
- no `3/9` promotion and no count delta;
- the old selected target and macrobox `next_stage` survive only below
  explicitly historical keys, while
  `historical_continuation_text_is_current` is `false`; and
- all 12 changed paths are approved.

The candidate's canonical verifier exits zero and its seven hostile canaries
reject. The original falsifier source replay and independent synthetic replay
also still pass with 12 sources and 9/9 hostile rejections. These are useful
corroboration, not substitutes for the missing route check below.

## Actionable mismatch

### `D4_TOTAL_COMPLEX_RETIRED_UNTIL_GLOBAL_INPUTS` is absent

The accepted PR #43 report distinguishes two dispositions in its final
strategy section:

1. pivot away from D4-S53 and prohibit continuation on that route; and
2. retire the complete alternating D4 route until its global input object
   exists, with an incomplete successor input gate stopping fail-closed.

The current cycle repeats the second disposition in its mandatory opening
strategy table: `D4 signed fivefold total complex` has verdict `RETIRE` until
global inputs exist. The falsifier work order quantifies over every accepted
route disposition, not only the eight endpoint field labels.

The candidate records only the first disposition. Its current status mentions
retired D4-S53 continuation and the five retired orbit-5563 local routes. Its
current ledger `retired_continuations` has those same six identifiers. Neither
canonical surface contains a current total-complex/complete-alternating-D4
retirement. The verifier constant `RETIRED_CONTINUATIONS` likewise omits it,
and the route-retirement hostile canary can therefore pass without testing it.

This is not a spelling, nesting, or schema disagreement. D4-S53 continuation
is a narrower route than the complete alternating D4 total complex, and PR #43
records them separately. The candidate silently loses one current governing
disposition. Under the exact work-order stop rule, this is actionable and the
head must reject.

## Complete mismatch adjudication

| Original falsifier assumption or mismatch | Candidate semantics | Authority classification |
| --- | --- | --- |
| status must literally contain canonical commit `e666...` | exact commit/tree/PR are machine-checked in the ledger | non-authoritative prose placement |
| status must contain contiguous phrase `no selected mathematical target` | the words are split by a newline but state exactly the same fact | non-authoritative formatting |
| status must contain phrase `no further D4-S53 cycle` | it says any further D4-S53 continuation is retired | non-authoritative equivalent prose |
| top-level current object must equal schema `9dvl-canonical-reconciliation-v1` byte-for-field | candidate uses ledger format v2 and a differently named current object | non-authoritative independently assumed schema |
| PR number and canonical commit/tree must live inside that object | candidate places them in the adjacent authoritative repository object | non-authoritative field placement |
| explicit `theorem_delta: NONE` field | unchanged exact score, proved set, open obligations, and no-change status establish the same semantics | non-authoritative encoding |
| D4 counts use `complete/b31/survivor_*` names | candidate uses `domain/proved/survivor_*` with identical values and arithmetic | non-authoritative field names |
| explicit D4-S53, D4-SP, and diagonal-four `OPEN` fields | all survivors remain, only diagonals 1 and 2 are proved, and status row four remains open | non-authoritative dedicated-field assumption |
| D3 current object also repeats `2,604` parent types and `40,320` frames | required endpoint records the quotient/raw identity; frozen sources remain pinned and replayed | non-authoritative stronger repetition assumption |
| Q3 status literal `MISSING_FAIL_CLOSED` | candidate uses `MISSING` and states blocked attachments | non-authoritative status vocabulary |
| route dispositions must be one nested mapping | candidate uses a retirement list plus target-selection field | non-authoritative structure except for the omitted total-D4 item |
| retained historical progress must omit `next_stage` | candidate moves it under `historical_selected_target_progress` and machine-checks that historical continuation is non-current | non-authoritative historical-preservation design |
| historical candidate row must not retain `selected: true` | it is below `historical_candidate_targets`; both live target pointers are null | non-authoritative preserved history |
| exact contract rejects candidate-only precedence/source/history fields as extras | those fields strengthen source binding and current-over-history precedence | non-authoritative extras |
| complete alternating D4/total-complex route must be retired until global inputs | no equivalent current field, prose, verifier assertion, or hostile canary exists | **actionable accepted-route omission** |

Thus the original exact-object equality is too strong to decide this candidate
as a whole. After field-level semantic adjudication, all of its schema/prose
differences are harmless except the last row.

## Theorem effect and nonconsequences

Theorem delta: **`NONE`**.

- score remains `2/9`;
- proved diagonals remain `[1, 2]`;
- D4 survivors remain `800,240 / 53` with zero PR #43 delta;
- D3 residue remains `1,162,302`;
- both D3 obligations remain open;
- Q3 remains missing;
- no mathematical target is selected; and
- this review proves no new mathematics and recommends no count or theorem
  change.

The rejection concerns canonical route completeness only.

## Suggested discriminator

The smallest decisive repair is a new candidate head that:

1. adds one explicit current canonical disposition equivalent to
   `D4_TOTAL_COMPLEX_RETIRED_UNTIL_GLOBAL_INPUTS` to both status and ledger;
2. makes the canonical verifier assert that disposition independently of
   D4-S53 retirement;
3. adds a hostile mutation that deletes or changes only the total-D4
   disposition while retaining D4-S53 retirement, and observes rejection; and
4. freezes a new exact commit/tree for independent referee replay.

The original falsifier verifier must remain unchanged. Its unmandated
schema/prose failures should be adjudicated explicitly rather than used as a
repair specification. Acceptance requires the new semantic discriminator and
all existing exact-count, no-target, source, path, and false-promotion gates.
