# Conjecture 6.6 continued: (4,6) resolved affirmatively; systematic odd-n resistance at (3,5), (4,5), (3,7)

Attack on Conjecture 6.6, *Maxout Polytopes* (Balakin, Cox, Loho, Sturmfels,
arXiv:2509.21286 §6), continuing `attack_maxout66.md` (which resolved the
smallest open case (4,4)). **2026-07-30.**

## Results

**Result 1 — CONFIRMED: (d,n) = (4,6) of part 2.** An explicit rational
(4,6)-zonoboxtope with **104 = 4·Σ_{k≤3} C(5,k)** vertices (the conjectured
maximum = the absolute cap). Certificate `cert_46_104.json`; verifier
`verify_c66_new_cases.py` pins f0 = 104 **exactly** in stdlib Fraction
arithmetic: all 2⁷ = 128 candidate sign points are pairwise distinct, 104
carry strict witness directions (vertices) and the other 24 carry explicit
rational convex combinations of other candidates (non-vertices). Modulo the
classical zonotope vertex bound (a d-dimensional zonotope with n generators
has at most 2·Σ_{k≤d−1} C(n−1,k) vertices), the case (4,6) is fully
resolved: max = 104. This is the second confirmed case of part 2, and the
first with n > d, where the paper reports no computational evidence at all.

**Result 2 — CONFIRMED (achievability): the even-n value of part 1 at
(3,8).** An explicit rational (3,8)-zonoboxtope with **110 =
4·Σ_{k≤2} C(7,k) − 6** vertices, exactly the conjectured maximum for the
first even n beyond the paper's DFS range (n ≤ 6). Certificate
`cert_38_110.json`, same exact structure (110 witnesses + 402 non-vertex
combinations over the 512 candidates). Because the conjectured value sits
below the cap 116 here, this confirms the **achievability half** of the
even-n formula at n = 8; the upper-bound half remains conjectural (their
DFS did not reach n = 8). The same searches never produced 112, i.e. no
refutation of the even-n deficit appeared.

**Result 3 — certified lower bounds at three odd-n cases that RESIST their
conjectured values.** Explicit rational instances with exactly

| (d,n) | cap | conjectured max | certified here | gap |
|---|---|---|---|---|
| (3,5) | 44 | 44 (part 1, odd) | **42** | 2 |
| (4,5) | 60 | 60 (part 2) | **58** | 2 |
| (3,7) | 88 | 88 (part 1, odd) | **84** | 4 |

(same exact witness + convex-combination structure; the counts are pinned,
not merely bounded below). These certify max ≥ 42 / 58 / 84. The
*conjectured* values were not found by any of the methods below, despite
search effort several orders of magnitude beyond what the paper reports
using for its own evidence.

## The empirical dichotomy

Every case probed with **n even or n = d** attains its conjectured maximum,
mostly within minutes: 16 at (3,3), 26 at (3,4), 60 at (3,6), 32 at (4,4)
(prior attack), and now 104 at (4,6) and 110 at (3,8). Every case probed
with **n odd, n > d** stalls at exactly the certified values above and never
moves. In detail, at
(3,5) the value 42 was the terminal count of: (i) ~1.5·10⁴ samples of the
paper's own Prop 6.5 family (endpoints on the unit sphere, split residual
weights) with exact-deduplicated hull counting — the paper reports 1000
samples sufficing for 44; (ii) hill-climbing in the full midpoint family;
(iii) ~250 *complete-per-direction-set* branch-and-bound searches (method
M3 below), including near-coplanar, incommensurate-fan and perturbed
families, at margins δ = 10⁻³ and 10⁻⁶; (iv) generator-drop seeding from an
exact (3,6)-extremal (all six drops → 42). At (4,5), 58 was terminal for
the analogous battery *plus* six generator-drops from the exact 104-vertex
(4,6) instance — the smaller case resists while its larger neighbor falls
instantly, which argues against raw search weakness as the explanation. At
(3,7), 84 was reached independently twice and survived eight
generator-drops from the exact 110-vertex (3,8) instance (all drops ≤ 80);
86 and 88 never appeared.

## Methods (validated before use; all claims are exact certificates)

**M1 — paper-faithful sampling + exact hull counting**
(`search_maxout67.py`). Segments mᵢ + [−uᵢ, uᵢ]; every vertex of
Q = conv(Z^a ∪ Z^b) is one of the 2^{n+1} sign points. The counter
deduplicates exactly and never joggles (both the prior attack's undercount
and the joggle overcount are excluded); it reproduces the exact generic
zonotope counts at n = 5, 6, 7.

