# D3 critical geometry: proved reductions and a corrected route

The original score remains **2/9**. This checkpoint does not prove the original
third diagonal. It proves global escape lemmas for substantial closed pieces
of its remaining geometric problem and replaces two false proposed shortcuts
with exact, independently verified statements.

The remaining sufficient endpoint is: for every original realizable uniform
rank4 parent on eight labels, every normalized parent component X, and every
three distinct primitive factors P,Q,R, every component of
X intersect {P=Q=R=0} is noncompact. Universal factor-pair Hc1 vanishing is
already proved for all9476/9476 source pairs. Together with the accepted
aligned-wall comparison, the full triple endpoint would prove original D3,
including both its injectivity and triple-bad obligations. No restriction to
generic parents, minimal signatures, cross-signature factor triples, or a
finite-certificate proof format has been introduced.

The original obligations are Hc0(T)=0 and injectivity of
D=(r01,-r02,r12): Hc1(A01) direct-sum Hc1(A02) direct-sum Hc1(A12) -> Hc1(T),
where Aij=Bi intersect Bj and T=B0 intersect B1 intersect B2, for every original
internal antichain. The all-factor triple endpoint is sufficient rather than
necessary; a direct proof of these original statements could bypass it.

## New conventional proofs

All statements below retain every original parent component and all relative
parent labelings. They are proved deductively; sample computations are used
only as diagnostics and independent arithmetic checks.

| Closed piece or structural statement | Verified conclusion | Proof |
|---|---|---|
| Three selected ordinary concurrences are collinear and one factor has kind36 or38 | The full collinear piece has Hc0=0 | [One-low collinear theorem](proof/ONE_LOW_COLLINEAR_ESCAPE.md) |
| Same collinear condition with a kind48 factor | The full collinear piece has Hc0=0 | [Complete-quadrilateral theorem](proof/TYPE48_COLLINEAR_ESCAPE.md) |
| Parent on the common concurrence line, or stacked transverse rank at most10 | These full closed pieces have Hc0=0 | [Rank filtration](proof/COLLINEAR_RANK_ESCAPE.md) |
| All factor kinds49–51, with a transverse block of rank at most3 | The full deficient-block piece has Hc0=0 | [Deficient-block theorem](proof/RANK_DEFICIENT_BLOCK_ESCAPE.md) |
| One remaining wall vanishes identically over a full anchor-height fiber | Its closed projected-base piece has Hc0=0 | [Flat-block excision](proof/FLAT_HEIGHT_BLOCK_EXCISION.md) |
| Two remaining height polynomials are proportional by specified parent units on a closed projected-base locus | The full triple piece over that locus has Hc0=0 | [Proportional-section excision](noncollinear/escape_redundant_height.md) |
| Directional gradient kernels for kinds38,48,49,50,51 | Exact global kernel classifications, with a non-flat kind48 axis | [Characteristic kernels](noncollinear/CHARACTERISTIC_KERNELS.md) |

The earlier collision excision and the theorem for two factors of kinds36/38
remain accepted inputs. The new one-low and kind48 results concern the
**collinear locus**, not all triples containing one such factor. They do not
remove the noncollinear part of those triples.

The common-line calculation is explicit. After normalizing the three distinct
points to e3,e4,e3+e4, write Y_i=(g_i,a_i,b_i), with g_i in R2. Each selected
triple gives a sparse row B_I of transverse two-by-two minors, and

\[
 M=\begin{pmatrix}0&B_P\\B_Q&0\\B_R&-B_R\end{pmatrix}.
\]

Four height shears and one genuine scale give rank M at most11. Below rank11,
the full normalized fixed-projection fiber is open in a positive-dimensional
affine space and has no compact component. A parent-unit linear scale chart
and a proper projected quotient make these full fibers closed; a dimension
count alone would not suffice.

The additional theorems address rank11. A low factor or a kind48 complete
quadrilateral forces a block rank at most3 on an entire explicit projected
base. So does a selected plane containing the common line. Rank11 then has a
unique normalized lift over an open subset of a base with no compact
component. The bases and every projected coincidence allowed by uniformity
are included in the proofs.

## What the exact counterexamples establish

Use the uniform parent

\[
Y=\begin{pmatrix}
1&0&0&0&1&1&1&1\\
0&1&0&0&1&-1&4&7\\
0&0&1&0&1&2&-5&-4\\
0&0&0&1&1&3&2&5
\end{pmatrix}.
\]

All70 parent brackets are nonzero. The first witness uses
P=123/145/246/356, Q=125/126/356/378, R=123/145/257/348.
Its concurrences are pairwise distinct and noncollinear, but one height
gradient is zero and their combined rank is1. An independent exact slide
of parent6 preserves all three concurrences and remains in the full parent
residence for -1/3<tau<8/11, ending at parent brackets1467 or4568.

The stronger witness uses

    P=123/145/246/356   (global48),
    Q=123/146/248/378   (global49),
    R=126/145/248/378   (global50).

Its concurrence representatives are (1,2,2,0), (1,2,-4,0), and
(1,-4,-4,-6). Using the height direction p=(1/2,1,1,0), both raw determinant
derivatives in the eight independent height motions are exactly

    (27,45,0,99,0,-18,0,-9).

They remain nonzero and dependent after the four projective gauges are
removed. Thus dependent gradients need not imply collinearity even after
excluding individually stationary walls. Referee-owned Fraction determinant
replays verify the walls, all70 brackets, all ordinary three-normal ranks,
support relabelings and deliberate corruptions.

