# The all-compact star forces a second wall; first-wall incidence cannot kill it

## Outcome

The exceptional all-compact decoration cannot be excluded by adding more
cofinal-padding rows, an integral Euler argument, or any other calculation
confined to the first wall.  The complete local matrix has a primitive
one-dimensional integral kernel.

There is nevertheless a proof-safe geometric advance:

> **Second-wall forcing theorem.**  At a generic simple residual support-drop
> wall, every strict cofinal spoke whose component is compact must meet a
> genuine residual wall for a **different circuit cofactor** inside the
> parent realization cell.

Every residual four-support has at least 30 such strict paddings (the exact
counts range from 30 to 52).  Hence an exceptional all-compact star forces at
least 30 second-wall incidences, counted with padding labels.  Ruling out a
compact simultaneous-bad component is now necessarily a global acyclicity or
exit theorem for this iterated signed wall graph.

Two proposed ways to supply that global theorem fail in their present form:

* the degree-one label of the strict partner does **not** make the residual
  wall equation linear after imposing its supporting plane; all thirteen
  residual types admit pencil-rigid incidence patterns in which that label has
  degree two or three in the wall support, and type 51 has an exact real oval
  slice;
* canonical one-coordinate Bland pivots do **not** monotonically accumulate
  bad-side signs.  An exact uniform transverse crossing of residual types 37
  and 44 gives a directed wall-label cycle `44 -> 37 -> 44` without meeting a
  parent wall or a third residual representative.

The exact type-51 oval is cut transversely by nineteen parent walls, so it is
not a compact-component counterexample.  Likewise the two-wall cycle is a
no-go for the proposed coordinate-pivot invariant, not a compact component of
the actual simultaneous-bad locus.  Both calculations narrow the missing
input without changing the proof score.

This does **not** finish diagonal two.  It proves that the proposed local
integral route stops for a genuine reason and isolates the next geometric
input.

## 1. Complete local cofinal carrier

Let `P` be the positive four-support at a simple residual wall and enumerate
all 52 five-support paddings as

\[
                         T_0,T_1,\ldots,T_{51},
\]

with `T_0=Q`.  Let `R` be the strict partner support.  In the exceptional
decoration, the components through the wall of every

\[
                         C_R\cap C_{T_i}                              \tag{1}

\]

are compact.  Denote their compact-component columns by `x_i`.

For `i != j`, the supports `T_i,T_j` share `P` and their union has at most six
triples.  The degree-at-most-two pencil theorem makes every component of
`C_(T_i) intersection C_(T_j)` noncompact, so no same-signature pair column
appears.  On the other hand, the triple component through the wall of

\[
                         C_R\cap C_{T_i}\cap C_{T_j}                  \tag{2}

\]

is a closed component of either compact pair component and is compact.  Its
restriction row is, after the usual Cech orientation,

\[
                              x_j-x_i=0.                              \tag{3}

\]

Including **all** triples (2), rather than only the 51 rows containing `Q`,
therefore gives the oriented vertex-edge incidence matrix of the complete
graph `K_52`:

\[
        d_{\rm wall}:\mathbb Z^{52}\longrightarrow
                     \mathbb Z^{\binom{52}{2}}.                      \tag{4}

\]

Every row annihilates `(1,...,1)`.  Conversely the 51 rows `(0,i)` force
`x_i=x_0`; after deleting column zero their matrix is the identity.  Thus

\[
 \ker d_{\rm wall}=\mathbb Z(1,\ldots,1),\qquad
 \operatorname{rank}d_{\rm wall}=51.                                \tag{5}

\]

The identity minor also proves that the image is saturated: there is no
hidden torsion which an integral Euler or Smith-normal-form calculation could
remove.  Rows from triples containing only padding pieces have no compact
pair columns.  Higher cofinal intersections through the same wall merely
encode the simplex identities among (3) and cannot change the kernel in the
degree-one Cech differential.

Additional triple components away from this wall can kill (5), but that is
precisely second-wall/global component data, not a refinement of the first
wall star.

## 2. Exact semialgebraic realization of the local axioms

The exceptional incidence pattern is topologically consistent.  In
`R^4`, put

\[
 L_0=\{x_3=x_4=0\},\qquad L_1=\{x_1=x_2=0\}.                          \tag{6}

\]

Assign every padding cover label `T_i` the closed plane `L_0` and assign the
partner label `R` the plane `L_1`.  Then

* every `R intersect T_i` component is the compact point `0`;
* every `T_i intersect T_j=L_0` is noncompact; and
* every triple `R intersect T_i intersect T_j` is the same compact point and
  has restriction row (3).

Both individual planes have `H_c^0=H_c^1=0`, while compact-support
Mayer--Vietoris gives

\[
                         H_c^1(L_0\cup L_1;\mathbb Z)\cong\mathbb Z. \tag{7}

\]

