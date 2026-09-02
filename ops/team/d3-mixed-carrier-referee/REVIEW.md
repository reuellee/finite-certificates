# Independent closing review: D3 mixed-carrier theorem feasibility

## Verdict

**`ACCEPT_FROZEN_CANDIDATE_FAIL_CLOSED`** for corrected frozen candidate
`2fc366e517c3bf30419b335053bec0895519b675`, tree
`1520090d7f6a9ce6febeef4a0c50b31982ace560`.

The governed referee handoff: `NULL`. The governed cycle handoff: `NULL`.
Here `NULL` means that no complete finite A/B/C proof program and no
full-scope universal negative survived the bounded gate. It does **not** prove
that A, B, C, D3, or 9DVL is impossible.

## Frozen intake and bounded correction

The tracked worktree was clean on
`research/lane-d3-mixed-carrier-referee-20260901` before review. I read the
package from immutable Git objects rather than accepting a mutable head. The
verified chain is:

| role | commit | tree | parent |
| --- | --- | --- | --- |
| immutable canonical predecessor | `9116771ba80ed3d033516d0dd666b34348aad348` | `a64438426dc792af67d5ccc0dd2f4d1231dbaa14` | `fa9787b8295fae46a262d610698e7d21790c63bd` |
| opening | `dd86907bebbfaaac9caee4e1d93dc77bc9f3ad8b` | `a59d740c008ae04accf200a8373d16b4d9c70ae4` | `9116771ba80ed3d033516d0dd666b34348aad348` |
| integrated evidence | `2cf92fa094b80b89816feceaf6cce6c712f72115` | `ec92c870ff48949b1c6587556b6a930e025da733` | `91e6a0eac369c93de6b8d7abee7a758c26c6aec6` |
| checkpoint | `f1f955f6ae69e6a847ea8795724c77896636c547` | `c4b68a4dfdafccb66f4c69695d733fa78e840570` | `2cf92fa094b80b89816feceaf6cce6c712f72115` |
| v1 preflight | `7f135917f7ef859ec272ac3126725db272ff3ea1` | `ab724829b045fd9a5d3f89573757db40adec6f38` | `f1f955f6ae69e6a847ea8795724c77896636c547` |
| corrected frozen v2 | `2fc366e517c3bf30419b335053bec0895519b675` | `1520090d7f6a9ce6febeef4a0c50b31982ace560` | `7f135917f7ef859ec272ac3126725db272ff3ea1` |

The v1 preflight rejection found a real report/protocol mismatch: the report
claimed protocol `PASS` but omitted six mandatory convergence labels. That
preflight was not a final referee handoff. The coordinator's bounded v2
correction changes exactly one path, `CYCLE_REPORT.md`, by 18 insertions and
zero deletions. The inserted block consists exactly of the six required
labels and their already-frozen values. No producer file, candidate or
checkpoint JSON, source pin, mathematical statement, ledger fact, or
program-status byte changed.

The exact repaired gate-table claim is retained and now replays:

| research-cycle protocol | `PASS`, 19 cycles and 78 work orders |

## Source, evidence, and producer identity

The V8 contract, all ten V8-declared source SHA-256 pins, all thirteen opening
source byte-count/SHA-256 pins, the charter/work orders, checkpoint, candidate,
report, and all six producer evidence bytes match the frozen v2 tree. The six
candidate evidence digests are reproduced in `RESULT.json` and independently
recomputed by `verify_referee.py`.

The three isolated producer commits are present but are not ancestors of the
frozen candidate, exactly as declared. Each has opening commit `dd86907...` as
its parent, changes only its two assigned files, and those file bytes equal the
integrated and frozen bytes:

| lane | isolated commit / tree | integrated commit | handoff |
| --- | --- | --- | --- |
| topology | `2697c7a87c085ed6066c9903cb224518737492db` / `418e214e7867d79d992ce50a9b8ea85c4c70fc03` | `3c78fb8a181dca98b191db68395cfad9bc68f6c0` | `NULL` |
| falsifier | `2c12eb03e86cf5412a9d701adafd30bcc5facb10` / `74388045eaa5215413122143d8e45f8f2ea46f6b` | `91e6a0eac369c93de6b8d7abee7a758c26c6aec6` | `NULL` |
| naturality | `a10a6e517af0ca66c5454926e7e7035358071c9c` / `2418ec86497a0271820d299016357936c96ab384` | `2cf92fa094b80b89816feceaf6cce6c712f72115` | `NULL` |

## Independent substantive reconstruction

All three discovery handoffs are exact `NULL`:

- A is `NULL`: its conditional `L_source` interface is noncircular, but there
  is no universal genuinely mixed assignment on one simultaneous subdivision
  with arbitrary face-chain coherence.
