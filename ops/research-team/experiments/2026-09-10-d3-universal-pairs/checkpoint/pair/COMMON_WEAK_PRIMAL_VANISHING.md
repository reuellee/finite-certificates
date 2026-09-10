# Low-degree vanishing for the common weak-primal bad locus

## Statement

Let X be one normalized realization-space component of a uniform rank-four
oriented matroid on eight labeled elements. Let S be any nonempty finite set
of fixed signed extension systems, with unsigned derived normals a_I(Y),
I a parent triple. Write B_sigma for strict infeasibility of
sigma(I)a_I(Y)p>0. Define

    I_S = intersection_(sigma in S) B_sigma,
    W_S = {Y in I_S : there exists p!=0 such that
                       sigma(I)a_I(Y)p>=0 for every sigma,I}.

Then W_S is closed relative to X and

    H_c^q(W_S;Q)=0 for 0<=q<=2.                    (1)

The proof uses a finite mathematical stratification and convex height fibers.
It requires neither a per-factor certificate inventory nor a continuous
choice of bad Gordan witnesses. The signs need not form an antichain for
this theorem. In particular it applies to every actual 9DVL antichain.

The theorem concerns a subset of simultaneous badness. A system possessing
a positive Gordan dependence whose support spans R4 has weak-primal cone
{0}; such points do not belong to W_S.

## 1. Proper weak-primal comparison

Fix one signature sigma0 in S. Four basis-triple normals, coming from four
fixed parent basis columns, are a continuously varying basis of the dual
four-space. In the normalized parent frame they are fixed nonzero multiples
of the four coordinate forms. The four sigma0-signed weak inequalities put
p in one fixed closed pointed orthant. Let ell be the positive sum of its
four signed basis coordinates. Every nonzero vector in this orthant satisfies
ell(p)>0, so impose ell(p)=1.

The normalized common weak cone is consequently a closed convex subset of
one fixed compact three-simplex. Define

    J_S={(Y,p):Y in I_S, ell(p)=1,
                 sigma(I)a_I(Y)p>=0 for every sigma,I}.

It is closed in X times that compact simplex. Projection pi:J_S->W_S is
proper, surjective, and has nonempty compact convex fibers. Its image is
closed in X. Proper base change identifies R pi_* Q with Q, including the
constant-sheaf unit, and hence

    R Gamma_c(J_S;Q) = R Gamma_c(W_S;Q).            (2)

This is a proper comparison. It differs from the degree-three compact-support
shift for retaining a strictly feasible private vector.

## 2. A finite closed filtration

At (Y,p), let Z be the set of parent triples satisfying a_I(Y)p=0. On its
complement, every permitted sign is already fixed by sigma0, since all weak
inequalities for sigma0 hold. If signatures disagree on a triple, that
triple necessarily belongs to Z.

The sets where at least m of these 56 evaluations vanish are closed in J_S.
Thus decreasing m gives a finite closed filtration, whose successive
differences are finite disjoint unions of the exact-Z strata. An exact-Z
stratum is clopen in its corresponding difference. It suffices to prove
low-degree vanishing on each nonempty exact-Z stratum; the localization long
exact sequences then give the same vanishing on J_S. This step handles the
attachment of extra-zero strata, including limits p equal to a parent point.

## 3. Contraction and existence of a projected frame

Contract the line p and denote the resulting rank-three vector configuration
by A. Locally in a projective normalization write

    p=e4,              Y_i=(A_i,h_i).

The signs and zeros of the projected triple determinants are precisely the
fixed sign/zero data of a_I(Y)p. Thus, on each exact-Z stratum, its projected
oriented matroid is fixed, and a fixed labeled projective frame can be chosen
once for the whole stratum.

Here are the small uniformity facts needed for this assertion and the later
height argument.

1. Every four parent columns project to rank at least three, because their
   original rank is four and quotienting by one line drops rank by at most
   one. Therefore at most three projected parent points can lie on a
   projective line, with multiplicities counted.
2. Every three parent columns project to rank at least two, by the same
   argument and original rank three. In particular every zero projected
   triple has rank exactly two.
3. There is at most one zero projected column. If A_e=0 then p is the parent
   point Y_e, and the remaining seven projected points are uniform rank three.
4. There cannot be two distinct parallel projected pairs: the corresponding
   four parent columns would project to rank at most two. Nor can three
   projected columns be parallel.

Consequently there is a projected projective frame of four nonzero points
with no three collinear. To see it directly, select three independent
projected points a,b,c. If no fourth point completes a frame, every remaining
point lies on one of their three connecting lines. Each such line contains
at most one additional point, by item 1; this accounts for at most six
nonzero projected points, counting multiplicities. There are at least seven
nonzero points. This contradiction proves the assertion. Whether a specified
four-tuple is a frame is determined by Z, so a fixed tuple works throughout
each stratum.

Normalize that projected frame, with the fixed orientation choices inherited
from the sign stratum. Use the ambient normalized realization stratum of
this fixed projected sign/zero pattern as the contraction base, allowing
empty fibers. This stratum is locally closed and semialgebraic; no local
compactness assertion about a projected image is needed. There is a
well-defined quotient map from the exact-Z incidence stratum. No single
projected frame is claimed to work across different Z strata.

## 4. The full height fiber is convex

