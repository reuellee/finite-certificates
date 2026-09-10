# Third diagonal: double contraction has no dimension-only payoff

## Verdict

Literal double contraction does not give the third diagonal from
multiconvexity or semialgebraic dimension alone.

For three private extensions the partial quotient base has dimension six.
After the fixed-sign row normalizations, each of the two lift-height rows
also has dimension six.  Fixing either row makes the inequalities in the
other row affine, so every double-lift fiber is homotopy equivalent to an
open subset of `R^6`.  This proves that an individual fiber has no ordinary
homology in degrees at least six.

That fiber bound is exactly one degree too weak for the total target
`H_6`.  A sharp normalized model below has

* a contractible six-dimensional base;
* two six-dimensional height rows;
* open convex fibers in either height row;
* only two fiber types, separated by one smooth base wall; and
* total homotopy type `S^6`.

Thus neither a rank stratification nor a proper compactification can finish
the argument without computing the exit/specialization maps.  The first
missing group is already the codimension-one specialization of fiber
`H_5`.

This is a generic bilinear no-go.  It does not satisfy the special
alternating-minor/Koszul identities of an actual double lift.  Those
identities are the only remaining possible source of a direct-contraction
proof, and their present support bounds do not remove the all-bilinear hard
case.

## 1. Exact dimensions for three private extensions

Contract two fixed parent columns.  The six remaining parent quotient points
give a normalized rank-two realization base of dimension three.  Each of the
three private quotient points contributes one coordinate, so

\[
                         \dim W=3+3=6.                 \tag{1}
\]

There are nine uncontracted columns: six parent and three private.  A height
row has nine entries.  Quotienting by the two-dimensional affine-functional
gauge leaves seven homogeneous coordinates, and fixing one prescribed
nonzero bracket removes positive row scale.  Hence each normalized height row
is an affine `R^6`.

For fixed first row `h`, every remaining inequality is affine in the second
row `k`.  Its nonempty fiber is open convex.  The usual local-section,
partition-of-unity, and straight-line argument gives

\[
                  L_b\simeq P_b\subset\mathbb R^6,     \tag{2}
\]

where `P_b` is open and semialgebraic.  Therefore

\[
                  \widetilde H_q(L_b;\mathbb Z)=0
                  \qquad(q\ge6).                       \tag{3}
\]

The homogeneous warning

\[
 \{(x,y)\in\mathbb R^7\times\mathbb R^7:x\mathbin\cdot y>0\}
       \simeq\mathbb R^7\setminus\{0\}\simeq S^6      \tag{4}
\]

has the right pre-normalization row dimension, but not the fixed affine
normalization in (2).  The next section gives a no-go with the exact
normalized `6+6` dimensions.

## 2. A normalized two-stratum countermodel

Let

\[
 W=\mathbb R_b^6,\qquad h,k\in\mathbb R^6,\qquad
 Z=\{(b,h,k):b_1^2+h\mathbin\cdot k>0\}.               \tag{5}
\]

For fixed `(b,h)`, the allowed `k` form an open halfspace, all of `R^6`, or
the empty set.  The same statement holds with `h` and `k` reversed.  Thus
(5) is separately open-convex in the two height rows.

Project to `(b,h)`.  A nonempty `k`-fiber exists exactly when

\[
                             (b_1,h)\ne0.               \tag{6}
\]

There is an explicit section `k=h`.  Indeed,
`b_1^2+||h||^2>0` on (6), and straight-line interpolation from any allowed
`k` to `h` remains allowed because

\[
 b_1^2+h\mathbin\cdot((1-t)k+th)
 =(1-t)(b_1^2+h\mathbin\cdot k)
   +t(b_1^2+\lVert h\rVert^2)>0.                       \tag{7}
\]

Consequently

\[
 \begin{split}
 Z&\simeq
 \{(b,h):(b_1,h)\ne0\}\\
  &\cong\mathbb R^5\times(\mathbb R^7\setminus\{0\})
   \simeq S^6,                                         \tag{8}
 \end{split}
\]

and hence

\[
                             H_6(Z;\mathbb Z)=\mathbb Z. \tag{9}
\]

The fixed-base fibers make the obstruction precise:

\[
 L_b\simeq
 \begin{cases}
 \mathbb R^6,&b_1\ne0,\\
 \mathbb R^6\setminus\{0\}\simeq S^5,&b_1=0.
 \end{cases}                                           \tag{10}
\]

