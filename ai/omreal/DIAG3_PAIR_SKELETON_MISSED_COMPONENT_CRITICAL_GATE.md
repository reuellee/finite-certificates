# Diagonal three: a finite exact critical gate for source-skeleton misses

## Classification

**PROVED**, as an exact semialgebraic reduction.  A finite set of exact
critical representatives can be made to meet every connected component of
one primitive full-support residual wall in the strict row-2599 parent cell.
Consequently, component coverage by the retained 40-edge source skeleton is
equivalent to attaching each of those finitely many representatives to that
skeleton inside the wall.

The stronger shortcut “the raw nearest-point or KKT system is itself
zero-dimensional” is **DISPROVED**.  Positive-dimensional critical loci occur
even for a smooth primitive irreducible wall and an internal line-segment
skeleton.  The finite object is obtained by exact semialgebraic
component-sampling of the critical locus, or by a separately certified generic
stratified-Morse perturbation; genericity must not be assumed.

This theorem does not construct the representatives for all 17,824 candidate
row-2599 factors, attach them to the source skeleton, label a global master
complex, or change the honest `2/9` ledger.

## 1. Pinned scope

The base revision is

```text
ec362dba8a912bc4749c004641aee2da0a88dc05
```

The compactification is the pinned product

\[
 X=(\Delta^3)^3
  =\left\{x=(x_{kj})\in\mathbb R^{12}:
       x_{kj}\geq0,\ \sum_{j=0}^3x_{kj}=1\ (k=6,7,8)\right\}.
                                                               \tag{1}
\]

Let

\[
 G_k(x)=\sum_{j=0}^3x_{kj}-1\quad(k=6,7,8)                 \tag{2}
\]

and let `H_I=chi_I[I]`, for the seventy 4-subsets `I` of `[8]`, be the
row-2599 sign-normalized parent brackets.  Thus `H_I>0` at the pinned parent
sample.  Write `P` for the connected strict row-2599 cell containing that
sample:

\[
 P\subset\{G_6=G_7=G_8=0,\ H_I>0\text{ for every }I\}\subset X. \tag{3}
\]

Its closure `bar P` is taken in `X`, not in one affine gauge chart.  The
twelve coordinate divisors of `(Delta^3)^3` are exactly the twelve pinned
parent-bracket divisors listed by the compactification atlas.  Hence

\[
 \partial_P:=\overline P\setminus P
       \subseteq \bigcup_I\{H_I=0\}.                         \tag{4}
\]

This is the **true parent boundary**.  It contains every proper product-
simplex support and every affine-chart infinity face.  No endpoint, edge, or
collar boundary of the retained source skeleton is added to (4).

Let `f in Q[x]` be one nonzero primitive full-support residual polynomial and
put

\[
 W_f=P\cap\{f=0\}.                                         \tag{5}
\]

Let `S` be the union of the forty closed parent-safe source segments with
indices

```text
1,4,7,12,13,15,16,17,21,22,24,27,30,36,37,39,45,52,60,61,
62,66,67,69,71,73,80,83,84,86,90,92,94,96,98,99,101,102,103,104.
```

Every segment is a compact subset of `P`.  The theorem below does not assume
that all wall components meet `S`; that is exactly the open coverage claim.

## 2. The true-boundary barrier

Define the exact polynomial

\[
                 B(x)=\prod_{I\in{[8]\choose4}}H_I(x).       \tag{6}
\]

The only properties of (6) used below are

\[
 B>0\text{ on }P,\qquad B=0\text{ on }\partial_P.            \tag{7}
\]

Thus any lower-degree exact polynomial with (7) can replace (6).  An
implementation may instead use the piecewise-polynomial parent margin

\[
                 m(x)=\min_I H_I(x),                          \tag{8}
\]

encoded by an auxiliary variable and active-bracket strata.  Equation (8)
has the same positive-interior/zero-boundary property and avoids expanding
the degree-70 product.  The product (6) is used in the theorem because it
gives one explicit polynomial critical system.

## 3. Critical-representative theorem

Let `J(q_1,...,q_s)` denote the Jacobian whose rows are the differentials of
the displayed polynomials in the twelve barycentric variables.  Define

\[
 \begin{split}
 \operatorname{Crit}_B(f)=\{x\in P:{}&
     G_6=G_7=G_8=f=0,\quad H_I(x)>0\ (\forall I),\\
   &\text{every }5\mathbin\times5\text{ minor of }
       J(G_6,G_7,G_8,f,B)\text{ vanishes}\}.
                                                               \tag{9}
 \end{split}
\]

