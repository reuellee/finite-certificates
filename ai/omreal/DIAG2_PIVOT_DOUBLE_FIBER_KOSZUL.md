# A bounded Koszul audit of the one-row double-contraction fiber

## Verdict

This audit does **not** prove

\[
                 \widetilde H_q(P_b;\mathbb Q)=0\qquad(q\ge 2),       \tag{1}
\]

and it does not construct a counterexample to (1).  The second diagonal
therefore remains open.

It does prove one uniform support-pruning theorem and one exact, genuinely
9DVL-compatible no-go certificate:

1. a minimal Gordan circuit in the one-row normal system cannot contain
   exactly one bracket involving one fixed contracted column; an all-bilinear
   circuit has support at most six, so every seven-circuit has at least two
   contracted-column linear rows;
2. two such linear rows are enough to destroy the tempting Koszul-kernel
   escape.  There is an exact uniform rank-two quotient and an allowed
   seven-row positive circuit for which the fixed-weight alternating pencil is
   invertible.  The witness equation has a unique first height row.

The second item comes from an honest uniform rank-four parent together with
two simultaneously realizable private extension signatures.  Every row in
the obstruction contains at most one private label, so no unprescribed
private-private basis is used.  The obstruction is not asserted to be a
proper incomparable pair; its role is to disprove a purported universal
fiber theorem, not the 9DVL statement.

The exact verifier is

```console
python ai/omreal/DIAG2_PIVOT_DOUBLE_FIBER_KOSZUL_VERIFY.py
```

## 1. The alternating/Koszul normal system

Fix a double-contraction base and write the eight remaining quotient columns
as

\[
                  v_i=(1,t_i,h_i,k_i),\qquad i\in D,\quad |D|=8.
\]

Quotient both height rows by the two-dimensional space spanned by `1` and
`t`.  The resulting homogeneous height space is

\[
                       V=\mathbb R^D/\langle 1,t\rangle,
                       \qquad \dim V=6.                            \tag{2}
\]

For a four-subset `I` omitting both contracted columns, Laplace expansion is
the alternating bilinear form

\[
                       [I](h,k)=h^T\Omega_I k,
                       \qquad \Omega_I^T=-\Omega_I.                \tag{3}
\]

After fixing `h`, its normal in the `k` inequalities is

\[
                            n_I(h)=h^T\Omega_I.                    \tag{4}
\]

In particular,

\[
                              n_I(h)h=0.                           \tag{5}
\]

Let the contracted columns be

\[
                  e=(0,0,1,0),\qquad f=(0,0,0,1).
\]

A bracket `J union {e}` gives a constant `k`-normal `c_J`.  Direct expansion
with the displayed column order gives the companion identity

\[
                         c_Jh=-[J\cup\{f\}](h).                    \tag{6}
\]

The right side is nonzero in a uniform first lift.

## 2. Uniform one-linear-row exclusion

> **Koszul support-pruning theorem.**  At a uniform first height row `h`, a
> nonzero linear dependence among signed second-row normals cannot have
> exactly one constant row `c_J`.  A support-minimal dependence containing no
> constant row has size at most six.  Consequently every support-minimal
> seven-row Gordan circuit contains at least two constant rows.

**Proof.**  All variable rows (4) lie in the five-dimensional hyperplane
`h^perp` by (5), so a minimal dependence among them uses at most six rows.
Now suppose a dependence contains exactly one constant row:

\[
                  \lambda_0\epsilon_0c_J+
                  \sum_i\lambda_i\epsilon_i n_i(h)=0,
                  \qquad \lambda_0\ne0.                           \tag{7}
\]

Pair (7) with `h`.  Every variable term vanishes by (5), while (6) turns the
remaining term into a nonzero uniform first-lift bracket.  This is a
contradiction.  A minimal circuit in the six-dimensional normal space has at
most seven rows, giving the last assertion.  QED.

This is a strict improvement over the undifferentiated support-`<=7` bound in
`DOUBLE_CONTRACTION_FIBERS.md`.  It is only a support classification; it does
not control the topology of a six- or seven-support bad locus.

## 3. Exact two-linear-row obstruction

Take the uniform rank-two quotient

\[
                             a_i=(1,i),\qquad 0\le i\le7,           \tag{8}
\]

and use the gauge `h_0=h_1=k_0=k_1=0`.  Declare quotient labels `0` and `2`
to be the two private extensions.  The other six quotient labels, together
with `e,f`, are the eight parent labels.

Use the following seven signed `k`-inequalities.  The first two supports mean
the bracket with `e`; the remaining five omit both contracted columns.

| kind | support | sign |
|---|---|---:|
| constant | `017e` | `-` |
| constant | `235e` | `-` |
| bilinear | `1456` | `-` |
| bilinear | `2356` | `-` |
| bilinear | `2346` | `+` |
| bilinear | `2357` | `+` |
| bilinear | `0457` | `-` |

No support contains both private labels `0,2`.  Thus every displayed bracket
is prescribed by the parent or by exactly one private signature.

At

\[
 h^-=(0,0,38/3,34/3,16/3,19/3,43/3,7/3),                         \tag{9}
\]

