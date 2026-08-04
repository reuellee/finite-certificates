# Block-Gordan hard triple: exact local cancellation and codimension-one obstruction

## Status

This note proves an exact **local cancellation theorem** for the hard
row-2599 third-diagonal triple.  The three support-frozen circuits found in
`THIRD_DIAGONAL_E1_REDUCTION.md` can be pivoted simultaneously across a
literal product cube.  The opposite corner admits one common pencil escape
to the boundary of the parent realization space.  The cube contraction and
escape extend continuously across every zero-weight and zero-block face of
the block-Gordan compactification.

Consequently, the component of

\[
 I=B_{\sigma_0}\cap B_{\sigma_4}\cap B_{\sigma_3}
\]

through the stored pattern-zero parent is noncompact.  It contributes zero
to \(H_c^0(I;R)\), over every coefficient ring \(R\).

This does **not** prove the third diagonal.  An exact codimension-one audit
also exhibits the obstruction to turning this particular cube into a global
matching: among its 19 residual cofactor walls, 16 are endpoint-specific.
At a second exact realization of the same parent chirotope, one endpoint of
the \(Q_4\)-to-\(R_4\) edge has disappeared while the other remains strict.
A global matching must therefore reroute its pivots across endpoint-specific
walls; merely allowing shared edges to collapse is insufficient.

The exact verifier is
[`BLOCK_GORDAN_TRIPLE_WALL_AUDIT.py`](BLOCK_GORDAN_TRIPLE_WALL_AUDIT.py).
It uses only integer and rational arithmetic.

## 1. The three exact pivot edges

Let \(Y_0\) be pattern zero in
`data/seeat_parent2599_shatter8.npz`.  For signature bits \(0,4,3\), the
stored positive-circuit vertices are

\[
\begin{aligned}
 Q_0&=123/134/267/258/468,\\
 Q_4&=123/256/127/357/478,\\
 Q_3&=123/256/356/127/347.
\end{aligned}
\]

The distinguished one-exchange vertices are

\[
\begin{aligned}
 R_0&=134/234/267/258/468,\\
 R_4&=134/256/127/357/478,\\
 R_3&=134/256/356/127/347.
\end{aligned}                                                    \tag{1}
\]

For each \(j\in\{0,4,3\}\), both endpoints are strict normalized positive
dependences in \(P_{\sigma_j}(Y_0)\).  Their supports share four triples and
their six-column union has rank four.  Hence

\[
 e_j=[q_j,r_j]\subset P_{\sigma_j}(Y_0)
\]

is a one-dimensional face, not just an arbitrarily chosen segment.  The
separately normalized intersection resolution contains the closed cube

\[
                         C=e_0\times e_4\times e_3.              \tag{2}
\]

The prior exact enumeration proves why (2) must be coordinated: among all
\(52\cdot34\cdot52=91{,}936\) one-exchange corners, exactly 18,480 are
pencil-flexible, and every one changes all three witness blocks.  No greedy
one-block or two-block pivot reaches an escape corner.

At the corner \((r_0,r_4,r_3)\), the union-degree vector is

\[
                         (2,5,5,5,4,4,5,3).                     \tag{3}
\]

Label 1 occurs only in the planes `134` and `127`.

## 2. Exact common pencil escape

Use the integer direction

\[
 v=(-48{,}680{,}481,\ 163{,}290{,}694,\ 329{,}496{,}695,\ 0)^T
\]

and move only the first parent column:

\[
                            y_1(t)=y_1+t v.                       \tag{4}
\]

The exact plane normals satisfy

\[
 a_{134}(t)=(1-8{,}365{,}328t)a_{134}(0),\qquad
 a_{127}(t)=(1-11{,}992{,}469t)a_{127}(0),                       \tag{5}
\]

while every other normal in the three supports (1) is fixed.  Equivalently,
\(v\) belongs to both planes `134` and `127`.  The motion is not projective
rescaling: \(y_1\) and \(v\) have rank two.

An exact scan of all 70 parent brackets gives the unique first positive
root

\[
 t_*=\frac{17036}{420822576313},\qquad [1467](t_*)=0.             \tag{6}
\]

Every parent bracket keeps its original nonzero sign for \(0\le t<t_*\),
and no other bracket vanishes at \(t_*\).  The two factors in (5) remain
strictly positive even at the exit:

\[
\begin{aligned}
1-8{,}365{,}328t_*&=
 \frac{278310848505}{420822576313}>0,\\
1-11{,}992{,}469t_*&=
 \frac{216518874429}{420822576313}>0.                            \tag{7}
\end{aligned}
\]

Let \(c_{j,I}>0\) be the coefficients of the \(R_j\) circuit at \(t=0\).
For a support normal with scale \(\alpha_I(t)\) from (5), or scale 1 for a
fixed normal, put

\[
 \widetilde c_{j,I}(t)=\frac{c_{j,I}}{\alpha_I(t)},\qquad
 c_{j,I}(t)=
 \frac{\widetilde c_{j,I}(t)}{\sum_K\widetilde c_{j,K}(t)}.      \tag{8}
\]

