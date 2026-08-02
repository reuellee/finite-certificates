# Adversarial review of FINAL_RESIDUE.md's verification claims

Written 2026-08-03 by an independent reviewer. Companion to
`ai/omreal/REVIEW_SWEEP_TOOLING.md` (Part A, the sweep tooling); this
document is Part B — trying to break `FINAL_RESIDUE.md`'s own verification
claims (`fastverify.py`, `certaudit.py`, `checkcert.py`, `fpcheck.py`,
`reverify.py`, `backfill.py`, `bfp2gordan.py`, `canaries.py`) the same way
every other deliverable in this project gets adversarially reviewed.

Nothing in `ai/omreal`, `ai/omopen/data`, or any existing `.py` file was
modified by this review (two tracked JSON/JSONL files were touched by
re-running `canaries.py` as a confirmation check and then restored with
`git checkout` — see §6). All new code is under `ai/omopen/review_scratch4/`
and `ai/omreal/review_scratch/` (shared codec library).

**Bottom line: every numeric claim in `FINAL_RESIDUE.md`'s §0/§6 was
independently re-derived from the raw shards and `st.dat`, using code that
imports nothing from this project, and matched exactly. Every sampled
certificate — 2,500 REALIZABLE (fresh Leibniz-expansion determinant),
5,400 NON_REALIZABLE (a third, independent Gordan checker with the "BIG"
term re-derived from the chirotope, not trusted from the record), and all
141 backfilled rows (checked directly against `Z.dat`, bypassing every
existing certificate file) — was accepted, 0 rejections. A 28-check
sabotage battery targeting real corruption failure modes was rejected
100% of the time by every real checker. One genuine methodology gap was
found and demonstrated (certaudit.py's byte-offset line parser can be
fooled by a corrupted payload with an intact `chi` field) — it is real,
it is worth fixing, and it did not affect the reported numbers, because
`fastverify.py`'s unconditional `json.loads` over the same files would
have crashed on any malformed line and did not, which this review's own
full-corpus scan (Part A, §4) independently confirms with 0 parse
failures over all 9,276,454 lines.**

---

## 0. What was actually re-derived, in one table

