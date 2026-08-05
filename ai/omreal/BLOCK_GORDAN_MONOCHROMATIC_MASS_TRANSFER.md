# Monochromatic block-mass transfer and common-wall escape

## Outcome

The remaining codimension-one block-Gordan gap now has a universal local
resolution.  Let a path cross one generic residual wall and suppose one or
more signature blocks lose their positive witnesses there.

1. Some block is bad on the receiving side.  All mass in the dying blocks
   transfers linearly to a normalized witness in that receiving block.
2. No block is bad on the receiving side.  Retarget every dying block to its
   positive wall circuit.  The circuits need not be the same: their labeled
   occurrences share the crossed global residual factor, and every component
   of that factor wall is noncompact.  Fixed bracket-unit circuit
   coefficients keep every block bad along a common proper wall escape.

Thus an individual dying block never needs a same-block circuit on the
feasible side.  Moreover, a compact component cannot terminate at any
all-block loss over one global factor, even when the blocks use different
labeled wall circuits.  The exact hard row-2599 triple shares a circuit and
remains a particularly small regression case.

This does **not** prove that the resulting global matching is acyclic or that
any diagonal vanishes.  Noncompact walls can enclose bounded chambers.  The pair
`H_c^1` and triple `H_c^0` terms for `s=3` remain open as global incidence
problems.

The exact verifier is `BLOCK_GORDAN_MONOCHROMATIC_MASS_TRANSFER.py`.

## 1. The transfer formula

Work in the joined block-Gordan fiber

\[
 \Gamma_S(Y)=\left\{(w_\sigma):
 w_\sigma\ge0,\quad A_\sigma(Y)^Tw_\sigma=0,\quad
 \sum_\sigma {\bf1}^Tw_\sigma=1\right\}.                       \tag{1}
\]

Suppose `D` is the set of blocks dying in the chosen crossing direction and
some block `rho` is bad on the receiving side.  At the wall choose a
normalized nonnegative witness `u_rho` in block `rho`.  Put

\[
 t_D=\sum_{\sigma\in D}{\bf1}^Tw_\sigma .                       \tag{2}
\]

For `0<=a<=1`, define

\[
 \begin{aligned}
 H_a(w_\sigma)&=(1-a)w_\sigma &&(\sigma\in D),\\
 H_a(w_\rho)&=w_\rho+a t_Du_\rho,\\
 H_a(w_\tau)&=w_\tau &&(\tau\notin D\cup\{\rho\}).
 \end{aligned}                                                  \tag{3}
\]

Every block equation in (1), nonnegativity, and total mass are preserved.
The formula remains defined when any dying block has zero mass and when the
receiving block initially has zero mass.  At `a=1` every dying block is zero,
so the witness continues to the receiving side.  A block born on that side
is an admissible receiver: its wall circuit already exists at the crossing.

Formula (3) intentionally leaves a zero-receiver face.  This is the
Mayer--Vietoris block differential, not a defect in face compatibility.
All faces which do not contain the receiver remain governed by the relative
acyclic-carrier induction.

## 2. The all-die case over one global factor

First suppose every dying block contains the same positive wall circuit `P`
at the wall.  It has

\[
                   |P|=4\quad\hbox{(ordinary wall)},\qquad
                   |P|=3\quad\hbox{(localization wall)}.        \tag{4}
\]

Each block fiber at the wall then contains a normalized positive witness
`p_sigma` supported on the same unsigned `P`.  Convexity gives the simultaneous
retargeting

\[
                    w_\sigma\longmapsto
                    (1-a)w_\sigma+a({\bf1}^Tw_\sigma)p_\sigma.  \tag{5}
\]

There are at most `3|P|<=12` parent-label incidences in `P`.  Among eight
parent labels, some `e` therefore has

\[
                              \deg_P(e)\le1.                    \tag{6}
\]

If the degree is zero, the `y_e` residence fiber is an open convex
three-cell.  If it is one, move `y_e` in its support plane; the residence
fiber contains an open convex two-cell.  In either case all support normals
in `P` are fixed up to positive scale, so inverse scaling transports every
block witness in (5).  The fiber has an end at a parent bracket wall.  The
resulting path stays in every active bad block and leaves every compact
subset of the uniform parent realization space.

Consequently:

> **Common-circuit mass-transfer theorem.**  At every generic residual wall,
> a dying block-Gordan face transfers to a block bad on the receiving side by
> (3).  If there is no receiver but all dying blocks share one positive wall
> circuit, its entire active-block face has the common proper escape
> (5)--(6).  No compact simultaneous-bad component can terminate at such a
> common-circuit all-die wall.

