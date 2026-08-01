# Adversarial review of `ai/omminor` (MINOR_THEORY.md and its pipeline)

Reviewer: Fable 5 (max-effort adversarial pass), 2026-08-01/02.
Scope: the eight attack areas assigned; everything re-derived or re-run
independently where feasible. All reviewer code is in
`ai/omminor/review_scratch/` (`myom.py` is a from-scratch reimplementation
of colex bases, minors, GP relations, the Gordan/feasibility LP with exact
rational verification of BOTH outcomes, and the G' action; it shares no
code with `minorlib.py` / `coverage_checker.py` / `bfp.py`). `ai/omreal/`
was touched read-only; all runs used `PYTHONDONTWRITEBYTECODE=1`.

## Verdict summary

| # | area | grade |
|---|---|---|
| 1 | Proposition R and the certificate lift | **CONFIRMED** (mechanism reproduced end-to-end from scratch; one disclosed conditionality, see D-4) |
| 2 | Closure fraction 90.7% and its CIs | **CONFIRMED** (all counts and all three Wilson CIs recomputed from the data files; uniform sample verified uniform) |
| 3 | Contractions never witness | **CONFIRMED** (modulo the disclosed omgamma completeness dependency) |
| 4 | Minimal set (1,758) | **CONFIRMED** on a 10-class / 90-deletion independent LP sample + full certificate re-check; no false inclusion or exclusion found |
| 5 | (4,10) infeasibility arithmetic | **CONFIRMED** (all arithmetic re-done; artifact sizes verified on disk; one terminology slip, D-3) |
| 6 | Rank-3 calibration 183/242 | **CONFIRMED — fully independently recomputed** (my own LP on all 2,420 deletions reproduces 183/242, 59 minimal, and the exact per-class histogram) |
| 7 | Canary integrity | **CONFIRMED** (suite re-run; sabotages re-run by me against checkcert; bfcanon validated with my own enumeration and my own group transforms) |
| 8 | Prose audit | **4 minor defects found (D-1..D-4), none load-bearing**; every checked number traced to an artifact |

**Defects found (all minor):**

