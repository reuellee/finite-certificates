# Diagonal three: adversarial architecture and coefficient audit

## Verdict

At the cohomology level, the two diagonal-three obstructions are genuine.
No change of cover, resolution, or compactification can make either one
disappear:

1. `H_c^0(B_0 intersect B_1 intersect B_2;Q)` must vanish; and
2. the alternating restriction map from pair `H_c^1` must be injective.

The current **implementations** of those obligations are not equally
necessary.  The universal primitive-factor triple census is a sufficient
way to prove the first item, not an invariant formulation of it.  Likewise,
an integral signed split contraction is stronger than the actual 9DVL
target.  For the pair item it is enough to construct the finite relative
complex over `F_2` and prove middle exactness there.  This removes orientation
signs and Smith-unit bookkeeping, but it does not remove coverage,
specialization, multiplicity-parity, or parent-infinity incidence.

## 1. Why triple noncompactness cannot be cancelled

For three closed bad loci the block-mass filtration is the finite closed-cover
spectral sequence

\[
 E_1^{p,q}=\bigoplus_{|I|=p+1}H_c^q(B_I;\mathbb Q)
 \Longrightarrow H_c^{p+q}(B_0\cup B_1\cup B_2;\mathbb Q).
\]

The possible incoming maps to `E_1^(2,0)` are the `d_1` from pair
`H_c^0` and the `d_2` from singleton `H_c^1`.  Both sources vanish by the
proved first two diagonals and the single-bad two-skeleton theorem.  There is
no outgoing map from column two.  Hence

\[
 E_\infty^{2,0}=H_c^0(B_0\cap B_1\cap B_2;\mathbb Q).
\]

Since this is an associated-graded quotient of the target, target vanishing
forces it to be zero.  A mixed-block three-cell can encode the required
proper triple escape, but cannot replace it with a cancellation.

The remaining `1,819,789` primitive-factor triples are not themselves an
invariant necessity.  They arise from one sufficient nested support-drop
theorem.  A direct theorem on triple-bad components, a family-specific active
factor atlas, or a different exact factor symmetry may bypass that raw list,
provided it still proves the displayed `H_c^0` group is zero.

## 2. Why the pair kernel is also genuine

After singleton `H_c^2`, singleton `H_c^1`, pair `H_c^0`, and triple
`H_c^0` vanish, the only surviving associated-graded piece in total degree
two is

\[
 \ker\!\left[
 \bigoplus_{i<j}H_c^1(B_i\cap B_j;\mathbb Q)
 \longrightarrow H_c^1(B_0\cap B_1\cap B_2;\mathbb Q)
 \right].
\]

It has no incoming higher differential and no later column to escape to.
Thus its vanishing is necessary.  The exclusive-pair/frontier complex in
`DIAG3_PAIR_DIFFERENTIAL_ENDS.md` is an exact model of this invariant, not a
cover artifact.  A different resolution may prove the kernel zero directly,
but must prove the same fact.

The sharp global-graph countermodel already in that note rules out deriving
this injectivity from component noncompactness alone.  The tapered-ribbon
class likewise rules out a proof using only local product charts.

## 3. The sufficient `F_2` certificate

The master 9DVL statement asks for
`H_tilde_(9-s)(F_S;Q)=0`; it does not require integral or
coefficient-universal vanishing.  Let

\[
 C^0\mathop{\longrightarrow}^{N}C^1
 \mathop{\longrightarrow}^{M}C^2,
 \qquad MN=0,
\]

be any finite free integral relative cellular model of the balanced pair
complex.  Put `n_1=rank C^1`.  If its reduction modulo two is exact in the
middle, then

\[
 \operatorname{rank}_{\mathbb F_2}N+
 \operatorname{rank}_{\mathbb F_2}M=n_1.
\]

For every integer matrix, rational rank is at least its rank modulo two.
On the other hand `MN=0` over `Q` implies

\[
 \operatorname{rank}_{\mathbb Q}N+
 \operatorname{rank}_{\mathbb Q}M\le n_1.
\]