The inequalities in (9) give the strict parent sign set.  The additional
`x in P` tag selects its connected component containing the pinned sample;
in an exact certificate that component membership must be retained by a
roadmap/path certificate rather than inferred from signs alone if the sign
realization set has more than one component.

> **Theorem (finite exact missed-component critical gate).**
> For every semialgebraically connected component `C` of `W_f`,
> `C intersect Crit_B(f)` is nonempty.  The semialgebraic set
> `Crit_B(f)` has finitely many semialgebraically connected components.
> Choose one exact real-algebraic sample point from each of them and call the
> resulting finite set `R_f`.  Then every connected component of `W_f`
> contains at least one point of `R_f`.
>
> In particular, for the retained source skeleton `S`,
>
> \[
> \boxed{
>  \text{every component of }W_f\text{ meets }S
>  \iff
>  \text{every }r\in R_f\text{ is joined to }S
>  \text{ by a semialgebraic path in }W_f.}             \tag{10}
> \]
>
> Therefore any component `C` avoiding `S` contains an exact algebraic
> representative `r in R_f`; its distance from `S` is strictly positive.

### Proof

Fix a component `C` and take its closure in `bar P`.  The set `bar C` is
compact because `bar P` is closed in the compact product of simplices.
Connected components of a semialgebraic set are semialgebraic and closed in
that set.  Since `W_f` is closed in `P`,

\[
                  \overline C\cap P=C.                       \tag{11}
\]

Choose any `c in C`.  Then `B(c)>0`.  On the other hand, every point of
`bar C minus C` lies in `partial_P`, so (7) gives `B=0` there.  The maximum
of `B` on the compact set `bar C` is therefore positive and is attained at a
point `p in C`.

If `p` is smooth on the hypersurface `f=0` relative to the affine hull
`G_6=G_7=G_8=0`, the Lagrange multiplier condition says

\[
dB(p)\in\operatorname{span}
       \{dG_6(p),dG_7(p),dG_8(p),df(p)\}.                    \tag{12}
\]

Here `C` is locally open in the smooth wall near `p`: semialgebraic sets are
locally connected, and a connected component is open in a locally connected
space.  Thus maximizing on `C` gives the ordinary constrained critical-point
condition on the wall itself.

This is exactly the vanishing of all `5 by 5` minors in (9).  If `p` is a
singular wall point, the first four rows
`dG_6,dG_7,dG_8,df` already have rank at most three, so all those `5 by 5`
minors vanish automatically.  Hence `p in Crit_B(f)` in both cases.  This
proves that (9) meets every `C`, including components whose closure reaches
parent infinity and components whose maximizing point is singular.

The set in (9) is semialgebraic over `Q`, so it has finitely many
semialgebraically connected components.  Exact real-algebraic sampling
(quantifier elimination, a critical-point sampler, CAD, or a roadmap
implementation with independently checked Thom encodings) returns one
algebraic point from each nonempty component.  A connected component of
`Crit_B(f)` is a connected subset of `W_f`, so it lies in one component of
`W_f`.  Since every component of `W_f` meets `Crit_B(f)`, sampling all
critical components gives the asserted finite set `R_f`.

Finally, connected semialgebraic sets are semialgebraically path connected.
If a wall component meets `S`, every critical representative in that
component has a path to `S`.  Conversely, every wall component contains a
representative, so paths from every representative to `S` force every wall
component to meet `S`.  This proves (10).  If `C` avoids `S`, then
`dist(C,S)>0`: otherwise compactness of `S` would give a sequence in `C`
converging to a point of `S subset P`, contradicting (11).  QED.

## 4. Nearest-skeleton boundary-stratified form

The barrier theorem is the smallest existence reduction because it forces
the witness into the strict parent cell and avoids recursive boundary work.
For an implementation that uses distance to the already stored skeleton,
the exact alternative is as follows.

For retained edge `e=[u_e,v_e]`, let

\[
 y_e(t)=u_e+t(v_e-u_e),\qquad
 D_e(x,t)=\|x-y_e(t)\|^2,\quad 0\leq t\leq1.               \tag{13}
\]