the seven signed normals in the quotient coordinates `2,...,7` are

\[
\begin{pmatrix}
0&0&0&0&0&1\\
2&-3&0&1&0&0\\
0&0&-77/3&49/3&7/3&0\\
21&-91/3&0&7&7/3&0\\
-21&98/3&-7&0&-14/3&0\\
-2&2/3&0&11/3&0&-7/3\\
0&0&98/3&-28&0&4/3
\end{pmatrix}.                                                    \tag{10}
\]

They have rank six, their sum is zero, and all seven signed alternating
six-by-six cofactors equal `-4802/3`.  Hence (10) is a support-minimal positive
Gordan circuit and the target second height row is infeasible at `h^-`.

Let

\[
                         S=\sum_{r=1}^5\epsilon_r\Omega_{I_r}.      \tag{11}
\]

For the five bilinear rows in the table, exact arithmetic gives

\[
                              \det S=9.                            \tag{12}
\]

The all-unit dependence equation is `S h=c`, where `c` is the signed sum of
the two constant normals.  Thus (9) is the unique fixed-weight solution.
After imposing any positive row-scale normalization, rescale the two constant
weights by the same positive factor; uniqueness remains.  The odd/even
alternation heuristic therefore supplies no nonzero tangent or global escape
at this witness.

This is not an artificial infeasible sign list.  Put

\[
\begin{aligned}
 h^+={}&(0,0,1,12581/10000,13466/10000,16766/10000,
                  23518/10000,22182/10000),\\
 k^+={}&(0,0,379,305,138,159,255,1).                              \tag{13}
\end{aligned}
\]

The ten columns consisting of the eight `(1,i,h_i^+,k_i^+)` and `e,f` form
a uniform rank-four realization.  Its parent is obtained by deleting private
labels `0,2`; either private label separately gives a uniform realizable
extension.  The seven signed bracket values in the table are respectively

\[
             1,\quad2,\quad171/200,\quad10902/625,\quad533/1000,
             \quad4631/5000,\quad671/625,                          \tag{14}
\]

so all are strict and positive.  Moreover, all 56 rank-three brackets of
`(1,i,h_i^-)` and `(1,i,h_i^+)` are nonzero and have the same signs.  Hence
the good and bad height rows lie in the same open convex first-lift chamber.

Because the positive cofactors at (9) are strict, infeasibility persists on a
relative neighborhood of `h^-`.  Thus even in this exact allowed-support
model the bad locus can have interior inside one uniform first-lift chamber.
The varying circuit weights, not a fixed height-kernel direction, carry that
neighborhood.

## 4. Exact topological target and the safe Leray payoff

Let `C_b` denote a normalized full-dimensional first-height chamber.  It is an
open convex five-cell.  Put

\[
                         B_b=C_b\setminus P_b.
\]

Gordan makes `B_b` closed relative to `C_b`, and Alexander duality in
`C_b\cong\mathbb R^5` gives, for `2<=q<=4`,

\[
                  \widetilde H_q(P_b;\mathbb Q)
                  \cong H_c^{4-q}(B_b;\mathbb Q).                 \tag{15}
\]

Therefore (1) is exactly the three-degree compact-support assertion

\[
                          H_c^0(B_b)=H_c^1(B_b)=H_c^2(B_b)=0.      \tag{16}
\]

The certificate above proves neither side of (16): an open bad neighborhood
may still attach to the parent boundary, and the full bad locus may still have
vanishing low compact-support cohomology.

There is a safe conditional Leray implication, but it needs more than the
ordinary groups in (1).

> **Conditional relative-Leray lemma.**  Suppose the normalized
> double-contraction projection admits a proper semialgebraic compactification
> as a map of pairs over a five-dimensional compactified base, and suppose the
> relative fiber cosheaves (including every Hardt boundary specialization)
> vanish in degrees `q>=2`.  Then the total relative homology vanishes in
> degrees at least seven.  In particular the degree-seven term needed for the
> second diagonal vanishes.

Indeed, the homological Leray spectral sequence is supported in base degree
`p<=5` and fiber degree `q<=1`, so `p+q<=6`.  Ordinary acyclicity of each open
`P_b` does **not** imply the relative-fiber hypothesis: the original
projection is nonproper, and homology can enter through the exit sets or
through specialization maps at Hardt-stratum boundaries.  This is the exact
reason that proving (1) alone would still require the boundary-control clause
already flagged in `DOUBLE_CONTRACTION_FIBERS.md`.

## 5. Remaining bounded problem

The Koszul theorem reduces the support types but does not reduce the target to
a fixed-weight calculation.  A proof along this route must keep the compact
simplex of Gordan weights and establish (16), compatibly with the exit
compactification, for two classes:

1. all-bilinear minimal circuits of size at most six; and
2. circuits with at least two contracted-column linear rows, of total size at
   most seven.

The exact example (8)--(14) is the regression case for the second class.  Any
argument assigning every positive witness a nonzero height-kernel escape, or
treating the bad locus as positive-codimensional, is false.  What remains
plausible is a block-Gordan matching which uses motion in the weight simplex
and cancels fixed-weight rigid strata across their zero-weight faces.
