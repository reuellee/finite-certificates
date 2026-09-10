# Candidate: escape when the concurrence line contains a parent

## Statement

Fix three ordinary occurrences of distinct primitive factors P,Q,R on a
normalized component X of a realizable uniform rank4 parent on8. Let Z be
their triple zero set, let p,q,r be the ordinary concurrence maps, and remove
their pairwise coincidence union Delta. Use p as the anchor, and let K be
the vertical critical locus in Z minus Delta, defined by dependence of the
two accepted eight-height circuit-gradient vectors gamma_Q,gamma_R.

For a parent label i define

    C_i={Y in K: p,q,r are collinear and Y_i lies on their line L}.

Then every component of C_i is noncompact. Consequently Hc0(C_i;Q)=0.
The finite union C=union_i C_i is closed in K and has Hc0=0, so its removal
preserves Hc0(K). This leaves the distinct-collinear locus with L disjoint
from all eight parents, as well as the noncollinear critical locus.

Status: candidate deduction by the referee track, requiring independent
prover review before acceptance. It is not a complete critical-locus theorem.

## Fixed-frame slide and its full residence

Take Y in C_i. Uniformity lets us choose a projective frame from five of the
other seven parents. Reframe X using that fixed labeled frame; all frame
denominators are nonzero parent brackets, so this is a homeomorphism of the
whole original normalized parent component. In these coordinates hold the
other seven parents fixed.

The three distinct concurrence points span a fixed projective line L. None
of them is the parent Y_i. Every selected ordinary plane containing label i
contains both Y_i and its own concurrence, and therefore contains all of L.
Its other two fixed parent columns determine that same plane together with
L. If they both lay on L, three original parents would be collinear,
contradicting uniformity; hence at least one lies outside L.

Replace Y_i by a point y moving along L. Whenever the parent remains
uniform, each selected plane containing i is exactly its original plane:
the span of y and the other two defining parents lies in that plane and is
three-dimensional. Every selected plane not containing i is fixed outright.
Thus all selected plane rays and all three ordinary concurrences remain
fixed on the entire allowed slide.

Choose a P plane whose triple does not contain i. Such a plane exists by
the ordinary-support condition. Its fixed normal ell vanishes at p but is
nonzero at Y_i by the parent bracket condition. Represent moving columns by
ell(y)=ell(Y_i), using positive column scaling on its fixed sign chart. This
identifies L minus p with an affine real line and includes every allowed
point in that column-sign chart. All parent brackets involving y are affine
in its parameter. Their prescribed strict signs therefore define one open
interval J containing the original point. All other brackets are constant.
No extra equality or sector restriction is inserted.

The interval J may be bounded or unbounded, but as a topological interval it
is noncompact. Its missing endpoints are outside the uniform parent
residence. The points p,q,r themselves are excluded: moving the parent to
one of these ordinary nonparent concurrences makes a selected plane not
containing i contain that parent, forcing a zero parent bracket.

The full fixed-other-parent, fixed-line, fixed-column-gauge slice in the
reframed X is closed in X. J is its full component with the prescribed
parent signs; it lies wholly in the same original component because it is
connected and contains Y. Equivalently, it is a component of the closed
slice and hence closed relative to that slice. No projective infinity is
lost in this assertion: ell(y) is nowhere zero on X, and the affine chart
excludes only the already-forbidden parent bracket ell(y)=0.

## The critical relation persists

Use the accepted pole-free circuit formula for gamma_Q. On the slide, write
each moving Q normal row as n_I(t)=a_I(t)n_I(0); its multiplier is nonzero
on J. Rows not containing i have a_I=1. If lambda_I(0) is a circuit
dependence, choose lambda_I(t)=lambda_I(0)/a_I(t). This is a continuous
dependence with the unchanged coefficients on all fixed rows.

For a selected Q row containing i, every contribution to every component
of its gradient is zero:

* When the differentiated column is another parent in that row, the
  determinant contains y,p,q. All three lie on L, so it vanishes.
* When the differentiated column is i, the determinant contains p,q and
  the other two defining parents. All four lie in the fixed Q plane that
  contains L, so it vanishes.

Rows not containing i use only fixed parents and the fixed p,q, and their
chosen circuit coefficients are fixed. Therefore gamma_Q remains fixed
with these representatives. The same argument applies to gamma_R, using r
instead of q. In particular their rank stays unchanged. Any further
nonzero rescaling of the circuit or parent representatives preserves this
rank. The slide remains in K; p,q,r remain distinct, and y remains on L.
Thus J lies entirely in C_i.

## Closed-component argument and excision

If a compact connected component D of C_i contained Y, then the connected
slide J would lie in D. Since J is a component of the fixed-coordinate
closed slice, it is closed in C_i. It would be a closed noncompact subset
of compact D, a contradiction. Hence C_i has no compact component.

In Z minus Delta, collinearity is a closed rank condition. The line through
p and q is continuous there, and membership of Y_i in this line is another
closed rank condition. Thus each C_i is closed in K. The finite closed-cover
degree-zero Mayer-Vietoris injection gives Hc0(C;Q)=0. Compact-support
localization then identifies Hc0(K minus C;Q) with Hc0(K;Q).

All ordinary support kinds and all original parent components are included.
The deduction uses no genericity, no finite sampling, and no unproved
criticality-to-collinearity implication. It does not settle the part where
the common line contains no parent, nor the noncollinear critical locus.
