# Pair-wall vanishing from two concurrence points

## Theorem

Let X be any normalized component of a uniform rank-four parent on eight
labels. Let P and Q be labeled type50 or type51 residual occurrences. Then

    H_c^q(X intersect H_P intersect H_Q;Q)=0,  q=0,1.      (1)

This includes every remaining balanced pair record. Together with the
inherited results for the other factor kinds, it closes the stronger universal
pair-wall H_c^1 endpoint for all9,476 unordered distinct residual-factor
pair orbits. It does not close the independent triple-bad compactness
obligation or by itself prove original D3.

The proof retains the two actual plane-concurrence points. After one
contraction, the four equations defining the second point are affine in five
height variables. No conic-fiber topology or separate orbit certificate is
required.

## 1. Incidence and normal ranks

Up to relabeling, the two kinds have supports

    type50: 123 / 145 / 246 / 378,
    type51: 123 / 145 / 267 / 468.

Each label occurs once or twice, with four labels of each degree. Every pair
of triples meets in at most one label. In either support, every selected
three triples contain two sharing a parent label absent from the third.
Their two derived normals are independent: otherwise their two planes
would coincide and contain at least four distinct parent points. Those
two normals annihilate their shared parent point, whereas the third normal
evaluates nontrivially there by a parent four-bracket. Thus every selected
three normal rows are independent on every uniform parent realization.

On the residual wall, all four rows have determinant zero and hence rank
exactly three. They have a unique common projective kernel point. Write p
for the point associated with P, and q for that associated with Q. Both are
continuous semialgebraic functions of Y; one fixed ordered triple of rows
gives their projective coordinates by its exterior product. Neither point
can equal a parent point, since each parent label is absent from at least
one support triple, which would then give a zero parent four-bracket.

The four P planes descend after contraction by p to four projective lines
in a projective plane. No three of these lines are concurrent, by the
three-row independence above. They form a labeled projective frame in the
dual plane and can be normalized to four fixed lines.

## 2. A four-dimensional projected parent base

The four degree-two parent labels project to the corresponding pairwise
intersections of the fixed P lines. Each degree-one parent projects to one
freely varying point on its one P line. Such a point cannot meet any other
P line: the original parent would then lie in a support plane whose triple
does not contain its label, contrary to uniformity.

Consequently each free projected point has a fixed affine line coordinate,
with three forbidden line intersections. There are four free coordinates,
giving an open projected parameter domain in R^4. Additional inequalities
or exclusions needed for a parent lift merely restrict this domain; their
nonempty-lift locus is open, because a strict feasible lift persists.
Allowed coincidences of two free projected points on the same P line are
retained. In particular the two low-degree labels7,8 of type50 may project
to the same point; no distinctness assumption deletes that stratum.

For completeness, the normalization may be performed using positive parent
column rescalings. Three independent P normals give quotient coordinates;
scale them so that the fourth is their sum. All three scale coefficients
are nonzero. Normalize each projected parent column using one P normal
whose triple omits that parent; its evaluation is a nonzero parent bracket.
The signs of these finitely many nonzero normalization coefficients are
locally constant. Work on their finite clopen sign sectors, choosing the
corresponding fixed signed projected representatives. This avoids negative
parent-column rescalings or silently identifying sign sheets. The eventual
vanishing on their finite disjoint union follows immediately.

The four high-degree projected parent points are fixed. For the displayed
supports, labels1,2,4 are independent in the projected three-space. Their
independence follows directly from the four fixed lines in general position.
The fourth high-degree label is3 for type50 and6 for type51.

## 3. Four parent height variables

Put p in the fourth coordinate direction and write the parent columns

    Y_i=(A_i,h_i),

where the projected signed representatives A_i are fixed by the four
coordinates above. Use the three height-translation gauges to set the
heights of labels1,2,4 to zero. The parent bracket on the four high-degree
labels is nonzero; use it to normalize the remaining positive height scale.
The height of the fourth high-degree parent is then a fixed nonzero constant
on the chosen orientation sector. The only remaining heights are those of
the four degree-one parents.

Every parent four-bracket is affine-linear in those four heights. For a
fixed projected configuration A, all prescribed parent signs therefore
cut out a possibly empty open convex polyhedron C_A in R^4. When nonempty
it is a full four-dimensional open convex manifold. It is the entire
height fiber; no residual determinant condition remains for P, whose four
planes already share p by construction.

