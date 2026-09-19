# Full stationary continuation and finite regular critical values

18 September 2026, America/Los_Angeles.

**Original 9DVL ledger: 2/9. Zero whole source orbits closed.**
The full negative-multiplier maximum locus remains unresolved, including K=0,
K!=0 and the singular orientation-equality locus. This checkpoint does not
promote a numerical search, a new saddle, or a generic unit ideal to source closure.

Source: `(5563,4373,23221)`, also `(5563,16134,19284)`.
Starting commit: `77618cc5e67073c8e525a63e45808742dea73929`.
Branch: `research/d3-critical-geometry-20260910`.

## Verified recovery

[Complete recovery archive](https://drive.google.com/file/d/1_1adbMENitdOg3zJAd8f6-6yyHbZXTBM/view)
contains the proof, full source-bound checkers, exact root certificate, exact
elimination inputs, discovery scripts and logs, and the unchanged complete
exceptional-conic predecessor archive. Drive access follows existing permissions.

- Filename: `9DVL_Full_Stationary_Critical_Values_2026-09-18.zip`.
- Bytes: `10777250`.
- SHA-256: `a01bc1cb6f4f6c00ccb6fea6e4c2b3c3d7ae1b276e502fcd62386e6932ef7974`.
- ZIP integrity and all 56 payload hashes passed.
- A fresh extraction restored and checked all 92 predecessor payload hashes.
- Both exact root checkers, the two-root audit and critical-value arithmetic
  checker passed from the fresh extraction.
- The uploaded ZIP, proof and report were downloaded and matched byte for byte.

[Full proof](https://drive.google.com/file/d/1oJxwRcH1OngCcTBQKVne38idz9E9bdWE/view)
and [report](https://drive.google.com/file/d/1Ixo5f3XO9cBBr_dxJ4GXZ7SqlTLQj_do/view)
provide the detailed mathematical arguments and executed limitations. The
executable scripts and large rational data are in the archive, not duplicated
in this note. This is a research snapshot, not a full Git-history bundle.

## 1. A second exact full stationary saddle

Use the authenticated chart

    Y = [[0,0, 0,1,1,1,   1,   1],
         [0,1, 1,0,0,B,   C,   D],
         [1,0,-1,0,A,0,-1-C,-1-D],
         [0,0, 1,0,u,v,   w,   t]].

All 70 original parent brackets remain strict. The source hash is
`f0261c6e52b5bc2df61a8278926bb80cba9823f1e489b46574ff486ce4696388`.
The actual four-plane supports are

    P: 123,145,246,378
    Q: 126,257,367,458
    R: 157,168,245,348.

The new certificate defines a unique real root of all nine original equations

    Q=R=0,
    j Q_x-R_x=0, x in {A,C,D,u,v,w,t}.

The exact definition is its rational box and contraction certificate, not
these approximate coordinates in order (A,B,C,D,u,v,w,t,j):

    (-0.7638618910846606,  2.1333133923118535,
      0.3154974854441029,  0.9170673049388551,
     -1.4783455107011516,  2.3563840120997592,
     -1.6044989563737755,  2.2994227699248735,
      0.1760399053819474).

Every exact coordinate radius is 10^-24. Rational interval arithmetic proves
that x-Y0 F(x) contracts this box strictly into its interior. The independent
replay's contraction bound is below 1.233*10^-20. All 70 parent brackets,
R_w, j and nu=j Q_B-R_B have strict signs throughout the box.

For H=j Hess(Q)-Hess(R), let

    V=AD partial_D+(At+u) partial_t,
    W=C partial_C+(w-u) partial_w.

The exact identities V(Q)=A Q and W(R)=R, together with full stationarity,
make V and W tangent to both walls. At the certified point

    H(V,V)>0, H(W,W)<0, nu>0,

with approximate values 1.5576659054, -0.4003558567 and 2.1080736895. Since
R_w!=0 and nu!=0, the wall intersection is smooth there. Differentiating
Q=R=0 twice along a wall curve gives nu B''=-X^T H X. Thus B has increasing
and decreasing local directions: this is a saddle, not a maximum or minimum.

The inherited curvature identity implies tau>0 at this root. It therefore
lies OUTSIDE the remaining tau<0 maximum target. Its orientation eta is
positive, showing that full stationarity and orientation alone do not imply
maximality. No assertion is made that an accepted predecessor proof claimed
such sufficiency. This root is a full-system diagnostic, not new maximum
exclusion credit.

The old and new B boxes are disjoint. Their signed parent vectors differ in
24 entries in this fixed chart. This does not classify them up to reorientation,
relabeling or projective equivalence, and is not a global stationary census.

## 2. Finite regular critical values without finite stationary fibers

Let f,g be polynomials in Q[B,x_1,...,x_m], set

    p_i=tau f_(x_i)-g_(x_i), eta=tau f_B-g_B.

Then the ideal

    (f,g,p_1,...,p_m,y eta-1)

is the unit ideal over Q(B). Consequently a nonzero polynomial P(B) vanishes
at every regular stationary B-value, even when its stationary fiber has
positive dimension. This is a standard-algebra deduction, not a novelty claim.

Proof: If the ideal were proper, a maximal ideal above it would have residue
field L finite algebraic over Q(B), by the finite-residue-field form of the
Hilbert Nullstellensatz. In characteristic zero, d/dB extends to L. For an
algebraic generator alpha with minimal polynomial h(T)=sum a_i T^i, the
extension satisfies D(alpha)=-sum D(a_i)alpha^i/h'(alpha); separability makes
the denominator nonzero. Differentiating f=g=0 in L yields

    0=tau D(f)-D(g)=eta+sum_i p_i D(x_i)=eta,

contradicting y eta=1. Thus the ideal is unit. Clearing the finitely many
Q(B) coefficient denominators in a unit identity gives

    0!=P(B)=a_f f+a_g g+sum_i a_i p_i+a_y(y eta-1).

Evaluation at any regular stationary point, with y=1/eta, gives P(B)=0.
This proves finiteness of values, not finiteness of points or absence of maxima.
The field-theoretic input is [Stacks, Theorem 10.34.1](https://stacks.math.columbia.edu/tag/00FV).

For the source, use f=d_q,g=d_p,x=(A,u,v,r,z), or apply the lemma directly to
Q,R,x=(A,C,D,u,v,w,t), multiplier j and parameter derivative nu. Both exact
inputs are supplied in REGULAR_VALUE_INPUT.json. No source P(B), explicit
unit multipliers or complete fiber census was obtained in this cycle.

A generic unit result must retain every zero of the cleared denominator
polynomial and check its original real fiber. The eta=0/nu=0 locus is not in
this generic calculation and remains a separate part of the original target.

The exact canary f=x^2-B+z, g=z has

    B=-f+g+(x/2)(2 tau x)-x^2(tau-1).

Its only regular critical B-value is zero, but x=z=0, tau=1 allows arbitrary
additional coordinate w. This explicitly prevents confusing finite values
with finite fibers. A separate eta=0 canary has stationary points for every B.
An inseparable characteristic-five canary records why the proof cannot simply
be transferred to a modular field.

## Checks, failures and scope

The first root verifier reconstructs every source polynomial and proves exact
contraction, original parent signs and tangent curvature. A separate Python
standard-library verifier uses independent Fraction interval and sparse
coefficient arithmetic, reconstructs all 73 determinant polynomials, and checks
their center values. It imports neither SymPy nor the first verifier nor the
predecessor interval library, and rejects two corrupted certificates.

The two-root audit replays both roots, proves the B boxes disjoint and rejects
four corruptions. The critical-value checker verifies the source chain-rule
identity and scope examples, and rejects three corrupted identities. The
universal field argument is the written proof, not an inference from canaries.
These are arithmetic implementation cross-checks, not independent mathematical
peer review or proof-assistant certification of the original topology.

Completed 600- and 2,400-start full-system numerical searches found the same
two admissible candidate clusters. Neither search is exhaustive; numerical
absence earns no maximum-exclusion credit. The 600-start run also regenerated
from the fresh archive and reproduced both clusters. A K=0 partial-curvature
screen suggested a sign pattern, but no universal K=0 identity was proved.

The discriminant regular-value Groebner attempt over Q(B) returned $Aborted
at its 20-second bound. Original-system regular-value and earlier K=0 attempts
returned HTTP 502. No source basis, critical-value polynomial, multiplier
identity or dimension result was returned. These failures are not mathematical
truth or falsity evidence.

## Replay and unresolved obligation

From a fresh archive extraction:

    python verify_payload.py
    python restore_predecessor.py
    python verify_full_root.py
    python verify_fraction_full.py
    python audit_roots.py
    python verify_critical_values.py

Restore before running acceptance scripts. Hashes are checked before replay
scripts regenerate logs. The unchanged predecessor archive is bundled.

The complete negative-multiplier stationary/maximum locus remains open,
including all original parent conditions, orientation equality, all 15 PSD
principal minors, and the K=0 transverse equation G_perp. The generic K!=0
maximum locus is also open. The next finite-value proof object requires an
explicit verified P(B) identity, all exceptional B fibers, and a separate
singular-locus argument, or a different complete escape theorem.

No whole source is closed. Universal triple-wall noncompactness and original
D3/exclusive-pair injectivity are unproved. The inherited remainder stays
1,162,302 source records, not components. The theorem ledger stays 2/9.
