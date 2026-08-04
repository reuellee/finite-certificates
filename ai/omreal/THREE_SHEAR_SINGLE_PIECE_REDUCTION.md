# Three-shear reduction for the third diagonal

## Outcome

This note proves a new compact-support vanishing theorem and applies it to
the entire single-piece column of the third diagonal.  It does **not** prove
the full third diagonal.

For a circuit support union `U`, suppose two moving labels are dominated by
one fixed apex and a third moving label is dominated by another fixed apex.
The resulting three shear parameters need not have a convex joint residence
domain.  Nevertheless, fixing the third parameter leaves a convex
two-dimensional fiber.  Every connected component of the full residence
domain is therefore contractible, and its compact-support cohomology is
concentrated in degree three.  Compact-support Leray descent gives

\[
                         H_c^q(Z;\mathbb Q)=0\qquad(q<3)
\]

for the corresponding intersection `Z` of circuit pieces.

The fixed-apex form first eliminates 38 of the 45 audited generic
five-support orbits which survived the earlier omission/common-apex filter.
A stronger degree-one-plane plus pencil form eliminates the remaining seven
and, by a direct incidence count, every nongeneric case as well.  Thus

\[
                 \boxed{H_c^2(C_{\rho,Q};\mathbb Q)=0
                         \quad\text{for every }|Q|\le5.}
\]

Consequently the full `E_1^(0,2)` column in the third-diagonal circuit-cover
spectral sequence is zero.  In particular, the unique genuine `beta=1`
orbit from `THIRD_DIAGONAL_E1_REDUCTION.md` is eliminated by this topological
argument.  The pair and triple columns remain unresolved.

## 1. Domination data

Let `U` be a set of triples on the eight parent labels.  Say that the moving
label `e` is **dominated by the apex** `f` when

\[
 e\ne f,\qquad e\in I\in U\Longrightarrow f\in I.       \tag{1}
\]

Thus the column shear

\[
                         y_e\longmapsto y_e+t y_f       \tag{2}
\]

preserves every support plane, and hence every derived normal, occurring in
`U`.

The new pattern consists of distinct moving labels `e_1,e_2,e_3` and fixed
apices `f,h`, none of which is moving, such that

\[
 e_1,e_2\in D_f(U),\qquad e_3\in D_h(U).                \tag{3}
\]

The apices may coincide.  When they do, (3) is the rank-three common-apex
case already covered by the simultaneous-shear lemma.  The useful new case
is `f != h`.

No support triple can contain a moving label from each apex block: such a
triple would have to contain both moving labels and both fixed apices.  A
triple may contain `e_1,e_2,f`; its exterior product is still unchanged by
both shears because every new term repeats `y_f`.  Consequently all circuit
conditions are constant along the three-parameter motion

\[
 \begin{aligned}
 y_{e_1}&\longmapsto y_{e_1}+t_1y_f,\\
 y_{e_2}&\longmapsto y_{e_2}+t_2y_f,\\
 y_{e_3}&\longmapsto y_{e_3}+u y_h.
 \end{aligned}                                         \tag{4}
\]

## 2. The block-plus-line shear theorem

> **Block-plus-line three-shear theorem.**  Let
>
> \[
> Z=C_{\rho_1,Q_1}\cap\cdots\cap C_{\rho_t,Q_t}
> \]
>
> be any intersection of closed Gordan circuit pieces, and let `U` be the
> union of their support triples.  If `U` has the domination pattern (3),
> then
>
> \[
>                        H_c^q(Z;\mathbb Q)=0
>                        \qquad(0\le q\le2).            \tag{5}
> \]

**Proof.**  The five labels outside `{e_1,e_2,e_3}` form a labeled
projective frame.  Use it to normalize the parent configuration globally.
For each moving column choose, from the fixed frame, a covector which
vanishes on its apex and is nonzero on that moving column.  Uniformity makes
the latter evaluation nonzero throughout the parent chirotope cell.  Retain
the normalized class of `y_(e_i)` modulo the span of its apex.  Together
with the five fixed columns, these data define a semialgebraic quotient map

\[
                              \pi:Z\longrightarrow Z'. \tag{6}
\]

Every nonempty fiber of (6) is precisely the set `Omega` of parameters
`(t_1,t_2,u) in R^3` for which (4) remains in the fixed open parent
chirotope cell.  Equation (3) makes every circuit witness invariant, so no
additional condition cuts the fiber.

Fix `u`.  Every parent four-bracket is affine jointly in `(t_1,t_2)`.
Indeed, multilinearity gives at most one occurrence of either parameter,
and the possible `t_1t_2` coefficient has two copies of `y_f` and therefore
vanishes.  The fixed-`u` section

