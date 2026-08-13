# Third diagonal: concurrence normal form and its exact frontier

## Outcome

The current diagonal-three endpoint consists of `1,819,789`
union-degree-four factor-triple orbits after the exact triangular,
role-frame unit-minor, and frame-1119 constant-plane sweeps.  This note gives
a theorem-safe normal form for their generic concurrence stratum and records
two exact no-go results:

1. the fixed-base four-bilinear projection has an internal real corank-one
   ramification point in a
   uniform parent cell, so it is not a universal unramified cover; and
2. at that point exactly the selected three residual factors vanish among all
   `26,740` factors, so fiber ramification does not universally force a
   fourth-factor exchange.

The normal form compresses a presentation to four equations in ten
variables and a generic fixed-base fiber of complex length at most six.  It
does **not** prove component noncompactness.  Auxiliary concurrence-rank,
affine-gauge, interpolation, and projective-boundary strata remain capable of
joining the finite sheets.  In this precise sense the construction relocates
rather than closes the `1,819,789`-orbit endpoint.

The dependency-free branch replay is

```bash
python ai/omreal/verify_diag3_concurrence_normal_form.py
```

It checks the support ranks and verifies that the stored CAS-produced
degree-20 rational-univariate branch satisfies all twelve incidence equations
and the ramification identity.  It also checks the stored polynomial's six
real roots, all `70` parent brackets at the chosen ramification point, the rank-three fiber
Jacobian, and a rigorous all-factor interval separation.  It does not replay
the saturation computation or certify completeness of the saturated ideal.

## 1. Determinants are concurrence equations

Let `P_1,...,P_8` be homogeneous parent points in `P^3`.  For a support
triple `T={a,b,c}`, write

\[
 n_T=*(P_a\wedge P_b\wedge P_c)\in (\mathbb R^4)^* .
\]

For an occurrence `E=(T_1,T_2,T_3,T_4)`, its full determinant equation is

\[
 D_E=\det(n_{T_1},n_{T_2},n_{T_3},n_{T_4})=M_Eq_f,       \tag{1}
\]

where `M_E` is a product of parent brackets and is a unit in a uniform
parent cell.  Linear algebra gives

\[
 D_E=0
 \quad\Longleftrightarrow\quad
 \exists [x_E]\in\mathbb P^3:
 n_{T_s}(x_E)=0\quad(s=1,2,3,4).                            \tag{2}
\]

Thus the four occurrence planes concur projectively.  If their covector
rank is three, `x_E` is unique.  At rank at most two the common locus is a
projective line or plane; this rank drop is part of the frontier, not a
choice of a unique concurrence point.

Choose one occurrence for each factor and denote concurrence points by
`x_1,x_2,x_3`.  On the open stratum

\[
 \operatorname{rank}(x_1,x_2,x_3)=3,
 \qquad
 h_j=\det(x_1,x_2,x_3,P_j)\ne0\quad(1\le j\le8),           \tag{3}
\]

a projective reframe sends the three points to `e_1,e_2,e_3`, and parent
column scaling by `h_j^{-1}` gives

\[
 P_j=(u_j,v_j,w_j,1).
\]

The incidence equation for a support triple `abc` is then a planar
collinearity determinant:

\[
\begin{aligned}
 x_1\in\langle P_a,P_b,P_c\rangle
   &\Longleftrightarrow C_{abc}(v,w)=0,\\
 x_2\in\langle P_a,P_b,P_c\rangle
   &\Longleftrightarrow C_{abc}(u,w)=0,\\
 x_3\in\langle P_a,P_b,P_c\rangle
   &\Longleftrightarrow C_{abc}(u,v)=0,
\end{aligned}                                               \tag{4}
\]

where

\[
 C_{abc}(y,z)=
 (y_b-y_a)(z_c-z_a)-(y_c-y_a)(z_b-z_a).                     \tag{5}
\]

Equations (2)--(5) are identities, not generic dimension heuristics.

## 2. Four bilinear equations in ten variables

The six primitive occurrence support types have representatives

| kind | four support triples |
|---:|---|
| `36` | `123/124/345/367` |
| `38` | `123/124/345/678` |
| `48` | `123/145/246/356` |
| `49` | `123/145/246/357` |
| `50` | `123/145/246/378` |
| `51` | `123/145/267/468` |

For fixed generic `u`, the four equations `C(u,z)=0` of every row have
rank four.  The checker exhibits a nonzero rank-four specialization at

```text
u=(2,3,5,7,11,13,17,19),
```

which proves generic rank four because there are only four rows.

On an additional affine-gauge chart normalize

\[
 u_1=v_1=w_1=0,
 \qquad
 u_2=v_2=w_2=1.                                             \tag{6}
\]

Use the color-two equations to solve four of the remaining `w` coordinates
and the color-three equations to solve four `v` coordinates.  Each kernel
has four parameters before (6), hence two afterward.  The surviving
coordinates are

\[
 (u_3,\ldots,u_8,v_r,v_s,w_r,w_s)\in\mathbb R^{10}.         \tag{7}
\]

