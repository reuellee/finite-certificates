# Fourth diagonal: fivefold circuit descent and a top-fiber escape

## Outcome

This note does **not** prove the fourth diagonal.  Its target remains

\[
 \widetilde H_5(F_S;\mathbb Q)=0
 \quad\Longleftrightarrow\quad
 H_c^3(B_S;\mathbb Q)=0,
 \qquad |S|=4.
\]

It gives three exact reductions which make that target smaller.

1. A direct Gordan escape proves `H_5(X;Z)=0` for every rank-four,
   eight-element parent, independently of the blanket contractibility result
   for realization spaces on fewer than nine elements.  Thus the displayed
   fourth-diagonal duality itself needs only the established rank-three,
   seven-element theorem.
2. Compact-support Cech descent shows generally that the diagonal target
   `H_c^(s-1)` depends only on intersections of at most `s+1` Gordan circuit
   pieces; five pieces suffice when `s=4`.
3. A two-stage deletion argument kills `H_c^q` for every `q<=3` whenever
   the support union omits one parent label and uses a second label at most
   twice.  In particular, a single five-circuit piece can contribute to the
   `(p,q)=(0,3)` term only if its support covers all eight parent labels.

The third assertion is one degree stronger than the direct three-dimensional
deletion-fiber bound: it also kills the possible top orientation class of that
fiber.

An exact census leaves `1,099,560` of the `2,021,992` generic labeled
five-supports, in `66` of the `117` `S_8`-orbits, after this single-piece
cover filter.  The remaining four-signature calculation is finite but still
large, and an exact row-2599 certificate shows that none of the incidence-only
deletion tests can finish it.

## 1. Direct parent `H_5` vanishing

The fourth-diagonal dual target can be justified without importing the
blanket statement that every realizable oriented matroid on fewer than nine
elements has contractible realization space.

> **Rank-four/eight parent theorem.**  For every realizable uniform oriented
> matroid `M` of rank four on eight elements,
>
> \[
>                       \widetilde H_5(\mathcal R(M);\mathbb Z)=0. \tag{P1}
> \]

**Proof.**  Choose a parent label `e`, put

\[
 D=\mathcal R(M\setminus e),
\]

and let `G_e^del subset D` be the locus over which `e` can be inserted with
the signs prescribed by `M`.  The deletion has rank four on seven elements;
its Gale dual has rank three on seven elements.  Gale duality identifies the
projective realization spaces (the discarded positive column-length factors
are contractible), and the established rank-three theorem on at most eight
elements makes `D` contractible.  A fixed projective-frame slice realizes
`D` as an oriented open six-manifold.  The source trace for this
rank-three input is recorded in `PARENT_CONTRACTIBILITY_AUDIT.md`, Section 3.

Over `G_e^del`, the insertion position of `e` ranges through its nonempty
projective residence chamber.  This is an open convex three-cell.  The same
fixed-affine-chart barrier trivialization used in Section 4 below makes the
total insertion space a product with `R^3`; in particular

\[
                   \mathcal R(M)\simeq G_e^{\rm del}.             \tag{P2}
\]

It remains to rule out compact components of

\[
                         B_e=D\setminus G_e^{\rm del}.
\]

At any `b in B_e`, Gordan's alternative supplies a positive dependence among
the signed normals `a_I(b)`, where `I` ranges over the triples of the seven
deletion labels.  A support-minimal dependence has at most five triples,
because the normals lie in `R^4`.  Those triples have at most fifteen label
occurrences.  Some one of the seven labels `f` therefore has support degree
at most two.

Pass to the globally equivalent projective-frame slice whose five frame
labels are chosen from the other six deletion labels; uniformity makes this
change of slice semialgebraic everywhere.  Now hold those other six deletion
points fixed.  If the degree of `f` is zero, move it through its full residence
chamber.  If the degree is one, move it in
the incident support plane.  If the degree is two, move its positive ray in
the intersection of the two incident support planes.  In every case the
involved normal rays are fixed or change by positive scalars, so rescaling the
Gordan coefficients preserves the positive dependence.  The path stays in
`B_e` and approaches the boundary of `D`.  Starting at an arbitrary bad
point therefore produces an escape inside its bad component.  Every
component of `B_e` is noncompact, and

\[
                            H_c^0(B_e;\mathbb Z)=0.                \tag{P3}
\]

Since `D` is a contractible oriented six-manifold, the homology sequence of
`(D,G_e^del)` and Poincare--Alexander duality give

\[
 \widetilde H_5(G_e^{\rm del};\mathbb Z)
   \cong H_6(D,G_e^{\rm del};\mathbb Z)
   \cong H_c^0(B_e;\mathbb Z)=0.
\]

