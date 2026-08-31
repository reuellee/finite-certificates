# Repaired canonical-reconciliation candidate review

Date: 2026-08-31 UTC

Track: `canonical-reconciliation-falsifier`

Reviewed candidate: commit
`77ea32c05eefd312a15ae0096e2990621da03a84`, tree
`669c6782874b2d8de97f0d78a5ee86cb5c0c3fcc`.

Verdict: **`ACCEPT_REPAIRED_CANONICAL_RECONCILIATION`**.

The repaired exact head records both distinct accepted PR #43 route
dispositions on both current canonical surfaces:

1. another D4-S53 cycle is retired; and
2. the complete alternating D4 total-complex route is separately
   `RETIRED_UNTIL_GLOBAL_INPUTS`, with all three required global inputs named
   and an incomplete successor input gate fixed at `STOP_FAIL_CLOSED`.

The canonical verifier asserts both dispositions. It directly hostile-tests
total-D4 deletion and reactivation, while the additive independent verifier
exercises deletion and reactivation for both routes across status, ledger, and
verifier surfaces. All repaired semantics, counts, sources, path scope,
history, and nonconsequences pass. No actionable defect remains in the
reviewed scope.

This red-team acceptance does not publish, merge, or select a mathematical
target. Final publication authority remains with the coordinator after a
fresh independent closing review at this exact head.

## Exact identity and rejected-head chain

| Stage | Commit | Tree | Result |
| --- | --- | --- | --- |
| canonical base / PR #44 | `e666990f5b0cf07fef4a639bbb6596ddc9c4515a` | `444f8a7e50ec58e4d97a71744090d7ed60330f19` | frozen source |
| reconciliation opening | `e548a28832232a34ed9e408224f6e16a9ebc9e4b` | `99d7c10657088d6cebc7c80568f7224d1079af7c` | frozen opening |
| rejected candidate | `6e8fa4a74dbc9e0e130719f9c55df86d58a75707` | `10fd994ccc89b722cd92118759cee65fc8a1906c` | `REJECT_ACTIONABLE_ROUTE_OMISSION` |
| rejection review | `3f764ce3e6fce92f984d0cf8249321452e7934c2` | `de18908882290dd304f2558daf439a18d170d077` | preserves exact defect |
| semantic repair | `ca6a154899fea133920dfa435a597632bf03728d` | `00bc0e4affed33ed29e7dee5ba17f0c3d4b5e3fd` | seals total-D4 route |
| reviewed repaired head | `77ea32c05eefd312a15ae0096e2990621da03a84` | `669c6782874b2d8de97f0d78a5ee86cb5c0c3fcc` | accepted by this red-team gate |

Git replay proves the exact parent chain

```text
6e8fa4a -> 3f764ce -> ca6a154 -> 77ea32c
```

and verifies base/opening ancestry. The final step adds the independently
authored rejection record for the old `6e8fa4a` head; every such artifact
explicitly binds that old head and therefore does not assert that the repaired
head is rejected.

Prior rejection evidence is byte-preserved:

| Artifact | SHA-256 |
| --- | --- |
| original falsifier verifier | `d482fa2337e0df542c9b550cd1b894aa7845d76200196071f8b51ad9d82cb840` |
| `CANDIDATE_REVIEW.md` | `9cb60fc5f89857c97be2b36a48746ab005aa866c4befd1e6148654c1c30a7e2e` |
| `CANDIDATE_HANDOFF.yaml` | `1adb7d13c83ae683b73b4cb36d636502d267d37771ac68427ec8f71509ed3e7a` |
| old closing `CLOSING_REVIEW.md` | `2a7e79b451fc5cd01ec62d739019967998d4825cd4c34ef6962750ffeb3edf04` |
| old closing `CLOSING_HANDOFF.yaml` | `fc920833045b91768ecc524449e379ca549092279eae93843f3db6ced8ee7d80` |
| old closing `CLOSING_MANIFEST.json` | `3c62bc8c943cf8582c40609634a5ad185dc51d8c0a6e723095b2d58abe1ebd9f` |
| old closing verifier | `9d14f0a0afa988f76d1ff86e92f2064958b6cee87f750da51fcd82da6db4c83c` |

## Repair replay on all three canonical surfaces

### Status

The leading current-precedence section retains the exact D4 accounting and
states that any further D4-S53 continuation is retired. A separate following
paragraph says the complete alternating D4 total-complex route is
`RETIRED_UNTIL_GLOBAL_INPUTS`, explicitly distinguishes it from D4-S53, names

- theorem-ready global compactification;
- signed face poset; and
- restriction matrices,

and requires a successor missing any input to `STOP` fail-closed. It also
retains `2/9`, the D3 quotient/raw/residue counts, the missing Q3 atlas, all
five orbit-5563 local retirements, `PIVOT_REQUIRED`, and no selected target.

Status SHA-256:
`a5865422b3337aba0ccd71eb02c1d521c201f4c338b9a2054afa0d21923e35b0`.

### Ledger

`retired_continuations` still contains `D4_S53_CONTINUATION` independently of
the five orbit-5563 local routes. The new current mapping is:

```text
conditional_route_dispositions.D4_ALTERNATING_TOTAL_COMPLEX
  status = RETIRED_UNTIL_GLOBAL_INPUTS
  distinct_from = D4_S53_CONTINUATION
  required_global_inputs =
    THEOREM_READY_GLOBAL_COMPACTIFICATION,
    SIGNED_FACE_POSET,
    RESTRICTION_MATRICES
  incomplete_successor_input_gate = STOP_FAIL_CLOSED
  reactivation_requires_all_inputs = true
```

