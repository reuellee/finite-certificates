# Local matching stars do not force a root-free shear

## Scope

The matching-star dichotomy in
[`SECOND_DIAGONAL_DEFECT_TWO.md`](SECOND_DIAGONAL_DEFECT_TWO.md) is a statement
about the **global minimum** partner defect.  It is not enough to find one
degree-three label whose three incident triples form a matching star and then
apply a partner shear at that label.

This note gives an exact realizable warning.  A proper incomparable extension
pair has a positive pencil-rigid `5+5` circuit pair with a matching star at
label `3`, but every one of the twelve oriented partner rays loses one of the
chosen strict five-circuit witnesses before reaching a parent wall.  The
union's global defect is one, at other labels, so this does **not** obstruct
the genuine defect-two residue.  It also does not disprove 9DVL: at one exact
first cofactor root a support change reaches a pencil-flexible face and exits.

The exact verifier is

```console
python ai/omreal/verify_matching_star_partner_no_go.py
```

## Parent, signatures, and supports

Use the parent realization

\[
Y=\begin{pmatrix}
3&-8&0&3&14&-5&13&-5\\
-8&-13&11&12&15&0&14&8\\
-10&-14&-2&14&9&-3&1&-10\\
-14&3&12&15&14&12&-8&11
\end{pmatrix}.
\]

The two realizable extension signatures are

```text
rho = 14182253433415844
eta = 4401715025916122
```

They have strict positive, support-minimal circuits

\[
\begin{aligned}
 Q&=237/258/678/345/148,\\
 R&=167/278/125/136/457.
\end{aligned}
\]

Their derived-wall types are respectively

\[
 (47,51,49,47,49),\qquad(50,32,39,46,32),
\]

so both pass the residual-cofactor filter.  Their union is pencil-rigid and
has degree vector

\[
                         (4,4,3,3,4,3,5,4).
\]

At label `3` its incident triples are

\[
                         237,\qquad345,\qquad136,
\]

whose six partners are distinct.  Thus label `3` is a matching star.  The
global partner defect is nevertheless one: labels `4` and `6` have repeated
partners.  This is precisely why the global `d=1` versus `d=2` split must be
made before selecting a star label.

## Properness and incomparability

The verifier checks two exact integer child realizations.  On a parent chart
realizing `rho`, signature `eta` has the positive circuit

```text
126/136/256/457/278.
```

On a parent chart realizing `eta`, signature `rho` has the positive circuit

```text
345/137/148/348/258.
```

Exact signs of all 126 child brackets and all alternating circuit cofactors
prove realizability, properness, and both failures of inclusion.  The child
matrices are constants in the verifier, so this claim does not depend on a
floating-point realization search.

## All partner rays meet a cofactor wall first

For every partner

\[
                         f\in\{1,2,4,5,6,7\},
\]

consider the genuine parent shear

\[
                         y_3(t)=y_3+t y_f.
\]

Only one parent column moves, so every parent bracket is affine in `t` and
every circuit cofactor has degree at most two.  The table gives rational
parameters which are still strictly inside the parent residence.  At each
parameter the named cofactor of `Q` has changed from positive to strictly
negative.  The intermediate value theorem therefore puts a cofactor zero
strictly before the corresponding parent wall on every ray.

| partner `f` | negative ray | lost cofactor | positive ray | lost cofactor |
|---:|---:|:---:|---:|:---:|
| 1 | `-1/10` | `678` | `1/10` | `258` |
| 2 | `-1/50` | `258` | `1/50` | `678` |
| 4 | `-1/10` | `258` | `1/10` | `678` |
| 5 | `-1/20` | `258` | `1/20` | `678` |
| 6 | `-1/20` | `258` | `1/25` | `678` |
| 7 | `-1/50` | `678` | `1/50` | `258` |

All sign comparisons and polynomial degree bounds are checked over
`Fraction`; the table is not a numerical root approximation.

Consequently a proof that freezes these two strict supports and promises a
root-free exit along one of the six partner lines is false, even with actual
extension realizability and proper incomparability.

## The exact support-change exit

The obstruction is local to the frozen witnesses.  Along the positive
`f=2` shear, the `678` cofactor is affine and its first zero is

\[
                  t_*={124918901021\over12278662519200}.
\]

At `t_*` all parent brackets retain their signs, the other four `Q`
cofactors are positive, and all five `R` cofactors are positive.  Hence the
point lies in

\[
                 C_{\rho,Q\setminus\{678\}}\cap C_{\eta,R}.
\]

After deleting `678`, label `6` has union degree two.  The
projective-plane-pencil lemma supplies a path from that boundary point to the
parent residence boundary while preserving both smaller witnesses.  Joining
the shear segment to that pencil path proves that the displayed point is in a
noncompact component of the original closed pair intersection.

This exact pivot is the model a universal argument must retain: a cofactor
root can be useful rather than fatal, but only after its lower-support face
has been checked.  The hard open case is still the global defect-two residue,
where the first support-drop face can remain pencil-rigid.