Together with (P2), this proves (P1).  QED.

The contraction-height theorem already gives `H_i(X;Z)=0` for `i>=6` for
the rank-four/eight parent space `X`.  Combining that fact with (P1), the
exact sequence

\[
 H_6(X;\mathbb Q)\longrightarrow H_c^3(B_S;\mathbb Q)
 \longrightarrow H_5(F_S;\mathbb Q)\longrightarrow H_5(X;\mathbb Q)
\]

reduces the fourth diagonal to `H_c^3(B_S)=0` without the blanket
parent-contractibility input.  Equivalently, the contraction-height argument
gave the bad-locus isomorphism independently for `s<=3`, and (P1) extends
that independent range through `s=4`.

## 2. Circuit cover

Let `X` be the normalized realization space of a fixed realizable
`UOM(4,8)` parent.  For a signature `rho` and a set `Q` of at most five
parent triples, write

\[
 C_{\rho,Q}=\left\{Y\in X:\ \exists\lambda\in\Delta_Q,
     \quad \sum_{I\in Q}\lambda_I\rho_Ia_I(Y)=0\right\}.
\]

Gordan's alternative and Caratheodory's theorem give the finite closed cover

\[
 B_S=\bigcup_{\rho\in S}\ \bigcup_{1\leq |Q|\leq5}C_{\rho,Q}.
 \tag{F1}
\]

For the deletion result below it is useful to keep the uncofinalized cover
with all support sizes.  A lower-support witness can of course be padded to a
five-support, but the padding can hide a label which the actual dependence
omits.

## 3. Only `(s+1)`-fold intersections affect diagonal `s`

Index the pieces in (F1) by `alpha`.  Compactly supported Cech descent for a
finite closed semialgebraic cover gives

\[
 R\Gamma_c(B_S;\mathbb Q)\simeq
 \operatorname{Tot}\left[
  \bigoplus_{\alpha_0<\cdots<\alpha_p}
  R\Gamma_c(C_{\alpha_0}\cap\cdots\cap C_{\alpha_p};\mathbb Q)
 \right].                                               \tag{F2}
\]

One completely concrete construction is to choose a simultaneous
semialgebraic compactification and triangulation, use relative cellular
cochains for compact supports, and take the alternating restriction maps in
the horizontal direction.  The degree-three cohomology of the total complex
is

\[
 \ker(\operatorname{Tot}^3\to\operatorname{Tot}^4)
 \big/
 \operatorname{im}(\operatorname{Tot}^2\to\operatorname{Tot}^3). \tag{F3}
\]

More generally, the diagonal-`s` target is `H_c^(s-1)(B_S)`.  It is the
middle cohomology of the three-term portion

\[
 \operatorname{Tot}^{s-2}\longrightarrow
 \operatorname{Tot}^{s-1}\longrightarrow
 \operatorname{Tot}^{s}.                              \tag{F3a}
\]

In total degree `n`, the nonnegative Cech degree is at most `n`, so that term
uses intersections of at most `n+1` pieces.  The largest term in (F3a) is
therefore an intersection of `s+1` pieces.  This proves the following exact
all-diagonal truncation.

> **`(s+1)`-fold truncation theorem.**  For a signature family `S` of size
> `s`, the group `H_c^(s-1)(B_S;Q)` is determined by functorial compact-
> support cochain models for intersections of at most `s+1` circuit pieces,
> truncated to cochain degree at most `s`.  No `(s+2)`-fold or higher circuit
> intersection can affect diagonal `s`.

For `s=1`, the nonexistent incoming negative total degree in (F3a) is simply
omitted.  The conclusion still says that intersections of at most two pieces
suffice.  For `s=4`, (F3a) is exactly (F3): total degrees `2,3,4` involve at
most `3,4,5` pieces.

Equivalently, on the spectral sequence

\[
 E_1^{p,q}=\bigoplus_{\alpha_0<\cdots<\alpha_p}
 H_c^q(C_{\alpha_0}\cap\cdots\cap C_{\alpha_p};\mathbb Q),
\]

the only terms on the target diagonal are

\[
 (p,q)=(0,3),(1,2),(2,1),(3,0),                       \tag{F4}
\]

and the differentials which can enter or leave them use at most the adjacent
total degrees two and four, hence at most five pieces.  Working with the
total cochain complex rather than only its `E_1` groups retains all higher
differentials automatically.

## 4. A two-stage top-fiber escape

For a tuple of circuit supports let `U` be the union of its distinct triples,
and let `deg_U(e)` be the number of triples of `U` containing label `e`.