- B is `NULL`: there is no finite exhaustive source instance, complete joined
  relative complex, filtration-preserving comparison to the actual bad union,
  or proved rational pair kernel.
- C is `NULL`: the source-orbit residual is not a component denominator and
  there is no component-complete stable-identity/continuation input reaching
  certified true parent infinity.

The falsifier's three exact negatives are scoped to fixed triangular order,
pointwise first-exit assembly, and graph-only pair-H1 inference. None is a
universal negative for A, B, or C. Conversely, naming conditional interfaces
and missing lemmas is not a positive finite program. The package therefore
contains neither a universal negative nor a positive finite program.

The midpoint fired after all three complete handoffs. Every continuation
condition is false, so the exact decision is
`STOP_DISCOVERY_FREEZE_AND_SEND_TO_REFEREE`; no referee-directed revision,
resource enlargement, or construction follows.

Opening and checkpoint vector:

```text
(2/9, 1, {diag3_pair_hc1, diag3_triple_hc0}, 7,
 UNKNOWN, UNKNOWN, 5, 8)
```

Closing vector:

```text
(2/9, 1, {diag3_pair_hc1, diag3_triple_hc0}, 7,
 UNKNOWN, UNKNOWN, 6, 9)
```

All seven obligations—global gluing, extension labels, strict closure,
relative infinity, middle-rank replay, `diag3_pair_hc1`, and
`diag3_triple_hc0`—remain `UNCHANGED`. The ledger remains `2/9`, delta `0/9`.
The trajectory is `STALLED`, action `STOP`, successor `NONE`, construction
`false`, and theorem promotion `NONE`.

## Accounting and scope checks

I independently enumerated joined shapes through total joined degree three.
There are 10 shape orbits modulo active-block permutation and 34 formal
labeled placements in one three-block family. Only `(0)`, `(1)`, and `(2)` are
universally credited. Thus `3/10` is taxonomy, not an end-to-end denominator.

Triple accounting remains `77,940,147 / 79,102,449`, with residual
`1,162,302` **source orbits** and delta zero. It is neither a component count
nor a pair denominator. Pair residual and global coverage remain literal
`UNKNOWN`, with zero certified global adjacencies, closure pairs/triples, or
parent-infinity cells.

The row-2599 chart-zero canary replays with ranks `3,6,7`, relative homology
`H0=0, H1=0, H2=Z`, and primitive relation
`(-1,1,1,1,1,1,1)`. It retires only singleton-only fixed-block-root carriers;
it is not a universal A negative or a D3 counterexample.

For C, I exhaustively checked all 4,096 directed graphs on three vertices with
all true-infinity markings. “Every vertex reaches certified true parent
infinity” is equivalent to “every sink SCC contains it.” This verifies the
conditional predicate only. The required component-complete, component-
faithful accepting input graph remains absent. Likewise, the compared signed
integral pair complex remains absent.

## Rejected overclaims

The review rejects every promotion from these facts, including:

- interpreting `NULL` as impossibility;
- promoting a scoped ansatz no-go to a universal negative;
- treating A's interface or dependency graph as a complete finite program;
- inferring global rank or the rational pair kernel from row 2599 or A alone;
- inferring pair H1 from a component exit graph;
- promoting one path per source orbit to all-component escape;
- treating `1,162,302` source orbits as components;
- treating `3/10` taxonomy as global coverage;
- treating support loss, witness rank drop, zero weight, or a local cutoff as
  true parent infinity; or
- promoting D3 or 9DVL while B and C remain open.

## Verification summary

The independent verifier is original Python standard-library logic and does
not import producer acceptance code. It checks immutable Git objects and
parents, exact v1-to-v2 repair topology, package and source/evidence SHA-256
pins, producer isolation/integration, cross-document contract relations,
shape enumeration, the conditional exit equivalence, and exactly 87 hostile
mutations. All 87 were rejected.

The following exact replays pass on frozen v2:

- V8 canonical contract: 98 hostile mutations;
- opening contract: 65/65 hostiles and 13/13 source pins;
- research-cycle protocol: 19 cycles and 78 authorized work orders;
- joined flow triangle, single-bad two-skeleton, fixed-order no-go,
  tangential first-exit no-go, and conditional global-exit criterion; and
- this independent referee verifier: frozen v2 accepted fail-closed, 87/87
  hostile mutations rejected.

## Final strategy decision

No construction, successor, ledger edit, or theorem promotion is authorized.
The next action is `STOP`; selected successor is `NONE`. Reopening requires a
new explicitly governed cycle with a concrete finite route for at least one
first missing global edge. The exact referee handoff remains `NULL`, and the
exact cycle handoff remains `NULL`.
