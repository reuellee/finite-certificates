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
DFS did not reach n = 8). The same searches never produced any count
above 110 (with midpoints there is no central symmetry, so already 111
would refute the even-n deficit); no refutation appeared.

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
search effort well beyond what the paper reports using for its own
evidence: 15× its stated sample budget on its own recipe, plus ~300
complete-per-direction-set searches of a qualitatively stronger kind,
plus structured seeding.

## The empirical dichotomy

Every case probed with **n even or n = d** attains its conjectured maximum,
mostly within minutes: 16 at (3,3), 26 at (3,4), 60 at (3,6), 32 at (4,4)
(prior attack), and now 104 at (4,6) and 110 at (3,8). Every case probed
with **n odd, n > d** stalls at exactly the certified values above and never
moves. In detail, at
(3,5) the value 42 was the terminal count of: (i) ~1.5·10⁴ samples of the
paper's own Prop 6.5 family (endpoints on the unit sphere, split residual
weights) with float hull counting (10⁻⁹ deduplication, no joggle) — the
paper reports 1000
samples sufficing for 44; (ii) hill-climbing in the full midpoint family;
(iii) ~300 *complete-per-direction-set* branch-and-bound searches (method
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

**M1 — paper-faithful sampling + careful float hull counting**
(`search_maxout67.py`). Segments mᵢ + [−uᵢ, uᵢ]; every vertex of
Q = conv(Z^a ∪ Z^b) is one of the 2^{n+1} sign points. The counter
deduplicates at 10⁻⁹ and never joggles (excluding the prior attack's
random-direction undercount and the joggle duplicate-overcount), and it
reproduces the known generic zonotope counts at n = 5, 6, 7 — but it is
floating-point qhull, not exact: search counts are numerical evidence.
Exactness lives only in the certificates.

**M2 — chamber model with the T-reduction** (`tsearch.py`). For full-support
instances Z^a, Z^b are normally equivalent and f0(Q) = #chambers +
#bicolored, where chamber ε of the arrangement {uᵢ⊥} is bicolored iff
s_ε = T + Σ_A αᵢεᵢuᵢ − Σ_B βⱼεⱼuⱼ avoids ±cone{εᵢuᵢ} (the paper's
Prop 6.3/Thm 5.5 specialized). **All midpoint freedom enters through the
single vector T = Σ_A αᵢmᵢ − Σ_B βⱼmⱼ**; the prior attack's centered family maps into the T = 0 slice (as do some
non-centered configurations), explaining its systematic shortfalls. Validated: model
count = hull count on live instances.

**M3 — facet-side coloring + complete-per-U branch and bound**
(`facet_lp.py`). The sign of ⟨s_ε, r⟩ at a facet normal r = uᵢ×uⱼ is shared
by all chambers around r, and — because Q is not centrally symmetric when
T ≠ 0 — the antipodal sides ±r carry *independent* signs, each **linear** in
(T, α, β). Cap attainment ⇔ some side-sign assignment makes every chamber
see both signs (not-all-equal constraints) and is LP-realizable. For fixed
directions U the branch and bound (LP-pruned partial assignments, rows
normalized so per-row margins are scale-invariant) is **complete for the
model it searches**: the fixed A/B split (first ⌈n/2⌉ or ⌊n/2⌋ generators
vs the rest), weights in [0.02, 10], side margins ≥ δ under the floating
LP's own tolerances, within the time budget. "Complete per U" below
always means complete in that qualified sense.
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
  overcount in their tightness verification (near-duplicate or
  triangulated-flat-face vertices); a subtle definitional mismatch — our
  formalization reproduces every other value they report, which bounds how
  large such a mismatch could be; an unstated difference in their sampling
  distribution or post-processing ("1000 samples" may include
  optimization or multiple coefficient draws per sample); or a wording
  slip — "this method succeeds" scoped loosely over n ≤ 6 with n = 5 not
  individually confirmed. Note also that a valid 44-instance cannot be
  measure-zero in the full parameter space (strict witnesses persist under
  small perturbations), so if it exists our samplers assign its basin very
  small mass rather than zero — which is itself notable. The paper publishes no instance data or code to check against
  (searched arXiv ancillary files, MathRepo, author pages, 2026-07-30).
  **An explicit certified 44-vertex (3,5)-zonoboxtope from the authors
  would settle this immediately**, and the harness here would verify it in
  seconds.
