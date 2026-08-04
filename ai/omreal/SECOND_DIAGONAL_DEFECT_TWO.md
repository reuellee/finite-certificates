# A genuine defect-two pair for the second diagonal

## Result

The exact row-2599 pencil-rigid sample has a tempting extra feature: for every
one of its 65 stored positive pair occurrences, some label $e$ has a partner
$f$ in all but at most one of the support triples through $e$.  Call the
minimum number of exceptions

\[
 d(U)=\min_{e\ne f}
 \#\{I\in U:e\in I,\ f\notin I\}.
\]

Thus the stored row-2599 occurrences all have $d(U)=1$; pencil rigidity
already excludes $d(U)=0$.  There is a universal reduction, but it stops
exactly one step later.

> **Matching-star dichotomy.**  If $U=Q\cup R$ for two five-sets of
> parent triples and $U$ is pencil-rigid, then
> \[
>                              1\le d(U)\le2.           \tag{A}
> \]
> Moreover $U$ has a degree-three label.  If such a label $e$ has defect
> two, its three incident triples have the form
> \[
>                    eab,\quad ecd,\quad efg,           \tag{B}
> \]
> where $a,b,c,d,f,g$ are six distinct labels.

Indeed, $|U|\le10$, so the sum of the eight label degrees is at most 30.
Pencil rigidity gives minimum degree at least three; hence some label $e$
has degree exactly three.  Its three incident triples contain six partner
occurrences among the other seven labels.  Some partner occurs at least once,
so the defect of $e$ is at most two.  Defect zero is precisely the
fixed-partner case excluded by pencil rigidity.  Equality two says no partner
is repeated, which is exactly the matching star (B).

Thus every cofinal pair either has a global one-defect label, or has
$d(U)=2$, in which case every degree-three label has the matching-star form.
(A defect-one union can still have a matching star at some *other* label.)
The global defect-two case is not merely a formal unsigned residue: this note
proves that it occurs under the full second-diagonal hypotheses.

### Shared versus unique star triples

There is a second finite split which matters at the first cofactor root.  Put

\[
 k=|Q\cap R|=10-|Q\cup R|.
\]

Pencil rigidity gives $|Q\cup R|\ge8$, hence $0\le k\le2$.  For a matching
star at $e$, let $s$ be the number of its three triples shared by $Q$ and
$R$, and let $q,r$ be the numbers of star triples occurring in $Q,R$.
Splitting the three triples into `Q-only`, `R-only`, and `shared` gives the
complete table

| shared `s` | possible `(q,r)` |
|---:|:---|
| 0 | `(0,3)`, `(1,2)`, `(2,1)`, `(3,0)` |
| 1 | `(1,3)`, `(2,2)`, `(3,1)` |
| 2 | `(2,3)`, `(3,2)` |

No fourth row is possible because $s\le k\le2$.  A zero coefficient at a
**unique** star triple removes that triple from the active union and lowers
$\deg(e)$ from three to two, so the projective-plane-pencil lemma gives a
boundary exit.  A zero at a shared occurrence need not lower the union
degree, because the other witness may retain the same triple; it belongs to
the boundary-pivot/$d_1$ case rather than the direct pencil case.

The two smaller union sizes admit sharper arithmetic.

* If $|Q\cup R|=8$, total degree is $24$.  Pencil rigidity forces every
  label degree to equal three.  Therefore deletion of **any unique union
  triple** is pencil-flexible.
* If $|Q\cup R|=9$, the total surplus above degree three is only three.  At
  most three labels have degree at least four.  Consequently a unique edge
  whose deletion can preserve minimum degree three is, if it exists at all,
  the single triple on exactly those three high-degree labels.  Every other
  unique support drop is pencil-flexible.

The verifier exhausts both the membership table and the surplus-three degree
distributions.  What remains analytically open is to prove that some
matching-star partner path either reaches a parent wall or has a first root
in one of these flexible/private boundary classes.  Shared-star roots and the
single possible rigid-deletable edge in the nine-edge case are the exact
small-union exceptions which such a proof must route through the Cech
differential.

> **Defect-two obstruction theorem.**  There is a realizable
> `UOM(4,8)` parent and two realizable extension signatures with proper,
> incomparable feasibility regions which, at one exact parent chart, have
> positive support-minimal five-circuits $Q,R$ such that $Q\cup R$ is
> pencil-rigid and
> \[
>                         d(Q\cup R)=2.                 \tag{1}
> \]
> Both supports pass the universal residual-cofactor signed filter.

Consequently a proof which assumes an all-but-one common partner after the
cofinal $5+5$ reduction cannot settle the second diagonal.  The example does
not disprove 9DVL.  In fact the displayed point has an exact shear path to the
parent boundary while both circuits persist.

The arithmetic-only verifier is

```console
python ai/omreal/verify_second_diagonal_defect_two.py
```

## Exact parent and positive pair

Use catalog parent 16 and the integer realization

