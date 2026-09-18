# Zero-curvature exclusion and a reduced maximum problem

18 September 2026. Canonical source (5563,4373,23221), also named
(5563,16134,19284). Starting GitHub commit:
`37e6d0f05ea9c3ab0633fc101188aa3f8f56972f`.
Original ledger: **2/9**. No source orbit is closed.

## 1. Scope and result

Work in the complete inherited P-contraction chart, with all 70 original parent
brackets strictly nonzero, every represented parent sign residence retained, and
no removal of B=D or C=D. The frozen source SHA-256 is
`f0261c6e52b5bc2df61a8278926bb80cba9823f1e489b46574ff486ce4696388`.
The source matrix, Q,R and all brackets are reconstructed by the checkers.

Write theta=(A,B,C,D,u,v,w,t), Z={Q=R=0} in an original open residence,
F_x=j Q_x-R_x for x other than B, L=R_w, and nu=j Q_B-R_B.
The inherited parent identities give L!=0, Q_B!=0 and j!=0 on the genuine
stationary domain. In particular the reciprocal stationary formulation includes
every possible B-maximum. Let

    H = j Hess_theta(Q) - Hess_theta(R),
    V = AD partial_D + (At+u) partial_t,
    W = C partial_C + (w-u) partial_w,
    h = -2 B C u^2 (A+1)(A+u),
    g = 2j(A+1)(u-v)[(B+u-v)(At+u)+Du(B+1)].

The preceding exact identities, replayed here, give V^T H V=h!=0,
W^T H W=g and V^T H W=0 on the stationary set.

**New theorem.** Every genuine stationary point with g=0 is excluded from the
B-maximum and B-minimum loci. This includes nu=0. This is an all-point statement
on this entire algebraic branch, not a statement inferred from a finite sample.

Together with the previous hg<0 exclusion, every possible maximum must have
hg>0. This permits a second Schur pivot and a four-by-four PSD test. On this
remaining domain C,D,j can also be eliminated by justified nonzero pivots,
giving an equivalent six-variable stationary formulation with all original
parent conditions restored by rational reconstruction.

None of these results asserts emptiness of the remaining maximum locus,
noncompactness of the whole source, or original diagonal-three closure.

## 2. An invertible parent-unit chart and two quadratic equations

Set

    r=(At+u)/D,  z=(w-u)/C,
    t=(Dr-u)/A,  w=Cz+u.

A,C,D are authenticated parent units, so this is invertible on the whole
admissible domain. Exact reconstruction gives

    Q=D q(A,B,C,u,v,r,z),
    R=C p(A,B,D,u,v,r,z)/A^2,

where q is independent of D and quadratic in C, while p is independent of C
and quadratic in D. Write q=a2 C^2+a1 C+a0 and p=b2 D^2+b1 D+b0. Explicitly,

    a0=(A+1)(u-v) k0,
    k0=r(B+u-v)+u(B+1),
    a2=(z-1){z[A(r+v)-B(r+u)]+r(u-v)},
    b0=B u^2(A+1)(A+u).

All coefficients are supplied by the executable source reconstruction, rather
than being accepted as unchecked input. Additional exact unit identities are

    [2458]=-D(r+u),  [1357]=-C(z-1),
    [2357]=A+C-Cz+1,  p_z=A^2 R_w.

On a stationary point, V=AD partial_D and W=C partial_C in these coordinates.
The identities V(Q)=AQ and W(R)=R therefore imply p_D=q_C=0. Both q and p
also vanish there. Notice that h=-2C b0 and g=2jD a0. Consequently g=0 implies
a0=0, and q=q_C=0 with C!=0 then implies a2=a1=0 as well. This follows without
dividing by a2 from q-C q_C=a0-C^2 a2.

## 3. Complete treatment of the flat q branch

Assume a0=a1=a2=0 and all original parent units. From k0=0,

    B=-(r(u-v)+u)/(r+u).

The denominator r+u is a parent unit. Also r cannot vanish: otherwise k0=0
would force u(B+1)=0, and both u and B+1 are parent units.

Substitute the displayed B and define

    d=A r+A v+r u-r v+u,
    J=r(A+u-v+1)+A v+u,
    S=d z+r(u-v).

Because z-1 is a parent unit, a2=0 implies S=0. Let b be a1 after the same
B substitution. Exact polynomial arithmetic gives the division-free identity

    d b - b_z S = -r(u-v)(A+u-v) J.

