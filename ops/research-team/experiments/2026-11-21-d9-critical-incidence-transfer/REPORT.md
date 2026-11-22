# 9DVL: positivity amplification via low-index critical incidence

Date: 2026-11-21. Scope: **bounded method-transfer pilot**, not a proof of any unproved 9DVL diagonal. Original ledger: **2/9; D9 open**. Publication is additive and does not modify canonical V10 or the proof ledger.

## Source alignment and choice

The 2026-11-20 Alpöge/Claude RH announcement describes iterated theta lifts as part of an analytic/arithmetic positivity argument. The Lean and Mathlib communities subsequently issued a joint formal-verification statement. The literal theta-lifting constructions, their arithmetic hypotheses, and their length estimates have **no established map to 9DVL**. We transfer only the **design pattern**: accumulate individually justified positive-semidefinite constraints until the unwanted kernel disappears. This is a mathematical analogy, **not** a use of the RH theorem or a consequence of theta lifting.

Source references:

- https://leanprover-community.github.io/blog/posts/riemann-hypothesis/
- https://www.alphaxiv.org/abs/2611.claimed-riemann-hypothesis-proof
- Repo: `ai/omreal/DIAG9_SIGN_GEODESY_AUDIT.md`; `ops/team/d9-universal-cut-falsifier/FINDINGS.md`; `ai/omreal/ATLAS_HELLY.md`.
- Prior November 20 local research: `9DVL_D9_Fiber_Elimination_Pilot_2026-11-20.md`, `9DVL_D9_Barrier_Stress_Test_2026-11-20.md`, and `9DVL_D9_Global_Proof_Plan_and_Executed_Gate_2026-11-20.md` (ChatGPT Library, not presented as merged GitHub files).

The existing 9DVL work has **already** established connected-fiber projection and shown that log-barrier uniqueness is too strong: a connected sector can have several minima. Repeating the fiber lemma or insisting on unique critical points would make no progress. This cycle tests the *critical incidence* alternative from the barrier stress test, with exact integer incidence matrices rather than numerical eigenvalues.

## General rank-one positivity lemma (elementary, unconditional)

Let `G=(V,E)` be a finite graph, allow loops, and let `D` be its oriented vertex-by-edge incidence matrix over `Q` (a loop gives the zero column). Define its graph Laplacian `L=D D^T`. For all real vectors `v`,

`v^T L v = sum_{(i,j) in E} (v_i-v_j)^2 >= 0`.

Consequently `ker L` consists exactly of vectors constant on each connected component; hence

`dim_Q ker L = #components(G) = |V| - rank_Q D`.

Adding a **source-certified** edge `(i,j)` adds the rank-one positive-semidefinite matrix `(e_i-e_j)(e_i-e_j)^T`. The kernel loses exactly one dimension if and only if `i,j` were in different connected components before that edge; otherwise it does not change. Proof: a new kernel vector must already lie in `ker L` and satisfy `v_i=v_j`. Thus adding *valid* attachments monotonically reduces the component-count uncertainty. It is not permissible to add an imagined edge or infer an edge from equality of factor signs.

For a proper Morse function on a finite union of open intervals in `R`, vertices can be its index-zero critical points (local minima); one edge is supplied by each index-one critical point (a local maximum), connecting the minima reached to its left and right. The graph has exactly the connected components of the original domain. Proof: each open interval has finitely many critical points, a minimum (properness), and alternating extrema. The order along that interval makes its minima a connected path through all intervening local maxima, with no edge between different intervals. This is a **one-dimensional** theorem; higher-dimensional index-one attachments require separately certified descending branches, which we do not have for 9DVL.

## Exact canary A: a disconnected nine-region abstract model

Reuse the *abstract*, not source-reconstructible `UOM(4,8)`, countermodel from the repository's D9 falsifier:

`q1=y`, `q2=x^2-1-y`, `q3=z1`, ..., `q9=z7`, with every `q_i>0`.

The explicit change `s=y/(x^2-1)` identifies its feasible sector with

`({x<-1} disjoint_union {x>1}) x (0,1) x (0,infinity)^7`.

Thus there are precisely two components regardless of how many additional independent convex witness fibers are adjoined. Project to the base `x^2-1>0`. The proper barrier

`Phi_D(x) = x^2 - log(x^2-1)`

