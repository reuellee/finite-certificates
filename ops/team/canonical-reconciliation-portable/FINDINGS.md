# PR #45 canonical-reconciliation portability findings

## Verdict

The published PR #45 head was not mergeable.  The defect was in the research
control plane, not in a mathematical theorem: it overwrote an immutable
diagonal-three ledger and treated an unpublished transient review chain as a
live CI dependency.

## Repair

- The original v1 diagonal-three ledger and verifier are preserved exactly by
  their Git blob and the pinned evidence bundle.  Their current repository
  paths hold the exact reviewed PR #46 v2 ledger and a historical-only,
  successor-safe verifier.
- The accepted v2 logical state is moved to
  `CANONICAL_RESEARCH_STATE.json` with only its authority/schema name changed.
  Reversing that one schema line reproduces SHA-256
  `73b0b742d6336d754ae99b7054858a3a3c96b3aaf1601b2228c076a732903d6e`.
- README, proof status, and the research operating system now identify the
  cross-diagonal canonical state as the sole current target selector.
- The four original exact-head PR #45 scripts and their transient commits are
  preserved in the pinned evidence bundle imported and replayed by CI.  At the
  current paths, one script remains byte-identical and three are successor-safe
  archival variants; the portable verifier pins both the original and current
  hashes, while `run_all.py` does not treat those historical scripts as current
  authority.
- A new standard-library verifier independently checks the immutable legacy
  bytes, the migrated state, published PR #42--#44 trees when available,
  pinned sources, authority pointers, governed paths, hostile mutations, and
  live legacy/current certificate replays.

## Scope

This repair changes no theorem claim.  The honest ledger remains **2/9**,
diagonals 1 and 2 only.  The state remains `PIVOT_REQUIRED`, with no selected
mathematical target pending the cross-domain opening audit.