| FINAL_RESIDUE.md claim | this review's independent re-derivation | match |
|---|---|---|
| 9,072,015 REALIZABLE + 203,780 NON_REALIZABLE + 659 RESIDUE = 9,276,454 shard records | full fresh `json.loads` scan of all 10 shard files, 0 parse failures | **exact** |
| certaudit: 9,276,454 matched, 0 unmatched, 0 duplicated, 141 missing (all `REALIZABLE(walk)`) | independent reconciliation, own parser + own key encoder + dict/array matching, not `certaudit.py`'s code | **exact** |
| st.dat: WALK 9,060,883 + REPAIR 11,273 + NONREAL 203,780 + OPEN 659 + TODO 0 | `st.dat` read directly for the first time in this review (everything else came from the shards) | **exact** |
| 659 OPEN rows (`st.dat`) = 659 RESIDUE certificates | set equality checked directly: `flatnonzero(st==OPEN)` vs. the `row` field of every RESIDUE record | **exact bijection**, plus each RESIDUE record's own `chi` independently re-checked against `catalog[row]` — 0/659 mismatches |
| 141 backfilled rows, all verify | re-checked directly against `Z.dat` + `hi.npy`/`lo.npy`, bypassing `certs_backfill.jsonl`'s own fields and `omdecode`/`realize.py` entirely | **141/141** |
| fastverify: 9,072,015 REALIZABLE accepted, 0 rejected | 2,500-record random sample, fresh Leibniz-permutation-expansion determinant | **0 rejected** |
| checkcert.py + fpcheck.py: 203,780/203,780 accepted | 5,400-record sample (the reviewer's entire reservoir), third independent Gordan checker, BIG term re-derived from chi (not trusted) | **0 rejected**, 362,176 inequality terms rebuilt |
| canaries.py: 7 controls / 23 sabotages, 0 failures | re-run live today against today's `sweep_state` | **reproduced**: 7/23/0 |

---

## 1. Sample-based re-verification of REALIZABLE certificates (task B.1)

`ai/omopen/review_scratch4/verify_realizable.py`, checker: `mycodec.py`
(this review's own — `ai/omreal/review_scratch/mycodec.py`), determinant by
**full Leibniz permutation expansion** (sum over all 24 permutations of
`{0,1,2,3}`, exact Python integers) — deliberately unrelated in algorithm
to `realize.py`'s / `fastverify.py`'s Laplace-by-2×2-minors, `checkcert.py`'s
cofactor recursion, `fpcheck.py`'s Bareiss elimination, and `reverify.py`'s
Fraction Gauss-Jordan.

Sample: 2,500 records drawn uniformly (Python `random.sample`, seeded) from
a 22,501-record reservoir that was itself collected by a **full, unbiased
reservoir sample across all 10 shard files** during the Part A parse scan
(not a prefix, not one shard).

```
[B1] RESULT over 2500 sampled REALIZABLE certificates (15.2 s, 6.08 ms/record):
   all 126 brackets nonzero & sign-correct : 2500
   vanishing bracket (non-uniform!)          : 0
   sign mismatch (WRONG CERTIFICATE!)         : 0
   malformed shape                            : 0
   largest |matrix entry| encountered          : 4096

[B1] ALL ACCEPTED BY THE FRESH CHECKER
```

**No mismatch found. Grade: CONFIRMED.**

---

## 2. Independent re-derivation of certaudit.py's reconciliation (task B.2)

`ai/omopen/review_scratch4/my_certaudit.py`. Does not import `certaudit.py`.
Reads `hi.npy`/`lo.npy`/`st.dat` as raw arrays; parses every shard line with
`json.loads` (not `certaudit.py`'s `line.index(b'"chi": "')` byte-offset
heuristic — see §5 for why that distinction matters); encodes each
certificate's `chi` string to a `(hi,lo)` key with the reviewer's own
validated formula; matches against a freshly sorted view of the catalog via
`numpy.searchsorted` (a different join implementation is not really
available as a "more independent" choice here — sort-join and hash-join are
both generic algorithms, not project logic — so the actual independence is
in the parsing and the encode formula, both fresh).

```
[B2] catalog keys sorted; duplicate keys IN THE CATALOG ITSELF: 0
[B2] parsed 9276454 certificate records (parse failures: 0)  (113.5 s)
[B2] certificates: 9276454;  matched to a catalog row: 9276454;  unmatched: 0
[B2] rows with >=1 certificate: 9276454;  rows with >1 (DUPLICATED): 0;  rows with 0 (MISSING): 141
[B2] missing rows by sweep status: {'TODO': 0, 'REALIZABLE(walk)': 141, 'REALIZABLE(repair)': 0, 'NON_REALIZABLE': 0, 'OPEN': 0}
```

This reproduces `certaudit.py`'s own headline numbers **exactly**, from
completely independent code. A row-index clustering follow-up on the 141
(`cluster141.py`) is reported in Part A §3.3, where it becomes the
diagnostic that pins the loss mechanism down to specific restart events.

**Beyond what certaudit.py itself claims:** this review additionally
checked the join `FINAL_RESIDUE.md`'s arithmetic depends on but that no
existing script explicitly verifies — that the 659 RESIDUE certificates and
`st.dat`'s 659 OPEN rows are the *same set*, not just the same *count*
(`verify_residue_open.py`):

```
=== st.dat status histogram, read directly (never done yet in this review) ===
   TODO                         0
   REALIZABLE(walk)       9060883
   REALIZABLE(repair)       11273
   NON_REALIZABLE          203780
   OPEN                       659
   SUM                    9276595   (matches NROWS: True)

(a) RESIDUE.row set == st.dat OPEN set ?
    rows claimed RESIDUE but st.dat says something else: 0
    rows st.dat marks OPEN but no RESIDUE record claims:  0
    EXACT SET MATCH: True

(b) each RESIDUE record's chi vs catalog[row], reviewer's own codec:
    mismatches: 0 / 659

(c) duplicate row values among RESIDUE records: False (659 records, 659 distinct)

ALL RESIDUE<->OPEN CHECKS PASS -- the four-population partition is a
verified bijection, not arithmetic
```

One process note, in the interest of full disclosure: this review's first
pass at this check compared the independently-read `st.dat` WALK total
(9,060,883) against `FINAL_RESIDUE.md` §6's figure of 9,060,742 and flagged
a "mismatch." That was **this review's own bug**, not a defect in
`FINAL_RESIDUE.md`: §6's table is explicitly the *certificate-matched*
subset of WALK (excluding the 141 backfilled rows), a different, correctly
different, and correctly labeled number from §0's *total-`st.dat`* figure
of 9,060,883 (9,060,883 − 141 = 9,060,742, exactly). Once the correct
reference number was used the two independently-sourced totals (this
review's direct `st.dat` read, and `FINAL_RESIDUE.md`'s own arithmetic)
agree exactly. Recorded here because a reviewer's own false alarm and its
resolution is itself useful information about how carefully the two
numbers in the source document need to be read.

**Grade: CONFIRMED**, including the one join no existing script had made
explicit.

---

## 3. Third independent Gordan check of NON_REALIZABLE certificates (task B.3)

`ai/omopen/review_scratch4/verify_nonrealizable.py`. For each sampled
record, the three signed terms of every named three-term Grassmann–Plücker
relation are rebuilt **from the class's own `chi` string**, the forced BIG
term is **independently recomputed** (not read from the record and
trusted), checked to equal the record's claim, and the weighted
`v = e_big1+e_big2−e_small1−e_small2` combination is required to sum to
**exactly** the zero vector over all 126 coordinates with every weight
strictly positive — precisely Gordan's theorem, no determinant needed.

Sampled the reviewer's **entire** reservoir (5,400 records, reservoir-drawn
across all 10 shards during the Part A scan) rather than stopping at a few
hundred, since the check is cheap (~1 ms/record):

```
[B3] RESULT over 5400 sampled NON_REALIZABLE certificates (5.6 s, 1.04 ms/record,
362176 total inequality terms rebuilt):
   Gordan vector independently verified : 5400
   REJECTED                              : 0
```

**Extended to the 141 least-independently-covered records** (they never
went through the sweep's normal write path; their certificate was reissued
by `backfill.py` reading `Z.dat`) — checked **all 141, not a sample**,
completely bypassing `certs_backfill.jsonl`'s own `chi`/`matrix` fields:
read `Z[row]` directly from the raw memmap, decoded `row`'s chirotope
directly from `hi.npy`/`lo.npy` with the reviewer's own codec, and
recomputed all 126 brackets with the reviewer's own Leibniz determinant:

```
[B3-141] checked all 141 backfilled rows directly against Z.dat + hi.npy/lo.npy (0.8 s)
   fully independently verified : 141
   REJECTED                      : 0
```

Also cross-checked, at the file level, that `bfp2gordan.py`'s schema
conversion (the step that lets `fpcheck.py` see the sweep's raw `bfp`
records at all) drops nothing: `nr_X.jsonl` (raw) and `nrg_X.jsonl`
(converted) have **identical line counts for every one of the 6 shards**
(33964/33964, 33964/33964, 33963/33963 ×4 = 203,780 both ways, confirmed
by direct `wc -l`, not by trusting either tool's self-report), and
`checkcert_*.log`/`fpcheck_*.log`'s own "distinct classes" figures match
those line counts exactly (no silent intra-file drop either).

**Grade: CONFIRMED.**

---

## 4. Sabotage battery (task B.4)

`ai/omopen/review_scratch4/sabotages.py`. `ai/omopen/canaries.py` already
runs 22 sabotages (C1–C22 plus 13a/13b) directly against
`fpcheck.check_record`/`checkcert.check_record` on in-memory dicts, and
this review re-ran it live rather than trusting the stale log
(**7 controls / 23 sabotages / 0 failures — reproduced**, §6). This
review's own battery deliberately does **not** duplicate that ground; it
targets what `canaries.py` never touches: raw file-line parsing under
corruption, and the reconciliation logic (`certaudit.py`-style) that
`canaries.py` never exercises at all.

| # | sabotage | checkcert.py | fpcheck.py | fastverify.py (real `check_batch`/`check_big`) | mycodec (reviewer) |
|---|---|---|---|---|---|
| S1 | matrix entry corrupted by a large delta, confirmed to actually flip a bracket | reject | reject | reject | reject |
| S2 | two REALIZABLE certs' **payloads swapped** (A's matrix + B's chi, and vice versa) | reject ×2 | reject ×2 | reject ×2 | reject ×2 |
| S3 | one bracket sign flipped in `chi`, matrix unchanged | reject | reject | reject | reject |
| S4 | a BFP term's weight corrupted to **negative** | reject | reject (via `bfp2gordan`) | n/a | n/a |
| S7 | duplicate + delete a record in a synthetic reconciliation | — | — | — | duplicate and missing both correctly detected |

All 28 individual pass/fail sub-checks (S1–S4, S7) behaved exactly as
expected: **every real corruption was rejected by every checker meant to
catch it, 28/28.**

**S5/S6 are documented findings, not pass/fail results** — they
characterize `certaudit.py`'s parser rather than break a numeric claim; see
§5, where they belong together with the rest of the independence analysis.

---

## 5. certaudit.py's method: a real, precisely-scoped gap

`certaudit.py` does not call `json.loads`. Its per-line parse is:

```python
i = line.index(b'"chi": "') + 8
c = line[i:i + M]
a, b = key_of(c)
kind = 3 if b'"NON_REALIZABLE"' in line else (1 if b'"REALIZABLE"' in line else 4)
```

This locates the `chi` field by a fixed byte offset and substring-searches
for the verdict word; it never looks at `matrix` or `bfp` at all. Two
sabotages demonstrate the consequence directly:

- **S5**: a NON_REALIZABLE record with one BFP weight corrupted to `-999`
  (chi and the `"NON_REALIZABLE"` substring left byte-for-byte intact).
  `checkcert.py` and `fpcheck.py` both correctly reject it
  ("weight -999 is not positive"). `certaudit.py`'s `key_of` **extracts a
  valid key from it anyway** — a record like this would be counted
  "matched, valid" by `certaudit.py`'s reconciliation, because
  reconciliation was never designed to look past the `chi` field.
- **S6**: a JSON line truncated **after** the `chi` field (mid-`matrix`).
  `checkcert.py` and `fpcheck.py`'s `check_file` both raise
  `JSONDecodeError` **loudly** (no silent skip — confirmed: `check_file`
  calls `json.loads(line)` with no surrounding `try/except` anywhere in
  either file). `certaudit.py`-style byte parsing on the identical bytes
  **succeeds**, because the truncation happened after the 126-byte window
  it reads. (When the same line is truncated *before* the `chi` field
  starts, `certaudit.py`'s parser does correctly raise — `line.index`
  fails to find the substring at all. The gap is one-sided: corruption
  landing after the `chi` field is invisible to it; corruption landing
  before is not.)

**This is a real methodology weakness, precisely scoped, and it did not
affect any reported number.** Two independent facts close the gap:

1. `certaudit.py`'s own docstring is explicit that its job is counting and
   matching ("`st.dat` says how many rows the sweep DECIDED; the
   certificate shards say how many decisions it WROTE DOWN" — a coverage
   claim), not certificate validity — that job belongs to `checkcert.py`/
   `fpcheck.py`/`fastverify.py`, all of which parse with real `json.loads`
   and were shown in §4 to reject the exact same corruptions `certaudit.py`
   would miss.
2. `fastverify.py` calls bare `json.loads(line)` — **no try/except** — on
   every line of the same 10 shard files, split across 3 workers with no
   gaps (`ln % nworkers`, a complete partition), and all three workers
   completed without crashing (`data/fastverify/f00.json`, `f01.json`,
   `f02.json` all present, "0 bad"). Any malformed line **anywhere** in the
   corpus would have crashed a worker. It did not. This review's own
   independent full-corpus scan (Part A §4: 9,276,454 lines, `json.loads`,
   **0 parse failures**) confirms the same thing by a third method.

**Grade: certaudit.py's *result* (the reconciliation numbers) —
CONFIRMED** (§2, independently re-derived and matched exactly).
**certaudit.py's *method* (the byte-offset parser) — DEFECT, severity
LOW**: real, demonstrated empirically here (not just observed in code) by
S5/S6, and worth fixing (switch to `json.loads` with an explicit per-line
try/except that counts failures rather than a fixed-offset substring
scan) — but it did not bite in this run, for the two independent reasons
above. This is the same grade §7's summary table uses; the two are meant
to agree.

---

## 6. Generator/checker independence — the import graph, traced

Traced by grepping every `import`/`from` line in every file under
`ai/omopen` that is part of the verification story, then confirmed by
reading the modules that matter.

**Genuinely independent** (no import of any decoder/producer module,
confirmed by grep and by reading):

| checker | stdlib only? | own colex order | own determinant algorithm | own catalog decode |
|---|---|---|---|---|
| `ai/omreal/checkcert.py` | yes | yes | cofactor recursion | n/a (works from `chi` string only) |
| `ai/omopen/fpcheck.py` | yes (no numpy even) | yes | Bareiss (fraction-free) | n/a |
| `ai/omopen/reverify.py` | yes + `Fraction` (numpy only to read the raw `.npz` container bytes) | yes | Fraction Gauss-Jordan | yes, hand bit-shifted |
| this review's `mycodec.py` | yes | yes | full Leibniz permutation expansion | yes, hand bit-shifted |

**Independent with an openly-documented exception:** `fastverify.py`
explicitly routes `NON_REALIZABLE` records straight to
`checkcert.check_record` (dynamically loaded via `importlib`) —
`FINAL_RESIDUE.md` says so plainly ("it *is* `checkcert.py`, run again")
and the code confirms it; this is not a hidden dependency. Its
`REALIZABLE`-path determinant, though freshly coded with its own colex
table, is **algorithmically** the same two-row-Laplace-by-2×2-minors
formula as `realize.py`'s own `_det_int64` (both derive from the same
generalized-Laplace identity along rows {0,1}/{2,3}; this reviewer verified
the sign formula by hand against the standard Laplace expansion and both
implementations match it). **This is a precision point, not a defect**:
`fastverify.py`'s independence for the REALIZABLE side rests on (a) its own
selftest cross-validating against `checkcert.py`'s genuinely different
algorithm on real data (2,625 small-entry + 34 large-entry certificates,
reproduced live in this review — "AGREE" both times, §0 table), and (b) the
broader ensemble — `checkcert.py` (cofactor), `fpcheck.py` (Bareiss),
`reverify.py` (Fraction Gauss-Jordan), and now this review's Leibniz
expansion — not on `fastverify.py` alone. The 2,500-record fresh sample in
§1 covers this directly regardless.

**`verifyall.py` is explicitly not a second opinion**: it imports
`checkcert` directly and re-runs its logic in parallel over the shards.
`FINAL_RESIDUE.md` is honest about this ("a belt-and-braces cross-check
rather than a load-bearing one"); confirmed by reading the import.

**The one real shared dependency, and why it is closed:**
`ai/omreal/omdecode.py` wraps `ai/omgamma/coverage_checker.py` for all
catalog decoding, and `ai/omopen/catalog.py` (hence `backfill.py`,
`exactgate.py`, `neighbours.py`, `weaponA.py`, `attack.py`, `runshard.py` —
all producer/search-side infrastructure, not checkers) goes through the
same chain. If `coverage_checker.build_tables`/`decode_keys` had a
systematic bug, it would be invisible to any tool built on `catalog.py` or
`omdecode.py`, because they would all consistently "agree" with the wrong
answer. This is exactly the risk Part A §1.1 closes: **two** independent
reimplementations of the decode (`reverify.py`'s, and this review's
`mycodec.py`) were cross-checked against `coverage_checker`'s actual output
on tens of thousands of real rows, 0 mismatches. `fpcheck.py`/
`checkcert.py` sidestep the question entirely — they only ever compare a
record's own `chi` string against its own `matrix`/`bfp`, never touching
the catalog decode at all, so a bug there could not affect their verdicts
either (only §2's row-*matching* step depends on the decode/encode chain,
and that step is independently re-derived twice over, per Part A §1.1 and
this document's §2).

**`canaries.py` re-run live** (not merely trusted from its stale log):
imports `catalog`, `fpcheck`, `gordan`, `weaponA`, and `checkcert` — a mix
of producer-side code (needed to *construct* realistic certificates to
sabotage) and the two genuinely independent checkers (needed to *check*
them), which is the correct and only workable pattern for a canary suite.
Reproduced exactly:

```
7 controls accepted, 23 sabotages rejected with the expected diagnosis, 0 failures
```

(`data/canaries.jsonl` and `data/canaries_result.json` were regenerated by
this re-run — both are `git`-tracked from a previous session — and were
restored to their pre-review committed state with `git checkout` after the
result above was captured in `review_scratch4/canaries_rerun.log`, so this
review leaves no footprint on existing evidence files. The regenerated
content differed only in an embedded timestamp and in which specific
optimal LP vertex `scipy`'s HiGHS solver happened to return for the Gordan
witnesses — both irrelevant to the pass/fail outcome.)

**Footprint note.** `git status` at the end of this review shows several
tracked files marked modified beyond the two `.md` reports this review
adds: `ai/omminor/verify_minimal.py` and
`ai/omopen/data/{validation*.json,validation*.jsonl,certs_no_bfp.jsonl,
certs_realizable.jsonl,open_set.txt,results.jsonl}`. None of these were
touched by any command in this review (`verify_minimal.py` in particular
is never referenced anywhere in this review's work) — they were already
showing as modified in the very first `git status` this review ran, before
any script was executed, and belong to the final agent's own tonight's
session (updating validation artifacts from the 126-residue snapshot to
the 659-residue one). The only files this review changed on disk, net of
the `canaries.py` restore above, are the two new `REVIEW_*.md` documents
and the untracked `review_scratch/` / `review_scratch4/` directories.

**Grade: CONFIRMED**, with the `fastverify.py` algorithmic-overlap nuance
and the `certaudit.py` method gap stated precisely above rather than
smoothed over.

---

## 7. Verdict

| task item | grade | severity |
|---|---|---|
| B.1 REALIZABLE sample re-check, fresh determinant | **CONFIRMED** | — |
| B.2 certaudit reconciliation, independent re-derivation | **CONFIRMED** | — |
| B.2 (extended) RESIDUE↔OPEN bijection | **CONFIRMED** | — |
| B.3 NON_REALIZABLE sample re-check, 3rd Gordan implementation | **CONFIRMED** | — |
| B.3 (extended) all 141 backfilled rows, direct against `Z.dat` | **CONFIRMED** | — |
| B.4 sabotage battery (7 families, 28 sub-checks) | **CONFIRMED** | — |
| B.5 generator/checker independence — genuinely independent checkers | **CONFIRMED** | — |
| B.5 `fastverify.py` algorithmic overlap with the producer | documented nuance | informational, not a defect |
| B.5 `certaudit.py` byte-offset parsing | **DEFECT** (methodology) | LOW — real gap, demonstrated, did not affect any reported number (closed by `fastverify.py`'s unconditional `json.loads` over the same files, and by this review's own full-corpus scan) |

**No certificate — sampled, sabotaged, or drawn from the single
least-covered population (the 141) — was found to be wrong, misattributed,
or accepted by any checker that should have rejected it.** The whole-
catalogue split — **9,072,815 realizable / 203,780 non-realizable / 0
undecided** — is trustworthy as stated. The sharpened conjecture ("a
uniform rank-4 oriented matroid on 9 elements with no biquadratic final
polynomial is realizable") survived a population this review re-examined
from the raw shard bytes up, using code that shares nothing with the
project on either side of the check.

---

## Files

- `review_scratch4/verify_realizable.py`, `verify_realizable_result.json` — §1
- `review_scratch4/my_certaudit.py`, `my_certaudit.log`, `my_certaudit_result.json`,
  `cluster141.py`, `verify_residue_open.py`, `verify_residue_open_result.json` — §2
- `review_scratch4/verify_nonrealizable.py`, `verify_nonrealizable_result.json`,
  `verify_141_backfill.py`, `verify_141_backfill_result.json` — §3
- `review_scratch4/sabotages.py`, `sabotages_result.json`, `sab_tmp/` — §4, §5
- `review_scratch4/canaries_rerun.log` — §6 (canaries.py re-run; source files restored via `git checkout`)
- `ai/omreal/review_scratch/mycodec.py` — the shared independent codec/determinant/Gordan library both this document and the companion Part A review are built on
- Companion review: `ai/omreal/REVIEW_SWEEP_TOOLING.md` — Part A, the sweep tooling
