# Canonical reconciliation independent falsifier

Date: 2026-08-31 UTC

Track: `canonical-reconciliation-falsifier`

Terminal classification: **complete independent hostile replay; future
candidate not reviewed by design**.

The frozen PR #42--#44 reports and closing reviews are mutually consistent.
They reconstruct one exact post-PR-44 state: the theorem score remains `2/9`,
the accepted D4 survivor class remains `800,240 / 53`, the D3 quotient has
`100,086,840` classes and raw multiplicity `104,993,280`, the D3 residue
remains `1,162,302`, and the first missing global object is
`Q3_COMPLETE_PARENT_BOUNDARY_ATLAS`. The mandatory disposition is
`PIVOT_REQUIRED`, with neither another D4-S53 cycle nor further orbit-5563
local roadmap/box/collar/macrobox/clipped-wall continuation authorized.

No future prover branch or candidate was inspected. The opening canonical
files are intentionally unreconciled controls and are rejected by the gate.

## Frozen identities and source accounting

| Object | Exact identity |
| --- | --- |
| canonical base | commit `e666990f5b0cf07fef4a639bbb6596ddc9c4515a`, tree `444f8a7e50ec58e4d97a71744090d7ed60330f19` |
| falsifier opening | commit `e548a28832232a34ed9e408224f6e16a9ebc9e4b`, tree `99d7c10657088d6cebc7c80568f7224d1079af7c` |
| accepted PR #42 merge | commit `aa784af939b55d3503e4782a9d65a9b06cf81ce0`, tree `6aa36a92c5e5d2e420ec660a1ad2c2be2b06a561` |
| accepted PR #43 merge | commit `9332f507996a8594883619cb530565ced79b59eb`, tree `692d173462497cb645127ea1ced6cbe40aba4d5a` |
| accepted PR #44 merge | commit `e666990f5b0cf07fef4a639bbb6596ddc9c4515a`, tree `444f8a7e50ec58e4d97a71744090d7ed60330f19` |
| source manifest semantic SHA-256 | `7527e9c0c7a1e4c2c407925b560a30a60c7bef6f44078738f4aa0385c982a145` |
| reconstructed fact SHA-256 | `a6a2913d7409ec9907ee9c249037d2fd508efa52a42b72603eb4e6e069f49789` |

The manifest pins 12 inputs: the protocol; the opening status, decision
ledger, and canonical ledger verifier; both reports/reviews for PR #42, PR
#43, and PR #44; and this cycle's `CYCLE.md` and `WORK_ORDERS.yaml`. Each file
is read from its declared frozen revision and checked byte-for-byte by
SHA-256. Protected reports, reviews, protocol, and cycle controls must also
match the working tree. The verifier independently checks all five commit/tree
identities above.

## Exact reconstruction

### Theorem and D4

| Field | Exact value |
| --- | ---: |
| theorem score | `2/9` |
| proved diagonals | `1, 2` |
| theorem delta | `NONE` |
| complete D4 supports / orbits | `1,715,980 / 130` |
| B31 supports / orbits | `915,740 / 77` |
| surviving supports / orbits | `800,240 / 53` |
| PR #43 survivor delta | `0 / 0` |
| size-four / size-five survivor orbits | `4 / 49` |
| D4-S53, D4-SP, diagonal four | `OPEN / OPEN / OPEN` |

The two exact cover identities replay:

```text
1,715,980 = 915,740 + 800,240
130 = 77 + 53
```

PR #43's complete zero-delta replay triggers the frozen stagnation rule. A
further D4-S53 cycle is prohibited, and the D4 total-complex route remains
retired until global inputs exist.

### D3

| Field | Exact value |
| --- | ---: |
| realizable unlabelled parent types | `2,604` |
| frames per parent | `40,320` |
| raw frame-parent presentations | `104,993,280` |
| quotient classes | `100,086,840` |
| hard-triple stabilizer order / orbit size | `1 / 40,320` |
| triple universe | `79,102,449` |
| proved noncompact | `77,940,147` |
| unresolved residue | `1,162,302` |
| first missing object | `Q3_COMPLETE_PARENT_BOUNDARY_ATLAS` |

The independent nine-bin automorphism-order histogram sums to all `2,604`
parents and `100,086,840` quotient classes; weighting each class count by its
automorphism order gives `104,993,280`. The two further identities replay:

```text
2,604 * 40,320 = 104,993,280
79,102,449 - 77,940,147 = 1,162,302
```

The missing atlas stays explicitly fail-closed. Representative matrices,
local charts, local collars, and artificial box boundaries are not promoted
to all-parent realization-space or compactification coverage.

## Independent acceptance contract