The support argument is invariant under relabeling and reorientation and
applies to an individual occurrence of all 13 residual wall types.  The
verifier checks their representative wall circuits individually; their
minimum support-label degree is always zero or one.

The common-circuit qualification is no longer needed.  By
`RESIDUAL_STRATUM_NONCOMPACTNESS.md`, choose any labeled occurrence of the
crossed global factor and put it in its adapted projective-frame gauge.  Its
residual equation is affine in one pivot coordinate with a nowhere-zero
parent-bracket-product slope.  The whole wall is therefore a graph over an
open subset of `R^8`, and none of its connected components is compact.

For every labeled occurrence of that same factor, the ordinary four-circuit
or localization three-circuit has coefficients whose signs are fixed
products of parent brackets.  Its positive relation at the crossing stays a
positive dependence along the entire factor-wall component, including at
intersections with other residual walls; support-minimality there is not
needed.  Retarget each dying block inside its convex wall fiber to its own
wall circuit, normalize those bracket-unit coefficients continuously, and
follow a proper semialgebraic curve from the crossing in the common wall
component.  This gives a simultaneous escape even when the union of the
different circuits is pencil-rigid.

> **Global-factor all-die theorem.**  At every generic residual wall, a
> dying block face either transfers to a receiving bad block by (3), or all
> dying blocks have a common proper escape along the crossed global-factor
> wall.  The blocks need not share one unsigned circuit.

## 3. Exact row-2599 antichain test

The transfer alternative can genuinely be absent even under the 9DVL
hypotheses.  At the exact row-2599 transverse node, take

\[
 \begin{aligned}
 \sigma_0&=448607715549184,\\
 \sigma_1&=3826331369078784,\\
 \sigma_2&=31604296963587053.
 \end{aligned}                                                  \tag{7}
\]

All three have exact local feasibility mask `0011`: they are feasible in
the two cells on one side of branch zero and bad in the two cells on the
other side.  Thus they die simultaneously when branch zero is crossed.

Exact recursive tope enumeration on charts `1,3,4,5` of the stored
178-chart atlas gives the masks

\[
                              1010,\qquad0100,\qquad1001.       \tag{8}
\]

Every ordered pair in (8) has a bit present on the left and absent on the
right.  Hence the three feasibility regions are nonempty, proper, and
pairwise incomparable.  This is an actual 9DVL family, not an abstract sign
model.

At the branch-zero wall, all three signed arrangements have the same strict
positive localization circuit

\[
                  P=(0,18,40)=123/356/348.                     \tag{9}
\]

On the bad side each signature has exactly 18 positive one-auxiliary
circuits based on (9), while the feasible-side count is zero.  There is no
receiving bad block.  But the parent-label degree vector of (9) is

\[
                              (1,1,3,1,1,1,0,1).                \tag{10}
\]

Label 7 is omitted, so the common escape is the especially simple
degree-zero case of (6).  This exact example both refutes a universal
partner-block assertion and verifies the common-wall escape which replaces
it.

For three coincident dying blocks, the local block incidence is the standard
augmented two-simplex complex.  With pair order `01,02,12`, its differentials
are

\[
 d_0=\begin{pmatrix}-1&1&0\\-1&0&1\\0&-1&1\end{pmatrix},
 \qquad
 d_1=\begin{pmatrix}1&-1&1\end{pmatrix}.                       \tag{11}
\]

One has `d_1d_0=0`; `d_1` is primitive and the rank-two minors of `d_0`
contain a unit.  Therefore this local repeated-cover incidence is integrally
acyclic.  Any surviving third-diagonal class must use global component
attachment, not the pure simultaneous-loss star (7)--(10).

## 4. What remains

Combining this note with `BLOCK_GORDAN_ALL_CODIM_COHERENCE.md` and
`RESIDUAL_STRATUM_NONCOMPACTNESS.md` removes every receiver-present wall and
every one-factor all-die wall as separate local obstructions.  The remaining
proof obligation includes:

- choose receivers and escapes on a finite proper subdivision;
- prove the induced matching has no directed cycle;
- verify properness at every parent-boundary end; and
- show that the residual component-incidence complex has no cohomology in
  the diagonal degree.

In particular, this note does not assert `H_c^1` of every pair intersection
or `H_c^0` of every triple intersection is zero.  It proves that a compact
class cannot be created merely because a witness block has a monochromatic
codimension-one loss.

## 5. Verification

Run

```console
python ai/omreal/BLOCK_GORDAN_MONOCHROMATIC_MASS_TRANSFER.py
```

The checker uses exact integer/rational arithmetic to verify all 13 light
individual wall circuits, the row-2599 common positive circuit and auxiliary
counts, the three exact node masks, pairwise incomparability on four exact
parent charts, and integral exactness of (11).
