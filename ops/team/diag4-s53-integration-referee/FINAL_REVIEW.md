# D4-S53 final integration-head review

Date: 2026-08-30 UTC

Track: `diag4-s53-integration-referee`

Verdict: **ACCEPT** the exact content of PR #43 at published head
`06de9659d5090846afe09c95f1f8549d1d7b2ba5`, tree
`692d173462497cb645127ea1ced6cbe40aba4d5a`, subject to required CI passing
at that unchanged head and the coordinator's separate merge decision.

This acceptance is invalid if the PR head or tree moves. It does not merge the
PR, edit the theorem ledger, approve a new research cycle, or promote either
null handoff to a theorem or counterexample.

## Exact candidate and PR state

The frozen local integration candidate is
`3d3c3b3109a2873b7a20856a637730c4c5995517`, tree
`692d173462497cb645127ea1ced6cbe40aba4d5a`. The authenticated GitHub connector
returned the matching published commit and tree:

- repository: `reuellee/finite-certificates`;
- PR: `#43`, “Close D4-S53 cycle with mandatory pivot”;
- state: open, non-draft, mergeable, not merged;
- base: `main` at `aa784af939b55d3503e4782a9d65a9b06cf81ce0`;
- head branch: `research/diag4-s53-cycle-20260830`;
- head commit: `06de9659d5090846afe09c95f1f8549d1d7b2ba5`;
- head tree: `692d173462497cb645127ea1ced6cbe40aba4d5a`;
- changed files: `21`, exactly the local base-to-head file set;
- CI at review time: workflow `verify`, run `33306581017`, `in_progress`.

The authenticated branch ref points to the same head. The published head's
parent is `3716290fbf0c30520c3cdb9e95abab4dda498b2c`, tree
`2a85625ee518ebbc67539a6658ee1ced1d199572`, which matches the report's
pre-report integrated publication. The final report commit adds only
`CYCLE_REPORT.md`; its staging language correctly leaves PR, CI, and merge
pending rather than claiming they had already passed.

## Frozen handoff identity

The integrated subtrees are exactly identical to the previously accepted
local handoff subtrees:

| Handoff | Frozen local commit | Published commit | Integrated subtree | Result |
| --- | --- | --- | --- | --- |
| prover | `f232021960689d0b2a6a9e033dfe16939143643d` | `a0ae3bee592c92b74856786078152f21638009c8` | `e0c1bf5a3ef29e0e6d91d2f95eaaf2fe3d9c3758` | PASS |
| falsifier | `e4903f5a4193fb73b9e0e75657df9d0741a8bf9e` | `3428d26ecede8fd708b790b63efc1335fd2fb397` | `e5e776442599ab28950de5d156bbbcb8b3ac2d3d` | PASS |
| opening/closing referee | `516f0d964c42e9eea93b8cb02a66d860db64e51e` | `f37bd7d58316453809921f2b968af07627713867` | `516b4a96654675772a0fda150525fb776c86c933` | PASS |

The connector independently returned the declared tree for every published
handoff commit. No discovery or referee artifact was altered during
integration.

## Independent replay at the integrated tree

The prover generator reproduced `STRUCTURAL_SCAN.json` byte-for-byte. Its
independent verifier and manifest passed and returned

`1,715,980 / 130 = 915,740 / 77 + 800,240 / 53`,

with four size-four and forty-nine size-five survivor orbits, common-apex-four
coverage `0/53`, the weaker profiles limited to `2+2`, `2+1+1`, and
`1+1+1+1`, and every signed, hostile-topology, orientation, and null canary
passing. Its outcome remains a complete structural null.

The falsifier generator reproduced `CANDIDATE_DOMAIN.json` byte-for-byte. Its
independent verifier and manifest passed: the exact row-2599 tuple and all
`70` signed parent polynomials reconstruct, the bounded outer enclosure is
valid, and `U=(-1/84,1/84)^4` has compact-support ranks `[0,0,0,0,1]`.
The whole-domain topology and full-piece inclusion remain explicitly
`UNREACHED`; all abstract-false-positive, sign-mutation, boundary,
realizability, and inclusion-failure canaries pass.

The closing referee YAML and review digest match, and retain
`PASS_NULL_HANDOFFS`, zero survivor delta, ledger `2/9 -> 2/9`, and mandatory
`PIVOT`.

## Publication-authorization hardening

`verify_cycle_protocol.py` now extracts the standing authorization quote from
`PROTOCOL.md` and requires byte-for-byte equality with each governed cycle's
anchored authorization block. It also requires every work order to reference
that anchor and separately requires `worker_restrictions`.

Independent checks confirm:

- two governed cycles parse, with three work orders each;
- all six aliases expand to the exact standing authorization;
- a hostile mutation of “authenticated GitHub connector” fails exact equality;
- the worker restriction remains outside the verbatim quote and forbids merge
  and theorem-ledger updates;
- after removing only authorization metadata and worker restrictions, both
  old and new work-order documents are semantically identical to their frozen
  predecessors.

Thus the hardening corrects the prior phrase-only weakness without changing a
target, quantifier, assumption, deliverable, stop rule, or role boundary.

## Claim, ledger, strategy, and recovery audit

The integration makes no theorem claim. The exact survivor class remains
`800,240` labeled supports in `53` orbits; the survivor delta is zero supports
and zero orbits. D4-S53, D4-SP, diagonal four, the multi-piece and
adjacent-degree terms, compactification, sign/orientation transport,
restriction maps, and fivefold exactness all remain open. The canonical ledger
file is byte-identical to the base, retains SHA-256
`f4360254e5c7e624b9c9194bb7cb0b3844d5fe3201ec9bc688c2f18d37276782`,
and remains `2/9`.

The closing strategy is therefore the frozen mandatory **`PIVOT`**. The
report correctly prohibits another D4-S53 cycle and treats a possible D3
successor only as a candidate requiring a new independently audited opening.

The recorded recovery bundle was also replayed locally: size `58,704,004`
bytes, SHA-256
`51329e0c7a288068d96144206695f65f090066a6aa9c0ab4eb3aa941012f80a8`,
complete history, and `git bundle verify` passes. Its ref and manifest bind the
pre-report integrated local commit and the identical published tree exactly as
stated in the cycle report.

## Final gate table

| Gate | Result |
| --- | --- |
| exact local/published PR-head tree | PASS |
| frozen handoff subtree identity | PASS |
| artifact manifests and deterministic replay | PASS |
| independent/hostile canaries | PASS |
| protocol and YAML parsing | PASS |
| exact standing-authorization enforcement | PASS |
| diff check and ledger immutability | PASS |
| claim scope and nonconsequences | PASS |
| zero survivor/ledger delta | PASS |
| mandatory PIVOT | PASS |
| recovery bundle receipt | PASS |
| required CI at exact PR head | **PENDING COORDINATOR** |
| merge at unchanged reviewed head | **PENDING COORDINATOR** |

No actionable content defect or claim inflation was found. **ACCEPT** the
exact PR #43 head named above; fail closed and rereview if it changes.
