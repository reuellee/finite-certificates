# Diagonal three: primitive-direction double-graph lemma

## The structural extension

Let `D` be the open eight-dimensional graph domain after a first
parent-unit graph.  Suppose the second cleared equation has a second
parent-unit graph

\[
                       r_2=A(u)y+B(u),
\]

and let `d` be a primitive integral direction in the seven coordinates other
than `y`.  Assume, as exact polynomial identities on the first graph,

\[
             D_dA=0,\qquad D_dB=0,\qquad D_d^2r_3=0.       \tag{1}
\]

Complete `d` to a basis of `Z^7`.  The associated `GL_7(Z)` linear change has
determinant `+-1`, is a homeomorphism of the ambient real coordinate space,
and sends `d` to the derivative in one coordinate `t`.  Its pullback of `D`
is still open.  The first two identities in (1) say that graphing the second
equation does not change the `t` direction; after clearing its parent-unit
denominator, the third identity says that the final equation is affine in
`t`.  Thus the usual one-equation affine-fiber lemma over the complementary
six-dimensional open base excludes every compact connected component,
including the final-slope rank-drop locus.

For the sparse direction `d=e_i+epsilon e_j`, `epsilon` in `{+-1}`, an explicit
unimodular completion is

```text
x_i = t
x_j = s + epsilon*t
```

with the remaining coordinates fixed.  Its two-by-two determinant is one and
`partial/partial t=D_d`.

## Exact bounded witness screen

An exact positive screen in the canonical type-50/pivot-3 first chart used
all directions `e_i+-e_j`.  It found `21` rows with
`d=e_4+e_7` in zero-based graph coordinates.  For every row, an independent
integer replay checked:

* anchor alignment and complete stabilizer transport;
* both exact graph reconstruction identities;
* the second slope as a complete product of graph-restricted parent brackets;
* `D_dA=D_dB=0` before the second substitution;
* `D_d^2r_3=0` before, and after, the second graph restriction; and
* the explicit unimodular substitution above, after which the final cleared
  equation has degree at most one in `t`.

The ordered witness semantic digest is

```text
68116c422a26d570de424cc510d397f2637cc205dbc6e6d97ba618be6daffd72
```

This screen is a positive structural regression, not an exhaustive
primitive-direction search.  All `21` rows are also closed by the tracked
generic coordinate double-graph certificate, whose SHA-256 is

```text
8a61846547b6a8ab1984a7ebe8273fd7326316c8a83c040af377a6251b21937c
```

The no-argument verifier reads that repository artifact and proves all `21`
rows occur in it.  Thus this direction layer contributes **zero** additional
ledger rows after that coordinate family and must not be added to the global
closure count.
