# Direct pair proof track

Status: an actual-parent low-degree vanishing and excision theorem was proved
and independently accepted. The original alternating restriction map remains
open; no original 9DVL obligation is discharged. This track did not impose a
finite certificate inventory.

The principal result is in COMMON_WEAK_PRIMAL_VANISHING.md: the simultaneous
bad locus admitting one common nonzero weak primal vector is closed and has
H_c^q=0 for q=0,1,2, for any number of signatures. The proof uses full convex
height fibers of dimensions four or three, including parent-point limits.
For an actual triple, this subset can be deleted coherently from the triple
locus and all three pair loci without changing either remaining original
obligation or the kernel of the alternating restriction map. This removes
the common-weak degeneracy stratum as a source of the obstruction. Actual
triple-bad points without any weak primal vector exist, so the complement
still requires a proof.

The remaining sections record a feasible-reference coordinate exploration
and one small formal shortcut countermodel; they are secondary to this
actual-parent theorem.

## 1. Exact feasible-reference coordinates

Fix distinct signatures i,j,k and put E_ij=B_i intersect B_j intersect F_k.
Retain a private feasible vector p for k. Let a_I(Y) be the unsigned derived
normal and define

    c_I(Y,p) = sigma_k(I) a_I(Y) / (sigma_k(I) a_I(Y)p).

Every denominator is strictly positive; every c_I evaluates to 1 on p. For
another signature l put epsilon_I=sigma_l(I)sigma_k(I). Then

    Y in B_l iff
    conv{c_I : epsilon_I=+1} intersects conv{c_I : epsilon_I=-1}.

An empty sign class has empty convex hull, so the formula includes it. Indeed,
a nonnegative nonzero signed Gordan relation becomes a relation among
epsilon_I c_I by positive diagonal rescaling. Evaluation on p says its two
total masses agree. Their common value is positive; dividing by it gives a
point in the two convex hulls. Conversely, an equality of convex combinations
gives a nonnegative Gordan relation. No general-position or constant-rank
assumption on the derived normals is used.

This is an actual-parent identity, valid on every parent component and through
all residual rank drops, as long as k is feasible. It uses no selected bad
witness. The feasible private-vector cone does admit a continuous section,
because strict feasible vectors persist locally and its fibers are convex;
this does not contradict the known failure of continuous bad-witness sections.

For compact supports, retain the degree shift. Normalize p by a positive sum
of the four basis-sign coordinates. Its feasible fiber is a nonempty open
convex three-dimensional polytope in an oriented affine hyperplane. The
normalized incidence projection f to E_ij is relatively open in an oriented
affine-three-bundle. Integration along the convex fibers gives

    R f_! Q = Q[-3],
    H_c^(q+3)(incidence over E_ij;Q) = H_c^q(E_ij;Q).

In particular the exclusive-pair target becomes degree FOUR on the incidence
space, not degree one. An ordinary homotopy equivalence obtained by forgetting
p does not preserve compact-support degrees.

Putting p=e4 and holding the rank-three contraction fixed makes the normalized
derived normals affine-linear in the parent lift heights. This is a useful
coordinate description, but the known actual same-contraction nonconvexity
example prevents an immediate convexity argument after an additional private
extension is forgotten. Nor does this description prove independence of the
three images in H_c^1(T). Those are the two unresolved load-bearing steps.

## 2. A common-row countermodel for the original map

The source graph countermodel in DIAG3_PAIR_DIFFERENTIAL_ENDS.md section 5
can be realized using one common unsigned rank-four row family and three
reorientations, while retaining all the inherited lower cohomology vanishings.
Thus common rows plus those vanishings do not supply a direct formal proof.

For arbitrary real-valued functions g0,g1,g2 use five rows

    a1=e1, a2=e2, a3=e3, a4=e4,
    a5=(g0^2,g1^2,g2^2,-1).

The family has rank four everywhere, and all rows are nonzero. Choose

    sigma0=(+,-,-,+,+),
    sigma1=(-,+,-,+,+),
    sigma2=(-,-,+,+,+).

For signature i, the first three primal coordinates have positive sign in
position i and negative signs in the other two positions, while p4>0. If
g_i=0, the fifth strict inequality is impossible. If g_i is nonzero, set
p4=1 and p_l=-1 for l distinct from i, and then choose p_i>0 sufficiently
large to make it hold. Consequently

    B_i = Z(g_i).

