# Exceptional conic continuation, 18 September 2026

**Original 9DVL ledger: 2/9. Zero whole source orbits closed.**

Source: `(5563,4373,23221)`, also `(5563,16134,19284)`.
Starting branch commit: `de731fcfc024a7eb25eda92d1eeace775048e00c`.
This checkpoint records a complete rational treatment of the retained K=0
conic exception, not exclusion of its stationary or maximum locus.

## Checked recovery snapshot

[Full recovery archive](https://drive.google.com/file/d/15cAX8wJmdoiN-lk6hHlmz-JwM8SyA-js/view)
contains the proof, exact checkers, sparse equations, exact partial-tangency
certificate, discovery records and unchanged complete predecessor snapshot.
Drive access follows the owner's existing permissions; no sharing change was made.

- Filename: `9DVL_Exceptional_Conic_Checkpoint_2026-09-18.zip`.
- Bytes: `10639072`.
- SHA-256: `b12c48b1453a4c0ad5db34227bbc0557cecae059c46d51b0da2943813420070e`.
- Uploaded bytes were downloaded and checked against that hash.
- ZIP integrity and all 92 payload hashes passed; both exact checkers passed
  again after fresh extraction.

[Full proof note](https://drive.google.com/file/d/15qPph8B16R5RRfFQWmrmpyULIQM0nqEe/view?usp=drivesdk)
and [report](https://drive.google.com/file/d/17dzJ4E-KlQtjMH2JOH5ksiIp_qZFZ-zy/view?usp=drivesdk)
state the complete assumptions and limits. Executable scripts and the large
derived coefficient files are in the recovery archive, not duplicated in this
GitHub checkpoint note. This is not a full Git-history bundle.

## Source and discriminants

Use the authenticated complete P-contraction chart with all 70 original
parent brackets nonzero and every original sign residence retained. Its source
SHA-256 is `f0261c6e52b5bc2df61a8278926bb80cba9823f1e489b46574ff486ce4696388`.
Set r=(At+u)/D and z=(w-u)/C. The source gives

    Q=D q, q=a2 C^2+a1 C+a0,
    R=C p/A^2, p=b2 D^2+b1 D+b0,
    f=a1^2-4a2 a0,
    g=(b1^2-4b2 b0)/(A^2 u^2).

Here g is the discriminant d_p, not the earlier curvature with the same name.
The remaining possible B extrema obey f=g=0 and

    tau f_x-g_x=0, x in {A,u,v,r,z}.

The preceding negative-multiplier proof is retained in the archive. It requires
tau<0, tau f_B-g_B>=0 and the full four-by-four discriminant Hessian matrix N
positive semidefinite. All 15 principal minors remain required, including the
nu=0 and other semidefinite cases. B=D and C=D are not removed.

## Exact conic-curvature filter

Put U=(A+1)(A+u)(r+u), K=B(A-r)+u, L=v-B, and define

    D0=B(r-A),
    M=A^2+Ar+2Au+A+u,
    c0=A^2B-ABr+ABu+AB-Bru-Br+ru+u^2,
    S=M+(D0 z+c0)/L.

D0 and L are parent units. Source coefficient identities give

    g=L{L(S^2-4AU)-4UK},
    g_z=2D0 L S,
    det(M_g)=-4B^2(A-r)^2 U^2 K^2,

where M_g is the homogeneous conic matrix in (v,z,1). For
kappa_g=g_vv*g_z^2-2*g_vz*g_v*g_z+g_zz*g_v^2, the quadratic identity yields

    kappa_g=32B^2(A-r)^2 U^2 K^2 on g=0.

At partial (v,z) tangency, N_vv=tau*kappa_f-kappa_g/tau^2. Therefore a genuine
maximum must satisfy

    tau^3*kappa_f >= 32B^2(A-r)^2 U^2 K^2.

This forces kappa_f<0 off K=0 and kappa_f<=0 on K=0. It is a necessary filter,
not a replacement for the remaining stationary equations or matrix conditions.

## A rational neighborhood of the entire exceptional branch

On K=0 put H=A(A+1), k=S/[2(A+u)], n=k^2-H and T=Bn-H. The conic equation gives

    u T=-AB n.

T cannot vanish: it would force n=0, after which T=-H!=0. Likewise n cannot
vanish because uT!=0. Also k!=0 follows from S^2=4AU!=0. Thus all displayed
denominators are justified parent units or proved nonzero consequences.
Every genuine K=0 conic point has the rational coordinates

    u_*=-ABn/T,
    r_*=A+u_*/B,
    v_*=B+L,
    z_*=1-u_*/B-AL(k-A-1)^2/(Bn).

Both signs of k and L are retained. To preserve the missing transverse
stationary equation, set epsilon=K and define

    H_e=(A+1)(A+epsilon/L),
    T_e=Bk^2-H_e(B+1),
    u_e={H_e(AB-epsilon)-ABk^2}/T_e,
    r_e=A+(u_e-epsilon)/B,
    v_e=B+L,
    S_e=2(A+u_e)k,
    z_e={-c0_e+L(S_e-M_e)}/(u_e-epsilon).

M_e,c0_e are the source formulas at u_e,r_e. At epsilon=0 the denominators
T_e and u_e-epsilon equal the proved units T and u_*. The exact conic equation
reduces to the linear equation defining u_e. The rational inverse is

    epsilon=B(A-r)+u, L=v-B, k=S/[2(A+u)],

with A,B unchanged. This is a genuine rational neighborhood in g=0, not just
a parametrization restricted to the exceptional hypersurface.

For Phi=f(A,B,u_e,v_e,r_e,z_e), full fixed-B stationarity is equivalent, with
f_z*g_z!=0, to

    Phi=Phi_A=Phi_k=Phi_L=Phi_epsilon=0.

At epsilon=0, exact denominator clearing gives five polynomial equations

    F=F_A=F_k=F_L=G_perp=0

in four variables (A,B,k,L). F has 6,428 terms and degree 30; G_perp has 10,187
terms and degree 35. G_perp is the transverse derivative and cannot be dropped.
All original reconstruction guards and maximum inequalities remain mandatory.
Five equations in four variables do not prove inconsistency or zero-dimensionality.

## Certified failure of a stronger partial shortcut

An exact real-algebraic point has A=-7/4, B=3/2, u=-2 and approximately

    (r,v,z)=(2.04529732825921180,-1.30682026597117631,-1.73684473677197838).

A rational contraction certificate proves f=g=g_z*f_v-f_z*g_v=0 in its
10^-15-radius box, with all 70 reconstructed parent brackets nonzero. Exact
interval bounds imply

    -4.039689 < tau < -4.039688,
    1235.85002 < N_vv < 1235.85003,
    336.32640 < tau*f_r-g_r < 336.32642.

Thus negative partial multiplier and positive tested curvature can coexist on
an actual parent. The last inequality proves this is NOT fully B-stationary.
It refutes only an overstrong partial-curvature shortcut, not the full maximum
route, original 9DVL, or any component-escape theorem.

## Replay and remaining gap

After extracting the complete snapshot:

    python verify_payload.py
    python verify_atlas.py
    python verify_partial.py

The atlas checker passed 102 exact checks and rejected five corrupted inputs.
The root checker passed exact contraction and parent-sign tests and rejected
two corrupted certificates. A separate clean minimal-input generation replay
also passed. These are arithmetic checks, not independent mathematical peer
review or proof-assistant certification.

A reproducible 96-start numerical pilot produced no admissible full stationary
candidate. Thirty-six small scaled residuals were rejected by pivot/coordinate
or unscaled-equation checks. A 25-second modular Groebner attempt returned
$Aborted. Neither experiment is a completeness or emptiness result.

The K=0 stationary/maximum problem remains open in its now-complete rational
coordinates; the K!=0 maximum problem is also open. No whole source orbit has
been closed. The conservative inherited remainder is still 1,162,302 source
records, not components. Universal triple-wall noncompactness and the original
D3/exclusive-pair endpoint are not proved. The original ledger stays 2/9.