The two contractible side fibers fill the `S^5` on the central stratum from
opposite sides.  Their union is its suspension `S^6`.  A correct compactified
Leray calculation must therefore retain a codimension-one degree-five
vanishing cycle.  Ordinary fiber groups without the specialization/exit map
lose exactly the class in (9).

## 3. Minimal relative-Leray obligations

For a proper semialgebraic compactification as a map of pairs, base degree is
at most six and (3) removes only fiber degrees `q>=6`.  Total degree six can
still occur in all six bidegrees

\[
 (p,q)=(1,5),(2,4),(3,3),(4,2),(5,1),(6,0).            \tag{11}
\]

The example (5) realizes the first one.  Therefore any safe theorem must, at
a minimum, kill the degree-five relative specialization group across every
codimension-one Hardt wall.  In the actual one-row projection, Alexander
duality in a normalized first-height chamber `C_b` homeomorphic to `R^6`
identifies this top fiber question as

\[
 \widetilde H_5(P_b;\mathbb Q)
       \cong H_c^0(C_b\setminus P_b;\mathbb Q).         \tag{12}
\]

Thus the first missing statement is already an all-strata proper-escape
theorem for every connected component of the one-row Gordan bad locus,
together with coherent specialization in `b`.  Lower fiber degrees require
the analogous `H_c^1,H_c^2,H_c^3,H_c^4` incidence information, and `(6,0)`
requires control of the component/exit cosheaf of the nonempty-fiber locus
itself.

A dimension-only conditional theorem would need relative fiber cosheaves
concentrated in degree zero **and** vanishing of the base-degree-six group
with those component coefficients.  This is substantially stronger than
the pointwise statement (3).

## 4. What the alternating-minor identity does and does not give

Before positive scale normalization, the height quotient for three private
extensions is

\[
                    V=\mathbb R^9/\langle1,t\rangle,
                    \qquad\dim V=7.                    \tag{13}
\]

Every row omitting both contracted columns has the Koszul form

\[
             n_I(h)=h^T\Omega_I,qquad
             \Omega_I^T=-\Omega_I,qquad n_I(h)h=0.    \tag{14}
\]

Hence all-bilinear normals lie in the six-plane `h^perp`; a support-minimal
all-bilinear circuit uses at most seven rows.  A circuit with exactly one
contracted-column constant row is impossible by pairing with `h`, and an
eight-row circuit has at least two constant rows.

For a fixed positive dependence with constant-row sum `c`, the first-height
equation is

\[
                             h^TS+c=0,                  \tag{15}
\]

with `S` alternating of odd order seven.  If `c` is nonzero, `ker S` gives a
nonprojective fixed-weight direction; normalization can be restored by a
positive rescaling together with the same rescaling of the constant-row
weights.  This removes the even-dimensional invertible-pencil obstruction
from `DIAG2_PIVOT_DOUBLE_FIBER_KOSZUL.md` for that class of circuits.

It does not settle (12).  In the all-bilinear case `c=0`, the current height
itself lies in `ker S`, and `S` may have rank six.  Then

\[
                             \ker S=\mathbb Rh,          \tag{16}
\]

so the only fixed-weight kernel direction is positive row scale, already
removed by normalization.  No theorem in the repository excludes (16) for
an allowed positive circuit, and fixed-weight motion would in any case need
to be glued across changing circuit weights and zero-weight faces.  The
alternating identity therefore prunes the first endpoint; it does not prove
the degree-five relative vanishing cycle absent.

## 5. Strategic comparison

The direct double-contraction route is not presently shorter than the dual
third-diagonal route.  It replaces the pair balanced-end map by six relative
Leray rows, beginning with the still-unproved all-bilinear escape and its
codimension-one specialization.

Diagonal nine has the simplest algebraic target, connectivity of a labeled
chamber graph, and its finite graph theorem is complete once a roadmap is
supplied.  It is nevertheless farther from a global proof: no complete
nine-dimensional roadmap exists for even one parent, the current exact
artifacts cover only lines, disks, and a repaired finite training network,
and parent infinity plus all `2,604` realizable parent classes remain.

The fastest honest route to a third proved entry is therefore still
diagonal three, but not by further pointwise escape counting alone.  The next
proof-bearing object should be a coherent signed factor-frontier atlas which
simultaneously computes

1. triple component escape; and
2. the balanced pair end map of `DIAG3_PAIR_DIFFERENTIAL_ENDS.md`.

Double contraction should remain a regression and possible source of local
Koszul lemmas.  Diagonal-nine roadmap work should remain a tooling pilot
until one full parent, including infinity, has a certified cover.