\[
                 \Omega_u=\{(t_1,t_2):(t_1,t_2,u)\in\Omega\}
\]

is consequently an intersection of strict affine halfspaces: it is empty or
open convex.

Let `Omega_0` be a connected component of `Omega`.  Its projection to the
`u`-axis is a connected open interval `J`.  A nonempty convex section
`Omega_u` cannot meet two components of `Omega`; hence the fibers of
`Omega_0 -> J` are the whole nonempty convex sections.  Locally persistent
points, a partition of unity, and straight-line motion in each section give
a continuous section and a deformation retraction

\[
                              \Omega_0\simeq J.         \tag{7}
\]

Thus every component of `Omega` is contractible.  It is also an oriented
open three-manifold, being a component of an open subset of `R^3`.
Poincare duality therefore gives

\[
 H_c^j(\Omega_0;\mathbb Q)
       \cong H_{3-j}(\Omega_0;\mathbb Q)=0\qquad(j<3). \tag{8}
\]

Semialgebraicity gives finitely many components, so (8) holds for the whole
fiber.  Proper base change for `R pi_!` and the compact-support Leray
spectral sequence now have no fiber row below degree three.  Hence the total
compact-support cohomology of `Z` vanishes below degree three, proving (5).
QED.

The theorem uses neither joint convexity of the full three-parameter domain
nor a column-torus escape.  The earlier exact two-apex midpoint obstruction
is compatible with the proof: it shows only that `Omega` need not itself be
convex, while (7) uses convexity of the two-dimensional sections.

## 3. A degree-one plane plus a pencil

There is a more flexible source of the same convex-block topology.

> **Degree-one-plane plus pencil theorem.**  Let `Z` be an intersection of
> circuit pieces with support union `U`.  Suppose a label `e` occurs in the
> unique support triple
>
> \[
>                             I=\{e,a,b\},              \tag{9}
> \]
>
> and a label `g notin I` has `1<=deg_U(g)<=2`.  Then
>
> \[
>                         H_c^q(Z;\mathbb Q)=0
>                         \qquad(0\le q\le2).           \tag{10}
> \]

**Proof.**  Move `e` through its full support plane by

\[
                         y_e\longmapsto y_e+s y_a+t y_b. \tag{11}
\]

This fixes the unique derived normal containing `e`.  Because `g notin I`
and `e` occurs nowhere else, no support triple containing `g` contains `e`.
If `deg_U(g)=1`, shear `g` toward either of the two fixed partners in its
unique triple.  If `deg_U(g)=2`, let `H_1,H_2` be its two incident support
three-planes.  Uniformity makes them distinct, so their vector-space
intersection is a two-plane containing `y_g`.  Move the positive projective
ray of `y_g` along the resulting open residence interval.  In either case
write the one parameter as `u`.  Every support plane through `g` stays fixed;
its normal changes only by a positive scalar before the parent residence
boundary.  Rescaling the corresponding coordinate in each piece's separate
Gordan weight simplex preserves every circuit witness.

Choose a projective frame among five of the six labels different from
`e,g`, and quotient by the invariants of (11) and the `g`-pencil.  A fiber is
an open parameter domain `Omega subset R^3`.  At fixed `u`, every parent
four-bracket is affine jointly in `(s,t)`, because only the single column
`y_e` carries those two parameters.  Hence every `Omega_u` is open convex.
The component retraction and compact-support Leray argument from Section 2
apply verbatim, proving (10).  QED.

The theorem includes support-plane motion not generated by a parent-column
shear: in the degree-two case the second generator of
`H_1 intersection H_2` need not be a parent column.  This is why it removes
the last fixed-apex residues below.

## 4. Complete vanishing of the single-piece column

> **Single-piece degree-two theorem.**  For every signature `rho` and every
> circuit support `Q` of at most five parent triples,
>
> \[
>                   H_c^q(C_{\rho,Q};\mathbb Q)=0
>                   \qquad(0\le q\le2).                \tag{12}
> \]

**Proof.**  If `Q` omits a parent label, deleting that label supplies the
globally oriented open three-cell residence fiber from the existing
projective-plane-pencil lemma, so compact-support cohomology vanishes below
degree three.

Suppose `Q` covers all eight labels.  Its at most five triples have at most
fifteen label occurrences.  Since every label has positive degree and
`15<2*8`, some label `e` has degree one; write its unique triple as
`I={e,a,b}`.  Among the five labels outside `I`, some label `g` has degree at
most two.  Otherwise those five labels contribute at least fifteen
occurrences and the three labels of `I` contribute at least three more,
contradicting the total bound of fifteen.  Coverage makes `deg_Q(g)>=1`.
The degree-one-plane plus pencil theorem applies and proves (12).  QED.

