# Diagonal 3: final open-`t` algebraic-`u`-section `v` lift

## Result

The last **4,582** open-`t`, algebraic-`u` section fibers are now exact.  They
contribute

```text
51,794 interior v-root points
56,376 open v strips
108,170 lifted cells
```

Together with the regular, endpoint-only, and coefficient-only checkpoints,
this completes all **132,134** algebraic-`u` sections over open `t` sectors:

| checkpoint | sections | lifted cells |
|---|---:|---:|
| regular raw-resultant fibers | 120,174 | 3,739,392 |
| endpoint-only fibers | 3,990 | 120,468 |
| coefficient-only fibers | 3,388 | 79,816 |
| coefficient-plus-endpoint fibers | 4,582 | 108,170 |
| **total** | **132,134** | **4,047,846** |

The cumulative section fibers contain 1,957,856 interior `v`-root points and
2,089,990 open `v` strips.  Algebraic-`t` fibers and global topology remain
open, so the honest 9DVL score remains **2/9**.

## Three exact mechanisms

The final three base factors require three mechanisms that the certificate
keeps distinct.

1. **Endpoint constant zero.**  A linear wall's constant coefficient has the
   target base factor, its leading coefficient is nonzero on the section, and
   its one root is exactly the certified `v=0` endpoint token.
2. **Unbounded leading-coefficient zero.**  A linear wall loses its leading
   coefficient while its constant remains nonzero.  Its root passes through
   infinity and is absent from both adjacent bounded stacks.
3. **Fiber-wide zero wall.**  A degree-zero wall vanishes on the complete
   `v`-fiber.  It contributes a wall label to every resulting `v` cell but no
   isolated root token or additional cut.

Every other one-sided token is owned by a multiplicity-one exact endpoint
factor.  The symmetric difference of the adjacent bounded token sets is
exactly the set of those endpoint tokens.  Interior collisions are then
computed only on common tokens, with every visible inversion owned by a raw
resultant and every collision component required to be a clique.  An unused
resultant is permitted only if it does not have two common bounded owners.

## Factor census

| base factor | sections | coefficient behavior | simple endpoint behavior |
|---:|---:|---|---|
| 35 | 1,694 | wall 0 constant zero | walls 0 and 15 enter |
| 56 | 1,694 | wall 12 root unbounded | wall 13 enters; wall 16 exits |
| 72 | 1,194 | wall 14 constant zero; wall 17 fiber-wide zero; wall 21 root unbounded | walls 14, 18, and 19 enter |
| **total** | **4,582** | **6,970 coefficient events** | **10,358 endpoint attachments** |

Factor 72 also has two endpoint evaluations of the degree-zero wall 17; they
are audited as boundary evidence for the fiber-wide zero and are not counted
as isolated endpoint attachments.

Across the final fibers the certificate reconstructs 21,910 raw resultants,
14,896 visible inversion edges, and 10,586 interior collision groups.

## Certificate and replay

The incremental partition is stored in 32 deterministic gzip shards.  The
verifier independently reconstructs coefficient and endpoint ownership from
the earlier projection artifacts, checks the bounded-token theorem, replays
every shard byte and semantic digest, and rejects 23 hostile claim and
structural mutations.  It does not import the final producer.

```console
python ai/omreal/build_diag3_pair_global_four_support_coefficient_endpoint_u_section_v_lift.py
python ai/omreal/verify_diag3_pair_global_four_support_coefficient_endpoint_u_section_v_lift.py
```

## Scope and next target

This closes the `v` lift only for algebraic `u` sections over open `t` sectors
in the two covered square-pyramid supports.  It does not yet lift the 261,571
base cells over algebraic `t` sections, glue the open and section fibers into a
global regular complex, attach extension-signature labels, replay the relative
middle rank, or prove diagonal three.

The next exact target is the algebraic-`t` `v` lift.  Once that is complete,
the open and algebraic fibers can be glued and subjected to closure,
`d^2=0`, infinity-subcomplex, label-closure, and middle-rank checks.
