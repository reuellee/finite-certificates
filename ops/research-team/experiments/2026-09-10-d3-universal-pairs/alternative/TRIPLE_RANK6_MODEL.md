# The populated rank-six triple obstruction and one scoped escape

## 1. The general remaining model

The concurrence-height pair proof in
`original/CONCURRENCY_HEIGHT_PAIR_VANISHING.md` has a direct triple analogue
when the three wall occurrences have unique concurrence points p,q,r and
one can use its type50/type51 contraction chart for the first occurrence.
Keep all four projected parent coordinates A and project q,r from p. On
q!=p and r!=p write

    q=(z_Q,w_Q), r=(z_R,w_R),  z_Q,z_R in RP^2.

The four Q and four R incidence equations are jointly affine in the four
parent heights and two concurrence heights:

    M(A,z_Q,z_R) (h_1,h_2,h_3,h_4,w_Q,w_R)^T = b(A,z_Q,z_R),

where M has eight rows and six columns. The parent inequalities still give
the full open convex height residence, with no restrictions on w_Q,w_R.

On the closed coefficient-rank-at-most-five locus, every nonempty fiber has
positive dimension and is open convex. Therefore its R^0 f_! and H_c^0
vanish. No smoothness assumption on that projected locus is required.

On the rank-six locus the unique candidate solution must satisfy two
additional compatibility conditions. Thus the full feasible incidence is a
graph over the actual locus

    E={ rank(M)=rank(M|b)=6, and the unique lift has all parent signs }.

E is a semialgebraic subset of the eight-dimensional projected base. It is
not known to be open there. An open-ambient-base argument cannot be applied
to E merely because the height solution is unique.

The remaining rank-six theorem would say that every component of this E is
noncompact for every relevant actual support triple, with all parent-sign
residences retained. Together with the lower-rank calculation, that would
exclude compact components of the corresponding triple intersection.

The concurrence collisions q=p or r=p must also be included. They impose
projected-parent conditions only for the collided block. The other block
still has at most four equations in five heights, so every nonempty fiber
has positive dimension; when both collide, the whole four-dimensional parent
height cell remains. These closed pieces have H_c^0=0. Collisions q=r!=p,
equal projected directions with different heights, and allowed projected
parent coincidences remain part of the model, including E. They cannot be
deleted as generic exceptions.

This does not by itself cover anchor kinds36,38,48,49 or occurrences whose
normal rank can drop. Any complete factor-triple route must either invoke
an already proved layer for those cases or supply the corresponding
contraction/incidence argument and its exceptional strata. A proof directly
for original triple-bad loci could use the actual proper three-signature
conditions and would not need this stronger all-factor endpoint.

## 2. An actual uniform point with rank six

`triple_rank_gate.py` reads the authenticated predecessor fixture, uses its
actual matrix and the explicitly stated supports below, and reconstructs
all incidence rows from determinants. It does not use legacy nested
`center.supports` metadata as the final support definition.

    P=123/145/246/357,
    Q=127/158/234/357,
    R=236/248/456/578.

The unique concurrence points are

    p=(1,7,7,0), q=(0,24,5,-4), r=(9,14,18,54).

Contract p using

    z(v)=(v_2-7v_1, v_3-7v_1, v_4), h(v)=v_1.

The projected parent matrix is

    (-7,1,0,0,-6,-8/3,24,31/9)
    (-7,0,1,0,-6,   0,-2,  -5)
    ( 0,0,0,1, 1,   6,-4,  -2),

and the two projected concurrence representatives are

    z_Q=(24,5,-4), z_R=(-49,-45,54).

Before height gauge fixing there are eight parent heights and w_Q,w_R,
so the eight incidence equations form an eight-by-ten homogeneous matrix.
The checker gives its complete rational matrix and a nonzero six-by-six
minor in `TRIPLE_RANK6_GATE.json`. Its exact rank is six. Its four-dimensional
kernel consists precisely of the three height shears and the actual lift
scaling direction. These four displayed vectors are independent and exhaust
the kernel by rank.

Fixing the heights of parents1,2,3,4 to (1,0,0,0) removes those four gauge
directions. The resulting eight-by-six matrix has rank six and its unique
solution is

    (h5,h6,h7,h8,w_Q,w_R)=(1,1,1,1,0,9).

Thus the zero-dimensional fixed-direction fiber is populated by an actual
uniform configuration; it is not a generic dimension-count speculation.
This fixture has a type49 anchor and serves as an exact local model of the
same affine incidence obstruction, not as a test of all global type50/51
quotient charts.

## 3. Allowing concurrence directions to vary restores escape here

Keep the projected parent matrix above but allow the four free heights to
vary, continuing to fix heights1..4. All70 parent brackets are jointly
affine in these four heights, so their fixed sign residence is an open
convex polyhedron.

The Q and R occurrence determinants factor as parent units times

    F=(126h7-164)h5+63h7h8-77h7-234h8+286,

    G=(205h5-95h7-208h8)h6
       +80h5^2+85h5h7+1301h5h8+582h7h8-1950h8^2.

The exact raw factors are (7/9)(4h5+h7)F and (8/3)h6 G. The checker
identifies [2357]=-(4h5+h7) and [2346]=-h6 in the original oriented parent
frame (and records further proportional parent brackets). Removing those
units therefore preserves the full uniform zero set. There are no discarded
coefficient-zero cases.

This is a triangular system: F is affine in h5 and independent of h6; G is
affine in h6. It excludes compact components over the open two-dimensional
base (h7,h8). Here is the rank-drop argument.

Suppose a compact component C existed. If its h6 coefficient in G vanished
at a point, G would be independent of h6 there, while F already is. The
full fixed-(h5,h7,h8) solution would contain an open h6 interval. Its
component is noncompact and closed in that fixed-base zero set, which is
closed in the full zero set. It lies in C, a contradiction.

Consequently the h6 coefficient is nonzero on C. Eliminate h6 and identify
this regular locus with an open residence in the F=0 locus. If the h5
coefficient in F vanishes at a point of C, consistency makes F identically
zero in h5 at that base. Again an open h5 interval, with h6 reconstructed
continuously, gives a noncompact component in a closed fixed-base fiber.
Otherwise both equations are successive graphs over an open subset of the
(h7,h8) plane, which has no compact component. All possibilities contradict
compactness.

This proves escape for the entire fixed-parent-projection zero locus of
this fixture, not just an infinitesimal direction or a finite sampled arc.
The projected directions of the two concurrence points are allowed to vary
along it. A compact component of the full triple locus through this fiber
would contain one of these noncompact closed fiber components and is
therefore also excluded.

The predecessor had already covered this factor triple by a different
square-affine height escape. This is not a new triple orbit or coverage
count. Its new diagnostic content is that the fixed-direction rank-six
obstruction is actually present, yet it disappears here after those
projected directions are allowed to vary.

## 4. Exact next endpoint

A complete next step must exclude compact components of the genuine
rank-six compatibility loci globally, or give a different global escape
that lets projected concurrence directions vary. It must retain all rank
changes, concurrence collisions, permitted projected-parent coincidences,
and parent boundaries, and must account for the remaining anchor kinds.
The triangular factorization above proves that step only over this one
fixed projected parent configuration. No argument currently extends that
triangular structure to every remaining support triple and every projected
parent configuration. No original diagonal is closed here.
