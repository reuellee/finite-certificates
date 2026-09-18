# An admissible real B-stationary saddle and a corrected maximum target

18 September 2026. Canonical source (5563,4373,23221), also named
(5563,16134,19284). Original 9DVL ledger: **2/9**. No source orbit is closed.
The fully parent-localized stationary-emptiness shortcut is false. The whole
survivor's noncompactness and both original diagonal-three obligations remain open.

## 1. Authenticated source and notation

The source chart is pinned by SHA-256
`f0261c6e52b5bc2df61a8278926bb80cba9823f1e489b46574ff486ce4696388`.
The previous published source is commit
`f7c73f00c2990f20baffa93977c146b55909ebd3` on
`research/d3-critical-geometry-20260910` in reuellee/finite-certificates.

Use coordinates theta=(A,B,C,D,u,v,w,t) and the parent matrix

```
Y = [0 0  0 1 1 1   1      1  ]
    [0 1  1 0 0 B   C      D  ]
    [1 0 -1 0 A 0  -1-C   -1-D]
    [0 0  1 0 u v   w      t  ].
```

The checker reconstructs all 70 four-column determinants of Y. It reconstructs
P,Q,R from the four normal rows for supports
P=123/145/246/378, Q=126/257/367/458, R=157/168/245/348.
P vanishes identically. Every parent bracket remains strictly nonzero.
Let Delta be the product of their 61 authenticated distinct irreducible factors.
No B=D or C=D branch is excluded. All original normalization exceptions remain
part of the larger source-coverage obligation.

Write L=R_w and U=Q_B. The source identities
L=-[1468][3458] and U=[1267][2458][2357] make these parent units.
The previously proved Qt identity shows that j=1/k is legitimate at every
genuine B-stationary parent. Set

    F_x = j Q_x - R_x,  x in {A,C,D,u,v,w,t},
    I = <Q,R,F_A,F_C,F_D,F_u,F_v,F_w,F_t>,
    nu = j Q_B - R_B.

Every hypothetical compact connected component supplies a B-maximum satisfying
these equations. This is a necessary condition, not an equivalence between
stationarity and compactness.

## 2. Exact real root certificate

There is a unique real zero of these nine equations in the closed rational box
specified by STATIONARY_WITNESS.json, with radius 10^-12 in every coordinate.
For orientation only, its coordinates are approximately

```
A = -0.483370536864927677641912851365
B = -0.129466430153343631210829972525
C = -0.366408339938349513044894152339
D =  0.0799692602928185912529966159902
u =  0.979340550400505555723095649340
v =  1.09293091995994354499324726070
w =  0.592290903310348578456756297887
t =  1.59450762436334807415711651196
j = -1.97099451965021958046141284058.
```

The decimals displayed above do not assert a rational root. The exact object is
the isolated real algebraic zero specified by the polynomial system and rational
isolating box.

Proof certificate. Let c be the stored rational center, X its box, and Y0 the
stored rational inverse approximation. The checker evaluates every Jacobian
entry on X using closed rational interval arithmetic. For T(x)=x-Y0 F(x), it
checks the induced infinity-norm derivative bound

    ||I-Y0 J_F(X)||_infinity < 4.429 * 10^-7 < 1

and the strict row-by-row self-mapping inequalities

    |(Y0 F(c))_i| + rho * sum_j sup |(I-Y0 J_F(X))_ij| < rho.

The maximum center correction is less than 4.814 * 10^-55. The determinant of
Y0 is checked nonzero exactly. Therefore T is a strict contraction of the box
into its interior, with a unique fixed point; that fixed point is a zero of F.
All comparisons establishing this are rational comparisons. The numerical
root search and refinement are discovery steps only.

Every one of the 70 bracket intervals excludes zero on the entire box. The
sign list is saved. L, U, j, and nu also have nonzero interval enclosures, with
nu positive. Thus this is a point of the fully parent-localized real stationary
locus, not another forbidden-boundary example.

Consequently I:Delta^infinity is proper. No identity with a nonzero product of
parent factors on the left and an I-combination on the right can exist: evaluation
at this root would give a nonzero number equal to zero. This refutes that entire
algebraic emptiness certificate target, over the reals as well as the complex
numbers. It does not refute 9DVL or prove a compact component exists.

## 3. The point is a genuine saddle of B

Define two polynomial vector fields with zero B component,

    V = AD partial_D + (At+u) partial_t,
    W = C partial_C + (w-u) partial_w.

The source identities V(Q)=AQ and W(R)=R hold identically. On Q=R=F_x=0,
both vector fields are tangent to both walls. Set

    H = j Hess_theta(Q) - Hess_theta(R).

Since nu is nonzero at the certified point, the two wall gradients are
independent: j grad Q-grad R=nu e_B, while R_w is nonzero. In particular,
Q_B R_w-Q_w R_B = (R_w/j) nu is nonzero. The wall intersection is smooth and
B is a smooth function of the other six coordinates locally.

For a tangent vector X, differentiation along a curve in the intersection gives

    Hess_Z(B)(X,X) = - X^T H X / nu.

Exact interval calculations at the certified algebraic root give

    0.0557412698 < Hess_Z(B)(V,V) < 0.0557412701,
   -0.0096646542 < Hess_Z(B)(W,W) < -0.0096646531.

Thus B both increases and decreases along local curves through the point.
It is neither a local maximum nor a local minimum. This is a certified saddle
of the coordinate objective on the whole local triple intersection, not just
an indefinite matrix evaluated at an unrelated numerical point.