All original current facts are unchanged. Ledger SHA-256:
`73b0b742d6336d754ae99b7054858a3a3c96b3aaf1601b2228c076a732903d6e`.

### Canonical verifier

The candidate verifier now:

- asserts the exact local-retirement list containing D4-S53;
- asserts the separate total-D4 disposition and all three inputs;
- requires the matching current status prose;
- rejects total-D4 reactivation;
- rejects total-D4 deletion; and
- reports 9/9 native hostile canaries.

Its clean replay exits zero. Canonical verifier SHA-256:
`3353ed3f7f185034f97a3e440e7957ebcf4046032a8fbf20bbc5d7e445060491`.

The native generic local-route canary deletes the last orbit-5563 entry rather
than D4-S53 specifically. That is not a semantic hole because the exact-list
assertion rejects any D4-S53 change, but it leaves a canary-coverage gap for
this review order. The additive independent verifier closes it with explicit
D4-S53 deletion and reactivation mutations without changing the canonical
verifier.

## Schema-neutral independent verifier

`verify_repaired_candidate_semantics.py` uses only the Python standard
library. It reads all reviewed canonical bytes with `git show` at the pinned
candidate commit; it imports neither candidate nor original falsifier logic.
It verifies:

- eight commit/tree identities, including accepted PR #42--#44, and the exact
  repair/rejection parent chain;
- all 12 frozen source SHA-256 digests;
- all three repaired canonical-output digests;
- seven preserved rejection-artifact digests;
- 18/18 opening-to-candidate paths within the approved surface;
- the eight bounded reconciliation endpoints and separate total-D4 route;
- D3 universe/residue arithmetic and both open obligations;
- candidate-native verifier exit zero and 9/9 native canaries; and
- the original verifier's unchanged expected non-authoritative rejection.

The independent replay rejects 20/20 hostile mutations. Twelve are the full
route matrix:

| Surface | D4-S53 deletion | D4-S53 reactivation | total-D4 deletion | total-D4 reactivation |
| --- | --- | --- | --- | --- |
| status | rejected | rejected | rejected | rejected |
| ledger | rejected | rejected | rejected | rejected |
| canonical verifier text | rejected | rejected | rejected | rejected |

The other eight mutations are false `3/9`, changed D4 count, changed D3
quotient count, changed D3 residue, promoted Q3, active old target, changed
source digest, and unauthorized path. All reject.

Verifier SHA-256:
`96089be7c1b84c22f9b907fcaf34a93f8ab7c20c6c744c37225709bf49021621`.

Deterministic result semantic SHA-256:
`037021e2fb8fe3692d961e8482a476c4ba2bb4d9b77427cd82e10faa26d3cf32`.

## Exact facts and nonconsequences

| Field | Repaired canonical value |
| --- | --- |
| theorem score | `2/9` |
| proved diagonals | `[1, 2]` |
| theorem delta | `NONE` |
| D4 identity | `1,715,980 / 130 = 915,740 / 77 + 800,240 / 53` |
| PR #43 survivor delta | `0` supports / `0` orbits |
| D4-S53 continuation | `RETIRED` |
| complete alternating D4 total complex | `RETIRED_UNTIL_GLOBAL_INPUTS` |
| D3 quotient/raw | `100,086,840 / 104,993,280` |
| D3 residue | `1,162,302` |
| first missing object | `Q3_COMPLETE_PARENT_BOUNDARY_ATLAS` / `MISSING` |
| orbit-5563 local continuation | roadmap, box, collar, macrobox, clipped-wall all retired |
| control state | `PIVOT_REQUIRED` |
| selected mathematical target | none |

The D3 obligation replay also preserves
`79,102,449 - 77,940,147 = 1,162,302`; both diagonal-three obligations remain
open. No D4 survivor or D3 row is removed, no compact component or global
closure is claimed, no diagonal is promoted, and no mathematical target is
selected.

## Original verifier arbitration

The original verifier remains byte-identical and continues to exit `1` with
exact output:

```text
REJECT candidate status missing accepted fact: e666990f5b0cf07fef4a639bbb6596ddc9c4515a
```

As the prior falsifier and independent referee already recorded, requiring the
base SHA literally in status prose and requiring exact equality to the
falsifier-invented v1 object are non-authoritative presentation assumptions.
The correct base commit/tree/PR identity is machine-checked in the ledger.
Neither `CYCLE.md` nor `WORK_ORDERS.yaml` mandates the falsifier's prose
location, field names, nesting, or no-extra-field rule. This review does not
relax or edit that verifier; it adjudicates the alternate schema by normalized
authoritative semantics.

## Source, path, and replay results

- 12/12 frozen source bytes: `PASS`.
- repaired candidate output bytes: `PASS`.
- rejected-head artifacts and ancestry: `PASS`.
- candidate canonical verifier: `PASS`, 9/9 native canaries.
- cycle protocol: `PASS`, 4 cycles / 13 authorized work orders.
- original source reconstruction: `PASS`, fact SHA-256
  `a6a2913d7409ec9907ee9c249037d2fd508efa52a42b72603eb4e6e069f49789`.
- original synthetic replay: `PASS`, 9/9 hostiles rejected.
- opening-to-candidate changed paths: 18/18 approved.
- independent semantic replay: `PASS`, 20/20 hostiles rejected.

No external source, paid service, mutable branch result, or new mathematical
artifact was used.

## Disposition

There is no falsifier-side repair request and no ledger/count/theorem change
recommended. The coordinator may freeze this exact repaired head for a fresh
independent closing review. Any later byte, path, route status, input gate,
count, Q3 state, target, or theorem-score change requires a new review; this
acceptance is not portable to another commit or tree.