Over B_i, the normalized Gordan fiber is a singleton. In the row order above,
its unnormalized weights are zero at basis row i, g_l^2 at the other two
basis rows, and 1 at each of rows 4 and 5. Divide by 2+sum_(l!=i)g_l^2.
The first four rows are a basis, so there is no other normalized relation.

Now take X=R_t times R_u^7 times R_z and

    r(u)=sum_(l=1)^7 u_l^2-1,
    g0=z, g1=z-r, g2=z-r(2+r^2).

Every B_i is a graph over R^8. Pairwise differences of these three graph
functions are r, r(2+r^2), and r(1+r^2). The latter extra factors never vanish
over the reals. Therefore all three pair intersections and the triple
intersection are exactly

    T={z=0,r=0}=R times S^6.

The three good loci are proper and pairwise incomparable. For example set
u=(1,1,0,0,0,0,0), hence r=1; the points z=0,1,3 lie respectively on only
B0, only B1, and only B2.

Compact-support Kunneth and B_i=R^8 give

    H_c^q(B_i;Z)=0 for q<=2,
    H_c^0(A_ij;Z)=H_c^0(T;Z)=0,
    H_c^1(A_ij;Z)=H_c^1(T;Z)=Z.

Every restriction A_ij to T is the identity, so

    D=(1,-1,1): Z^3 -> Z,
    ker D = Z^2,
    H_c^2(B0 union B1 union B2;Z)=Z^2.

All E_ij are empty. Thus the precise failure is image independence, not
exclusive-pair H_c^1. This model also has H_c^1 of the full bad union zero,
as in the original graph example.

If exactly 56 rows are desired, append 51 rows e4+c a5 with distinct rational
c>0, c!=1, assigning their signs + in all three signatures. They are positive
combinations of two already-positive primal rows and hence redundant. Their
fourth coordinates are 1-c, so none is zero. This preserves all bad sets and
the rank-four condition, although the normalized witness fibers need no longer
be singletons; they remain compact convex polytopes.

## 3. Exact scope boundary

This is NOT an actual parent counterexample. On T, a5=-e4; there is a positive
two-row circuit. Distinct derived normals of a uniform rank-four parent cannot
be proportional: equal normal lines would put the union of two distinct
parent triples (at least four distinct labels) in one three-plane, contrary
to uniformity. The countermodel deliberately violates this actual constraint.

The source already had a two-signature common-row countermodel that violated
the second diagonal, and separately a three-signature graph model satisfying
the lower vanishings. The present combination shows that common rows do not
repair the latter model. It is an auxiliary logical separation, not original
theorem advancement or a claim of literature novelty.

The smallest next discriminator for this particular formal route is whether
one can preserve the low cohomology and the mixed kernel after excluding every
two-row derived dependence. Even a positive answer would still be an abstract
countermodel unless the full third-compound determinant identities and actual
extension axioms were imposed. The direct mathematical proof must use such
additional parent geometry, not only reorientation of a common matrix.

For a positive continuation of the reference-coordinate route, the necessary
new lemma is a genuine low-degree compact-support theorem for the two
convex-hull-intersection conditions in the actual contraction-height family,
including its exit data at the third-bad frontier. The coordinate equivalence
alone supplies none of that theorem. No convergent computational search or
completion-time claim is made.

## 4. Inputs and independent review

All source inputs are the authenticated checkpoint at base
499f1190d988be5729b38db59e6cc8230fae7857, with mathematical sources at
59fec66666518257c585194b81061f60d91f439d:

- checkpoint/inputs/DIAG3_PAIR_DIFFERENTIAL_ENDS.md, especially sections 1,2,5;
- checkpoint/inputs/DIAG3_JOINED_FLOW_TRIANGLE.md, especially sections 6,7;
- checkpoint/inputs/ATLAS_HELLY.md, sections 4.1,13,14 and the common-row
  second-diagonal countermodel;
- inputs/BLOCK_GORDAN_FORMAL_NO_GO.py, inspected to distinguish independent
  block matrices from one shared unsigned row family.

The feasible-reference equivalence, its compact-support shift, the common-row
construction, and the complete actual-parent common-weak theorem received
independent deductive acceptance from /root/referee. No numerical experiment
or computer theorem is used in these deductions.