Neither witness is a counterexample to triple noncompactness. Both are in
inherited covered classes. In the stronger witness, parent7 occurs only in
the single distinct plane378 across all three supports, giving the inherited
light-label escape. It also admits a global sequential-affine graph:

\[
 a=b+c-bc,\qquad d=f(b-1)+ah/b,\qquad g=i(b-1)+ah/b.
\]

The denominators used to prove the graph are genuine parent units. Its full
normalized triple is an open subset of R6 on every uniform parent residence.
Consequently these counterexamples retire the **unrestricted** implications;
they do not refute those implications restricted to the authenticated
unresolved source triples. They earn no new source count.

For the stronger witness's entire source triple, a complete contraction-chart
calculation also identifies its whole vertical critical locus. With the chart
defined in [the critical classification](noncollinear/escape_critical_classification.md),
it is exactly the piece x=2,z=5, where [1234]R=-[1245]Q holds in every height
variable. The new proportional-section excision proves this closed piece
escapes. This is a global explanation of the example, while its source triple
remains inside inherited coverage.

The independent kind48-axis diagnostic also prevents an incorrect repair:
a direction in the height-gradient kernel can have second-order determinant
change -u^2 along a uniform motion. Kernel membership alone is insufficient
for the full-height identity required by flat-block excision. That diagnostic
direction is not asserted to be an actual third-factor concurrence.

## Exact remaining gap

After the accepted closed collinear pieces are removed, the collinear
critical case is confined to factors49,50,51, with all three block ranks4,
stacked rank11 and

\[
\dim\bigl(\operatorname{row}B_P\cap\operatorname{row}B_Q
\cap\operatorname{row}B_R\bigr)=1.
\]

Here the rank condition imposes a genuine compatibility equation on the
projected base. Openness in the whole base has not been proved. The exact
rank11 canary in this checkpoint is vertically regular and therefore does
not settle this remaining critical case.

The new [linear-gradient-pencil gate](proof/LINEAR_GRADIENT_PENCIL_GATE.md)
gives an exact further discriminator. For point-kernel maps C_Q,C_R and
distinct collinear p,q,r, dependence at p is equivalent to proportionality
of C_Q(r) and C_R(q). It supplies a degree-one polynomial kernel of
C_Q-t C_R. No theorem excluding such pencils for all actual source pairs is
claimed. The stronger noncollinear witness fails this collinear gate, as
expected.

Noncollinear critical loci also remain. Both flat-block and proportional-section
excision require a whole-fiber identity, not merely zero first derivatives. The characteristic
kernel results remove several proposed ambiguities but do not prove escape
for every actual kind48 stationary direction or for every pair of dependent
nonzero gradients. The proportional-section theorem proves vanishing under
its stated identity; proving that every remaining critical component satisfies
that hypothesis, or supplying another escape, is still open.

These are missing global deductions, not a demonstrated lower bound on
search runtime. Nothing here establishes a reliable time to3/9.

## Source accounting, verification and continuation

The mathematical input is the authenticated350-file checkpoint at commit
52b4a0efdad0c1bf05503f4126b2c6f5dc78c246, retained under checkpoint/.
The canonical original ledger remains2/9. The inherited triple inventory
has79,102,449 source records,77,940,147 accepted records and1,162,302 residual
records. New numerical triple credit is zero; no overlap census was rerun.
The operational-seven count is a separate unchanged ledger.

The new finite deformation probes change the projected parent and include
cubic restrictions. Their boundary canaries are correctly rejected by zero
parent brackets. Their finite null results are not global regularity or
compactness theorems. The earlier231 quadratic-pair checks still apply only
to their one projected parent and22 quadratic restrictions;92 cubics were
present in the original120-occurrence dataset.

[SOURCE_ROUTE_AUDIT.md](SOURCE_ROUTE_AUDIT.md) records the route and overlap
boundary. [NEXT_GATE.md](NEXT_GATE.md) requires the next attempted
counterexample to start with authenticated survivor provenance. The known
hard canonical tuple(5563,4373,23221), named presentation(5563,16134,19284),
is an inherited concrete target. Its prior exact conic and fold results
remain open inputs, not newly solved cases.

The final bounded calculation now recovers that survivor's ordinary supports
and matches them symbolically to its authenticated source polynomials:

    5563:  123/145/246/378  (type50),
    16134: 126/257/367/458  (type50, raw determinant has opposite sign),
    19284: 157/168/245/348  (type51).

All twelve selected planes are distinct; the union label degrees are
(5,5,4,5,5,4,4,4). Its full P50 contraction gives two cubic height polynomials.
The exact derivative R_w=-[1468][3458] is a parent unit, so w can be eliminated
globally. The remaining resultant E has1690 terms, total degree13 and height
degree7. Its complete vertical critical system is

\[
 E=E_u=E_v=E_t=0
\]

in the seven variables A,B,C,D,u,v,t, with every reconstructed parent bracket
nonzero. Projected leaf coincidence C=D is retained. This is an exact
survivor model, not a proof that the system is empty or has no compact
component, and the larger eliminated polynomial supplies no demonstrated
runtime improvement. [The survivor findings](noncollinear/survivor_FINDINGS.md)
give the compact formulas and replayable input for continuing this case.

The independent reviews are in referee/. The clean replay authenticates
all frozen files and reconstructs the new exact diagnostics in a temporary
directory. It does not claim to mechanically verify the conventional proofs.
The complete deduction and exact remaining gap, rather than another finite
sample, are the promotion gate for the original third diagonal.
