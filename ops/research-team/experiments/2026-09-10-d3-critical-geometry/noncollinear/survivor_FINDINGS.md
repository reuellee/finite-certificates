# Actual survivor: exact ordinary supports and the remaining contraction gate

Status: **useful bounded null result; no triple or original diagonal closed**.
This is the inherited survivor with canonical row `(5563,4373,23221)` and named
presentation `(5563,16134,19284)`. The new chart supplies a useful parent-unit
pivot but does **not** demonstrate a complexity improvement over the inherited
conic model or over retaining the two cubic height equations.

## 1. Authenticated ordinary presentations

The source is
`checkpoint/checkpoint/checkpoint/checkpoint/inputs/DIAG3_triple_fullspace_critical_h1.json`,
SHA-256 `c9244a47ded5736e7afe724a9914e75631a22b78653442e88c14f5c397919eb8`.
The ordinary supports recovered and exactly matched to its normalized polynomials
are:

| Named factor | Ordinary normal quartet | Global kind | Raw/source ratio |
|---|---|---:|---:|
| 5563 | 123 / 145 / 246 / 378 | 50 | −1 |
| 16134 | 126 / 257 / 367 / 458 | 50 | −1 |
| 19284 | 157 / 168 / 245 / 348 | 51 | +1 |

The two recovered supports were found at two targeted rational uniform wall
parents, with 8 and 3 candidate substitutions respectively, followed by exact
symbolic comparison. This was not an orbit census. The twelve triples are
pairwise distinct. Their parent-label occurrence degrees are
`(5,5,4,5,5,4,4,4)`, so the earlier light-label escape does not apply immediately.
The independent referee reconstructed the supports and all subsequent chart
normals without importing the recovery code.

## 2. Full four-line chart

Write the anchor concurrence as `p=(0,0,0,1)`. Normalize its four projected lines
to `z1=0`, `z2=0`, `z3=0`, `z1+z2+z3=0`. After fixing the high-parent height gauge,
the columns of the parent matrix are

\[
Y=\begin{pmatrix}
0&0&0&1&1&1&1&1\\
0&1&1&0&0&B&C&D\\
1&0&-1&0&A&0&-1-C&-1-D\\
0&0&1&0&u&v&w&t
\end{pmatrix}.
\]

The four projected parameters are `A,B,C,D`; the four heights are `u,v,w,t`.
The original parent residence is the conjunction of its seventy strict bracket
sign conditions. Each bracket is affine jointly in the four heights. The usual
finite orientation sectors of this normalization are retained.

The chart follows from the ordinary four-line anchor normalization: the first,
second, third and fourth high parents are the relevant line intersections;
parent uniformity makes the chosen low-parent affine coordinates and the
high-parent height gauge legitimate. In particular **C=D is allowed**. Parents
7 and 8 can have coincident projections and different heights; no division by
C−D occurs anywhere here.

Let Q and R be the raw four-normal determinants of the two recovered supports.
The raw anchor determinant is identically zero. Q and R have height degree 3,
with 76 and 30 expanded terms, respectively. All raw equations and all seventy
brackets are frozen in `survivor_CONTRACTION_CHART.json`.

## 3. Global parent-unit pivot and exact critical equation

The exact identity

\[
L:=R_w=(Bt-Dv)(-AD+At+u)=-[1468][3458]
\]

holds as a polynomial. Thus L never vanishes anywhere in a uniform parent
residence. Put `N=R|_{w=0}`. Then `R=Lw+N`, and the entire R wall is the rational
graph `w=-N/L` over an **open** subset of the seven coordinates
`(A,B,C,D,u,v,t)`. Openness follows by substituting this graph in the strict
original residence inequalities. No branch or rank exception of R is omitted.

Write `Q=q2 w²+q1 w+q0` and define the compactly represented polynomial

\[
E=q_2N^2-q_1NL+q_0L^2.
\]

Exact expansion proves

\[
E=\operatorname{Res}_w(R,Q)=L^2Q(A,B,C,D,u,v,-N/L,t).
\]

The full triple is therefore `E=0` in that open seven-coordinate residence.
The resultant has one irreducible factor over the rationals, of total degree
13, height degree 7, and 1690 terms. Its degrees in `(A,B,C,D,u,v,t)` are
`(4,3,2,5,5,4,5)`. No resultant factor has been discarded. These large expanded
numbers are a limitation, not evidence of a new efficient method.

Because `R_w` is nonzero, eliminating the R equation identifies the full
vertical critical locus exactly with

\[
K=\{E=E_u=E_v=E_t=0\}
\]

inside the same open residence. Indeed, along R=0 the vanishing of the three
height derivatives of Q restricted to its graph is equivalent to
`rank(d_h Q,d_h R)<2`; on Q=0 differentiation of the displayed identity only
multiplies those derivatives by the nonzero factor L². This equivalence includes
all critical ranks and all projected coincidences. The derivative term counts
are 1627,1224,1400; the uneliminated six minor equations remain available in the
chart artifact and are substantially more compact as determinant expressions.

A second useful fact is only a **wall-local nonvanishing assertion**:
`Q_t != 0` at every uniform point of Q=0. The ordinary circuit formula expresses
Q_t as a nonzero scalar times `det(Y4,Y5,p,q)`, where q is the Q concurrence.
If this determinant were zero, q would belong to the anchor plane145 and to
plane458, hence to line45; these planes are distinct by [1458] !=0. Since q also
belongs to plane257, [2457] !=0 would force q=Y5, contradicted by [1256] !=0
because q belongs to plane126. The three-column wedge `(Y4,Y5,p)` is nonzero:
A is nonzero since `[2456]=-Av` is a parent unit. This proves Q_t nonzero on its
wall. It does **not** say the polynomial Q_t is globally a product of parent
units, and it does **not** prove the two vertical gradients are independent.

## 4. Precise remaining theorem and limits

For this source triple, the inherited regular-locus argument reduces
noncompactness to proving `H_c^0(K)=0` after the already accepted collision and
other closed excisions, or to a direct noncompactness proof of the whole triple.
A successful argument must cover every real component in every original parent
residence, including C=D and the full critical set above. It must supply an
actual escape or a justified global maximum principle. The existence of the
unit pivot and two individually regular walls does not supply that argument.

This bounded gate found no affine escape, globally cut conic, or identity that
settles K. It does not close this survivor, any new source orbit, or the original
triple obligation. Extending to D3 still requires a theorem covering all actual
remaining source triples (or a direct original-signature triple theorem), not
merely solving this selected survivor.

The earlier accepted source-specific graph and proportional-section proofs in
`escape_*` remain separate. Their application was already covered by inherited
light-label escape and receives no new count.

## 5. Reproduction

Run `survivor_recover.py`, `survivor_chart.py`, `survivor_eliminate.py`, then
`survivor_finalize_algebra.py`. No network, floating-point decision, numerical
root acceptance, broad census, torus-scaling scan, or unsaturated Groebner basis
is used. Only the recovery stage searches two bounded collections of rational
parent substitutions; all reported identities are symbolic.