This construction is a coordinate description of the original projective
realization quotient, rather than a projection which drops further lift
conditions. Conversely every point of C_A reconstructs a uniform parent
realization on H_P. Its connected height fiber maps entirely into one
normalized parent component. Restricting to X selects whole fibers.

## 4. The locus q=p is closed and has four-dimensional fibers

Inside the pair-wall intersection Z= X intersect H_P intersect H_Q, equality
of the two continuous projective concurrence points is a closed condition.
Denote this locus by Z0.

In the P contraction chart, q=p is equivalent to

    det(A_I)=0 for every triple I in Q.                     (2)

These conditions depend only on the projected base. They imply that all
four Q normals annihilate p; their rank is still exactly three by section1,
so their concurrence is indeed p. Thus over the projected locus (2), the
fiber of Z0 is the whole C_A. Compact-support base change gives

    R^r f_! Q =0 for r<=3,
    H_c^r(Z0;Q)=0 for r<=3.                               (3)

No smoothness or openness of the locus (2) is required.

## 5. On q!=p, four affine equations in five heights

Let Z*=Z minus Z0. Project q from p to a nonzero projective point
z in RP^2. In a local choice of representative for z write

    q=(z,w).

The scalar w is one additional height variable. Different choices of z
representative change w by a nonzero linear transition; this is a line
bundle over RP^2 and causes no loss of projective ends or sign sectors.
The base for Z* consists of the four projected parent coordinates and
z in RP^2. It has dimension six.

The four equations that q belongs to the Q support planes are

    det(Y_I,q)=0,   I in Q.                                (4)

For fixed A and z, expanding each determinant along the height row makes
(4) affine-linear in the four free parent heights and w. Thus

    M(A,z) (h_1,h_2,h_3,h_4,w)^T = b(A,z),                (5)

with a four-by-five coefficient matrix. The remaining conditions are the
strict parent inequalities C_A on h; w has no inequality. Every full
nonempty fiber is consequently an open convex subset of the affine
solution space to (5).

Retaining q introduces no spurious parent points. A point satisfying (4)
has rank-three Q normals by uniformity, so q is their unique concurrence.
Conversely every pair-wall point with q!=p has exactly this representation.

## 6. Rank filtration and compact supports

On the open coefficient-rank-four locus, the affine solution spaces form
an affine-line bundle. The nonempty-parent-residence locus V in its
six-dimensional base is open: a solution in the strict convex parent cell
persists by a local nonzero four-by-four coefficient minor. Restriction to
X still selects whole connected fibers and an open image.

The ambient base is an open subset of R^4 times RP^2, on each finite
normalization sign sector. Each ambient component is noncompact; for
example it projects onto a noncompact open component of the four-dimensional
parent-position domain. V can therefore have no compact component. Every
fiber over V is one connected oriented or orientation-twisted open interval.
Integration along it gives its orientation local system shifted by one.
Hence H_c^0(V;orientation)=0 and

    H_c^0(Z*_(rank4);Q)=H_c^1(Z*_(rank4);Q)=0.             (6)

The coefficient-rank-at-most-three part is closed in Z*. Its nonempty
fibers are open convex manifolds of dimension at least two, including
inconsistent/identically-zero equation cases by allowing empty fibers.
Therefore its R^0 f_! and R^1 f_! vanish. Compact-support Leray and the
closed/open localization sequence combine this with (6) to yield

    H_c^0(Z*;Q)=H_c^1(Z*;Q)=0.                             (7)

Finally apply localization for the closed subset Z0 of Z and use (3).
This proves (1).

The argument uses full convex fibers and proper-support direct images.
It preserves all parent-boundary ends, unbounded lift directions, concurrence
collisions q=p, coefficient-rank drops, and allowed projected coincidences.
No inference is made from nonproper ordinary homotopy equivalence or from
pointwise conic rationality.

## Scope and audit status

Complete candidate proof submitted for independent line-by-line review.
The conclusion concerns universal factor-pair H_c^0,H_c^1 vanishing. Original
diagonal three still needs the independent triple obstruction and the
audited global comparison connecting the sufficient endpoint to the
original statement. No original theorem-ledger promotion is made here.
