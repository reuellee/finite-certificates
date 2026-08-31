# PR #45 canonical-reconciliation portability findings

## Verdict

The published PR #45 head was not mergeable.  The defect was in the research
control plane, not in a mathematical theorem: it overwrote an immutable
diagonal-three ledger and treated an unpublished transient review chain as a
live CI dependency.

## Repair

- The v1 diagonal-three ledger and verifier are restored byte-for-byte.
- The accepted v2 logical state is moved to
  `CANONICAL_RESEARCH_STATE.json` with only its authority/schema name changed.
  Reversing that one schema line reproduces SHA-256
  `73b0b742d6336d754ae99b7054858a3a3c96b3aaf1601b2228c076a732903d6e`.
- README, proof status, and the research operating system now identify the
  cross-diagonal canonical state as the sole current target selector.
- Four exact-head PR #45 scripts remain byte-for-byte archival evidence at
  their documented paths.  Their transient commits are no longer retrievable,
  so `run_all.py` reports them as archival instead of pretending they replay.
- A new standard-library verifier independently checks the immutable legacy
  bytes, the migrated state, published PR #42--#44 trees when available,
  pinned sources, authority pointers, governed paths, hostile mutations, and
  live legacy/current certificate replays.

## Scope

This repair changes no theorem claim.  The honest ledger remains **2/9**,
diagonals 1 and 2 only.  The state remains `PIVOT_REQUIRED`, with no selected
mathematical target pending the cross-domain opening audit.
