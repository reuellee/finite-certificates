# Column-torus escape: exact scope, obstruction cones, and a viable quotient strategy

## Outcome

Positive column scaling gives a useful **finite toric boundary fan** for every
tuple of Gordan circuit supports.  Its cones are decided by a small exact
linear program, and the remaining quotient directions are precisely the
weight-gauge invariants already measured by `beta`.

It does **not**, by itself, produce an escape in the normalized parent
realization space.  Column scaling changes homogeneous representatives of the
same eight projective points, so every such one-parameter subgroup projects to
a constant point of `X`.  In particular, an argument that sends every lifted
Gordan witness to a toric boundary face would not prove either
`H_c^0(B)=0` or `H_c^1(B)=0`.

The viable version of the strategy is therefore:

1. quotient the column-scaling directions exactly;
2. use their Hilbert--Mumford cones only to organize and prune the boundary
   faces of the witness compactification;
3. search for **non-gauge** real-tropical directions in the nine projective
   parent coordinates and the `beta` invariant weight coordinates; and
4. compute the degree-zero and degree-one relative cohomology of the resulting
   compactification and its genuine boundary at infinity.

The exact row-2599 residues make this sharper than a generic proposal.  For
the stored `4+5, beta=0` and `5+5, beta=1` positive pencil-rigid support pairs,
every proper coherent column-torus face has a non-pencil-rigid support union.
Thus the toric boundary is already eliminated by the projective-plane-pencil
test; only the interior quotient locus can carry the unresolved obstruction.

## 1. The column torus is vertical gauge

Let `R_GL(M)` be the space of realizing `4 by 8` matrices modulo left
`GL(4,R)`, and let `X` be the normalized projective realization space.  The
effective positive column torus is

\[
 T=(\mathbb R_{>0})^8/\mathbb R_{>0,\mathrm{diag}}
   \cong (\mathbb R_{>0})^7.
\]

The fixed labeled projective-frame normalization gives

\[
 \mathcal R_{GL}(M)\cong X\times T.
\]

Every extension feasibility condition is projectively invariant.  Hence, if
`B` is any bad locus or intersection of bad loci in `X`, its lift is

\[
                         \widetilde B=B\times T.       \tag{T1}
\]

This yields a useful no-go theorem.

> **Vertical-torus no-go theorem.**  Every nonempty component of
> `widetilde B` has an escaping column-torus one-parameter subgroup, whether
> or not the corresponding component of `B` is compact.  Under the logarithm
> `T` is `R^7`, so
> \[
>       H_c^{q+7}(\widetilde B;\mathbb Q)
>          \cong H_c^q(B;\mathbb Q),                  \tag{T2}
> \]
> and `H_c^k(widetilde B)=0` for `k<7`.
> Consequently low-degree vanishing in the lift says nothing about
> `H_c^0(B)` or `H_c^1(B)`.

**Proof.**  A column scaling sends each nonzero vector `y_e` to a positive
multiple of itself, hence fixes its projective point.  Formula (T1) follows
from the global normalization section.  Any nonconstant one-parameter
subgroup escapes in the `T` factor while its image in `X` is constant.
Formula (T2) is compact-support Kunneth together with
`H_c^7(R^7;Q)=Q` and all other compact-support groups of `R^7` zero.  QED.

This is also why the existence of a toric limit of the **weights** cannot be
silently reinterpreted as a path to the boundary of `X`.

## 2. Exact Hilbert--Mumford cones of a support tuple

Let `H=(Q_1,...,Q_t)` be a tuple of positive circuit supports.  Write
`chi_I in {0,1}^8` for the incidence vector of a parent triple `I`.  Positive
column scaling

\[
                  y_e\longmapsto \exp(r u_e)y_e
\]

multiplies the derived normal `a_I` by
`exp(r <chi_I,u>)`.  The same signed dependence is therefore represented by
the normalized weights

\[
 \lambda_{j,I}(r)=
 \frac{\lambda_{j,I}\exp(-r\langle\chi_I,u\rangle)}
 {\sum_{K\in Q_j}\lambda_{j,K}
                    \exp(-r\langle\chi_K,u\rangle)}.  \tag{T3}
\]

Its limiting support is

\[
 F_j(u)=\mathop{\rm argmin}_{I\in Q_j}
                     \langle\chi_I,u\rangle.          \tag{T4}
\]

For a prescribed tuple of nonempty faces `F=(F_1,...,F_t)`, choose
`I_j in F_j`.  The exact Hilbert--Mumford cone is

\[
\begin{split}
 \mathcal C_H(F)=\{[u]\in\mathbb R^8/\mathbb R\mathbf1:\;&
 \langle\chi_I-\chi_{I_j},u\rangle=0
                         &&(I\in F_j),\\
 &\langle\chi_K-\chi_{I_j},u\rangle>0
                         &&(K\in Q_j\setminus F_j),\ \forall j\}.
                                                               \tag{T5}
\end{split}
\]

