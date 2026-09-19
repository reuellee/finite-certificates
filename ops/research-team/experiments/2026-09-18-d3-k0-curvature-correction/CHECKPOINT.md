# K=0 curvature correction and complete guarded slice exclusion

18 September 2026, America/Los_Angeles.

**Original 9DVL ledger: 2/9. Zero whole source orbits closed.**
The stronger auxiliary factor-wall route remains a sufficient route, not a
proved universal theorem. The partial K=0 curvature conjecture proposed in the
preceding conversation is false. The full stationary maximum route is not refuted.

Source: `(5563,4373,23221)`, also `(5563,16134,19284)`.
Starting GitHub commit: `f9e065ca0f02205513d0647d55d5d2ddd4be033b`.
Branch: `research/d3-critical-geometry-20260910`.

## Verified recovery

[Complete recovery snapshot](https://drive.google.com/file/d/1uBoUO26CtY91iMygeN-m2huAgiqISpNb/view)
contains the proof, source-bound exact checkers, independent standard-library
checker, exact counterexample, full integer eliminants, discovery records and
the unchanged Original Target Reset predecessor archive. That predecessor retains
the intervening full-stationary and earlier checkpoints.

- Filename: `9DVL_K0_Curvature_Correction_2026-09-18.zip`.
- Bytes: `10986852`.
- SHA-256: `cb62f751dc46139276742364fda1effa9ffc27f00190d7456b3b5608ad5d303c`.
- ZIP integrity and all 31 payload hashes passed.
- The unchanged predecessor's 24 payload hashes passed.
- Fresh extraction passed all three mathematical replays.
- Uploaded ZIP, proof and report were downloaded and matched byte for byte.

[Full proof](https://drive.google.com/file/d/1Qf0CMtha-mixgj6FHJEEPzTrulWyuQ6C/view)
and [report](https://drive.google.com/file/d/1D16NsIDp-eDnht7zRtJ-Sy_B50paO-bm/view)
state all assumptions and limits. Executable scripts and large coefficient data
are in the archive, not duplicated in this note. Sharing permissions are unchanged.
This is a research snapshot, not a full Git-history bundle.

## 1. Exact source and remaining stationary domain

The source JSON hash is
`f0261c6e52b5bc2df61a8278926bb80cba9823f1e489b46574ff486ce4696388`.
The checkers reconstruct

    Y = [[0,0, 0,1,1,1,   1,   1],
         [0,1, 1,0,0,B,   C,   D],
         [1,0,-1,0,A,0,-1-C,-1-D],
         [0,0, 1,0,u,v,   w,   t]].

All 70 original parent brackets must be nonzero. The four-normal supports are
P:123/145/246/378, Q:126/257/367/458, R:157/168/245/348. P vanishes identically.
Set r=(At+u)/D and z=(w-u)/C. The source gives

    Q=D q, q=a2 C^2+a1 C+a0,
    R=C p/A^2, p=b2 D^2+b1 D+b0,
    f=a1^2-4a2 a0, g=(b1^2-4b2 b0)/(A^2 u^2),
    K=B(A-r)+u.

Here g is a discriminant, not the older curvature with the same symbol.
Remaining nonflat stationary candidates satisfy

    f=g=0, tau f_x-g_x=0 for x in {A,u,v,r,z},
    a2*b2*f_z*g_z!=0.

Recover C=-a1/(2a2), D=-b1/(2b2), tau=g_z/f_z,
j=tau*C*a2*u^2/(D*b2), w=Cz+u and t=(Dr-u)/A. Check all original brackets.
Possible full-source B maxima also require tau<0, eta=tau*f_B-g_B>=0 and the
full four-by-four N positive semidefinite, with all 15 principal minors. Eta=0,
B=D and C=D remain in scope. The inherited flat-q branch is excluded from extrema;
this note does not assert that flat-q stationary points do not exist.

## 2. The proposed partial curvature conjecture is false

At A=B=1 set n=k^2-2, T=k^2-4 and

    u=-n/T, r=1+u=-2/T, v=1+L,
    z=1-u-L(k-2)^2/n.

These coordinates satisfy K=g=0 identically and retain the guards k*L*n*T!=0.
The source pullback is f=F(k,L)/(T^6*n^2), with F an integer polynomial of
bidegree (16,6), containing 108 terms.

The new exact point is the unique root of F=F_L=0 in a rational box with
coordinate radius 10^-30, centered at rational approximations beginning

    k=-0.04445630500895926332033458969360017543...
    L=-1.36654499459596918865284559396576127618...

The certificate JSON supplies the complete rational center and preconditioner.
Both exact replays prove contraction strictly into the box, with norm bound
below 8.247e-25 and invertible preconditioner. Source reconstruction proves
Q=R=0, all 70 parent brackets nonzero, f_z*g_z!=0 and partial tangency

    g_z*f_v-f_z*g_v=0.

Define kappa_f=f_vv*f_z^2-2*f_vz*f_v*f_z+f_zz*f_v^2. Exact interval bounds give

    -23.249 < tau < -23.248,
    -7.100e-7 < kappa_f < -7.099e-7,
     1.650e-5 < N_vv < 1.651e-5,
     60.767 < tau*f_r-g_r < 60.769.

The minimum absolute original parent bracket exceeds 0.000275 throughout the
box. On K=0 the inherited identity is N_vv=tau*kappa_f. Thus the conjecture
that negative partial multiplier forces positive kappa_f is refuted on a genuine
uniform parent. The nonzero r-stationarity residual proves this point is NOT
fully stationary. It is not a maximum, a compact component, or a 9DVL counterexample.

## 3. A complete positive slice theorem

**Theorem.** No remaining nonflat full-source B-stationary candidate satisfying
all reconstruction guards has A=B=1 and K=0. Together with the inherited flat-q
extrema exclusion, no maximum of B on a component of the full source can lie on
that slice. No orientation-equality case is deleted.

A=B=1 is an actual restriction on moduli, not a normalization of arbitrary
parents. The theorem concerns extrema on the full source and then restricts
their possible locations; it does not claim that B varies on a B=1 slice.

Full stationarity implies F=F_k=F_L=0. Excluding this weaker necessary system
is sufficient; accepting a solution of only that system as fully stationary
would not be justified. Compute the exact integer resultants

    R1=Res_L(F,F_L), R2=Res_L(F,F_k).

Their degrees are 176 and 180. The supplied coefficient identities give

    R1=G*U1, R2=G*U2,
    G=k^11*(k-2)^48*(k-1)^5*(k+2)^35*(k^2-3)^2*(k^2-2)^5.

U1,U2 have degrees 63 and 67. Their leading coefficients stay nonzero modulo
101 and their reductions are coprime. Therefore their integer Sylvester
resultant is nonzero modulo 101, hence nonzero over Q. This is a valid
univariate characteristic-zero coprimality certificate, not a multivariate
modular unit-ideal inference. Every common root of R1,R2 must be a root of G.

The guards exclude k=0, k=2, k=-2 and k^2=2. All remaining values are handled:

- At k=1, F=(3L+4)^2*H1, where
  H1=81L^4+270L^3+837L^2+732L+196 has nonzero discriminant
  922502939738112. Thus F=F_L=0 forces L=-4/3. Reconstruction gives
  u=v=-1/3 and the forbidden parent bracket [1256]=0.
- Modulo k^2-3, F=L^2*H3, where the supplied H3 has no repeated root in either
  embedding. Its derivative resultant has field norm
  188291004161502191026176, which is nonzero. Hence F=F_L=0 forces L=0,
  so v=B and the original parent bracket [1346]=0.

Every admissible possibility is excluded, including unbounded k,L and both
signs of sqrt(3). No assumed zero-dimensionality or sampled-root completeness
is used. This proves the guarded slice theorem, not the full source theorem.

## 4. Independent replay and limits

The standard-library checker reconstructs all 73 determinant polynomials and
both discriminants. It independently verifies the two resultant identities by
364 literal fixed-size Sylvester determinants at distinct integer k values,
using proved degree bounds 176 and 186. These finite interpolation checks prove
polynomial identities; they are not sampled sign evidence. It checks integer
factorizations, degree preservation modulo 101, coprimality, exceptional values,
root contraction, all parent signs and the omitted stationarity residual.
It rejects five corrupted certificates/data cases. The primary point checker
rejects three corruptions. These are independent arithmetic implementations,
not independent mathematical peer review or formal topology verification.

An 80-start targeted full-stationary numerical search accepted no candidates.
That search earns no emptiness or maximum-exclusion credit. Failed exploratory
executions and their corrections are recorded in the report.

From a fresh extraction:

    python verify_payload.py
    python cycle/verify_k0_counterexample.py
    python cycle/verify_slice.py
    python cycle/verify_independent.py

Hash checks precede scripts that rewrite replay outputs. SymPy is needed only
by primary checks; the independent checker uses Python's standard library.
No compiled executable is distributed. The predecessor archive is unchanged.

## Remaining obligation

The arbitrary-A,B K=0 maximum locus remains open, as do K!=0, the full singular
eta=0 problem, and the source critical-value polynomial. A finite list of good
slices cannot replace parameter-uniform coverage. The original triple-wall,
exclusive-pair injectivity and diagonal-three conclusions are not proved.
The conservative inherited remainder remains 1,162,302 source records, not
components. The original theorem ledger remains 2/9.