The factors r, u-v and A+u-v are nonzero. Hence J=0. The identity
S=z J+r(u-v-z) now forces z=u-v.

Put delta=A+u-v+1. No delta=0 exception is discarded. Were delta=0, J=0 would
imply A v+u=0. Substituting A=v-u-1 gives
A v+u=-(u-v)(v-1). Since u-v!=0, v=1, after which delta=0 would imply A+u=0,
a forbidden parent boundary. Thus delta!=0, and every admissible flat-q point
has the exact parameterization

    r=-(A v+u)/(A+u-v+1),
    z=u-v,
    B=(A u v-A u-A v^2-u)/((A+u)(u-v)).              (FLAT)

Conversely, substitution verifies a2=a1=a0=0. This classifies the specified
flat-q branch subject to parent conditions, not the full stationary set or p.
All denominators above are justified; no sign sector has been selected.

## 4. A nonzero mixed curvature on both remaining cases

For base coordinates a,b in {A,u,v,r,z}, define, before making the FLAT
substitution,

    J_ab=q_a q_Cb-q_b q_Ca,
    Y_ab=q_a partial_b-q_b partial_a.

The vector Y_ab has zero B,C,D components and annihilates q. At a stationary
point jD dq=(C/A^2)dp on all fixed-B directions, so it annihilates p as well.
It is therefore tangent to both original walls. The Hessian change-of-coordinate
correction vanishes on fixed-B directions: j grad Q-grad R=nu dB and the chart
leaves B unchanged. Differentiating Q=Dq and R=Cp/A^2 consequently gives

    H(W,Y_ab)=jDC J_ab.

The terms involving dp(Y_ab) vanish. On the g=0 branch H(W,W)=0.

The following identities use partial derivatives taken BEFORE FLAT substitution:

    J_Ar|FLAT =
      -u(A+1)(C+1)^2(u-v)^2(v-1)(u-v-1)^2/(A+u).    (1)

All factors in (1), except v-1, are nonzero on this domain. In particular C+1
is the factor of [2467], and u-v-1=z-1 is nonzero by [1357]. Therefore v!=1
implies a nonzero mixed curvature H(W,Y_Ar).

The case v=1 is retained. FLAT then becomes

    r=-1, z=u-1, B=1/(1-u).

A second exact identity is

    J_uz = (-A+C u-2C-1)^2 = [2357]^2 != 0.         (2)

The rightmost equality holds on this case of FLAT. Thus H(W,Y_uz) is nonzero.

In either case, the quadratic form on span(W,Y) has a matrix

    [[0, m], [m, n]],   m!=0.

Its determinant is -m^2<0, so it has both positive and negative directions.
This proves indefiniteness on the fixed-B tangent space at every genuine
g=0 stationary point, not merely at regular points.

## 5. Why indefiniteness excludes extrema even when nu=0

Eliminate w using R_w!=0 and let f(B,x) be Q on the R graph, with six other
coordinates x. At a stationary point f_x=0. The fixed-B restriction of H is
j times Hess_x(f), so the indefiniteness just proved transfers to f.

If f_B!=0, the wall intersection is locally the graph B=b(x), and
Hess(b)=-Hess_x(f)/f_B at this point. Its indefinite Hessian prevents a local
maximum or minimum.

If f_B=0, choose x directions with strictly positive and negative quadratic
terms. At B=B(p)+epsilon^3 and x=x(p)+epsilon e_+ or x(p)+epsilon e_-, Taylor
expansion gives opposite signs of f for all sufficiently small epsilon>0.
The intermediate value theorem supplies zeros between those x values, with
B>B(p), approaching p. All strict parent inequalities persist nearby.
A semialgebraic set has finitely many connected components, each relatively
closed. Thus sufficiently nearby zeros lie in the same component as p.
This rules out a maximum on that component. Replacing +epsilon^3 by
-epsilon^3 rules out a minimum. This argument retains singular points;
no division by nu or generic-rank assertion is used.

This finishes the zero-curvature theorem.

## 6. Executed follow-through: a four-by-four maximum test

A compact component must supply a B-maximum. By the preceding result and the
previous hg<0 argument, every such maximum has hg>0. Let L=R_w and
T_x=L e_x-R_x e_w for x in {A,u,v,t}. The basis

    (V,W,T_A,T_u,T_v,T_t)

spans the fixed-B tangent space to R: the minor with rows (D,C,A,u,v,t) has
determinant AD*C*L^4!=0. At a stationary point all six vectors are also tangent
to Q. In this basis write

        [ h  0  a^T ]
    M = [ 0  g  b^T ].
        [ a  b   N  ]

