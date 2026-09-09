# Publication replay audit — 9DVL exploration, 2026-09-09

Implementation commit: `498a61d9cdb9a1fab3dac44d3d6779756b69ee46`.

Verdict: ACCEPT publication replay adaptation, conditional on importing the complete pinned research and recovered mixed-100 evidence bundles before the suite. No mathematical assertions or historical evidence files were edited. The canonical ledger remains 2/9; all seven global obligations remain open.

## Selection integrity

- The selected CI universe is 335 verifiers. The exact pre-existing four delegated gates, one external-input gate, and 18 archival exclusions/replacement relationships are unchanged.
- Nine selected gates execute the unchanged original verifier in an exact pinned clean worktree; none is discarded or reclassified.
- The saturation-injectivity referee remains selected and receives the two raw candidate revisions recorded in its independent replay.
- Each historical route pins the original commit, full tree, current verifier SHA256, and historical verifier SHA256. The shard-coverage gate independently freezes the mapping and still proves union and disjointness.

## Historical context mapping

| Selected path | Execution revision |
|---|---|
| `ops/research-team/cycles/2026-09-02-d3-triple-critical-saturation-component-gate1/verify_closing.py` | `fb667bfe33ef9e945a82e9a23b615e67f5f39c0f` |
| `ops/research-team/cycles/2026-09-03-d3-mixed-block-100-universal-carrier-gate1/verify_closing_candidate.py` | `a10a47d1e934e4296b9612ccbde6d0b1a74a88bb` |
| `ops/research-team/cycles/2026-09-03-d3-mixed-block-100-universal-carrier-gate1/verify_final_closing.py` | `a10a47d1e934e4296b9612ccbde6d0b1a74a88bb` |
| `ops/research-team/cycles/2026-09-03-d3-mixed-block-100-universal-carrier-gate1/verify_mid_cycle.py` | `a10a47d1e934e4296b9612ccbde6d0b1a74a88bb` |
| `ops/research-team/cycles/2026-09-03-d3-mixed-block-100-universal-carrier-gate1/verify_opening_state.py` | `a10a47d1e934e4296b9612ccbde6d0b1a74a88bb` |
| `ops/research-team/cycles/2026-09-04-d3-block-gordan-compact-relative-source-gate1/verify_opening_state.py` | `843eac01cbb0a8c0a84840e286a7a42943bcac9c` |
| `ops/team/d3-mixed-100-carrier-constructor/verify_constructor.py` | `a10a47d1e934e4296b9612ccbde6d0b1a74a88bb` |
| `ops/team/d3-mixed-100-carrier-falsifier/verify_falsifier.py` | `a10a47d1e934e4296b9612ccbde6d0b1a74a88bb` |
| `ops/team/d3-mixed-100-independent-verifier/verify_independent.py` | `a10a47d1e934e4296b9612ccbde6d0b1a74a88bb` |

The final mixed-100 verifier in the raw latest checkpoint includes a successor adapter. Its frozen replay runs the original verifier at the recorded final close, with both versions separately SHA256-pinned. No historical file is rewritten.

## Verification evidence

- Targeted baseline audit executed 45 changed or context-sensitive scripts; it identified stale census, historical source drift, missing raw mixed-100 objects, missing required referee arguments, and a local SymPy dependency. These issues were addressed without broadening the mathematical claims.
- All nine pinned historical routes passed after importing the recovered original mixed-100 bundle.
- The saturation-injectivity referee passed with its recorded prover/falsifier arguments.
- Updated shard census and canonical reconciliation gates passed.
- Mixed-100 closing referee passed all 57 hostile mutations after recovery; algebra identity gate passed after SymPy installation.
- Synthetic publication commit `bb76737550377650680086d578aaeaecedd74c81` has public main `9e77c365b266e9d884e6ac14a0443992bec92c64` as its sole parent. All 16 context-sensitive candidates passed in that checkout. The raw research chain is not an ancestor of this synthetic publication.
- Five adapter hostile controls rejected missing commit, incorrect tree, altered current verifier pin, altered historical verifier pin, and an undeclared path.
- The topology producer verifier rewrites timing fields in `EXACT_RESULT.json`; the audit restored only this audit-generated drift before the clean-tree reconciliation check. The mathematical result bytes were not changed by the publication adaptation.

## Replay commands

```sh
python -B ai/omreal/verify_run_all_ci_shards.py
python -B ops/team/canonical-reconciliation-portable/verify_canonical_reconciliation_portable.py
python -B ops/research-team/publications/2026-09-09-exploration/replay_verifier.py <exact-selected-path-from-table>
python -B ops/team/d3-satinj-referee/verify_frozen_candidates.py --prover-revision 3c3ccbcac95fe05543a870c86da1b2d29342f526 --falsifier-revision 1f8be67c47679d4283edec4b67ba3ae70c1c4818
python -B ops/team/d3-mixed-100-closing-referee/verify_close.py
python -B ops/team/ai-d3-reset-source/verify_identities.py
```

## Remaining limits

No unresolved failure remains in this targeted portability audit. The complete expensive verifier suite, Lean kernel job, and capstone CI gates were not rerun locally; required GitHub checks remain the publication acceptance gate. This audit does not certify the coordinator’s bundle importer or public upload byte equivalence; those are separate coordinator checks.