Choose a finite semialgebraic Whitney stratification `{T_a}` of
`bar W_f=bar P intersect {f=0}` compatible with `partial_P`.  It may also be
made compatible with every other residual wall if signature labels or a
master subdivision are being constructed, but those extra residual factors
are **not needed** for the one-wall component-existence implication.

On a smooth stratum `T_a`, use a finite exact chart cover on each member of
which equality equations
`Q_a=(G_6,G_7,G_8,q_{a1},...,q_{ar})` have constant full Jacobian rank; retain
the chart and stratum's strict sign conditions.  (A smooth semialgebraic
stratum need not be one global complete intersection.)  For the open edge
stratum `0<t<1`, the nearest-point critical system on such a chart is

\[
 Q_a(x)=0,\quad
 \operatorname{rank}J_x(Q_a,D_e)=\operatorname{rank}J_xQ_a,
 \quad \partial_tD_e=0,                                  \tag{14}
\]

together with its sign conditions.  The rank equality is encoded by the
vanishing of all one-rank-larger minors and one certified nonzero maximal
minor of `J_x Q_a`.  At `t=0` and `t=1`, fix `t` and omit the last equation;
those are endpoint strata of the artificial edge parameter, not parent
infinity.  Zero-dimensional `T_a` are included without a tangential equation.

Let `C` be a wall component disjoint from `S`.  The exact positive number

\[
 \delta_C^2=\min\{D_e(x,t):x\in\overline C,
             e\text{ retained},\ 0\leq t\leq1\}             \tag{15}
\]

is attained.  A minimizer lies on some product stratum
`T_a times {0}`, `T_a times (0,1)`, or `T_a times {1}` and therefore satisfies
(14) or its endpoint version.  If `T_a subset P`, this is an interior smooth
or singular-wall witness.  If `T_a subset partial_P`, it is a **true parent-
boundary witness**.  Singularities cause no gap because they are replaced by
smooth Whitney strata; alternatively, singular points may be included
wholesale by Jacobian-rank-drop equations as in (9).

Sampling one exact point from every semialgebraically connected component of
the finitely many systems (14) gives a finite exact candidate set.  The
distance form is algebraically lower-degree but has up to forty edge families
and all true-boundary strata.  The barrier form has one family and no boundary
alternative but a high-degree product.  The active-margin encoding (8) is a
useful hybrid.

## 5. Exact no-go for raw KKT finiteness

Primitivity, smoothness, and skeleton avoidance do not make the unperturbed
distance critical locus zero-dimensional.  Take

\[
 P=(-2,2)^3,\qquad f=x^2+y^2-1,
 \qquad S=\{(0,0,t):-1\leq t\leq1\}.                       \tag{16}
\]

The polynomial `f` is primitive and irreducible over `Q`; its wall in `P` is
the smooth connected cylinder

\[
 C=\{x^2+y^2=1,\ -2<z<2\},                              \tag{17}
\]

which avoids `S`.  For every point `(x,y,z)` with `x^2+y^2=1` and
`-1<z<1`, the unique closest skeleton point is `(0,0,z)` and the squared
distance is exactly `1`.  Hence the complete two-dimensional set

\[
 \{x^2+y^2=1,\ -1<z<1\}                                \tag{18}
\]

lies in the smooth nearest-point KKT locus.  Thus a certificate schema that
requires the raw KKT ideal to be zero-dimensional is false.  Exact sampling
of the finitely many connected critical components, as in Sections 3--4, is
the weakest unconditional repair.  A generic perturbation is also valid only
when its stratified-Morse and boundary behavior are separately certified.

## 6. Certificate contract and next discriminator

For one factor `f`, a proof-bearing implementation should emit:

1. the normalized sparse polynomials `f`, the seventy `H_I`, and either `B`
   or the active-margin graph, with semantic digests;
2. exact component samples for (9), or for every declared stratum of (14),
   as rational univariate representations/Thom encodings;
3. a completeness certificate for the critical-locus component sampling,
   including singular and true-boundary strata;
4. for every critical representative, an exact semialgebraic path in `W_f`
   to one of the forty retained segments, or an explicit unattached residue;
5. explicit separation of `parent_infinity_subcomplex` from edge endpoints,
   box faces, collar ends, and other artificial scope boundaries; and
6. hostile canaries for a missed interior sphere/cylinder, a singular wall,
   a component escaping only to true parent boundary, and a skeleton endpoint
   minimizer.