Equations (5), (7), and (8) give a strict normalized positive dependence for
each active \(R_j\) at every \(0\le t<t_*\).  Thus (4) is a path in every
simultaneous-bad intersection indexed by a nonempty subset of the three
blocks.  It approaches a point outside the uniform parent space at (6), so
the path leaves every compact subset of that parent space.

## 3. Zero weights and zero blocks

The block-Gordan union resolution uses weights \(w_j\ge0\) with total mass
one, not a separate normalization of every block.  Write

\[
                             t_j={\bf1}^Tw_j.
\]

On the closed join of the cube (2), define

\[
 H_a(w_j)=(1-a)w_j+a,t_jr_j,\qquad 0\le a\le1.                  \tag{9}
\]

This is well-defined directly in block coordinates, including where the
usual expression \(w_j=t_ju_j\) has no unique \(u_j\) because \(t_j=0\).
It has four immediate properties:

1. \({\bf1}^TH_a(w_j)=t_j\), so all block masses and their total are fixed.
2. \(A_{\sigma_j}(Y_0)^TH_a(w_j)=0\) by linearity.
3. Nonnegativity is preserved.
4. If \(t_j=0\), then \(H_a(w_j)=0\) for every \(a\).

Thus (9) contracts the entire closed cube/join, not merely its positive-mass
interior, to the far \(R\)-face.  It also retains coordinate-zero faces of
the circuit endpoints.  Every nonempty zero-block face of that far face uses
label 1 only through the same two planes `134` and `127`, so the single
pencil (4)--(8) escapes every such face compatibly.

This is precisely the compatibility that is lost by deleting zero blocks or
by working only with strict circuit supports.

## 4. Local compact-support consequence

Concatenate, in the simultaneous-bad base intersection, the fixed-parent
pivots (2) with the parent motion (4).  The base point remains \(Y_0\) during
the pivots, and then follows \(Y(t)\) for \(0\le t<t_*\).  All three bad
signatures remain certified by (8), while (6) shows that the path has no
limit in the parent realization space.

Therefore the component of

\[
 B_{\sigma_0}\cap B_{\sigma_4}\cap B_{\sigma_3}
\]

containing \(Y_0\) is noncompact.  A compactly supported locally constant
section on a connected noncompact component is zero.  Hence this component
contributes no summand to

\[
 H_c^0(B_{\sigma_0}\cap B_{\sigma_4}\cap B_{\sigma_3};R)        \tag{10}
\]

for any coefficient ring \(R\).

In a support-refined circuit cover, (10) need not appear as termwise
vanishing of the original \(Q_0/Q_4/Q_3\) support piece.  The cube records
the necessary cancellation through adjacent support pieces.  This is why
the block-Gordan resolution, whose block-mass filtration functorially
recovers compact-support Mayer--Vietoris, is the correct bookkeeping space.

## 5. Complete codimension-one cofactor audit

The six vertices \(Q_j,R_j\) have 30 cofactor occurrences.  The three
Q/R pairs share one four-support each, leaving 27 distinct cofactor walls.
Their exact 52-wall classification is:

| kind | distinct walls |
|---|---:|
| fixed bracket units | 8 |
| residual derived walls | 19 |
| zero polynomials | 0 |

The 19 residual walls are listed below.  A repeated occurrence is a shared
Q/R wall; all other rows are endpoint-specific.

| four-support | orbit | occurrence |
|---|---:|---|
| `123/127/357/478` | 36 | Q4, omit `256` |
| `123/134/258/468` | 41 | Q0, omit `267` |
| `123/134/267/258` | 39 | Q0, omit `468` |
| `123/134/267/468` | 41 | Q0, omit `258` |
| `123/256/356/347` | 36 | Q3, omit `127` |
| `123/256/357/478` | 50 | Q4, omit `127` |
| `123/267/258/468` | 47 | Q0, omit `134` |
| `123/356/127/347` | 36 | Q3, omit `256` |
| `134/127/357/478` | 46 | R4, omit `256` |
| `134/234/267/258` | 39 | R0, omit `468` |
| `134/256/127/347` | 37 | R3, omit `356` |
| `134/256/127/357` | 49 | R4, omit `478` |
| `134/256/127/478` | 50 | R4, omit `357` |
| `134/256/356/127` | 41 | R3, omit `347` |
| `134/256/357/478` | 50 | R4, omit `127` |
| **`134/267/258/468`** | **50** | **Q0 omit `123`; R0 omit `234`** |
| `234/267/258/468` | 46 | R0, omit `134` |
| **`256/127/357/478`** | **47** | **Q4 omit `123`; R4 omit `134`** |
| **`256/356/127/347`** | **41** | **Q3 omit `123`; R3 omit `134`** |

Thus exactly three residual walls are shared edge-collapse candidates, and
16 are endpoint-specific.  At a generic shared wall, if the common four
normals have rank three, the coefficients of both unique endpoint normals
vanish and the two normalized endpoints approach the same common
four-circuit.  This is the benign local model a cellular matching can absorb
by collapsing its matched edge.

An endpoint-specific wall has a different local model: one endpoint may be
born or die without the other.  The next section verifies that this actually
happens inside the row-2599 parent chirotope.