- Search-negative results are not proofs. M3's completeness is per
  direction set; the U-space is not exhausted.

## Stage 1 addendum (2026-07-30, later the same day): the σ-complete max-margin search at (3,5)

Executed by GPT-5.6 (codex, maximum reasoning effort) against a written
brief, then adversarially reviewed (`stage1_gpt/REVIEW_stage1_claude.md`;
independent σ-count reproduction, margins-table audit, boundary-instance
rebuild). Design: since any 43+-vertex (3,5) instance forces a generic
arrangement, whose chamber/side incidence structure is unique in every
sample tested, the side-sign assignments σ can be enumerated EXHAUSTIVELY —
there are exactly **33,140** valid ones (16,570 mod global flip; two
independent enumerators in Stage 1 and a third in review agree) — and each
gets a gauge-fixed max-margin optimization over ALL remaining parameters
(directions included).

Result: **the best margin over the entire σ space is 2.1×10⁻¹⁷ — numerical
zero — and it is not attained**: the maximizing sequences degenerate
(T → 0, a weight at the positivity floor, chirotope walls), and the
boundary object rebuilt at the best point has only 36 vertices. The binding
obstruction concentrates on both antipodal sides of the five facet classes
forming the 5-cycle (0,2),(2,4),(4,1),(1,3),(3,0), with a 4-side LP dual
summing to 1. Direction-space optimization is local (the executor's and the
review's shared caveat), so this is strong numerical evidence, not proof —
but it upgrades the working hypothesis to **max f₀(3,5) = 42**, i.e. the
odd case of Conjecture 6.6.1 (and Prop 6.5's sampled tightness at n = 5)
being wrong at n = 5. Stage 2 = turn the T = 0 / 5-cycle dual structure
into an exact impossibility certificate. Artifacts and seeded rerunnable
code: `stage1_gpt/`.

## Stage 2a addendum (2026-07-30): first exact theorem-pieces toward max f0(3,5) = 42

Executed by Gemini 3.1 Pro (High) in three bounded calls against a written
brief (`stage2_gemini/STAGE2A.md`), then adversarially reviewed and repaired
(`stage2_gemini/REVIEW_stage2a_claude.md`). Post-review state:

- **Centered-slice theorem (exact):** at T = 0 the 20 side signs collapse to
  10 class signs (valid assignments are antipodal-symmetric; exactly **200**
  exist, a structure-invariant count). For an explicit integer configuration
  (Pythagorean-quadruple rows), **all 400 (assignment x split) systems are
  infeasible with exact rational Farkas certificates**
  (`stage2_gemini/farkas_t0_exact.json`, generator `t0_exact_fixed.py`): the
  centered slice of that exact cell cannot reach 44. The executor's original
  artifact had a labeling gap (valid set enumerated on one configuration,
  LPs run on another) plus corrupt serialization; the review rebuilt the
  chain self-consistently — the idea survived, the artifact was replaced.
- **The binding obstruction is a Grassmann-Plucker relation:** Stage 1's
  numerically-binding dual demands four class signs (E02<0, E03>0, E13<0,
  E24>0 — decoded from Stage 1's own sigma, orientation-free at T=0) that
  are **algebraically contradictory throughout Stage 1's chirotope cell**:
  c2*E24 + c4*E03 = c1*E02 + c3*E13 holds identically there with all four
  coefficients strictly positive (products of absolute determinants;
  verified exactly on the rationalized Stage-1 optimum, all five
  per-coordinate residuals identically zero). The identity is
  chirotope-conditional — correctly scoped per reorientation class.
- **T-cancellation:** equal dual multipliers on antipodal-symmetric classes
  cancel T identically; Stage 1's best dual instead cancels T through a
  geometric rank-dependence of four facet normals. The precise coverage
  condition for a fully T-independent certificate family is formulated —
  that condition, plus per-cell GP contradictions for the
  symmetry-breaking assignments, is exactly what a complete
  max f0(3,5) = 42 proof (Stage 2b) still requires.

## Stage 2b addendum (2026-07-31): the per-configuration theorem — max f0(3,5) = 42 on an explicit direction set

Executed by GPT-5.6 (codex, maximum reasoning effort), repo-pointed;
adversarially reviewed (`stage2b_gpt/REVIEW_stage2b_claude.md`). Result,
post-review:

**THEOREM (fully certified, exact).** On the directions of the explicit
integer configuration U_ints, no zonoboxtope — any midpoints, any positive
weights, any A/B split — has more than 42 vertices; and 42 is attained
(`cert_35_42.json`). Components: 66,280 exact primitive-integer Gordan
certificates for splits k=1,2 over all 33,140 valid side assignments
(`stage2b_gpt/gordan_bundle.json.gz`; k=3,4 by the global flip); 33,140
further exact certificates closing k=0 (`stage2b_gpt/k0_bundle.json.gz`,
added in review — the original homothetic-copy argument covered only
exact-homothet pairs; k=5 by flip); an even-parity + perturbation argument
excluding 43 (chamber adjacency is bipartite; verified in review); and a
stdlib-only exact checker (`stage2b_gpt/check_stage2b.py`, ~4 s). Review
also verified the sigma-set equality against an independent enumeration and
1,500 sampled certificates against an independently constructed system
matrix.

Consequences and scope: the conjectured odd-n maximum 44 of Conjecture
6.6.1 is NOT attained on this configuration — the first exact, complete
negative instance for the conjectured value at (3,5). The global maximum
over all configurations remains open (Stage 2c): certificates are
per-configuration; the conservative symbolic chirotope-wise attempt is
0/100; and Stage 2a's complete-symmetry-coverage conjecture is now
DISPROVEN (16.1% of classes uncovered for at least one split even at this
configuration), so cell-wide transfer needs a richer certificate family.

## Stage 2c preparation (2026-07-31): third-party validation and the cell landscape

Two computed anchors for the cell-wide program, both this-repo-independent
or citation-free:

- **Third-party exact cross-check** (`check_instances_cddlib.py`, requires
  `pip install pycddlib`): Fukuda's cddlib, in exact GMP rational mode,
  independently recomputes the vertex count of every certified instance —
  32/42/58/84/104/110 — and agrees with all six (an entirely separate
  codebase from this repo's verifiers, from qhull, and from the
  model-generated pipelines).
- **The chirotope landscape at (3,5)** (`check_om35_uniqueness.py`, stdlib):
  exhaustive enumeration from the three-term Grassmann-Plucker sign axioms
  gives exactly **384 uniform rank-3 chirotopes on 5 elements, forming a
  single orbit** under relabeling x reorientation x global negation, with
  `U_ints`' chirotope among them. Hence Stage 2c's quantifier "over all
  generic configurations" reduces to ONE equivariantly-stated chirotope
  cell (realizability of all rank-3 oriented matroids on <= 8 elements is
  classical, so no non-realizable phantom cells exist here).

## Reproduction

- `python verify_c66_new_cases.py` — exact verification of all five pinned
  counts (stdlib only, ~2 s).
- `search_maxout67.py sanity` — M1 ladder: 16/26/42*/60 (*the contested
  case; the paper claims 44).
- `facet_lp.py`, `tsearch.py`, `ray_polish.py`, `build_cert_extremal.py` —
  search/build tools kept for provenance; floats there, exactness lives in
  the verifier.
