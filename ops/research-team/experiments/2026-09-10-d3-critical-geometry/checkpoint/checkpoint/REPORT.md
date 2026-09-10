# 9DVL: universal pair-wall vanishing

The stronger pair-wall requirement is now proved for **all 9,476 factor-pair orbits**, over every uniform rank-four parent on eight labels and every normalized parent component. A conventional geometric proof closes the entire remaining family; it does not require further enumeration of parent realizations.

The original ledger remains **2/9**. The new theorem completes endpoint P in the existing sufficient route to the third diagonal. Endpoint T—noncompactness of every connected component of a triple-wall intersection—is now the sole unproved hypothesis in that route. The original alternating restriction-map injectivity and original triple-bad vanishing are not separately declared solved.

## The theorem proved

For every pair of distinct primitive residual factors f,g and every original parent component X,

\[
H_c^1\bigl(X\cap\{f=0\}\cap\{g=0\};\mathbb Q\bigr)=0.
\]

The inherited proof already covered all factor-kind families except some type50/type51 pairs. The new proof covers every relative labeling of those two kinds, including the hardest balanced cases. Their canonical four-plane supports are

\[
P_{50}=123/145/246/378,\qquad P_{51}=123/145/267/468.
\]

The full new proof is [original/CONCURRENCY_HEIGHT_PAIR_VANISHING.md](original/CONCURRENCY_HEIGHT_PAIR_VANISHING.md), SHA256 `c4542171cc2cd0c1dd5007bc80d3dfa2e079892cf6417edce760410eed069f91`. The independent referee accepted this exact text. The falsification track separately checked its geometric hypotheses and an actual previously hard example. These are independent research-agent reviews, not external peer review or proof-assistant certification.

## Why the new argument works

Each type50/type51 wall is the condition that four actual parent-triple planes share a point. Uniformity forces every three of their normals to be independent, so this concurrence point is unique on the wall. Denote the two points by p and q.

Project the parent configuration from p. The first four planes become four lines in a projective plane, with no three concurrent. Normalize this line frame. Four parent points become fixed intersections of these lines; the other four have one position coordinate each. Their possible projected configurations form an open domain in four-dimensional affine space. Allowed coincidences of projected points are retained.

Lifting back requires four free parent heights, after removing three shears and one scale. Every prescribed parent bracket is affine in these heights, so the entire permitted height fiber is an open convex four-dimensional cell. The first wall is automatic.

When q differs from p, retain its projected point and its height w. Requiring q to lie in the second set of four planes gives **four affine equations in five height variables**: the four parent heights and w. At coefficient rank four, the full nonempty fiber is one open interval. Its base is open in a product of the four-dimensional position domain and the projective plane; no component of that base is compact. Compact-support integration along the interval therefore gives zero in degrees zero and one.

The remaining strata are included in the proof. Coefficient rank at most three gives convex fibers of dimension at least two. The closed stratum q=p has full four-dimensional convex height fibers. Compact-support localization glues these pieces and proves the vanishing. Positive normalization and the uniqueness of q ensure that the construction retains whole fibers in each original parent component.

The key change is the projection being used. The older projection had conic fibers whose components could merge. Retaining the concurrence point produces affine equations and connected full fibers, including rank changes.

## Exact accounting

| Pair-wall coverage | Newly covered | Remaining |
| --- | ---: | ---: |
| Inherited geometric results | 8,902 | 574 |
| One-column affine elimination | 529 | 45 |
| Two-column affine elimination | 27 | 18 |
| Universal concurrence-height theorem | 18 | 0 |
| Total | **9,476** | **0** |

The last theorem actually covers the entire type50/type51 family, including the preceding two layers. The table partitions new credit to avoid double counting. These numbers classify equations up to relative relabeling; they are not counts of original parent components or a percentage of the nine-diagonal proof.

The one-column and two-column arguments remain in the checkpoint as independently reviewed intermediate proofs. Their applicability inventories were reconstructed separately from the authenticated 574-record input. The universal proof depends on the two canonical support types and their parent-unit geometry, not on testing individual parent realizations.

## The precise route from here to 3/9

It is now sufficient to prove:

> For every original parent component X and every three distinct primitive residual factors f,g,h, every connected component of X intersect {f=g=h=0} is noncompact.

Equivalently,

\[
H_c^0\bigl(X\cap\{f=g=h=0\};\mathbb Q\bigr)=0.
\tag{T}
\]

The inherited triple inventory has 79,102,449 factor-triple orbits, of which 1,162,302 source records remain unresolved. This cycle does not change that count. A structural proof of (T) can replace further enumeration; a finite certificate for each row is not a prerequisite.