For completeness, the eight fixed-unit cofactors are

```text
123/256/127/347  (30)   123/256/127/357  (29)
123/256/127/478  (33)   123/256/356/127  (31)
134/234/258/468  (32)   134/234/267/468  (32)
134/256/356/347  (34)   134/356/127/347  (30)
```

## 6. An exact one-wall obstruction to the fixed cube

Chart 7 of `data/seeat_parent2599_upper178.npz` has exactly the same signs on
all 70 parent brackets as \(Y_0\).  At this chart the five raw alternating
cofactors of \(Q_4\), in support order, are

\[
\begin{split}
(&-578582431137700472,
 -70253942367169540,
 +336425478039445424,\\
 &-54963867325648880,
 -46201975207436930).
\end{split}                                                     \tag{11}
\]

The positive third entry in (11) is the coefficient obtained by omitting
`127`.  Its wall is

```text
123/256/357/478, residual orbit 50.
```

Thus \(Q_4\) is not a positive circuit at chart 7.  In contrast, the raw
cofactors of \(R_4\) are

\[
\begin{split}
(&-578582431137700472,
 -908594655031293132,
 -349727606339858544,\\
 &-742528912103169852,
 -685978694109578506),
\end{split}                                                     \tag{12}
\]

so \(R_4\) remains strict.  At \(Y_0\), both \(Q_4\) and \(R_4\) are
strict.  Equations (11)--(12) are therefore an exact endpoint-specific
birth/death obstruction: the selected \(Q_4\)-to-\(R_4\) edge is present at
one realization of the parent chirotope and absent at another.

This does not obstruct all possible matchings.  It proves only that a global
matching cannot use this fixed product cube without a wall-dependent
rerouting.

## 7. Strongest viable cross-wall target for diagonals 3--8

The block-Gordan audit in `BLOCK_GORDAN_AUDIT.md` proves functorially that

\[
 R\Gamma_c(\Gamma_S;R)\simeq R\Gamma_c(B_S;R),                  \tag{13}
\]

and that the block-mass filtration of \(\Gamma_S\) is exactly the
compact-support Mayer--Vietoris spectral sequence

\[
 E_1^{p,q}=\bigoplus_{|T|=p+1}H_c^q
       \left(\bigcap_{\sigma\in T}B_\sigma;R\right)
 \Longrightarrow H_c^{p+q}(B_S;R).                             \tag{14}
\]

Consequently, the viable finite target is not a separate shelling of each
fixed witness polytope.  It is a **coherent matching of the constructible
block-Gordan family over the residual-wall face poset**, with all of the
following properties:

1. **Block-face coherence.**  Sending a block mass to zero restricts the
   matching for an active set \(T\) to the matching for
   \(T\setminus\{\sigma\}\).  Formula (9) is the local model.
2. **Shared-wall contraction.**  A matched pivot edge may contract to its
   common four-circuit at a shared residual wall.
3. **Endpoint-wall rerouting.**  At each endpoint-specific wall, circuit
   elimination must provide a matched two-cell or higher cube that replaces
   a dying pivot without producing a directed cycle.  Equations (11)--(12)
   show this clause is mandatory.
4. **Coordinated pivots.**  Matchings may change several signature blocks at
   once.  The 18,480-corner census proves that independent blockwise greedy
   pivots are insufficient even in the first hard triple.
5. **Index bound.**  After quotienting matched pairs, the total complex of
   (14) must have no critical cochain in total degree \(s-1\).  Equivalently,
   the matched constructible cellular complex must be acyclic in precisely
   the compact-support degree required by diagonal \(s\), for every
   \(3\le s\le8\).

All data entering this target are finite: parent residual-wall strata,
positive circuits of support at most five, pivot adjacencies, and block-mass
face maps.  A proof can therefore be certified by a lexicographic/Bland-type
potential together with exact local rerouting tables.  The essential new
verification obligation is acyclicity after the endpoint-specific
reroutings; fixed-fiber shellability alone does not imply it.

The present cube supplies one exact matched three-cell and proves that its
entire block-face closure has no local critical \(H_c^0\) contribution.  The
orbit-50 example supplies the smallest observed cross-wall test that any
candidate global rule must pass.

## 8. Verification

Run

```bash
python ai/omreal/BLOCK_GORDAN_HARD_TRIPLE_PIVOT.py
python ai/omreal/BLOCK_GORDAN_TRIPLE_WALL_AUDIT.py
```

The second checker verifies exactly:

* the `30 -> 27 -> (8 unit + 19 residual)` cofactor census;
* the `3 shared + 16 endpoint-specific` residual split;
* the two plane equations and normal scale factors in (5);
* all 70 bracket signs, the unique first root (6), and positivity (7);
* transported positive-circuit equations for the three far endpoints;
* the closed cube contraction (9), including a literal zero block;
* common-pencil compatibility for every nonempty active-block subset; and
* the same-parent chart-7 obstruction (11)--(12).

No diagonal is promoted by this note.  It removes the stored hard triple
component as a possible compact component and isolates endpoint-specific
residual walls as the exact next obstruction.