* **D-1 (low, artifact hygiene).** `data/checkcert_harvest_uniform.log`
  — shipped as the record of the §0 claim "all 5,400 uniform-corpus
  certificates were re-verified by checkcert.py … all accepted" — actually
  contains a **crashed run** (`KeyError: 'n'`, a record predating
  `harvest_pilot.py`'s `setdefault('n'/'r')`), not a pass. The claim itself
  is TRUE of the current file: my re-run accepts all 5,400
  (4,893 R / 116 NR / 391 RESIDUE). The log is stale evidence for a true
  statement. Fix: regenerate the log.
* **D-2 (low, unsupported "at most").** §8.2 computes the crossing-failure
  slice as "at most 14,396 + 60 + 575 = 15,031 (≤1.04%)". The 575
  REALIZABLE(repair) figure is quoted from the wave-15 log line
  (1,074,562 classes), while 14,396 + 60 are from the frozen prefix
  (1,445,227 lines). Scaled, repair ≈ 775 at the freeze, so the "at most"
  is not actually an upper bound; the honest figure is ≈1.05%. No
  downstream impact (§8.3 uses the separately verified 0.91% = 13,117 /
  1,445,227).
* **D-3 (nit, terminology).** §9 calls +7.90 → +11.78 "second differences"
  of log₂(count). They are first differences of (3.46, 11.36, 23.14)
  (equivalently log₂ of the successive ratios); the second differences are
  +4.44 → +3.88. The extrapolated band (next ratio 3–8×10⁴, count
  ~10¹¹–10¹²) is unaffected — both readings land inside it.
* **D-4 (nit, statement hygiene).** Proposition R is stated
  unconditionally but its proof needs the **completeness of the (4,8)
  classification** (2,628 classes) — an omgamma result. §10 does disclose
  exactly this dependency ("rests on omgamma's mass identity and agreement
  with the published counts"), but the Proposition itself should carry the
  proviso. Same for Lemma K / the §3 theorem (completeness of (3,8) and
  (4,8)). Also minor: §11's file table says `data/verify_minimal.json`;
  the actual artifacts are `verify_minimal_{sweep,ext,uniform}.json`; §9
  says the (4,9) cell "closed … at ~86 core-hours" while §0 says the sweep
  is still running (projected vs actual); the two derived catalog files
  `data/cat48_keys.npz` / `data/cat48_lines.txt` are read by three scripts
  but no script in the tree writes them (no recipe — ironically the exact
  sin ATLAS_SPEC §2.3 legislates against). Content of both verified
  correct against `cat_4_8.txt` + `certs_4_8.jsonl`.

**Do the headline conclusions survive?** Yes, all four:
90.7% closure (with the stated caveats) — reproduced; "no classification
theorem worth the name" — supported (the negative structure finding is
consistent with the data; the minimal classes are generic, order-10⁴
projected); Proposition R — correct as a mechanism, verified end-to-end,
conditional only on (4,8) completeness as disclosed; (4,10) enumeration
infeasibility — arithmetic checks out from measured per-class costs and
on-disk artifact sizes.

---

## 1. Proposition R / the lift (CONFIRMED)

**Theory re-derivation.** I re-derived the three claims of §5 from the
definitions: (i) (φ⁻¹L; φ⁻¹a<…<φ⁻¹d) is a GP relation of χ — immediate
since φ⁻¹ is strictly increasing and misses e; (ii) each signed term is
EQUAL (not merely equal up to sign): the brackets are equal by definition
of deletion, and an increasing map preserves inversion counts, so both
tuple-sorting signs are unchanged — hence big/small carry over; (iii) the
basis map B ↦ φ⁻¹B is injective into the bases avoiding e, so the weighted
cancellation transports coordinate-by-coordinate, and untouched
coordinates stay zero. The §5.1 invariance argument was re-checked by hand
(swap(c,d) gives (−T1,−T3,−T2), swap(b,c) gives (−T2,−T1,−T3), both a
3-permutation with one common sign; reorientation contributes
(−1)^{|ε∩{a,b,c,d}|} common to all three terms since the L-part cancels;
global sign contributes (+1)). All correct. Note BFP-existence ⟺
infeasibility of the full strict system, by LP duality, so invariance also
follows abstractly; the term-level argument in §5.1 is right anyway.

**Code vs prose.** `liftcert.py`'s `phi_inv` / `lift` implement exactly
the prose (relabel L and abcd, keep big/small/w). The lifted record is
checked against the ORIGINAL 9-element sign string by `checkcert.py`,
which recomputes the term signs and the cancellation on the 9-element
side — so acceptance is itself the proof, independent of the lift
reasoning. Verified claims:

* Re-ran `checkcert.py` (my copy) on `data/lifted_certs.jsonl`: **80/80
  accepted** (reproduces the canary). On `data/lifted_canaries.jsonl`:
  **5/5 rejected**, each with the specific expected diagnosis.
* With my own deletion code: all 40 (8-elt, 9-elt) pairs in
  `lifted_certs.jsonl` satisfy chi8 = my_deletion(chi9, e), and the
  9-element term list is exactly my own relabelling of the 8-element one
  (0 defects).
* **Fresh end-to-end reproduction** (`attack1_lift.py`): 5 rows liftcert
  never touched (different seed, LAST witness element instead of first);
  my deletion → my LP finds a Gordan vector (exactly reconstructed over ℚ
  and verified) → my lift → **checkcert accepts all 10 records**. My own
  5 sabotages of my own lift (wrong element / weight / big-small swap /
  dropped term / wrong class) → **all rejected**.
* The 24 (4,8) obstructions: my LP finds an exactly verified Gordan
  vector on **24/24** catalog reps — so "its class carries a Gordan
  vector" holds without consulting `certs_4_8.jsonl`'s stored vectors.
* §5.1 transport, computationally: random G'-transforms (my own action
  code) of an obstruction rep stay GORDAN 3/3; of a realizable rep stay
  strictly-feasible 3/3.
