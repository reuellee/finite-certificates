# Referee report: `maxout35note.tex` — "The maximum number of vertices of a (3,5)-zonoboxtope is 42"

Reviewer: Claude (Fable 5), maximum-effort adversarial pass with independent
re-derivation and re-computation. Date: 2026-07-31.
Scope: the note, its ancillary bundle, `capstone/CAPSTONE.md`, the certificate
artifacts, the prior GPT-5.6 and Gemini 3.1 Pro reports, and the source
paper's HTML (`bcls.html`) for definition fidelity.

## VERDICT: NEEDS FIXES

The mathematics is correct. I re-derived every step of the reduction chain
myself, re-ran every checker, re-enumerated the valid-pattern set from
scratch (a fourth independent enumeration), re-verified sampled certificates
both symbolically (my own Grobner basis, my own identity construction, with a
working negative control) and by specialization at two fresh integer
realizations of the reference chirotope that are not `U_ints` and not any
group image of it, and re-verified the coverage completeness pattern-by-
pattern for all four split representatives. I found no gap in the proof of
max f0(3,5) = 42, and the attainment instance is exactly verified. The
refutation of Proposition 6.5's tightness at n = 5 and of the odd case of
Conjecture 6.6 part 1 at n = 5 stands.

What blocks immediate submission is a short list of sentence-level defects,
one of which is a checkably false claim about the verification methodology
(the canary sentence — the k = 0 sweep has no canaries), introduced in the
revision that responded to the previous GPT review's item 11. All fixes are
local; none touches the result. After findings 1–4 are addressed, the note
is submittable.

---

## Findings

