# Diagonal two: an exact undominated birth and the birth-budget reduction

## Result

The first exact attack on the transition class left open by
`DIAG2_EXTREMAL_SEPARATOR_BIFURCATIONS.md` finds a genuine undominated
separator birth outside the four-singleton regime, but certifies that it is
still safe for the tracked extremal pair.

On the standard `e`-coordinate line through catalog parent `187`, isolated
type-`49` residual factor `23604` has a simple exact root.  Reversing the
crossing:

* births singleton row `1` (triple `124`) at sources `1`, `2`, and `4`;
* retains the size-two separator `{30,33}` at sources `6` and `7`;
* shrinks one endpoint escape mask from `67` to `61` directions; and
* shrinks its common overlap with the fixed partner from `15` to `9`.

Thus this is not a safe-loss transition in the birth direction, and its
destination is not covered by the four-singleton obstruction.  It is the
first proof-pinned representative of the sharper open transition class.
Exactly nine common elementary shears nevertheless survive.

This exact edge does not prove diagonal two.  It refutes the tempting
shortcut that every undominated birth must land in the four-singleton regime
and replaces the broad target with a smaller one: **budget-tight mixed
births** capable of deleting every previously common direction.

## 1. Birth-budget lemma

Let an edge keep two signatures `rho,eta` bad.  Suppose only the `rho` escape
mask shrinks in the chosen direction, and write

```text
E'(rho) subset E(rho),       L = E(rho) minus E'(rho),
E'(eta) = E(eta).
```

Then

```text
E'(rho) intersect E'(eta)
  = (E(rho) intersect E(eta)) minus L,
```

so

```text
|E'(rho) intersect E'(eta)|
  >= |E(rho) intersect E(eta)| - |L|.                 (1)
```

More generally, if both masks lose direction sets `L_rho,L_eta`, the lower
bound subtracts `|L_rho|+|L_eta|`.  A separator birth can therefore create a
disjoint pair only if its loss budget is at least the old overlap.  When the
only changes are births, each loss set is contained in the union of the new
separators' nonescape covers, giving a directly computable separator-cover
budget.

Equation (1) is elementary, but it is the correct falsification filter.  The
undominated/dominated distinction alone does not measure whether a birth can
close the remaining common-shear gap.

## 2. Exact isolated type-49 crossing

Normalize the checked-in integer realization of parent `187` to

```text
[1 0 0 0 1 1 1 1]
[0 1 0 0 1 a d g]
[0 0 1 0 1 b e h]
[0 0 0 1 1 c f i].
```

Vary coordinate `e`.  Global residual factor `23604` belongs to incidence
type `49` and has labeled occurrence rows

```text
134, 357, 167, 568.
```

Its monic affine restriction has exact root

```text
-1089491496778107199382036370734683661740772
------------------------------------------------
 27814073111268337001739262415917341966019625.
```

At the root this is the unique zero among all `26,740` primitive global
residual factors.  Exact perturbations by `10^-12` preserve all seventy
parent-bracket signs and every unselected residual-factor sign.  Both
endpoints have exactly `26,112` complete derived topes, and the crossing
exchanges exactly two topes in each direction.

The three overlap-six atlas pairs map to the same pinned normalized
signatures used by the preceding type-50 verifier:

```text
(41791434804464172, 69849397930972629)
(41224216731022549, 41224087949575724)
(68230936274949461, 70482716760692055).
```

The first two pairs remain simultaneously bad.  In the third pair the first
signature is a complete tope on both sides, so that pair is outside the
bad-pair transition question on this edge.

## 3. The mixed undominated birth

For affected signature `41791434804464172`, the pre-birth separator families
at sources `1`, `2`, and `4` are

```text
source 1: {1,2}, {1,30}
source 2: empty
source 4: {1,2}.
```

After crossing they are all replaced by singleton `{1}`.  No old separator
is contained in that new singleton, so the separator-dominance hypothesis
fails.  Simultaneously, the destination retains

```text
source 6: {30,33}
source 7: {30,33}.
```

It is therefore a mixed singleton/non-singleton profile, not a
four-singleton endpoint.

The singleton birth deletes exactly six escape directions:

```text
(2,3,-), (2,5,-), (2,6,-), (2,7,-), (2,8,-), (4,3,+).
```

All six were common with the unchanged partner.  The fifteen-direction
pre-birth overlap consequently falls to the following nine survivors:

```text
(1,2,-), (1,4,-), (1,4,+), (1,5,-), (3,7,+),
(4,1,-), (6,8,-), (7,3,-), (8,6,+).
```

This saturates (1): `15 - 6 = 9`.  The edge is dangerous in the precise
sense that the birth spends only common directions, but its loss budget is
still too small by nine.

## 4. Reproduction and scope

Replay the exact certificate with

```console
python ai/omreal/verify_diag2_extremal_undominated_birth_edge.py
```

The pinned semantic digest is

```text
a121da97360beede1c54d956877b12fe52a374d686bc6a496923704ec41172e6.
```

The verifier independently checks the parent normalization, factor orbit and
occurrence, unique wall zero, isolated perturbation, complete endpoint tope
tables, `2/2` exchange, all six tracked signatures, full minimal-separator
profiles, escape-mask reconstruction, the exact six lost directions, and the
nine survivors.

This is one labeled type-`49` edge in one parent realization cell.  It is not
coverage of all type-`49` walls or all undominated births.  The next finite
target is now narrower: isolate births for which the total new separator
cover budget meets or exceeds the incoming common overlap, especially when
both destination profiles remain mixed.  The honest 9DVL score remains
`1/9`.