* Consequence for WALK_THEORY §7: quote checked verbatim against
  `ai/omreal/WALK_THEORY.md` (lines 328–330); given Prop R, hypothesis
  "all deletions realizable" follows from "no BFP", so the equivalence
  claim (deletion clause redundant) is correct propositional logic.
* §4.3's mechanism additionally needs the sweep's BFP search to find a
  Gordan vector whenever one exists. `ai/omreal/bfp.py::find_bfp` solves
  the full-system LP (HiGHS) and reconstructs exact integer weights; its
  failure modes (float infeasibility, exact-reconstruction failure) can
  only UNDER-certify, pushing classes to OPEN — the safe direction — and
  the measured 451/451 OPEN-rows-without-witness is consistent.

Conditionality: the Proposition needs (4,8) completeness (D-4). Within
that, CONFIRMED.

## 2. Closure fraction (CONFIRMED)

Recounted from `data/minors_{sweep,ext,uniform}.jsonl` with my own script
and my own Wilson implementation (`attack2_counts.py`):

* frozen: 14,396 NR / 13,117 with a NR deletion = **91.12%**, Wilson
  [90.64, 91.57] — matches; hist {0:1279, 1:10021, 2:2703, 3:393} ✓;
* extended: 18,944 / 17,186 = **90.72%** [90.30, 91.12] ✓; minimal 1,758 ✓;
* uniform: 116 / 105 = **90.52%** [83.81, 94.62] ✓; minimal 11 ✓;
* contraction witnesses: **0** in all 20,571 rows ✓; OPEN rows with a
  witness: 0/60, 0/84, 0/391 ✓ (the "451 of 451");
* witness usage: 16,606 occurrences, top-4 = rows 2330/2146/2611/2391 =
  10,432 (62.8%) ✓, all 24 used, row 2597 exactly once ✓;
* the 24-row witness index set rebuilt by me from `cat_4_8.txt` ×
  `certs_4_8.jsonl` verdicts = the set the pipeline used ✓; and
  `checkcert.py` (rerun by me) accepts certs_4_8.jsonl as
  **2,604 R / 24 NR / 0 residue**, covering exactly the 2,628 catalog
  lines ✓ — the witness set is certified data;
* per-element ground truth: for 12 sweep NR rows + 3 uniform NR rows
  (135 deletions), my own LP reproduces `del_nonreal` **element-for-element**
  (a deletion is flagged iff it has a Gordan vector) — the
  canonicalization-based identification is semantically right on sample;
* uniformity of the uniform corpus: `pilot.py --sample49` draws
  `rng.choice(9,276,595, replace=False)` over the full coverage key
  array — genuinely uniform; the merged corpus is 2000 + 400(+repeat) +
  6000-truncated draws, deduplicated (cal∩cal2 = 400 by design — a re-run
  pair; s2000∩u = 2 — consistent with random collision); truncated shards
  are class-blind prefixes, so inclusion stays exchangeable → Wilson CI
  valid (finite-population effects negligible at 5.4k of 9.28M);
* depth-bias: §4.2's per-band table reproduced from the report (sums
  14,396 / 13,117 check; per-band fractions recomputed); the direction
  (falling with depth, so the prefix is optimistic and catalogue-wide ≈
  90%) is ARGUED from the data, not assumed, and the frozen→extended
  drift 91.12→90.72 moved as predicted; the uniform corpus (depths
  12–25, verified) pools to 90.5%;
* the freeze bookkeeping: shard line counts sum to 1,445,227 = 15.58% of
  9,276,595 ✓; extended 1,773,749 = 19.12% ✓; `minors_sweep.jsonl` is a
  byte-prefix of `minors_ext.jsonl` ✓, `harvest_sweep.jsonl` of
  `harvest_ext.jsonl` ✓, minimal_sweep ⊂ minimal_ext ✓; current live
  shards are larger than both recorded offset sets ✓; all 15,171 harvest
  chi distinct ✓ and canonical fixed points (25/25 spot check) ✓;
  harvest↔minors verdicts agree row-for-row ✓.
