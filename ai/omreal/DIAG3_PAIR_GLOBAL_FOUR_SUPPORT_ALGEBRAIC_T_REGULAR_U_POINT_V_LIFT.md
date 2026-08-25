# Diagonal 3: regular algebraic-`t`, algebraic-`u` point `v` lift

## Result

The pure-resultant tranche now lifts **118,001** of the 129,939
algebraic-`u` point fibers over algebraic `t` sections.  It contributes

```text
1,773,150 interior v-root points
1,891,151 open v strips
3,664,301 lifted cells
```

Exactly **11,938** coefficient/endpoint point fibers remain.  Global gluing,
labels, closure,
middle-rank replay, and both diagonal-three invariant obligations remain open,
so the honest 9DVL score remains **2/9**.

## Exact regular mechanism

For each algebraic-`u` point, the certificate takes the two incident
algebraic-`t` open-`u`-strip signatures and the complete set of base factors
owning that point.  A point enters this tranche only when:

1. the two bounded token multisets agree;
2. every owning raw event is a resultant, with no coefficient or endpoint
   event;
3. every visible inversion is owned by one of those resultants;
4. every resultant whose two walls remain bounded is included in the algebraic
   collision graph, even when tangency preserves adjacent order; and
5. every connected algebraic collision component is a clique, hence one exact collision
   group.

This supports simultaneous point ownership: 1,455 completed points have two or
more distinct base-factor owners, including one point with ten owners.  Across
the completed tranche the replay reconstructs 182,648 raw resultant events,
169,056 visible inversion edges, 169,113 total algebraic collision edges, and
148,041 collision groups.

Section 960 retains the already-certified persistent collision of walls 1 and
6 at `v=t` on every point fiber.  That collision is added to both the permitted
event set and the collision graph before the new `u`-point events are grouped.

## Exact frontier

| remaining mechanism | point fibers |
|---|---:|
| coefficient only | 3,380 |
| endpoint with count change | 3,976 |
| endpoint with equal count | 2 |
| coefficient plus endpoint with count change | 2,888 |
| coefficient plus endpoint with equal count | 1,692 |
| **total** | **11,938** |

Nine additional pure-resultant points require exact tangential resultant
edges.  Their raw resultant factors vanish and both wall tokens remain
bounded, but 14 wall pairs preserve adjacent order.  Eight edges complete
already connected multi-collision components into cliques; six are standalone
tangential `K2` collisions.  The completed points occur at the exact
`(section, point)` indices

```text
(175,34), (181,15), (279,47), (287,75), (350,15),
(350,66), (412,48), (412,61), (702,46)
```

They are recorded with their complete point-owner sets, missing wall-pair
resultants, and uniquely resolved bounded token occurrences.  They remain
distinctly labelled as connected clique completions or isolated tangential
`K2` collisions; no tangency is
misreported as a visible transverse inversion.  Every missing pair contains a
degree-one wall, so its resultant-zero shared root is fixed by that wall's
unique bounded token; the one nonlinear participant is wall 8 of degree two.

## Certificate and replay

Thirty-two deterministic gzip shards store every completed point signature and
every residual point.  A separate deterministic gzip artifact contains the
4,721-entry point-signature catalog.

The verifier does not import the producer.  It reconstructs base-point groups
through the previous independent section verifier, rebuilds the raw event and
endpoint-owner maps through earlier independent verifiers, reproduces every
shard and catalog byte, and rejects 28 hostile claim and structural mutations.

```console
python ai/omreal/build_diag3_pair_global_four_support_algebraic_t_regular_u_point_v_lift.py
python ai/omreal/verify_diag3_pair_global_four_support_algebraic_t_regular_u_point_v_lift.py
```

## Next target

Replay the existing coefficient and endpoint mechanisms on the remaining
11,938 point fibers.  The resulting algebraic-`t`
point signatures will complete the fiber inventory required for global
gluing.
