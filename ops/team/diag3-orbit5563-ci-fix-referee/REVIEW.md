# Independent review: D3 closing-verifier CI portability fix

Review date: `2026-08-30`

Verdict: **`ACCEPT_CI_PORTABILITY_FIX_AT_EXACT_PUBLIC_HEAD`**.

This review is exact-head evidence for the one-file CI portability repair only.
It does not advance a theorem, authorize topology, change a residue row, or
change the theorem ledger.

## Candidate identity and scope

- local candidate: `ef1e68d033df374d4401be869e401357818b528d`
- staged public candidate: `bf9fbfad75706794c2f05ce6f5d9a530ae53b23c`
- common parent: `827959f624a4e2d197f940c066b4baf4a9df5d5e`
- common tree: `444f8a7e50ec58e4d97a71744090d7ed60330f19`
- sole changed path:
  `ops/team/diag3-orbit5563-referee/verify_closing_referee.py`
- common verifier blob: `235e85bf211f08dadd0562ea967db2fd6e5ac319`
- verifier SHA-256:
  `29733ddef3128b736db27fb56daa4c1907d713daf80f1f65c69c180143d029e7`

The authenticated GitHub connector returned the public commit and its one-file
patch.  An exact read-only fetch followed by
`git show -s --format='%H %T %P %s' FETCH_HEAD` returned the public commit,
common tree, common parent, and expected message.  Both
`git diff --name-status 827959f624a4e2d197f940c066b4baf4a9df5d5e..FETCH_HEAD`
and the corresponding local diff reported only the verifier path.  The
`git ls-tree` check returned the same verifier blob for both candidates.

## Failure reproduction evidence

GitHub Actions workflow run `33310282641`, job `99254032091`, checked out the
synthetic pull-request merge `37cf865b8b8f4a9b4f8a18663c63392593cfc14a`
with `--depth=1`.  After the preceding shard verifiers passed, the old closing
verifier failed in `verify_repository_surface()` when
`git rev-parse bf6050ddc16e01dbff6da07d3d8c3ec31a9ab52f^{tree}` could not resolve
that local-only historical object.  This is a deterministic checkout
portability defect, not a mathematical or transient-infrastructure failure.

## Independent replay and hostile tests

All Python commands used `PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0`.

| Check | Exact command or construction | Result |
|---|---|---|
| full-history repository gate | `python3 ops/team/diag3-orbit5563-referee/verify_closing_referee.py --surface-only` | `PASS repository surface FULL_PUBLISHED_HISTORY` |
| genuine shallow checkout | `git clone --depth 1 --no-local --branch agent/diag3-orbit5563-ci-fix-referee-20260830 file:///workspace/scratch/9ff480392984/finite-certificates <pristine>`; run `--surface-only` | shallow=`true`; `PASS repository surface SHALLOW_PINNED_SURFACE` |
| changed pinned control artifact | append a hostile line to governed `CYCLE_REPORT.md` in a separate shallow clone; run `--surface-only` | exit `1`; `AuditError: governed artifact changed: .../CYCLE_REPORT.md` |
| missing governed artifact | move governed `OPENING_REVIEW.md` outside the governed roots in a separate shallow clone; run `--surface-only` | exit `1`; `AuditError: D3 governed surface changed` |
| extra governed artifact | add `UNAUTHORIZED_EXTRA.txt` under the referee root in a separate shallow clone; run `--surface-only` | exit `1`; `AuditError: D3 governed surface changed` |
| changed verifier working tree | modify the verifier docstring in a separate shallow clone; run `--surface-only` | exit `1`; `AuditError: governed D3 surface is dirty in shallow checkout` |
| non-shallow checkout lacking published history | archive the candidate tree into a new non-shallow Git repository with one synthetic root commit; run `--surface-only` | shallow=`false`, exit `1`; `AuditError: published history missing from full checkout` |
| complete closing replay | `python3 ops/team/diag3-orbit5563-referee/verify_closing_referee.py` | `PASS`; 2,604 parents, 40,320 frames, 100,086,840 quotient classes, 104,993,280 raw presentations; `7/7` hostile mathematical mutations rejected |
| cycle protocol | `python3 ops/research-team/verify_cycle_protocol.py` | `PASS research-cycle strategy/publication protocol: 3 cycles, 9 authorized work orders` |
| patch whitespace | `git diff --check 827959f624a4e2d197f940c066b4baf4a9df5d5e..ef1e68d033df374d4401be869e401357818b528d` | `PASS` (no output) |

The complete closing replay preserved
`CLOSING_SEMANTIC_SHA256 =
0ae6a0662872e78d31d116c53c77ec2df0efcee6d6f01dc39e16ca32235a5050`.
It ended with
`ACCEPT terminal=null row=1162302 ledger=2/9 strategy=PIVOT`.

## Fail-closed assessment

The full-history route remains strict: it resolves both published historical
commits or rejects partial history, compares both pinned trees, and requires
the exact twelve-file worker delta.  The fallback is entered only when neither
published object is resolvable and Git itself reports a shallow repository.
It requires the exact governed D3 path census, SHA-256 pins for all 21 governed
evidence/control artifacts, and a tracked, clean verifier.  The verifier source
is fixed externally by this exact public commit/tree/blob review; moving that
head invalidates this acceptance.  Thus the shallow route is not an unpinned
fallback and does not provide an escape hatch for damaged full repositories.

The frozen research result is unchanged:

- terminal classification: `null`;
- unresolved row count: `1,162,302 -> 1,162,302`;
- theorem ledger: `2/9 -> 2/9`;
- smallest missing global object: `Q3_COMPLETE_PARENT_BOUNDARY_ATLAS`;
- required next strategy: `PIVOT`;
- topology and row removal remain unauthorized.

## Invalidation conditions

This acceptance is invalid if the public candidate commit, parent, tree, blob,
or sole-path delta differs from the identities above; if the publication branch
moves to another head without a fresh exact-head review; if any governed digest
or path census changes; if either strict full-history check is weakened; if the
shallow route can accept a changed, missing, extra, dirty, or non-shallow
missing-history case; if the complete semantic digest changes; or if CI does
not pass at the exact independently reviewed publication head.