\[
Y=\begin{pmatrix}
8&4&-3&-6&1&0&8&1\\
1&8&8&1&2&-5&-1&-3\\
3&-1&5&-2&-8&5&-1&-8\\
-1&-1&0&8&2&8&4&5
\end{pmatrix}.                                         \tag{2}
\]

For the two 56-bit extension signatures

```text
rho = 26988370886400909
eta = 45348283816043521
```

the signed derived normals have strict positive circuits on

\[
\begin{aligned}
Q&=123/124/134/235/567,\\
R&=126/247/158/468/378.                                \tag{3}
\end{aligned}
\]

Every maximal cofactor is nonzero, so both are support-minimal rank-four
five-circuits.  The derived-wall orbit types of their alternating cofactors
are respectively

\[
       (37,22,22,12,10),\qquad(47,47,49,51,49).         \tag{4}
\]

In particular each support has a genuine residual cofactor, so neither is
removed by the all-unit obstruction.

The ten triples in (3) have label-degree vector

\[
                         (5,5,4,4,3,3,3,3).            \tag{5}
\]

No label has one fixed partner in every incident triple, so the union is
pencil-rigid.  Directly evaluating all 56 ordered pairs $e\ne f$ in (1)
gives minimum two.  For example labels 1 and 2 miss each other in two of
their five incident triples; no label-partner pair does better.

## Properness and incomparability

The verifier checks the 126 brackets of the following two integer child
realizations.  The first realizes `rho`:

\[
\begin{pmatrix}
32&-12&-7&11&-32&32&12&-3&-11\\
18&29&32&9&-6&3&-4&-16&6\\
-25&-32&1&-5&-30&3&-16&-11&8\\
-24&-4&5&32&7&17&1&6&32
\end{pmatrix}.                                         \tag{6}
\]

On its first eight columns, `eta` has the exact positive circuit

```text
124/125/457/148/378.
```

Thus this parent chart lies in $F_\rho\setminus F_\eta$.  The second child
realizes `eta`:

\[
\begin{pmatrix}
-1765&-365&-944&-363&4096&-2048&-1745&2048&-4096\\
-251&-1329&-1024&1509&1591&1254&4096&1360&2694\\
-4096&-907&414&4096&-827&1335&-326&-250&-3700\\
1820&4096&923&1211&3383&305&3460&1173&-2605
\end{pmatrix}.                                         \tag{7}
\]

On its first eight columns, `rho` has the exact positive circuit

```text
137/567/238/358/478.
```

Hence that parent chart lies in $F_\eta\setminus F_\rho$.  Equations
(2)--(7), checked by integer determinants and alternating cofactors, prove
realizability, properness, and both failures of inclusion without numerical
optimization.

## The displayed point still escapes

Although (1) blocks the proposed one-defect reduction, it does not produce a
trapped component.  Starting from (2), use the genuine projective shear

\[
                         y_1(t)=y_1+t y_4.              \tag{8}
\]

For

\[
                         0\le t<\frac{399}{2456},       \tag{9}
\]

all 70 parent brackets retain their signs.  At the right endpoint precisely
the bracket $[1678]$ vanishes.  Along (8), every alternating cofactor of
both signed circuits in (3) is a polynomial of degree at most two.  Exact
interpolation followed by evaluation at the endpoints and, for a convex
quadratic, its rational vertex proves that all ten cofactors stay strictly
of one common sign throughout the closed interval (9).  The two positive
Gordan dependences therefore persist to the parent boundary.

Thus the point (2) lies in a noncompact component of the simultaneous circuit
intersection.  This is deliberately only a pointwise statement: another
component of the same closed intersection, or another signed support pair,
could still be compact.

The same point also passes the more specific matching-star test.  Label `8`
has the matching star

\[
                         158,\qquad468,\qquad378.
\]

Along its genuine partner ray

\[
                         y_8(t)=y_8+t y_1,
\]

both positive circuits persist for

\[
                         0\le t\le {217\over1966},
\]

and the endpoint is exactly the parent wall `[2348]=0`.  All other parent
brackets keep their signs.  Exact quadratic interpolation and the rational
vertex test prove strict positivity of all ten oriented cofactors on the
whole interval.  Thus the only presently known exact global-defect-two
occurrence has a certified escape along a matching-star partner path itself,
not only along the unrelated shear (8).  This remains a certificate for one
point, not a universal matching-star theorem.

## Consequence for the remaining proof

The cofinal compact-component incidence formulation remains exact:

\[
 \bigoplus_{\alpha<\beta}H_c^0(C_\alpha\cap C_\beta)
 \longrightarrow
 \bigoplus_{\alpha<\beta<\gamma}
 H_c^0(C_\alpha\cap C_\beta\cap C_\gamma).             \tag{10}
\]

The matching-star dichotomy reduces every cofinal pair to two local star
forms.  The new example shows that neither the universal residual filter, actual
extension realizability, nor proper incomparability reduces every surviving
pair to the one-defect shear template.  A complete proof still needs a global
escape/compactification argument or the full incidence differential in (10),
including defect-two generic $5+5$ strata.