**M2 — chamber model with the T-reduction** (`tsearch.py`). For full-support
instances Z^a, Z^b are normally equivalent and f0(Q) = #chambers +
#bicolored, where chamber ε of the arrangement {uᵢ⊥} is bicolored iff
s_ε = T + Σ_A αᵢεᵢuᵢ − Σ_B βⱼεⱼuⱼ avoids ±cone{εᵢuᵢ} (the paper's
Prop 6.3/Thm 5.5 specialized). **All midpoint freedom enters through the
single vector T = Σ_A αᵢmᵢ − Σ_B βⱼmⱼ**; the prior attack's centered family
is exactly T = 0, explaining its systematic shortfalls. Validated: model
count = hull count on live instances.

**M3 — facet-side coloring + complete-per-U branch and bound**
(`facet_lp.py`). The sign of ⟨s_ε, r⟩ at a facet normal r = uᵢ×uⱼ is shared
by all chambers around r, and — because Q is not centrally symmetric when
T ≠ 0 — the antipodal sides ±r carry *independent* signs, each **linear** in
(T, α, β). Cap attainment ⇔ some side-sign assignment makes every chamber
see both signs (not-all-equal constraints) and is LP-realizable. For fixed
directions U the branch and bound (LP-pruned partial assignments, rows
normalized so margins are scale-free) is **complete** up to the δ margin.
Validation: finds the cap at (3,3) on the first random U (hull-confirmed);
never finds the impossible cap 28 at (3,4) in 222 complete runs — matching
the paper's proven max 26.

## A falsified intermediate hypothesis (kept for the record)

Before the (4,6) run, every observed maximum fit the one-parameter law
"deficit from cap = 2⌈(n−d)/2⌉", which extends the paper's even-n rule and
would have contradicted part 2 wholesale. We treated the law as a
prediction and tested it out-of-sample at (4,6): the law says 102; the
search promptly found **104**. The law is dead, and the surviving pattern
is the odd/even dichotomy above. (The paper's own formulas and its d=2
extremal constructions are parity-split too — Thm 6.1's odd-n examples use
incommensurate fans — so parity structure in this problem has precedent.)

## What this does and does not establish

- (4,6) is **resolved** (modulo the classical zonotope bound); the three
  odd-n certificates are **lower bounds only**. Conjecture 6.6 is **not
  refuted** anywhere in this note.
- The odd-n resistance admits two readings: (a) the conjectured odd-n
  values are wrong for n > d; (b) odd-n extremal instances exist but occupy
  a thin, structured region that defeats generic sampling, generic-U
  complete searches, hill-climbing, and generator-drop seeding alike —
  while the even-n extremals are generic. The paper's d=2 odd-n extremals
  being *incommensurate* constructions lends (b) some plausibility; the
  failure of its own 1000-sample recipe (per our re-implementation) at
  (3,5) cuts against the paper's evidence either way.
- The one direct tension with a stated result: Prop 6.5's tightness claim
  at (3,5) ("using only 1000 samples … this method succeeds"). Our
  re-implementation of that exact recipe reproduces 16/26/60 instantly but
  tops out at 42 for n=5 in 15× the sample budget. Possible resolutions:
  a thin extremal region their run happened to hit; a float-hull
  overcount in their tightness verification (near-duplicate vertices); or
  a subtle definitional mismatch — our formalization reproduces every
  other value they report, which bounds how large such a mismatch could
  be. The paper publishes no instance data or code to check against
  (searched arXiv ancillary files, MathRepo, author pages, 2026-07-30).
  **An explicit certified 44-vertex (3,5)-zonoboxtope from the authors
  would settle this immediately**, and the harness here would verify it in
  seconds.
- Search-negative results are not proofs. M3's completeness is per
  direction set; the U-space is not exhausted.

## Reproduction

- `python verify_c66_new_cases.py` — exact verification of all five pinned
  counts (stdlib only, ~2 s).
- `search_maxout67.py sanity` — M1 ladder: 16/26/42*/60 (*the contested
  case; the paper claims 44).
- `facet_lp.py`, `tsearch.py`, `ray_polish.py`, `build_cert_extremal.py` —
  search/build tools kept for provenance; floats there, exactness lives in
  the verifier.