The proof uses only the support-size bound, not genericity, residual-wall
regularity, positivity of all five weights, or a weight gauge.  It therefore
includes structural supports, residual-wall degenerations, and all
zero-weight faces of the closed cofinal pieces.

In the third-diagonal spectral sequence

\[
 E_1^{p,q}=\bigoplus_{\alpha_0<\cdots<\alpha_p}
 H_c^q(C_{\alpha_0}\cap\cdots\cap C_{\alpha_p};\mathbb Q),
\]

equation (12) gives the exact simplification

\[
                         \boxed{E_1^{0,2}=0}.           \tag{13}
\]

The target `H_c^2(B_S)` may still receive contributions from
`E_1^(1,1)` and `E_1^(2,0)`, together with their differentials.  Thus (13)
is one complete column, not the third diagonal itself.

## 5. Exact audit of the former 45 generic orbit types

The independent third-diagonal census left 45 generic support orbits after
requiring coverage of all eight labels, common-apex rank at most two, and at
least one residual cofactor.  Their earlier split was

| common-apex rank `delta` | `beta` | orbits | labeled supports |
|---:|---:|---:|---:|
| 1 | 0 | 5 | 65,520 |
| 2 | 0 | 39 | 692,160 |
| 2 | 1 | 1 | 2,520 |
| **total** |  | **45** | **760,200** |

The domination test (3) eliminates 38 of the 40 `delta=2` orbits, including
the `beta=1` orbit.  It initially leaves the five `delta=1` orbits and two
`delta=2,beta=0` orbits:

```text
345/246/156/137/128
245/356/237/147/128
356/456/237/147/128
245/156/356/347/128
256/456/137/347/128
146/356/347/157/128
246/356/347/157/128
```

Their exact orbit sizes sum as follows.

| residue | orbits | labeled supports |
|---|---:|---:|
| `delta=1, beta=0` | 5 | 65,520 |
| `delta=2, beta=0` | 2 | 25,200 |
| **total** | **7** | **90,720** |

Every one of these seven supports has a degree-one-plane plus pencil witness,
so theorem (12) eliminates the apparent residue.  The checker
`verify_three_shear_single_piece_filter.py` verifies both stages, all orbit
sizes under `S_8`, the centered-incidence ranks giving `beta=0`, and the
stable fingerprint tying its 45 inputs to the two earlier independent
censuses.

## 6. Exact scope

The numerical intermediate statement `45 -> 7 -> 0` starts from the audited
generic list, but theorem (12) does not: it covers every support of size at
most five and the entire associated closed circuit piece.  No smaller-support
boundary has been discarded.

The third diagonal still contains pairwise `H_c^1` and triple-intersection
`H_c^0` columns.  Exact examples in `THIRD_DIAGONAL_E1_REDUCTION.md` show
that neither column vanishes by the earlier fixed-deletion fiber tests.
Therefore this result removes the single-piece column completely but does
not establish `H_c^2(B_S)=0`.

## 7. Two-pencil corollary and propagation to diagonals four through eight

The same argument has a two-dimensional version which is useful on
multi-piece intersections.

> **Two-pencil theorem.**  Let `Z` be an intersection of circuit pieces with
> support union `U`.  Suppose distinct labels `e,g` each have support degree
> at most two and no triple of `U` contains both.  Then
>
> \[
>                         H_c^q(Z;\mathbb Q)=0
>                         \qquad(0\le q\le1).           \tag{14}
> \]

**Proof.**  A degree-zero label has an arbitrary one-dimensional residence
shear.  A degree-one label can be sheared toward either fixed partner in its
unique support triple.  A degree-two label moves along the positive
projective interval in the intersection of its two distinct incident support
planes.  Because no support triple contains both moving labels, each motion
leaves the other label's support planes fixed.  All involved normal rays are
therefore fixed up to positive scale, so all Gordan witnesses persist.

Use a projective frame avoiding `e,g` and quotient by the two pencil
parameters.  A fiber is an open set `Omega subset R^2`; fixing either
parameter leaves an intersection of strict affine inequalities in the other,
hence an interval.  Every connected component projects with interval fibers
to an interval and is contractible.  It is an oriented open two-manifold, so
its compact-support cohomology is concentrated in degree two.  Compact-
support Leray gives (14).  QED.

Together with the original one-pencil escape, define three purely
combinatorial rejection predicates for a support union `U`:

