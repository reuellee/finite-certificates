# Review of Stage 2b (GPT-5.6 xhigh via codex) — adversarial verification

Reviewer: Claude (this repo's session agent), 2026-07-30/31. Stage 2b was
executed repo-pointed (context read from the repo, not inlined) with full
execution rights; see `STAGE2B.md`. This review verified the load-bearing
claims independently, found one substantive gap, and closed it.

## Independently verified

1. **Checker audit.** `check_stage2b.py` is a genuine trust boundary within
   the executor's own work: stdlib-only, it re-derives the chamber set with
   deterministic exact rational witnesses, re-enumerates the 16,570
   representatives with its own DFS, rebuilds the integral system rows, and
   verifies every certificate identity. It passes everything in ~4s.
2. **Shared-misconception elimination.** Because generator and checker share
   an author, the reviewer rebuilt the system matrices from first principles
   in independent code (own cross/determinant routines, facet_lp side
   labeling) and verified a random sample of **1,500/1,500** bundle
   certificates exactly against that independent B — y ≥ 0, y ≠ 0, Bᵀy = 0
   in integer arithmetic.
3. **σ-set equality.** The reviewer's independent enumeration of the valid
   labeled assignments from `U_ints`' own incidence (vectorized 2²⁰ scan
   over a separately-sampled chamber structure) equals the bundle's set
   exactly — 33,140 = 33,140 as *sets*, not merely counts. The Stage 2a
   labeling-gap failure mode is excluded.
4. **The 43 ⇒ 44 parity argument** (so that excluding 44 yields f₀ ≤ 42) was
   re-derived and is sound: chamber adjacency embeds in the 5-cube graph
   (bipartite), the support-difference zero set decomposes into cycles
   alternating chambers and walls, so generic (T, w) gives an even bicolored
   count; a 43-vertex instance has 43 strict-witness vertices which persist
   under a (T, w)-perturbation at fixed U, and genericity then forces ≥ 44,
   contradicting the certificates.
5. **Honest-negative spot checks**: the antipodal-coverage counts and the
   0/100 symbolic outcome are reported with correct scoping (the
   symmetric-coverage conjecture of Stage 2a is now *disproven* — a real
   result: T-independent equal-pair support cannot cover all classes).

## Gap found and closed (review finding)

**The k = 0/5 split argument in `STAGE2B.md` is insufficient as written.**
It reduces those cases to Q = conv(Z, 2Z), which is only the exact-homothet
subfamily; general all-one-sign weight differences with free midpoints give
Q = Z ⊕ conv({0} ∪ (t₀ + Z_δ)), not a homothetic pair, and the claimed
"at most 42" does not follow from the stated separation argument.

Closure (this review): the same Gordan machinery was run for the k = 0
split (s = all-minus) over **all 33,140 valid labeled assignments**:
**33,140/33,140 infeasible with exact primitive-integer certificates, zero
feasible, zero failures** (`k0_bundle.json.gz`, same system order as the
core bundle); k = 5 follows by the global flip. The homothetic argument is
retired; the theorem no longer depends on it.

## Post-review status of the theorem

For the explicit integer configuration `U_ints`, combining:
- core bundle (k = 1, 2; both labeled flip members): 66,280 exact
  certificates — executor, sample-verified independently;
- k = 3, 4 by the global flip symmetry (verified as an identity on the row
  model);
- k = 0, 5: 33,140 exact certificates — this review;
- the parity/perturbation argument for 43 (verified);
- `cert_35_42.json` (repo, earlier): a 42-vertex instance with exact
  witness/non-vertex certificates —

**max f₀(3,5) = 42 on the directions of `U_ints`, exactly and completely
certified.** The conjectured value 44 of Conjecture 6.6 part 1 (odd case)
is therefore not attained at this configuration; by Prop 6.5's proven upper
bound (44) and this theorem, any 44-vertex (3,5)-zonoboxtope — if one
exists at all — must use directions outside this configuration's
equivalence... more precisely, outside the specific U_ints direction set.
The global statement max f₀(3,5) = 42 over ALL configurations remains
open (Stage 2c): the certificates are per-configuration, the symbolic
chirotope-wise attempt is 0/100 so far, and cell-transfer is the named
frontier.

## Curation

Committed: `STAGE2B.md`, `check_stage2b.py`, `make_stage2b.py`,
`gordan_bundle.json.gz`, `t0_k1_bundle.json.gz`, `symmetric_coverage.json.gz`,
`reference_structure.json`, `second_configuration_crosscheck.json`,
`symbolic_gp_search.py`, `symbolic_gp_results.json`, `k0_bundle.json.gz`
(review), this review. The checker runs standalone
(`python check_stage2b.py` → PASS, ~4s); it does not yet cover the k=0
bundle — its verification lives in the review script and should be folded
into the checker in a follow-up.
