# Diagonal 3: coefficient-only algebraic-`u`-section `v` lift

## Result

The exact `v` lift now includes all **3,388** residual algebraic `u`
sections over open `t` sectors whose only non-regular event is a simple
leading-coefficient zero of a linear wall.  They contribute

```text
38,214 interior v-root points
41,602 open v strips
79,816 lifted cells
```

The prior endpoint checkpoint left 7,970 sections.  This degree-drop
certificate reduces the fail-closed frontier to **4,582** sections, all of
which combine coefficient and endpoint events.  The honest 9DVL score stays
**2/9**.

## Bounded degree-drop theorem used here

Write the affected linear wall as

```text
a(t,u) v + b(t,u).
```

On the target algebraic `u` section, the first projection certifies a
multiplicity-one factor of `a`.  Exact coefficient factorization separately
shows that `b` does not vanish on the open section.  Therefore the unique root
`-b/a` passes through infinity when the section is crossed; it neither enters
nor leaves the bounded interval `0 < v < 1`.  This is also replayed from the
adjacent root-token stacks: the wall token is absent on both sides and the two
bounded token sets are identical.

For the common bounded tokens, every order inversion is owned by an exact raw
pair resultant and every connected inversion component is a clique.  A clique
of size `k` represents one interior `k`-fold collision and reduces the section
root count by `k-1`.  An unused resultant is accepted only when at least one
owner is absent from the bounded stack.  Thus no bounded collision is inferred
from numerical sampling or from a root count alone.

## Exact census

| base factor | degree-dropping wall | nonzero constant factorization | sections |
|---:|---:|---|---:|
| 27 | 13 | factor 32 | 1,694 |
| 38 | 15 | unit after boundary reduction | 1,694 |
| **total** |  |  | **3,388** |

The certificate reconstructs 3,388 simple leading-coefficient events, 11,858
raw resultants, 10,704 visible inversion edges, and 10,704 interior collision
groups.  The remaining frontier is:

| reason | sections |
|---|---:|
| coefficient plus endpoint, equal adjacent count | 1,694 |
| coefficient plus endpoint and count change | 2,888 |
| **total** | **4,582** |

## Certificate and replay

The complete incremental partition is stored in 32 deterministic gzip shards.
The verifier reconstructs the wall coefficients, the 136-to-114 projection
factor ownership, endpoint factors, adjacent ordered root-token stacks,
inversion cliques, cell counts, shard bytes, and semantic hashes without
importing this producer.  It rejects 19 hostile claim and structural
mutations.

```console
python ai/omreal/build_diag3_pair_global_four_support_coefficient_only_u_section_v_lift.py
python ai/omreal/verify_diag3_pair_global_four_support_coefficient_only_u_section_v_lift.py
```

## Scope

This proves only the coefficient-only open-`t`, algebraic-`u` fibers in the
first two covered four-support domains.  It does not prove the remaining
coefficient-endpoint fibers, any algebraic-`t` `v` lift, global gluing,
extension-signature labels, the relative middle rank, or diagonal three.