> **Omitted-plus-light deletion theorem.**  Let
>
> \[
> Z=C_{\rho_1,Q_1}\cap\cdots\cap C_{\rho_t,Q_t}.
> \]
>
> Suppose there are distinct parent labels `e,f` such that
>
> \[
>                    \deg_U(e)=0,\qquad \deg_U(f)\leq2. \tag{F5}
> \]
>
> Then
>
> \[
>                     H_c^q(Z;\mathbb Q)=0
>                     \qquad(0\leq q\leq3).            \tag{F6}
> \]

**Proof.**  Delete `e`.  Because no support triple contains `e`, every
derived normal and every Gordan equation defining `Z` is independent of the
position of `e`.  The deletion map therefore has the form

\[
 \pi_e:Z\longrightarrow Z',                           \tag{F7}
\]

where `Z'` is the intersection of the same circuit conditions inside the
nonempty-insertion locus `G_e^del` for the deletion oriented matroid.  This
locus is open: one strict insertion of `e` persists under a small change of
the deletion realization.

The fibers in (F7) are not merely pointwise open three-cells; they form a
globally trivial oriented `R^3`-bundle.  To see this without appealing only
to a Hardt stratification, choose a labeled projective frame among five of
the six labels different from `e,f`.  Uniformity makes those same five labels
a projective frame over the whole deletion realization space.  The unique
frame change gives a global semialgebraic change from the original normalized
slice to this one, and all circuit-piece conditions are projectively
invariant.  Thus this change loses no topology and, importantly, never uses
the two columns that will move.  Use four frame columns as a vector basis.
The four coordinates of `y_e` then have fixed nonzero signs on the parent
chirotope cell.  Positive projective scaling therefore gives the fixed affine
normalization

\[
            \sum_{i=1}^4 s_i(y_e)_i=1,
       \qquad s_i(y_e)_i>0,                            \tag{F8a}
\]

where the signs `s_i` are constant.  Every residence fiber `P_b` is now a
nonempty bounded open convex polyhedron in one fixed oriented affine
three-space `A`: its inequalities are the prescribed signed parent brackets
containing `e`, and their coefficients vary continuously with `b in Z'`.

There is a continuous fiberwise trivialization which also fixes the
orientation.  Write those positive affine inequalities as
`ell_j(b,x)>0` and, after identifying `A` with `R^3`, put

\[
 \phi_b(x)=\tfrac12\|x\|^2-\sum_j\log\ell_j(b,x).
\]

This is strictly convex, and the barrier tends to positive infinity at the
boundary of the bounded polyhedron.  For every `u in R^3`, the function
`phi_b(x)-<u,x>` has a unique interior minimizer.  Hence

\[
 (b,x)\longmapsto (b,\nabla_x\phi_b(x))                \tag{F8b}
\]

is a bijection from the total residence family to `Z' times R^3`.  The
positive-definite Hessian and the implicit-function theorem show that it and
its inverse depend continuously on `(b,x)` and `(b,u)`.  Its fiber Jacobian
has positive determinant, so it preserves the fixed orientation.  Thus
(F7) is globally a product bundle, not just a stratumwise one.  Compact-
support Kunneth gives

