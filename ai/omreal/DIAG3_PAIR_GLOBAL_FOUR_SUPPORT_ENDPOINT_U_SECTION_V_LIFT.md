# Diagonal 3: endpoint-only algebraic-`u`-section `v` lift

## Result

The exact `v` lift now includes all **3,990** residual algebraic `u`
sections over open `t` sectors whose only non-regular feature is a simple
root crossing `v=0` or `v=1`.  Together they contribute

```text
58,239 interior v-root points
62,229 open v strips
120,468 lifted cells
```

The earlier regular checkpoint completed 120,174 sections and left 11,960.
This endpoint attachment reduces that fail-closed frontier to **7,970**
sections, all of which carry a coefficient event.  Algebraic-`t` fibers,
global gluing, extension-signature labels, middle-rank replay, and the triple
obligation remain open.  The honest 9DVL score stays **2/9**.

## Endpoint attachment theorem used here

Fix one simple algebraic `u` section inside an open `t` sector.  The two
incident open-`u` strips already carry complete ordered root-token lists for
the 22 original walls in `0 < v < 1`.  Suppose:

1. every raw first-projection event on the section is a multiplicity-one pair
   resultant;
2. the exact `v=0,1` factorization has one multiplicity-one owner on a wall
   that is linear in `v`;
3. the symmetric difference of the two bounded root-token sets is precisely
   that endpoint owner's root token; and
4. the inversion graph on the common tokens is a disjoint union of cliques,
   with every inversion owned by a raw resultant.

Then the endpoint token reaches the certified boundary and is not an
interior root on the section.  Every common bounded branch continues to the
section.  A clique of size `k` is one interior `k`-fold collision and reduces
the section root count by `k-1`.  Any unused simple resultant must have an
owner absent from the common bounded stack, so it cannot hide another
interior collision.  Thus

```text
section interior roots
  = number of common tokens - sum over collision cliques (size - 1),
section open strips = section interior roots + 1.
```

This is an endpoint version of the neighboring-stack continuation argument
used by the regular checkpoint.  It does not infer an attachment from root
counts alone: the exact endpoint factorization, owner, multiplicity, fiber
degree, and one-token symmetric difference are all replayed.

## Exact census

Only three of the 114 base factors meet the theorem's hypotheses:

| base factor | endpoint wall | endpoint | direction across increasing `u` | sections |
|---:|---:|---:|---|---:|
| 12 | 3 | `v=1` | exit | 1,194 |
| 57 | 12 | `v=1` | entry | 1,694 |
| 86 | 21 | `v=1` | entry | 551 |
| 86 | 21 | `v=1` | exit | 551 |
| **total** |  |  |  | **3,990** |

Across these fibers the certificate reconstructs 10,184 raw simple
resultants, 9,951 visible inversions, and 7,747 interior collision groups.
Every endpoint symmetric difference is exactly one token.  No endpoint token
is included in an interior collision group, no visible inversion lacks an
owner, and no unused resultant has both owners in the common bounded stack.

The remaining exact frontier is:

| reason | sections |
|---|---:|
| coefficient event only | 3,388 |
| coefficient plus endpoint event, equal adjacent count | 1,694 |
| coefficient plus endpoint event and count change | 2,888 |
| **total** | **7,970** |

## Certificate and replay

The producer derives the raw coefficient/resultant/discriminant map from the
22 walls and the certified 136-to-114 factorization.  It independently joins
that map to all 44 endpoint factorizations and the two adjacent open-cell
root signatures.  The complete 132,134-section partition is stored in 32
deterministic gzip shards: 120,174 prior regular sections are omitted from
the incremental rows, 3,990 endpoint sections are completed, and all 7,970
coefficient-event sections remain explicit.

The separate standard-library verifier reconstructs the first projection,
endpoint ownership, section classification, branch-token differences,
collision groups, counts, shards, and semantic hashes without importing the
new producer.  It also rejects 19 hostile claim and structural mutations.

```console
python ai/omreal/build_diag3_pair_global_four_support_endpoint_u_section_v_lift.py
python ai/omreal/verify_diag3_pair_global_four_support_endpoint_u_section_v_lift.py
```

## Scope and next target

This proves only the endpoint-only count-change fibers in the first two
covered four-support domains.  It does not supply the remaining degree-drop
fibers, any algebraic-`t` `v` lift, a global closure complex, or a diagonal-
three invariant.

The next exact target is the 7,970-section coefficient-event residue.  It is
supported on only five base factors: 27 and 38 are coefficient-only; 56 has
an endpoint exchange with equal adjacent root count; and 35 and 72 combine
coefficient degeneration with endpoint count change.  Those fibers require
an exact bounded degree-drop analysis rather than endpoint attachment alone.
