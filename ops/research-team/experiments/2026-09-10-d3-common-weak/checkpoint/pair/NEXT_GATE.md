# The first test of the 574-case endpoint

The next target is exactly the 574 relative-label pair-wall source orbits
remaining in coordinator/HARD_PAIR_RESIDUE.json. This is a stronger sufficient
endpoint for original D3, not the original pair restriction map itself.

The first populated hard case is the actual type50+50 pair

    P = 123/145/246/378,
    Q = 567/158/268/347.

Its support union has degree3 at every label. The falsifier provided and
independently verified a uniform rational point on both walls. Thus empty
geometry cannot dismiss this support obstruction.

We tested whether the successful ruled-quadric proof can simply be reused
by forgetting one parent column. It cannot: at the exact anchor, fixing the
first seven columns and varying column8 gives the full pair-wall fiber

    g = -5*i/4 - 8,
    h = (115*i - 1196)/67,
    -12 < i < -36/5.

Here g,h,i are the three affine coordinates of column8. The first wall gives
the g formula. After substituting it into the second determinant, the exact
polynomial is

    (3/16)(h - 10*i - 32)(67*h - 115*i + 1196).

The first factor is literally the parent bracket [2678], hence is nonzero
on the original parent cell. This leaves the displayed affine line. All70
prescribed parent signs become strict linear inequalities in i. Their exact
intersection is the interval shown; its endpoints are the genuine parent
walls [3468]=0 and [3458]=0. The coordinate i is retained, so the map is
bijective and there are no omitted branches or projective ends.

This full fiber has Hc1=Z. Consequently the one-column forgetting map has a
nonzero degree-one compact-support direct-image stalk. This does not prove
a global pair cohomology class, and it does not refute the stronger endpoint.
It does reject an automatic extension of the current zero-Hc1 fiber proof.

The executable replay is verify_hard_column_fiber.py, using exact polynomial
arithmetic over rational numbers, with no imports of producer symbolic
acceptance code. It reconstructs both derived determinants, the parent-unit
factor, all70 signs, both interval endpoints, and a hostile endpoint change.
Its output is HARD_COLUMN_FIBER_CERTIFICATE.json. The earlier SymPy scripts
are discovery records only and are not needed for this certificate.

A concrete successor must therefore either (1) exhibit a quotient moving at
least two parent columns whose full fibers have Hc0=Hc1=0, including all
singular fibers, or (2) retain the nonzero R1 f! term and prove that it has no
compactly supported global sections on the deletion base. The latter is a
real specialization problem; pointwise interval noncompactness does not
settle it. Before applying either construction to the574-source list, its
formula must pass this exact populated hard pair and its parent boundaries.
No rotating-plane two-column quotient has yet been proved.

## A stronger affine-fiber rescue was also tested

A nonzero Hc1 stalk is not itself fatal to a quotient proof. If all full
fibers are connected oriented open intervals over an open6-dimensional
base, the degree-one direct image is locally constant and its Hc0 vanishes.
If the two equations are uniformly affine-linear in the forgotten column,
one can also retain the closed coefficient-rank-drop stratum, whose fibers
are convex planes or3-cells. That would prove pair Hc1=0 without requiring
all stalks vanish. The independent referee accepted this conditional lemma.

However, the interval's two-linear-equation presentation is not uniform
for the chosen hard pair and the fixed column8 projection. Change the
retained coordinate c from-4 to-399/100, keeping

    (a,b,d,e,f)=(7,-8,-17/4,2,-3).

The first equation still gives g=-5i/4-8. The second becomes3/160000 times

    Q(h,i)=696072h²-7855535hi-9451068h
           +11465000i²-83098930i-383497152.

The homogeneous conic matrix has exact determinant

    -144211276259416406250 !=0.

Thus this conic is nonsingular and cannot be a parent-unit factor times an
affine-linear residual on a nonempty open parent chamber. This is populated
actual geometry: column8

    (g,h,i)=(458935322,-6168314428,-1504387688)/177693661

satisfies both walls and all70 parent brackets are nonzero. The exact checker
verify_smooth_conic_gate.py reconstructs this identity and point independently
of the discovery symbolic calculations. Its report is
SMOOTH_CONIC_GATE_CERTIFICATE.json.

This refutes only the uniform affine-linearity rescue in this particular
projection. A connected-conic fiber theorem, a different projective frame or
forgotten column, and a two-column quotient remain possible. The next
construction must include both this nonsingular conic and the earlier
parent-unit-degenerate conic, with their specialization. No claim about the
number or topology of full smooth-conic fiber components is certified here.
No additional original or stronger pair-wall source orbit was closed by
these two discriminators; the honest residue remains574.