\[
 H_c^q(Z;\mathbb Q)\cong H_c^{q-3}(Z';\mathbb Q).       \tag{F8}
\]

Equivalently, before choosing the fixed orientation, the right-hand side is
`H_c^{q-3}(Z';O_e)`, where `O_e` is the rank-one fiber-orientation local
system; the displayed global trivialization makes `O_e` constant.  Thus only
`q=3` requires an additional argument.

Start at any point of `Z'` and move the deletion point `f` while holding the
other six deletion points fixed.  If `deg_U(f)=0`, use its full residence
chamber.  If the degree is one, use the projective-plane shear preserving the
unique incident support plane.  If the degree is two, use the positive-ray
interval in the intersection of the two incident support planes.  Along the
last path an incident normal changes only by a continuous positive scalar;
rescale its separate Gordan weight in every support and renormalize.  Hence
all circuit-piece conditions persist, and the path approaches the boundary
of the deletion realization cell.

Parameterize this path as `gamma:[0,1) ->` the deletion realization cell,
with `gamma(0)` the chosen point and with `gamma(t)` approaching its residence
boundary as `t -> 1`.  Let `J` be the connected component containing zero of

\[
             \{t\in[0,1):\gamma(t)\in G_e^{del}\}.
\]

Because `G_e^del` is open, `J=[0,a)` for some `a<=1`.  If `a=1`, the path
escapes through the deletion-cell boundary.  If `a<1`, continuity gives a
limit `gamma(a)` inside the deletion realization cell, but maximality and
openness imply `gamma(a) notin G_e^del`; otherwise `J` would extend past
`a`.  Thus `gamma|J` lies in `Z'`, starts at the arbitrary chosen point, and
has no limit in `Z'` in either case.

Every path component of `Z'` is consequently noncompact.  Semialgebraic sets
are locally path connected and have finitely many components, so every
connected component is noncompact and `H_c^0(Z';Q)=0`.  Equation (F8) proves
(F6).  QED.

For one support `Q` with at most five triples, omission of a label `e` forces
a second light label: the at most fifteen remaining label occurrences are
distributed among seven labels, so one of them has degree at most two.
Therefore

\[
 \boxed{\quad
 Q\text{ omits a parent label}
 \quad\Longrightarrow\quad
 H_c^q(C_{\rho,Q};\mathbb Q)=0\quad(q\leq3).
 \quad}                                                \tag{F9}
\]

In particular the `(0,3)` source in (F4) may be restricted to circuit
supports which cover all eight labels.  The theorem also applies to any
multi-piece intersection satisfying (F5), including intersections with two
omitted labels.

## 5. The exact degree-three support sieve

Combine (F6) with the projective-plane-pencil and common-apex shear lemmas.
For a support union `U`, define these necessary predicates for a possibly
nonzero compact-support group:

* `A0(U)`: `U` is pencil-rigid: every label has degree at least three and no
  label has one fixed partner in all its incident triples;
* `A1(U)`: every degree is at least two and `delta(U)<=1`;
* `A2(U)`: every degree is at least one and `delta(U)<=2`;
* `A3(U)`: there is no pair `e!=f` with `deg_U(e)=0` and
  `deg_U(f)<=2`.

Here

\[
 \delta(U)=\min\left(3,\max_a
   \#\{e\ne a:e\in I\in U\Rightarrow a\in I\}\right).
\]

The three total-complex degrees needed in (F3) have the following exact
incidence sieve.  An entry records a necessary predicate; a dash means that
these deletion lemmas impose no condition.

| total degree | 1 piece | 2 pieces | 3 pieces | 4 pieces | 5 pieces |
|---:|---|---|---|---|---|
| `2` | `q=2: A2` | `q=1: A1` | `q=0: A0` |  |  |
| `3` | `q=3: A3` | `q=2: A2` | `q=1: A1` | `q=0: A0` |  |
| `4` | `q=4: -` | `q=3: A3` | `q=2: A2` | `q=1: A1` | `q=0: A0` |

This is a sufficient rejection table, not an assertion that every retained
group is nonzero.  A finite fourth-diagonal computation can now discard every
cellular intersection failing its displayed predicate before constructing
restriction matrices.

## 6. Exact generic census and sharp obstruction

Away from the residual derived walls, a support-minimal five-circuit is a
five-edge three-uniform hypergraph in which every label degree is at most
three and every pair codegree is at most two.  Exhaustion gives the following
cover-all residue of (F9).

| sorted degree sequence | labeled supports | `S_8` orbits |
|---|---:|---:|
| `1,1,1,1,2,3,3,3` | 144,480 | 10 |
| `1,1,1,2,2,2,3,3` | 582,960 | 30 |
| `1,1,2,2,2,2,2,3` | 341,880 | 22 |
| `1,2,2,2,2,2,2,2` | 30,240 | 4 |
| **total cover-all** | **1,099,560** | **66** |
| removed by (F9) | 922,432 | 51 |
| all generic five-supports | 2,021,992 | 117 |

The residue is real, not just an unsigned counting artifact.  On the exact
row-2599 pattern-zero chart, the four shatter signatures numbered
`0,4,3,5` have strictly positive, support-minimal five-circuits.  The union of
the first two supports is already pencil-rigid, and adding the other two
keeps it so.  The same exact certificate realizes all sixteen good/bad
patterns on these four signatures, so their feasibility regions are proper
and pairwise incomparable.

This does **not** produce nonzero compact-support cohomology: it proves only
that the surviving four-piece intersection is nonempty and that the
incidence/shear predicates `A0`--`A3` cannot remove it.  Compactness at
infinity or the differentials in (F2) remain essential.

Run the exact verifier with

```console
python ai/omreal/verify_fourth_diagonal_reduction.py
```

It uses integer arithmetic for the support census, orbit calculation,
parent determinants, strict extension witnesses, and Gordan dependences.

## 7. Remaining finite task

For each realizable parent and four-signature antichain, form functorial
relative cellular cochain models for only the retained intersections in the
table above.  Assemble total degrees `2 -> 3 -> 4` of (F2).  The fourth
diagonal holds exactly when the middle cohomology is zero.  The top-fiber
escape theorem removes the orientation classes coming from every omitted
single support, but the cover-all single supports, pencil-rigid fourfold
terms, boundary-weight faces, and their restriction maps remain unresolved.
