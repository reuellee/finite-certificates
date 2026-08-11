# Diagonal three: tapered ribbon and tangential-shift audit

## Outcome

The exact two-dimensional tapered normal-slice ribbon does not close the
pair obligation.  Its cellular census is

```text
base:  (V,E,F) = (4547,13734,9188)
T:               (370,740,370)
E01:            (1515,3048,1533)
E02:            (2613,7342,4728)
E12:              (49,228,179)
```

Over `F2`, the three exclusive-pair cohomology dimensions in degrees
`0,1,2` are respectively

```text
E01: (0,0,0)    E02: (0,1,0)    E12: (0,0,0).
```

The balanced complex has

```text
N: 12098 x 4917, rank 4917
M:  7180 x 12098, rank 7180
```

and hence one middle class.  Both ranks are already maximal over `F2`, so
the same ranks hold over `Q` and the rational middle dimension is also one.
The checker pins a signed integral representative on 242 edges: the initial
`q0=0,q1>0` wall edge and the 241 upper factor half-edges on
`q1=0,q0<0`, terminating at factor `13063`.

This is a theorem about the covered two-dimensional normal slice.  It is not
an ambient counterexample: seven tangential directions can shift or fill the
class.  Conversely, the presently known local product charts do not prove
that they do.

## 1. What a tangential shift would prove

Let `X` be a locally compact semialgebraic set with a finite closed
filtration

\[
 \varnothing=F_{-1}\subset F_0\subset\cdots\subset F_m=X,
 \qquad S_i=F_i\setminus F_{i-1}.
\]

If `H_c^0(S_i;R)=H_c^1(S_i;R)=0` for every `i`, then the compact-support
closed/open long exact sequence proves inductively that

\[
                         H_c^0(X;R)=H_c^1(X;R)=0.       \tag{1}
\]

In particular, (1) holds when every `S_i` is a locally trivial
`R^{r_i}`-bundle with `r_i>=2` over a semialgebraic Hardt stratum.  The
compact-support fiber cohomology is concentrated in degree `r_i`; a possible
orientation local system does not create degrees zero or one.  No global
trivialization, and no single disk bundle across different strata, is
needed.

Thus an exhaustive, frontier-compatible Whitney--Hardt filtration whose
pieces carry the seven-dimensional tangential shift would close the
individual `H_c^1(E_ij)` terms.

## 2. Why the current local charts do not imply (1)

Local dimension and Whitney regularity alone do not control compact-support
ends.  A sharp smooth semialgebraic countermodel is

\[
                         X=S^7\times\mathbb R.          \tag{2}
\]

Every point of (2) has a neighborhood `R^7 x interval`, but

\[
 H_c^1(X;\mathbb Q)
 \cong H^0(S^7;\mathbb Q)\otimes H_c^1(\mathbb R;\mathbb Q)
 \cong\mathbb Q.                                      \tag{3}
\]

The required node model can also be marked without changing (3).  In
coordinates `(u,s,t)` on

\[
 S^7\times\mathbb R
 =\{(u,s,t):u\in\mathbb R^7,\ |u|^2+s^2=1\},
\]

the regular hypersurface

\[
 t(1-s)=1+s                                             \tag{4}
\]

is the closed proper stereographic graph

\[
 y\longmapsto
 \left(\frac{2y}{1+|y|^2},
       \frac{|y|^2-1}{1+|y|^2},|y|^2\right)
\]

and is semialgebraically homeomorphic to `R^7`.  It has a two-sided local
`interval x R^7` model.  Additional transverse marked walls and split
coincidences can be inserted in a coordinate chart; they do not alter (3).
Hence the proved generic ray charts, `R^7` node charts, and local splitting
data do not force ambient `H_c^1` vanishing.

The exact factor audit reinforces this logical point.  The 39 coincident
factor parameters split immediately in tangential directions: among 53
factor pairs there are zero tangencies.  Therefore the one-dimensional star
does not presently extend as one common product over all seven tangential
directions.

## 3. Minimal next certificate

Either of the following is sufficient and properly scoped.

1. An exhaustive proper Whitney--Hardt filtration of each ambient `E_ij`,
   including exceptional tangential fibers and parent infinity, whose
   locally closed pieces satisfy the degree-zero and degree-one vanishings
   in (1).  Stratumwise `R^7` bundles are a convenient stronger certificate.
2. A finite relative cellular model of the ambient `E_ij` through degree
   two, with an exact full-rank or unit-Smith certificate for
   `ker d^1 / im d^0`.

A local tubular chart, a normal-slice ribbon, or a Hardt partition without
fiber and exit data is not enough.

## Replay

```console
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/verify_diag3_pair_tapered_ribbon.py
```

The replay ends with an explicit scope line excluding any ambient
tangential theorem.