### 1. SERIOUS — the canary claim is false for the k = 0 sweep
**Location:** `maxout35note.tex` lines 245–248 ("Deliberately impossible
control systems (`canaries') … were wired into **every** final certificate
sweep and correctly rejected throughout"); same overclaim in
`capstone/CAPSTONE.md` §2 ("Canary discipline …: **every sweep** wires in a
provably-uncertifiable negative control and a known positive control; all
passed in every shard").

**Evidence.** The three final certificate sweeps are the k∈{1,2} complement
sweep (`stage2c2_gpt/gp_all_d2_sweep.py`, 4 shards), the k=0 sweep
(`stage2c2_gpt/k0_cellwide_sweep.py`, 1 shard), and the {0,2}-split sweep
(`capstone/split02_cellwide_sweep.py`, 4 shards).
- The four `gp_all_d2` shard files serialize a `controls` array: negative
  canary → `EXACT_DEGREE_NO_GO` (rejected), positive control →
  `EXACT_CELLWIDE_CERTIFICATE`. Correct.
- The four `split02` shard logs (`capstone/split02_shard{0..3}.out`) each
  print `canaries OK` from `run_canaries` before the sweep. Correct.
- `k0_cellwide_sweep.py` (read in full, 140 lines) contains **no canary or
  control logic whatsoever**; its shard JSON has no `controls` field; and
  `stage2c2_gpt/REVIEW_completion_claude.md` correctly attributes canaries
  only to the complement sweep (item 1) and makes no canary claim for the
  k=0 sweep (item 2). The master note (`attack_c66_deficit.md`) is likewise
  accurate ("canaries passing in every shard" is said only of the
  k∈{1,2} completion).

So "every final certificate sweep" is false for the sweep that produced
33,140 of the 132,560 certificates (including 570 explicit ones). This
sentence is precisely the narrowed replacement demanded by REVIEW_note_gpt
item 11, and the narrowing landed on a still-false statement — the one
place where the previous review cycle's fixes introduced a defect.

**Mathematical impact: none.** The k=0 bundle is re-verified by the
standalone audit (all quotient-ring identities + specialization), was
re-checked 970/970 in the completion review, and I re-verified **all 570
explicit k=0 certificates** at two fresh realizations of the chirotope
(finding zero failures; see verification log below). But in a certificate
paper the methodology claims are part of the trust story and must be exact.
**Fix:** e.g. "…were wired into the k∈{1,2} completion sweep and the
{0,2}-split sweep and correctly rejected throughout; the k=0 sweep ran
without canaries and its certificates are covered by the standalone audit."

### 2. MINOR — §2.2 asserts a false equality; the proof needs only "≤"
**Location:** `maxout35note.tex` lines 189–193:
"$f_0(Q) = \#\text{chambers} + \#\text{bicolored chambers}$, where a chamber
… is bicolored when it contains linear objective directions maximized on
each of the two copies."

As literally stated (generic U, a, b > 0 — the standing hypotheses at that
point), the equality is false in admissible edge cases. Example: a = b and
all midpoints such that T = 0, i.e. Z^a = Z^b. Then every objective
direction is maximized on (a point of) both copies, so under the stated
tie-inclusive definition every chamber is bicolored and the formula yields
44, while f_0(Q) = 22. Under a strict reading of "bicolored", equality can
still fail through cross-chamber candidate coincidences (v_A(C) = v_B(C')
merging two counted vertices). What is true unconditionally — and is all the
proof ever uses at this point — is the inequality
f_0 ≤ #chambers + #bicolored (strict sense), which I re-proved via the
extreme-ray decomposition of the pointed chamber cones; the literal equality
is then correctly re-asserted *in strict generic position* in §2.5 ("the
count … is literal"), where I verified it holds. **Fix:** one word — write
"≤" in §2.2 (with equality in the generic position of §2.5), or add the
no-coincidence proviso.

### 3. MINOR — the "≤ 20" step in §2.1 is stated with an incomplete justification
**Location:** `maxout35note.tex` lines 178–184.

From "at most 2(1+4+6) = 22 …, with equality iff the arrangement is simple"
alone, a non-generic configuration gives ≤ 21, not ≤ 20. The missing
half-step: chamber counts of central arrangements are even (chambers come in
antipodal pairs; concretely, for 5 distinct central planes in R^3 the count
is 2·L_2 + 2 where L_2 = Σ_lines (multiplicity − 1) ≤ 10, which I verified
by Zaslavsky/Whitney — one coplanar triple gives exactly 20). The claim
"≤ 20" is **true**, and in fact even the lazy bound 21 + 21 = 42 < 43 would
suffice for the argument (only f_0 ≥ 43 must be excluded in the degenerate
regime), but as printed the inference does not follow from the stated facts.
**Fix:** add "and chamber counts of central arrangements are even" (or cite
the 2·L_2 + 2 formula).

### 4. MINOR — "Searches that are exhaustive for each fixed sampled direction configuration" still overstates the artifact
**Location:** `maxout35note.tex` lines 162–164.

Per the master note's own definition (`attack_c66_deficit.md`, method M3),
per-configuration completeness is qualified: fixed A/B split (first
⌈n/2⌉/⌊n/2⌋ generators), weights in [0.02, 10], side margins ≥ δ under the
floating LP's tolerances, within a time budget. "Exhaustive … for each fixed
sampled direction configuration" (the phrasing requested by
REVIEW_note_gpt item 9) drops the fixed-split and box/tolerance
qualifications. Since this sentence is only evidence for an explicitly open
question, either add "for the searched model" or drop the aside.

### 5. NOTE — vestigial "(after a normalization removing square roots)"
**Location:** `maxout35note.tex` lines 196–197. In the note's own
parameterization no square roots ever arise: with I_i = m_i + [−u_i, u_i],
Δh(±C_ij) = ±⟨C_ij, T⟩ + Σ_t s_t w_t D_tij holds identically with
w_t = |a_t − b_t| and D_tij = |det(u_t,u_i,u_j)| (scalar triple product; I
re-derived eq. (2) from scratch and it is exact as printed). The
parenthetical is an artifact of the Stage-2b unit-vector convention and may
confuse a careful reader; consider deleting it or saying "(w_t = |a_t − b_t|
after the harmless positive row scaling used in the implementation)".

### 6. NOTE — "two zonotopes with pairwise parallel generators"
**Location:** `maxout35note.tex` line 100. The paper (bcls.html lines
411–416) says "corresponding generators are parallel"; "pairwise parallel"
invites a wrong reading (all generators mutually parallel). Say
"correspondingly parallel generators".

### 7. NOTE — the OM-realizability parenthetical is not load-bearing
**Location:** `maxout35note.tex` lines 262–265. The citation ("all rank-3
oriented matroids on at most eight elements are realizable … so there are no
other cells") is true but unnecessary for the reduction: the chirotope of
any real generic configuration automatically satisfies the three-term GP
sign conditions, hence lies in the enumerated 384 (necessity is the only
direction used); realizability of the remaining cells is irrelevant, and
even phantom non-chirotopes in the enumerated set would be harmless since
the set is a single orbit through χ_ref. Fine to keep as reassurance, but a
skeptical reader may waste time believing the argument depends on it.

### 8. NOTE — audit description slightly over-uniform
**Location:** `maxout35note.tex` lines 358–366. "re-verifies every
certificate in the library: coefficient nonnegativity, all quotient-ring
identities …, and specialization …" — for the 74,923 family items the audit
(correctly) checks the single-class criterion plus exact specialization; the
quotient-ring re-derivation applies to the 57,637 explicit certificates
(the family identity is an ordinary polynomial identity needing no GP
reduction, as the note itself says at lines 236–240). Consider "…all
quotient-ring identities of every explicit certificate…".

### 9. NOTE — "whether the odd-case deficit 2 persists for all odd n > 3"
**Location:** `maxout35note.tex` lines 164–166. At (3,7) the certified value
84 sits at deficit 4 from the conjectured 88 (the true max could be 84, 86,
or 88), so "the deficit 2" reads ambiguously. Clarify (e.g. "whether the
conjectured odd-n values fail for all odd n > 3, and by how much").

### 10. NOTE — "a depth-first search over the combinatorial types"
**Location:** `maxout35note.tex` lines 72–74. In the paper the DFS is over
valid bicolorings, performed for each combinatorial type of zonotope
(bcls.html lines 1612–1635). Cosmetic; "for each combinatorial type" would
be exact.

### 11. NOTE — CAPSTONE-side wording (the note points readers there)
**Location:** `capstone/CAPSTONE.md` §2 ("all eight quotient-ring
identities") — the implementation (`gp_degree3_search.quotient_matrix`,
re-read line-by-line) imposes ten identity families: five u_t-dotted
T-identities plus five weight identities, which is sufficient and stronger
(the five u_t span R^3, forcing the 3-vector T-part to vanish); "eight"
refers to B's columns. Also: CAPSTONE's §3.1 perturbation lemma is stated in
zonoboxtope coordinates (a, b, m) and CAPSTONE's Claim is zonoboxtope-scoped
(internally consistent), while the candidate-coordinates recast that powers
the note's candidate-family claim exists only in the note; since the note
advertises CAPSTONE as "the full argument", consider porting the recast
there. (The GPT capstone review's finding 4 — the SymPy dependency sentence —
is fixed in the current CAPSTONE §4.)

### 12. NOTE — scope of the completeness side-remark
**Location:** `maxout35note.tex` lines 238–240. The boundary theorem
("provably the complete coefficientwise-positive mechanism among ordinary
polynomial identities") is established in the artifacts for the prefix
splits k ∈ {1,2} (33,437 vs 32,843, reconfirmed by `check_stage2c2.py` in
this review). Not load-bearing — the library never relies on family
completeness — but the sentence could carry the k∈{1,2} qualifier.

### 13. NOTE — externally unverifiable claims
The public-repository claim (lines 140–143) cannot be checked from this
machine; ensure the tree (including `capstone/` and the shard files) is
actually public at submission time. The BCLS bibliography entry
(arXiv:2509.21286, 2025) matches the source HTML.

### 14. NOTE — LaTeX status
Fresh compile with MiKTeX `pdflatex -halt-on-error`, two passes: exit 0,
6 pages, no errors, no undefined references; only underfull hboxes in the
monospaced-filename paragraphs (cosmetic, caused by `\sloppy`). Both
blockers from REVIEW_note_gpt (abstract placement, xcolor) are correctly
fixed. The submission zip's `maxout35note.tex` and ancillary files are
byte-identical to the working copies; `anc/cert_35_42.json` is
byte-identical to the top-level certificate.

---

## Disposition of the previous review cycle (REVIEW_note_gpt.md, 12 items)

Items 4, 5 (LaTeX blockers): fixed, verified by fresh compile.
Item 6 (verifier scope): fixed acceptably ("once equipped with vertex
witnesses by any exact convex-hull code … in the format of our ancillary
verifier" — accurate; the shipped script verifies its five named files).
Item 7 (candidate scope): fixed by the candidate-coordinates lemma; I
re-proved it sound, including the previously-uncovered case of equal or
proportional width vectors with independent translations (see below).
Items 8, 9, 10, 12: fixed (with the residual phrasing points in findings
4 and 9 above). Item 11: the "no unverified model output" half is fixed;
the canary half was mis-narrowed and is now finding 1.

---

## Independently verified (what and how)

All computations below are mine unless stated; "fresh realization" means an
integer configuration with chirotope equal to χ_ref that is neither U_ints
nor any (π, ε)-image of it (built by perturbing 8·U_ints entrywise and
checking the chirotope).

1. **Definition fidelity (bcls.html).** Eq. (1) of the note matches the
   paper's (24) verbatim (segments I_i ⊂ R^d, a_i, b_i ∈ R_{≥0}); the
   candidate definition (HTML 411–416: two zonotopes, corresponding
   generators parallel — hence independent translations and widths);
   Proposition 6.5's statement, tightness sentence, DFS-over-bicolorings
   proof method, sampling recipe and the "Using only 1000 samples … this
   method succeeds" sentence (HTML 1612–1641); Conjecture 6.6 parts 1–3
   verbatim (part 1's odd/even formulas exactly as printed in the note;
   part 2 gives 60 at (4,5) and 104 at (4,6); part 1 gives 44/88/110 at
   n = 5/7/8 — all recomputed); Remark 6.7 verbatim; the neural-network
   framing sentence matches the paper's abstract nearly verbatim.
2. **Chamber model.** Re-derived Δh(±C_ij) = ±⟨C_ij,T⟩ + Σ_{t∉{i,j}} s_t
   w_t D_tij exactly (scalar triple product; no normalization needed), the
   25×8 system, and Gordan's alternative as stated. Re-proved: strict
   44-attainment (in strict generic position) forces every chamber
   strictly bicolored, and — via Minkowski–Weyl for the pointed chamber
   cones — both strict signs among each chamber's incident rays, i.e. the
   observed σ lies in the NAE set. This is the necessity direction the
   proof requires; enumeration overkill is harmless.
3. **Chambers, incidence, valid count (from scratch).** Verified all ten
   3×3 minors of U_ints nonzero; verified the 22 stored chamber sign
   vectors are distinct and realized by the stored exact rational
   witnesses, and that 22 is the maximum (so the list is complete);
   recomputed the full 22×20 chamber/ray incidence from the definition
   (closure conditions ε_k⟨u_k, ±C_ij⟩ ≥ 0) — equal to the reference's
   `chamber_side_incidence`; total incidences 80 = 4 per ray (matches the
   local structure and the Euler check V−E+F = 20−40+22 = 2); exhaustively
   scanned all 2^20 sign assignments for the not-all-equal condition:
   exactly **33,140**, and the set equals the reference `VALID_BITS`
   (fourth independent enumeration). Verified the incidence data is
   determined by the chirotope (signs only), so it is identical at every
   realization of χ_ref.
4. **Library accounting.** Re-derived the single-class family eligibility
   per split and counted within my own valid set: 32,570/24,691/8,746/8,916
   family and 570/8,449/24,394/24,224 explicit — exactly the note's
   74,923 + 57,637 = 132,560 = 4·33,140. Verified pattern-by-pattern (not
   just counts) from the shard files that for each of the four splits,
   family ∪ explicit = the 33,140 valid patterns, disjointly. Verified the
   committed audit ledger: per-bundle counts sum to exactly 132,681 =
   132,560 + 121 (120 prioritized targets + positive control, redundant),
   0 failures, verdict PASS, 1351 s ("about 20 minutes").
5. **Certificates — fresh-realization specialization (mine).** For two
   fresh realizations: all 570 explicit k=0 certificates, 60 sampled per
   gp_all_d2 shard, 60 sampled per split02 shard (all degree 2 — no
   degree-3 entries exist), and sampled family items at all four splits,
   decoded with the shard variable layout (side-major, homogeneous
   degree-2/3 monomials in the ten D's; layout re-derived and confirmed
   against `quotient_matrix`) and checked with **my own row builder**:
   B^T y = 0 in all 8 columns exactly, y ≥ 0, y ≠ 0. ~2,400 checks, zero
   failures. This directly confirms cell-wideness beyond the reference
   configuration and outside the orbit of U_ints.
6. **Certificates — independent symbolic verification (mine).** For 9
   sampled certificates (3 each from gp_all_d2, k0, split02): rebuilt the
   ten identity polynomials (five u_t-dotted T-equations + five weight
   equations) in my own signed-D convention, reduced them modulo **my own**
   sympy Grobner basis of **my own** GP relations (whose validity on real
   configurations I first sanity-checked on random integer matrices): all
   reduce to 0. A deliberately corrupted certificate coefficient produces a
   nonzero residue (D0·D1·D6), so my checker is not vacuous — and the
   residue shows these identities genuinely need the GP ideal.
7. **Single-class closed form.** Re-derived by hand that y_{ij,±} = 1,
   y_{w,t} = 2 D_tij is an exact cell-wide certificate whenever the class
   has equal ray signs σ* with σ* s_t = −1 off the pair (T-parts cancel
   antipodally; weight parts cancel against positivity rows), and machine-
   checked it at fresh realizations.
8. **Symmetry.** Re-ran `check_om35_uniqueness.py` (384 uniform chirotopes,
   single orbit, U_ints inside; code read line-by-line — the enumeration
   axioms are necessary conditions for realizable chirotopes, which is the
   only direction used; the group action code is correct including
   alternating-sign relabeling). Re-ran `check_split_orbits.py` (exit 0):
   stabilizer order 10 with 10 distinct permutations (faithful), orbits
   {∅}; {0}×5; {0,1}, {0,2} (5+5); k=3 reps (0,1,2), (0,1,4) with
   complement-consistency confirmed; "ACCOUNTING CONFIRMED". Independently:
   |stab| = |G|/|orbit| = 3840/384 = 10; the only order-10 subgroup class
   of S_5 is D_5; D_5 on the pentagon has exactly the edge/diagonal orbits
   on 2-subsets — matching. Verified the subset action uses π only (ε does
   not move the split), as reorientation fixes each segment.
9. **Transport and flip.** Re-derived C_{lo,hi}(gU) = τ C_{ij}(U) with
   τ = ±ε_lo ε_hi (sign − iff π reverses the pair), the D-permutation, and
   the flip row identity Row(flip σ, −s; c, r) = Row(σ, s; c, −r) by hand;
   noted that pure negation (−σ, −s) also transports (T-columns flip,
   kernel unchanged), so the stage-2b flip convention is equally sound.
   Re-ran `check_transport.py`: 2,220 (g, certificate) pairs verified
   exactly against an independent row builder at g·U_ints, FLIP OK,
   VALIDITY CLOSURE OK (all 10 stabilizer elements fix the valid set).
   Also verified the main chain needs only the geometric path: the
   transformed instance is itself a strict-44 instance at a realization of
   χ_ref whose own observed σ is valid for the (chirotope-determined,
   hence identical) incidence.
10. **Perturbation lemma (candidate coordinates).** Re-proved: every vertex
    is strictly exposed among the 2^6 candidate values; candidates are
    polynomial (linear) in (c_A, c_B, a, b); cluster-persistence gives
    f_0(Q') ≥ v; the excluded loci (residual zeros, the twenty side values,
    all pairwise candidate coincidences) are proper algebraic subsets — in
    candidate coordinates every pair of distinct candidates is non-identical
    as a polynomial map (same copy: a differing sign contributes ±2a_i u_i;
    cross copy: the c_A − c_B block), covering in particular candidates with
    equal or proportional width vectors and independent translations, the
    case the previous review flagged. Finite unions of proper subsets have
    dense complement, and U is untouched, so genericity and the chirotope
    are preserved.
11. **Parity.** Re-proved in full: in strict generic position Δh's zero set
    on S² avoids the 20 vertices, meets each wall in at most one interior
    point (linear restriction, nonzero at the bounding rays), meets each
    open chamber in one connected great-circle arc (plane ∩ convex pointed
    cone), enters/exits through distinct walls, and so traces closed walks
    visiting each bicolored chamber exactly once in the chamber-adjacency
    graph, which is bipartite (sign-vector parity); closed walks in
    bipartite graphs are even, hence #bicolored is even and f_0 = 22 +
    #bicolored is even; f_0 ≥ 43 forces f_0 = 44 with all chambers
    bicolored and strict side signs. Also verified the literal count in
    strict generic position (winners distinct, every winner has a
    full-dimensional normal cone, tie-only-on-crossing analysis).
    Consistency spot-check: all five certified instances have even
    bicolored counts (42 = 22+20, 58 = 30+28, 84 = 44+40, 110 = 58+52,
    104 = 52+52).
12. **Degenerate cases.** Re-derived f_0 ≤ f_0(Z^a) + f_0(Z^b); zonotope
    vertices = chambers of the dual central arrangement (robust to
    repeated/zero generators and lower-dimensional zonotopes); r = 2L_2 + 2
    for 5 distinct central planes (Zaslavsky), so non-simple ⟹ ≤ 20;
    support-deficient ⟹ ≤ 2(1+3+3) = 14; all branches < 43 (finding 3 on
    the printed justification).
13. **Attainment.** Read `verify_c66_new_cases.py` line-by-line: it
    recomputes the 2^{n+1} candidates from (U, M, a, b) in exact Fractions,
    checks pairwise distinctness, strict witnesses, and exact convex
    combinations partitioning the candidates — which pins f_0 exactly
    (vertices of conv of a finite set = its extreme points). Ran it: PASS
    in 1.8 s ("~2 seconds" as claimed), all five instances (42/110/104/
    58/84). Proposition 2's U, m_1, a, b match `anc/cert_35_42.json`
    coordinate-for-coordinate; the (4,6) resolution arithmetic
    (104 = 2·2Σ_{k≤3}C(5,k) = 2·52) and all conjectured-value arithmetic
    (44/60/88/110 at the cited cases) recomputed.
14. **Gordan endgame.** The strict-generic 44-instance satisfies its own
    labeled system strictly (tautologically, with w = |δ| > 0), the
    normalized (σ, s) lies in (valid set) × (four representatives after
    stabilizer/flip), and the library's certificate specializes to that
    realization with y ≥ 0, y ≠ 0, B^T y = 0 — contradiction with Gordan's
    theorem, whose statement in the note is correct.
15. **Other checkers.** `check_stage2c2.py` re-run: PASS (91 s), including
    the 51,430/14,850 equal-pair vs HARD ground truth and the
    33,437/32,843 boundary theorem counts. LaTeX recompiled clean (finding
    14). Submission zip contents verified byte-identical to disk.

## Assessment

This is a carefully engineered computer-assisted refutation with an unusual
density of independent verification, and it survives a hostile review that
attempted to break each link: the enumeration semantics (necessity, not
sufficiency, is what is used — and it holds), the quantifier bridge from
"all instances" to "one cell, four splits" (single orbit, faithful D_5
stabilizer, edge/diagonal 2-subset orbits, flip for complements — all
re-derived), the cell-wide certificate semantics (ideal membership in the
signed-D GP ideal implies exact vanishing at every realization; confirmed by
my own symbolic reduction and at realizations outside the U_ints orbit), the
degenerate and boundary cases (perturbation lemma in candidate coordinates,
correctly covering the wider candidate family of Remark 6.7), and the
parity endgame. The previous reviews' twelve fixes are correctly implemented
with one exception (finding 1). Fix findings 1–4 (a few sentences); the
remaining notes are at the authors' discretion.
