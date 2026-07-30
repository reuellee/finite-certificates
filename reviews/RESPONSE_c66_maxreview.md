# Adjudication of the max-settings dual review (2026-07-30)

Reviews: `GEMINI_c66_attack2_maxreview.md` (Gemini 3.1 Pro High, second deep
pass — VERIFIED-SOUND) and `GPT56_c66_attack2_maxreview.md` (GPT-5.6 at
xhigh reasoning — BLOCKING). Every finding adjudicated below; the P1 and all
accepted P2/P3s are applied in the same commit, and the full verifier suite
re-passes (5/5 certificates, run_all 21/21).

## GPT-5.6 findings

| # | Finding | Disposition |
|---|---|---|
| P1.1 | Negative-index aliasing: a combo entry `j = i − 2^{n+1}` satisfies `j != i` yet `pts[j] is pts[i]`, so a hostile certificate could self-certify every non-vertex | **ADOPTED — real soundness hole in the verifier as a trust boundary.** Range check added (`0 ≤ j < len(pts)`, integer-typed) ahead of the self-use check; schema strictness added for instance arrays and witness dimensions while at it. The five shipped certificates use plain hull-vertex indices and re-pass unchanged; as the review itself notes, the witness half (hence every lower bound, and the full (4,6) resolution via cap) was unaffected even before the fix. |
| P2.1 | M1 is float qhull + 10⁻⁹ rounding, not "exact hull counting" | **ADOPTED.** All "exact" language for search counting removed from the note; M1 retitled "careful float hull counting" with an explicit "search counts are numerical evidence; exactness lives only in the certificates". |
| P2.2 | facet_lp "complete per U" needs qualifiers (fixed A/B split, weight box [0.02,10], δ-margin, float LP tolerances, time budget) | **ADOPTED.** The note now defines "complete per U" in exactly that qualified sense and uses it consistently. |
| P2.3 | Reported run counts (~250 vs ~300) unsubstantiated/inconsistent | **ADOPTED (reconciled).** Both documents now say ~300 (session tally at (3,5): 45+53+158+56 = 312 per-U runs, plus 222 at (3,4)); logs were session-side, so the count is presented as reported, not auditable. |
| P3 | "four certificates" docstring leftover; "orders of magnitude" overstatement; README title stronger than body; "centered family is exactly T=0" imprecision; (3,8) refutation threshold is 111 (no central symmetry with T≠0), not 112 | **ALL ADOPTED.** Fixed: "five"; effort quantified as 15× samples + ~300 qualified-complete searches; README title now "(4,6) resolved, (3,8) achievability confirmed"; "maps into the T=0 slice"; threshold corrected to "any count above 110 (111 refutes)". |
| — | Steelman list (10 author-side explanations) | **ADOPTED (merged).** The tension paragraph now includes the sampling-distribution/post-processing possibility, the wording-slip ("succeeds" scoped loosely over n ≤ 6), and the observation that a valid 44-instance cannot be measure-zero (strict witnesses persist under perturbation) — only sampler-mass-starved. |

Not adopted: rejecting certificates with extra unused JSON fields (the new
schema checks pin all dimensions the verifier consumes; unknown extra keys
are inert), and re-running the searches with committed seeds/logs (the note
now explicitly flags search-effort figures as reported rather than
auditable — a future attack should log seeds).

## Gemini findings

VERIFIED-SOUND; no defects. Its three additional author-side explanations
(ghost-claim/typo over the n ≤ 6 range, specialized sampling distribution,
float-hull inflation of a 42 into a 44 via triangulated flat faces) are
merged into the tension paragraph. Its independent re-derivations (the
T-reduction, the a_i = 0 degeneracy being caught by the distinctness check,
the chamber-count assertion equaling the theoretical n²−n+2 maximum) match
ours and stand as recorded.

## Post-fix verification state

`verify_c66_new_cases.py`: 5/5 certificates PASS after hardening;
`run_all.py --fast`: 21/21. The negative-index exploit is covered by a
regression path (out-of-range indices now fail closed).