* §0's re-verification claim re-executed by me: `harvest_sweep.jsonl`
  (15,171: 715 R / 14,396 NR / 60 RES) and `harvest_uniform.jsonl`
  (5,400) — **all accepted** by checkcert. (But see D-1: the shipped
  uniform log shows a crash, not this pass.)

## 3. Contractions never witness (CONFIRMED)

* Lemma C re-proved and re-tested: on 3 certified realizable (4,9)
  records, exact-rational quotient projections along x_e reproduce my
  contraction sign string up to one global sign, for e ∈ {2,5,9}; column
  deletion reproduces my deletion string (Lemma D). My own
  deletion/contraction code was itself validated against random integer
  configurations first.
* Contraction of a uniform (4,9) chirotope is a uniform rank-3 chirotope
  on 8 elements: values never vanish (uniformity — no loops/parallels
  possible), and the GP conditions of χ/e are the χ-relations with e ∈ L
  (checked in code: `gp_valid` passes on all 90 contractions of my
  10-class sample; the pipeline's G1 asserted it on all 185,139 —
  pass lines present in `minorsweep_*.log`).
* "All 135 (3,8) classes realizable, verified not assumed": re-ran
  checkcert on `certs_3_8.jsonl` → **135 R / 0 NR**, and the 135 chi
  strings are EXACTLY the 135 lines of `cat_3_8.txt` ✓. With (3,8)
  completeness (omgamma; published count 135), every possible contraction
  class is realizable — identification not even needed; the pipeline's G2
  ("every contraction key lands in the catalog", asserted on all rows) is
  belt-and-suspenders on top.
* Rank-2 side for (3,10): one uniform class per n, realizable (moment
  curve) — standard; spot-checked in rank3check.py (3 rows, 1 class).

## 4. The minimal set (CONFIRMED on sample; certificates fully re-checked)

* **False-inclusion attack** (`attack4_minimal.py` A): 10 random entries
  of `minimal_ext.txt`; all 90 deletions computed with MY code; my LP
  with exact verification: **0 Gordan vectors — every deletion carries an
  exactly-verified strict-feasibility witness**, i.e. provably not one of
  the 24 (all 24 have Gordan vectors; BFP-existence is a class
  invariant). No false inclusions in the sample. All 90 contractions are
  valid rank-3 chirotopes.
* **False-exclusion attack** (B): 5 random witnessed NR rows: the flagged
  deletion has an exactly-verified Gordan vector in every case → those
  classes are correctly OFF the minimal list.
* Certificates: my checkcert re-run accepts all **1,758**
  `certs_minimal_ext.jsonl` records (and the 1,279 subset), whose chi
  sets equal the minimal lists exactly → every listed class is
  independently certified non-realizable.
* The list recomputed from `minors_{sweep,ext,uniform}.jsonl` (NR ∧ no NR
  deletion ∧ no NR contraction) equals the shipped lists exactly (1,279 /
  1,758 / 11) ✓. §7 structure claims recounted: 1,279/1,279 distinct
  deletion multisets ✓, 1,347 distinct realizable (4,8) deletion classes ✓,
  stab histograms ✓ (from report; consistent). §6.1's own falsification
  artifacts check out: 11,286 + 15,463 + 99 = 26,848 distinct-LP count ✓,
  positive controls 60+60+20 = 140 ✓.
* **bfcanon.py attacked** (area 7 overlap): logic audited (the hi/lo
  two-stage max is a correct lexicographic max over the orbit; the
  mask∘perm composition covers all of G′ since σ·ε = σ(ε)·σ); its (3,6)
  validation reproduced with MY OWN enumeration (23,808 valid chirotopes
  from all 2²⁰; **4 orbits** by union-find under my own generator action)
  and its smoke test re-run (rc=0, same numbers); its form is invariant
  under my own random G′ transforms of two (4,8) reps and separates them.
* Caveat kept: 10 of 1,758 is a 0.57% sample; but the deliverable's own
  §6.1 test (which I audited for logic, not just re-ran: zero Gordan
  vectors across all 15,463 distinct deletions settles misassignment
  REGARDLESS of the canonicalizer) covers the full list, and my sample
  independently validates that test's machinery on both sides
  (positive/negative) with different code.