Combining the two inequalities forces equality over `Q`, hence
`ker(M_Q)=im(N_Q)`.  Therefore

\[
             H^1(C^\bullet;\mathbb F_2)=0
             \quad\Longrightarrow\quad
             H^1(C^\bullet;\mathbb Q)=0.
\]

This is one-way only.  Rational exactness need not imply mod-two exactness
(the matrix `[2]` is the standard warning), and mod-two exactness does not
give the integral or every-coefficient theorem claimed by a unit-Smith
contraction.

Operationally, a theorem-grade pair atlas may therefore use **unsigned
mod-two incidence**.  It must still be a coverage-certified finite relative
model and must retain zero witness faces, simultaneous-factor
specializations, incidence parity, and parent infinity.  The exact final
test is only

```text
rank_F2(N) + rank_F2(M) = dim_F2(C1).
```

There is one indispensable lift hypothesis behind this shorthand.  The
unsigned matrices must be the reductions of an actual finite free integral
cellular/Cech complex, so that some signed integral lifts satisfy `MN=0`
over `Z`.  The signs need not be computed for the rank test, but existence of
that lift must follow from the covered geometric complex.  Arbitrary
mod-two matrices are insufficient: `N=[1]`, `M=[2]` are middle-exact after
reduction modulo two, but their displayed integral lifts have `MN=2` and do
not even form a rational complex.

## 4. Fixed triangular orders do not supply the atlas

A natural attempt is to fix a total order of the eight labels and always
choose a common elementary root descending in that order.  The exact
regression `verify_diag3_pair_fixed_order_no_go.py` disproves this even for
actual extension signatures.

At the canonical type-49 wall with active circuit support

```text
0/7/14/28
```

the GP-valid positive signings

```text
11880862721603236
4655783301794266
```

have 22 common compatible roots.  For the order
`1 > 2 > ... > 8`, every one points upward: its source label is numerically
larger than its target.  Both parameter signs occur, so allowing either sign
does not repair the directional failure.  Simultaneous `S_8` equivariance
relabels this example against any proposed globally fixed order.

Thus the proved same-factor root connectivity cannot be upgraded to a
global triangular potential.  A dynamic receiver atlas or another global
properness mechanism is still required.

## 5. Naive Gale complementation is not a triple closure

The proposed substitution

```text
p_I -> epsilon(I,I^c) p_(I^c)
```

cannot be applied term by term to the six displayed normalized-chart factor
formulas.  The products in each formula have unequal column multidegrees.
Consequently the independent column rescalings needed to put the Gale kernel
back into the standard chart change their relative coefficients.

`verify_diag3_gale_normalization_no_go.py` gives an exact zero-locus
regression.  It reconstructs an isolated canonical wall center for each of
types `36,38,48,49,50,51`, applies the exact normalized Gale involution, and
evaluates the proposed naive complement equation at the dual point.  The
original primitive factor vanishes, while the proposed transported equation
is nonzero in all six cases.  Thus affinity masks computed from those naive
equations do not describe the transported residual walls and cannot close
any part of the triple census.

This does not rule out Gale duality itself.  A valid version must pull back
the **full labeled occurrence determinant** on an unnormalized kernel such
as `[-A^T|I]`, or equivalently retain every normalization weight, then strip
only proved nonvanishing parent units.  It must separately verify the
resulting zero locus, signs, chart domain, and factor/source accounting.

That corrected construction has now also been tested, with the appropriately
narrow conclusion recorded in `DIAG3_TRIPLE_GALE_CANARY_NO_GO.md`.  Full
occurrence pullbacks on `[-A^T|I]` are well-defined modulo complementary
parent units.  Across all `40,320` relabelings of six pinned hard canaries,
none has a common three-coordinate affine block or a triangular unit graph;
the larger exact modular necessary screens likewise have zero survivors.
Thus corrected Gale duality does not supply any of the currently tested
small certificate families for those canaries.  This is a bounded no-go,
not an exclusion of boundary-stratified Gale roadmaps or other birational
symmetries, and it closes none of the `1,819,789` residue.