Thus a proposed face tuple is coherent if and only if a rational homogeneous
strict LP is feasible.  There is an exact certificate requiring no numerical
optimization.  Let `E` be the equality matrix in (T5), restrict the inequality
rows to `V=ker(E)`, and call the resulting covectors `b_1,...,b_m`.  Gordan's
theorem gives

\[
 \mathcal C_H(F)\ne\varnothing
 \quad\Longleftrightarrow\quad
 \nexists\,\mu\in\mathbb R_{\ge0}^m\setminus\{0\}
       \text{ with }\sum_r\mu_r b_r=0.                \tag{T6}
\]

A minimal obstruction on the right is a positive vector in a one-dimensional
rational nullspace.  Enumerating these small supports is therefore an exact
finite LP algorithm.  Equivalently, because (T5) is homogeneous and rational,
each strict `>0` can be normalized to `>=1` whenever the cone is nonempty.

If `D_H` is the log-weight gauge matrix with rows
`chi_I-chi_(I_j)`, the cone which retains the full support in every block is

\[
 L_H=\ker(D_H)/\mathbb R\mathbf1,
 \qquad \dim L_H=7-\operatorname{rank}(D_H).           \tag{T7}
\]

Every `u` outside `L_H` sends at least one weight block to a proper face.  A
generic `u` has a unique minimum on every finite `Q_j`, so **every** support
tuple has a simultaneous vertex degeneration.  This universality is another
warning: toric weight degeneration alone cannot distinguish a compact bad
component from a noncompact one.

The quotient weight dimension remains

\[
 \beta(H)=\sum_j(|Q_j|-1)-\operatorname{rank}(D_H).    \tag{T8}
\]

Vectors in `ker(D_H^T)` give all invariant Laurent monomials.  Formulae
(T5)--(T8) add the missing boundary fan to the weight-gauge theorem.

## 3. Exact row-2599 face-fan calculation

The checker

```console
python ai/omreal/verify_torus_escape_cones.py
```

uses rational row reduction and the Gordan alternative (T6).  It studies the
two exact positive, support-minimal, proper, incomparable, pencil-rigid pairs
already verified in the row-2599 certificate.

| pair | `rank(D_H)` | `beta` | `dim L_H` | coherent proper face tuples | vertex tuples | pencil-rigid proper faces |
|---|---:|---:|---:|---:|---:|---:|
| `5+5` | 7 | 1 | 0 | 784 | 25 | 0 |
| `4+5` | 7 | 0 | 0 | 464 | 20 | 0 |

For the `4+5` tuple, all `31*15-1=464` non-full face tuples are coherent;
the omitted full/full tuple would require a nontrivial vector in `L_H`, which
does not exist.  For the `5+5` tuple, 784 proper face tuples are coherent.
Most importantly, every proper coherent face union in both examples fails the
existing pencil-rigidity test.  Therefore any toric boundary complex for these
two support strata has only already-prunable proper faces.

The stronger statement for every stored residue is false, and the same
checker gives an exact counterexample.  Across all 65 row-2599 pencil-rigid
occurrences (55 distinct support pairs), there are 137 proper face tuples whose
union remains pencil-rigid; 39 are coherent, occurring on 28 distinct `5+5`
pairs.  Their face-size distribution is

| surviving face sizes | coherent tuples |
|---|---:|
| `4+5` | 28 |
| `3+5` | 7 |
| `4+4` | 4 |

Neither of the two distinct stored `4+5` pairs has such a face.  A concrete
`5+5` counterexample is

\[
\begin{aligned}
 Q_1&=123/124/256/357/478,\\
 Q_2&=123/145/367/468/178.
\end{aligned}
\]

For

\[
                   u=(0,2,1,1,1,0,1,1),              \tag{T8a}
\]

all five triples of `Q_1` have weight three; the last four triples of `Q_2`
have weight two, while its `123` has weight three.  Hence the limit is
`(Q_1,Q_2 minus {123})`.  The triple `123` is shared with `Q_1`, so the union
of distinct triples is unchanged and remains pencil-rigid.  This exactly
falsifies the tempting claim that every proper toric face is removed by the
pencil lemma.

This is useful boundary information, but not a vanishing theorem: (T3) changes
homogeneous representatives and weights while leaving the normalized parent
point fixed.  It does not give a path from the pencil-rigid interior locus to
one of the prunable loci inside `X`.

## 4. The correct tropical quotient cone

Fix the projective-frame chart.  Uniformity makes the nine free normalized
coordinates nonzero, and their signs are fixed by the parent chirotope, so
their absolute values give positive coordinates `x in (R_>0)^9`.  Coordinate
valuations alone do **not** see every end of `X`: a parent bracket can tend to
zero while all nine coordinates tend to finite nonzero values.  Use instead
the positive graph embedding which adjoins every signed parent-bracket slack

\[
                    b_J=\epsilon_J[\,J\,](x)>0.       \tag{T9a}
\]

The graph equations `b_J-epsilon_J[J](x)=0` retain the original space and
make every residence-wall end visible as a positive valuation of some `b_J`.
Unbounded or zero coordinate ends are already visible in `x`.  In a lifted
Gordan incidence chart, also retain seven column-length coordinates `ell` and
the `m=sum_j(|Q_j|-1)` log-weight ratios `z`.

