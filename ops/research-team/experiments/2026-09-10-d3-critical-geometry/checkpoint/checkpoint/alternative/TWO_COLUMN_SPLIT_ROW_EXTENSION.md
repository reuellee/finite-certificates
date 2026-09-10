# The split-row extension of the two-column affine theorem

This is a deductive extension of `original/TWO_COLUMN_AFFINE_VANISHING.md`.
It keeps that proof's quotient, positive column gauges, parent residence,
and rank-stratified compact-support calculation.

The first occurrence P still has both moving labels e,j confined to one
triple {a,e,j}, and its three other normals have a unique common point z
with z different from a. The second occurrence may instead have the form

    Q = {e,b,c}, {e,d,f}, {j,g,h}, {j,k,l},

with all letters other than e,j referring to the six fixed parent labels.
Within each triple the labels are distinct; repetitions between different
triples are permitted.

Retain the three planes

    Pi=span(a,e,j), He=span(e,b,c), Hj=span(j,g,h).

The proof in the original theorem shows that their normals are independent
on every actual uniform parent. In the positive gauges Hj(e)=epsilon_e and
He(j)=epsilon_j, let S span their common kernel. Then the full parent
residence in the retained quotient is an open convex polyhedron in

    e(s)=E+sS, j(t)=J+tS.

Every parent bracket is jointly affine by the cancellation S wedge S=0.
The two retained normal rows are nonvanishing scalar multiples of He,Hj;
the scalars are parent brackets up to fixed nonzero normalization factors.
Divide the Q determinant by these parent units. After a fixed row ordering,
its remaining equation is

    det(He, N_0+sN_1, Hj, M_0+tM_1)=0,

where N_1 is the derived normal of S,d,f and M_1 that of S,k,l. Its only
possible nonlinear term has coefficient

    det(He,N_1,Hj,M_1).

All four rows annihilate the same nonzero vector S. This coefficient is
therefore identically zero, without any genericity assumption or additional
parent-unit factorization. The reduced equation is jointly affine in s,t.

Consequently the entire compact-support calculation from the original
theorem applies: the rank-one locus has full open-interval fibers over an
open six-dimensional quotient; the closed rank-zero locus has full open
convex two-cell fibers. Thus the full pair-wall intersection has

    H_c^0=H_c^1=0

on every normalized uniform parent component, including every coefficient
rank drop and genuine parent-infinity end covered by that theorem's
coordinate identification.

For the balanced type50/type51 residue, this adds precisely the second
possible incidence pattern for the two moving labels. Each label occurs
twice in Q, and a type50 or type51 quartet has no repeated label pair.
Thus either one triple contains both moving labels (the original theorem),
or no triple contains both (this extension). Every record containing a
type50 factor can use its two degree-one labels in the same triple as e,j.
The type50 parent-unit P hypothesis was already proved in the original note.

The eight newly applicable source indices are

    254,256,482,483,486,488,497,499.

This gives 35 of the 45 balanced records when combined with the original
27-case presentation test, leaving the ten type51/type51 records. These
counts describe this support template; the coordinator and independent
referee own any resulting accepted coverage update. This note alone does
not close an original diagonal or the triple-bad obligation.
