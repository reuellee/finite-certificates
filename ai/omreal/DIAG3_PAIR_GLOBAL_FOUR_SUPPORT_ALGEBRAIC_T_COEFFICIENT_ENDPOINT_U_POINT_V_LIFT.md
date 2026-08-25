# Diagonal 3: final algebraic-`t`, algebraic-`u` point `v` lift

## Result

The coefficient/endpoint tranche lifts the final **11,938** algebraic-`u`
point fibers over algebraic `t` sections. It contributes

```text
147,604 interior v-root points
159,542 open v strips
307,146 lifted cells
```

Together with the prior open-`u`-strip and pure-resultant point tranches, all
**261,571** base cells over the 1,693 algebraic-`t` sections now have exact
local `v` lifts:

| base-cell tranche | base cells | lifted cells |
|---|---:|---:|
| open `u` strips | 131,632 | 4,419,172 |
| pure-resultant `u` points | 118,001 | 3,664,301 |
| coefficient/endpoint `u` points | 11,938 | 307,146 |
| **total** | **261,571** | **8,390,619** |

This is a complete **local fiber inventory**, not a global cell complex.
Global gluing, labels, closure, middle-rank replay, and both diagonal-three
invariant obligations remain open, so the honest 9DVL score remains **2/9**.

## Exact residual mechanisms

The completed point fibers retain the exact fail-closed census from the prior
checkpoint:

| mechanism | point fibers |
|---|---:|
| coefficient only | 3,380 |
| endpoint with count change | 3,976 |
| endpoint with equal count | 2 |
| coefficient plus endpoint with count change | 2,888 |
| coefficient plus endpoint with equal count | 1,692 |
| **total** | **11,938** |

For every point, the producer and independent verifier reconstruct all base
factor owners, raw coefficient and resultant events, endpoint owners, and the
two incident bounded-root signatures. They then require:

1. each leading-coefficient loss to remove its wall root to infinity;
2. each constant-coefficient loss to agree with an endpoint attachment;
3. every fiber-wide-zero wall to emit no root token;
4. all endpoint token changes to be owned by simple degree-one endpoint
   factors;
5. every visible inversion and every order-preserving algebraic collision to
   be owned by a raw resultant; and
6. every final collision component to be a contiguous clique on both adjacent
   signatures.

No point has simultaneous vanishing of both coefficients of a nominally
degree-one wall. Wall 17 is the only expected fiber-wide-zero mechanism, with
both endpoint incidences recorded on 1,193 factor-72 point fibers.

## Exact endpoint tangency

One endpoint factor is deliberately not reported as an entry or exit. At
`(section, point)=(550,30)`, the section is exactly `t=1/4` and the
multi-owner point is exactly `u=1/3`. For wall 21,

```text
wall21(t=1/4,u,v=1) = -factor86(t=1/4,u)
factor86(t=1/4,u)   = (1-3u)^2/16
```

The coefficient of `v` in wall 21 equals `1/16` at that point. Hence the
wall root is `v>=1` on both adjacent `u` strips and merely touches `v=1`
at `u=1/3`; no bounded token is created or destroyed. The certificate stores
the specialized integer coefficient vectors and the verifier recomputes this
identity directly from the original wall and projection-factor polynomials.

## Algebraic collision completion

The residual fibers contain 36,053 visible inversion edges, four persistent
section-960 wall-(1,6) edges, and ten additional order-preserving resultant
edges. The ten additions occur at five exact point fibers:

```text
(306,22), (412,21), (473,38), (550,30), (835,35)
```

Six edges complete already-connected collision components. The remaining four
edges form one isolated tangential `K2` and one isolated tangential `K3`;
the three `K3` edges are recorded as a single complete component, not as
three unrelated pair collisions. Every added edge has a degree-one wall and a
unique bounded token occurrence.

The final residual census is 36,067 algebraic collision edges and 29,203
collision groups. All four residual section-960 fibers retain the previously
proved wall-(1,6) collision.

## Certificate and replay

Thirty-two deterministic gzip shards store all 11,938 completed point fibers.
A separate deterministic gzip artifact stores the 418-entry point-signature
catalog.

The verifier does not import this producer. It independently rebuilds the raw
event, endpoint-owner, and coefficient-factor maps; recomputes the exact
endpoint tangency; reconstructs both adjacent point signatures; reproduces
every shard and catalog byte; and rejects 32 hostile claim and structural
mutations.

```console
python ai/omreal/build_diag3_pair_global_four_support_algebraic_t_coefficient_endpoint_u_point_v_lift.py
python ai/omreal/verify_diag3_pair_global_four_support_algebraic_t_coefficient_endpoint_u_point_v_lift.py
```

## Next target

Use the now-complete local `v`-lift atlas to construct global gluing,
extension-signature labels, strict closure data, and the relative middle-rank
replay. No theorem-score promotion is justified until those global obligations
and both diagonal-three invariant checks are independently certified.
