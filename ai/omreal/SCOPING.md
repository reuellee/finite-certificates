# OMREAL — scoping the realizability split of uniform rank-4 oriented matroids on 9 elements

Slow-lane program note. Started 2026-08-01. Status: **PILOT COMPLETE —
CONDITIONAL GO.** The (4,8), (3,9) and (3,8) splits are reproduced exactly
with machine-checkable certificates and zero residue; at (4,9) the pipeline
settles 99.63% of a random sample and leaves a measured residue it has no
method for. Predecessor standards apply: every claim carries a certificate
or an explicit trust boundary, and deliberately-broken controls (canaries)
are wired in.

**Read the verdict in §9 before the rest. It is not "we can fill in the
blank cell." It is "we can produce a certified partition of 99.6% plus an
explicit list of open cases, for about $315, and we do not yet have a
method for the last 0.37% (95% interval 0.21%–0.66%, i.e. 19 000–60 800
classes)."**

---

## 1. Status check: is the cell still open?

**Yes.** Fukuda, Miyata & Moriyama, *Complete Enumeration of Small
Realizable Oriented Matroids*, Discrete Comput. Geom. 49 (2013) 359–381
([arXiv:1204.0645](https://arxiv.org/abs/1204.0645),
[ar5iv full text](https://ar5iv.labs.arxiv.org/html/1204.0645),
[doi](https://doi.org/10.1007/s00454-012-9470-0)) print the cell we care
about — their Table 2, rank 4, n = 9, uniform sub-entry — literally as
`unknown (unknown)`. Nothing since has filled it.

Checked, as of 2026-08-01:

| Where we looked | Result |
|---|---|
| [*Oriented Matroids Today*, eljc Dynamic Survey DS4, v4 (Apr 2024)](https://www.combinatorics.org/files/Surveys/ds4/ds4v4-2024.pdf) — the live survey of record | credits FMM13 with rank 3 / n = 9 and rank 4 / n = 8 only; (4,9) never mentioned as closed |
| Semantic Scholar citation list of arXiv:1204.0645 (37 papers) | none closes it |
| arXiv abstract sweeps for "oriented matroids" + realizability, through Jul 2026 | nothing |
| [Finschi's Homepage of Oriented Matroids](https://finschi.com/math/om/) | catalogues the classes; carries **no realizability data at all**, and the (4,9) chirotopes are access-by-email, not downloadable |
| [Aichholzer order type database](https://www.ist.tugraz.at/staff/aichholzer/research/rp/triangulations/ordertypes/) | 2-D / rank 3 only — does not touch rank 4 |
| [Rote, NumPSLA (arXiv:2503.02336, 2025)](https://arxiv.org/abs/2503.02336) | rank 3 only |
| [Miyata & Padrol, neighborly polytopes (arXiv:1408.0688)](https://arxiv.org/abs/1408.0688) | neighborly OMs only; no OM(4,9) |
| FMM13 results page `www-imai.is.s.u-tokyo.ac.jp/~hmiyata/oriented_matroids/` | **could not verify it still resolves** (archive services blocked from this network). If alive it holds their (4,8)/(3,9)/(6,9) realizations and final polynomials — worth a mirror request before any full run |

Confidence the cell is open: high (~90%). Residual risk is a 2025–26
result that neither cites FMM13 nor surfaces in arXiv abstract search;
a 9.3M-instance classification would be a headline result and DS4's
maintainers would have picked it up.

### What IS known — do not reprove any of this

All numbers below are **reorientation classes** with the *uniform* count in
parentheses, FMM13's convention (their Def. 2.7: relabelling, allowing a
global sign flip, plus sign reversal on a subset). Finschi's site says
"isomorphism class" for the same equivalence — the naming trap; his
glossary defines it as "an arbitrary combination of relabeling and
reorientation". Both agree with the group `G' = S_n × {0,1}^n × {0,1}`
that `ai/omgamma` uses, so our catalogue counts the same objects.

| result | value | source |
|---|---|---|
| uniform (3, n≤8) realizable | all of them | Goodman & Pollack 1980; FMM13 Table 2 |
| uniform (3,9) | 4382 total, **4381 realizable / 1 non-realizable** (non-Pappus) | FMM13 Tables 1–2; Bokowski's 1991 table `4382:1` ([OEIS A006248 attachment](https://oeis.org/A006248/a006248.pdf)) |
| uniform (3,10) | 312 356 total, **312 114 / 242** | FMM13 Table 1 minus Table 2 |
| uniform (3,11) | 41 848 591 total, **41 693 377 / 155 214** | FMM13 Table 1 minus Table 2 |
| uniform (4,7) | 11 total, all realizable | FMM13 Tables 1–2 (206 (11) in both) |
| uniform (4,8) | 2628 total, **2604 / 24** | FMM13 Table 2; [Bokowski & Richter, *Classification of non-realizable OMs, Part I*, TH Darmstadt Preprint 1283 (1990)](http://science-to-touch.com/Articles/jrg/03_classification2.pdf) — `2628:24`, with all 24 representatives in their Appendix 2 |
| OM(4,8) all simple | 181 472 total, 177 504 / 3 968 | FMM13 Thm 1.1(a) — *this* was FMM13's new contribution at (4,8); the uniform split was already Bokowski–Richter 1990 |
| OM(3,9) all simple | 461 053 total, 460 779 / 274 | FMM13 Thm 1.1(b) |
| BFP completeness, empirically | a biquadratic final polynomial exists for **every** non-realizable class in OM(4,8), OM(3,9), OM(6,9), uniform (3,10) and uniform (3,11) | FMM13 §5 ("Surprisingly, the biquadratic final polynomial method … can detect all non-realizable oriented matroids in these classes"); DS4 §3.4 |
| smallest BFP-resistant example | OM(3,14) (Richter-Gebert Ω<sup>−</sup><sub>14</sub>); one on 12 points announced by Scheucher | FMM13 §5; DS4 |
| Mnëv universality | bites already at **rank 3** — there is no rank below which realizability is provably easy | DS4 §3.1 |

Two further facts that shape the design:

* **FMM13 did not run a non-realizability engine at all.** They realized
  everything they could and observed that the leftovers coincided exactly
  with the BFP hits of Bokowski–Richter 1990. So the historical evidence
  for "BFP is enough" is an *observation at small n*, not a theorem.
* **FMM13 give no CPU estimate and no hard-residue analysis for (4,9).**
  Their only statement is "Our classification almost reaches the limit of
  today's computational environments." Their (3,9) timing table is the
  warning that matters: of 461 053 instances, 58 took 10<sup>8</sup>–10<sup>9</sup> ms
  each — up to ~11 CPU-days apiece. The blank cell is *enumeration- and
  tail-limited*, not merely "nobody had the catalogue".

### One number to flag

FMM13 Table 1 gives the uniform (4,9) count as **9 276 601**; Finschi, and
`ai/omgamma`'s independently generated and mass-verified catalogue, give
**9 276 595**. The other cell where FMM13's rank-4 row disagrees with
Finschi is provably wrong (r=4, n=6 printed as 4; it is 1 by duality with
rank 2), and OEIS A063851 carries the editorial note "[Beware typos in
Table 1]". `ai/omgamma/OMGAMMA.md` resolves it in favour of 9 276 595 via
an exact mass identity. We use 9 276 595 throughout; the discrepancy does
not affect the open/closed verdict, but it should be stated in anything
published.

---

## 2. What we hold, and the trust boundary

`ai/omgamma/data/coverage_4_9/` is a certified catalogue of all
**9 276 595** isomorphism classes of uniform rank-4 chirotopes on 9
elements. `tree_4_9.npz` (10.4 MB, in git) is THE certificate; the legacy
`coverage_4_9.npz` holds `key_hi`/`key_lo`/`stab` directly and its three
raw arrays are pinned by SHA-256 in the same `MANIFEST.json`.

`ai/omreal/omdecode.py` **reuses only the decoder** from
`ai/omgamma/coverage_checker.py` — `build_tables`, `decode_keys`,
`encode_keys`, `gp_parities`, `gp_valid` — and nothing else from that
project. It sampled from the legacy array after verifying all three array
hashes against the manifest (replaying the tree costs hours and buys the
same provenance). omgamma carries **no realizability opinion** to inherit:
it is purely combinatorial (mutation-graph connectivity), so every verdict
here is new.

**No canonicalisation is involved anywhere in this pipeline.** Decoding a
key yields 126 signs in a fixed labelling 1..9; a certificate is checked
against exactly that sign string. This is what makes checking microsecond-
cheap and makes the sweep perfectly shardable — no worker needs to know
about any other class.

---

## 3. Pipeline design

Elements are 1..n, bases are the C(n,r) r-subsets in **colex** order, a
chirotope is ±1 per basis, and `chi[j]` is the sign of the j-th bracket.

### 3.1 REALIZABLE — an integer r × n matrix

`realize.py`. The observation the whole searcher rests on: brackets are
multilinear, so **with all columns but one fixed, the conditions on the
remaining column are homogeneous linear**. For each basis `B ∋ p`,

```
sigma_B * <v_{B\p}, x_p>  >  0,   v_S defined by det(x_{s1},..,x_{s_{r-1}}, y) = <v_S, y>
sigma_B = chi(B) * (-1)^(r-1-position of p in B)
```

so placing one point is "find a point in an open polyhedral cone" — 56
constraints in R⁴ at (4,9). Solved by a log-barrier Newton homotopy
(`cone_center`) that returns the cone's **analytic centre**, not a vertex:
a well-centred point keeps every bracket far from zero, which is what makes
the later rounding to rationals succeed with small denominators. It also
returns a best-effort point when the cone is empty, which is what turns the
repair sweep into a real descent instead of a no-op.

Four moves, in order of how much they cost:

1. **build** — place elements r+1..n one at a time, each an easy cone
   problem against the already-placed points.
2. **prefix backtracking** (`_repair_prefix`) — when element k will not go
   on top of the current sub-configuration, jitter the prefix and
   coordinate-descend it back to correctness. This picks *another point of
   the deletion's realization space*, which is the right fix; another
   random restart is not.
3. **repair sweep** — coordinate descent: re-place each point in turn
   against all C(n−1,r−1) of its constraints, with a kick when stalled.
4. **wall crossing** (`cone_push`) — *the move that mattered*. The search
   overwhelmingly stalls with **exactly one** bracket wrong: it has
   realized a *mutant* of the target. Crossing means driving that one
   bracket through zero while the other 125 hold, which is done by
   maximising `t·(a_j·x) + Σ_{i≠j} log(a_i·x) − (μ/2)|x|²` with t growing.
   Adding this took the (4,9) residue from **8.25% to 3.25%** at equal
   budget, and it is the single reason the target looks feasible at all.
5. **mutation warm-start** (`realize_via_mutant`) — the same idea run
   deliberately instead of opportunistically. A basis j is *mutable* when
   flipping `chi[j]` leaves a valid uniform chirotope; the mutant
   `mu_j(chi)` is then a neighbour of chi in the mutation graph. Realize
   the mutant **from scratch** and push the single wall at j. This samples
   the mutant's realization space at points a stuck direct search never
   visits, and it realized **17 of 27** classes that had already survived
   the entire A–D cascade including 60 tries × 120 sweeps, at 3.9 s each.
   Mutability is computed from chi alone, so the stage is stateless and
   shards like everything else.  Across three draws it converted 63-78%
   of the A-D residue.

Whatever comes out is scaled to integers and **verified exactly**: all
C(n,r) determinants over ℤ, every one nonzero (uniformity) and matching
chi. The search is a heuristic; the output is not.

Note a theorem that makes this direction complete in principle: for a
*uniform* chirotope the realization space is defined by strict
inequalities, hence **open**, so if it is nonempty it contains rational —
indeed integer — points. Irrationality can never block a certificate here.
(FMM13's irrational realizable examples — Perles in OM(3,9), Nakayama's two
in OM(4,8) — are all non-uniform, which is why we hit none of them.)

### 3.2 NON-REALIZABLE — a Gordan vector over three-term GP relations

`bfp.py`. Each three-term Grassmann–Plücker relation
`e1[Lab][Lcd] + e2[Lac][Lbd] + e3[Lad][Lbc] = 0` has three signed terms
summing to zero; validity forbids all three agreeing, so exactly one — the
BIG one — is opposite to the other two, giving `|big| = |t1| + |t2|` and
hence, strictly, `|big| > |other|` twice over. In logs `u_j = log|[B_j]|`
each is a linear inequality `v·u > 0` with `v = e_p + e_q − e_s − e_t ∈ ℤ^M`.
(4,9) has 1260 relations, so up to 2520 such rows in ℤ^126.

If some `w ≥ 0, w ≠ 0` has `Σ w_i v_i = 0`, no `u` can satisfy them all, so
no realization exists — Gordan's theorem, exactly the algebra `ai/maxout`
used. The LP (scipy/HiGHS) is only the *search*: the emitted `w` is
recomputed in exact rational arithmetic on the LP's support and shipped as
integers.

BFP is **provably incomplete** (Richter-Gebert's Ω<sup>−</sup><sub>14</sub>).
A class it misses is reported as RESIDUE, never as realizable.

### 3.3 The cascade

| stage | what | budget |
|---|---|---|
| A | cheap realization | tries 2, sweeps 15, rerolls 3, wall budget 3 |
| B | biquadratic final polynomial | — |
| C | medium realization | tries 8, sweeps 40, rerolls 8, wall budget 12 |
| D | heavy realization | tries 60, sweeps 120, rerolls 10, wall budget 90 |
| E | mutation warm-start | up to 20 mutable bases × 3 attempts |
| — | otherwise | RESIDUE |

B is interposed before C and D because it is cheap and settles a class
outright; there is no point paying for a heavy realization search on a
class that has a final polynomial. E is last because it is only ever
reached by ~1% of classes — but it is *cheaper per class than D* and
converts most of what D leaves, so on a rerun it should be promoted
ahead of D.

### 3.4 The checker — `checkcert.py`

Standard library only. Imports **nothing** from this project and nothing
from omgamma: it rederives the colex order, the GP relations and the
determinant signs from their definitions, and uses a **different
determinant algorithm** from the producer (plain cofactor expansion on
Python ints vs. Laplace expansion by complementary 2×2 minors in int64).

* REALIZABLE — recompute all C(n,r) brackets exactly; each must be nonzero
  and match the class's sign string position by position.
* NON_REALIZABLE — for every listed inequality, recompute the three signed
  term-signs *from the class's own sign string*, demand that the named BIG
  term really is the odd one out, rebuild `v ∈ ℤ^M`, and require
  `Σ w_i v_i = 0` with every `w_i > 0` and at least one term.
* RESIDUE — carries no claim; counted, never accepted as a verdict.

Measured: **~1–2 ms per certificate**; 7145 certificates (the three
reproduction catalogues) re-verified in 8.7 s, and all ~8900 certificates
produced in this pilot — reproduction catalogues plus every (4,9) sample —
accepted in 18.8 s.

### 3.5 Why the two directions cannot silently disagree

A realization and a Gordan vector for the same class are contradictory, so
a systematic error would show up as a class where both succeed. Two
standing cross-checks, run inside the sweep, hunt for exactly that:

* every realizable class (up to a cap) is *also* fed to the BFP search —
  0 spurious certificates in 500 (4,8) + 500 (3,9) + several hundred (4,9)
  classes;
* every BFP-certified class is *also* fed to the heavy realizer —
  0 realized, including all 24 non-realizable (4,8) classes.

The colex convention is also cross-checked implicitly and continuously:
this module builds its basis order independently of `coverage_checker`,
and a mismatch would make every produced matrix fail exact verification
against the catalogue's sign string. It never did, ~8900 times.

---

## 4. Reproduction of the published splits — the correctness gate

Command: `python pilot.py --cat <r> <n> --out certs_<r>_<n>.jsonl`

| case | classes | our REALIZABLE | our NON-REALIZABLE | residue | published | match |
|---|---|---|---|---|---|---|
| uniform (3,8) | 135 | **135** | **0** | 0 | 135 / 0 | ✔ |
| uniform (3,9) | 4382 | **4381** | **1** | 0 | 4381 / 1 | ✔ |
| uniform (4,8) | 2628 | **2604** | **24** | 0 | 2604 / 24 | ✔ |

All three exactly, with **zero residue** — every class carries a
certificate. All 7145 certificates were then accepted by `checkcert.py`.

Cross-checks run inside the sweep (both must be zero, both were):

* 500 realizable (4,8) classes and 500 realizable (3,9) classes fed to the
  BFP search → **0** produced a non-realizability certificate.
* All 24 BFP-certified (4,8) classes fed to the *heavy* realizer → **0**
  realized.

---

### 4.1 The BFP stress test at (3,10)

The three cases above are small (135, 4382, 2628) and their non-realizable
sets are tiny (0, 1, 24). Passing them shows the pipeline is *correct*; it
cannot show it *scales*. Uniform (3,10) is the only case with a published
answer, a large class count and a non-trivial non-realizable set:
**312 356 classes, 312 114 realizable, 242 non-realizable** (FMM13
Table 1 minus Table 2).

The catalogue is not shipped with omgamma, so it was regenerated by
running `ai/omgamma/runcat.py 3 10` **in a scratch copy** (omgamma itself
was not touched). It produced exactly **312 356** classes — matching
FMM13's published total independently, before any realizability work.

The test, pre-committed before the run: **does the full A–E cascade find
exactly 242 non-realizable classes with zero residue?**

* 242 with zero residue → the BFP implementation and the realizer are
  jointly complete at 300 000-class scale.
* fewer than 242, with residue → there is a gap that would otherwise have
  been carried silently into 9.28M classes.
* more than 242 → a false non-realizability certificate, which
  `checkcert.py` must then have caught.

**How far this generalises, stated in advance so it is not over-read
later.** (3,10) has 720 three-term GP relations against (4,9)'s 1260, a
different rank, and a non-realizable density of 0.077% against the 2.10%
we measure at (4,9) — a factor of 27. A clean result at (3,10) confirms
the *implementation* at scale. It does **not** establish BFP completeness
at (4,9), which is a different rank with a 27× denser non-realizable
population.

<!--TEST310RESULT-->


## 5. Canaries

`python canaries.py` — all pass.

**A. classification** — A1 the chirotope of an explicit random integer
point set → REALIZABLE. A2 the non-Pappus class, the unique non-realizable
uniform rank-3 OM on 9 elements → NON_REALIZABLE. A3 all 24 non-realizable
(4,8) classes → NON_REALIZABLE (24/24). A4 all 135 uniform (3,8) classes →
REALIZABLE.

**B. certificate rejection** — the checker must reject, and does: a
realization with one point reflected through the origin; a realization
whose chirotope string has one bit flipped; a rank-deficient matrix (a
bracket vanishes); a Gordan vector with one term dropped; with one weight
zeroed; with one weight negated; **with all weights zeroed** (the `w ≠ 0`
check people forget); with `big` moved to a term that is not the odd one
out; and one attached to a different class's sign string.

*Design note.* The first attempt at the corruption canary nudged a matrix
entry by 1 and expected rejection — and the checker accepted it, correctly:
the realization space is open, so a ±1 nudge of a well-conditioned integer
realization is usually just *another valid realization of the same class*.
The canary was wrong, not the checker. It now applies corruptions that
provably leave the cell and asserts that they do.

**C. decoder** — a sign string that violates a Grassmann–Plücker relation
is rejected as not a chirotope, and the BFP builder refuses to run on one.
Every decoded (4,9) key in every sample was also asserted to be a valid
uniform chirotope before use.

---

## 6. Measured cost at (4,9)

Sampling: `omdecode.load_coverage_4_9()` verifies the SHA-256 of `key_hi`,
`key_lo` and `stab` against `MANIFEST.json` before anything is decoded.

**Threading matters and must be pinned.** The first parallel run was ~15×
slower per class than a single process, because each worker's BLAS spawned
12 threads on a 12-core box. All numbers below are with
`OMP_NUM_THREADS=MKL_NUM_THREADS=OPENBLAS_NUM_THREADS=1`. Any deployment
must set these.

### 6.1 Per-class cost — one process, one core, no contention

`python pilot.py --sample49 300 --seed 77`, i7-9750H @2.6 GHz, 300 classes,
448.1 s wall = **1494 ms/class**.

| stage | entered | hit | ms/hit | miss | ms/miss | total | share of class-time |
|---|---|---|---|---|---|---|---|
| A realize cheap | 300 | 262 | 75.3 | 38 | 304.6 | 31.3 s | 7.0% |
| B bfp | 38 | 9 | 254.7 | 29 | 87.4 | 4.8 s | 1.1% |
| C realize medium | 29 | 14 | 795.1 | 15 | 3007.2 | 56.2 s | 12.5% |
| D realize heavy | 15 | 10 | 9335 | 5 | 52469 | 355.7 s | **79.4%** |

Distributions (not just means — the means are the misleading part):

* stage C: n=29, median 2.84 s, p90 3.19 s, **max 3.23 s**
* stage D: n=15, median 14.77 s, p90 54.10 s, **max 54.41 s**

Both distributions are *bounded by the budget*, not by a pathological
tail: a stage-D miss costs 52 s because it exhausts 60 tries × 120 sweeps,
every time. That is good news — there is no FMM13-style 11-CPU-day
outlier lurking here — but it also means **79% of the sweep's cost is
stage-D searches that fail**, and a hard per-class wall-clock cap is
mandatory before any deployment.

Memory: 224 MB peak per worker, and that is almost entirely the 62 MB
`coverage_4_9.npz` load. A worker fed a pre-sharded key file needs
< 50 MB. Nothing here strains a 7 GB runner.

### 6.2 Outcome rates on random (4,9) classes

Combined uniform random samples, current pipeline (`--sample49`, seeds 1
and 77), sampled after verifying the manifest hashes and after asserting
every decoded key is a valid uniform chirotope:

**3002 distinct classes.**

| verdict | count | rate | 95% Wilson interval | implied count of 9 276 595 |
|---|---|---|---|---|
| REALIZABLE, stages A–D | 2911 | 96.97% | [96.29%, 97.53%] | 8 995 000 |
| REALIZABLE, stages A–E | 2928 | **97.54%** | [96.92%, 98.03%] | 9 048 000 [8 991 000, 9 094 000] |
| NON_REALIZABLE | 63 | **2.10%** | [1.64%, 2.68%] | 194 700 [152 500, 248 200] |
| RESIDUE after A–D | 28 | 0.933% | [0.646%, 1.345%] | 86 500 [59 900, 124 700] |
| RESIDUE after A–E | **11** | **0.366%** | [0.205%, 0.655%] | **34 000 [19 000, 60 800]** |

The last row is the one that matters. Running the mutation warm-start
(stage E) on the 27 A–D survivors then available realized **17 of them**,
at 3.9 s each — classes that had already resisted 60 tries × 120 sweeps of
direct search. An independent earlier draw of 19 converted 13 and one of
18 converted 14, so the conversion rate is 63–78% across three runs.

All 17 stage-E matrices were written out and **accepted by
`checkcert.py`**. That matters because stage E reaches
`_rationalise` by a different code path from stages A–D, and a
producer-side check would not have caught a fault in it.

A stratified sample of the 8913 classes with non-trivial stabiliser is
reported in §6.4; at 0.096% of the catalogue it cannot move these totals.

### 6.3 What the residue actually is

Two diagnostics, both run on residue classes:

**Every residue class has all 9 deletions realizable.** Deleting one
element gives a uniform (4,8) class, and our (4,8) pipeline settles all
2628 of them, so this profile is exact. Of **18** residue classes (the
survivors of the full A+B+C+D cascade) and of 33 earlier ones, *every
single one* came back (9 realizable, 0 non-realizable). This matters
because the GP relations of a deletion are a *subset* of the class's, so a
BFP for a deletion is already a BFP for the class: the residue carries no
inherited obstruction, and any obstruction it does carry must be genuinely
9-element.

By contrast, of **25** BFP-certified non-realizable classes, 17 had one
non-realizable (4,8) deletion, 6 had two, and **2 had none** — so BFP is
still finding genuinely new 9-element obstructions (~8% of its hits), but
most of what it catches is inherited from (4,8). Sampled realizable
classes are, as they must be, 25/25 all-realizable-deletions.

**The search stalls at exactly one wrong bracket.** On 20 residue classes
(before the wall-crossing move existed), the minimum number of wrong
brackets reached was 1 in 17 cases and 2 in 2 cases. In other words the
searcher realizes a *mutant* of the target and cannot cross the last wall.
That single observation drove every subsequent improvement:

| move added | residue on a random (4,9) sample |
|---|---|
| build + repair sweep only | 17.6% |
| + prefix backtracking | 8.25% |
| + wall crossing (`_cross_wall`) | 3.25% |
| + heavy stage D | 0.85% |
| + mutation warm-start (stage E) | **0.37%** |

Every increase in realizer strength has eaten most of what was left, and
each was aimed at the *same* structural failure rather than being more
brute force. That is suggestive — but it is still not evidence that the
remaining residue is realizable. A method that keeps converting most of
the residue is not the same as a method that converges.

### 6.4 Structure: symmetric classes

Only 8913 of the 9 276 595 classes have a non-trivial stabiliser. A
stratified sample of them (`--stab-only`) is **enriched in
non-realizability** (2.8%, and 7.6% in an earlier 500-class draw, vs 1.7%
overall) and **depleted in residue**. So the algebraically special classes
are the ones BFP handles *best*, not worst; the uniform-sample rates are
not hiding a hard symmetric stratum, and at 0.096% of the catalogue this
stratum cannot move the totals anyway.

### 6.5 Threading

The first parallel attempt ran ~15× slower per class than a single
process: each worker's BLAS spawned 12 threads on a 12-core (6-physical)
box. With threads pinned it recovered, but on this laptop 6 concurrent
workers still achieved well under 6× the single-process throughput —
6 physical cores, hyperthreads that do not help this workload, and one
competing job. Treat 6 physical cores as ~5 effective workers here.

---

## 7. Extrapolation to 9 276 595 classes

### 7.1 Compute

Stages A–D measure at 1.494 s/class single-core; stage E adds ~3.9 s on
the ~0.93% of classes that reach it, i.e. ~0.034 s/class amortised:

```
9 276 595 classes x 1.53 s = 14 190 000 s = 3 940 core-hours
```

The cost/residue frontier, all measured except where noted:

| configuration | s/class | core-hours | residue |
|---|---|---|---|
| A + B only | 0.121 | 312 | ~13% (stage-A misses that BFP does not catch) |
| A + B + C | 0.308 | 794 | ~5% |
| A + B + C + D | 1.494 | 3 850 | 0.933% [0.65%, 1.35%] |
| A + B + C + D + E | 1.53 | **3 940** | **0.366%** [0.21%, 0.66%] |

**Stage D is 79% of that cost and stage E is 2%, yet E converts ~2/3 of
what D leaves.** The obvious rerun is to put E *before* D — order the cascade
A, B, C, E, D — which on the measured per-stage rates should land near
1.3 s/class with the same or better residue. Not measured; do it first
on any real run.

**Checking is not the problem.** At 1–2 ms per certificate, re-verifying
all 9.28M certificates costs **3–5 core-hours** — a laptop afternoon,
standard library only. That asymmetry is the entire point of the
finite-certificates program and it holds here: the sweep is a cloud job,
the proof is a laptop job.

Artifact volume: mean certificate 462 bytes as JSON → ~4.3 GB for the full
catalogue, ~1.5 GB gzipped. A packed binary form (realizable: 36 signed
bytes; Gordan vector: ~40 terms × 8 bytes) would be ~600 MB. This should
be designed before the sweep, not after.

### 7.2 What the sweep would actually produce

Not the split. Concretely:

* **~9 048 000 classes certified REALIZABLE** [8 991 000, 9 094 000], each with an explicit
  integer 4×9 matrix — a *lower bound* on the realizable count that is
  checkable in microseconds per class;
* **~194 700 classes certified NON-REALIZABLE** [152 500, 248 200], each
  with a Gordan vector over three-term GP relations — a *lower bound* on
  the non-realizable count;
* **~34 000 classes RESIDUE** [19 000, 60 800] — an explicit, published
  list of open cases with no certificate either way.

Caveat on that last figure: it is a *directly measured* 0.93% A–D residue
multiplied by a *measured conversion rate* for stage E (63–78% on three
draws of 18–27 classes). It therefore carries an assumption on top of its
Wilson interval — that the residue population stays homogeneous as the
sweep scales by 3000x. The ~34 000 projected survivors could be
structurally unlike the ~70 we have looked at. The A–D residue,
~86 500 [59 900, 124 700], is the figure with no extra assumption in it.

The two bounds are exact and independently checkable. The cell is filled
only if the residue reaches zero.

### 7.3 Is the tail Mnëv territory?

Honestly: **unknown, and there is no theorem to lean on.** Mnëv
universality bites already at rank 3 (DS4 §3.1), so "rank 4 on 9 elements
is too small for real-algebraic pathology" is not a statement anyone can
make. What can be said:

* The *empirical* record is entirely favourable: BFP has sufficed for
  every class ever fully enumerated — OM(4,8), OM(3,9), OM(6,9), uniform
  (3,10), uniform (3,11) — and the smallest known BFP-resistant oriented
  matroid lives at n = 12–14, well above 9.
* Our own residue shows no *algebraic* signature so far: no vanishing
  margins, no need for large denominators (99.9% of realizations round at
  denominator ≤ 256), no stage-D outliers beyond the budget cap.
* But the residue does not shrink to zero, and each increment of realizer
  strength has bought a diminishing amount of it.

So there are exactly two possibilities for the residue, and they are both
interesting:

1. **They are realizable and the searcher is not strong enough.** Then a
   better realizer (see §9.2) closes the cell.
2. **They are non-realizable and have no biquadratic final polynomial.**
   Then they are BFP-resistant oriented matroids at **n = 9**, three to
   five elements smaller than any known example — which would be a result
   in its own right, and a strictly more interesting one than the count.

We cannot currently tell these apart, and that is the whole of the risk.

---

## 8. Deployment

Budget: **3 940 core-hours** for the full A+B+C+D+E sweep.

### (a) This laptop — NO

i7-9750H, 6 physical cores / 12 logical, 16 GB. Measured effective
parallelism is ~5 workers, so

```
3 940 core-hours / 5 = 790 hours = 33 days of continuous run
```

and that is before the residue pass. The machine also has a documented
instability history (episodic nonpaged-pool exhaustion) that makes
month-long pinned runs a bad idea. **Reject.** The laptop's role here is
the *checker*: 3–5 core-hours to re-verify everything, which is exactly
what it should be doing.

### (b) GitHub Actions on a public repo — supplement, not primary

20 concurrent jobs × 2 cores × 6 h = **240 core-hours per wave**.

```
3 940 / 240 = 16.4 waves  ->  ~97 hours of wall clock if waves run back to back
```

Free, and genuinely attractive for *re-verification* (the checker pass is
one wave with room to spare, and it being reproducible by anyone with a
GitHub account is a real feature).

Three costs the raw arithmetic hides:

1. **The key shards do not exist yet.** `coverage_4_9.npz` (62 MB) is not
   in git; `tree_4_9.npz` (10.4 MB) is, but replaying 9.27M mutations to
   recover the keys is a multi-hour job. A one-time preparation run must
   reconstruct the keys and publish ~40 sharded key files (148 MB raw,
   ~40 MB packed) as release assets. Without this step the plan does not
   run at all.
2. **Artifacts.** 0.6–4.3 GB of certificates to move and retain, against
   Actions' artifact size and retention limits, with no shared state to
   accumulate into.
3. **Terms of service.** A 3 940 core-hour arithmetic sweep on free public
   runners is close to the use Actions' terms discourage, even for a repo
   whose stated purpose is that computation. Not worth the risk for the
   bulk pass when the paid alternative costs $315.

### (c) GCP spot VMs — RECOMMENDED for the sweep

```
3 940 core-hours x $0.08 = $315
```

Shape options at that price:

| fleet | vCPU | wall clock |
|---|---|---|
| 4 x c2d-standard-16 spot | 64 | ~60 h |
| 8 x c2d-standard-16 spot | 128 | ~30 h |
| 16 x c2d-standard-16 spot | 256 | ~15 h |

Preemption is a non-issue: shards are completely independent (no
canonicalisation, no shared state), so resuming means skipping the shards
that already have output. Egress is negligible. Standing discipline
applies — **stop the VMs when done**, budget alert first, and pin
`OMP_NUM_THREADS=1` in the worker image or lose most of the throughput.

### Recommendation

**GCP spot for the sweep ($315, ~31 h wall on 128 vCPU), GitHub Actions
for the independent re-verification pass (free, one wave, reproducible by
anyone), the laptop for development and for spot-checking certificates.**
Do the cheap A+B+C configuration first ($64, 794 core-hours) to get the
bounds and the residue list, *then* add stage E (cheap) and only
then decide whether stage D's extra ~$210 still earns its place — on the
measured rates, E ahead of D makes most of D redundant.

---

## 9. Verdict

### 9.1 GO / NO-GO

**CONDITIONAL GO — with the deliverable renamed.**

GO, because:

* The cell is genuinely open and we hold the one input it needs.
* The pipeline reproduces **all three** published splits exactly —
  (3,8) 135/0, (3,9) 4381/1, (4,8) 2604/24 — with **zero residue** and
  7145 certificates accepted by an independent standard-library checker.
  The correctness gate the brief demanded is passed, not approximated.
* Both certificate shapes are small, exact and fast to check: 1–2 ms per
  class, 3–5 core-hours for the entire 9.28M catalogue.
* The bulk sweep is *cheap*: $315 on spot, or $64 for the configuration
  that already yields both bounds and a (larger) residue list. Cost is not
  the constraint. It was never going to be.
* The residue has been driven from 17.6% to **0.37%** in this pilot alone,
  every step by aiming at the same structural failure rather than by
  spending more compute — and the last step, the mutation warm-start, is
  one of the *cheapest* stages in the cascade.

NO-GO on the headline claim, because:

* **~0.37% of classes (~34 000, 95% interval 19 000–60 800) are settled by
  neither method, and we have no third method.** A sweep today produces a
  certified lower bound on realizable, a certified lower bound on
  non-realizable, and an explicit list of open cases. That is strictly
  more than exists today and is worth publishing — but it is **not**
  filling in FMM13's blank cell, and it must not be described that way.
* BFP's completeness at n = 9 is an empirical hope, not a theorem. FMM13
  themselves never ran a non-realizability engine; they *observed* that
  their leftovers matched Bokowski–Richter's BFP hits. We are relying on
  the same observation one element further out.

**Is the tail intractable?** The trend is strongly favourable and the
plateau has not been located. That is weaker than "no", and deliberately so — and this is the
honest, hedged version. The residue shows none of the signatures of
real-algebraic hardness: no runaway denominators, no unbounded search
times (every stage-D failure is a budget exhaustion at 52 s, not a
blow-up), no vanishing margins, and no obstruction inherited from any
8-element minor. Every strengthening of the searcher has eaten most of the
residue, most recently the wall-crossing move which halved it. But the
residue has not gone to zero, and "each improvement helps" is not a
convergence argument.

### 9.2 The gate, stated precisely

Before spending anything on a full sweep, **locate the plateau**. The
residue has fallen 17.6% → 8.25% → 3.25% → 0.93% → 0.37% across five
successive improvements, all aimed at the same structural failure. Nobody
should commit 3 940 core-hours without knowing whether the next
improvement takes it to 10⁻⁴ or whether it has already stopped moving.
The decisive experiments, in order:

1. **A residue-only run at scale.** Sweep a few hundred thousand classes
   with stages A–C only (cheap: ~$5), collect the ~5% residue, then throw
   E and D at it. That gives a residue set of thousands rather than the
   ~70 we have looked at, and it is the only way to tell whether the
   surviving classes are a homogeneous population or a structured family.
   *This is the gate.* If the post-E residue rate on that set matches the
   0.37% measured here, the projection holds; if it plateaus higher, the
   projection was optimistic and the plateau is the finding.
2. **Tree-based mutation warm-starting.** Stage E currently realizes the
   mutant *from scratch*. The catalogue ships a mutation spanning tree
   (`tree_4_9.npz`, max depth 27), so the parent's realization could be
   reused directly and the inner search skipped entirely — strictly
   stronger and much cheaper than what is built. It is stateful (parents
   before children), which fights sharding, but 27 depth-waves is a
   workable schedule.
3. **A second non-realizability method.** This is the real gap: we can
   only ever *fail* to realize, never prove non-realizability outside BFP.
   Options, in increasing cost:
   final polynomials beyond the biquadratic ones; the non-Euclideanness
   and HK\* tests FMM13 list; Scheucher's SAT chirotope encoding
   ([arXiv:2105.08406](https://arxiv.org/abs/2105.08406)) with DRAT
   certificates, which is the closest working rank-4 machinery and yields
   independently checkable proofs — the right shape for this program.
4. **FMM13's own solvability-sequence realizer**, which is constructive
   and algorithmically unlike ours, so it will fail on different classes.
   Also: try to reach Miyata/Fukuda for a mirror of their results page
   before it is gone.

**Decision rule.** After 1 and 2, re-measure. If the residue rate falls to
~10⁻⁴ or below, commit to the full sweep and expect to close the cell. If
it plateaus in the tens of thousands, stop calling this an enumeration
project and start treating the plateau as the object of study — a
candidate family of BFP-resistant oriented matroids at n = 9 would be
smaller than anything in the literature by three to five elements, and is
the more interesting result of the two.

### 9.3 What must not be done

Do not run this on the laptop (§8a). Do not start a full sweep before the
key shards exist and a per-class wall-clock cap is in place — one
uncapped pathological class stalls a whole job. Do not report the residue
count without its interval; the verdict lives inside that interval.

---

## 10. The code

| file | what |
|---|---|
| `omdecode.py` | catalogue access. REUSED DECODER from `ai/omgamma/coverage_checker.py` and nothing else; verifies the manifest SHA-256 of `key_hi`/`key_lo`/`stab` before sampling |
| `realize.py` | realization search (cone centring, prefix backtracking, repair sweep, wall crossing) + exact integer determinant verification |
| `bfp.py` | three-term GP inequality system, Gordan LP search, exact rational reconstruction of the certificate |
| `pilot.py` | the A/B/C/D cascade, sharding, per-stage timing, cross-check canaries |
| `checkcert.py` | **the checker.** Standard library only; imports nothing from this project or omgamma; different determinant algorithm from the producer |
| `canaries.py` | the canary battery of §5 |
| `diag.py` | residue diagnostics: deletion profiles, budget hammering |
| `aggregate.py` | shard aggregation, Wilson intervals, extrapolation |

```
python pilot.py --cat 4 8 --out certs_4_8.jsonl --cross 500   # the gate
python pilot.py --sample49 3000 --seed 1 --shard 0 6 --out s0.jsonl
python checkcert.py certs_4_8.jsonl                            # independent
python checkcert.py --selftest
python canaries.py
python aggregate.py "certs_49_u_*.jsonl"
```

Set `OMP_NUM_THREADS=MKL_NUM_THREADS=OPENBLAS_NUM_THREADS=1`. Requires
numpy + scipy for the pipeline; the checker requires neither.
