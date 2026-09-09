# September 9 exploration publication

This publishes the independently reviewed research checkpoint
`4e9b79480529473889b82048570af3bc1d6b1faf`, tree
`75f9e2f1622f8123bd520d34ae3359d644c181fd`, on the September 2 public main
`9e77c365b266e9d884e6ac14a0443992bec92c64`.

The user subsequently instructed: **"update github with that"**. That instruction
authorizes this publication branch and pull request. The historical cycle
records describing GitHub as read-only remain true records of those cycles.
This publication does not start another research cycle or advance a theorem.

The latest [cycle report](../../cycles/2026-09-09-exploration/CYCLE_REPORT.md) and
[independent review](../../../team/d3-explore-referee/FINAL_REVIEW.md) accept four
scoped auxiliary results: an actual feasibility boundary in parent-matrix
coordinates, a certified escape of one specified triple-bad component in
normalized parent space, a coherent-witness example, and a narrow obstruction
to replacing endpoint coordinates or columns. The ledger remains **2/9**;
all seven global obligations remain open. The unresolved **1,162,302** count
is a source-orbit count, not a connected-component denominator.

Earlier unpublished cycles are included because their exact certificates and
source pins are dependencies of this checkpoint. All research evidence remains
byte-identical to the reviewed checkpoint. Publication changes are limited to
the README pointer, CI/replay routing, the verifier census, and this directory.
The original versions of the changed navigation and CI files remain in the
evidence bundle.

## Reproduce

Use a full clone with Python 3.12 and numpy, scipy, and sympy installed. From
the repository root:

```sh
python -B ops/research-team/publications/2026-09-09-exploration/import_evidence.py
python -B ops/research-team/publications/2026-09-09-exploration/check_publication.py
python -B ops/team/d3-explore-referee/audit_opening.py
python -B ops/team/d3-explore-referee/verify_candidates.py
python -B ops/research-team/verify_cycle_protocol.py
python -B ai/omreal/verify_run_all_ci_shards.py
```

The bundle preserves the original commits even though GitHub publication has
a different parent chain. Its hash, prerequisites, refs, and the 354 changed
research files are recorded in [EVIDENCE_MANIFEST.json](provenance/EVIDENCE_MANIFEST.json).
The original September 3 mixed-carrier backup supplied four worker commits
that had been omitted from later recovery clones. Its recorded hash was checked
before import. Replays fail on absent objects, incorrect trees or digests, or
failed mathematical assertions.

The deterministic suite retains all **335** selected verifiers. Nine historical
gates run in their declared original worktrees; the saturation referee receives
its required frozen revision arguments. Existing archival exclusions and their
replacement gates are unchanged. The independent shard audit pins this mapping.
The GitHub workflow additionally requires the current exploration scope and
independent referee replay before the complete-suite check can pass.

CI status belongs to the actual GitHub publication commit and pull request;
this note makes no claim that pending or future checks have passed.