## 5. (4,10) arithmetic (CONFIRMED, one wording nit)

* Ratios: 11 → 239 (2628/11 = 238.9) → 3,530 (9,276,595/2,628 = 3,529.9);
  growth 21.7× and 14.8× → "15–22×" ✓. Next-ratio band 3–8×10⁴ ⇒ count
  2.8–7.4×10¹¹ ✓ ("a few ×10¹¹", band 10¹¹–10¹² honest). log₂ figures
  3.46/11.36/23.14 correct; **"second differences" mislabel (D-3)**.
  Rank-3 comparison series 2.75/12.3/32.5/71.3 with ratio-of-ratios
  4.46/2.65/2.20 → "decays towards ~2" ✓.
* Costs at 5×10¹¹: 26.5 ms → 3.68×10⁶ core-hours (~420 core-years) ✓;
  16 B/class → 8 TB ✓; 1.12 B/class → 560 GB ✓; 160 B/class → 80 TB ✓.
  The per-class constants verified on disk: `hi.npy`+`lo.npy` =
  2×74,212,888 B = 16 B/class (148 MB) ✓; `tree_4_9.npz` = 10,437,614 B =
  1.125 B/class ✓; `Z.dat` = 1,335,829,680 B = 144 B/class = 4·9·4 ✓.
  26.5 ms/class and ~70/86 core-hours quoted correctly from WALK_THEORY §6
  ✓ (the live log's 30.0 ms/class/core is the contended figure; the doc
  flags contention explicitly in §8).