At a possible maximum, nu*h>=0 and hM must be positive semidefinite. For nu!=0
this is the ordinary constrained second-derivative condition. For nu=0 it is
the necessary semidefinite condition from Section 5, with sign fixed by h!=0.
Since hg>0, eliminating the first two pivots is valid. The remaining condition
is exactly positive semidefiniteness of

    P4 = g^2 (h N-a a^T)-h g b b^T.                  (3)

Indeed the Schur complement in hM is hN-aa^T-(h/g)bb^T, and (3) is its product
with the strictly positive scalar g^2. The checker verifies the general
congruence exactly and constructs all source-specific a,b,N entries.

The necessary maximum target is now

    Q=R=F_x=0, all original parent conditions,
    hg>0, nu*h>=0, P4 positive semidefinite.         (MAX4)

P4 is retained as an arithmetic circuit to avoid unnecessary high-degree
expansion. A complete four-by-four PSD test uses all 15 nonempty principal
minors. Leading principal minors alone are not sufficient. No remaining
semidefinite degeneracy, nu=0, B=D or C=D branch is removed.

## 7. Executed follow-through: six-variable stationary reconstruction

On MAX4, a0!=0 since g=2jD a0; b0 is already a parent unit. The double-root
equations give a2 C^2=a0 and b2 D^2=b0. Thus a2,b2!=0, and

    C=-a1/(2a2), D=-b1/(2b2).

Define two polynomials in (A,B,u,v,r,z):

    Dq=a1^2-4a2 a0,
    Dp=(b1^2-4b2 b0)/(A^2 u^2).

The second quotient is a polynomial, verified exactly. At a double root,
differentiating 4a2 q=q_C^2-Dq and the corresponding identity for p yields

    q_x=-Dq_x/(4a2),
    p_x=-A^2 u^2 Dp_x/(4b2).

Set tau=j D b2/(C a2 u^2). The original fixed-B stationary equations become

    Dq=Dp=0,
    tau Dq_x-Dp_x=0 for x in {A,u,v,r,z}.             (CRIT7)

There is another justified pivot. The source identities give
p_z=A^2 R_w!=0 and D q_z=C Q_w!=0, the latter because jQ_w=R_w and j!=0.
Consequently Dq_z,Dp_z are nonzero at the relevant double roots, and

    tau=Dp_z/Dq_z.

Eliminating tau gives six equations in six variables:

    Dq=Dp=0,
    Dq_z Dp_x-Dp_z Dq_x=0 for x in {A,u,v,r}.         (CRIT6)

Recover C,D from above, followed by

    j=tau a2 C u^2/(D b2), t=(Dr-u)/A, w=Cz+u.

Conversely, any real solution of CRIT6 with these nonzero pivots and all 70
reconstructed parent brackets nonzero gives a genuine stationary point with
g!=0. The differentiated double-root identities and chart chain rule recover
all seven original F_x equations. Parent signs and normalization sectors must
be checked on this reconstruction, not replaced by an arbitrary subset.
The MAX4 inequalities are still required; CRIT6 alone does not characterize
maxima. No division by nu has occurred.

Dq has degree 8 and 248 terms; Dp has degree 6 and 78 terms. CRIT7 has maximum
degree 8. The four additional expanded CRIT6 equations have degree 12 and
2,376, 2,639, 2,423 and 2,293 terms. Fewer variables do not establish a solver
speedup or zero-dimensionality. Both formulations are supplied, with sparse
coefficients for the expanded six-variable version.

## 8. Evidence and remaining scope

The exact checkers reconstruct the source, verify the displayed identities,
authenticate every parent factor used in a division, replay the Schur congruence,
and reject deliberately corrupted identities. A separate implementation using
Python Fraction and permutation determinants checks ten rational instances of
the two mixed-curvature formulas. Those finite arithmetic checks are not the
universal proof and are not independent mathematical peer review.

A 160-start seven-variable numerical pilot recovered the existing certified
saddle and no new certified maximum. A separate 384-start original-system
screen also produced no new exact certificate. These are bounded discovery
experiments, not component counts or emptiness proofs.

The unresolved task is the global real resolution of MAX4, or a different
complete component-escape argument. The whole authenticated survivor,
H_c^0(S), original pair injectivity and original D3 remain open. The inherited
remainder remains 1,162,302 source records. No source closure or 3/9 promotion
is made by this note.