* `P1`: some label has degree at most two (or has a fixed partner in all its
  incident triples); then `H_c^0=0`;
* `P2`: two degree-at-most-two labels occur together in no support triple;
  then `H_c^0=H_c^1=0` by (14);
* `P3`: a degree-one label `e` and a degree-at-most-two label outside its
  unique triple exist; then `H_c^0=H_c^1=H_c^2=0` by (10).
* `P4`: a label is omitted and a distinct label has degree at most two; then
  `H_c^0=...=H_c^3=0` by the omitted-label theorem proved below.

The `P4` test is applied on the uncofinalized closed cover by supports of
size at most five.  Padding a smaller witness by zero weights into a
five-support can add the omitted label to the *piece index*, so omission is
not a valid predicate on that padded maximal piece.  No zero-weight face is
lost: the uncofinalized cover contains it as its own closed circuit piece.

These are sufficient rejection tests, not converses.  They apply to the
four lowest cochain degrees in every diagonal complex.  If `t` is the number of
intersected circuit pieces, the exact three-total-degree computation for
diagonal `s` may discard the following terms:

| total degree | discard by `P4` (`q=3`) | discard by `P3` (`q=2`) | discard by `P2` (`q=1`) | discard by `P1` (`q=0`) |
|---:|---:|---:|---:|---:|
| `s-2` | `t=s-4` | `t=s-3` | `t=s-2` | `t=s-1` |
| `s-1` | `t=s-3` | `t=s-2` | `t=s-1` | `t=s` |
| `s` | `t=s-2` | `t=s-1` | `t=s` | `t=s+1` |

Terms with a negative or zero piece count are absent.  Thus the theorem
propagates unchanged through `s=4,...,8`: it removes four low
fiber-cohomology bands before any CAD or relative-cellular matrices are
built.  Apart from the omitted-support predicate `P4`, it does not address
the `q>=3` bands which dominate the early piece columns of those diagonals.

### A safe degree-three upgrade for omitted supports

There is one genuine improvement in the next cohomological degree.

> **Omitted-label plus pencil theorem.**  Suppose the support union `U`
> omits a label `e`, and some distinct label `g` has support degree at most
> two.  Then
>
> \[
>                         H_c^q(Z;\mathbb Q)=0
>                         \qquad(0\le q\le3).          \tag{15}
> \]

Indeed, the omitted column `e` moves through its full three-dimensional
parent residence chamber without changing a circuit normal.  Move `g`
through any one-dimensional support-preserving pencil (an arbitrary line if
its degree is zero, a partner shear if its degree is one, or the intersection
of its two support planes if its degree is two).  Normalize using five of the
six columns different from `e,g`, and quotient these four parameters.  At a
fixed pencil parameter every parent bracket is affine in the three affine
coordinates of `e`.  The section is therefore empty or open convex.  The
projection of each connected component to the pencil coordinate is an open
interval, and the component retracts onto that interval exactly as in
Section 2.  Each fiber component is consequently a contractible oriented
open four-manifold.  The `R pi_!` argument has no row below four and proves
(15).

For a single support of at most five triples which omits `e`, the other seven
labels carry at most fifteen incidences.  Hence one of them has degree at
most two, so (15) always applies.  Thus the possible fourth-diagonal
single-piece term `H_c^3(C_{rho,Q})` is supported entirely on cover-all
supports.

For a cover-all support, incidence counting still supplies a degree-one
label `e` and **two** distinct degree-at-most-two labels outside its unique
triple.  This gives four support-preserving parameters on only three moving
columns.  It does not, by itself, extend (15).  The plane block and the two
pencils interact through bilinear parent-bracket terms, and the top sheaf
`R^3 pi_! Q` records births, mergers, and deaths of the connected components
of the three-dimensional residence fibers.  Showing that one distinguished
component escapes along the second pencil does not rule out a compactly
supported section carried by other component branches.

This is a real logical obstruction rather than a technical preference.
Separate convexity of the two parameter blocks is insufficient: for any
nonzero `a in R^2`,

\[
 \Omega=\{(x,y)\in\mathbb R^2\times\mathbb R^2:
                    (x+a)\mathbin\cdot(y+a)>0\}        \tag{16}
\]

contains the origin and has open convex fibers under either coordinate
projection.  Translation identifies it with
`{(u,v):u dot v>0}`.  Projection to `u in R^2-{0}` has contractible
half-space fibers and a section `v=u`, so
`Omega` is homotopy equivalent to `S^1`.  Poincare duality on this oriented
open four-manifold gives

