# The final residue of the (4,9) sweep

Written 2026-08-02, after `ai/omreal/sweep49.py` finished all 9,276,595
uniform rank-4 classes on nine elements and left **659** of them OPEN.
This is the companion to `OPEN_ATTACK.md`, which decided the 126-class
residue visible at the 26% mark; the toolkit is the same, the residue is
the final one, and the numbers below are the whole catalogue's.

---

## 0. Result

**All 659 are realizable. The residue is empty.**

| | |
|---|---|
| OPEN classes attacked | **659** — the sweep's entire final residue (9,276,595 rows decided, 100.00%) |
| **REALIZABLE**, with an exact integer 4x9 certificate | **659** |
| **NON_REALIZABLE** | **0** |
| **STILL_OPEN** | **0** |
| accepted by `fpcheck.py` | 659 / 659 |
| accepted by `ai/omreal/checkcert.py` | 659 / 659 |
| accepted by `reverify.py` (written tonight, fourth implementation) | 659 / 659 |
| certified to have **no biquadratic final polynomial** (exact Gordan witness, level L0) | **659 / 659** |
| certified to have no Gordan vector over the wider L1 support | **659 / 659** |
| median time to realize | **3.9 s** (max 178.7 s; 6,855 s of deciding runs) |

### The critical question

> **Did any class turn out non-realizable without a biquadratic final
> polynomial?**
>
> **No. Not one.** Across 728 result records covering all 659 classes there
> were **zero** NON_REALIZABLE verdicts of any kind: zero Gordan vectors at
> level L0 *on all 659*, zero at level L1 *on all 659*, zero monochrome
> relations, and zero general final polynomials at every degree and support
> that was reached (§4.1 says exactly which classes reached that stage and
> why the others did not need to). Every class was decided in the *positive*
> direction, with a matrix.

So the sharpened conjecture of `ai/omminor/MINOR_THEORY.md` §4.3 —

> *a uniform rank-4 oriented matroid on 9 elements with no biquadratic final
> polynomial is realizable*

— **is not refuted, and it survived the only population that could have
refuted it.** Every one of the 659 was a genuine candidate: each carries a
verified exact certificate that it has *no* biquadratic final polynomial, so
each satisfied the conjecture's hypothesis before it was attacked, and each
would have been a counterexample had a final polynomial then been found for
it. All 659 are now closed with an explicit integer matrix.

Be precise about what the witnesses add, because it is less than it looks.
`OPEN_ATTACK.md` §0 states the Lemma and it still applies at 659: once a
class is realized by X, putting u_B = log|det X_B| satisfies every forced
inequality, so "no BFP" is a *corollary of the realization*, not an
independent finding. The witnesses matter because they are what a
counterexample's hypothesis would have been, because they are an
independent cross-check (a class carrying both a witness and a Gordan vector
is impossible, and none does), and because they exclude a false OPEN —
`ai/omreal/bfp.py` returning `None` conflates an infeasible LP with a failed
exact reconstruction, and the witness excludes that outright.

### The whole (4,9) catalogue

| | classes | how backed | re-verified in this session |
|---|---|---|---|
| **REALIZABLE** | **9,072,815** | integer 4x9 matrix, all 126 brackets exact | **9,072,815 / 9,072,815** |
| **NON_REALIZABLE** | **203,780** | biquadratic final polynomial | **203,780 / 203,780**, by two independent checkers |
| **undecided** | **0** | — | — |
| total | **9,276,595** | | **9,276,595 / 9,276,595** |

**Every certificate for every class in the cell was re-checked tonight**
(§6.2): 9,072,015 sweep realizations + 203,780 sweep refutations + 141
reissued + 659 new, **0 rejected**.

9,072,815 = 9,060,883 (sweep, walk) + 11,273 (sweep, repair) + **659**
(this work). Certificate coverage is reconciled row by row in §6, including
the 141 rows whose certificate line the sweep lost and which are reissued
here, and every certificate the sweep wrote is re-checked in §6.2.

---

## 1. The residue, and that it really is 659

