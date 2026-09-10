# 9DVL: direct proof cycle and common weak-primal excision

The third diagonal is **still open: 2/9**. This cycle proves a new geometric reduction in the original parent setting. It does not prove injectivity of the remaining map or noncompactness of every triple-bad component. A conventional mathematical proof was accepted without requiring an orbit-by-orbit computational certificate.

## The proved result

Let X be any normalized component of a realizable uniform rank-four parent on eight labels. For any finite nonempty family S of extension signatures, let B_sigma be the locus where its strict extension inequalities are infeasible. Inside their intersection, let W_S consist of the parents for which one common nonzero vector satisfies every block's inequalities weakly.

Then W_S is closed in X and

\[
H_c^q(W_S;\mathbb Q)=0\qquad(q=0,1,2).
\]

This covers all parent components, all weak-cone dimensions, changing witness supports, projected parallelities, and limits where the weak point becomes a parent point. No antichain hypothesis is needed for this auxiliary theorem, so it applies in particular to every original admissible antichain.

For three signatures set T=B_0\cap B_1\cap B_2, A_ij=B_i\cap B_j, and W=W_{012}. Deleting the same W from T and all three A_ij preserves their compact-support cohomology in degrees zero through two. The natural isomorphisms commute with restriction. In particular the original map

\[
D:\bigoplus_{i<j}H_c^1(A_{ij};\mathbb Q)\longrightarrow H_c^1(T;\mathbb Q),
\qquad D=(r_{01},-r_{02},r_{12}),
\]

is conjugate to the corresponding map on A_ij minus W and T minus W. Its kernel is unchanged. The other remaining original obligation, H_c^0(T)=0, is also unchanged. This is a reduction of the actual original problem, not just a statement about a selected factor wall.

The full proof is in [pair/COMMON_WEAK_PRIMAL_VANISHING.md](pair/COMMON_WEAK_PRIMAL_VANISHING.md). It received independent deductive review and a separate falsification pass. These are research-team reviews, not proof-assistant certification or external peer review.

## Why the proof works

1. Normalize a common weak vector inside a fixed compact simplex using four signed basis inequalities. Retaining that vector gives a proper map with compact convex fibers, so it preserves compact-support cohomology without a degree shift.
2. Stratify by exactly which derived normals vanish on the vector. A finite closed filtration retains the attachments where additional normals vanish.
3. Contract by the weak point. For a fixed projected configuration, the entire allowed parent-height fiber is an open convex four-dimensional cell, or a three-dimensional cell when the weak point is a parent label.
4. Every badness witness is supported on the zero normals. Along a height fiber, each such normal changes only by a positive scalar. Simultaneous badness therefore retains the full convex fiber.
5. Compact-support cohomology below the fiber dimension vanishes. Shriek direct image, the finite closed filtration, and the proper weak-vector comparison give the stated theorem. Closed/open localization gives the coherent excision.

The proof uses actual determinant geometry. It does not rely on the stronger all-factor endpoint, an arbitrary choice of Gordan witness, or a blanket parent-contractibility citation.

## What the exact examples establish

The computations support scope checks; they are not the proof of the vanishing theorem.

**The prior local example is admissible.** Three exact arcs certify that the project-colex signatures 1115179617623167, 1110781571112063, and 1115179340274814 are realizable, proper and pairwise incomparable in the same parent component. Along each arc one signature is feasible and the other two are infeasible. The verifier checks every parent bracket and every strict primal margin, as well as the polynomial Gordan identities on the entire stated parameter interval.

**The uncovered locus is nonempty even in the interior.** A fourth exact arc for that same family is triple-bad and has a positive rank-four witness for each block. Each block's weak-primal cone is therefore just zero. These points are outside W. The common-weak resolution cannot replace all of T.

**Distinct boundary directions also occur.** A separate exact fixture has three unique, linearly independent weak-primal rays. Each block has exactly four zero normals forming a positive rank-three circuit, so its full normalized witness polytope is a singleton. Its colex signature IDs are 5019905080784346, 68833058600159780, and 59311597535541546. The union of these unique supports has label degrees (4,6,4,5,5,3,3,3). Thus neither a common weak point nor the union-support degree-at-most-two shortcut covers every original admissible boundary stratum. These IDs were converted from the producer's lex order during independent review; the final certificate records both conventions explicitly.

This last fixture is not a compact-component or injectivity counterexample. Its three selected walls are affine in one common set of parent-height coordinates. The existing square-affine escape argument handles their common zero set, including rank drops. It illustrates why rigidity of a selected weak-point or witness parametrization does not establish rigidity of the full parent geometry.

## Routes audited without additional theorem credit

The feasible-third-signature chart identifies each other block's badness with intersection of two convex hulls of normalized actual normals. Retaining that strictly feasible private point has a compact-support shift of three; the exclusive-pair target becomes degree four on the incidence space. This coordinate identity does not prove the required vanishing or the independence of the three images in D.

A common unsigned row family can reproduce the inherited graph countermodel with ker D isomorphic to Q^2 while satisfying the known lower-degree vanishings. That construction violates actual uniform-parent normal constraints and is not a 9DVL counterexample. It shows that common rows and the lower vanishings alone cannot supply the missing proof.

The affine-system compactness argument was found explicitly in the pinned historical source DIAG3_TRIPLE_SEQUENTIAL_AFFINE_COMPRESSION.md, section 1. It receives no new method or residual-count credit here. The inherited parent H6/H7 reduction, full Gordan comparisons and Mayer-Vietoris reductions likewise receive no new credit.

## Remaining work and ledger

The exact direct target is now the alternating restriction map on A_ij minus W and T minus W, together with H_c^0(T minus W)=0. The exclusive-pair strata are unchanged. A proof must control the regions with distinct weak directions and the regions where even individual weak directions do not exist, including how those regions attach and reach parent infinity.

A concrete next attempt should construct a global relative-cohomology or frontier-incidence model on this complement. Retaining separate weak points does not yet do so: the exact multiweak height test has only gauge motion in a selected fixture, and other constructions introduce bilinear constraints. Any proposed replacement must prove its comparison map and compact-support behavior before its local calculations can close an original obligation.

| Ledger item | Status after this cycle |
| --- | --- |
| Original diagonals proved | 2/9 |
| Original pair-map injectivity | Open |
| Original triple-bad H_c^0 | Open |
| Original operational obligations closed this cycle | 0 |
| Common weak-primal vanishing and coherent excision | Proved; independently reviewed |
| Stronger pair-wall coverage, inherited | 8,902 of 9,476 factor-pair orbits |
| Stronger pair-wall remainder, inherited | 574 factor-pair orbits |
| Triple-factor residue, inherited | 1,162,302 source records |

The factor counts are not original parent-component counts or a percentage of the proof. No completion-time estimate or guaranteed convergent search is justified by this cycle. Removing the computational-certificate requirement allowed a useful conventional proof; the remaining obstacle is a missing global argument.

## Reproducibility and provenance

Mathematical inputs are pinned to 59fec66666518257c585194b81061f60d91f439d. The immediately preceding checkpoint is 499f1190d988be5729b38db59e6cc8230fae7857. The supplied research index is an entry point; the pinned sources and current ledger determine the mathematical status.

The new proof, exact fixtures, independent verifiers, handoffs and source audit are included with this report. CHECKPOINT_MANIFEST.json authenticates the snapshot; replay_checkpoint.py checks those identities and runs the new independent computational verifiers in an isolated copy. It does not pretend to machine-prove the deductive theorem. The final independent assessment is referee/FINAL_REVIEW.md.

This is an additive research checkpoint. It does not change the original theorem ledger or merge a purported third diagonal.
