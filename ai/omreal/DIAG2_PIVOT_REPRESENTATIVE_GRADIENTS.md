# Exact size-two representative-gradient classification

## Result

In the standard nine-variable normalization, collapse residual types 46 and
47 to their common polynomial.  For every one of the remaining

\[
                         \binom{12}{2}=66
\]

pairs, an exact `2 by 2` Jacobian minor is a signed product of parent
brackets.  It is therefore nonzero throughout every uniform parent cell.
Consequently the gradients of two **distinct representative residual
polynomials** are linearly independent on the uniform locus.

There is also a topological consequence.  On the common zero set, projection
to the seven coordinates complementary to the displayed minor is a local
diffeomorphism.  The image of any connected component is a nonempty open
subset of `R^7`; it cannot be compact.  Hence every common-zero component of
two distinct canonical representative walls is noncompact.  This still does
not classify relative labeled overlaps.  See
`RESIDUAL_STRATUM_NONCOMPACTNESS.md`.

Thus the representative size-two Farkas classification is complete:

* distinct representative types always have a nonempty common strict cone;
* types 46 and 47 define the same residual wall; and
* opposite orientations of that common wall give the unique representative
  two-term positive dependence `g+(-g)=0`.

The latter case is the exact proper incomparable pair in
`DIAG2_PIVOT_CONE_FARKAS.md`, and its shared lower-support circuit has a
tangent omitted-label escape.

This theorem is deliberately scoped.  A second labeled wall occurrence is
obtained by a relative `S_8` relabeling, not merely by choosing another one of
the thirteen canonical representatives.  The current certificate table does
not by itself classify all such relative labeled overlaps.  That finite gap
is now treated in `DIAG2_PIVOT_LABELED_PAIR_THEOREM.md`: 9,354 of the exact
9,476 factor-pair orbits are certified noncompact, with 122 left as residue.

## Exact certificates

Let `q_r` denote the residual polynomial of type `r`.  For each pair `(r,s)`
the verifier stores coordinate indices `u,v`, a sign `epsilon`, and parent
brackets `B_1,...,B_m` such that

\[
 \partial_u q_r\,\partial_v q_s
 -\partial_v q_r\,\partial_u q_s
 =\epsilon B_1\cdots B_m.                                        \tag{1}
\]

The factors have length at most four.  Examples include

\[
 J^{a,b}_{36,46}=-[1237]^2,
 \qquad
 J^{a,d}_{37,46}=[1267],
 \qquad
 J^{a,d}_{48,49}=[2357].                                         \tag{2}
\]

All 66 identities are expanded over the integer polynomial ring by the
dependency-free verifier; none is inferred from floating-point samples or
symbolic factorization at run time.

Run

```console
python ai/omreal/DIAG2_PIVOT_REPRESENTATIVE_GRADIENT_VERIFY.py
```

## Size-three boundary (updated)

For three distinct representative gradients, a positive Farkas dependence
requires their `3 by 9` Jacobian to have rank at most two.  A direct exact
minor scan proves rank three for many of the 220 triples by finding a
`3 by 3` minor which is again a parent-bracket product.  It does not settle
every triple: several triples have no certificate of this particularly simple
form, and exact saturation of their full Jacobian-minor ideals is materially
more expensive.

The formerly first unresolved representative triple `(36,38,42)` now has an
exact two-step saturation certificate proving rank three throughout the
uniform locus.  However, the universal size-three claim is false: four other
canonical triples have exact uniform rational rank-two witnesses.  The
current proof-safe census is 171 rank-three triples, 4 rank-drop triples, and
45 open triples.  See `DIAG2_PIVOT_REPRESENTATIVE_TRIPLES.md` and its
dependency-free verifier.

The remaining finite tasks are therefore:

1. saturate each of the 45 still-open representative triple ideals by the
   product of parent brackets;
2. saturate the exact 122-orbit relative-label pair residue and enumerate
   relative labeled triple overlaps up to simultaneous `S_8`; and
3. for every surviving positive dependence, recover the signed circuit data
   and test for a common lower-support tangent escape.

## Why the proposed lexicographic termination measure is not yet a proof

The pair

\[
                 (\text{support size},\text{parent-boundary depth})
\]

is useful bookkeeping but is not currently well-founded under the actual
wall moves.

At a support-drop wall, a strict five-circuit becomes a four- or
three-support circuit, but cofinal continuation on the other side pads it
back to size five.  The exact 52-padding wall star therefore contains
transitions `5 -> 4 -> 5`; support size is not monotone.

Nor is “parent-boundary depth” presently an independent invariant.  If it
means Euclidean or projective distance, it is coordinate-dependent and need
not decrease under a common cone direction.  If it means shortest-path
distance to a boundary vertex in the finite signed wall graph, proving that
every simultaneous-bad state has an allowed edge of smaller depth is exactly
the missing no-compact-component/connectivity theorem in different words.

A noncircular stratified termination theorem would need a specified finite
potential `Phi` with two checked properties:

1. every strict-cone transition lowers `Phi`; and
2. every minimal Farkas obstruction either lowers the support stratum and
   exits immediately by an omitted label, or has a tangent transition which
   lowers `Phi`.

The 46/47 obstruction satisfies the terminal omitted-label alternative, but
the representative-pair theorem does not supply `Phi` for all labeled wall
transitions.  Diagonal two therefore remains open.