The candidate contract is a versioned, exact JSON object, not a loose keyword
test. A candidate ledger must be through PR #44 at the canonical commit and
tree, be dated `2026-08-31`, have state `PIVOT_REQUIRED`, select no target,
retain both D3 obligations as `OPEN`, reproduce every D3/D4 count, preserve
`2/9` and proved diagonals `[1,2]`, name the Q3 blocker as missing, and encode
all mandatory retirements. Historical selected-target progress is allowed
only if non-governing and has no `next_stage`.

These are intentionally strict schema assumptions, independently chosen
without seeing the prover candidate: the reconciliation object must occur at
top-level key `canonical_reconciliation` and equal the manifest contract
without missing, changed, or extra fields; `repository.audited_tree` is
required; `selected_target_progress`, if retained, must have one of
`HISTORICAL`, `HISTORICAL_FROZEN`, or `RETIRED_HISTORY`; and the status prose
must contain the prescribed exact facts plus case-insensitive phrases for no
selected target and both retirements. A semantically equivalent candidate
using a different schema will reject and requires explicit coordinator/referee
adjudication rather than silent relaxation of this independent gate.

The status document is separately required to state the exact D4 identity,
D3 quotient/raw/residue counts, Q3 blocker, zero theorem promotion, no selected
target, and both route retirements. The changed-path gate allows only the four
canonical reconciliation paths and the three named team surfaces.

The verifier imports no candidate module, canonical verifier, generator, or
prover acceptance logic. It uses only Python standard-library modules and
frozen bytes obtained directly with `git show`.

## Hostile replay

The synthetic positive control passes. All nine hostile mutations reject:

| Canary | Mutation | Result |
| --- | --- | --- |
| `stale_pr37_head` | restore PR #37 commit/current-control identity | `REJECTED` |
| `active_old_target` | select `fullsupport_master_closure_compiler` | `REJECTED` |
| `macrobox_continuation` | restore the macroboxes `0..5` next stage | `REJECTED` |
| `d4_s53_continuation` | permit another D4-S53 cycle | `REJECTED` |
| `false_3_of_9` | promote the score to `3/9` | `REJECTED` |
| `changed_d3_count` | alter the D3 residue (the full contract also seals quotient/raw counts) | `REJECTED` |
| `changed_d4_count` | alter a D4 survivor count (the full contract seals every D4 count) | `REJECTED` |
| `missing_q3_blocker` | mark the missing Q3 atlas as passed | `REJECTED` |
| `unapproved_path` | add `README.md` to the candidate change set | `REJECTED` |

Self-test semantic SHA-256:
`e2b4fda007208c9d9eb692428d785c4bad12ed24a9414a6cae0cf9887d54aff4`.

## Opening-state negative control

Running the candidate gate on the untouched opening state exits nonzero at
the first missing reconciliation fact:

```text
REJECT candidate status missing accepted fact:
1,715,980 / 130 = 915,740 / 77 + 800,240 / 53
```

An independent field read also confirms the known stale controls: ledger
format v1, status `ACTIVE`, date `2026-08-28`, audited PR #37 commit
`e8600495e70e6f5548cb0c73e0cfd2f33faacc0b`, selected target
`fullsupport_master_closure_compiler`, an active macrobox next-stage, and no
versioned canonical-reconciliation object. These controls are not defects in
a future candidate because no future candidate was inspected.

## Checked, unchecked, and nonconsequences

Checked completely:

- all 12 frozen source digests and five commit/tree identities;
- every accepted PR #42--#44 count and arithmetic identity listed above;
- all accepted route dispositions and theorem nonconsequences;
- exact candidate field contract and allowed change surface; and
- the positive control plus all nine hostile mutations.

Unchecked by explicit work-order separation:

- any future prover branch, commit, tree, or candidate artifact digest;
- an integrated candidate's actual changed-path set and candidate verifier;
- coordinator integration, clean-head replay, CI, publication, and merge.

This work proves no diagonal, removes no survivor, changes no count, selects
no mathematical target, and recommends no ledger edit. It does not construct
the Q3 atlas or authorize a finite/global compactification theorem. The next
use of this artifact is adversarial replay against a separately frozen
integrated candidate by the independent closing referee.

## Replay

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 python3 \
  ops/team/canonical-reconciliation-falsifier/verify_canonical_reconciliation_falsifier.py \
  --sources-only

PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 python3 \
  ops/team/canonical-reconciliation-falsifier/verify_canonical_reconciliation_falsifier.py \
  --self-test

PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 python3 \
  ops/team/canonical-reconciliation-falsifier/verify_canonical_reconciliation_falsifier.py \
  --candidate
```

Expected results are respectively `PASS`, `PASS` with nine rejected hostile
mutations, and `REJECT` on the untouched opening state. The candidate command
is intended to pass only after invocation from an independently frozen,
fully reconciled integration head.
