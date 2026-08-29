# Diagonal-four signed delta rereview

Date: 2026-08-29 UTC

Integrated correction revision:
`977d0afdcffe0937005f6eddd0dd026dedb47a39`

Integrated correction tree:
`5a7003bf3f2a7e299d32918b676386825eae2c69`

Prior referee revision:
`b08c6e4ee2ea21cf879e67edd7bbac3b2a44dd94`

## Disposition

**REJECT the current exact head for publication, with one narrow wording
defect.**  The mathematical correction, semantic digest, file digests,
replays, prover clarifications, and nonconsequences all pass.  The falsifier
still contains several unqualified “complete/minimal abstract” output
sentences.  The prior handoff required every completeness sentence—not only
the schema and detailed domain paragraph—to state the base-line/two-exterior-
ray scope.

No mathematical recomputation or strategy change is required.  After the
sentences below are narrowed and their affected digests are refreshed, a
second signed-text delta is sufficient.

## Passed delta gates

### Falsifier schema and detailed scope

`MINIMAL_SIGNED_MODELS.json` now contains

```text
base_topology=oriented_line_with_two_exterior_rays
```

inside `abstract_search`.  The verifier requires the exact field and value.
Its module contract also states the full domain: a base line with two exterior
rays, connected exterior fibers, no births/deaths, at most two generic
split/merge events, and at most two simultaneous branches.

The detailed completeness paragraphs in `FINDINGS.md` and `RESULT.yaml` now
state the base-line scope and explicitly exclude circular and other non-line
bases.  The boundary canary is likewise limited to that domain.

### Refreshed semantic and file digests

The corrected JSON semantic digest is

```text
8a190441c7b307feb6fc6981f97a99ed8e0781d1423ea290ff1975f4a3d3c81e
```

and the corrected file SHA-256 values are:

| File | SHA-256 |
| --- | --- |
| `MINIMAL_SIGNED_MODELS.json` | `fee24515c91c3cf7fd9c06ac1f24204022e5a0bf6e8fc7723b990a6d83d80a16` |
| `verify_diag4_top_sheaf_falsifier.py` | `45d96cdcdbd9baf2a201c5df23f763f80553907a2db3b9edf849e34c13fdf7b3` |
| `FINDINGS.md` | `3c9ac3798d0a5eeeff0ba743da5f78db45ce741bdc3685c1093d9f0ad17c617c` |
| `RESULT.yaml` | `82befa766066844d60294d396248c0f19531704381d9c7f595de2ecaad325c8c` |

Every artifact digest stored inside `RESULT.yaml` matches the corrected file.
The falsifier replay exits zero and verifies the corrected semantic digest.

### Prover wording and manifest

`PROOF.md` now explicitly:

1. uses the four nonmoving rays as a basis;
2. invokes uniformity to make every moving-ray coordinate nonzero;
3. proves that the residual diagonal stabilizer is scalar by combining the
   `f`-line and distinct-`h`-line constraints;
4. states that no global trivialization of the top orientation local system
   is used because all fiber rows below four vanish; and
5. cites the canonical full `256`-pattern replay for signature index `7` in
   the positive B31 canary.

The updated prover manifest passes `sha256sum -c`; the corrected proof digest
is `9bef2f9e1c4fc2862080ebd83805f488001cb9d3eface0b0fb21bfc838006157`.
The canonical `verify_seeat_shatter8.py` replay also passes all 256 patterns.

### Claim-delta audit

The integrated changes do not broaden any accepted claim.  The falsifier
domain is narrowed; its topology and full-piece inclusion remain explicitly
uncomputed.  The prover still claims only the B31 intermediate theorem and
the `915,740 / 77` support-shape reduction.  D4-SP, the restriction maps,
diagonal four, and the `2/9` ledger remain open.

## Remaining fail-closed wording defect

The following sentences still assert abstract completeness/minimality without
the exact base-line qualifier:

1. `FINDINGS.md` outcome: “complete minimal abstract classification.”
2. `FINDINGS.md` classification conclusion: “exactly excludes every zero- or
   one-event obstruction in the declared abstract class.”
3. `RESULT.yaml` summary: “complete minimal abstract two-event signed class.”
4. `MINIMAL_SIGNED_MODELS.json` `theorem_effect`: “exactly excludes every
   zero- or one-event obstruction in the declared abstract class.”
5. Verifier output: “PASS abstract minimality: zero/one events are trees...”
6. Verifier output: “OUTCOME finite-exact abstract classification...”

The schema definition nearby does not satisfy the prior requirement that
**every completeness sentence** carry the scope.  In particular, a reader or
log consumer can encounter the summary or output line without its surrounding
definition.

Required correction:

- replace each occurrence with wording that explicitly says “over an
  oriented base line with two exterior rays” (and retain the other event,
  branch, exterior-connectivity, and birth/death bounds where the sentence
  summarizes the full class);
- keep circular and non-line bases explicitly excluded;
- refresh the JSON semantic digest if `theorem_effect` changes;
- refresh all affected file digests in `RESULT.yaml`; and
- rerun only the falsifier verifier, digest audit, prover manifest check, and
  canonical 256-pattern canary.

## Final gate state

| Gate | Result |
| --- | --- |
| Exact integrated identity/tree | pass |
| JSON base topology lock | pass |
| Verifier base topology lock | pass |
| Detailed domain/nonconsequence prose | pass |
| Every completeness sentence scoped | **fail** |
| Semantic/file digests | pass |
| Falsifier replay | pass |
| Prover required wording | pass |
| Full-256-pattern canary | pass |
| No claim broadening | pass |
| Ledger honesty | pass; no change |
| Publication at exact head | **rejected pending wording repair** |

The post-cycle `CONTINUE` verdict from the prior review is unchanged; this is
only a publication-scope defect.
