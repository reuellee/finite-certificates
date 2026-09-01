# Independent closing review: D9 S12,37 normal-link gate

## Verdict

**ACCEPT** `NORMAL_LINK_REDUCTION_NO_GO` at frozen head
`5efbd07a25b818306f9fd22597fd81a0f2091309`, tree
`b8cb35941043ff40be06cba98461ddab0ba14c8f`.

This is a finite-exact **local normal-link route no-go**. It retires the
tangential four-support reduction as stated and changes no theorem claim. The
ledger remains `2/9`.

## Frozen-head and authority gates

- The reviewed head has the exact declared tree and sole parent
  `c6bd7a6afeda0888fc950710b941cac6f6c9bf95`.
- Every path changed from that parent lies in exactly one of the producer,
  falsifier, or certificate-engineer surfaces. The referee changes only its
  assigned surface.
- The 2026-09-01 authority epoch replays exactly: ChatGPT Library is canonical,
  Google Drive `Projects/research-backups` is recovery-only, local scratch is
  ephemeral, and GitHub is read-only. No push, PR, CI trigger, or merge was
  performed.
- The cycle protocol and opening audit replay from their pinned source files.

## Independent source and orientation replay

The referee does not import discovery-side acceptance code. It rebuilds the
84,840 transported circuit occurrences with its own exact 4-by-4 determinant,
localization, normalization, and family-alignment routines. The replay finds:

- 8,916 certified-empty factor classes;
- 3,539 active oriented factor classes;
- 6,167 total global occurrences of those active classes, which is the
  producer inventory convention;
- 5,026 occurrences aligned with at least one `S12,37` family signature,
  which is the certificate contract convention; and
- certificate census semantic digest
  `a1b9d3d9da1e01df83621dc8f1c7959f86ae2e0d9bd3bc457124c561cbac245a`.

Thus 6,167 and 5,026 are distinct, reconciled counts rather than a discrepancy.
All 6,167 producer occurrence rows are compared to independently derived
foursets, representatives, raw-to-primitive signs, stripped parent units,
unit signs, scalar signs, and active-signature incidence.

## Producer obstruction

All 70 oriented parent inequalities are rebuilt from the pinned parent source.
At `(a,g,h)=(3/4,1/4,1/2)`, exact differentiation gives these decisive raw
and primitive first forms:

| Support | Labels | Raw forms | Primitive forms | Positive Gordan weights |
| --- | --- | --- | --- | --- |
| `(3,1,15)` | `1237`, `1367` | `n4`, `-3/4 n4` | `n4`, `-n4` | `(1,1)` after positive primitive normalization; equivalently `(3,4)` raw |
| `(3,3,7)` | `1237`, `1278` | `n3`, `-1/2 n3` | `n3`, `-n3` | `(1,1)` after positive primitive normalization; equivalently `(1,2)` raw |

Positive normalization preserves each strict halfspace. Therefore the ordinary
common-radial strict parent model is infeasible at both exact replayed support
points. This is a singular first-order model, not a theorem that inward arcs
do not exist. Weighted blow-ups on the forced facets remain required.

The referee also checks the full producer inventories: 3,539 factor forms and
70 parent forms on each support, their semantic digests, and the no-go result
digest. The accepted consequence stops before a stabilization radius because
the ordinary first-order strict link is already singular.

## Falsifier obstruction

Independent orientation gives factor 8552 the allowed side `d*i-e<0`. On
support `(3,1,15)` its lowest normal form is `d/4-e`. The referee replays all
70 parent inequalities for the exact minus, wall, and plus rays and lifts:

| Side | Lowest form | Exact factor value at `t=1/100` | Parent zero profile |
| --- | ---: | ---: | --- |
| minus | `-29/220` | `-40141/30250000` | `1237` only |
| wall | `0` | `0` | `1237` only |
| plus | `1/35` | `8/30625` | `1237` only |

The wall lift enforces `e=d*i` exactly. All three lifts stay in the same weak
recursive facet, so higher terms do not erase the displayed two-sided wall.
This is not a strict open-parent crossing: `1237` stays zero. It is not a
collar, mincut, global separator, or diagonal-nine result.

## Certificate-engineering gap and referee adapter

Certificate V1 correctly remains endpoint-neutral because the isolated
certificate track had no materialized producer payload. Its incomplete
sample-only template is rejected, and the referee does not relabel it as an
accepted mathematical certificate.

`REFEREE_ADAPTER.json` closes only the two materialized frozen-head witness
methods above: opposite exact parent initial forms with positive Gordan
weights, and an exact same-recursive-stratum residual wall. The referee
independently reconstructs their source preimages and exact arithmetic.
Digest-only geometry and every other producer method remain outside the
adapter.

## Hostile gates and nonconsequences

The closing verifier rejects 16 mutations covering source/tree drift,
literal and occurrence omission, parent omission, orientation and wall
digests, digest-only geometry, sampled evidence, false no-arc/radius/strict
crossing/collar/D9/`3/9` claims, unauthorized paths, and the wrong authority
epoch.

The accepted statement is only:

> finite-exact local normal-link route no-go; ordinary radial model singular;
> recursive weighted walls, strict open-parent crossing, and global coverage
> remain open; tangential four-support reduction retired as stated; ledger
> stays 2/9.

## Exact replay

```bash
PYTHONDONTWRITEBYTECODE=1 python \
  ops/team/diag9-s1237-normal-link-referee/verify_closing_referee.py
```