`ai/omreal` was read-only throughout; the sweep process had already exited
(no `python.exe` with `sweep49` in its command line at any point in this
session), and `sweep_state/st.dat` has the same SHA-256 before and after
this work, `ce470cf1e56e7b98cc9e8ad47e1bbee3c3e8d3fd2c1632045bb7e6966fe5800c`.
No `.pyc` file was written under `ai/omreal` (its `__pycache__` still holds
only yesterday's entries); every invocation set `PYTHONDONTWRITEBYTECODE=1`
and every module sets `sys.dont_write_bytecode = True`.

| statement | value |
|---|---|
| `catalog.py`'s own enumeration from `st.dat` | 659 |
| what `sweep49.py report` printed | 659 |
| `RESIDUE` records in the sweep's own certificate shards | **659**, and they carry `row`, matching the OPEN rows exactly |
| status counts summing to the catalogue | 0 + 9,060,883 + 11,273 + 203,780 + 659 = 9,276,595 |
| previous session's 126-row snapshot ⊂ this 659 | **yes**, exactly; 533 rows are new |

Tree depths run 13–26, against 13–17 for the 126 at the 26% mark: 1, 4, 32,
54, 94, 127, 122, 97, 70, 28, 17, 9, 2, 2 at depths 13…26. The residue rate
rose from 0.0052% to **0.0071%** of the catalogue as the sweep walked deeper
into the tree. That, and the pass-1 survival rate (54 of 531, ~10%, against
13 of 107, ~12% previously), is the same picture at eight times the scale:
**the OPEN set is an artefact of how far the walk has to search, not a
structural population.**

---

## 2. Method

Three tools, in the order they get to speak. Nothing here is new except the
exact gate (§2.2) and the neighbour source (§2.4); the rest is
`OPEN_ATTACK.md`'s, re-run.

### 2.1 Weapon A — one-point completion, in float

Fix an element *p*, take an integer 4x8 configuration *Y* realizing the
deletion χ∖*p*, and the 56 brackets containing *p* become homogeneous linear
conditions on the missing column: one LP in four variables. Successes are
exact (the proposed column is rounded to integers and re-checked against the
exact integer rows, then all 126 brackets are recomputed) — failures are
heuristic. Run in three passes over the 533 new rows:

| pass | budget | walk-depth | decided |
|---|---|---|---|
| 1 | 60 s | 8 | **479** |
| 2 | 240 s | 60 | **53** |
| 3 (one class) | 1800 s | 200 | **1** |

Four workers, sharded by `runshard.py` so that concurrent appends cannot
interleave. The 126 rows of the previous session were skipped by the resume
rule, exactly as designed.

### 2.2 THE EXACT GATE — `exactlp.py` as the completion oracle

`OPEN_ATTACK.md` §3.1 records the float LP's scope as *"exactly verified
success, heuristic numerical failure"*, and the rule that follows: exact
rational feasibility is **required** before any class is reported STILL_OPEN
on numerical grounds. `exactgate.py` is where that rule is applied. It
replaces the float completion test with `exactlp.exact_feasible`, which
decides `A x > 0` in rational arithmetic and returns a self-verified integer
certificate either way — an integer column x with `A x > 0`, or a
nonnegative integer λ ≠ 0 with `Aᵀλ = 0`.

It is strictly stronger than the float path as a **searcher**, because two
loss channels disappear:

* `weaponA._round_positive` rounds the float solution against a fixed ladder
  of denominators and gives up if none lands;
* `weaponA._shrink` discards the completed matrix outright if any entry
  exceeds 2²² — a size guard, unrelated to correctness, that can throw away
  a genuine realization.

Neither exists in the exact path, and the difference is not theoretical:
see §4.2, where the exact oracle minted a realization whose largest entry is
**2⁶⁶·⁴**, forty-four binary orders of magnitude past that cap, and all three
checkers accepted it.

**What it cannot do, and this is written into the data model.** A class is a
set of sign conditions; *Y* is one point of the nine-dimensional realization
space of χ∖*p*. An exact INFEASIBLE certificate proves that *that Y* does not
extend, and nothing about χ. Ten thousand of them prove ten thousand
statements about points. So `exactgate.py` emits only REALIZABLE or
STILL_OPEN, never NON_REALIZABLE, and a STILL_OPEN record carries
`exact_lp`, `exact_infeasible` and `deletions_covered` rather than any
boolean claim of non-extendibility. §4.2 is the empirical demonstration that
this caution is not pedantry.

### 2.3 Weapon B — non-realizability, at two supports and two degrees

* **level L0** — Gordan vectors over the 1,260 three-term
  Grassmann–Plücker relations (2,520 forced inequalities). This is
  bit-for-bit `ai/omreal/bfp.py`'s support, re-implemented independently, so
  it is a cross-check on the sweep as well as a search. Run on **all 659**.
* **level L1** — the same over the 5,544 relations of the whole one-step
  Plücker exchange family (three-, four- and five-term), ~8,100
  inequalities. Run on **all 659**.
* **general final polynomials** (`fpoly.py`), degree 2 and degree 3 at both
  levels, run on the classes weapon A failed to decide within a pass.

### 2.4 The neighbour source, implemented at last

`OPEN_ATTACK.md` §10 lists as escalation step 2 a source it never built:
canonicalize each of a class's ~15 mutants, look up its catalogue row, and
recover its stored realization — giving *every* realizable mutation
neighbour, where the tree gives only the parent and any already-realized
children. `neighbours.py` implements it, and the last undecided class is
exactly the case that motivates it: **row 3992924 has no children in the
spanning tree at all**, so T1/T2 offered it one starting point, while it has
15 mutable bases, 12 of whose mutants are realizable.

"At the cost of the group element" is avoided rather than paid.
Canonicalization says *which* row a mutant belongs to and supplies a
relabelling; it is not trusted to say how to move a matrix. Instead the
catalogue representative's realization is permuted, its bracket signs are
computed exactly, and the reorientation and global sign are **solved for**
as a 126-equation linear system over GF(2) in ten unknowns — then the
resulting matrix's 126 brackets are recomputed and it is used only if they
equal the mutant exactly. A wrong convention fails the bracket check and the
neighbour is skipped; it cannot propagate. Recovered: **12 of 15**, each
verified to differ from χ in exactly the one flipped bracket.

In the event this was not needed — the deep float pass realized row 3992924
first — so it is reported as a tool that works and was not load-bearing.

---

## 3. Validation

Every gate below was run tonight, against the **finished** sweep state.

| gate | claim | measured | |
|---|---|---|---|
| `gplib.py` | the identity tables really are identities | 1,260 + 3,780 + 504 relations × 60 random integer 4x9 configurations, exact determinants, **0 failures**; a deliberately flipped ε is caught | PASS |
| `exactlp.py` | the exact oracle's own self-test, including a 2⁶⁰ cancellation where float64 would report margin 0 | 160 cases | PASS |
| `fpcheck.py --selftest` | the independent checker's sabotages | 4 cases | PASS |
| `canaries.py` | 23 sabotaged certificates must be rejected *with the expected diagnosis* | 7 controls accepted, **23 sabotages rejected**, 0 failures | PASS |
| **A1** | weapon A reproduces REALIZABLE(**repair**) — the hard-but-solved population | **40 / 40**, median 0.34 s, max 21.4 s | PASS |
| **A2** | weapon A on REALIZABLE(walk), smoke control | **40 / 40**, median 0.01 s | PASS |
| **B1** | level-0 Gordan fires on every certified NON_REALIZABLE class | **40 / 40** | PASS |
| **B2** | level-0 and level-1 Gordan fire on **no** certified REALIZABLE class (**fatal if violated**) | **0** false positives on 80, at both levels | PASS |
| **B3** | the exact witness exists for every certified REALIZABLE class, and for none of the NON_REALIZABLE ones | **80 / 80** and **0 / 40**, at both levels | PASS |
| **B4** | both checkers accept everything the gates produce | 80 realizations + 40 Gordan vectors + 160 witnesses, 0 rejections | PASS |

`data/validation.json`, `data/validation_final.log`,
`data/canaries_result.json`. Three further gates were built tonight,
specifically for the exact gate, because its *negative* direction is the one
thing in this toolkit that is not self-checking.

### 3.1 Does float64 ever disagree with the exact oracle? (`probe_exact_vs_float.py`)

The regime where float64 should fail is large integer entries — deletion
entries reach 2²², so 3x3 minors can exceed 2⁶⁸. Fresh (8,4) realizations do
not live there; configurations deep in a hill-climb and matrices transported
from the sweep's store do. All three were sampled, on 12 randomly chosen
OPEN classes:

| regime | configurations | float says feasible, exact says no | exact says feasible, float says no |
|---|---|---|---|
| `fresh` | 36 | 0 | 0 |
| `store` (transported) | 48 | 0 | 0 |
| `walk`, 40 steps | 180 | 0 | 0 |

**264 configurations, zero disagreements.** The reason is measurable and
worth recording: the completion rows' entries top out around **2³⁷** in
practice (median 2²⁶), well inside float64's exact-integer range of 2⁵³,
because `_shrink`'s 2²² cap on the deletion keeps them there. So float64
represents these coefficients exactly and the residual risk is solver
tolerance at t ≈ 0, not representation. Median cost: 2.0 ms float, 19 ms
exact. `data/probe_exact_vs_float.json`.

### 3.2 Are the completion rows the *right* rows? (`rowcheck.py`)

An INFEASIBLE certificate is a true statement about the matrix `A` that
`weaponA.completion_rows` builds. If that construction had a sign or index
convention wrong, the certificate would be internally valid and meaningless.
Successes are self-checking; failures are not. So the rows were checked
against ground truth: take a known realization Z of χ, delete column *p*,
build `A`, and require `A · Z[:,p] > 0` in **every** coordinate — an exact
integer test with no solver in it — and require `exact_feasible(A)` to
return FEASIBLE, since a solution demonstrably exists.

**120 known realizations × 9 deletions = 1,080 (Y, p) pairs: 0 violations of
either.** `data/rowcheck.json`.

### 3.3 Can the exact oracle mint a realization that does not exist? (`exactgate.py selftest`)

| check | measured |
|---|---|
| reproduces REALIZABLE(repair) classes with the exact oracle | **8 / 8** |
| the big-integer determinant agrees with `numpy.linalg.det` | 200 / 200 random 4x4 |
| on **certified NON_REALIZABLE** classes, where no configuration can extend | **4,441 exact LPs, 4,441 INFEASIBLE (100.0%), 0 realizations minted** |

The last row is the fatal one and it also exercises the INFEASIBLE path
4,441 times, each with a self-verified integer λ.
`data/exactgate_selftest.log`.

---

## 4. Results

### 4.1 The 659

| | |
|---|---|
| attacked | **659** |
| **REALIZABLE** | **659** |
| NON_REALIZABLE | 0 |
| STILL_OPEN | 0 |
| deciding-run wall time | **6,855 s** (median 3.9 s, min 0.2 s, max 178.7 s) |
| all result records, including passes that failed | 11,442 s |
| float completion LPs that came back infeasible | **716,477** across all passes; 17,357 in a single deciding run |
| largest matrix entry emitted | 262,144; 34 of the 659 exceed 16,384 |

Which source produced the winning eight-point configuration:

| source | classes |
|---|---|
| `walk` — a fresh (8,4) deletion realization, then the guided hill-climb | 531 |
| `store_walk` — the sweep's stored parent/child realization, then the hill-climb | 55 |
| `fresh` — a fresh deletion realization, completed immediately | 38 |
| `store` — the sweep's stored realization, completed immediately | 35 |
| `control` — `realize.realize` with a large budget | **0** |

The control never fired, on any of the 659. That is its purpose: if the
project's existing searcher had succeeded where the structured search
failed, the structure would be wrong.

Weapon B, on the classes that reached it:

| search | classes | certificates found |
|---|---|---|
| Gordan, level L0 (= `bfp.py`'s support) | **659** | **0** |
| Gordan, level L1 (three-, four- and five-term families) | **659** | **0** |
| monochrome relation, either level | 659 | 0 |
| final polynomial, degree 2, levels L0 and L1 | 2 (rows 375712, 3992924) | 0 |
| final polynomial, degree 3, levels L0 and L1 | 1 (row 375712) | 0 |

The final-polynomial searches ran only on classes weapon A had failed within
that pass — by design, since a realized class needs no refutation. Degree 3
at level L1 is a 698,544-column LP against 335,790 monomials and cost 592 s
on the one class that reached it; its optimum was −2.0 × 10⁻¹⁰, i.e. zero.

### 4.2 The exact gate, and the one class that needed it

Only one class ever became a STILL_OPEN candidate: **row 3992924**, depth
19, which survived pass 1 (60 s) and pass 2 (240 s, walk-depth 60, plus
degree-2 final polynomials at both levels). It was put through the exact
gate twice, and the two runs together are the clearest possible statement of
what the gate does and does not prove:

| run | budget | exact LPs | INFEASIBLE (all with a verified integer λ) | deletions covered | outcome |
|---|---|---|---|---|---|
| seed 20260802 | 900 s | **31,542** | **31,542 — every one** | **9 / 9** | no realization found |
| seed 777001 | 1800 s | 21,370 | 21,369 | 9 / 9 | **REALIZABLE** at 633 s, max entry 2⁶⁶·⁴ |
| seed 424242 | 1800 s | 42,669 | 42,668 | 9 / 9 | **REALIZABLE** at 1,136 s, max entry 2⁵⁸·⁷ |

The first run produced **thirty-one thousand five hundred and forty-two
exact Gordan infeasibility certificates, covering all nine deletions, for a
class that is realizable.** That is the whole argument of §2.2 in one line:
exact infeasibility on sampled configurations is not evidence about the
class, and had this class been reported STILL_OPEN on the strength of those
certificates, the report would have been true and useless. The three runs
differ only in seed.

The two realizations the exact oracle *did* find are worth keeping for a
different reason: their completion columns carry entries near
**9.9 × 10¹⁹ ≈ 2⁶⁶·⁴** and **4.8 × 10¹⁷ ≈ 2⁵⁸·⁷** — beyond int64, and up to
2⁴⁴ times past `_shrink`'s 2²² cap, so the float path could not have emitted
either one even had it found the same cone. They are in
`data/exactgate_realizable_e2_s0.jsonl` and
`data/exactgate_realizable_e3_s0.jsonl`, and are accepted by `fpcheck.py`,
`ai/omreal/checkcert.py` and (for e2) `reverify.py`. That is the §2.2 claim
"strictly stronger as a searcher" measured rather than argued. The class's
headline certificate is the smaller one the deep float pass found (max entry
16,384, 161.8 s, after 16,289 infeasible completion LPs).

**So the exact gate ended with nothing left to gate.** No class in this batch
is reported STILL_OPEN, and therefore **no verdict anywhere in this session
rests on an infeasibility claim** — the same position `OPEN_ATTACK.md`
reached on 126 classes, now on 659.

### 4.3 Per-class outcomes

`data/final_outcomes.tsv` (659 rows: row, depth, verdict, source, seconds,
largest entry, witness at L0 and L1, exact-gate counters). Appendix B below
is the same table in markdown.

---

## 5. Certificates, and three independent checkers

| file | records | what |
|---|---|---|
| `data/certs_realizable.jsonl` | **659** (659 distinct chirotopes) | the result: integer 4x9 matrices in `ai/omreal`'s schema |
| `data/certs_no_bfp.jsonl` | 1,392 records, **1,318 distinct (class, family-set) pairs = 659 × 2** | the exact "no final polynomial" witnesses at L0 and L1. The 74 surplus records are re-emissions from rows attacked in more than one pass; every class has both levels exactly once after de-duplication |
| `data/certs_backfill.jsonl` | 141 | §6 |
| `data/exactgate_realizable_e2_s0.jsonl` | 1 | the big-integer realization of §4.2 |
| `data/certs_nonrealizable.jsonl` | **does not exist** | nothing produced one |

Checked by:

```
fpcheck.py            659 realizations + 1,392 witnesses + 141 backfill  ALL ACCEPTED
../omreal/checkcert.py   659 realizations + 141 backfill                 ALL ACCEPTED
reverify.py           659 + 141 + 1 realizations, 1,392 witnesses
                      (3,507,840 inequalities rebuilt and tested)        0 failures
```

`reverify.py` was written tonight for this run and shares no code with
anything: standard library only, no numpy in its decision path, its own
rebuild of the colex order, its own decoding of the catalogue's 128-bit keys
with python integer shifts, its own generation of the three-term relations,
and determinants by **exact rational Gaussian elimination over `Fraction`** —
a fourth algorithm, distinct from `fpcheck.py`'s fraction-free Bareiss,
`checkcert.py`'s cofactor expansion and `exactgate.py`'s Laplace along two
rows. It also verifies:

* the **provenance** of the catalogue — the SHA-256 of
  `coverage_4_9.npz`'s three raw arrays against `MANIFEST.json`'s
  `array_sha256`: **match**;
* that each certificate's chirotope equals the one decoded **from the npz**
  for the catalogue row the result file names: **800 / 800**.

---

## 6. The whole catalogue's certificate coverage (`certaudit.py`)

`st.dat` says how many rows the sweep *decided*; the certificate shards say
how many decisions it *wrote down*. Those are different claims. Every
certificate carries its 126-sign chirotope, so each was re-encoded into the
catalogue's 128-bit key and matched against `sweep_state/{hi,lo}.npy`.

| | |
|---|---|
| certificate records in `ai/omreal/sweep_state/certs/` | 9,276,454 |
| matched to a catalogue row | **9,276,454** (0 unmatched) |
| rows carrying more than one certificate | **0** |
| rows carrying none | **141** |
| the 141, by sweep status | **all REALIZABLE(walk)**; 0 non-realizable, 0 OPEN |

And the certificates agree with the status array on every matched row, with
no exceptions:

| sweep status | certificate verdict |
|---|---|
| REALIZABLE(walk) 9,060,742 | REALIZABLE 9,060,742 |
| REALIZABLE(repair) 11,273 | REALIZABLE 11,273 |
| NON_REALIZABLE 203,780 | NON_REALIZABLE **203,780** |
| OPEN 659 | RESIDUE 659 |

**The 141 are lost lines, not lost work**, and they are reissued here. The
sweep's shared `Z.dat` still holds the realization it found for each; all
141 stored matrices were re-checked bracket by bracket and **141 of 141**
verify against the catalogue chirotope, so `backfill.py` emits them as
certificates without any search (`data/certs_backfill.jsonl`, accepted by
all three checkers). The likely cause is a worker's output buffer at
shutdown; 141 across nine shards is the right order.

So the honest coverage statement, which must not be compressed into one
number:

> The sweep's own shards certificate-back **9,276,454** of the 9,276,595
> rows. The remaining **141**, all REALIZABLE(walk), are certificate-backed
> from `Z.dat` via `ai/omopen/data/certs_backfill.jsonl`. The **659** OPEN
> rows are certificate-backed by this work. Every row in the (4,9)
> catalogue therefore has, on disk, either an integer realization or a
> biquadratic final polynomial.

### 6.2 And every one of them was re-checked (`fastverify.py`, `verifyall.py`, `bfp2gordan.py`)

Counting certificates is not checking them, and for the conjecture the
difference is load-bearing in **both** directions. A counterexample is a
class that is non-realizable and has no BFP. Ruling one out across the
catalogue requires every class to be demonstrably realizable *or* to carry a
valid BFP — and a **bogus realization certificate** would leave a class in
neither bucket, because the sweep stops looking at a class it believes it
has realized and never tests it for a final polynomial at all. So the
realizable side matters as much as the refuted side.

**The 203,780 non-realizability certificates: verified, twice.**

| checker | result |
|---|---|
| `ai/omreal/checkcert.py` (cofactor determinants, rebuilds the GP relation from `L` and `abcd`, requires `big` to be the unique odd term, requires Σ w_i v_i = 0 exactly with every w_i > 0) | **203,780 / 203,780 ACCEPTED**, 203,780 distinct classes |
| `fpcheck.py` (Bareiss determinants; additionally re-verifies every relation a certificate names as a polynomial identity on random integer 4x9 matrices before looking at its arithmetic) | **203,780 / 203,780 ACCEPTED** |

`bfp2gordan.py` performs the purely nominal field rename between the two
schemas (`gordan.gordan_record_bfp` is the same map in reverse); no
arithmetic is recomputed or trusted in the conversion. Logs in
`data/nonreal/checkcert_*.log` and `data/nonreal/fpcheck_*.log`.

So **every non-realizable class in the (4,9) catalogue demonstrably has a
biquadratic final polynomial**, checked twice, tonight. That is precisely
the half of the conjecture that the OPEN residue could not speak to.

**The 9,072,015 realization certificates: verified, all of them.**
`fastverify.py` streams the shards in place — no 4 GB copy — and recomputes
all 126 brackets of every matrix, requiring each to be nonzero and to match
the class's sign string.

| | |
|---|---|
| certificate records streamed | **9,276,454** (every record the sweep wrote) |
| REALIZABLE accepted | **9,072,015** |
| NON_REALIZABLE accepted | 203,780 — but see the note below |
| RESIDUE (carries no claim) | 659 |
| **REJECTED** | **0** |
| matrices routed to the unbounded-precision python-integer path | 1,665 |
| wall time | 565 s on three workers |

**The NON_REALIZABLE row of that table is not a third opinion.**
`fastverify.py` routes non-realizable records straight to
`checkcert.check_record` — it *is* `checkcert.py`, run again. The two
independent checks of the 203,780 refutations are the ones in the table
above (`checkcert.py`, and `fpcheck.py` via `bfp2gordan.py`). Where
`fastverify.py` contributes coverage that nothing else had is the
**REALIZABLE** row: 9,072,015 matrices, each with all 126 brackets
recomputed.

Speed is not bought with precision. `int64` is used only where the result is
*provably* exact, and the guard is checked per matrix rather than assumed:
for a 4x4 matrix with entries ≤ m the two-row Laplace expansion bounds every
intermediate by 4m⁴ and the determinant by 24m⁴, so m < 24,800 is safe in
int64 with room to spare; the 1,665 matrices that reach the threshold go
through a pure python-integer path with no bound at all. Nothing is skipped
and nothing is approximated.

`fastverify.py` rebuilds the colex order, the chi parsing and the
determinant from the definitions, and its self-test
(`data/fastverify_selftest.log`) checks it against `ai/omreal/checkcert.py`
directly: **agreement on 2,625 small-entry and 34 large-entry real
certificates, and 200 of 200 single-sign corruptions rejected.**

A redundant pass over the same records driving `checkcert.check_record`
directly (`verifyall.py`, eight workers) was started alongside and
**deliberately stopped before completion**: at ~8.8 ms per record it needed
about three more hours, and it is a belt-and-braces cross-check rather than
a load-bearing one, since the non-realizable half had already gone through
`checkcert.py` in full and `fastverify.py` is validated against `checkcert.py`
directly. **What it did complete: at least 1,600,000 records (200,000 per
worker x 8), 0 rejected**, logs in `data/verifyall_w*.log`. It is not
counted in any tally above; re-running it to completion is a matter of
`python verifyall.py --worker k --nworkers 8` and patience.

**The two halves compose, and the join is the whole point.** §6.2 verifies
each record's *matrix against the chi string that record carries*; §6
verifies each record's *chi string against the catalogue*, by re-encoding it
to the 128-bit key and matching: 9,276,454 records, 9,276,454 matched, **0
unmatched and 0 rows carrying two certificates**. Neither statement alone
says "every catalogue row has a verified certificate" — a verified matrix
attached to the wrong row, or two certificates on one row and none on
another, would satisfy one and not the other. Together they do say it,
because the matching is a bijection onto the rows it covers and the
remaining 141 + 659 rows are accounted for individually:

    9,072,015  sweep realizations, matrix verified, chi matched to a row
  +   203,780  sweep refutations, certificate verified, chi matched to a row
  +       141  reissued from Z.dat, verified, row named in the record
  +       659  decided here, verified, row named in the record
  = 9,276,595  = every row of the catalogue, each exactly once.

**So every one of the 9,276,595 classes in the (4,9) cell carries exactly
one certificate, that certificate was independently re-verified in this
session, and not one was rejected.**

---

## 7. Trust boundaries

Stated as what would have to be wrong.

**Unconditional.** A REALIZABLE verdict is an integer matrix whose 126
brackets are recomputed exactly by three checkers sharing no code with the
producer or with each other, using three different determinant algorithms.
For these 659 to be wrong, integer determinants would have to be wrong in
three independent implementations. Nothing about oriented matroid theory,
the mutation tree, Roudneff–Sturmfels or BFP completeness is load-bearing.

**Unconditional given Gordan's theorem (1873).** A NO_FINAL_POLYNOMIAL
witness is an integer vector satisfying an explicit integer inequality
system that the checkers rebuild from the definitions — `reverify.py`
rebuilt 3,507,840 of those inequalities from scratch tonight and tested
every one.

**Depends on the definition of "biquadratic".** "No BFP" here means "no
Gordan vector over the inequalities forced by the three-term
Grassmann–Plücker relations" — `bfp.py`'s support, and the support
`MINOR_THEORY.md`'s Proposition R and the sharpened conjecture are stated
against. The L1 witness covers a strictly wider family, so the statement
survives that particular widening.

**Depends on the catalogue, and the chain was checked** — array SHA-256
against the manifest, and every certificate's chirotope against the npz
decoded by hand, 800 / 800. Nothing here re-derives the catalogue itself.

**The refuted side is now this session's too.** All 203,780 biquadratic
final polynomials were re-checked tonight by `ai/omreal/checkcert.py` and,
after a field rename, by `fpcheck.py` — two implementations sharing no code,
using different determinant algorithms, the second additionally re-verifying
each named Grassmann–Plücker relation as a polynomial identity. Both accept
all 203,780 (§6.2).

**Soundness of the refuted side — no realizable class wrongly refuted —**
is a different claim, and it is not proved by checking the certificates: a
valid Gordan vector *is* a proof of non-realizability, so the only way a
realizable class could appear there is if the identity tables themselves
were wrong. That is what gate B2 tests (0 false positives on 80 certified
realizable classes, at two supports) and what `gplib.py`'s identity test
tests (5,544 relations × 60 random integer configurations, exact, 0
failures). It is strong evidence, not a proof over all 203,780.

**The 9,072,156 rows the sweep realized are now this session's too.** All
9,072,015 whose certificate the sweep wrote were re-checked by
`fastverify.py` and the 141 whose line was lost were reissued from `Z.dat`
and re-checked by three checkers; 0 rejected (§6.2). Everything else about
those rows — how they were found, the mutation tree, Roudneff–Sturmfels —
is irrelevant to their certificates, which stand or fall on 126 integer
determinants each. What is *not* re-derived here is the catalogue itself:
that a given key is a distinct G'-class, and that the 9,276,595 keys are
exactly the uniform rank-4 classes on nine elements, remains `ai/omgamma`'s
result, pinned by the manifest hash checked above.

**From representatives to oriented matroids.** What was verified is
9,276,595 catalogue *representatives*, one per G'-class (relabelling,
reorientation, global sign). The lift to "every uniform rank-4 oriented
matroid on nine elements" uses two invariances, both standard and both
already relied on elsewhere in this project: **realizability is
G'-invariant** — relabel or negate the columns of the matrix, or negate a
row for the global sign, and the transformed matrix realizes the
transformed chirotope, which is exactly the construction `neighbours.py`
performs and bracket-checks — and **existence of a biquadratic final
polynomial is G'-invariant**, `MINOR_THEORY.md` §5.1. So both the verdict
and the hypothesis of the conjecture are constant on a class, and verifying
one representative verifies the orbit. That the catalogue's 9,276,595 keys
really are exactly the G'-classes is `ai/omgamma`'s result, not re-derived
here (see the paragraph above).

**BFP completeness at (4,9) is not proved, and is not needed.** What this
run shows is that on this catalogue it never *bit*: every non-realizable
class does in fact have a biquadratic final polynomial, so the method was
complete *in practice* over the whole cell. Whether it is complete as a
theorem, at (4,9) or in general, is untouched.

**A note on file times.** `sweep_state/st.dat` and `Z.dat` carry an mtime of
2026-08-01 13:21 because they are memory-mapped and Windows does not update
mtime on mapped writes. Their *contents* are final (0 TODO), and §6's
independent reconciliation against the certificate shards confirms it.

**Adversarially re-reviewed, 2026-08-03.** A separate agent attacked both
the sweep tooling that produced these verdicts and this document's own
verification claims — full reports in `ai/omreal/REVIEW_SWEEP_TOOLING.md`
and `ai/omopen/REVIEW_FINAL_RESIDUE.md`. A sixth independent implementation
(sharing no code with anything in this project) re-derived every headline
number from the raw shard bytes and `st.dat`; 2,500 REALIZABLE and 5,400
NON_REALIZABLE certificates, plus all 141 backfilled rows, were re-checked
by fresh code with 0 rejections; a 28-sabotage battery was rejected 100% of
the time; the 659 RESIDUE certificates were independently confirmed to be
exactly `st.dat`'s 659 OPEN rows (a bijection nobody had checked explicitly
before). **Verdict: the whole-catalogue result stands.**