The four color-one equations are affine-bilinear in
`(v_r,v_s)` and `(w_r,w_s)`, with rational functions of the six `u`
coordinates as coefficients.  After fixing `u` and projectivizing the two
affine fiber planes, the four equations are divisors of bidegree `(1,1)` in
`P^2 x P^2`.  A proper zero-dimensional complex fiber therefore has length
at most

\[
 [H_v^2H_w^2](H_v+H_w)^4=\binom42=6.                        \tag{8}
\]

This is a fiber-degree bound on the chart.  It is not a six-sheeted global
cover theorem: a fiber can be nonproper, acquire a positive-dimensional
piece, or meet one of the frontiers below.

## 3. Exact generic-chart ramification

Take the selected occurrences

```text
factor  5563: 123/145/246/378
factor 16134: 126/257/367/458
factor 19284: 245/157/348/168
```

and the rational base slice

\[
 u=(0,1,4/5,-3/4,3/20,1/4,1/3,t).                          \tag{9}
\]

With free coordinates `(v_r,v_s)=(v_7,v_8)` and
`(w_r,w_s)=(w_7,w_8)`, exact interpolation gives

\[
\begin{aligned}
v={}&\left(0,1,
 \frac{315tv_r-360t-252v_r+527v_s+288}{85(4t+3)},
 \frac{9(7v_r-8)}{68},\frac{9v_r}{20},\frac{v_s}{4t},v_r,v_s\right),\\
w={}&\left(0,1,\frac{33w_r-7}{5},
 \frac{204tw_r-44t+153w_r-144w_s-33}{8(20t-3)},
 \frac{51w_r-11}{40},\frac14,w_r,w_s\right).               \tag{10}
\end{aligned}
\]

Let `F_1,...,F_4` be the primitive numerator polynomials of the four
remaining incidences and let

\[
 R=\det\frac{\partial(F_1,F_2,F_3,F_4)}
                   {\partial(v_r,v_s,w_r,w_s)}.              \tag{11}
\]

CAS elimination after saturating the construction by `[1234]` and by
`t(4t+3)(20t-3)` produced a degree-20 RUR.  The checked data file stores the
degree-20 elimination polynomial and the four coordinate
parametrizations

