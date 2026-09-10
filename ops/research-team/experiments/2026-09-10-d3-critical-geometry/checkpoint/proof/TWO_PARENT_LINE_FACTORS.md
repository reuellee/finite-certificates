# Triple noncompactness with two parent-line concurrence factors

## Theorem

For every realizable uniform rank4 parent on eight labels, every normalized
connected parent component X, and every three distinct primitive residual
factors P,Q,R, suppose at least two of the factors belong to the global
families36 or38. Then every component of

    X intersect {P=Q=R=0}

is noncompact. Equivalently its H_c^0 with rational coefficients is zero.

No genericity, transversality or coefficient-rank assumption is imposed. All
projected-parent coincidences, concurrence collisions and original parent
components are included. This theorem is a subclass of the missing universal
triple endpoint; it does not by itself close the original third diagonal.

## Inputs

The independently audited all-factor contraction model is recorded in
`../referee/ANCHOR_COVERAGE_AUDIT.md`. Every global factor admits an ordinary
four-normal occurrence with a unique nonparent concurrence. In particular:

* global36 can be represented by a relabeling of ordinary type37,
  `123/124/345/567`;
* global38 can be represented by a relabeling of ordinary type38,
  `123/124/345/678`.

Unit equivalence on the uniform parent locus permits these ordinary
representatives for the two selected factors, independently of which original
localized occurrence was used to name each factor. For each representative,
every three of the four normal rows are independent on its wall.

## Parent-line parameters

Name the two selected factors Q,R. Their ordinary occurrences each have a
pair of triples sharing two parent labels. Write Q's first two planes as

    span(Y_a,Y_b,Y_c), span(Y_a,Y_b,Y_d).

Uniformity implies that their intersection is exactly the projective parent
line span(Y_a,Y_b). The unique Q concurrence q lies on that line and is neither
parent endpoint. For any fixed representatives of the parent columns it can
therefore be represented uniquely in the form

    q=Y_a+t Y_b,  with t in R minus {0}.

The corresponding parameter for R is

    r=Y_e+u Y_f,  with u in R minus {0}.

These parameters are continuous functions of the parent on the triple wall.
They do not require the projections of either parent pair to be distinct.
For example, if p lies on line(Y_a,Y_b), the projected representatives can
coincide or even cancel at one value of t; the original vector Y_a+tY_b
remains nonzero because the two parent columns are independent. Such a value
simply gives q=p and is retained.

## Four affine equations in four heights

Use any ordinary occurrence for P and its all-factor contraction chart. On
each of the finitely many clopen sign sectors, the P wall is a full strict
parent residence in

    (A,h) in an open subset of R4 times R4.

Here A comprises four projected-parent coordinates, and the four free parent
heights h remain after three height shears and one positive scale gauge. For
fixed A the parent sign conditions define an open convex cell C_A.

The first two Q incidence equations hold automatically for q=Y_a+tY_b.
Its other two equations are

    det(Y_i,Y_j,Y_k,Y_a+tY_b)=0

for the remaining two Q triples. Each determinant is affine in all four
height variables together at fixed A,t: every parent column has the form
z_j+h_j p, and terms containing p twice vanish. This also holds when the
last column's height is h_a+t h_b. There is no division by a height-dependent
coefficient.

R supplies exactly two more equations of the same form with parameter u.
Thus the entire triple incidence is

    M(A,t,u) h = b(A,t,u),    h in C_A,

with four equations in four unknown heights over the open six-dimensional
base A4 times (R minus {0}) squared. The incidence is homeomorphic to the
original triple zero set on this sector: from a parent on the triple wall,
uniqueness of its ordinary concurrences gives unique t,u; conversely the
four affine equations together with the two automatic planes in each block
give exactly the three factor-wall conditions. Parent uniformity ensures
that the ordinary concurrence rank never introduces an extra solution.

## Compact-component exclusion, including every rank drop

Suppose this incidence had a compact connected component C.

At a point whose coefficient matrix has rank at most3, the full fiber over
(A,t,u) is a nonempty open convex subset of an affine space of dimension at
least1. It is connected and noncompact. This full fiber is closed in the
incidence, since the parameter point is closed, and it lies in C because it
is connected and meets C. It would then be a closed noncompact subset of a
compact space, a contradiction.

Consequently C lies wholly in the rank4 locus. There the unique solution is
h=M^{-1}b. Its membership in the full strict parent residence is an open
condition on (A,t,u), so the rank4 incidence is a graph over an open subset
of R6. Since C is a connected component of that regular locus as well, its
image is a nonempty open subset of R6. Compactness of C would make that image
compact, which is impossible.

Both possibilities contradict compactness. The proof includes all lower
coefficient ranks, all sign sectors and every original parent component.
This proves the theorem.

## Coverage boundary

The theorem covers every actual support and specialization whenever at least
two factors are in the global families36/38, with an arbitrary third factor
of any of the six global kinds. Its application needs no finite inventory.
No new numerical triple-orbit count is asserted here: the coordinator must
compare this theorem with the authenticated already-covered source layers
before assigning any count. Triples with at most one such factor remain
outside this theorem.