This integer linear model is not claimed to arise from a third compound.  It
proves the exact logical limitation: closed-cover topology, pencil pruning,
all cofinal containments, and integral incidence alone do not contradict the
all-compact decoration.  Actual compound geometry at another wall is
indispensable.

## 3. Compact strict spokes must meet another residual wall

Return to a genuine `UOM(4,8)` parent cell `X`.  Suppose `P` is a minimal
positive four-circuit at a generic simple residual wall and `R` remains a
strict positive five-circuit there.  A padding `T=P union {q}` is
**strict-eligible** when none of its five four-faces has a structural-zero
incidence type.

At the generic wall, the four nonzero coefficients inherited from `P` have
one common orientation.  The fifth coefficient vanishes transversely.  On
one side it therefore becomes a strict positive five-circuit.  Since `R`
remains strict in a neighborhood, that side contains a nonempty open strict
pair chamber

\[
                 U_{q}\subset C_R\cap C_T.                            \tag{8}

\]

The derived-wall theorem supplies a canonical free coordinate `z` for the
wall of `P`.  In the standard nine-variable frame its residual factor is
affine in `z` and

\[
                 \frac{\partial q_P}{\partial z}=u,                 \tag{9}
\]

where `u` is a signed product of parent brackets (or `1`).  None of those
brackets uses the parent column carrying `z`, so `u` is independent of `z`
and has a fixed nonzero sign on `X`.

Hold the other eight normalized coordinates fixed.  Every parent bracket is
affine in `z`; its prescribed sign therefore cuts out a half-line, and the
parent-cell fiber is their intersection, an open interval.  Equation (9)
shows that `q_P` has exactly one zero in that interval.  Starting just inside
the strict side (8), continue `z` away from that zero.  The incoming
cofactor cannot vanish again.  The path either reaches an endpoint of the
parent interval (a parent wall or infinity), or a different one of the other
nine strict cofactors of `R,T` vanishes first.

If the pair component `D_q` containing the first wall were compact, the
first alternative would be an escape inside `D_q` and is impossible.
Therefore a different circuit cofactor vanishes.

A cofactor which was nonzero at (8) cannot have a structural-zero incidence
type.  Fixed types are signed parent-bracket monomials and never vanish on
`X`.  By the exhaustive 52-wall classification, every remaining zero is one
of the thirteen genuine smooth residual walls.  Thus `D_q` meets a second
residual-wall incidence belonging to another cofactor.  Several coefficients
may vanish simultaneously; that lower-dimensional case belongs to the same
iterated component-decorated graph.

The exact strict-padding counts for residual wall types
`36,37,38,39,41,42,44,46,47,48,49,50,51` are respectively

\[
            30,48,48,30,48,48,48,34,34,52,52,52,52.                \tag{10}

\]

Hence every exceptional all-compact first wall forces at least 30 branches
of the form above.  These branches may meet the same later wall and may form
cycles; (10) is not an acyclicity theorem.

## 4. Why the degree-one partner label does not give a linear escape

Let `ell` be a label of degree at most one in the five-support `R`.  If it is
absent, its projective motion has dimension three; if it occurs in the triple
`ell,u,v`, preserving that normal ray confines it to the fixed projective
plane

\[
                         H=\langle y_\ell,y_u,y_v\rangle.            \tag{11}
\]

The tempting count is then `dim H - one wall equation >= 1`.  This does not
imply that a component reaches the boundary.  The derived determinant of `P`
has degree equal to the number of triples of `P` containing `ell`, before
removing nonzero parent-bracket factors.  In the pencil-rigid residue this
degree need not be one.

The verifier gives, for each of the thirteen residual support orbits, an
explicit generic five-support `R` such that

1. `P union R` is pencil-rigid;
2. some label `ell` has degree one in `R`; and
3. the same label has degree two or three in `P`.

The maximum degrees of the thirteen representatives are

\[
\begin{array}{c|ccccccccccccc}
\text{type}&36&37&38&39&41&42&44&46&47&48&49&50&51\\ \hline
\max\deg_P&3&2&2&3&2&2&2&3&3&2&2&2&2.
\end{array}                                                        \tag{12}
\]

This table is only an incidence no-go; it does not assert simultaneous signed
realizability of every displayed pair.

There is also an exact geometric nonlinear witness.  For the type-51 support

\[
                       P=123/145/267/468,                            \tag{13}
\]

move label 6 in the plane through fixed columns 3 and 5 by

\[
             y_6(s,t)=(-1,-6,7,-1)+s\,y_3+t\,y_5.                  \tag{14}
\]

The seven fixed integer columns are listed in the verifier and every one of
their 35 four-brackets is nonzero.  Direct exact expansion gives

\[
\begin{split}
q_{51}(s,t)={}&2602626880s^2+7481446528st+5762380800t^2\\
              &+3323795896s-9522111088t+74607300904.                \tag{15}
\end{split}
\]

Its quadratic discriminant and translated-radius invariant are respectively

