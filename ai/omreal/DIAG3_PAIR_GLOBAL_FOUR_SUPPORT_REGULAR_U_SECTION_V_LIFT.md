# Diagonal 3: regular algebraic-`u`-section `v` lift

## Result

The `v` lift is exact for **120,174 of the 132,134 algebraic `u` sections**
over the 1,694 open `t` sectors in the first two covered four-support domains.
These completed fibers contain

```text
1,809,609 interior v-root points
1,929,783 open v strips
3,739,392 regular lifted cells
```

This is a proof-bearing partial lift, not diagonal-three closure.  The exact
fail-closed residue is 11,960 coefficient or endpoint/count-change fibers.
All `v` lifts above algebraic `t` sections, global gluing, extension-signature
labels, relative middle-rank replay, and the triple obligation remain open.
The honest 9DVL score stays **2/9**.

## Why the regular fibers are determined by neighboring stacks

Inside an open `t` sector, the second projection guarantees that every stored
`u` section is a simple root of exactly one base factor.  The certified open
base cells on its two sides already carry the complete ordered list of
interior roots of the 22 original walls in the `v` fiber.

For a section accepted by this checkpoint:

1. every raw event above its base factor is a multiplicity-one pair
   resultant;
2. no wall coefficient, quadratic discriminant, or `v=0,1` endpoint factor
   vanishes there; and
3. the adjacent interior-root lists have equal size.

Consequently every real bounded root branch continues across the section and
the only possible changes are transverse pair collisions.  The adjacent-order
inversion graph identifies the visible collisions.  On every accepted
section its connected components are complete graphs and every inversion has
its exact raw resultant owner.  A component of size `k` is one `k`-fold
collision point, so it reduces the section root count by `k-1`.  Raw simple
resultants with no adjacent inversion lie outside the bounded `v` interval
and do not change the section fiber.

This argument uses no generic-position assumption: multiplicity, coefficient,
discriminant, boundary, count-change, non-clique, and ownership failures are
explicit rejection conditions.

## Exact census

The 120,174 completed sections contain 183,374 raw resultant events,
169,750 visible adjacent-order inversions, and 148,896 interior collision
groups.  Their event/inversion/group census is:

| raw events | inversions | collision groups | sections |
|---:|---:|---:|---:|
| 1 | 0 | 0 | 6,743 |
| 1 | 1 | 1 | 84,855 |
| 2 | 1 | 1 | 1,527 |
| 2 | 2 | 2 | 13,234 |
| 3 | 3 | 1 | 1,903 |
| 3 | 3 | 3 | 2,655 |
| 4 | 2 | 2 | 500 |
| 4 | 3 | 3 | 1,001 |
| 4 | 4 | 2 | 3,481 |
| 4 | 4 | 4 | 1,387 |
| 8 | 4 | 2 | 733 |
| 8 | 7 | 3 | 421 |
| 8 | 8 | 4 | 1,734 |

All 132,134 sections are accounted for exactly.  The unresolved frontier is:

| reason | sections |
|---|---:|
| endpoint event and adjacent root-count change | 3,990 |
| coefficient event only | 3,388 |
| coefficient plus endpoint event and root-count change | 2,888 |
| coefficient plus endpoint event, with equal adjacent counts | 1,694 |
| **total** | **11,960** |

No section has an unowned visible inversion, a non-clique collision component,
a missing raw event, or a raw-event multiplicity above one.

## Certificate and replay

The producer reconstructs all 255 raw first-projection obligations with exact
rational polynomial arithmetic, maps them through the independently certified
136-to-114 factorization, and joins them to the 44 exact endpoint
factorizations and the two neighboring open-cell stack signatures.  Accepted
fibers must preserve the exact bounded branch-token set, and every surplus
simple resultant must have at least one owner absent from that set.  The
120,174 completed rows and 11,960 residual rows are stored in 32 deterministic
gzip shards.

The separate standard-library verifier independently reconstructs the event
map and section partition, replays the endpoint factorizations, regenerates
every shard byte-for-byte, checks all cell counts and digests, and rejects
20 hostile claim, provenance, shard, or collision mutations.

```console
python ai/omreal/build_diag3_pair_global_four_support_regular_u_section_v_lift.py
python ai/omreal/verify_diag3_pair_global_four_support_regular_u_section_v_lift.py
```

Semantic SHA-256:
`4caa3b63cfa4dd6e88b88076e0b4d6cd299822c7ff8680a73c6113f6ff3ff0ac`.

## Next exact target

Resolve the 11,960 residual fibers in four fail-closed classes.  Endpoint
count changes can be attached first from the exact `v=0,1` ownership data;
coefficient fibers then require bounded degree-drop analysis.  Only after
those are complete should the lift move to the 261,571 base cells above the
1,693 algebraic `t` sections.
