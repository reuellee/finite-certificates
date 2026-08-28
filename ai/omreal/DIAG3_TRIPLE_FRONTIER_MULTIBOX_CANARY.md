# Diagonal three: deterministic multibox projection frontier

## Exact bounded outcome

At base revision
`ec362dba8a912bc4749c004641aee2da0a88dc05`, the accepted hard presentation

```text
(5563,16134,19284) -> canonical unresolved row (5563,4373,23221)
```

admits an exact projection-critical corridor strictly larger than the prior
single-box canary.  Let `V` be the common zero set of its three authenticated
residual factors.  The new rectangular corridor is the union of `20`
consecutive radius-`1/128` macroboxes in the negative-`a` direction.  Exact
one-bisection interval certificates refine those macroboxes into `35`
certificate boxes.  On every certificate box the same Jacobian minor

```text
det d(q5563,q16134,q19284) / d(d,e,h)
```

is strictly negative.  All `70` normalized parent brackets retain their base
sign on every macrobox.  Consequently the entire corridor lies in one
uniform parent cell, the triple-zero set is smooth there, and projection to
`(a,b,c,f,g,i)` is a local diffeomorphism.  The compact-open argument from the
accepted one-box canary therefore gives

\[
  \boxed{\text{every connected component of }V\text{ restricted to the
  corridor meets one of its 18 outer facets}.}
\]

The exact zero in the original box makes this theorem nonvacuous.

This is a finite exact multibox compiler result.  It is not a complete-row or
complete-orbit noncompactness theorem.

## Deterministic selection rule

The work order allowed either a smallest-family closure or a discriminating
multibox canary.  The accepted source contract explicitly records that the
canonical materialized `1,162,302`-row final-residue presentation stream is
unavailable.  The branch rule therefore selected the multibox canary.

Adjacent same-radius boxes were ordered by

```text
(coordinate 0, direction -1), (coordinate 0, direction +1),
(coordinate 1, direction -1), ...
```

The first box retaining all parent signs and the fixed projection-minor sign
is the negative-`a` neighbor.  Extension then proceeded by increasing macrobox
index.  At each macrobox the permitted projection certificates were tested in
the fixed order

```text
no split, bisect a, bisect b, ..., bisect i.
```

Only one bisection was allowed.  The selected subdivisions are:

| macrobox indices | first successful subdivision | certificate boxes |
|---|---|---:|
| `0..4` | none | `5` |
| `5..13` | bisect `a` | `18` |
| `14..18` | bisect `c` | `10` |
| `19` | bisect `g` | `2` |
| **total** |  | **`35`** |

Thus the result is not based on an adaptive choice of a favorable direction,
radius, or deeper subdivision.

## Exact accounting

The independent replay reconstructs:

- `20` accepted macroboxes and `35` projection certificate boxes;
- `1,400 = 20 x 70` strict parent-bracket intervals;
- `35/35` strictly negative projection-minor intervals;
- `18` geometric outer facets, `19` macrobox adjacency seams, and `15`
  intra-macro subdivision seams;
- parent interval-record SHA-256
  `99d41026fe2529f5cbeceeb00ddfd2b8725fb1d6bfa40efaaa2efe93143de2a5`;
- projection interval-record SHA-256
  `fb03065512c9bcd8e0b3ed380598f18cc43efadba518d0ed59c5bb7f4c82b4ac`;
- certificate semantic SHA-256
  `5a71b5a6144aa0ab858a5cda2fbca6ee485332954f92976f17f8ce599fd46447`.

The parent bracket closest to zero on the accepted corridor is `[3468]` on
macrobox `19`, with direct interval

```text
[-9/224,-1/112].
```

## First exact frontier

The stop rule fires on macrobox `20`.  Exactly `69/70` parent brackets retain
their strict sign.  The remaining factor is the two-term parent bracket

```text
[3468] = g-a.
```

Its exact vertex range on that macrobox is

```text
[-11/448,3/448].
```

The opposite signs give an exact parent-wall point on their connecting
segment:

```text
(-223/224,-105/32,-431/224,-1119/224,-895/224,
 -671/224,-223/224,449/224,897/224),
```

where `g-a=0`.  This is not merely direct-interval overestimation.  It is the
first genuine parent-cell frontier in the deterministic corridor.  The next
proof-producing object should replace macrobox `20` by a cell clipped at
`[3468]=0`, certify the fixed projection on that clipped cell, and attach its
terminal face to the parent-wall stratum.

## Trust boundary and canaries

The producer first replays the accepted one-box certificate and then emits the
new JSON object.  The frontier verifier does not import the producer.  It
reconstructs the source equations, all parent brackets, the projection minor,
the deterministic direction and subdivision choices, the exact corridor
partition, both interval-record digests, and the wall witness from pinned
inputs.  It also rejects `10/10` re-sealed hostile mutations covering counts,
direction, subdivision, interval data, digests, wall identity, wall witness,
scope, residue accounting, and theorem score.  A compact interior sphere is
retained as the negative projection-sign canary.

The calculation uses only authenticated repository inputs and exact rational
arithmetic.  No new external mathematical source is needed: the topological
implication is the same elementary local-diffeomorphism/compact-open lemma
already audited in `DIAG3_TRIPLE_LOCAL_ROADMAP_CANARY.md`.

## Replay

```bash
PYTHONDONTWRITEBYTECODE=1 \
  python ai/omreal/diag3_triple_frontier_build_multibox.py
PYTHONDONTWRITEBYTECODE=1 \
  python ai/omreal/diag3_triple_frontier_verify_multibox.py
```

The certificate is
`ops/team/triple-frontier/DIAG3_TRIPLE_FRONTIER_MULTIBOX_CANARY.json`.

## Honest theorem accounting

This corridor covers no complete factor triple, no complete `S_8` orbit, and
no full parent cell.  All `18` outer facets remain artificial scope boundary;
the exact `[3468]` wall point lies in the first rejected macrobox, not on the
accepted corridor boundary.  Therefore the unresolved source count remains
`1,162,302`, `diag3_triple_hc0` remains open, and the honest 9DVL score remains
`2/9`.