Three findings, none affecting any reported number: (1) a latent race in
how `sweep49.py`'s worker processes could in principle write to the same
certificate shard — zero observed damage, confirmed by a full corpus scan
finding 0 malformed lines and 0 duplicate chirotopes; (2) the exact
mechanism behind the 141 missing certificates — buffered JSONL writes
flushing less often than the durable `Z.dat`/`st.dat` memmap writes,
independently re-diagnosed and the repair independently re-confirmed
correct; (3) `certaudit.py` originally parsed shard lines by byte-offset
substring search rather than `json.loads`, which could in principle let a
corrupted record (not a missing one) pass its reconciliation count
unnoticed — demonstrated concretely with a constructed sabotage that
`certaudit.py` missed but `checkcert.py`/`fpcheck.py` caught. Fixed: it now
parses every line as JSON and raises on anything malformed rather than
silently miscounting it; the reconciliation numbers above are unchanged
under the fix (re-run and confirmed identical).

---

## 8. What this supports, and what is still open

**Strongest supported statement.**

> Of the **659** classes the (4,9) sweep left OPEN over the **complete**
> catalogue of 9,276,595 uniform rank-4 oriented matroids on nine elements,
> **all 659 are realizable**, each with an explicit integer 4x9 matrix
> verified by three checkers sharing no code, and each also carrying an
> exact certificate that it has no biquadratic final polynomial and no
> Gordan vector over the wider four- and five-term Plücker exchange support.
>
> The (4,9) cell therefore splits into **9,072,815 realizable** and
> **203,780 non-realizable** classes with **no residue** — and **every one
> of those 9,276,595 verdicts is backed by a certificate that was
> independently re-checked in this session, with zero rejections.**
>
> Consequently **no uniform rank-4 oriented matroid on nine elements is
> non-realizable without a biquadratic final polynomial**: every
> non-realizable class in the cell demonstrably has one.

Consequences, in decreasing strength.

1. **The (4,9) cell is closed.** The blank (4,9) row of
   Finschi–Fukuda–Moriyama gets a number and no asterisk. Every class is
   decided and every decision is a checkable certificate on disk.
2. **The candidate set for the sharpened conjecture is empty.** These 659
   were, by construction, the only classes in the catalogue that could have
   refuted it: undecided, and certified to have no biquadratic final
   polynomial. Prior support was 0 residue in 10,000 (`WALK_THEORY.md` §5),
   451 of 451 OPEN classes with all deletions realizable
   (`MINOR_THEORY.md` §4.3), and 126 of 126 emptied at the 26% mark. This
   empties the candidate set over the whole cell.
3. **At n = 9, rank 4, the conjecture becomes a finite verification — and it
   passes.** State the logic explicitly, because "survived" and "verified"
   are different claims and the second one has a dependency.

   A counterexample is a class that is *non-realizable* and has *no*
   biquadratic final polynomial. Partition the catalogue:

   | population | why it is not a counterexample | verified tonight |
   |---|---|---|
   | 203,780 refuted by the sweep | each carries a **valid BFP** | **203,780 / 203,780**, two checkers (§6.2) |
   | 659 left OPEN by the sweep | each carries an **integer realization** | **659 / 659**, three checkers |
   | 9,072,015 realized by the sweep, certificate on disk | each carries an **integer realization** | **9,072,015 / 9,072,015** (§6.2) |
   | 141 realized by the sweep, certificate line lost | reissued from `Z.dat` | **141 / 141**, three checkers (§6) |

   The four populations are disjoint and exhaust the catalogue, and **not
   one certificate was rejected**. So **no uniform rank-4 oriented matroid
   on nine elements is non-realizable without a biquadratic final
   polynomial.** The conjecture holds at n = 9, as a finite verification in
   which every step is a certificate that was re-checked.

   That the realizable side had to be checked at all is worth spelling out:
   a *bogus* realization certificate would be the only remaining way a
   counterexample could hide, because a class the sweep believes it has
   realized is never tested for a final polynomial. Checking the refuted
   side alone would have left that door open.

   None of this touches the conjecture as a general statement. At n ≥ 10 —
   where the smallest known BFP-resistant oriented matroids live — nothing
   here applies, and GPT-5.6's moduli-dimension heuristic
   (`CONSULT_GPT56.md`) puts the modal first rank-4 failure at n = 11.
4. **Difficulty is a property of searching, not of the matroid.** Median
   3.9 s to realize a class the sweep abandoned after its whole ladder;
   the hardest took 179 s and 16,289 refuted completion LPs. Replicated
   now at 8x the previous scale, and with the residue rate rising with
   tree depth rather than with anything intrinsic.
5. **A concrete recommendation for `sweep49.py`, unchanged and now better
   supported.** Gate A1 reproduces 40 of 40 REALIZABLE(repair) classes at a
   median of 0.34 s. Running weapon A as the repair ladder's last rung — or
   replacing `realize._cross_wall` with the completion LP — would very
   likely take the OPEN count to zero at source. With `exactlp` as the
   inner oracle it would do so without a numerical failure mode at all.

**Still open, and not attempted here.**

* **The mutation-graph component cut**, proposed by GPT-5.6 as a post-sweep
  cross-check (`CONSULT_GPT56.md` §1): since the realizable induced subgraph
  is connected (Roudneff–Sturmfels), the certified non-realizable set should
  be exactly the complement of a known realizable seed's component in
  G − B. This is a whole-catalogue consistency check of the final split that
  is independent of every certificate, and it is the natural next
  verification now that the split is final. It needs full mutation adjacency
  — ~9.07 million vertices × up to 126 candidate flips, each needing a
  validity test, a canonicalization and a catalogue lookup — which is a
  multi-hour build, not an add-on to tonight's run. `neighbours.py` now
  contains the per-class primitive it would need (validity test →
  `canon_batch` → key lookup → status), so the remaining work is scale, not
  method. **Recommended as the next job.**
* **Certificate cores** (`CONSULT_GPT56.md` §2) — reducing each Gordan
  certificate to an inclusion-minimal positive dependence and canonicalizing
  the partial signed pattern, so one core refutes many chirotopes. Now
  applicable to a *complete* set of 203,780 certificates.
* **Richter-Gebert's Theorem 5.1** and its claimed rank-4 generalization
  remain unchecked against the primary source; `LITERATURE.md`'s caveat
  stands. Note that consequence (3) above is exactly the corollary
  `CONSULT_GPT56.md` predicted: if every non-realizable (4,9) class has a
  BFP, no one-sided realizable mutation wall exists on nine elements.

---

## Appendix A — files

| file | what |
|---|---|
| `attack.py` | the resumable driver (unchanged) |
| `runshard.py` | **new** — shards `attack.decide` across workers with per-shard files and an idempotent merge |
| `exactgate.py` | **new** — weapon A with `exactlp.exact_feasible` as its oracle; big-integer bracket check; the non-realizable soundness control |
| `neighbours.py` | **new** — the mutation-neighbour source of `OPEN_ATTACK.md` §10.2, with the group element solved for over GF(2) rather than trusted |
| `probe_exact_vs_float.py` | **new** — float-vs-exact disagreement probe across three configuration regimes |
| `rowcheck.py` | **new** — ground-truth check that the completion rows are the right rows |
| `certaudit.py` | **new** — reconciles the sweep's certificate shards against `st.dat` |
| `verifyall.py` | **new** — streams every certificate the sweep wrote through `checkcert.check_record`, in parallel, without copying the 4 GB |
| `fastverify.py` | **new** — the same verification, batched in numpy, with a proved int64 safety bound (24·m⁴ < 2⁶³ for m < 24,800) and a python-integer path for every matrix that reaches it; ~70x faster, self-tested against `checkcert.py` |
| `bfp2gordan.py` | **new** — the nominal schema rename that lets `fpcheck.py` check the sweep's `bfp` certificates too |
| `backfill.py` | **new** — reissues the 141 lost certificates from `Z.dat` |
| `reverify.py` | **new** — a fourth, fully independent checker (stdlib, `Fraction` Gaussian elimination) |
| `finaltable.py` | **new** — the per-class table and summary numbers |
| `exactlp.py`, `gordan.py`, `gplib.py`, `fpoly.py`, `weaponA.py`, `catalog.py`, `validate.py`, `canaries.py`, `fpcheck.py` | unchanged from `OPEN_ATTACK.md` |
| `data/certs_realizable.jsonl` | **the 659 realization certificates — the result** |
| `data/certs_no_bfp.jsonl` | the exact "no final polynomial" witnesses, 659 classes × two family sets |
| `data/certs_backfill.jsonl` | the 141 reissued certificates |
| `data/final_outcomes.tsv`, `data/final_table.md` | per-class outcomes |
| `data/results.jsonl` | per-class outcome log; the resume key |
| `data/open_set.txt`, `data/enumerate_100pct.txt` | the final OPEN snapshot and the sweep state when it was taken |
| `data/open_set_126_snapshot.txt`, `data/enumerate_26pct.txt`, `data/results_126_snapshot.jsonl` | the previous session's snapshot, preserved |
| `data/certaudit.json`, `data/backfill.json` | catalogue certificate coverage |
| `data/fastverify.json`, `data/fastverify_selftest.log`, `data/fastverify/f*.json` | the full-catalogue re-verification and its self-test |
| `data/nonreal/checkcert_*.log`, `data/nonreal/fpcheck_*.log` | the 203,780 refutations, checked twice |
| `data/verifyall/`, `data/verifyall_w*.log` | the redundant `checkcert.py` pass over the same records |
| `data/reverify.json`, `data/rowcheck.json`, `data/probe_exact_vs_float.json`, `data/exactgate_selftest.log` | the new gates |
| `data/validation.json`, `data/canaries_result.json` | the standing gates, re-run tonight |
| `data/exactgate_*.jsonl` | the exact gate's records for row 3992924 |
| `data/omreal_state_snapshot.json` | file sizes, mtimes and `st.dat`'s SHA-256, for the read-only claim |

