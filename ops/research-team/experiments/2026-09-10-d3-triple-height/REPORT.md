# Triple escape: parent-line theorem and the remaining critical locus

The original score remains **2/9**. This cycle proves a full subclass of the
missing factor-triple theorem and identifies a more precise remaining
obstruction. It does not establish the third diagonal.

## Accepted progress

**Every triple with at least two factors in global families 36 or 38 has
noncompact connected components**, for every realizable uniform rank-four
parent on eight labels and every original normalized parent component.
The third factor may have any of the six global kinds. The proof includes
all coefficient ranks, all concurrence collisions and all allowed projected
parent coincidences. The full proof is
[TWO_PARENT_LINE_FACTORS.md](proof/TWO_PARENT_LINE_FACTORS.md), independently
reviewed in [TWO_PARENT_LINE_AUDIT.md](referee/TWO_PARENT_LINE_AUDIT.md).

The mechanism is exact. An ordinary representative of each selected factor
forces its unique concurrence onto a parent line. Write those points as
Y_a+tY_b and Y_c+uY_d. After contracting at the third factor's concurrence,
the remaining constraints are four affine equations in four parent heights
over an open six-dimensional parameter base. A rank drop gives a positive-
dimensional full convex fiber. At full rank, the solution is a graph over an
open base. Neither case permits a compact connected component.

This uses the newly audited extension of the contraction coordinates to
**all six factor families**, including the required coincident projected
parents for kinds 36 and 38. See
[ANCHOR_COVERAGE_AUDIT.md](referee/ANCHOR_COVERAGE_AUDIT.md) and its
[independent constructive review](proof/ANCHOR_AUDIT_REVIEW.md).

## The precise remaining problem

Fix ordinary occurrences for three arbitrary factors, with concurrence points
p,q,r. All three collision loci p=q, p=r and q=r form a closed union with
vanishing H_c^0. Re-anchoring the contraction at the repeated point proves
this using at most four affine equations in five heights; the all-equal
piece has a full four-height fiber. The
[coincidence audit](referee/COINCIDENCE_EXCISION_AUDIT.md) checks the excision.

In a contraction chart write the two remaining wall equations as F(A,h) and
G(A,h), with four projected-parent coordinates A and four heights h. Outside
the collision union define

\[
 K=\{F=G=0,\ \operatorname{rank}(d_hF,d_hG)<2\}.
\]

The complement of K projects submersively onto an open subset of R^4, so its
components are noncompact. Compact-support localization shows that

\[
                 H_c^0(K;\mathbb Q)=0
\]

would suffice to complete the universal factor-triple endpoint. Together
with the already completed universal pair endpoint and the inherited wall-
union comparison, that would give the original third diagonal. This last
vanishing statement remains unproved. Full details and the pole-free circuit
formula for the two height gradients are in
[VERTICAL_CRITICAL_REDUCTION.md](proof/VERTICAL_CRITICAL_REDUCTION.md).

Neither a dimension count nor ordinary smoothness settles K. It is also not
proved that a critical point must have collinear concurrence points. Even
distinct collinear points require a further escape argument. With only one
parent-line factor, the analogous construction leaves a compatibility
equation; the square-affine proof above does not extend automatically.

## Exact checks and their limits

The inherited simultaneous critical canary (39,48,50) is redundant:

\[
             q_{39}=(f-i)q_{48}+(1-c)q_{50}.
\]

Its entire triple zero set is a previously proved pair zero set. Two
independent exact implementations reconstruct its nonzero parent brackets,
ordinary concurrences and vertical derivatives. It earns no new count.

The falsification track constructed 120 actual relabeled determinant
occurrences at one fixed projected parent. Among them, 22 quadratic
restrictions give 231 unordered pairs. Exact pencil analysis, including
algebraic exceptional parameters and the parameter at infinity, excludes
uniform vertical critical points for those pairs at that fixed projection.
This is finite evidence about regularity. A smooth fixed-projection
intersection could still have a compact component; the calculation is not a
proof of global triple escape. The full scope and replay are in
[falsifier/FINDINGS.md](falsifier/FINDINGS.md).

## Accounting and reproducibility

The previous universal pair theorem remains complete for all 9,476 pair
orbits. The inherited triple inventory has 79,102,449 rows, with 77,940,147
already covered and 1,162,302 in the old residue. The new subclass's overlap
with that exact residue was not reconstructed, so no numerical increment is
claimed. See [SOURCE_SCOPE_AUDIT.md](SOURCE_SCOPE_AUDIT.md).

The base is commit a7a98a927e57c8872aca2b1e48d4615ede649171. Its full checkpoint
is preserved under checkpoint/. SOURCE_MANIFEST.json binds the inherited
files and pinned additional sources. CHECKPOINT_MANIFEST.json binds the new
deliverable; CLEAN_REPLAY.json records clean replay. The final independent
verdict is [referee/FINAL_REVIEW.md](referee/FINAL_REVIEW.md).

The next work should target the collision-free critical locus for triples
outside the two-parent-line subclass: either prove its H_c^0 vanishing or
construct an exact uniform critical example that tests a proposed geometric
classification. Repeating generic fixed-projection sampling cannot discharge
that universal obligation. Conventional proofs remain admissible; a finite
certificate requirement is not the blocker in this cycle.
