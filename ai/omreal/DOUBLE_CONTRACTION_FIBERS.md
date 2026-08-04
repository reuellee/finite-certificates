# Double-contraction fibers for the second diagonal

This note records what literal double contraction does and does not prove for
two extension signatures.  It is deliberately separate from
`ATLAS_HELLY.md`: the only new row-2599 result below is a no-go certificate for
one stratified route, not a proof or counterexample to the second diagonal.

## 1. The five-dimensional base

Let `M` be a realizable uniform rank-four oriented matroid on eight elements,
and let `S={sigma,tau}`.  Work in the incidence space with independent
extension columns `p_sigma,p_tau`.  Contract two fixed parent elements `e,f`.
Choose coordinates in which their columns are the last two coordinate vectors.
For every remaining column write

\[
                 v_a=(a_a,h_a,k_a),\qquad a_a\in\mathbb R^2.
\]

The six remaining parent quotient columns realize `M/{e,f}`.  Its normalized
rank-two realization space has dimension

\[
                    (2-1)(6-2-1)=3.
\]

For each extension, the brackets containing `e,f` put its quotient point in a
fixed open interval of the projective line.  Each contributes one further
coordinate.  Thus the partial double-contraction incidence base is an open
semialgebraic set

\[
                    W_{S,e,f}\subset\mathbb R^{3+|S|}
                    =\mathbb R^5.                    \tag{1}
\]

This is the literal source of the formal `3+s=5` count.  Contracting the two
extension columns instead gives the same generic dimension: their span is a
projective line and the eight parent columns give a normalized rank-two
configuration of dimension five.  The parent-contraction model is cleaner
because (1) remains a single Euclidean-open incidence space even when the two
extension quotient points coincide.

## 2. Exact bilinear lift equations

Brackets containing both contracted columns are already fixed on (1).
Brackets containing exactly one of them are linear in one height row.  A
bracket omitting both has the form

\[
 \det(v_i,v_j,v_k,v_l)
 =\sum_{\{a,b\}\subset\{i,j,k,l\}}
   \epsilon_{ab}\det(a_c,a_d)(h_a k_b-h_b k_a),       \tag{2}
\]

where `{c,d}` is the complementary pair and `epsilon_ab` is the Laplace sign.
The parent chirotope prescribes (2) for four parent columns.  An extension
signature prescribes the same expression when one of the four columns is its
private extension column and the other three are parents.  No bracket using
both private extension columns is prescribed.

Consequently the normalized lift fiber over `b in W_(S,e,f)` is an open
semialgebraic set cut out by linear and bilinear strict inequalities in two
height rows.  Before sign inequalities, each height row has eight entries.
Adding an arbitrary linear functional of the two quotient coordinates is a
two-dimensional gauge, leaving six coordinates; fixing one nonzero bracket
then removes the remaining positive row scaling and leaves five normalized
coordinates.  Thus every nonempty double-lift fiber is open in a
ten-dimensional normalized height space.

There is still one exact convex reduction.

> **One-row resolution lemma.**  For a fixed double-contraction base `b`, the
> normalized lift fiber `L_b` is homotopy equivalent to an open semialgebraic
> subset `P_b` of `R^5`.  Hence
> \[
>              \widetilde H_i(L_b;\mathbb Z)=0\qquad(i\ge5).    \tag{3}
> \]

**Proof.**  Fix the first normalized height row `h`.  Every inequality in the
second row `k` is affine-linear: this is immediate for brackets containing a
contracted element, and follows from (2) for the remaining brackets.  Its
nonempty fiber is therefore an open convex polyhedron in the five normalized
`k`-coordinates.  The locus `P_b` of first rows with a nonempty second-row
fiber is open and semialgebraic.  Locally persistent choices, a partition of
unity, and straight-line motion in the convex fibers give `L_b\simeq P_b`.
An open subset of `R^5` has no ordinary integral homology in degrees at least
five, including degree five.  QED.

The order of the rows is immaterial; reversing it gives a second such
resolution.  This is substantially weaker than the acyclicity needed for the
second diagonal.  A five-dimensional base together with (3) still permits
total-degree-seven terms of bidegrees `(3,4)`, `(4,3)`, and `(5,2)` in a
stratified Leray calculation.  Moreover the incidence projection is not
proper, so fiber acyclicity by itself would not supply a Vietoris--Begle
equivalence without boundary control.  A successful theorem along this route
would need, at minimum, vanishing of the degree-two-and-higher fiber homology
plus compatible control at the Hardt-stratum boundaries.

## 3. An exact disconnected affine slice of the projected model

The existing row-2599 residence certificate supplies a literal
double-contraction test for the lower-dimensional model which forgets the
second extension quotient point.  Thus this subsection studies the projected
extra-feasibility locus, not the full incidence fiber `L_b` of Section 2.  Let
`L,R` be its two positions of parent element 1, put

\[
                         p=L-R,
\]

and define

\[
                         e(u)=2R+up,qquad0\le u\le2.   \tag{4}
\]

The column `p` realizes one uniform extension signature `sigma_1` along all of
(4).  Contract `p` and fixed parent element 2.  Every fixed parent column has
constant quotient, while `e(u)-e(0)=up`; hence the rank-two quotient is
literally constant.  It is uniform.

Let `sigma_2` be the stored residence signature.  Its exact endpoint witnesses
remain strict at `u=0,2`.  At `u=1`, signed derived-normal rows

\[
                         0,4,13,44,51                  \tag{5}
\]

form the stored positive five-circuit.  Each row in (5) is affine in `u`, so
its five alternating four-by-four cofactors are polynomials of degree at most
four.  Exact interpolation and conversion to the Bernstein basis prove that
all five positive circuit weights stay positive on

\[
                         \frac12\le u\le\frac32.       \tag{6}
\]

Gordan's alternative therefore makes `sigma_2` infeasible throughout (6).
It follows that

\[
 \{u\in[0,2]:e(u)\text{ supports }\sigma_2\}
\]

has at least two connected components.  The exact checker is

```console
python ai/omreal/verify_double_contraction_gap.py
```

This is stronger than observing one failed midpoint: it certifies a whole
closed infeasible interval in the projected extra-feasibility locus over one
literal uniform double-contraction fiber for the first extension, separating
two feasible relative-open intervals.

It does **not** prove that the full fiber `L_b`, or its projection after
forgetting the second private column, is disconnected.  The two feasible
pieces can in principle connect around (6) through the other height
coordinates.  Thus the result rules out proofs which require every affine
height stratum or every line slice to be acyclic; it does not rule out a
global deformation, shelling, or stratified cancellation theorem.

## 4. Remaining finite target

For a fixed rank-two base, project to the first height row as in the proof of
(3).  Gordan's alternative expresses the complement of `P_b` as a finite
union of positive-circuit loci for the second-row normal system.  All normal
coefficients are affine in the first row.  After quotienting the
two-dimensional linear-functional gauge but before fixing positive row scale,
that homogeneous system lives in a six-dimensional height space.  Hence a
minimal positive circuit uses at most seven normals and has exact
determinant-polynomial weights.  The unresolved fiber question can therefore
be stated finitely:

1. enumerate the signed minimal supports compatible with the parent and the
   two contracted signatures;
2. stratify the first-row chamber by the signs and zero sets of their cofactor
   polynomials;
3. compute the compactly supported incidence maps across adjacent strata;
4. decide whether `H_tilde_q(P_b;Q)` vanishes for `q>=2`, uniformly over every
   base stratum and every catalog parent.

The row-2599 gap proves that this stratification is nontrivial already for one
five-circuit.  It supplies a regression case for any proposed fiber-acyclicity
algorithm.