* Filter economics: 9,276,595 × 6.07 ms = 15.6 core-hours ✓ vs saving
  0.91% × 250 ms × catalog = 5.9 ✓ (0.91% = 13,117/1,445,227 = 0.9076% ✓);
  ceiling 5.9/70 < 10% ✓; slice arithmetic ✓ (modulo D-2's "at most");
  6.07 / 187.9 ms and survivor rates 0.41% / 12.3% match
  `data/fastminor.json` (n=2000 each, 0 disagreements with the pipeline)
  ✓; the §8.1 "80% realizable" workload label verified: first 2,000
  uniform rows = 1,607 R / 350 RES / 43 NR = 80.35% ✓. `fastminor.py`'s
  stage-1 invariant audited: built from the mutable-basis masks of the
  nine deletions via degree/pair-degree multisets — all sorted multisets,
  G′-invariant; stage 1 can indeed only send extra survivors to stage 2.
* n=10 sampling-study plan arithmetic: 10⁶ × ~4 ms ≈ 1.1 core-hours ✓;
  crossings at 2–3× 26.5 ms → 15–22 core-hours ✓ (factor explicitly
  flagged as unmeasured); extension-sampling bias caveat correctly stated.

## 6. Rank-3 calibration (CONFIRMED — strongest result of this review)

Full independent recomputation, zero shared code, zero canonicalization
(`attack6_rank3.py`): the 242 certified non-realizable (3,10) classes
(checkcert re-accepts all 242; 242 distinct strings), all 2,420 deletions
computed with my code (2,274 distinct), each decided by my exact LP
(196 GORDAN / 2,078 FEASIBLE, both sides exactly verified, no numerical
fence-sitters):

> **my count: 183 of 242 classes (75.62%) have a non-realizable (3,9)
> deletion; 59 minor-minimal; per-class histogram {0:59, 1:155, 2:28} —
> identical to `data/rank3check.json`.**

Provenance of "242": `certs_3_10_nonrealizable.jsonl` is certified
(Gordan vectors, re-checked), and SCOPING §4.1 documents a pre-committed
full (3,10) BFP sweep over all 312,356 classes landing on exactly the
published 242 (FMM13 Table 1 − Table 2), which simultaneously certifies
BFP-completeness at (3,10). The (3,9) side: certs_3_9.jsonl re-checked =
4,381 R / 1 NR over exactly the 4,382 catalog lines; my LP-iff-non-Pappus
logic therefore needs only (3,9) catalog completeness (published 4,382;
OMGAMMA.md documents the Knauer–Marc 482 typo). The doc's provenance
statements are accurate.

## 7. Canary integrity (CONFIRMED)

* `canaries.py --tag sweep --all` re-run by me (2026-08-01, live sweep
  running): **ALL CANARIES PASSED**, with numerically identical outcomes
  to §10's table — S1 1080/1080→1030/1080, S2 1080/1080→977/1080, S3
  225/225, S4 0/200 & 0/20, C1 5,608 rows / 0 violations, C2 25/25
  (checkcert rc=0), C3 25/25 (rc=0), C4 12/12 agree + 12/12 separated.
* Sabotage semantics verified at the source: S1/S2 flip real in-memory
  table entries before re-deriving minors (not straw men); S3's
  per-deletion sensitivity condition is the right one (a corrupted basis
  must move exactly the deletions that see it); S4 draws fresh random
  strings each run.
* The five lift sabotages: re-run through checkcert by me (5/5 rejected,
  correct diagnoses) AND re-created from scratch with my own lift and my
  own corruptions (5/5 rejected) — the checker, not the pipeline, is the
  gatekeeper, and it bites.
* The "independent whole-group canonicalizer validated on (3,6)" claim:
  reproduced twice over (their smoke test re-run: 23,808/4, rc=0; my own
  enumeration + union-find: 23,808 valid, 4 orbits).
* checkcert's own selftest re-run (4/4 behaviors) ✓; note checkcert's
  NON_REALIZABLE acceptance logic re-audited for soundness: odd-one-out +
  positive weights + exact cancellation ⇒ 0 > 0 in any realization —
  sound; acceptance genuinely proves non-realizability.

## 8. Prose audit (4 minor defects; everything else traced)

Beyond D-1..D-4: §0's "15,171" = 14,396 NR + 60 RESIDUE + 715 sampled
realizable ✓ (matches state file, `realizable_sample: 2000`, rmod
1,430,771); C1's "5,608 realizable rows" = 715 + 4,893 ✓ (and my recount
extends it: 877 ext-realizable rows also have zero NR minors); "185,139" =
136,539 + 48,600 ✓ (G1 pass lines in both logs); §4.3's "451 of 451" ✓;
"~9× more" = 451/51 ✓; §6's ≈194,700 / 17,000 traced to SCOPING §6.2
(63/3,000 sample) and 8.9% ✓; §7's BFP-shape rows (73.5/74/[41,96] vs
61.7/62/[27,96], weights 249,833 vs 106,676) match `report_sweep.json` —
note they are measured on 200-class subsamples per group, which the table
does not say (the uniform-corpus replication 75.6 vs 62.9 is full-group,
n=11) — nit; §5's "25/25" C2 and §10's C1–C5/G1–G3 tables match the
canary code and logs ✓; the §0 extend-test triple (row-identity,
byte-prefix, subset) re-verified byte-for-byte ✓; harvest reader honors
its complete-lines-only contract (code audited; `shard_root` offset 322
consistent). Generator/checker independence holds where it matters: every
verdict-bearing number rests on checkcert (stdlib, shares nothing with
the producers) or on the LP falsification test, not on the code that
produced it; the one genuinely shared component (coverage_checker as
canonicalizer for identification) is cross-checked by C4/bfcanon, by the
§6.1 LP test, and now by this review's independent per-element LPs.

## What this review did NOT verify

* Completeness of the (4,8)/(3,8)/(3,9) catalogs (2,628/135/4,382) and of
  the (4,9) catalog (9,276,595) — inherited from `ai/omgamma` (mass
  identity + published counts) and disclosed as such in §10. All
  fraction-type results are conditional only on the small-catalog side;
  the (4,9) count enters only percent-of-catalog and extrapolation
  figures.
* The sweep's own realizability verdicts beyond the harvested prefix
  (owned by `ai/omreal`; every harvested certificate was re-checked
  here).
* Depth values (`depth.npy`) were taken as read for §4.2's banding (the
  band SUMS were verified against the closure totals; the
  depth-independent uniform corpus separately confirms the ≈90% level).
* The 1,758-list exhaustively (sampled 10; the shipped full-list LP
  falsification was audited for logic and its artifacts checked).
