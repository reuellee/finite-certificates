# 9DVL guess-and-check experiment — 10 September 2026

Status: candidate results awaiting final independent review. Original cohomological injectivity remains open; the theorem ledger is 2/9.

This cycle tested whether selecting and transporting a single normalized Gordan witness could supply a useful ingredient for the missing boundary-attachment proof. It used the exact September 9 checkpoint and then constructed a new actual uniform rank-four parent family. It did not run a larger census of the old local witnesses.

## Guesses and outcomes

| Guess | Candidate outcome | Mathematical scope |
|---|---|---|
| The old three-row rank event obstructs continuous witness transport. | Refuted on the pinned example: a six-row piecewise rational witness passes through the event and equals the original witness there. | One exact original-parent interval. |
| Full affine rank plus a strictly positive normalized witness makes minimum-norm selection continuous. | Proved by a standard convex-feasibility argument and checked on an exact full56 witness fixture. | A conditional local lemma in a fixed raw-normal gauge. |
| Every proper signature on actual parents admits a continuous normalized Gordan witness choice near every bad parent. | Candidate exact counterexample: two bad approaches force disjoint limit constraints. | One new actual uniform parent chamber and one realizable proper signature; no three-signature antichain is certified. |

## The useful negative result

For a signed derived-normal matrix A(Y), define the normalized witness polytope

\[
P(Y)=\{w\ge0:\;\mathbf1^Tw=1,\;A(Y)^Tw=0\}.
\]

The new literal parent is

\[
Y_0=\begin{pmatrix}
1&1&1&1&1&1&1&1\\
0&1&2&0&1&2&0&1\\
0&0&0&1&1&1&2&2\\
-2&2&4&15&-10&-10&-8&-3
\end{pmatrix}.
\]

All 70 four-brackets are nonzero. For signature 1110781293763710, evaluation on e4 makes 51 signed normals strictly positive and five zero. Consequently every normalized witness at the center is supported on those five rows.

Two explicitly certified parent paths Y1(t) and Y2(t), for 0<t<=10^-6, stay in the same strict parent chamber and have exact positive Gordan witnesses. The last-coordinate equations force any limiting witness to satisfy, respectively,

\[
d\cdot w\le0,\qquad d\cdot w\ge1/89.
\]

These constraints cannot hold for the same normalized vector. Thus a continuous choice of one witness on a relative neighborhood of Y0 in this bad locus cannot exist. A third path supplies a strict feasible extension in the same chamber, establishing that the signature is realizable and its good locus is nonempty. The witness-bearing center establishes that the bad locus is nonempty.

In particular, the raw-normal minimum-norm choice is discontinuous. Its center weights on the five zero rows are (200,32,10,25,0)/267 and d·w=2/89. The stronger no-section conclusion does not depend on choosing the Euclidean minimum.

This is an obstruction to a proposed witness-selection construction. It does not give a nonzero class in the original cohomology kernel, disprove 9DVL, establish a triple-bad compact component, or settle any original source orbit. No literature novelty claim is made.

## What survived

At the earlier pinned rank event, a constant positive five-row reserve exists on the entire exact interval [-75255/222208,75255/222208]. It yields both a continuous six-row witness through the original sparse witness and a separate affine full56 witness whose coordinates are at least 1/1000. The original three-row support has rank two only at t=0 and rank three otherwise. Support enlargement resolves that particular event.

The distinction is concrete: strictly positive full-support witness neighborhoods admit local continuous selection, whereas genuine feasibility boundaries can forbid every continuous choice. The conditional lemma therefore remains useful, but cannot be extended to all bad parents without additional hypotheses.

## Research consequence

The next useful guess should retain the whole witness polytope, or use compatible local choices with explicit comparison data, instead of requiring one continuous witness globally. The new two-path example is a mandatory small test for such a construction. Its first useful output would be an exact attachment calculation that includes both approaches and the full center fiber; a local result would still require a separate comparison with the original compact-support maps.

Original score: 2/9 before and after. Original pair injectivity and triple Hc0 remain open. Original global obligations closed: 0. Pair coverage/residual: UNKNOWN. Triple source records unresolved: 1,162,302; these are not component counts.

## Evidence

Source revisions: 3e69bc43f1a92ebd1c508bd75e695af76c99e0b0 and 59fec66666518257c585194b81061f60d91f439d. The source manifest pins 15 consulted files to exact Git blobs and SHA-256 digests. The checkpoint includes the constructive proof and exact fixture, the falsification family and certificate, and independently implemented referee arithmetic. It is a self-contained snapshot of this experiment and its consulted inputs, not a complete repository-history backup.

Final review and replay details will be recorded before publication.