The highest-value discriminator is a preregistered replay on factor `19069`:
run the barrier/active-margin sampler in the whole compactified parent cell,
require it to recover a representative attaching to the already certified
edge-39 collar, and report every additional critical component fail-closed.
This tests the new global gate on the algebraically largest mandatory witness
without pretending that the local collar is full-parent coverage.

## 7. Semialgebraic dependencies

The standard finiteness, path, and exact-sampling facts used above are
separated from the project-specific barrier argument.  Basu, Pollack, and
Roy, *Algorithms in Real Algebraic Geometry*, revised second edition (2016),
Theorems 5.21--5.23 prove that a semialgebraic set has finitely many connected
semialgebraic components and that connectedness is equivalent to
semialgebraic path connectedness.  Their Algorithm 13.11 is an exact sampling
procedure meeting every semialgebraically connected component of every
realizable sign condition.  Section 5.5 supplies the finite smooth
semialgebraic stratification used only in the alternative formulation of
Section 4.

Author-maintained bibliographic page and online-book record:

- <https://mariefrancoiseroy.pages.math.cnrs.fr/MFRoymathpublications.html>
- <https://link.springer.com/book/10.1007/3-540-33099-2>

The attached source index's Basu--Pollack--Roy component-count paper remains a
useful quantitative reference, but it is not used as the source for these
qualitative and algorithmic facts.

## 8. Input accounting

All digests are SHA-256 at the pinned base.

| input | SHA-256 |
|---|---|
| `DIAG3_PAIR_GLOBAL_MASTER_QUOTIENT.md` | `af64cf292ce04234f4dabf48d0ae278c7a9ea1bee7ae83b525a0631d287f3eb7` |
| `DIAG3_PAIR_FULLSUPPORT_SEGMENT_COVER.md` | `55a68acd5e74c011f92a0184ba240475f6076adf54d6ffb0df4ac42a601f2e6a` |
| `data/DIAG3_PAIR_FULLSUPPORT_SEGMENT_COVER.json` | `19248dd148d1fd002931ed5f48197869dd42c68a513376e1a4d6941389bda307` |
| `DIAG3_PAIR_FULLSUPPORT_COMPONENT_COLLAR.md` | `513c858d10261bc2f2d9b1662838f02283b031cdc9f05f3926c8bc5a190f941a` |
| `DIAG3_PAIR_DIFFERENTIAL_ENDS.md` | `5c47ce64a77784673c8deecc0279fd279154582b625d2d6a86d6da9d35bdde15` |
| `data/DIAG3_PAIR_GLOBAL_CLOSURE_OPEN_OBJECT.json` | `fb73899be7ff4aed5739b7f6a999d623db2a0504f212d5fe5aba35e1df1b1465` |
| `data/DIAG3_PAIR_GLOBAL_row2599_compactification_atlas.json` | `956fbe7e5c7b1e04c8873ed9c0f3de9cb5420e3e06f1d5fae4c60f4e0571b364` |
| attached `01-9DVL_RESEARCH_SOURCES-1-.md` | `659a2818f409f01100bcb9886248c23767e65791fe1827ba29ab3a8a4ae093e1` |

The attached source index was used to confirm the existing quantitative
component-count reference.  The exact qualitative and algorithmic dependencies
are the book results identified in Section 7.

## 9. Check procedure

No executable code is introduced.  From the pinned worktree, check the base,
input pins, retained-edge list, and note bytes with

```console
git rev-parse HEAD
sha256sum \
  ai/omreal/DIAG3_PAIR_GLOBAL_MASTER_QUOTIENT.md \
  ai/omreal/DIAG3_PAIR_FULLSUPPORT_SEGMENT_COVER.md \
  ai/omreal/data/DIAG3_PAIR_FULLSUPPORT_SEGMENT_COVER.json \
  ai/omreal/DIAG3_PAIR_FULLSUPPORT_COMPONENT_COLLAR.md \
  ai/omreal/DIAG3_PAIR_DIFFERENTIAL_ENDS.md \
  ai/omreal/data/DIAG3_PAIR_GLOBAL_CLOSURE_OPEN_OBJECT.json \
  ai/omreal/data/DIAG3_PAIR_GLOBAL_row2599_compactification_atlas.json \
  ai/omreal/DIAG3_PAIR_SKELETON_MISSED_COMPONENT_CRITICAL_GATE.md
jq '.source_bank.selected_edge_indices' \
  ai/omreal/data/DIAG3_PAIR_FULLSUPPORT_SEGMENT_COVER.json
```