## 4. Global curvature identities valid on every admissible stationary point

Define

    h = -2 B C u^2 (A+1)(A+u),
    Xi = (B+u-v)(At+u) + D u(B+1),
    g = 2 j (A+1)(u-v) Xi.

Exact polynomial identities, checked by expansion, are

    V^T H V - h
      = 2A(AD F_D + (At+u)F_t - j A Q) + 2A^2 R,

    W^T H W - g
      = 2C F_C + 2(w-u)F_w + 2R - 2jQ,

    V^T H W
      = A C F_C + A(w-u)F_w + A R - j A Q
        + AD F_D + (At+u)F_t.

Therefore the restriction to span(V,W) is diag(h,g) on the stationary locus.
Every factor B,C,u,A+1,A+u is an authenticated parent unit. In particular,
**h never vanishes on the genuine stationary domain**. By contrast, no
nonvanishing assumption is made about Xi, g, nu, B-D, or C-D.

Whenever h*g<0, the constrained quadratic form is indefinite on these two
directions. Such a point cannot be a B-maximum of a compact component, including
when nu=0. At the certified witness h<0 and g>0.

A further exact provenance identity for T0=W(Q) is

    L T0 = Q_w (C F_C + (w-u) F_w + R) - T0 F_w.

This places T0 in the localization using the authenticated unit L, without
an unexplained division by the reciprocal multiplier.

## 5. Why the singular case is retained

The identity h!=0 does NOT prove nu!=0. At nu=0 the two wall gradients can be
dependent, so it is not legitimate to use a regular constrained-Hessian test
alone or simply discard that branch.

Eliminate w using R_w!=0 and write f=Q on that graph, with remaining coordinates
(B,x), x=(A,C,D,u,v,t). At a stationary point f_x=0. At nu=0, f_B=0 too.
The restriction of H to the fixed-B tangent space is j times Hess_x(f).
If this restricted form is indefinite, choose fixed x-directions with opposite
strict quadratic signs. At B=B(p)+epsilon^3 and x=x(p)+epsilon e_+ or
x(p)+epsilon e_-, Taylor expansion gives opposite signs for f for sufficiently
small positive epsilon. The intermediate value theorem produces zeros with
B>B(p) approaching p. The domain is semialgebraic and locally path connected,
with finitely many connected components; sufficiently nearby zeros lie in the
same component as p. This contradicts maximality on that component.

Thus at a singular B-maximum the restricted form must be semidefinite. Since
its V diagonal h is nonzero, its semidefinite sign is fixed by h.
This proves the two-direction exclusion h*g<0 for both regular and singular
points. It does not assert that a semidefinite point is a maximum.

## 6. A complete necessary maximum filter with a five-by-five Schur matrix

Let T_x = L e_x - R_x e_w for x in {A,u,v,t}. On the stationary domain the
ordered list (V,W,T_A,T_u,T_v,T_t) is a basis of the six-dimensional fixed-B
tangent space to the R wall. It is a basis because AD,C,L are nonzero. Every
vector in it is also tangent to Q at the stationary point.

In this basis write the H matrix as

        [ h   b^T ]
    M = [ b    C0 ].

Define the polynomial symmetric five-by-five matrix

    K = h C0 - b b^T.

No division is required. A B-maximum must satisfy

    Q=R=F_x=0,  all original parent conditions,
    nu*h >= 0,  K positive semidefinite.                 (MAX)

For nu!=0, Hess(B)=-M/nu is negative semidefinite at a maximum. Because h!=0,
nu*h>0 and h*M is positive semidefinite. For nu=0, Section 5 gives h*M positive
semidefinite, and nu*h=0. The Schur complement of the strictly positive entry
h^2 in h*M is exactly K, proving the necessary condition. Its W diagonal is
h*g, recovering the inexpensive two-direction filter.

A proof that (MAX) is empty on every original residence would rule out compact
components of this authenticated source. No such emptiness proof is asserted.
A genuine maximum, if later found, still would not prove the component compact;
a global escape or component-coverage argument could remain necessary.

The next computation should first apply the low-degree filters nu*h>=0 and
h*g>=0, retaining nu=0 and g=0. Only survivors need the rest of the Schur test.
K's complete positive-semidefinite condition is not equivalent to testing only
leading principal minors. The recipe above is a proved reduction; this cycle
does not claim an expanded global K census or a completed real solver run.

## 7. Additional algebra and scope

The invertible parent-unit change r=(At+u)/D, z=(w-u)/C makes
Q=D*q(C) and R=C*gq(D)/A^2. The checker reconstructs both quadratic identities;
q is independent of D, and gq is independent of C. The constant term of gq is
B u^2(A+1)(A+u), which is nonzero on the genuine domain. The expanded polynomials
are supplied in LOWER_CHART.json. This is a structural representation, not a
measured end-to-end solver speedup.

The original semidefinite set S from the height-critical reduction is different
from the B-maximum target in this note. Neither H_c^0(S)=0 nor full triple
noncompactness is established here. The inherited remainder stays 1,162,302
source records. It is not a component count. Original ledger stays 2/9.

Separate Fraction arithmetic checks the raw normal determinants and all 16 first
derivatives at the rational center. Negative controls reject a zero inverse,
a displaced center, an undersized box, a wrong curvature sign, and an interval
zero divisor. These are arithmetic and implementation checks, not independent
mathematical peer review. The full mathematical claims are the displayed proofs
and exact replayable certificates.