\[
  4AC-B^2=4017266500180361216>0,
\]

\[
  CD^2-BDE+AE^2-F(4AC-B^2)
   =236709361662361009684254720000>0.                               \tag{16}
\]

Thus (15) is a nonempty compact real ellipse.  This is a decisive no-go for
the dimension-minus-one argument: one scalar equation inside the `R`-plane
can have a compact branch.

This plane can be supplied by the exact generic partner support

\[
                         R=356/123/124/378/578.                     \tag{17}
\]

The union with (13) is pencil-rigid and label 6 occurs only in the first
triple of `R`.  Along (14), `n_356` is literally constant because adding
multiples of `y_3,y_5` does not change
`y_3 wedge y_5 wedge y_6`; the other four `R` normals do not use label 6.
Their exact rank is four and all five alternating cofactors are nonzero.
After fixing their signs once, the strict positive `R` witness therefore
persists on every uniform arc of the ellipse.

It is not a counterexample to escape in the uniform realization cell.  Exact
line-conic discriminants show that nineteen of the parent bracket walls meet
the ellipse transversely and none is tangent.  Removing those points breaks
the oval into open arcs, and every component belonging to one fixed parent
chirotope has parent-wall endpoints.  Thus this specific nonlinear hard slice
is noncompact while its `R` witness persists.  A universal proof would have to
show that this parent-wall/cofactor cutting phenomenon always occurs on every
positive oval; the degree count and the thirteen incidence representatives
alone do not show it.

## 5. Exact two-wall no-go for canonical Bland descent

Use the standard normalized chart and set

\[
(a,b,c,d,e,f,g,h,i)=
\left(\frac12,-3,-1,\frac14,-1,2,2,3,-3\right).                    \tag{18}
\]

All seventy parent brackets are nonzero; their minimum absolute value is
`1/4`.  Exactly the type-37 and type-44 residual representatives vanish.  If
`x=a-1/2` and `y=d-1/4`, their bad sides may be oriented as

\[
                   p_{37}=-q_{37}=3x-2y,
        \qquad    p_{44}=-q_{44}=-6x+12y.                           \tag{19}
\]

The canonical pivot for type 37 is increasing `a`, while the canonical pivot
for type 44 is increasing `d`.  The cross derivatives are

\[
 \partial_a p_{37}=3,\quad \partial_a p_{44}=-6,\qquad
 \partial_d p_{37}=-2,\quad \partial_d p_{44}=12.                  \tag{20}
\]

So each canonical bad-direction decreases the other acquired bad-side sign.
This is not merely infinitesimal.  With `epsilon=1/10000`, put

\[
 A:(x,y)=(2\epsilon,\epsilon),\quad
 B:(x,y)=(2\epsilon,3\epsilon),\quad
 C:(x,y)=(6\epsilon,3\epsilon).                                   \tag{21}
\]

At `A`, `p_37>0` and `p_44=0`.  The canonical type-44 motion `A -> B`
enters `p_44>0` but reaches `p_37=0`.  At `B`, the canonical type-37 motion
`B -> C` enters `p_37>0` but reaches `p_44=0`.  Hence the transition labels
are

\[
                             44\longrightarrow37\longrightarrow44. \tag{22}
\]

Only `d` changes on `A B` and only `a` changes on `B C`.  Every parent bracket
and residual representative is affine in the moving coordinate.  Exact
endpoint signs prove that both segments stay in the same uniform parent cell,
and none of the other eleven residual representatives vanishes.  This is the
smallest possible directed cycle in wall labels.

Equation (22) does not exclude a combined two-coordinate vector field: the
two open inequalities in (19) have a common sector.  It does prove that the
canonical one-coordinate continuation cannot support a finite descent whose
set of previously acquired wall signs strictly grows.  A successful descent
must use a multi-coordinate cone rule or a different global potential.

## 6. Exact verifier and remaining target

The checker verifies the primitive `K_52` kernel, the rational transverse-
plane model, checks the canonical pivot incidences, independently reconstructs
(10) from the exact 52-orbit classification, checks all thirteen nonlinear
incidence witnesses, expands the exact ellipse, classifies all 35 parent-line
intersections with it, and certifies the two wall-pivot segments:

```console
python ai/omreal/DIAG2_PIVOT_ALL_COMPACT_SECOND_WALL_VERIFY.py
```

The remaining universal statement is now sharply global:

> Every connected component of the iterated signed residual-wall graph for a
> realizable proper incomparable signature pair has an exit to the parent
> boundary.

A support order or first-wall Euler count cannot establish this statement,
because (5) is the constant compact-component generator itself.  A proof
needs either a monotone invariant on actual compound wall transitions or an
exact exclusion of closed transition cycles.  Sections 4 and 5 show that
neither raw dimension counting nor the canonical one-coordinate wall pivot
provides that invariant.  No universal multi-coordinate invariant is proved
here, so diagonal two remains open.
