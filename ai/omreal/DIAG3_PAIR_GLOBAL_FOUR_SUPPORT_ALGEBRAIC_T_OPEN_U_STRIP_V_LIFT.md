# Diagonal 3: algebraic-`t`, open-`u`-strip `v` lift

## Result

All **131,632 open `u` strips** over the 1,693 algebraic `t` sections now have
an exact `v` lift.  They contribute

```text
2,143,770 interior v-root points
2,275,402 open v strips
4,419,172 lifted cells
```

This completes 131,632 of the 261,571 base cells over algebraic `t` sections.
The remaining 129,939 base cells are the algebraic `u` points on those
sections.  Global gluing, labels, closure, the relative middle-rank replay, and
both diagonal-three invariant obligations remain open, so the honest 9DVL
score remains **2/9**.

## Transport certificate

The producer reconstructs the ordered `u`-point groups in every algebraic `t`
section from the five completed base-lift certificates.  For the 28 final
sections it includes the virtual `u=0` and `u=1` owner groups, then requires a
unique monotone alignment to both adjacent open-`t` sector stacks.  All 28
alignments are unique; the other 1,665 sections use their already-certified
collision transport.

Each section strip compares its two incident, independently certified open-cell
`v` signatures:

| exact mechanism | strips |
|---|---:|
| unchanged signature transport | 131,549 |
| walls 1 and 6 collide in the interior | 48 |
| wall 6 exits through `v=1` | 35 |
| **total** | **131,632** |

The certificate emits a 2,125-entry algebraic-section signature catalog.  A
normal root is a singleton token group; the walls 1/6 collision is one
two-token root group.  Thirty-two deterministic gzip shards store the exact
left/right strip alignments and algebraic-section signature identifier for
every base strip.

## The 48-strip interior collision

The only inversion occurs in algebraic `t` section 960, whose exact parameter
satisfies

\[
t^2-3t+1=0, \qquad 0<t<1.
\]

The two linear fiber walls are

\[
F_1=-v+t, \qquad F_6=(1-t)^2v-t^2.
\]

Their linear-in-`v` resultant is

\[
-t(1-3t+t^2),
\]

and the independently reconstructed raw-event map assigns base factor 9 only
to the multiplicity-one resultant of walls 1 and 6.  Thus both walls have the
same simple root `v=t`, strictly inside `(0,1)`, on all 48 open `u` strips.
The adjacent signatures have the same token multiset and exactly this one
inversion.

## The 35-strip endpoint exit

Section 1193 is exactly `t=1/2`.  Wall 6 has root

\[
v=\left(\frac{t}{1-t}\right)^2,
\]

and its upper-endpoint evaluation is `F_6(t,u,1)=1-2t`.  The root is in
`(0,1)` on the left, equals the excluded boundary `v=1` on the section, and is
greater than 1 on the right.  Therefore token `(6,0)` is absent from all 35
section signatures.  Every other token retains its certified order.

## Independent replay

The verifier does not import the producer.  It uses a top-down exhaustive
alignment algorithm (rather than the producer's bottom-up dynamic program),
reconstructs the raw event map through the earlier independent verifier,
checks both polynomial identities directly, reproduces all shard bytes and
semantic digests, and rejects 24 hostile claim and structural mutations.

```console
python ai/omreal/build_diag3_pair_global_four_support_algebraic_t_open_u_strip_v_lift.py
python ai/omreal/verify_diag3_pair_global_four_support_algebraic_t_open_u_strip_v_lift.py
```

## Next target

Lift the remaining **129,939 algebraic-`t`, algebraic-`u` point fibers**.  Only
after those fibers are exact can the open and section lifts be glued into a
global regular complex and checked for strict closure, `d^2=0`, the infinity
subcomplex, label closure, and relative middle rank.