Here is the complete transfer, using the previously reviewed reduction in [checkpoint/checkpoint/pair/FINDINGS.md](checkpoint/checkpoint/pair/FINDINGS.md), section 1. For an original signature family S, let B be the union of its bad loci, and W the union of all primitive walls circuit-aligned with at least one signature in S. The parent-unit circuit identities give W contained in B, and support persistence makes B minus W clopen in X minus W. Known lower-degree vanishing gives an injection

\[
H_c^2(B;\mathbb Q)\hookrightarrow H_c^2(W;\mathbb Q).
\]

The finite closed-cover spectral sequence for W has only three potentially relevant kinds of terms in total degree two: single-wall H_c^2, pair-wall H_c^1, and triple-wall H_c^0. Single-wall vanishing was already known. Pair-wall vanishing is now complete. Statement (T) would remove the last terms, so H_c^2(B)=0. For every original admissible three-signature family, the inherited duality and Mayer–Vietoris comparison then prove both original D3 obligations and the third diagonal.

This transfer needs all triple walls in the aligned union, including triples aligned to the same signature. Restricting to triples matched to three different signatures is insufficient for this particular proof route. No new parent-contractibility assumption is used.

## What happens when the height argument is extended to triples

Retaining two further concurrence points gives eight affine incidence equations. After the parent-height normalization there are six height variables: four parent heights and two concurrence heights. Positive-dimensional consistent fibers still give escape, but coefficient rank six can leave a single point. The nonempty-image locus is then constrained by compatibility equations; it cannot be declared an open subset of the ambient parameter space.

The alternative track constructed this model on the predecessor's actual three-boundary fixture. The eight-by-ten homogeneous matrix has rank six; its four-dimensional kernel consists exactly of three shear directions and the actual lift scaling. Fixing those gauges gives an eight-by-six system of rank six. Thus the rank-six obstruction to a fixed-direction escape argument is populated, not just a dimension-count possibility.

That fixture is not a counterexample to (T). Letting the concurrence directions vary gives a triangular description of its fixed-parent-projection fiber and an escape argument. It was already settled by a different affine escape in the predecessor, so it earns no additional triple-orbit credit here. A next step within the contraction route is to exclude compact components on the rank-six compatibility locus, or find another projection that retains escape there. A proof of (T) must also cover the remaining factor kinds, all concurrence collisions and all lower-rank strata; the present pair proof does not establish those steps.

## Checks and other results retained

An independent exact reconstruction of the old hard pair, source orbit254, verifies the new height model. Its coefficient matrix has rank four in five variables, its motion changes normalized parent heights, and all 70 prescribed parent signs hold on the full interval

\[
-162656/818755<t<162656/2831745.
\]

This is a scope check for the proof. The theorem itself is not inferred from this example.

The older conic projection was independently shown to have two components at one exact base point and one component at another, within the same parent component. This refutes a locally constant component-sheaf shortcut for that projection; it does not contradict the new theorem. The ruled-quadric marker and rational-chart results remain valid coordinate facts, with no separate cohomology credit.

A separate seven-label deletion argument proves H_4(X;Q)=0 for the original parents, using inherited rank-four/seven-label contractibility and a reviewed one-bad-locus argument. Its author and reviewer were different agents. This extends the supported bad-union duality through diagonal five, but proves no additional diagonal. The historical qualification concerning blanket parent contractibility is retained.

## Final ledger and provenance

| Claim | Status |
| --- | --- |
| Original diagonals | **2/9** |
| Universal factor-pair H_c^1, endpoint P | **Proved, independently reviewed** |
| Stronger factor-pair residue | **0** |
| Universal triple-factor H_c^0, endpoint T | Open |
| Triple-factor residue records | 1,162,302, unchanged |
| Original alternating-map injectivity | Open |
| Original triple-bad H_c^0 | Open |
| Original operational obligations closed this cycle | 0 |

Mathematical historical inputs are pinned to `59fec66666518257c585194b81061f60d91f439d`; the predecessor checkpoint is `401602fe9f8bcfad74116b46bb5574f63b6a3040`. The source manifest authenticates all 216 predecessor files and five additional historical sources. The supplied research index is an entry point, not a substitute for the pinned theorem ledger.

`CHECKPOINT_MANIFEST.json` binds the final snapshot. `replay_checkpoint.py` checks file identities and runs the new exact verifiers in a clean temporary copy. `referee/FINAL_REVIEW.md` records the independent final assessment. The publication is an additive research checkpoint; it does not promote a purported third diagonal.