## 6. Pointwise tangential exits do not automatically form a strip

The row-2599 tangential calculation first produced a useful conditional
algebraic fact: **if** its selected shear rays assemble into a proper relative
cylinder over the complete `q0` end, then the displayed unit cylinder
incidence kills the tapered-ribbon class integrally.  The base-only support
scan did not prove that geometric hypothesis.

For each base point separately, taking the component of the feasible shear
ray that contains parameter zero gives an interval ending at the triple locus
or parent infinity.  First endpoints can nevertheless jump when a terminal
wall is born, dies, or becomes tangent in the two-parameter
`(base,shear)` plane.  The union of the pointwise components can then have a
frontier made of feasible, parent-uniform points.  Adding only the selected
terminal endpoints does not make its projection proper; taking the ambient
closure can add extra fiber components and destroy relative acyclicity.

`verify_diag3_tangential_first_exit_no_go.py` pins the smallest exact model.
Let the base be `[-1,1]`, the compactified shear fiber be `[0,2]`, the triple
relative point be `(0,1)`, and `u=2` be parent infinity.  The fiber component
from `u=0` ends at `1` over `s=0` and at `2` otherwise.  Every selected fiber
pair is an interval relative to its endpoint, but their union is not closed:
`(1/n,3/2)` converges to the omitted feasible point `(0,3/2)`.  Its ambient
closure has central fiber

\[
                  ([0,2],\{1,2\}),
\]

whose relative `H_1` is `Q`.

Thus proper base change cannot be invoked from pointwise exit data alone.
The row-2599 canary has since received the missing certificate: the complete
two-parameter verifier covers all 84,840 labeled wall occurrences, restricts
all 26,740 factors, and finds 1,707 active block-1 factors.  Bernstein signs
put their only zeros on the triple-relative side or the intersection of two
parent-wall facets.  The actual residence domain is therefore a proper
relative quadrilateral, and the signed `N/M` contraction genuinely kills
that one class integrally.

This is a scoped repair, not a universal first-exit theorem.  Every other
pair component still needs its own coverage-complete frontier, or a global
theorem providing the same proper compactification with controlled Hardt
transitions.  The rectangle regression remains mandatory protection against
reusing pointwise exits without that extra audit.

## 7. Smallest honest remaining pair certificate

After any coverage-safe contraction of root and occurrence choices, retain
one finite relative complex for the actual three-signature family.  It need
only record, modulo two:

1. connected chamber and factor-wall germs;
2. support-shrink and simultaneous-factor attachments;
3. which branches meet the triple locus and which meet parent infinity; and
4. the parity of every remaining two-cell incidence.

Prove the single middle-rank identity of Section 3.  This is strictly smaller
than the signed integral `N,M`/Smith endpoint, while remaining cover-correct
and exactly sufficient for the rational diagonal-three theorem.

## 8. Recommendation

Diagonal three should remain open.  The smallest theorem-grade completion
has two independent finite certificates:

1. **Triple certificate.**  Pin the exact `1,819,789` source rows, then give
   a boundary-stratified semialgebraic roadmap for every connected component
   of their three-factor intersections.  Every leaf must meet a proved
   parent-boundary face (or another already relative face), with concurrence
   rank drops, chart denominators, sheet attachments, and source accounting
   retained.  A different symmetry is welcome, but its exceptional divisors
   must appear in this roadmap rather than be silently declared infinity.
2. **Pair certificate.**  Build a coverage-certified relative cell complex
   for every exclusive-pair component and its triple/parent frontier,
   including all two-parameter exit jumps and simultaneous-factor faces.
   Prove that it has an integral signed lift with `MN=0`, then replay only the
   unsigned mod-two middle-rank equality.  Integral Smith units are optional
   strengthening, not part of the rational target.

Neither certificate can cancel or substitute for the other in the closed-
cover spectral sequence.