\[
                         H_c^3(\Omega;\mathbb Q)
                         \cong H_1(\Omega;\mathbb Q)
                         \cong\mathbb Q.               \tag{17}
\]

Therefore a proof of the cover-all `H_c^3` column needs an additional
oriented-matroid constraint or an explicit calculation of the top
component sheaf.  The light-label count alone cannot establish it.

Even refining the quotient by connected components and proving that every
refined component reaches an end is not sufficient unless splitting and
remerging are excluded.  Put

\[
 A=\{(t,x)\in\mathbb R^2:t^2+x^2>1\},\qquad
 \widetilde\Omega=A\times\mathbb R^2,
\]

and project to `t`.  Every fiber component is a contractible oriented open
three-manifold.  For `|t|>1` the fiber is connected; for `|t|<=1` it has two
components.  Both branches merge into the unique component on either side
and every branch can be followed to infinity.  Nevertheless the component
Reeb graph contains the compact loop made by the doubled interval
`[-1,1]`.  Equivalently, `R^3 pi_! Q` has a compactly supported
anti-diagonal section.  Since `A` is the exterior of a disk,

\[
 H_c^3(\widetilde\Omega;\mathbb Q)
   \cong H_c^1(A;\mathbb Q)
   \cong\mathbb Q.
\]

Thus the missing condition is component persistence with no split--remerge
cycle (or a direct proof that the corresponding top-sheaf differential is
injective), not merely noncompactness of component trajectories.

### Compact-support and closed-face audit

None of the preceding Leray arguments assumes that the quotient map is
proper.  For a semialgebraic quotient `pi:Z -> Z'`, compactify the parameter
coordinates fiberwise, take the closure of its graph, and write

\[
                 Z\mathrel{\mathop{\hookrightarrow}^{j}}\overline Z
                    \mathrel{\mathop{\longrightarrow}^{\bar\pi}}Z',
\]

where `bar pi` is proper.  By definition
`R pi_! Q = R bar pi_* j_! Q`; proper base change identifies its stalk at
`b` with `H_c^*(pi^{-1}(b);Q)`.  The identity

\[
 R\Gamma_c(Z;\mathbb Q)
   =R\Gamma_c(Z';R\pi_!\mathbb Q)
\]

then gives the compact-support Leray spectral sequence used above.  If all
fiber cohomology rows below `d` vanish, so does `H_c^q(Z)` for `q<d`, with no
claim about `R^d pi_!`.  This last qualification is exactly why (16)--(17)
blocks the proposed cover-all degree-three upgrade.

The argument is also on the closed cofinal circuit pieces, not just their
full-weight strata.  A support-plane motion sends each derived normal in a
specified support to a positive multiple of itself before the parent
residence boundary.  Divide the corresponding Gordan coordinate by that
multiple and renormalize the simplex.  A zero coordinate remains zero, so
the motion preserves every lower-support face.  The only endpoints omitted
from a residence fiber are parent nonuniformity boundaries, which lie
outside `X`; they are precisely the ends measured by compact supports.

The saved row-2599 obstruction examples delimit the gain sharply.  The
pair used to exhibit a nonzero common-light residence-fiber `H_c^1` has union
degree vector `(4,5,3,5,4,4,2,3)`, hence only one degree-at-most-two label and
fails `P2`.  The triple obstruction has degree vector
`(3,5,5,4,4,4,5,3)` and fails even `P1`.  Therefore (14) does not silently
dispose of either known hard term.

There is a stronger exact obstruction at the hard triple.  Retain the three
actual signed sparse Gordan tensors `c_0,c_4,c_3` rather than only their
support planes.  The simultaneous line stabilizer

\[
 \{(A,\mu_0,\mu_4,\mu_3):
          A\cdot c_j=\mu_jc_j\text{ for }j=0,4,3\}
 \subset\mathfrak{gl}_8\oplus\mathbb Q^3
\]

is one-dimensional and consists only of scalar matrices (with the induced
degree-three tensor scalings).  The first two tensors alone have a
two-dimensional stabilizer, which is an internal positive control.  Thus the
triple is rigid even under the full exact sparse-tensor stabilizer, not just
under support-plane-preserving column shears.  This rules out a common
`GL(8)` orbit escape for that term; it still does not prove the component is
compact.  The exact modular-rank certificate is
`verify_third_diagonal_full_tensor_rigidity.py`.

## Reproduction

```console
python ai/omreal/verify_three_shear_single_piece_filter.py
python ai/omreal/verify_third_diagonal_full_tensor_rigidity.py
python ai/omreal/verify_fourth_single_piece_light_count.py
```