---

## Appendix B — per-class results

All 659 rows. Verdict REALIZABLE throughout; certificate in
`data/certs_realizable.jsonl`. `how` is which source produced the
eight-point configuration that completed. `s` is the deciding run's wall
time — for the 54 classes that needed a second pass it excludes the 60 s
they had already spent, and for row 3992924 the 60 s and 240 s before it.
The last column is the exact no-final-polynomial witness at level L0
(three-term relations only, i.e. "no biquadratic final polynomial") and at
level L1 (plus the four- and five-term exchange families). The `exact gate`
column is populated only for the one class that reached it.

| row | depth | verdict | how | s | max&#124;entry&#124; | no-FP witness (L0 / L1) | exact gate |
|---|---|---|---|---|---|---|---|
| 46731 | 21 | REALIZABLE | walk | 1.8 | 1024 | yes / yes | - |
| 69368 | 20 | REALIZABLE | walk | 16.6 | 64 | yes / yes | - |
| 69566 | 17 | REALIZABLE | walk | 16.2 | 256 | yes / yes | - |
| 69816 | 15 | REALIZABLE | walk | 1.6 | 262144 | yes / yes | - |
| 118764 | 18 | REALIZABLE | store_walk | 1.0 | 256 | yes / yes | - |
| 128257 | 18 | REALIZABLE | walk | 5.0 | 1024 | yes / yes | - |
| 129082 | 23 | REALIZABLE | walk | 15.0 | 1024 | yes / yes | - |
| 161446 | 17 | REALIZABLE | walk | 1.6 | 16384 | yes / yes | - |
| 176370 | 19 | REALIZABLE | walk | 2.4 | 1024 | yes / yes | - |
| 220350 | 18 | REALIZABLE | fresh | 1.6 | 1024 | yes / yes | - |
| 242592 | 20 | REALIZABLE | walk | 2.7 | 1024 | yes / yes | - |
| 254042 | 22 | REALIZABLE | walk | 7.2 | 16384 | yes / yes | - |
| 272814 | 19 | REALIZABLE | walk | 9.4 | 16384 | yes / yes | - |
| 274772 | 17 | REALIZABLE | walk | 2.8 | 64 | yes / yes | - |
| 282184 | 20 | REALIZABLE | walk | 4.0 | 256 | yes / yes | - |
| 303394 | 19 | REALIZABLE | walk | 32.7 | 8192 | yes / yes | - |
| 317216 | 26 | REALIZABLE | walk | 4.5 | 1024 | yes / yes | - |
| 319785 | 18 | REALIZABLE | store_walk | 0.9 | 1024 | yes / yes | - |
| 331960 | 19 | REALIZABLE | store_walk | 0.7 | 1024 | yes / yes | - |
| 338300 | 17 | REALIZABLE | walk | 23.3 | 1024 | yes / yes | - |
| 357940 | 19 | REALIZABLE | walk | 11.0 | 1024 | yes / yes | - |
| 362222 | 18 | REALIZABLE | walk | 6.5 | 1024 | yes / yes | - |
| 367890 | 19 | REALIZABLE | walk | 7.2 | 16384 | yes / yes | - |
| 375712 | 20 | REALIZABLE | walk | 29.4 | 1024 | yes / yes | - |
| 383472 | 15 | REALIZABLE | walk | 35.2 | 1024 | yes / yes | - |
| 461608 | 23 | REALIZABLE | walk | 2.6 | 1024 | yes / yes | - |
| 471533 | 21 | REALIZABLE | walk | 2.8 | 16384 | yes / yes | - |
| 479804 | 20 | REALIZABLE | walk | 1.4 | 64 | yes / yes | - |
| 482339 | 17 | REALIZABLE | fresh | 1.1 | 1024 | yes / yes | - |
| 541044 | 24 | REALIZABLE | walk | 17.0 | 16384 | yes / yes | - |
| 560157 | 15 | REALIZABLE | walk | 6.1 | 1024 | yes / yes | - |
| 563127 | 19 | REALIZABLE | walk | 9.2 | 1024 | yes / yes | - |
| 586623 | 16 | REALIZABLE | walk | 4.6 | 8192 | yes / yes | - |
| 595394 | 15 | REALIZABLE | walk | 8.9 | 1024 | yes / yes | - |
| 604909 | 18 | REALIZABLE | walk | 2.5 | 262144 | yes / yes | - |
| 612224 | 18 | REALIZABLE | walk | 29.9 | 256 | yes / yes | - |
| 635791 | 24 | REALIZABLE | walk | 38.6 | 1024 | yes / yes | - |
| 638582 | 20 | REALIZABLE | walk | 2.7 | 1024 | yes / yes | - |
| 699735 | 20 | REALIZABLE | walk | 3.2 | 1024 | yes / yes | - |
| 705805 | 18 | REALIZABLE | walk | 1.5 | 512 | yes / yes | - |
| 710482 | 17 | REALIZABLE | walk | 3.4 | 16384 | yes / yes | - |
| 711053 | 17 | REALIZABLE | walk | 2.5 | 512 | yes / yes | - |
| 746892 | 18 | REALIZABLE | walk | 1.5 | 16384 | yes / yes | - |
| 761880 | 18 | REALIZABLE | walk | 5.4 | 1024 | yes / yes | - |
| 771844 | 18 | REALIZABLE | walk | 2.1 | 131072 | yes / yes | - |
| 777026 | 21 | REALIZABLE | walk | 20.0 | 1024 | yes / yes | - |
| 785797 | 15 | REALIZABLE | walk | 30.5 | 1024 | yes / yes | - |
| 801301 | 21 | REALIZABLE | walk | 20.8 | 64 | yes / yes | - |
| 802666 | 19 | REALIZABLE | fresh | 2.0 | 1024 | yes / yes | - |
| 828175 | 21 | REALIZABLE | store | 1.2 | 1024 | yes / yes | - |
| 849936 | 23 | REALIZABLE | walk | 2.7 | 1024 | yes / yes | - |
| 865559 | 15 | REALIZABLE | walk | 1.9 | 1024 | yes / yes | - |
| 902448 | 16 | REALIZABLE | walk | 1.1 | 64 | yes / yes | - |
| 910517 | 17 | REALIZABLE | walk | 1.1 | 1024 | yes / yes | - |
| 922831 | 21 | REALIZABLE | walk | 2.4 | 1024 | yes / yes | - |
| 950263 | 15 | REALIZABLE | walk | 3.9 | 16384 | yes / yes | - |
| 954944 | 19 | REALIZABLE | walk | 5.1 | 16384 | yes / yes | - |
| 977620 | 18 | REALIZABLE | walk | 4.1 | 16384 | yes / yes | - |
| 991473 | 21 | REALIZABLE | walk | 4.3 | 1024 | yes / yes | - |
| 998077 | 19 | REALIZABLE | walk | 5.7 | 1024 | yes / yes | - |
| 998211 | 21 | REALIZABLE | store | 1.1 | 256 | yes / yes | - |
| 1004217 | 18 | REALIZABLE | walk | 1.5 | 1024 | yes / yes | - |
| 1005826 | 21 | REALIZABLE | walk | 20.3 | 16384 | yes / yes | - |
| 1037864 | 21 | REALIZABLE | walk | 2.1 | 1024 | yes / yes | - |
| 1041960 | 19 | REALIZABLE | walk | 44.6 | 1024 | yes / yes | - |
| 1084812 | 24 | REALIZABLE | walk | 34.2 | 1024 | yes / yes | - |
| 1097568 | 18 | REALIZABLE | walk | 5.3 | 16384 | yes / yes | - |
| 1102214 | 20 | REALIZABLE | store_walk | 1.2 | 64 | yes / yes | - |
| 1114374 | 19 | REALIZABLE | walk | 2.4 | 1024 | yes / yes | - |
| 1132081 | 19 | REALIZABLE | store_walk | 1.6 | 64 | yes / yes | - |
| 1152258 | 18 | REALIZABLE | walk | 22.2 | 16384 | yes / yes | - |
| 1164918 | 16 | REALIZABLE | walk | 0.9 | 64 | yes / yes | - |
| 1170862 | 19 | REALIZABLE | walk | 2.9 | 64 | yes / yes | - |
| 1182996 | 22 | REALIZABLE | walk | 6.5 | 1024 | yes / yes | - |
| 1200032 | 15 | REALIZABLE | walk | 8.7 | 16384 | yes / yes | - |
| 1202926 | 21 | REALIZABLE | walk | 5.9 | 16384 | yes / yes | - |
| 1207981 | 19 | REALIZABLE | fresh | 1.0 | 16384 | yes / yes | - |
| 1208882 | 19 | REALIZABLE | walk | 4.4 | 64 | yes / yes | - |
| 1213079 | 16 | REALIZABLE | walk | 11.7 | 262144 | yes / yes | - |
| 1242292 | 22 | REALIZABLE | walk | 1.9 | 262144 | yes / yes | - |
| 1246075 | 18 | REALIZABLE | walk | 23.7 | 1024 | yes / yes | - |
| 1260426 | 18 | REALIZABLE | walk | 32.7 | 16384 | yes / yes | - |
| 1278069 | 15 | REALIZABLE | walk | 14.3 | 16384 | yes / yes | - |
| 1303828 | 21 | REALIZABLE | walk | 16.7 | 16384 | yes / yes | - |
| 1321961 | 16 | REALIZABLE | store | 0.8 | 64 | yes / yes | - |
| 1329822 | 20 | REALIZABLE | walk | 92.4 | 1024 | yes / yes | - |
| 1338010 | 22 | REALIZABLE | walk | 17.0 | 16384 | yes / yes | - |
| 1341479 | 21 | REALIZABLE | walk | 29.7 | 8192 | yes / yes | - |
| 1345534 | 17 | REALIZABLE | fresh | 1.0 | 16384 | yes / yes | - |
| 1351088 | 19 | REALIZABLE | store_walk | 1.9 | 8192 | yes / yes | - |
| 1372417 | 19 | REALIZABLE | store | 1.7 | 1024 | yes / yes | - |
| 1407171 | 16 | REALIZABLE | walk | 20.3 | 1024 | yes / yes | - |
| 1419655 | 17 | REALIZABLE | walk | 4.6 | 16384 | yes / yes | - |
| 1428097 | 23 | REALIZABLE | walk | 35.8 | 1024 | yes / yes | - |
| 1430412 | 21 | REALIZABLE | walk | 8.5 | 1024 | yes / yes | - |
| 1430874 | 20 | REALIZABLE | store | 0.9 | 4096 | yes / yes | - |
| 1437575 | 20 | REALIZABLE | walk | 7.3 | 1024 | yes / yes | - |
| 1481122 | 23 | REALIZABLE | store_walk | 1.0 | 64 | yes / yes | - |
| 1482377 | 18 | REALIZABLE | walk | 48.5 | 1024 | yes / yes | - |
| 1485575 | 21 | REALIZABLE | walk | 2.1 | 1024 | yes / yes | - |
| 1486611 | 15 | REALIZABLE | walk | 1.0 | 256 | yes / yes | - |
| 1504477 | 17 | REALIZABLE | walk | 1.2 | 1024 | yes / yes | - |
| 1510131 | 15 | REALIZABLE | walk | 24.8 | 1024 | yes / yes | - |
| 1514892 | 16 | REALIZABLE | walk | 4.1 | 1024 | yes / yes | - |
| 1518293 | 17 | REALIZABLE | walk | 16.5 | 1024 | yes / yes | - |
| 1544603 | 22 | REALIZABLE | walk | 10.5 | 1024 | yes / yes | - |
| 1555339 | 18 | REALIZABLE | walk | 3.1 | 16384 | yes / yes | - |
| 1577209 | 20 | REALIZABLE | store | 1.0 | 1024 | yes / yes | - |
| 1592644 | 21 | REALIZABLE | walk | 1.7 | 64 | yes / yes | - |
| 1650169 | 19 | REALIZABLE | walk | 3.1 | 16384 | yes / yes | - |
| 1674635 | 20 | REALIZABLE | walk | 2.2 | 16384 | yes / yes | - |
| 1684953 | 17 | REALIZABLE | walk | 4.0 | 262144 | yes / yes | - |
| 1697361 | 21 | REALIZABLE | walk | 13.2 | 1024 | yes / yes | - |
| 1702648 | 18 | REALIZABLE | fresh | 1.3 | 1024 | yes / yes | - |
| 1705788 | 19 | REALIZABLE | walk | 3.5 | 1024 | yes / yes | - |
| 1711280 | 19 | REALIZABLE | walk | 8.1 | 1024 | yes / yes | - |
| 1761704 | 21 | REALIZABLE | walk | 50.2 | 16384 | yes / yes | - |
| 1766203 | 18 | REALIZABLE | walk | 4.6 | 16384 | yes / yes | - |
| 1769360 | 16 | REALIZABLE | walk | 21.5 | 1024 | yes / yes | - |
| 1771198 | 19 | REALIZABLE | walk | 9.3 | 1024 | yes / yes | - |
| 1774140 | 17 | REALIZABLE | walk | 26.2 | 16384 | yes / yes | - |
| 1790566 | 21 | REALIZABLE | walk | 3.0 | 64 | yes / yes | - |
| 1791359 | 20 | REALIZABLE | walk | 2.5 | 16384 | yes / yes | - |
| 1805687 | 21 | REALIZABLE | walk | 1.9 | 1024 | yes / yes | - |
| 1841418 | 19 | REALIZABLE | walk | 18.3 | 1024 | yes / yes | - |
| 1857375 | 20 | REALIZABLE | walk | 25.9 | 16384 | yes / yes | - |
| 1862494 | 17 | REALIZABLE | walk | 3.3 | 64 | yes / yes | - |
| 1865511 | 16 | REALIZABLE | walk | 21.2 | 1024 | yes / yes | - |
| 1872381 | 18 | REALIZABLE | walk | 3.1 | 16384 | yes / yes | - |
| 1875632 | 24 | REALIZABLE | walk | 29.5 | 16384 | yes / yes | - |
| 1886053 | 22 | REALIZABLE | walk | 5.3 | 1024 | yes / yes | - |
| 1891741 | 21 | REALIZABLE | walk | 12.7 | 1024 | yes / yes | - |
| 1909005 | 20 | REALIZABLE | walk | 3.2 | 1024 | yes / yes | - |
| 1922968 | 21 | REALIZABLE | walk | 4.4 | 1024 | yes / yes | - |
| 1923081 | 18 | REALIZABLE | walk | 2.9 | 256 | yes / yes | - |
| 1934773 | 21 | REALIZABLE | walk | 1.5 | 1024 | yes / yes | - |
| 1940365 | 19 | REALIZABLE | walk | 35.2 | 1024 | yes / yes | - |
| 1963286 | 21 | REALIZABLE | walk | 3.2 | 16384 | yes / yes | - |
| 1969147 | 20 | REALIZABLE | walk | 1.9 | 1024 | yes / yes | - |
| 1983462 | 19 | REALIZABLE | walk | 10.4 | 1024 | yes / yes | - |
| 1988690 | 17 | REALIZABLE | walk | 15.4 | 1024 | yes / yes | - |
| 1989477 | 16 | REALIZABLE | walk | 19.7 | 64 | yes / yes | - |
| 2008328 | 19 | REALIZABLE | walk | 2.2 | 1024 | yes / yes | - |
| 2016110 | 17 | REALIZABLE | walk | 5.6 | 8192 | yes / yes | - |
| 2069473 | 18 | REALIZABLE | walk | 7.5 | 16384 | yes / yes | - |
| 2075101 | 20 | REALIZABLE | walk | 31.1 | 512 | yes / yes | - |
| 2078423 | 20 | REALIZABLE | walk | 1.6 | 1024 | yes / yes | - |
| 2081164 | 20 | REALIZABLE | store_walk | 1.5 | 16384 | yes / yes | - |
| 2081170 | 18 | REALIZABLE | walk | 2.9 | 1024 | yes / yes | - |
| 2091742 | 19 | REALIZABLE | walk | 43.2 | 16384 | yes / yes | - |
| 2126752 | 14 | REALIZABLE | store | 0.6 | 1024 | yes / yes | - |
| 2141986 | 19 | REALIZABLE | walk | 18.0 | 1024 | yes / yes | - |
| 2155979 | 19 | REALIZABLE | walk | 4.8 | 16384 | yes / yes | - |
| 2164183 | 19 | REALIZABLE | walk | 3.1 | 16384 | yes / yes | - |
| 2183269 | 18 | REALIZABLE | fresh | 1.3 | 1024 | yes / yes | - |
| 2188427 | 20 | REALIZABLE | walk | 9.0 | 1024 | yes / yes | - |
| 2204680 | 20 | REALIZABLE | walk | 2.3 | 1024 | yes / yes | - |
| 2204739 | 18 | REALIZABLE | store | 1.2 | 256 | yes / yes | - |
| 2218209 | 17 | REALIZABLE | walk | 3.9 | 1024 | yes / yes | - |
| 2239264 | 19 | REALIZABLE | walk | 14.1 | 1024 | yes / yes | - |
| 2246262 | 14 | REALIZABLE | store_walk | 0.2 | 1024 | yes / yes | - |
| 2282929 | 19 | REALIZABLE | walk | 9.8 | 1024 | yes / yes | - |
| 2297105 | 18 | REALIZABLE | fresh | 2.2 | 16384 | yes / yes | - |
| 2308629 | 20 | REALIZABLE | walk | 3.6 | 1024 | yes / yes | - |
| 2334901 | 19 | REALIZABLE | walk | 3.3 | 1024 | yes / yes | - |
| 2337131 | 19 | REALIZABLE | walk | 11.4 | 1024 | yes / yes | - |
| 2367423 | 19 | REALIZABLE | walk | 4.9 | 1024 | yes / yes | - |
| 2383063 | 18 | REALIZABLE | store | 1.0 | 4096 | yes / yes | - |
| 2400626 | 18 | REALIZABLE | walk | 178.7 | 1024 | yes / yes | - |
| 2403470 | 18 | REALIZABLE | store_walk | 1.2 | 1024 | yes / yes | - |
| 2422219 | 17 | REALIZABLE | walk | 37.0 | 1024 | yes / yes | - |
| 2432532 | 19 | REALIZABLE | fresh | 2.8 | 1024 | yes / yes | - |
| 2444483 | 17 | REALIZABLE | walk | 11.0 | 16384 | yes / yes | - |
| 2472030 | 16 | REALIZABLE | store_walk | 0.4 | 1024 | yes / yes | - |
| 2533674 | 21 | REALIZABLE | walk | 9.0 | 1024 | yes / yes | - |
| 2540731 | 17 | REALIZABLE | walk | 2.1 | 1024 | yes / yes | - |
| 2569376 | 22 | REALIZABLE | walk | 5.6 | 1024 | yes / yes | - |
| 2579493 | 20 | REALIZABLE | walk | 3.0 | 1024 | yes / yes | - |
| 2595537 | 17 | REALIZABLE | walk | 9.0 | 1024 | yes / yes | - |
| 2605311 | 19 | REALIZABLE | walk | 2.2 | 16384 | yes / yes | - |
| 2610382 | 22 | REALIZABLE | store_walk | 1.2 | 16384 | yes / yes | - |
| 2614882 | 21 | REALIZABLE | walk | 3.3 | 16384 | yes / yes | - |
| 2616175 | 17 | REALIZABLE | walk | 2.2 | 2048 | yes / yes | - |
| 2621036 | 20 | REALIZABLE | walk | 29.8 | 16384 | yes / yes | - |
| 2635483 | 15 | REALIZABLE | fresh | 0.2 | 512 | yes / yes | - |
| 2639833 | 21 | REALIZABLE | fresh | 1.9 | 1024 | yes / yes | - |
| 2654739 | 20 | REALIZABLE | store | 1.4 | 256 | yes / yes | - |
| 2661356 | 21 | REALIZABLE | walk | 19.7 | 1024 | yes / yes | - |
| 2664774 | 22 | REALIZABLE | walk | 2.3 | 1024 | yes / yes | - |
| 2672675 | 18 | REALIZABLE | walk | 3.6 | 16384 | yes / yes | - |
| 2706717 | 17 | REALIZABLE | walk | 3.9 | 16384 | yes / yes | - |
| 2717208 | 21 | REALIZABLE | walk | 5.5 | 1024 | yes / yes | - |
| 2717342 | 20 | REALIZABLE | store_walk | 1.2 | 64 | yes / yes | - |
| 2718178 | 19 | REALIZABLE | walk | 1.6 | 4096 | yes / yes | - |
| 2725178 | 23 | REALIZABLE | fresh | 2.0 | 1024 | yes / yes | - |
| 2750734 | 19 | REALIZABLE | walk | 6.5 | 1024 | yes / yes | - |
| 2765699 | 17 | REALIZABLE | store_walk | 1.1 | 131072 | yes / yes | - |
| 2781558 | 20 | REALIZABLE | walk | 3.5 | 262144 | yes / yes | - |
| 2795558 | 20 | REALIZABLE | walk | 5.9 | 8192 | yes / yes | - |
| 2797208 | 19 | REALIZABLE | walk | 8.8 | 64 | yes / yes | - |
| 2808879 | 19 | REALIZABLE | walk | 4.9 | 16384 | yes / yes | - |
| 2818124 | 18 | REALIZABLE | walk | 3.6 | 1024 | yes / yes | - |
| 2821417 | 20 | REALIZABLE | walk | 13.4 | 64 | yes / yes | - |
| 2830887 | 19 | REALIZABLE | store | 0.8 | 4096 | yes / yes | - |
| 2890345 | 18 | REALIZABLE | walk | 20.7 | 16384 | yes / yes | - |
| 2905158 | 18 | REALIZABLE | walk | 2.5 | 8192 | yes / yes | - |
| 2917082 | 23 | REALIZABLE | walk | 10.5 | 16384 | yes / yes | - |
| 2927497 | 16 | REALIZABLE | walk | 1.4 | 256 | yes / yes | - |
| 2955134 | 23 | REALIZABLE | walk | 2.4 | 16384 | yes / yes | - |
| 2963994 | 17 | REALIZABLE | walk | 6.7 | 1024 | yes / yes | - |
| 2971832 | 21 | REALIZABLE | store_walk | 1.2 | 256 | yes / yes | - |
| 2972286 | 16 | REALIZABLE | walk | 1.1 | 1024 | yes / yes | - |
| 3008848 | 19 | REALIZABLE | store_walk | 1.3 | 1024 | yes / yes | - |
| 3028937 | 19 | REALIZABLE | walk | 36.5 | 1024 | yes / yes | - |
| 3032526 | 20 | REALIZABLE | walk | 2.4 | 1024 | yes / yes | - |
| 3049200 | 19 | REALIZABLE | walk | 115.9 | 1024 | yes / yes | - |
| 3052236 | 20 | REALIZABLE | walk | 18.1 | 1024 | yes / yes | - |
| 3072854 | 20 | REALIZABLE | walk | 13.7 | 16384 | yes / yes | - |
| 3102244 | 21 | REALIZABLE | walk | 1.9 | 4096 | yes / yes | - |
| 3109487 | 20 | REALIZABLE | walk | 2.0 | 1024 | yes / yes | - |
| 3110852 | 18 | REALIZABLE | store_walk | 1.2 | 256 | yes / yes | - |
| 3133872 | 16 | REALIZABLE | walk | 45.3 | 16384 | yes / yes | - |
| 3144919 | 17 | REALIZABLE | walk | 2.5 | 1024 | yes / yes | - |
| 3145203 | 18 | REALIZABLE | walk | 4.5 | 16384 | yes / yes | - |
| 3169660 | 19 | REALIZABLE | walk | 92.5 | 1024 | yes / yes | - |
| 3172786 | 18 | REALIZABLE | walk | 23.6 | 16384 | yes / yes | - |
| 3180653 | 19 | REALIZABLE | walk | 5.6 | 16384 | yes / yes | - |
| 3191077 | 21 | REALIZABLE | walk | 4.0 | 8192 | yes / yes | - |
| 3193338 | 16 | REALIZABLE | store | 0.2 | 4096 | yes / yes | - |
| 3193344 | 19 | REALIZABLE | walk | 9.9 | 1024 | yes / yes | - |
| 3202535 | 16 | REALIZABLE | walk | 9.9 | 64 | yes / yes | - |
| 3242686 | 18 | REALIZABLE | walk | 43.2 | 8192 | yes / yes | - |
| 3258103 | 16 | REALIZABLE | fresh | 1.2 | 64 | yes / yes | - |
| 3271807 | 24 | REALIZABLE | walk | 3.7 | 16384 | yes / yes | - |
| 3281611 | 19 | REALIZABLE | walk | 4.4 | 1024 | yes / yes | - |
| 3281692 | 22 | REALIZABLE | walk | 32.2 | 1024 | yes / yes | - |
| 3300476 | 20 | REALIZABLE | walk | 1.3 | 1024 | yes / yes | - |
| 3309238 | 19 | REALIZABLE | walk | 20.6 | 16384 | yes / yes | - |
| 3311701 | 26 | REALIZABLE | walk | 15.1 | 1024 | yes / yes | - |
| 3329017 | 19 | REALIZABLE | store | 0.7 | 4096 | yes / yes | - |
| 3343276 | 17 | REALIZABLE | walk | 2.5 | 256 | yes / yes | - |
| 3355052 | 19 | REALIZABLE | walk | 1.9 | 1024 | yes / yes | - |
| 3375322 | 18 | REALIZABLE | walk | 42.4 | 1024 | yes / yes | - |
| 3380682 | 16 | REALIZABLE | walk | 15.1 | 1024 | yes / yes | - |
| 3388902 | 19 | REALIZABLE | walk | 1.9 | 512 | yes / yes | - |
| 3404375 | 21 | REALIZABLE | walk | 1.3 | 1024 | yes / yes | - |
| 3485456 | 20 | REALIZABLE | walk | 14.0 | 16384 | yes / yes | - |
| 3496132 | 19 | REALIZABLE | walk | 6.2 | 1024 | yes / yes | - |
| 3497798 | 19 | REALIZABLE | walk | 7.9 | 1024 | yes / yes | - |
| 3569788 | 24 | REALIZABLE | walk | 1.9 | 1024 | yes / yes | - |
| 3572151 | 15 | REALIZABLE | walk | 0.8 | 1024 | yes / yes | - |
| 3584761 | 18 | REALIZABLE | walk | 10.8 | 1024 | yes / yes | - |
| 3584854 | 19 | REALIZABLE | walk | 4.8 | 1024 | yes / yes | - |
| 3610937 | 19 | REALIZABLE | fresh | 2.3 | 512 | yes / yes | - |
| 3611074 | 18 | REALIZABLE | walk | 3.3 | 1024 | yes / yes | - |
| 3615914 | 19 | REALIZABLE | walk | 12.6 | 262144 | yes / yes | - |
| 3639895 | 18 | REALIZABLE | walk | 42.4 | 262144 | yes / yes | - |
| 3640543 | 21 | REALIZABLE | walk | 3.0 | 16384 | yes / yes | - |
| 3644142 | 19 | REALIZABLE | walk | 79.7 | 1024 | yes / yes | - |
| 3654633 | 18 | REALIZABLE | walk | 6.2 | 1024 | yes / yes | - |
| 3654683 | 21 | REALIZABLE | walk | 12.2 | 1024 | yes / yes | - |
| 3673625 | 18 | REALIZABLE | walk | 18.0 | 1024 | yes / yes | - |
| 3674773 | 17 | REALIZABLE | store_walk | 1.5 | 8192 | yes / yes | - |
| 3674842 | 22 | REALIZABLE | walk | 7.9 | 1024 | yes / yes | - |
| 3718175 | 16 | REALIZABLE | walk | 2.9 | 16384 | yes / yes | - |
| 3745519 | 15 | REALIZABLE | store | 0.6 | 4096 | yes / yes | - |
| 3753992 | 21 | REALIZABLE | walk | 17.6 | 8192 | yes / yes | - |
| 3758360 | 18 | REALIZABLE | walk | 21.4 | 1024 | yes / yes | - |
| 3773519 | 20 | REALIZABLE | walk | 1.6 | 1024 | yes / yes | - |
| 3793011 | 18 | REALIZABLE | walk | 1.8 | 262144 | yes / yes | - |
| 3797119 | 19 | REALIZABLE | walk | 4.1 | 1024 | yes / yes | - |
| 3816617 | 17 | REALIZABLE | walk | 20.3 | 1024 | yes / yes | - |
| 3820504 | 21 | REALIZABLE | walk | 20.6 | 1024 | yes / yes | - |
| 3820584 | 20 | REALIZABLE | walk | 12.1 | 1024 | yes / yes | - |
| 3840632 | 16 | REALIZABLE | walk | 2.7 | 1024 | yes / yes | - |
| 3842585 | 15 | REALIZABLE | walk | 1.3 | 1024 | yes / yes | - |
| 3843947 | 20 | REALIZABLE | walk | 24.8 | 512 | yes / yes | - |
| 3848412 | 18 | REALIZABLE | store | 1.3 | 256 | yes / yes | - |
| 3885899 | 16 | REALIZABLE | walk | 1.4 | 1024 | yes / yes | - |
| 3925297 | 18 | REALIZABLE | walk | 3.2 | 262144 | yes / yes | - |
| 3927725 | 22 | REALIZABLE | walk | 2.8 | 1024 | yes / yes | - |
| 3942006 | 19 | REALIZABLE | walk | 3.0 | 1024 | yes / yes | - |
| 3942144 | 18 | REALIZABLE | store_walk | 1.2 | 512 | yes / yes | - |
| 3951870 | 18 | REALIZABLE | walk | 21.3 | 1024 | yes / yes | - |
| 3956638 | 18 | REALIZABLE | walk | 8.9 | 1024 | yes / yes | - |
| 3969889 | 16 | REALIZABLE | walk | 2.0 | 16384 | yes / yes | - |
| 3992924 | 19 | REALIZABLE | walk | 161.8 | 16384 | yes / yes | 31542 LP, 31542 inf, 9/9 p |
| 4005296 | 17 | REALIZABLE | walk | 4.4 | 1024 | yes / yes | - |
| 4018483 | 20 | REALIZABLE | fresh | 40.4 | 512 | yes / yes | - |
| 4027379 | 21 | REALIZABLE | walk | 11.0 | 1024 | yes / yes | - |
| 4032009 | 19 | REALIZABLE | store | 1.4 | 512 | yes / yes | - |
| 4050361 | 18 | REALIZABLE | walk | 2.8 | 16384 | yes / yes | - |
| 4056527 | 19 | REALIZABLE | walk | 4.8 | 1024 | yes / yes | - |
| 4059162 | 24 | REALIZABLE | walk | 2.3 | 1024 | yes / yes | - |
| 4066535 | 16 | REALIZABLE | walk | 9.5 | 1024 | yes / yes | - |
| 4066558 | 18 | REALIZABLE | walk | 23.3 | 1024 | yes / yes | - |
| 4067790 | 23 | REALIZABLE | walk | 5.1 | 16384 | yes / yes | - |
| 4068824 | 18 | REALIZABLE | walk | 2.3 | 1024 | yes / yes | - |
| 4091957 | 19 | REALIZABLE | store | 1.3 | 32 | yes / yes | - |
| 4099514 | 15 | REALIZABLE | store | 0.6 | 4096 | yes / yes | - |
| 4107985 | 19 | REALIZABLE | walk | 3.9 | 1024 | yes / yes | - |
| 4125921 | 17 | REALIZABLE | walk | 3.4 | 1024 | yes / yes | - |
| 4126892 | 21 | REALIZABLE | walk | 8.6 | 1024 | yes / yes | - |
| 4133159 | 20 | REALIZABLE | walk | 44.2 | 1024 | yes / yes | - |
| 4164751 | 17 | REALIZABLE | walk | 11.6 | 16384 | yes / yes | - |
| 4166868 | 22 | REALIZABLE | fresh | 1.7 | 4096 | yes / yes | - |
| 4176085 | 18 | REALIZABLE | store_walk | 1.2 | 256 | yes / yes | - |
| 4212492 | 21 | REALIZABLE | walk | 8.4 | 16384 | yes / yes | - |
| 4215145 | 22 | REALIZABLE | walk | 3.7 | 1024 | yes / yes | - |
| 4216348 | 18 | REALIZABLE | walk | 15.3 | 16384 | yes / yes | - |
| 4218710 | 17 | REALIZABLE | walk | 3.2 | 1024 | yes / yes | - |
| 4242067 | 19 | REALIZABLE | walk | 2.9 | 1024 | yes / yes | - |
| 4252898 | 18 | REALIZABLE | walk | 1.6 | 1024 | yes / yes | - |
| 4266114 | 19 | REALIZABLE | walk | 1.9 | 16384 | yes / yes | - |
| 4289821 | 15 | REALIZABLE | walk | 3.9 | 1024 | yes / yes | - |
| 4290333 | 17 | REALIZABLE | walk | 3.6 | 1024 | yes / yes | - |
| 4298243 | 19 | REALIZABLE | store_walk | 1.5 | 64 | yes / yes | - |
| 4305048 | 19 | REALIZABLE | walk | 32.0 | 16384 | yes / yes | - |
| 4310721 | 17 | REALIZABLE | store_walk | 1.3 | 2048 | yes / yes | - |
| 4319814 | 21 | REALIZABLE | store | 1.8 | 4096 | yes / yes | - |
| 4334536 | 20 | REALIZABLE | walk | 35.7 | 1024 | yes / yes | - |
| 4357916 | 16 | REALIZABLE | walk | 1.0 | 1024 | yes / yes | - |
| 4364287 | 18 | REALIZABLE | walk | 1.5 | 1024 | yes / yes | - |
| 4373774 | 20 | REALIZABLE | walk | 8.8 | 1024 | yes / yes | - |
| 4405516 | 15 | REALIZABLE | walk | 5.2 | 1024 | yes / yes | - |
| 4451161 | 17 | REALIZABLE | walk | 25.6 | 1024 | yes / yes | - |
| 4454084 | 17 | REALIZABLE | walk | 2.0 | 1024 | yes / yes | - |
| 4456288 | 19 | REALIZABLE | walk | 46.6 | 1024 | yes / yes | - |
| 4468620 | 19 | REALIZABLE | store_walk | 1.0 | 256 | yes / yes | - |
| 4475757 | 18 | REALIZABLE | walk | 2.2 | 1024 | yes / yes | - |
| 4487690 | 16 | REALIZABLE | walk | 16.7 | 8192 | yes / yes | - |
| 4500573 | 15 | REALIZABLE | walk | 2.7 | 1024 | yes / yes | - |
| 4517357 | 19 | REALIZABLE | store_walk | 1.2 | 4096 | yes / yes | - |
| 4541944 | 18 | REALIZABLE | walk | 1.4 | 16384 | yes / yes | - |
| 4546369 | 16 | REALIZABLE | store_walk | 0.4 | 16384 | yes / yes | - |
| 4555132 | 17 | REALIZABLE | walk | 157.0 | 262144 | yes / yes | - |
| 4568826 | 20 | REALIZABLE | walk | 14.6 | 64 | yes / yes | - |
| 4570179 | 22 | REALIZABLE | walk | 2.5 | 16384 | yes / yes | - |
| 4603165 | 19 | REALIZABLE | walk | 1.5 | 16384 | yes / yes | - |
| 4638320 | 20 | REALIZABLE | walk | 7.8 | 1024 | yes / yes | - |
| 4655856 | 20 | REALIZABLE | walk | 17.9 | 1024 | yes / yes | - |
| 4656434 | 17 | REALIZABLE | walk | 6.0 | 1024 | yes / yes | - |
| 4660787 | 19 | REALIZABLE | walk | 21.1 | 16384 | yes / yes | - |
| 4699676 | 20 | REALIZABLE | walk | 4.7 | 1024 | yes / yes | - |
| 4748789 | 15 | REALIZABLE | store_walk | 0.3 | 4096 | yes / yes | - |
| 4764650 | 20 | REALIZABLE | walk | 6.5 | 256 | yes / yes | - |
| 4769844 | 17 | REALIZABLE | walk | 2.7 | 1024 | yes / yes | - |
| 4779869 | 18 | REALIZABLE | store_walk | 3.3 | 16384 | yes / yes | - |
| 4781467 | 19 | REALIZABLE | walk | 9.0 | 1024 | yes / yes | - |
| 4804428 | 22 | REALIZABLE | fresh | 1.4 | 512 | yes / yes | - |
| 4811069 | 19 | REALIZABLE | walk | 1.4 | 262144 | yes / yes | - |
| 4824476 | 23 | REALIZABLE | walk | 34.0 | 1024 | yes / yes | - |
| 4829527 | 19 | REALIZABLE | fresh | 1.3 | 16384 | yes / yes | - |
| 4829901 | 20 | REALIZABLE | walk | 4.6 | 1024 | yes / yes | - |
| 4836120 | 17 | REALIZABLE | walk | 2.5 | 16384 | yes / yes | - |
| 4857807 | 20 | REALIZABLE | walk | 18.3 | 16384 | yes / yes | - |
| 4869075 | 19 | REALIZABLE | walk | 11.4 | 16384 | yes / yes | - |
| 4869658 | 22 | REALIZABLE | walk | 6.9 | 1024 | yes / yes | - |
| 4869659 | 21 | REALIZABLE | walk | 1.2 | 1024 | yes / yes | - |
| 4873812 | 18 | REALIZABLE | walk | 4.8 | 1024 | yes / yes | - |
| 4979988 | 20 | REALIZABLE | store_walk | 1.2 | 16384 | yes / yes | - |
| 4993531 | 15 | REALIZABLE | walk | 6.4 | 16384 | yes / yes | - |
| 5000657 | 17 | REALIZABLE | walk | 1.7 | 262144 | yes / yes | - |
| 5026440 | 19 | REALIZABLE | walk | 25.3 | 16384 | yes / yes | - |
| 5026671 | 18 | REALIZABLE | walk | 2.7 | 1024 | yes / yes | - |
| 5026863 | 17 | REALIZABLE | walk | 1.8 | 16384 | yes / yes | - |
| 5057183 | 23 | REALIZABLE | fresh | 1.9 | 1024 | yes / yes | - |
| 5062436 | 15 | REALIZABLE | store_walk | 0.6 | 1024 | yes / yes | - |
| 5083477 | 19 | REALIZABLE | walk | 8.1 | 1024 | yes / yes | - |
| 5100633 | 16 | REALIZABLE | walk | 4.5 | 8192 | yes / yes | - |
| 5101034 | 19 | REALIZABLE | walk | 10.0 | 1024 | yes / yes | - |
| 5115025 | 21 | REALIZABLE | walk | 8.7 | 16384 | yes / yes | - |
| 5159768 | 16 | REALIZABLE | walk | 1.4 | 1024 | yes / yes | - |
| 5178084 | 17 | REALIZABLE | store_walk | 3.0 | 1024 | yes / yes | - |
| 5193545 | 16 | REALIZABLE | walk | 5.0 | 64 | yes / yes | - |
| 5236613 | 19 | REALIZABLE | walk | 41.3 | 1024 | yes / yes | - |
| 5246735 | 18 | REALIZABLE | walk | 2.2 | 16384 | yes / yes | - |
| 5253037 | 18 | REALIZABLE | walk | 30.2 | 1024 | yes / yes | - |
| 5288949 | 19 | REALIZABLE | walk | 28.8 | 1024 | yes / yes | - |
| 5298491 | 16 | REALIZABLE | walk | 2.8 | 1024 | yes / yes | - |
| 5301846 | 19 | REALIZABLE | walk | 3.1 | 1024 | yes / yes | - |
| 5307915 | 17 | REALIZABLE | store_walk | 1.2 | 64 | yes / yes | - |
| 5312454 | 17 | REALIZABLE | walk | 16.8 | 1024 | yes / yes | - |
| 5324328 | 17 | REALIZABLE | store | 0.9 | 256 | yes / yes | - |
| 5329825 | 20 | REALIZABLE | walk | 3.0 | 1024 | yes / yes | - |
| 5329996 | 18 | REALIZABLE | walk | 5.0 | 1024 | yes / yes | - |
| 5331146 | 17 | REALIZABLE | store_walk | 0.9 | 16384 | yes / yes | - |
| 5356492 | 21 | REALIZABLE | walk | 8.8 | 16384 | yes / yes | - |
| 5398419 | 17 | REALIZABLE | walk | 29.1 | 64 | yes / yes | - |
| 5428019 | 17 | REALIZABLE | walk | 1.8 | 1024 | yes / yes | - |
| 5454090 | 19 | REALIZABLE | walk | 30.2 | 16384 | yes / yes | - |
| 5459000 | 17 | REALIZABLE | walk | 1.8 | 1024 | yes / yes | - |
| 5471051 | 21 | REALIZABLE | walk | 8.3 | 262144 | yes / yes | - |
| 5493753 | 17 | REALIZABLE | walk | 2.2 | 1024 | yes / yes | - |
| 5498207 | 22 | REALIZABLE | walk | 3.3 | 262144 | yes / yes | - |
| 5500905 | 21 | REALIZABLE | fresh | 1.6 | 1024 | yes / yes | - |
| 5513785 | 21 | REALIZABLE | walk | 7.4 | 1024 | yes / yes | - |
| 5514695 | 14 | REALIZABLE | walk | 2.7 | 1024 | yes / yes | - |
| 5515844 | 18 | REALIZABLE | store_walk | 1.0 | 64 | yes / yes | - |
| 5535032 | 20 | REALIZABLE | walk | 2.6 | 1024 | yes / yes | - |
| 5593952 | 17 | REALIZABLE | walk | 2.5 | 64 | yes / yes | - |
| 5600139 | 20 | REALIZABLE | walk | 1.7 | 64 | yes / yes | - |
| 5600178 | 19 | REALIZABLE | walk | 2.7 | 1024 | yes / yes | - |
| 5616046 | 16 | REALIZABLE | walk | 28.6 | 131072 | yes / yes | - |
| 5626380 | 21 | REALIZABLE | walk | 17.0 | 1024 | yes / yes | - |
| 5643179 | 19 | REALIZABLE | walk | 25.9 | 262144 | yes / yes | - |
| 5655604 | 18 | REALIZABLE | store | 0.8 | 256 | yes / yes | - |
| 5656956 | 25 | REALIZABLE | walk | 3.7 | 1024 | yes / yes | - |
| 5664182 | 20 | REALIZABLE | walk | 4.3 | 512 | yes / yes | - |
| 5671004 | 20 | REALIZABLE | walk | 21.6 | 1024 | yes / yes | - |
| 5698728 | 19 | REALIZABLE | fresh | 2.1 | 1024 | yes / yes | - |
| 5723047 | 16 | REALIZABLE | store_walk | 1.9 | 16384 | yes / yes | - |
| 5749535 | 16 | REALIZABLE | walk | 3.4 | 262144 | yes / yes | - |
| 5754575 | 18 | REALIZABLE | walk | 31.3 | 4096 | yes / yes | - |
| 5806888 | 18 | REALIZABLE | fresh | 2.1 | 1024 | yes / yes | - |
| 5825745 | 19 | REALIZABLE | store_walk | 1.2 | 1024 | yes / yes | - |
| 5833118 | 18 | REALIZABLE | walk | 1.4 | 16384 | yes / yes | - |
| 5843499 | 17 | REALIZABLE | walk | 1.5 | 1024 | yes / yes | - |
| 5862420 | 22 | REALIZABLE | walk | 18.6 | 1024 | yes / yes | - |
| 5866617 | 20 | REALIZABLE | walk | 20.7 | 1024 | yes / yes | - |
| 5882647 | 17 | REALIZABLE | walk | 48.3 | 1024 | yes / yes | - |
| 5904286 | 19 | REALIZABLE | walk | 7.6 | 16384 | yes / yes | - |
| 5928991 | 18 | REALIZABLE | walk | 4.2 | 512 | yes / yes | - |
| 5959805 | 19 | REALIZABLE | walk | 23.3 | 1024 | yes / yes | - |
| 5964604 | 19 | REALIZABLE | walk | 7.4 | 1024 | yes / yes | - |
| 5988663 | 17 | REALIZABLE | store_walk | 1.1 | 1024 | yes / yes | - |
| 6017490 | 17 | REALIZABLE | store_walk | 1.3 | 16384 | yes / yes | - |
| 6030645 | 17 | REALIZABLE | walk | 2.4 | 1024 | yes / yes | - |
| 6039871 | 18 | REALIZABLE | walk | 5.0 | 16384 | yes / yes | - |
| 6046137 | 19 | REALIZABLE | store_walk | 1.5 | 1024 | yes / yes | - |
| 6058672 | 21 | REALIZABLE | walk | 7.2 | 1024 | yes / yes | - |
| 6059982 | 20 | REALIZABLE | walk | 8.2 | 1024 | yes / yes | - |
| 6061266 | 20 | REALIZABLE | walk | 23.1 | 16384 | yes / yes | - |
| 6063809 | 21 | REALIZABLE | walk | 48.8 | 16384 | yes / yes | - |
| 6069948 | 19 | REALIZABLE | store_walk | 1.1 | 64 | yes / yes | - |
| 6080132 | 16 | REALIZABLE | walk | 9.3 | 64 | yes / yes | - |
| 6110040 | 19 | REALIZABLE | walk | 8.7 | 1024 | yes / yes | - |
| 6126692 | 22 | REALIZABLE | fresh | 1.7 | 64 | yes / yes | - |
| 6128130 | 20 | REALIZABLE | walk | 5.0 | 262144 | yes / yes | - |
| 6159573 | 21 | REALIZABLE | walk | 2.0 | 1024 | yes / yes | - |
| 6169872 | 15 | REALIZABLE | walk | 0.7 | 64 | yes / yes | - |
| 6173401 | 21 | REALIZABLE | walk | 13.5 | 16384 | yes / yes | - |
| 6180535 | 18 | REALIZABLE | walk | 13.8 | 16384 | yes / yes | - |
| 6181489 | 21 | REALIZABLE | walk | 2.4 | 16384 | yes / yes | - |
| 6198185 | 20 | REALIZABLE | store_walk | 1.3 | 4096 | yes / yes | - |
| 6216161 | 17 | REALIZABLE | walk | 1.8 | 1024 | yes / yes | - |
| 6232905 | 20 | REALIZABLE | fresh | 3.7 | 32 | yes / yes | - |
| 6241133 | 20 | REALIZABLE | walk | 1.0 | 1024 | yes / yes | - |
| 6263337 | 17 | REALIZABLE | fresh | 1.8 | 64 | yes / yes | - |
| 6271695 | 20 | REALIZABLE | walk | 6.5 | 1024 | yes / yes | - |
| 6297571 | 19 | REALIZABLE | walk | 10.9 | 16384 | yes / yes | - |
| 6312306 | 16 | REALIZABLE | walk | 1.6 | 512 | yes / yes | - |
| 6365428 | 20 | REALIZABLE | walk | 7.4 | 16384 | yes / yes | - |
| 6377516 | 17 | REALIZABLE | walk | 51.8 | 1024 | yes / yes | - |
| 6389945 | 17 | REALIZABLE | fresh | 2.3 | 64 | yes / yes | - |
| 6401704 | 18 | REALIZABLE | walk | 4.6 | 1024 | yes / yes | - |
| 6418717 | 19 | REALIZABLE | store_walk | 2.9 | 1024 | yes / yes | - |
| 6441311 | 18 | REALIZABLE | walk | 6.1 | 1024 | yes / yes | - |
| 6455926 | 18 | REALIZABLE | walk | 9.0 | 262144 | yes / yes | - |
| 6457287 | 16 | REALIZABLE | walk | 9.7 | 1024 | yes / yes | - |
| 6494535 | 17 | REALIZABLE | walk | 3.1 | 16384 | yes / yes | - |
| 6501049 | 17 | REALIZABLE | walk | 48.0 | 1024 | yes / yes | - |
| 6509329 | 19 | REALIZABLE | store_walk | 1.3 | 1024 | yes / yes | - |
| 6511615 | 22 | REALIZABLE | store | 1.0 | 256 | yes / yes | - |
| 6543930 | 19 | REALIZABLE | store | 0.9 | 256 | yes / yes | - |
| 6559976 | 16 | REALIZABLE | store_walk | 0.3 | 256 | yes / yes | - |
| 6586361 | 20 | REALIZABLE | store | 1.2 | 256 | yes / yes | - |
| 6627291 | 17 | REALIZABLE | store_walk | 1.2 | 1024 | yes / yes | - |
| 6627394 | 18 | REALIZABLE | walk | 6.3 | 1024 | yes / yes | - |
| 6633202 | 20 | REALIZABLE | walk | 13.2 | 1024 | yes / yes | - |
| 6637551 | 18 | REALIZABLE | walk | 1.8 | 512 | yes / yes | - |
| 6660961 | 19 | REALIZABLE | walk | 2.5 | 1024 | yes / yes | - |
| 6695429 | 16 | REALIZABLE | store_walk | 0.5 | 1024 | yes / yes | - |
| 6704386 | 20 | REALIZABLE | walk | 23.2 | 1024 | yes / yes | - |
| 6712784 | 20 | REALIZABLE | walk | 10.4 | 16384 | yes / yes | - |
| 6714423 | 18 | REALIZABLE | walk | 26.7 | 1024 | yes / yes | - |
| 6734990 | 21 | REALIZABLE | walk | 35.9 | 16384 | yes / yes | - |
| 6740955 | 18 | REALIZABLE | walk | 5.2 | 16384 | yes / yes | - |
| 6755885 | 17 | REALIZABLE | walk | 13.1 | 1024 | yes / yes | - |
| 6768412 | 20 | REALIZABLE | walk | 28.7 | 1024 | yes / yes | - |
| 6771198 | 19 | REALIZABLE | walk | 3.2 | 16384 | yes / yes | - |
| 6786910 | 18 | REALIZABLE | store | 1.1 | 256 | yes / yes | - |
| 6794284 | 18 | REALIZABLE | walk | 5.2 | 64 | yes / yes | - |
| 6795529 | 16 | REALIZABLE | walk | 0.9 | 16384 | yes / yes | - |
| 6797578 | 18 | REALIZABLE | fresh | 1.5 | 1024 | yes / yes | - |
| 6801373 | 16 | REALIZABLE | walk | 5.4 | 16384 | yes / yes | - |
| 6804432 | 17 | REALIZABLE | walk | 1.8 | 16384 | yes / yes | - |
| 6832186 | 19 | REALIZABLE | store | 1.2 | 256 | yes / yes | - |
| 6841782 | 18 | REALIZABLE | walk | 16.4 | 1024 | yes / yes | - |
| 6842821 | 19 | REALIZABLE | walk | 12.6 | 1024 | yes / yes | - |
| 6862079 | 19 | REALIZABLE | walk | 10.9 | 64 | yes / yes | - |
| 6862284 | 15 | REALIZABLE | walk | 0.7 | 1024 | yes / yes | - |
| 6883171 | 15 | REALIZABLE | store_walk | 0.5 | 64 | yes / yes | - |
| 6883541 | 21 | REALIZABLE | walk | 4.4 | 1024 | yes / yes | - |
| 6885585 | 16 | REALIZABLE | walk | 4.0 | 512 | yes / yes | - |
| 6885994 | 18 | REALIZABLE | walk | 3.3 | 1024 | yes / yes | - |
| 6888979 | 18 | REALIZABLE | walk | 7.9 | 1024 | yes / yes | - |
| 6891706 | 17 | REALIZABLE | walk | 11.2 | 1024 | yes / yes | - |
| 6904353 | 16 | REALIZABLE | walk | 24.0 | 1024 | yes / yes | - |
| 6913616 | 22 | REALIZABLE | walk | 14.1 | 512 | yes / yes | - |
| 6928542 | 16 | REALIZABLE | store_walk | 0.5 | 64 | yes / yes | - |
| 6953817 | 21 | REALIZABLE | walk | 25.4 | 1024 | yes / yes | - |
| 6957258 | 20 | REALIZABLE | walk | 1.6 | 16384 | yes / yes | - |
| 6962149 | 20 | REALIZABLE | walk | 13.1 | 16384 | yes / yes | - |
| 6969448 | 21 | REALIZABLE | store | 1.4 | 64 | yes / yes | - |
| 7014264 | 18 | REALIZABLE | walk | 11.9 | 1024 | yes / yes | - |
| 7014892 | 21 | REALIZABLE | walk | 8.9 | 1024 | yes / yes | - |
| 7022567 | 22 | REALIZABLE | walk | 4.8 | 64 | yes / yes | - |
| 7030182 | 18 | REALIZABLE | walk | 6.6 | 1024 | yes / yes | - |
| 7041689 | 18 | REALIZABLE | walk | 4.0 | 1024 | yes / yes | - |
| 7058639 | 17 | REALIZABLE | walk | 3.9 | 8192 | yes / yes | - |
| 7062963 | 21 | REALIZABLE | walk | 8.9 | 1024 | yes / yes | - |
| 7070158 | 20 | REALIZABLE | walk | 21.9 | 16384 | yes / yes | - |
| 7073614 | 20 | REALIZABLE | walk | 48.3 | 1024 | yes / yes | - |
| 7079741 | 17 | REALIZABLE | walk | 31.0 | 8192 | yes / yes | - |
| 7080395 | 18 | REALIZABLE | walk | 10.3 | 8192 | yes / yes | - |
| 7088631 | 20 | REALIZABLE | walk | 9.7 | 1024 | yes / yes | - |
| 7091229 | 17 | REALIZABLE | store | 1.4 | 256 | yes / yes | - |
| 7097231 | 18 | REALIZABLE | store | 0.9 | 64 | yes / yes | - |
| 7108308 | 21 | REALIZABLE | walk | 1.6 | 16384 | yes / yes | - |
| 7117317 | 18 | REALIZABLE | walk | 2.2 | 64 | yes / yes | - |
| 7128998 | 18 | REALIZABLE | store | 1.0 | 1024 | yes / yes | - |
| 7137310 | 24 | REALIZABLE | fresh | 1.3 | 1024 | yes / yes | - |
| 7143767 | 17 | REALIZABLE | walk | 48.4 | 1024 | yes / yes | - |
| 7143916 | 17 | REALIZABLE | walk | 3.4 | 4096 | yes / yes | - |
| 7208948 | 17 | REALIZABLE | walk | 1.5 | 1024 | yes / yes | - |
| 7209645 | 18 | REALIZABLE | walk | 2.3 | 1024 | yes / yes | - |
| 7223024 | 21 | REALIZABLE | walk | 2.0 | 64 | yes / yes | - |
| 7250611 | 20 | REALIZABLE | walk | 11.7 | 1024 | yes / yes | - |
| 7268803 | 15 | REALIZABLE | store_walk | 0.4 | 262144 | yes / yes | - |
| 7284957 | 23 | REALIZABLE | walk | 5.5 | 1024 | yes / yes | - |
| 7291053 | 18 | REALIZABLE | walk | 2.1 | 8192 | yes / yes | - |
| 7306091 | 17 | REALIZABLE | fresh | 2.2 | 1024 | yes / yes | - |
| 7310060 | 18 | REALIZABLE | walk | 2.9 | 16384 | yes / yes | - |
| 7336929 | 20 | REALIZABLE | walk | 5.5 | 16384 | yes / yes | - |
| 7338078 | 16 | REALIZABLE | walk | 8.9 | 1024 | yes / yes | - |
| 7345378 | 21 | REALIZABLE | walk | 22.9 | 64 | yes / yes | - |
| 7347226 | 20 | REALIZABLE | walk | 3.3 | 1024 | yes / yes | - |
| 7347848 | 19 | REALIZABLE | walk | 8.3 | 1024 | yes / yes | - |
| 7348678 | 17 | REALIZABLE | walk | 26.1 | 1024 | yes / yes | - |
| 7363702 | 18 | REALIZABLE | store_walk | 1.3 | 1024 | yes / yes | - |
| 7387490 | 22 | REALIZABLE | walk | 19.8 | 1024 | yes / yes | - |
| 7397977 | 17 | REALIZABLE | walk | 2.3 | 16384 | yes / yes | - |
| 7420791 | 20 | REALIZABLE | walk | 2.9 | 16384 | yes / yes | - |
| 7432045 | 18 | REALIZABLE | walk | 29.4 | 256 | yes / yes | - |
| 7459250 | 18 | REALIZABLE | walk | 17.3 | 1024 | yes / yes | - |
| 7481173 | 20 | REALIZABLE | fresh | 2.4 | 16384 | yes / yes | - |
| 7515166 | 22 | REALIZABLE | walk | 8.5 | 16384 | yes / yes | - |
| 7617933 | 18 | REALIZABLE | walk | 1.0 | 1024 | yes / yes | - |
| 7651291 | 18 | REALIZABLE | walk | 41.6 | 1024 | yes / yes | - |
| 7668526 | 19 | REALIZABLE | walk | 12.5 | 1024 | yes / yes | - |
| 7698446 | 20 | REALIZABLE | walk | 49.8 | 1024 | yes / yes | - |
| 7732312 | 18 | REALIZABLE | walk | 10.7 | 1024 | yes / yes | - |
| 7770795 | 19 | REALIZABLE | walk | 25.7 | 16384 | yes / yes | - |
| 7776099 | 20 | REALIZABLE | walk | 25.3 | 1024 | yes / yes | - |
| 7781474 | 17 | REALIZABLE | walk | 3.9 | 1024 | yes / yes | - |
| 7783239 | 16 | REALIZABLE | walk | 5.6 | 1024 | yes / yes | - |
| 7816209 | 16 | REALIZABLE | walk | 34.5 | 64 | yes / yes | - |
| 7832252 | 18 | REALIZABLE | walk | 46.7 | 1024 | yes / yes | - |
| 7898156 | 18 | REALIZABLE | walk | 1.6 | 1024 | yes / yes | - |
| 7902858 | 16 | REALIZABLE | walk | 3.1 | 1024 | yes / yes | - |
| 7903688 | 23 | REALIZABLE | fresh | 2.2 | 16384 | yes / yes | - |
| 7916819 | 13 | REALIZABLE | walk | 4.5 | 262144 | yes / yes | - |
| 7920230 | 18 | REALIZABLE | walk | 3.8 | 16384 | yes / yes | - |
| 7958480 | 18 | REALIZABLE | walk | 1.9 | 8192 | yes / yes | - |
| 7984914 | 17 | REALIZABLE | store | 0.9 | 1024 | yes / yes | - |
| 7986648 | 17 | REALIZABLE | walk | 14.7 | 262144 | yes / yes | - |
| 8001604 | 19 | REALIZABLE | walk | 13.4 | 262144 | yes / yes | - |
| 8002801 | 23 | REALIZABLE | walk | 1.7 | 1024 | yes / yes | - |
| 8016040 | 19 | REALIZABLE | walk | 3.1 | 262144 | yes / yes | - |
| 8031476 | 17 | REALIZABLE | walk | 4.4 | 1024 | yes / yes | - |
| 8031626 | 17 | REALIZABLE | walk | 10.8 | 1024 | yes / yes | - |
| 8067562 | 15 | REALIZABLE | walk | 16.4 | 1024 | yes / yes | - |
| 8067581 | 17 | REALIZABLE | walk | 2.3 | 16384 | yes / yes | - |
| 8127895 | 16 | REALIZABLE | store_walk | 0.6 | 16384 | yes / yes | - |
| 8138516 | 19 | REALIZABLE | walk | 54.2 | 1024 | yes / yes | - |
| 8140234 | 20 | REALIZABLE | walk | 12.0 | 1024 | yes / yes | - |
| 8145146 | 16 | REALIZABLE | walk | 11.9 | 1024 | yes / yes | - |
| 8157899 | 17 | REALIZABLE | fresh | 1.8 | 1024 | yes / yes | - |
| 8175918 | 24 | REALIZABLE | walk | 5.0 | 1024 | yes / yes | - |
| 8185290 | 18 | REALIZABLE | walk | 27.7 | 1024 | yes / yes | - |
| 8218575 | 21 | REALIZABLE | walk | 7.4 | 262144 | yes / yes | - |
| 8245156 | 16 | REALIZABLE | walk | 0.6 | 1024 | yes / yes | - |
| 8251786 | 18 | REALIZABLE | walk | 2.0 | 1024 | yes / yes | - |
| 8260089 | 21 | REALIZABLE | walk | 8.8 | 1024 | yes / yes | - |
| 8265580 | 18 | REALIZABLE | walk | 8.5 | 1024 | yes / yes | - |
| 8271217 | 20 | REALIZABLE | store | 0.8 | 256 | yes / yes | - |
| 8283784 | 19 | REALIZABLE | fresh | 2.0 | 1024 | yes / yes | - |
| 8287318 | 17 | REALIZABLE | walk | 4.7 | 1024 | yes / yes | - |
| 8301399 | 15 | REALIZABLE | walk | 2.7 | 1024 | yes / yes | - |
| 8306255 | 20 | REALIZABLE | walk | 51.8 | 1024 | yes / yes | - |
| 8337295 | 17 | REALIZABLE | store | 0.7 | 256 | yes / yes | - |
| 8362319 | 17 | REALIZABLE | walk | 13.9 | 64 | yes / yes | - |
| 8372832 | 15 | REALIZABLE | walk | 3.4 | 1024 | yes / yes | - |
| 8376872 | 17 | REALIZABLE | fresh | 1.5 | 1024 | yes / yes | - |
| 8392218 | 21 | REALIZABLE | walk | 1.2 | 1024 | yes / yes | - |
| 8394107 | 19 | REALIZABLE | walk | 2.1 | 1024 | yes / yes | - |
| 8402751 | 20 | REALIZABLE | walk | 31.1 | 1024 | yes / yes | - |
| 8404474 | 23 | REALIZABLE | walk | 20.0 | 16384 | yes / yes | - |
| 8411975 | 19 | REALIZABLE | walk | 7.5 | 262144 | yes / yes | - |
| 8428610 | 20 | REALIZABLE | store_walk | 1.1 | 16384 | yes / yes | - |
| 8430431 | 17 | REALIZABLE | store_walk | 1.1 | 1024 | yes / yes | - |
| 8444963 | 15 | REALIZABLE | walk | 13.5 | 1024 | yes / yes | - |
| 8445265 | 21 | REALIZABLE | walk | 1.4 | 1024 | yes / yes | - |
| 8452912 | 20 | REALIZABLE | walk | 1.2 | 16384 | yes / yes | - |
| 8453352 | 16 | REALIZABLE | walk | 17.3 | 1024 | yes / yes | - |
| 8460795 | 18 | REALIZABLE | walk | 2.7 | 8192 | yes / yes | - |
| 8505902 | 16 | REALIZABLE | walk | 3.4 | 1024 | yes / yes | - |
| 8529503 | 18 | REALIZABLE | walk | 7.0 | 262144 | yes / yes | - |
| 8541456 | 15 | REALIZABLE | walk | 10.1 | 64 | yes / yes | - |
| 8545392 | 17 | REALIZABLE | walk | 12.6 | 1024 | yes / yes | - |
| 8545612 | 20 | REALIZABLE | walk | 1.6 | 1024 | yes / yes | - |
| 8559272 | 20 | REALIZABLE | walk | 8.6 | 16384 | yes / yes | - |
| 8603583 | 14 | REALIZABLE | walk | 18.0 | 1024 | yes / yes | - |
| 8636420 | 20 | REALIZABLE | walk | 50.9 | 1024 | yes / yes | - |
| 8640746 | 20 | REALIZABLE | walk | 21.1 | 16384 | yes / yes | - |
| 8684939 | 19 | REALIZABLE | walk | 2.2 | 16384 | yes / yes | - |
| 8689254 | 17 | REALIZABLE | walk | 10.1 | 1024 | yes / yes | - |
| 8698279 | 16 | REALIZABLE | walk | 12.2 | 8192 | yes / yes | - |
| 8705199 | 21 | REALIZABLE | walk | 6.5 | 1024 | yes / yes | - |
| 8723746 | 20 | REALIZABLE | store | 1.5 | 256 | yes / yes | - |
| 8741624 | 19 | REALIZABLE | walk | 2.0 | 1024 | yes / yes | - |
| 8749834 | 20 | REALIZABLE | walk | 8.0 | 1024 | yes / yes | - |
| 8789238 | 19 | REALIZABLE | walk | 1.4 | 16384 | yes / yes | - |
| 8792735 | 19 | REALIZABLE | fresh | 1.3 | 1024 | yes / yes | - |
| 8796224 | 21 | REALIZABLE | walk | 2.4 | 1024 | yes / yes | - |
| 8866214 | 22 | REALIZABLE | fresh | 2.2 | 16384 | yes / yes | - |
| 8867071 | 19 | REALIZABLE | walk | 1.5 | 1024 | yes / yes | - |
| 8882587 | 18 | REALIZABLE | walk | 2.2 | 16384 | yes / yes | - |
| 8898840 | 18 | REALIZABLE | store | 1.0 | 65536 | yes / yes | - |
| 8910349 | 18 | REALIZABLE | walk | 3.7 | 1024 | yes / yes | - |
| 8921342 | 19 | REALIZABLE | walk | 4.0 | 1024 | yes / yes | - |
| 8924175 | 16 | REALIZABLE | walk | 17.5 | 16384 | yes / yes | - |
| 8928494 | 18 | REALIZABLE | walk | 8.7 | 16384 | yes / yes | - |
| 8929110 | 15 | REALIZABLE | walk | 3.6 | 1024 | yes / yes | - |
| 8931295 | 18 | REALIZABLE | walk | 12.2 | 262144 | yes / yes | - |
| 8942650 | 17 | REALIZABLE | walk | 2.4 | 262144 | yes / yes | - |
| 8948682 | 22 | REALIZABLE | walk | 1.6 | 8192 | yes / yes | - |
| 8956018 | 19 | REALIZABLE | fresh | 2.0 | 8192 | yes / yes | - |
| 8964644 | 19 | REALIZABLE | walk | 37.7 | 1024 | yes / yes | - |
| 8975349 | 17 | REALIZABLE | walk | 40.6 | 1024 | yes / yes | - |
| 9004974 | 18 | REALIZABLE | walk | 3.0 | 512 | yes / yes | - |
| 9024158 | 18 | REALIZABLE | walk | 3.2 | 262144 | yes / yes | - |
| 9069175 | 18 | REALIZABLE | walk | 1.3 | 1024 | yes / yes | - |
| 9072423 | 21 | REALIZABLE | walk | 29.5 | 16384 | yes / yes | - |
| 9080995 | 18 | REALIZABLE | walk | 2.3 | 1024 | yes / yes | - |
| 9098969 | 25 | REALIZABLE | walk | 12.7 | 1024 | yes / yes | - |
| 9111863 | 18 | REALIZABLE | walk | 51.2 | 1024 | yes / yes | - |
| 9128142 | 20 | REALIZABLE | walk | 4.1 | 16384 | yes / yes | - |
| 9128143 | 21 | REALIZABLE | store_walk | 1.0 | 16384 | yes / yes | - |
| 9134243 | 20 | REALIZABLE | walk | 5.7 | 1024 | yes / yes | - |
| 9180297 | 23 | REALIZABLE | walk | 12.4 | 16384 | yes / yes | - |
| 9183456 | 20 | REALIZABLE | walk | 19.4 | 1024 | yes / yes | - |
| 9197921 | 18 | REALIZABLE | store_walk | 0.8 | 64 | yes / yes | - |
| 9205025 | 23 | REALIZABLE | fresh | 1.8 | 1024 | yes / yes | - |
| 9239163 | 18 | REALIZABLE | walk | 1.3 | 1024 | yes / yes | - |
| 9240741 | 18 | REALIZABLE | walk | 6.5 | 1024 | yes / yes | - |
| 9246277 | 22 | REALIZABLE | store_walk | 1.0 | 4096 | yes / yes | - |
| 9258244 | 18 | REALIZABLE | walk | 2.0 | 16384 | yes / yes | - |