has derivative `2x(x^2-2)/(x^2-1)` on the base. It has precisely two nondegenerate local minima, at `x=+-sqrt(2)`, and no interior local maxima. The exact incidence matrix is 2-by-0, `rank(D)=rank(L)=0`, and `dim H0=2`. This is a decisive countercontrol to any claim that empty/local-only witness lifting *itself* makes connectedness follow.

## Exact canary B: connected sector with several minima

Reuse the November 20 positive-polynomial canary

`p(x)=(x^2-4)^2+1/4 > 0` on all real `x`;
`Phi_C(x)=x^2-log(p(x))`.

Exact differentiation yields

`Phi'_C(x) = 2x (4x^4-40x^2+97)/(4x^4-32x^2+65)`.

The denominator is `4(x^2-4)^2+1 > 0`; the numerator has the critical points

`x=0, x=+-sqrt(5-sqrt(3)/2), x=+-sqrt(5+sqrt(3)/2)`.

The minima are `0` and `+-sqrt(5+sqrt(3)/2)` (three vertices). The two maxima `+-sqrt(5-sqrt(3)/2)` are index-one critical points, each joining neighboring minima. In left-to-right order the exact incidence matrix is

```
D = [-1   0]
    [ 1  -1]
    [ 0   1]
```

It has rational rank 2, and `L=D D^T` has exact rank 2, leaving `dim H0=3-2=1`, correctly detecting that `p>0` is connected despite having **three separate minima**. A connected-sector test based on uniqueness of stationary points would incorrectly reject this example. This incidence-based test does not.

Adding the two certified index-one edges has PSD rank progression `0 -> 1 -> 2`. Removing one edge or replacing it by a self-loop leaves `dim H0=2` and is rejected by the verifier's negative controls. Merely fabricating a bridge between the two components in canary A would also force `dim H0=1`; hence geometric soundness of every edge is indispensable.

## Machine replay

Run `python verify_critical_incidence.py` (Python standard library only). The verifier checks the polynomial derivative identities and root-order discriminant, constructs the exact integer boundary and Laplacian matrices, performs independent rational row reduction on each, verifies `rank D=rank L`, evaluates the component dimensions, and rejects edge-deletion/self-loop hostile modifications. The committed `RESULT.json` is the complete deterministic output, not a separate authoritative proof source. It reports **13 exact checks passing**, connected canary `H0=1`, disconnected canary `H0=2`, PSD rank progression `[0,1,2]`, and hostile altered graphs `H0=2`.

Trust boundary: the topology of the one-dimensional canaries is proved in this note; the executable replay audits its explicit algebra and matrices. This is **not** an independent verification of a 9DVL parent, a higher-dimensional Morse attachment, or the Alpöge theorem.

## Decision and next theorem-capable gate

**Survives:** an incrementally checkable positivity-amplification *certificate format* for connectedness, provided the input is a **complete, source-backed** index-0/index-1 Morse incidence graph. It avoids the false `unique minimizer` target. It also distinguishes the disconnected abstract 9-region falsifier from the connected multi-minimum canary in exact arithmetic.

**Fails / cannot claim:** no inference from theta lifts to semialgebraic connectivity; no conclusion from local wall/pivot data alone; no inference from a graph made of sampled critical points without an exact all-critical-point count and every index-one handle attachment. No new global sign-sector component count, parent coverage, signature antichain denominator, or 9DVL diagonal has been proved.

**First required new input** for an actual D9 application: choose a source-reconstructible parent-2599 nine-family with the exact 70 parent brackets and properly oriented active factor list (the 3,539 count is a *candidate-active* census, not a complete certified wall incidence object). Construct a proper barrier on the *entire* strict parent sector. Prove by exact real-algebraic isolation that **all** index-zero and index-one critical points (including degenerate stratified substitutes where needed) are accounted for, and certify the global incidence/descending-endpoints of every index-one attachment. Only then evaluate the rational Laplacian rank. Failure of the low-index completeness gate means **STOP**, not local atlas growth. No complete all-parent decision procedure or theorem-level strict decrease has been furnished by this pilot.

**Ledger:** original 9DVL remains **2/9**. D9 and the other six open diagonals remain unproved. Canonical V10 `STOP / NONE` is unchanged; this is an additive bounded prospecting result, not a reopened construction program.
