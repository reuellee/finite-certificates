# D3 orbit-5563 independent falsifier gate

Date: 2026-08-30 UTC

Track: `diag3-orbit5563-falsifier`

Terminal classification: **`null`**.

The exact type/frame/`S_8` quotient is complete, but the full-space
transport gate stops at the first missing obligation: there is no complete
parent-boundary atlas and attachment proof over all normalized realization
spaces. No local topology computation was started. The unresolved-row count
remains `1,162,302`, and the theorem ledger remains `2/9`.

## Frozen input identity

| Object | Identity |
| --- | --- |
| local opening-GO base | commit `bf6050ddc16e01dbff6da07d3d8c3ec31a9ab52f`, tree `4213fdb2adf5722d1b8a6b70aba4507e959fba6d` |
| published opening-GO base | commit `9e578f6e9d094b3342ca474f0d188428dd44ae7a` |
| canonical row | `(5563,4373,23221)` |
| named presentation | `(5563,16134,19284)` |
| parent catalog | SHA-256 `c55e805d60d8086bcb84a312f2103a9973fc2691d0fd97f3d9a1d9809d2b163b` |

## Layer 1: exact quotient manifest

The reconstruction reads the `2,604` realizable reorientation-class
chirotopes and independently enumerates every lexicographic `S_8` frame.
For a parent type `M`, it compares all `70` normalized bracket signs after:

1. putting the first four framed columns at the coordinate basis;
2. putting the fifth column at `(1,1,1,1)` by exact Cramer signs; and
3. fixing the residual projective orientations of positions `5,6,7` with
   the nonzero anchor brackets `012k`.

Equality of all `70` signs reconstructs the exact projective/reorientation
automorphism group `Aut(M)`. Exhaustive group closure and inverse checks pass
for every parent. A redundant, non-oracular cross-check agrees for all
`2,604` parents with the independently stored `omgamma` full-group
stabilizer orders after its exact order-two sign kernel is removed.

The quotient is

```text
Aut(M) \ S8 / Stab(5563,16134,19284).
```

The named factor triple has trivial stabilizer, verified directly from the
pinned primitive-factor action. Thus the parent automorphism action on
frames is free, every quotient class for `M` has multiplicity `|Aut(M)|`,
and the manifest records the complete quotient compactly with an identity-
only default plus the exact automorphism frame ranks for every nontrivial
parent.

| Quantity | Exact result |
| --- | ---: |
| realizable unlabelled parent types | `2,604` |
| frames per parent | `40,320` |
| raw frame-parent presentations | `104,993,280` |
| quotient classes | `100,086,840` |
| sum of quotient multiplicities | `104,993,280` |
| named-triple stabilizer order | `1` |

The exact quotient-class multiplicity histogram is:

| Class multiplicity | Quotient classes |
| ---: | ---: |
| `1` | `96,042,240` |
| `2` | `3,689,280` |
| `3` | `134,400` |
| `4` | `161,280` |
| `6` | `20,160` |
| `8` | `30,240` |
| `12` | `3,360` |
| `16` | `2,520` |
| `24` | `3,360` |

The weighted sum is exactly `104,993,280`. The quotient semantic SHA-256 is

```text
89bd3a5d7185cfe66b26afb7225ae5262da44e071604372445bcf0d342f1e15c.
```

## Layer 2: full-space transport contract

Open-cell sign and chart transport passes at its exact quantifier. For every
point of every uniform normalized parent realization space and every framed
quotient class:

- every chart denominator is a nonzero parent bracket;
- its sign is fixed by the chirotope;
- the normalized bracket signs follow the exact determinant-order and Cramer
  gauge formula used by the quotient reconstruction; and
- transitions between valid open charts are rational Cramer maps localized
  only at parent-bracket units.

This is a statement about every point, not an evaluation at the stored
representative matrix. It still does not partition triple-zero components or
cover rank drop, closure, or infinity.

The smallest missing obligation is
`Q3_COMPLETE_PARENT_BOUNDARY_ATLAS`: a complete finite normalized
compactification atlas for every parent quotient class, with exact transition
domains and exhaustive named boundary strata. The existing exact boundary
stratification is for one named chart and explicitly disclaims a global
primary decomposition or closure theorem. Consequently all component,
rank-drop, simultaneous-wall, extra-factor, and true-infinity attachments
remain blocked.

The required strata remain fail-closed:

```text
open parent points; coordinate; chart divisor; parent wall;
singular/rank drop; occurrence rank; concurrence rank; extra factor;
simultaneous wall; true parent infinity.
```

The transport-contract semantic SHA-256 is

```text
a790d8eabf5172bba9b51bbfef1a87c19d6cac78a2f8f0d9138f14c4ca78fe2e.
```

## Hostile canaries and scope

The replay rejects all of the following mutations:

- a missing quotient multiplicity;
- a missing identity automorphism;
- an artificial chart or work boundary relabelled as true infinity;
- an omitted singular/rank-drop stratum; and
- promotion of a stored representative matrix to full realization-space
  coverage.

No prover acceptance flag or artifact was used. No component search, local
box, collar, macrobox, clipped-wall continuation, row-count edit, or theorem-
ledger edit was performed.

## Clean replay

```bash
PYTHONDONTWRITEBYTECODE=1 python3 \
  ops/team/diag3-orbit5563-falsifier/verify_falsifier_gate.py
```

Observed clean replay: under `13` seconds and `202,020 KiB` peak resident
memory, well below the 30-minute first gate and 12-GiB ceiling.

The terminal handoff is `null`, not `timeout`: the quotient manifest is
complete, while the minimal full-space boundary/attachment proof is missing.
The mandatory recommendation is **`PIVOT`**. Do not start another local box,
collar, macrobox, or clipped-wall continuation for this residue.