At the valuation level the vertical gauge subspace is

\[
 G_H=\{(0,0,u,-D_Hu):u\in\mathbb R^8/\mathbb R\mathbf1\}
 \subset \mathbb R^9_x\oplus\mathbb R^{70}_b
          \oplus\mathbb R^7_\ell\oplus\mathbb R^m_z. \tag{T9}
\]

A pure column one-parameter subgroup lies in `G_H` and has zero image in the
quotient.  A candidate **genuine** escape must instead have nonzero class in

\[
 \bigl(\operatorname{Trop}_{\mathbb R}
              \widetilde\Gamma_H\bigr)/G_H.           \tag{T10}
\]

Concretely, its non-gauge coordinates are the nine projective valuations,
the dependent but boundary-detecting parent-bracket valuations, and the
`beta(H)` valuations of invariant Laurent weight monomials.  When `beta=0`,
every weight valuation is gauge and only the normalized parent configuration
can certify escape.  When `beta=1`, the one primitive balanced monomial from
`ker(D_H^T)` supplies the additional independent quotient coordinate.

There is a finite exact route to (T10).  On a fixed support and sign stratum:

1. write the bracket graph equations, parent inequalities, and Gordan
   incidence as signed Laurent polynomials in the positive chart;
2. choose the terms attaining minimal valuation in each polynomial;
3. solve the resulting rational equalities and strict inequalities on the
   valuation vector by LP;
4. quotient the cone by (T9); and
5. solve the corresponding positive real initial equations.

Every semialgebraic branch to infinity supplies such a nonzero quotient
valuation after a Puiseux reparametrization.  Conversely, a positive
nonsingular solution of an initial system lifts by the implicit-function
argument to a real Puiseux branch.  Merely satisfying the tropical
**prevariety** conditions polynomial by polynomial is only necessary; one
must check the initial ideal, or at least a nonsingular initial solution.
This distinction prevents a second false escape proof.

The finite toric face fan from Section 2 handles weight-simplex boundary
strata recursively.  In the two exact residues above all its proper faces are
pencil-prunable, so a first implementation can focus on the full-support
initial systems with `9+beta` independent quotient variables (and the
dependent bracket-slack graph coordinates), rather than on the original column
lengths and all weight ratios.

## 5. What is needed for `H_c^0` and `H_c^1`

Let `Z` be one circuit-piece intersection and let `bar Z` be a compact
semialgebraic/toroidal compactification whose genuine quotient boundary is
`L=bar Z minus Z`.  Then

\[
                         H_c^*(Z)\cong H^*(\bar Z,L).  \tag{T11}
\]

The beginning of the long exact sequence is

\[
 0\to H_c^0(Z)\to H^0(\bar Z)\to H^0(L)
 \to H_c^1(Z)\to H^1(\bar Z)\to H^1(L).               \tag{T12}
\]

Accordingly:

* `H_c^0(Z)=0` once every component of `bar Z` meets a **non-gauge** boundary
  component.  A CAD roadmap plus the quotient cones (T10) can certify this.
* An escape from every component is not enough for `H_c^1(Z)=0`.  One must
  also control how many boundary components attach to each component and the
  kernel of `H^1(bar Z)->H^1(L)`.  In practice this is a finite incidence
  matrix/one-skeleton computation after semialgebraic triangulation.

The elementary curve

\[
 Z_0=\{(x,y)\in\mathbb R_{>0}^2:y=x+x^{-1}\}
\]

shows both limitations sharply.  It is homeomorphic to `R`, so
`H_c^0(Z_0)=0` but `H_c^1(Z_0)=Q`.  It has paths to infinity, yet it contains
no nontrivial coordinate-torus orbit.  Indeed an orbit would require

\[
 y_0t^b=x_0t^a+x_0^{-1}t^{-a}\quad\text{for all }t>0.
\]

If `a` is nonzero, the right side has two distinct powers and cannot equal
one monomial; if `a=0`, then `b=0`.  General Puiseux escapes, rather than pure
one-parameter subgroups, are therefore necessary, and even their existence
does not kill compactly supported degree one.

## 6. Concrete next computation

For the exact `4+5, beta=0` survivor, use the column torus to fix all eight
independent weight ratios.  The full-support equations then involve two fixed
sparse three-vectors, one of which is `e_h wedge omega` with `rank(omega)=6`.
Enumerate the real initial cones of this fixed-form incidence in the nine
positive parent coordinates with the bracket-slack graph embedding (T9a).
Discard the zero quotient cone and attach every nonzero cone to a CAD roadmap
component.  Because all proper toric weight faces are pencil-prunable, no
unresolved weight-boundary stratum enters this first calculation.

For the exact `5+5, beta=1` survivor, repeat with one additional invariant
monomial coordinate.  Its two ends (`w->0` and `w->infinity`) must be attached
to the coherent face fan before applying (T12).

This does not yet prove the second diagonal, but it reduces the proposed
torus/tropical method to a finite and falsifiable calculation and identifies
exactly which apparent escape directions are gauge.
