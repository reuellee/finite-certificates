# Adversarial review of ai/omopen (OPEN_ATTACK.md and artifacts)

Reviewer: Fable (max-effort adversarial pass), 2026-08-01/02.
Scope: the seven attack areas assigned; everything material re-derived and
re-run with reviewer-owned code in `review_scratch2/` (no imports from
omopen/omreal/omgamma on any verification path; the deliverable's own code
was executed only where the task was to re-run it).  ai/omreal and
ai/omminor were read but never written; all reviewer outputs live in this
file and `review_scratch2/`.

## Verdict summary

| # | area | verdict |
|---|---|---|
| 1 | Headline: all 126 OPEN classes realizable, with certificates | **CONFIRMED** (all 126 re-verified independently, not a sample) |
| 2 | Completion-LP completeness (weapon A) | **CONFIRMED** (proof sound; failure direction never verdict-bearing; 1134/1134 positive and 12/12 exact-negative empirical checks) |
| 3 | "Realized ⟹ no BFP" lemma and the 252 witnesses | **CONFIRMED** (lemma verified in exact integers on all 126 realizations over the full L1 support; all 252 witnesses re-checked against a third, reviewer-built inequality system) |
| 4 | BFP-vs-Gordan correction | **CONFIRMED** (re-derived; consistent with `bfp.py` and MINOR_THEORY; L0 support is bit-for-bit `bfp.py`'s) |
| 5 | Validation and canary integrity | **CONFIRMED**, with one minor code defect (D1) |
| 6 | Weapon B2 positive finding | **CONFIRMED** (2 shipped + 1 fresh fired certificate verified by reviewer expansion; second-opinion status verified), with provenance nits (D3, D4) |
| 7 | Prose audit, trust boundary, write hygiene | **CONFIRMED** overall; minor prose/provenance defects D2, D5–D8; trust chain independently re-verified end to end; no writes to omreal/omminor in or after the session window |

**The headline survives.** 126/126 OPEN classes of the 26.15% snapshot are
realizable, each certificate independently re-verified by this review; the
sharpened conjecture is unrefuted on the emptied candidate set; the
completion-LP completeness claim is mathematically correct as stated and is
never used in the direction that could have made it dangerous.  **No defect
found touches the soundness of any verdict.**  All defects are
documentation/provenance/convenience-level.

---

## Method

Reviewer-owned code (stdlib arithmetic; scipy used only as a *search* in
C2/F5, with every conclusion reconstructed in exact rationals):

| script | what it does |
|---|---|
| `review_scratch2/verify_headline.py` | H1–H7 below |
| `review_scratch2/verify_witness_lemma.py` | W1–W5 below |
| `review_scratch2/verify_completion.py` | C1–C2 below |
| `review_scratch2/verify_fp.py` | F1–F5 below |
| `review_scratch2/my_sabotages.py` | S1–S4 fresh sabotages |
| `review_scratch2/rerun_gates.py`, `rerun_canaries.py` | shipped gates re-run, outputs redirected to `review_scratch2/gates_data/` |

Independence measures: a **fourth** determinant algorithm (explicit 24-term
permutation expansion on Python ints — producer uses Laplace-by-2x2-minors,
fpcheck uses Bareiss, checkcert uses cofactor expansion); a hand-written
stdlib `.npy`/`.npz` parser; catalog keys decoded by hand from the MANIFEST
bit convention; `st.dat` read as raw bytes; identity families rebuilt from
the definitions and validated as exact identities on fresh random integer
configurations before use; constraint rows for the completion LP built
directly from the definition (column := unit vector, take det4), sharing no
cofactor conventions with `weaponA.completion_rows`.

---

## 1. Headline — all 126 OPEN classes realizable  [CONFIRMED]

What was tried, and what failure would have looked like: any certificate
whose recomputed chirotope differs from its `chi` (fake realization); any
chi that does not match the catalog row it is attributed to (misattribution);
any snapshot row not actually OPEN in the sweep (fabricated residue); any
checker rejection.

Observed (`verify_headline.py`, all PASS):

* **H1** — all **126/126** matrices are 4x9 integer matrices whose 126
  exact determinant signs (reviewer's own algorithm) equal the stated `chi`.
  (Task asked for ≥15 sampled; all 126 were done.)
* **H2** — the 126 certificate chis are distinct and equal, as a set, to
  the 126 chis of `data/open_set.txt`; `results.jsonl` maps row↔chi↔verdict
  consistently for all 126.
* **H3** — `coverage_4_9.npz` parsed with a hand-written stdlib reader; the
  SHA-256 of each raw array (`key_hi`, `key_lo`, `stab`) matches
  `MANIFEST.json.array_sha256`; the 126 rows' keys decoded by hand
  (bit `M-1-j` of `(hi<<64)|lo`, per the MANIFEST convention) reproduce the
  snapshot/certificate chis **126/126**.  This is the reviewer's own
  class lookup, not omopen's.
* **H4** — the sweep's working copies `sweep_state/hi.npy`, `lo.npy` agree
  with the npz at all 126 rows.
* **H5** — `st.dat` (raw bytes) says OPEN(=4) at all 126 rows.  Reading
  `sweep49.py`: the sweep only ever writes a status to a TODO row
  (`wave[st[wave]==TODO]`), so OPEN is terminal — the current OPEN status
  certifies the rows were OPEN at snapshot time and that the sweep never
  decided them itself.  Cross-check of the reimplemented enumeration
  against `sweep49.py`: status codes agree (TODO..OPEN = 0..4), the row
  set is `st==OPEN`, and the chi source is the same key arrays (H4).  The
  one difference: `report --enumerate-open` writes `stab` in column 2,
  `attack.py enumerate` writes `depth` — immaterial, and consistent with
  how OPEN_ATTACK.md uses the column.  As further corroboration, the
  sweep's own shard files contain `RESIDUE` records with matching row
  number *and* chi for sampled OPEN rows (3/3 checked).
* At review time the live sweep stood at 27.25% done with 134 OPEN rows —
  strictly ahead of the snapshot (2,426,068 done / 126 OPEN), 8 new OPEN
  rows since; nothing contradicts the snapshot, and the OPEN rate is
  holding near the documented 0.005%.
* **H6** — snapshot depths match `depth.npy`; the depth histogram is
  exactly the documented {13:1, 14:4, 15:32, 16:54, 17:35}.
* **H7** — Appendix B was parsed out of OPEN_ATTACK.md and checked cell by
  cell against `results.jsonl` + `open_set.txt` + the certificates: all
  126 rows match on depth, source, seconds, and max|entry| (0 mismatches).
  Aggregates match: sources walk 103 / store_walk 14 / store 5 / fresh 4 /
  control 0; median 3.41 s; max 45.26 s; total 933.7 s; 47,723 infeasible
  LPs with per-class max 2,938; largest entry 262,144 with exactly 8 certs
  above 16,384; 13 first-pass STILL_OPEN records burned 674 s (doc: ~670).
* Both shipped checkers re-run on everything: `fpcheck.py --trials=16`
  accepts 126 REALIZABLE + 252 GORDAN_WITNESS; `../omreal/checkcert.py`
  accepts 126 REALIZABLE — output text identical to the transcript quoted
  in OPEN_ATTACK.md §8.

Dependency honestly declared and out of scope here: that the 9,276,595
catalog rows are pairwise non-isomorphic orbits is omgamma's certificate;
the deliverable's §9 states this dependence correctly (the certificates are
statements about the carried sign vectors regardless).

## 2. Completion-LP completeness  [CONFIRMED]

(a) *Strict vs closed.*  The chirotope constraints are `A x > 0` (strict,
homogeneous, integer rows).  The shipped LP maximises t subject to
`(A/|a_i|) x ≥ t, |x|∞ ≤ cap, t ≤ 1`.  The strict-to-closed gap closes
exactly: if some x has `A x > 0`, homogeneity scales it into the box with
margin t > 0, so the exact optimum is positive; conversely optimum t* > 0
exhibits a strict solution.  So "optimum ≤ 0 ⟹ no completion of THIS Y"
is a theorem *for the exact LP*.  Margin exactly 0 is correctly *not* a
completion: a boundary point has a vanishing bracket, excluded by
uniformity.  Row degeneracy cannot occur on a genuine deletion realization
(any 3 columns of a uniform rank-4 configuration are independent), and the
code guards the zero-norm case anyway.

(b) *Projective/sign handling.*  The cone fixes the sign of x_p; the box
covers both orientations; homogeneity handles scale.  No completion can
hide at margin 0 (see above).

(c) *Rational vs real.*  The cone is open with integer data: nonempty over
R ⟹ contains rational points ⟹ scales to integer points.  That is the
property the rounding loop relies on; the code's exact integer re-check
(`A y > 0`, then all 126 brackets) means float error can only *lose* a
completion, never mint a false one.

(d) *The asymmetry.*  Read closely in `attack.py`/`weaponA.py`:
`NON_REALIZABLE` is only ever written from MONOCHROME / GORDAN / FP
certificates; weapon-A failure produces `STILL_OPEN` ("no BFP (certified),
no realization found") and §10 explicitly forbids reading failure as
non-realizability.  The LP's failure direction is used only as a heuristic
(hill-climb objective, blocker extraction).  The prose scopes the
completeness claim to "this Y" wherever it states it.  §11(4)'s
recommendation is hedged ("very likely") and correctly grounded: the LP is
complete per (Y, p), not per class.

Empirical (`verify_completion.py`, reviewer-built rows):

* **C1** — for every certificate Z and every p (126 x 9 = **1,134**
  instances) the deletion must complete, and did: LP margin > 0, reviewer's
  own integer rounding produced an exact completion whose full chirotope
  (reviewer determinants) equals chi, **1134/1134**.  This also validates
  the constraint-row construction end to end.
* **C2** — manufactured infeasible instances (Y from cert i, sign demands
  from cert j): 12/12 float-infeasible verdicts were **proven** correct by
  exact rational Farkas certificates (w ≥ 0, wᵀA = 0 over Fractions) — the
  float "no" is a real "no" on every instance tested.

Caveat worth stating (not a defect): the *implemented* LP is float HiGHS,
so "definitively" is a property of the exact LP it approximates; on the
success side exactness is restored by rounding + integer re-check, and on
the failure side nothing verdict-bearing is derived.  The claim as used is
sound.

## 3. "Realized ⟹ no BFP" lemma and the witnesses  [CONFIRMED]

The lemma's proof is the standard one and is stated correctly: substituting
y_B = χ(B)[B] > 0 into an identity with a unique odd-sign term makes the
odd term equal to the sum of the ≥ 2 others, hence strictly greater than
each; with u = log y every forced inequality v·u > 0 holds; a Gordan vector
w would give 0 = Σ w_i (v_i·u) > 0.  (The coexistence-impossible direction
does not even need Gordan's theorem; only the "witness exists" half of the
dichotomy does.)

Verified exactly, without logs (`verify_witness_lemma.py`):

* **W2** — for every one of the 126 certificate matrices and every forced
  inequality over the **full L1 support**, the integer inequality
  `|det P||det Q| > |det S||det T|` holds — 0 failures.  This simultaneously
  confirms the lemma on real data and the big/small orientation of the
  entire inequality machinery (a swapped orientation could not survive
  against actual bracket magnitudes).
* **W3** — all 5,544 identities evaluate to exactly 0 on every certificate
  matrix.
* **W1** — all **252** shipped witnesses satisfy every inequality of a
  third, reviewer-built system (exact integers): 0 failures; no monochrome
  relation on any of the 126 classes (W1b).
* **W4** — L0 row count is exactly 2,520 for every class, as it must be.

The witnesses are consistent with the lemma and are, as §0 says, a
cross-check rather than an independent finding; the three stated reasons
they still matter (counterexample hypothesis, cross-implementation check,
false-OPEN exclusion) are each logically sound — in particular the third:
a verified witness proves `bfp.py`'s `None` was a true negative, since no
Gordan vector exists to have been missed.

## 4. BFP-vs-Gordan correction  [CONFIRMED]

Re-derivation.  A degree-2 coefficient-space final polynomial over a
relation set is Σ_j λ_j R_j with one-signed monomial coefficients — a
statement about *monomials* cancelling.  A BFP/Gordan vector is a
cancellation of *exponent vectors* in Z^126 ({y1y2, y3y4} vs {y1y3, y2y4}:
same exponent sum, different monomials — the builder's example is right).
Over the three-term relations the degree-2 rung is empty for *every*
chirotope: an unordered bracket pair {B, B'} with |B∩B'| = 2 determines its
relation (L = B∩B', abcd = B△B') and its term, so the monomial-relation
incidence has exactly one relation per monomial; `Aλ ≤ 0` then forces
λ_j s_jk ≤ 0 for all three k, and since a valid chirotope never has all
three s_jk equal, λ = 0.  Reviewer measured the premise directly (W5):
3,780 distinct monomials over the 1,260 relations, none shared — matching
`fp_probe.json`'s `one_per_row: true`.  Since BFPs demonstrably exist for
30,513 sweep classes while the degree-2 rung is empty for all chirotopes,
**BFP is not the degree-2 case of this hierarchy** — the correction stands.
Converting a Gordan vector to a polynomial identity via
Π(y_P y_Q)^{w_i} = Π(y_S y_T + y_U y_V)^{w_i} costs degree 2Σw (the classic
Bokowski–Richter-Gebert route from a solvable biquadratic system to a bona
fide final polynomial), and MINOR_THEORY §7's measured Σw ≈ 10^5
(means 249,833 / 106,676 — quoted correctly in §5.2) puts that far beyond
degree 3.  Shipped-artifact consistency: `bfp.py` and `checkcert.py` define
"BFP" as a Gordan vector over the three-term support; `gordan.py`'s L0 was
verified **bit-for-bit identical** to `bfp.py`'s table (relation list,
order, term order, signs; derived inequality rows equal on an OPEN class),
so "no BFP" in this directory means exactly what the rest of the project
means by it.  MINOR_THEORY's Proposition R and the sharpened conjecture are
quoted accurately (451/451 measured; conjecture text matches
WALK_THEORY §7 + MINOR_THEORY §4.3).  Nothing in the shipped artifacts
contradicts the correction.

## 5. Validation and canary integrity  [CONFIRMED, defect D1]

* Re-ran `validate.py` (n=40, budget=120, outputs redirected).  The sweep
  has advanced, so the pools are a **fresh draw** — and every gate passed
  again: A1 40/40 (median 0.23 s), A2 40/40, B1 40/40, **B2 0 false
  positives on 80 at both levels** (the fatal soundness gate), B3 80/80 and
  0/40 at both levels, both checkers rc=0.  `data/validation.json` matches
  §7.1's table for the recorded run.
* Re-ran `canaries.py` (redirected): **7 controls accepted, 23 sabotages
  rejected with the expected diagnosis, 0 failures** — replicating the
  claim on a fresh draw.  The shipped `canaries_result.json` shows the same
  30 outcomes with corruption-naming diagnoses.
* The two redesigned canaries: the documentation is honest — the code
  contains the matching NOTE blocks, and C21 explicitly screens for a
  non-monochrome substitute exactly as §7.2 recounts.  The redesigns are
  probative (both rejected with named diagnoses).  The underlying claim
  that "one entry off by one is not a sabotage" was **independently
  confirmed**: in reviewer test S1, deltas of 1 and 2 on a certificate
  entry flipped no bracket (the perturbed matrix still realizes the class);
  delta 4 was needed to corrupt.
* Three fresh reviewer sabotages (plus a bonus), all first *proven*
  corrupting with reviewer code, then fed to **both** shipped checkers:
  S1 corrupted matrix entry, S2 chi relabelled by a 9-cycle with the matrix
  untouched, S3 two certificates' payloads swapped, S4 witness u rotated.
  fpcheck rejected 4/4 and checkcert 3/3 (S4 is not in its schema), each
  with a diagnosis naming the failure; the uncorrupted controls were
  accepted.
* All shipped selftests pass: `fpcheck.py --selftest`,
  `checkcert.py --selftest`, `python gplib.py` (including the
  flipped-epsilon sabotage catch).

## 6. Weapon B2  [CONFIRMED, nits D3–D4]

* **F1** — both shipped fired certificates (`fp_found.jsonl`, rows 337599
  and 362889) re-expanded with reviewer code from the relation specs alone:
  valid final polynomials (8 monomials, one sign).  The §5.3 example is the
  shipped row 337599 record, generator for generator.
* **F3/F4** — both rows are `NONREAL(3)` in `st.dat`, their chis match the
  reviewer's catalog decode, and the sweep's own NON_REALIZABLE shard
  certificates for both chis were located and accepted by `checkcert.py` —
  so the B2 hits are exactly the "second, independent refutations" the doc
  claims, and no FP certificate anywhere asserts a new non-realizability
  verdict (the only NON_REALIZABLE-shaped records shipped are validation
  and probe artifacts on sweep-certified classes, plus the clearly-labeled
  rigged positive control, whose sign vector is not a chirotope at all;
  `attack.py` never created `certs_nonrealizable*.jsonl`, confirmed
  absent).
* **F5** — fresh out-of-sample fire: 30 sweep-certified NONREAL classes
  (chi decoded by reviewer from st.dat + npz) through `fpoly.find_fp` at
  degree 2 / L1 produced 1 hit, and that fresh certificate re-verified
  under reviewer expansion — 3 fired certificates checked in total, as the
  task required.  1/30 is at the low end of "roughly one in ten" but
  consistent for small samples (doc itself reports 3/25 then 2/25 and warns
  the rate is approximate).
* The positive control re-verified under reviewer expansion (F2), and the
  degree-2-over-gp3 infeasibility proof was re-derived with its premise
  measured (area 4).  LP-size claims match `fp_probe.json`
  (1,260x3,780; 5,544x6,615 — 21,420 nonzeros = 1260·3+3780·4+504·5;
  158,760 = 1,260·126 columns at degree 3; ~6.5 s each).

## 7. Prose audit, trust boundary, hygiene  [CONFIRMED, defects D2, D5–D8]

Numbers audited against artifacts: §0 table (126/126/0/0, both checkers,
median/max/total times); §1 (0.0052%, ~480 projection — recomputed: 481.8);
§8 (snapshot counts = `enumerate_final.txt`, 2,393,416+2,013+30,513+126 =
2,426,068 = 26.15%; pass staging = run1/run2/run3 logs: 107→94+13, 13/13,
11/11, 8; source table; entry sizes; the two quoted checker transcripts
byte-typical); §11 (residue arithmetic).  Appendix B fully verified (H7).
All match.

Trust boundary (§9): the five-link chain was re-executed by the reviewer
(npz hashes vs MANIFEST; chi vs npz decode 126/126; certificate
count/distinctness/set-equality; snapshot vs attacked rows; still-OPEN in
the live sweep) — all hold.  The section is honest about what depends on
the catalog: if the sweep/catalog mislabelled a row, the certificates
remain true statements about the carried sign vectors; if the sweep had
wrongly marked OPEN a class that actually has a BFP, stage 0's independent
L0 Gordan search would have flagged a DISAGREEMENT (it fired on 0/126, and
the witnesses *prove* no BFP exists, closing that hole outright).  The
declared unconditional core — integer matrices checked by two independent
checkers (now three, counting this review) — is accurate.

Write hygiene: no file under `ai/omreal` or `ai/omminor` (including
`__pycache__`) has an mtime inside or after the omopen session window
(19:47–21:11); the `.cpython-311.pyc` files there predate it (17:01–18:56,
from earlier omminor-session activity).  The claim of §2.3 is confirmed —
in the observed window not even certificate shards were flushed.

### Defects

* **D1 (minor, code).** `python attack.py canaries` crashes:
  `weaponA`'s import calls `catalog.realize_mod()`, which puts `ai/omreal`
  at `sys.path[0]`; `__import__('canaries')` then resolves to
  `ai/omreal/canaries.py`, which has `main()` but no `run(a)` →
  AttributeError.  Reproduced by this review.  The documented runbook
  (§10) uses `python canaries.py`, which works, but `attack.py`'s own
  docstring advertises the broken subcommand.  Fix: import by explicit
  path or insert OMREAL at the *end* of sys.path.
* **D2 (minor, prose).** §3.2's illustrative measurements do not match the
  shipped artifacts: "row 586623 survived 2,004 completion LPs" (artifact:
  1,920 in pass 1), "fell in 4.3 s" (artifact: 4.6), "row 1213079 in
  19.2 s" (artifact: 11.7), "row 1200032 in 0.4 s" (artifact: 8.7).  The
  qualitative claim — the margin hill-climb cleared all 13 first-pass
  survivors quickly — is fully supported by run2.log; the specific numbers
  appear to come from an unshipped development measurement.
* **D3 (minor, provenance).** `data/fp_found.jsonl` carries
  `also_has_L0_gordan_vector` / `L0_gordan_terms` fields the shipped
  `fpprobe.py` does not produce (enriched out-of-band), and the file is
  from a later 2-hit draw while `fp_probe.json` records the 3-hit run —
  the prose discloses the two-draw story but the two artifacts are not
  from one run, and the shipped generator cannot reproduce the artifact's
  schema byte for byte.
* **D4 (nit, artifact).** `fp_positive_control.jsonl` says `"level": "L0"`
  while its generator is a five-term (L1-family) relation —
  `fpoly.positive_control` forwards `sup` but not `level` to `find_fp`.
  The checker rebuilds from the spec and ignores the label; cosmetic.
* **D5 (nit, prose).** §7.1a's generator-vs-checker system comparison
  ("identical sets, 6/6 classes"; rows 8,172–8,644; distinct 7,082–7,476)
  has no shipped artifact or script.  This review confirmed the substance
  with a third implementation on **all 126** classes (L0 = 2,520 exactly;
  L1 rows in [7,896, 8,644], distinct in [6,813, 7,476] — the doc's
  6-class ranges sit inside these).
* **D6 (nit, prose).** §7.1/§10 present the gates as `validate.py --n 40`;
  the recorded run used `--budget 120` (validation.json), not the default
  60.
* **D7 (nit, provenance).** Pass-1 rows of `results.jsonl` were produced by
  an earlier `attack.py` revision (their records lack the `L0_witness`/L1
  stages the shipped `decide()` always emits; witnesses were backfilled by
  `attack.py witness`, visible at the end of run3.log).  Legitimate under
  the append-only design, but shipped code + logs are not a byte-level
  replay of the shipped results file.
* **D8 (nit, prose).** §7.2 says a sabotage passes "only if the rejection
  names the corruption"; two sabotages (C4, C17) are coded with
  `expect=None`, i.e. any rejection counts.  Their actual diagnoses do
  name it.

None of D1–D8 weakens any mathematical claim.

---

## Bottom line

* **126/126 realizable: stands.**  Re-verified certificate by certificate
  with a fourth determinant implementation, against a reviewer-decoded,
  hash-verified catalog, against the live sweep's own state and its own
  RESIDUE records.
* **Conjecture unrefuted: stands**, and the supporting structure is
  exactly as claimed: no Gordan vector at L0 or L1 on any OPEN class
  (0/139 records, reviewer-confirmed dichotomy via 252 exact witnesses),
  no monochrome relation, no final polynomial, and every candidate
  eliminated by an explicit realization.
* **Completion-LP completeness: stands** as a statement about the exact LP
  per (Y, p); the implementation uses it only on the safe side, and both
  directions were exercised with exact arithmetic by this review
  (1,134/1,134 completions; 12/12 rational Farkas emptiness proofs).