\[
 \xi(t)=-\frac{P_\xi(t)}{d_\xi E'(t)},
 \qquad \xi\in\{v_r,v_s,w_r,w_s\}.                           \tag{12}
\]

Direct pseudo-remainder arithmetic verifies `F_i=R=0` modulo `E`.  This
proves the stored branches but does not independently replay saturation or
prove that the RUR is complete.  A Descartes
partition of the whole real line proves that `E` has exactly six distinct
real roots, one in each interval

```text
(-1/2,-1/4)  (-1/50,-1/100)  (0,3/1000)
(1/10,2/5)   (7/10,1)        (2,3).
```

The ramification point used here is narrowly isolated by

\[
 t\in
 [7879209203118614/10^{16},
  7879209203118616/10^{16}].                                 \tag{13}
\]

At this root, rigorous rational interval arithmetic gives

```text
vr = -0.19918615935098...
vs = -0.20160217122091...
wr =  0.18281515029306...
ws =  0.34045732156583...
```

and proves:

* all twelve incidences (4) vanish exactly;
* all `70` parent brackets are nonzero, with smallest interval margin greater
  than `0.00126104`;
* the fiber determinant (11) is exactly zero; and
* a displayed `3 x 3` fiber-Jacobian minor lies in
  `[0.559641...,0.559642...]`.

The fiber Jacobian therefore has rank exactly three.  This is an internal
real ramification point in the independent-concurrence, `h_j != 0`, uniform
parent chart.  It rules out a universal fixed-`u` submersion and a universal
unramified-cover argument.

The pinned RUR semantic digest is

```text
fad0e330d2502e6a95f2cbc365409ecb96e37f5c44ac603f51c3564348b885db
```

## 4. No fourth factor at the ramification point

The checker also converts the exact rational enclosures of the eight parent
points to outward `96`-bit dyadic intervals.  It constructs all `56` plane
normals and evaluates one occurrence determinant for each of the `26,740`
primitive residual factors.  Exactly three determinant intervals contain
zero:

```text
5563   occurrence (0,7,14,52)
16134  occurrence (10,27,32,44)
19284  occurrence (8,26,40,45)
```

Every other interval excludes zero.  Equation (1) and the already verified
nonzero parent brackets turn this into a rigorous statement about primitive
factors at the selected real root.  Consequently an internal fiber-rank drop
does **not** universally force a fourth residual factor whose wall could be
used for factor exchange.

The semantic digest of all `26,740` factor intervals is

```text
f6132b7058b7cd2747e37979ef094a678e93d5c9e417a5821fd22de2d5858923
```

## 5. Exact status of the frontier

The reduction in Section 2 is valid only where every operation used to
construct it is invertible.  The omitted loci are genuine geometric strata:

| locus | meaning | current status |
|---|---|---|
| `rank(x_1,x_2,x_3)<=2` | concurrence points cannot be reframed to three coordinate points | may attach generic sheets; no escape theorem |
| some `h_j=0` | a parent point lies in the auxiliary concurrence hyperplane | not a parent-bracket wall in general |
| occurrence-normal rank `<=2` | an occurrence has a concurrence line or plane rather than a unique point | the lift has a projective fiber; not an automatic noncompact parent motion |
| a gauge difference in (6) vanishes | the chosen affine normalization fails | another chart may apply, but global attachment is unproved |
| an interpolation minor vanishes | a four-row kernel chart changes rank or pivot set | may create positive-dimensional fibers or sheet attachments |
| projective fiber boundary | a solution of the `(1,1)^4` compactification leaves the affine chart | may land on any of the preceding auxiliary loci |

None of `h_j=0`, concurrence-rank drop, or interpolation-rank drop is forced
to be a parent inequality becoming equality.  Parent-cell sign constancy
therefore does not remove these strata.

There is one useful exact shared-edge warning.  Suppose the two occurrences
used as the linear `v`- and `w`-kernel systems share a support triple
`abc`.  Then

\[
 C_{abc}(u,v)=C_{abc}(u,w)=0.                                \tag{14}
\]

Unless `u_a=u_b=u_c`, both `v` and `w` are affine functions of `u` on those
three labels, so `P_a,P_b,P_c` are collinear.  Every parent bracket containing
those three labels vanishes, contradicting parent uniformity.  Thus a
uniform solution in that role must lie on the auxiliary frontier
`u_a=u_b=u_c` or use a different color role.  A generically invalid
shared-edge chart is not evidence that the original factor-triple stratum is
empty.

Positive-dimensional fibers do not by themselves finish the argument:
real algebraic curves can have compact oval components.  Likewise the even
generic degree six in (8) has no useful real parity consequence.  Boundary
solutions may be nonreal, and a real even-sheeted branched cover may have
compact components.

## 6. Mixed-minor diagnostic (sampled, not a theorem)

The strongest direct Morse screen in the reduced model uses the `4 x 10`
Jacobian.  There are

```text
C(10,4) = 210
```

distinct four-column minors.  For one prescribed Morse base coordinate
`u_k`, `C(9,4)=126` minors exclude that column.  Across the six base
coordinates this is `6*126=756` tagged tests, with the same four-column set
appearing under more than one Morse tag.

A deterministic diagnostic sampled `1,000` rows from the then-live
`1,819,850`-row pre-constant-plane residue and tested all three choices of
which color supplies the four bilinear coupling equations.  For each valid
interpolation chart, a modular logarithmic-derivative annihilator tested
whether any minor could be
a product or ratio of the allowed chart units:

```text
70 parent-bracket numerators
27 nonconstant u-coordinate differences
 2 interpolation determinants
```

The modulus was `1,000,000,007`.  The result was

```text
3000 color-role presentations
2855 generically uniform interpolation charts
 145 shared-edge-invalid role charts
   0 unit-compatible minors in every valid chart
```

Every sampled row had at least one valid color role.  The six hard canaries
also had zero survivors among all `210` minors.  The role patterns were

| valid/invalid role pattern | rows |
|---|---:|
| `(0,0,0)` | `872` |
| `(0,0,invalid)` | `46` |
| `(0,invalid,0)` | `39` |
| `(invalid,0,0)` | `26` |
| `(0,invalid,invalid)` | `17` |

Here `0` means zero modular survivors, not zero Jacobian rank.

This diagnostic is intentionally **not** counted as a theorem-safe closure.
It samples rows, uses one deterministic occurrence witness and affine gauge,
and does not enumerate all pivot charts or frontier attachments.  The modular
test is a necessary identity test for the presentations it evaluates, but it
is not an exhaustive census of either the sampled pre-constant-plane source
or the current `1,819,789` orbits.  Moreover, even an
exact survivor involving a `u`-difference or interpolation determinant would
initially prove only chart-saturated noncriticality: those denominators are
auxiliary internal frontiers, not parent units, and would still require a
gluing argument.

## 7. Decision for the endpoint

The concurrence construction is a useful algebraic compression:

* twelve plane incidences become three colored four-row collinearity systems;
* two systems are rationally interpolated;
* the generic chart becomes four equations in ten variables; and
* a proper fixed-base fiber has complex length at most six.

It does not currently give a materially smaller finite global certificate.
The relative colored support placement still changes the coefficient and
frontier arrangement presentation by presentation.  The exact ramification
point proves
that internal discriminants occur before any parent wall, and the all-factor
separation proves that such a point need not offer a fourth-factor exchange.
The sampled mixed-minor screen supplies no evidence for a uniform fixed-minor
shortcut.

The remaining theorem obligation is therefore still componentwise: control
how the finite generic sheets attach across ramification, shared-edge,
concurrence-rank, `h_j`, interpolation, and projective-boundary strata, and
show that every resulting real component reaches a parent boundary or chart
infinity.  Until that attachment theorem or an exact compact-component
counterexample is supplied, the honest score remains `2/9`.
