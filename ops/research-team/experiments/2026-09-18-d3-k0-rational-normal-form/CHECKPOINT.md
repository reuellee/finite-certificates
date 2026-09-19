# Complete rational normal form for the remaining K=0 stationary problem

18 September 2026, America/Los_Angeles.

**Original 9DVL ledger: 2/9. Zero whole source orbits closed.**
This is a complete lower-degree reformulation, not a K=0 exclusion, a global
maximum classification, or original diagonal-three closure. The stronger
auxiliary route remains a sufficient route. The previously refuted partial
curvature conjecture remains refuted.

Source: `(5563,4373,23221)`, also `(5563,16134,19284)`.
Starting commit: `1840b2329ccb59f668e8be8748672286eaedb116`.
Branch: `research/d3-critical-geometry-20260910`.

## Verified recovery

[Complete archive](https://drive.google.com/file/d/1perDvTanYZtoJHH6NZkLBBZKfESqBCmT/view?usp=drivesdk),
[full proof](https://drive.google.com/file/d/1BxYqJhTqQCUmRIvulxEjcF-iPgC1j0Sq/view?usp=drivesdk),
and [report](https://drive.google.com/file/d/1zwwjjYpY4LnpXPnURK9vNE_m1ZZJFxZC/view?usp=drivesdk)
are in Projects/research-backups. Access follows the existing Drive permissions.
The executable checkers and integer coefficients are in the archive, not duplicated
in this GitHub checkpoint note. No sharing settings are changed.

- Archive: `9DVL_K0_Rational_Normal_Form_2026-09-18.zip`.
- Bytes: `11128376`.
- SHA-256: `c55ead90eed44e7a4a8eaff291c6949854381c3fcdaa910700f28c2051561eb4`.
- ZIP integrity and all 27 payload hashes passed.
- The unchanged predecessor's 31 payload hashes and its nested predecessor's
  24 payload hashes passed.
- Both new exact mathematical replays passed from a fresh extraction.
- Uploaded archive, proof and report were downloaded and matched byte for byte.

This is a research snapshot, not a full Git-history bundle. The old Drive LATEST
pointer is not replaced by this cycle; use this checkpoint and its archive.

## 1. Original source and guards

The authenticated source SHA-256 is
`f0261c6e52b5bc2df61a8278926bb80cba9823f1e489b46574ff486ce4696388`.
The matrix is

    Y = [[0,0, 0,1,1,1,   1,   1],
         [0,1, 1,0,0,B,   C,   D],
         [1,0,-1,0,A,0,-1-C,-1-D],
         [0,0, 1,0,u,v,   w,   t]].

The four-normal supports are P:123/145/246/378, Q:126/257/367/458,
R:157/168/245/348. P vanishes identically. All 70 original parent brackets
are nonzero, and original sign residences remain mandatory.

Set r=(At+u)/D, z=(w-u)/C and K=B(A-r)+u. The source gives

    Q=D q, q=a2 C^2+a1 C+a0,
    R=C p/A^2, p=b2 D^2+b1 D+b0,
    f=a1^2-4a2 a0, g=(b1^2-4b2 b0)/(A^2 u^2).

Full B-stationarity forces q=q_C=p=p_D=0. The inherited flat-q extrema
exclusion is retained. On the remaining nonflat domain, a2*b2*f_z*g_z!=0,
with tau=g_z/f_z and eta=tau*f_B-g_B. Full remaining stationarity is

    f=g=0, tau*f_x-g_x=0 for x in (A,u,v,r,z).

Maxima must also satisfy tau<0, eta>=0 and the full four-dimensional
discriminant curvature form positive semidefinite. All 15 principal minors
are retained. No eta=0 or original parent-sign case is deleted.

## 2. A complete rational replacement of the earlier K=0 chart

Define

    a=AB/u=(D-B)/(t-D), e=B+a,
    s=(Bt-Dv)/(B(t-D)), h=(D-B)/D,
    T=s^2-2(e+1)s+(e+1).

Here h is a NEW coordinate, not the older curvature with that symbol. The inverse is

    A=e*s^2/T,
    u=B*A/(e-B), D=B/(1-h),
    t=B*(e-B+h)/((e-B)*(1-h)),
    v=B+B*h*(1-s)/(e-B),
    r=A*(e-B+1)/(e-B),
    z=1-A/(e-B)+h*e*(e+1)*(s-1)/((e-B)*T),
    w=C*z+u.

C remains free before q=q_C=0. Source coefficient identities give

    b1=-2*b0*(1-h)/B, b2=b0*(1-h)^2/B^2,

so the formal quadratic p is b0*(1-D*(1-h)/B)^2. The reconstructed D gives
p=p_D=0. B,e,e+1,e-B,s,s-1,T,h,1-h are proved nonzero on the guarded domain.
For example [1348]=D-t, [1468]=Bt-Dv, [1346]=B-v, and
K=0 implies u(D-B)=AB(t-D). These establish the less obvious moving-column guards.

The complete predecessor chart used H0=A(A+1), n0=k^2-H0, T0=B*n0-H0.
The exact coordinate link is

    e=H0/n0, s=k/(k-A-1),
    h=L*(k-A-1)*T0/(B*n0*(A+1)).

The apparently exceptional k=A+1 case is not lost: the double-root coefficient
identities above hold before dividing by k-A-1 and would force D=B, then t=D,
a forbidden parent. Moreover

    T=(A+1)*k^2/(n0*(k-A-1)^2),
    k=s*(e+1)*(s-1)/T, L=B*h*(1-s)/(e-B).

Both coordinate compositions are verified exactly. This replaces the earlier
complete chart without restricting A=B=1 or selecting a real sign branch.

## 3. Lower-degree source polynomials and complete stationarity

Explicit integer polynomials P2,P1,P0 satisfy

    q=-e*s^2*(e+1)/((e-B)^3*T^4) * (P2*C^2+P1*C+P0),
    P1^2-4*P2*P0=B^2*T^2*F.

They have 152, 284 and 202 terms. On the guarded nonflat branch,
F=0 and C=-P1/(2*P2), P2!=0, recover q=q_C=0. The reconstructed C and
all other original parent brackets must still be checked.

F has 1,550 terms and total degree 20, versus 6,428 terms and degree 30 in
the preceding complete exceptional chart. Its h-degree is six, with coefficient
B^2*e^2*(s-1)^6*T^2>0. Thus that sextic has no guarded degree-drop stratum.

Put U=e+1-s and V=h*(s-1)-s. Differentiating before substitution gives

    s^2*p_r=U*V*p_z,
    s^2*q_r-U*V*q_z=-s^2/((e-B)^2*T^3)*(M2*C^2+M1*C+M0),
    2*M2*P0-M1*P1+2*M0*P2=B^2*T^2*G.

At the double roots G=0 is equivalent to q_r-(p_r/p_z)*q_z=0.
G has 1,999 terms and total degree 21, versus 10,187 terms and degree 35 in
the old normal polynomial. It retains the indispensable derivative transverse
to K=0 within g=0.

The (e,s,h) directions span the fixed-B tangent space to g=K=0, and
W_r=g_z*partial_r-g_r*partial_z is tangent to g=0 with dK(W_r)=-B*g_z!=0.
Together these span the four-dimensional fixed-B tangent space to g=0.
Consequently the COMPLETE stationary system is equivalent to

    F=F_e=F_s=F_h=G=0,

with all guards, f_z*g_z!=0, reconstructed original brackets and signs. This
argument imposes no eta!=0 condition and is not just partial tangency.

An optional equivalent normal equation is

    J=B*e^2*s+B*e^2-2*B*e*s^2+5*B*e*s-B*e
      +B*s^3-4*B*s^2+5*B*s-2*B+e^2+e,
    G4=6*B*e*(s-1)*(G-U*F)+J*F_h.

G4 has h-degree four, 2,492 terms and total degree 22. On F=F_h=0 its nonzero
multiplier makes it equivalent to G=0. Its quartic leading coefficient is not
assumed nonzero. These are smaller explicit inputs, not a proved solver speedup.

## 4. Necessary maximum filters without discarding singular points

The old discriminant restricts to f=Omega*F, where

    Omega=B^2*e^2*s^4*(e+1)^2/((e-B)^6*T^6)>0.

At full stationarity, the chain rule along the B coordinate on g=0 gives

    eta=tau*Omega*F_B.

On tau<0, the original orientation condition is therefore equivalent to F_B<=0.
Equality corresponds exactly to eta=0 and is retained. On the three tangent
coordinates (e,s,h), the curvature pullback is

    pullback[tau*Hess(f)-Hess(g)]=tau*Omega*Hess_(e,s,h)(F).

Thus a possible maximum requires the three-by-three Hessian of F to be negative
semidefinite, including all seven principal minors of its negative. This is only
a necessary subspace test. The full four-by-four test and its normal mixed
entries remain required. No actual maximum or emptiness conclusion follows.

## 5. Replay and limits

From a fresh extraction run:

    python verify_payload.py
    python cycle/verify_normal_form.py
    python cycle/verify_independent.py

Hash checks precede scripts that regenerate logs. The primary checker reconstructs
the source, verifies the identities and inverse chart, and rejects five corrupted
coefficient inputs. The independent standard-library checker reconstructs all 73
determinant polynomials, performs exact sparse coefficient arithmetic, and rejects
three corruptions. It imports neither SymPy nor the producer. These are independent
arithmetic implementations, not independent mathematical refereeing or formal
topological verification.

A portable 20-second modular F5B replay did not return a completed basis. Its input
omits parent localization and maximum inequalities. A remote lower-degree attempt
returned HTTP 502. Neither attempt provides a rational certificate or real census.
No modular unit conclusion is used for acceptance. Failed expression expansions
and dependency installation attempts are recorded in the report.

The complete K=0 maximum locus is OPEN, as are K!=0, other source records, original
triple-bad Hc0 and exclusive-pair injectivity. No whole source or diagonal is closed.
The conservative inherited remainder stays 1,162,302 source records, not components.
The next target is the guarded real system with tau<0, F_B<=0 and the full curvature
condition, or a complete alternative source escape. Merely adding successful slices
or sampled saddles cannot establish the universal claim.