For a fixed normalized projected configuration A, choose fixed nonzero vector
representatives for its nonloop columns. Every lift is described by heights
h_i. Changing h by a linear functional of A is the three-dimensional
translation gauge. A positive common height scaling is the residual
one-dimensional projective gauge. Parent bracket signs are homogeneous
linear strict inequalities in the heights:

    det(Y_i,Y_j,Y_k,Y_l)
        = sum_(v in {i,j,k,l}) signed h_v det(A_(others)).

Choose three independent projected columns and use the translation gauge to
set their heights to zero. Fix the remaining positive height scale by one
parent four-bracket, whose sign is fixed and nonzero on X. The nonempty
height domain is then an open convex polyhedron.

If A has no loop, there are eight heights, three translation gauges, and
one scale gauge. Its dimension is four. If A has a loop e, the lift of that
column lies on p and its independent positive column scaling fixes its
height. There are seven remaining heights. Three translation gauges and the
residual positive height scale leave dimension three. In this case use a
parent bracket excluding e to fix the scale. Such a bracket is nonzero by
uniformity; brackets including e already have their signs fixed by A and
the oriented loop lift.

The inequalities are strict in these affine coordinates. Hence every
nonempty fiber is a full-dimensional open convex three- or four-manifold,
not a lower-dimensional slice. Each fiber is connected. On mapping its
lifts back to the original parent-frame normalization, its entire image lies
in one parent realization component. Thus restricting to the chosen X
selects whole fibers and does not truncate a fiber into disconnected pieces.

## 5. Simultaneous badness saturates these fibers

Fix I in Z. By item 2 above, A_I has rank two. Let n_I be a fixed nonzero
normal to its two-plane in the projected three-space. Then its full derived
normal has the form

    a_I(Y) = L_I(h) (n_I,0),                       (3)

where L_I is linear in the heights. Choose a parent label j outside that
two-plane; it exists because A has rank three. The four-bracket on I union
{j} is, up to the fixed ordering sign,

    L_I(h) n_I(A_j).

The second factor is fixed and nonzero; the first bracket has a fixed
nonzero parent sign. Therefore L_I is everywhere nonzero and has constant
sign on the whole height fiber. Between two heights, every zero-triple
normal in (3) changes by a positive scalar.

Now take any block sigma. If it is bad, a nonzero nonnegative Gordan
dependence exists. Pairing this dependence with the common weak p gives a
sum of nonnegative terms equal to zero. Every positive witness coordinate
therefore belongs to Z. Conversely, any positive dependence among the
sigma-signed zero-triple normals is a full Gordan witness. Positive diagonal
rescaling of those normals preserves the existence of every such dependence.
Thus badness of every block is constant on the full height fiber.

The weak inequalities outside Z depend only on the projected determinant
signs, hence only on A. Those on Z remain equalities. The exact-Z incidence
stratum is therefore fiber-saturated: over a projected A it contains either
the entire parent height cell from section 4 or nothing.

## 6. Compact-support vanishing and gluing

On each exact-Z stratum the contraction map into that ambient base is
semialgebraic. Its fibers are empty or open convex d-manifolds, where d is
three or four. Fiber compact-support
cohomology vanishes in every degree q<=2. Base change for the shriek direct
image therefore gives

    R^q f_! Q = 0 for q<=2.

The compact-support Leray spectral sequence is in nonnegative base degrees,
so H_c^q of the exact-Z stratum vanishes for q<=2. No constant orientation
local system is needed for this low-degree conclusion. In particular no
unproved global section of the contraction map is being used.

The finite closed filtration of section 2 now gives the same vanishing for
J_S. Equation (2) proves (1).

## 7. A natural reduction of the original three-block map

For an actual three-signature family, put W=W_{012}, T=I_{012}, and
A_ij=B_i intersect B_j. W is a common closed subset of all four spaces and
has H_c^q(W;Q)=0 for q=0,1,2. Closed/open localization supplies natural
isomorphisms

    H_c^q(A_ij minus W;Q) -> H_c^q(A_ij;Q),
    H_c^q(T minus W;Q)    -> H_c^q(T;Q),       q=0,1,2.

These are extension-by-zero isomorphisms. They commute with restriction to
the triple locus, by the open/closed Cartesian square. Consequently the
original alternating restriction map is conjugate to

    direct_sum H_c^1(A_ij minus W;Q) -> H_c^1(T minus W;Q),
    (x01,x02,x12) -> r01(x01)-r02(x02)+r12(x12).

Its kernel is unchanged. The original triple H_c^0 obligation is likewise
unchanged by deleting W. The exclusive-pair strata themselves remain the
same, since (A_ij minus W) minus (T minus W)=A_ij minus T.

This rigorously removes the common-weak locus from both original remaining
obligations. It does not prove that their complements have vanishing
cohomology. Actual strictly infeasible triple-bad points are known outside
W, so replacing the whole triple locus by this weak-primal resolution would
be incorrect.

## Audit status

The complete proof received independent line-by-line acceptance from
/root/referee, including the projected-frame count, loop and nonloop height
dimensions, parallel projections, fiber saturation, the proper comparison,
the finite closed filtration, and natural excision. The requested distinction
between strict-system infeasibility and a trivial weak-primal cone was fixed.
No original diagonal is claimed. Source assumptions are the actual derived-normal/Gordan
model and the normalized parent geometry in the authenticated checkpoint.
The proof does not depend on Tsukamoto's blanket contractibility statement,
the 8,902 pair-wall certificate, or any triple-factor census.
