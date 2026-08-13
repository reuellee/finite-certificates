# Third diagonal: corrected Gale hard-canary no-go

## Outcome

Gale duality is a biregular involution of the uniform `Gr(4,8)` quotient, but
it does **not** turn the six pinned hard factor triples into any of the small
affine/unit certificate families currently used on diagonal three.  Across
all `40,320` simultaneous `S8` frames of the six triples, the exact audit finds

```text
241,920  transformed hard-canary rows
      0  jointly affine three-coordinate blocks
      0  triangular sequential unit graphs
      0  modular survivors among 20,321,280 coordinate Jacobian minors
      0  modular survivors among 365,783,040 decomposable minor sums
```

The last two zeros are rigorous **necessary-filter no-go results** for a
Jacobian minor equal to a nonzero scalar times a product of parent brackets.
They are not ideal-saturation calculations and do not exclude more general
polynomial combinations, nonconstant vector fields, or boundary-aware Gale
roadmaps.

This note proves no triple-factor noncompactness theorem.  In particular, it
does not change the `1,819,789` unresolved count or the honest `2/9` score.

## 1. Why bare Pluecker complementation is wrong

The displayed primitive residual identities such as

\[
 q_{49}=[1234][1357]-[1246][2357]
\]

hold in the fixed nine-coordinate normalization.  Their two monomials do not
even have the same column multidegree.  Thus they are not homogeneous
functions on the column-scaled Grassmannian.  Replacing each bracket by its
complement in such a formula omits the column-renormalization scalars and need
not preserve the residual zero set.

This is not a technical caveat.  Direct exact tests on all six canonical wall
centers put the true residual factor at zero while the naively complemented
polynomial stays nonzero.  No theorem or certificate in the repository uses
that invalid substitution.

## 2. Correct homogeneous pullback

Write the standard parent chart as

\[
                         M=[I_4\mid A].
\]

An unnormalized Gale kernel matrix is

\[
                         N=[-A^T\mid I_4],
                         \qquad MN^T=0.                 \tag{1}
\]

The verifier checks (1) as a polynomial identity.  For each primitive factor
`f`, choose one of its certified full residual occurrences `E_f` and evaluate

\[
 R_f(M)=\det(n_{T_1}(N),n_{T_2}(N),n_{T_3}(N),n_{T_4}(N)),
 \qquad E_f=(T_1,T_2,T_3,T_4).                          \tag{2}
\]

Equation (2) is column-multihomogeneous before the standard chart is imposed.
The global occurrence theorem says its value on a normalized Gale chart is a
primitive factor times parent-bracket units.  Under Gale duality those units
pull back to complementary parent brackets, which are nonzero on every
uniform parent cell.  Consequently stripping exact parent-bracket factors
from (2) preserves precisely the pullback zero set.  This avoids every
renormalization ambiguity in the naive formula.

The construction is independent of the selected certified occurrence:
any two occurrences of one localized factor differ only by parent-bracket
units, and Gale sends those units to complementary parent-bracket units.
Thus the stripped pullback zero locus, and hence its factor index, is
well-defined on the uniform parent cell.  Since this is only a bounded
no-go audit, no signature or chirotope transport is asserted here.

The exact corrected census has

```text
26,740  pullback polynomials
25,620  with no stripped parent factor
 1,120  with one stripped parent factor
637,044 total sparse terms
```

Its polynomial-database digest is

```text
9b508dcbcadca9029d86866844ef33698ab256d2aeea37f63fadaf2bad802f50
```

## 3. The bounded canary screens

The six sources are

```text
(2277,390,22507)     (5563,16134,19284)
(12985,16183,7196)   (20355,5442,5949)
(9667,16486,26315)   (9758,24338,15810)
```

Their simultaneous `S8` images are disjoint and give exactly `241,920` rows,
with digest

```text
fd688604376a65eddc8adac7dd1f1ad8bbc82444e3499e2ee7bf551f91d5da38
```

### Square affine and triangular graphs

For every corrected pullback, the verifier recomputes all `84` coordinate
three-block affinity bits.  There are `26,128` factors carrying at least one
bit and `429,696` bits in total, but none of the `241,920` canary rows has a
common bit.

It also differentiates all `26,740 x 9` factor/coordinate pairs exactly.
Every recorded unit derivative is divided into a signed product of the 62
nonconstant parent brackets.  The pinned feature digest is

```text
5b510bb9aeb0229e7ab201b2cab8abef910d3b8c9dbb3f762eca729ed8bd0d56
```

No canary row has a three-stage triangular unit graph.

### Coordinate and decomposable-plane minors

At seven deterministic non-parent points modulo the Mersenne prime
`2^31-1`, the 62 parent logarithmic gradients have rank 62 in 63 sampled
coordinates.  The verifier constructs their one-dimensional annihilator.
Any nonzero scalar product of parent brackets must have zero logarithmic
derivative along this annihilator.  It therefore must survive the modular
test.

The L1 derivative bound is `96`.  A coordinate `3 x 3` Jacobian minor has
coefficient bound at most `6*96^3`, and a sum or difference of two minors has
bound at most `12*96^3`, both strictly below the prime.  Thus a nonzero scalar
cannot vanish merely by reduction modulo the prime.  Zero modular survivors
rigorously excludes the tested parent-unit identity family; no probabilistic
inference is made.

The decomposable planes tested are all sums and differences of coordinate
three-minors whose coordinate triples share two axes.  This is the complete
sparse constant-shear family used by the previous diagonal-three screen, not
the full real Grassmannian of constant three-planes.

## 4. Replay and scope

Run the compact polynomial and square-affine replay with

```bash
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/verify_diag3_triple_gale_canary_no_go.py --fast
```

Run every screen with

```bash
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/verify_diag3_triple_gale_canary_no_go.py --workers 9
```

The companion OpenMP source is
`verify_diag3_triple_gale_canary_no_go.cpp`.

The conclusion is deliberately narrow:

\[
 \boxed{\text{corrected Gale + S8 does not close the six hard canaries by
 the tested affine/unit families}.}
\]

It does not rule out a boundary-stratified Gale argument or another Coble/Weyl
transformation.  Any such argument must retain all auxiliary divisors instead
of treating them as parent boundary automatically.
