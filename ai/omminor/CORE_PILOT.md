# Certificate-core pilot on the minor-minimal population

Run 2026-08-02, following the preregistered experiment in
[`CERTIFICATE_CORE_PROGRAM.md`](CERTIFICATE_CORE_PROGRAM.md).

## Decision

**The unoptimized BFP-core route fails its preregistered compression gate on
the hard population. Do not scale the raw-core matcher to all 1,758 tracked
minor-minimal classes or to the completed sweep.**

On a deterministic 64-class sample of the tracked minor-minimal prefix:

| measurement | result |
|---|---:|
| unique BIG-term conditions per emitted BFP | min 54, median 76, max 97 |
| classes matched literally by another emitted core | **0 / 64** |
| classes matched by another emitted core after exhaustive \(S_9\) relabelling | **5 / 64** |
| exact realizable controls matched | **0 / 206** |
| best coverage by any 3 emitted cores (the 5% budget) | **6 / 64** |
| cores needed by greedy cover for 90% | **54 / 64** |
| cores needed by greedy cover for 100% | **60 / 64** |
| deterministic held-out test covered by training cores | **2 / 36** |

The gate required at most 3 core orbits to cover at least 58 of the 64
classes. Exhaustively checking every 1-, 2- and 3-core combination gives
maximum coverages 2, 4 and **6**, respectively. This is not a near miss.

This is a useful negative result, not a theorem that no compressed
certificate library exists. It says that the BFPs naturally emitted by the
current LP are almost private explanations on the minor-minimal population.

---

## 1. Corpus and scope

`data/minimal_ext.txt` contains the canonical chirotopes of the 1,758 classes
proved minor-minimal over the 19.12%-complete depth-ordered sweep prefix in
`MINOR_THEORY.md`. The large original certificate records were deliberately
gitignored, but a chirotope is sufficient to regenerate a BFP.

`build_core_sample.py` selects the 64 smallest values of

\[
\operatorname{SHA256}(
  \texttt{"uom49-minor-minimal-core-pilot-v1"}\,\|\,0\,\|\,\chi)
\]

from those 1,758 strings. Selection is independent of file order. For every
selected class it reruns `ai/omreal/bfp.py`, reconstructs positive integer
weights, and writes `data/core_minimal_sample.jsonl`. The independent
standard-library `ai/omreal/checkcert.py` accepts all 64 certificates.

The sample is deterministic, but it is **not** a uniform sample of the final
minor-minimal population. Its parent population is the depth-biased 19.12%
prefix. The result is a bounded method test, not a catalogue-wide frequency
estimate.

The 206 preregistered realizable controls are frozen in
`data/core_realizable_controls.jsonl`.  This dedicated snapshot prevents later
growth or regeneration of the completed-sweep artifacts from silently changing
the pilot population.  It is the record-for-record concatenation of the 80
validation and 126 certificate records used at source commit `95630b8`, with
line endings normalized to LF and SHA-256
`a2ce5aace93a9afd6832190901d048c450a9eb69388808f31d24bfd7664b60a5`.
The independent verifier recomputes all 126 maximal minors of every stored
integer matrix, so it does not trust the snapshot's `REALIZABLE` labels.

---

## 2. What counts as a core

A BFP term names a three-term GP relation \((L;a,b,c,d)\), its BIG term, a
SMALL term and a positive integer weight. The proof of cancellation uses the
weighted terms. Applicability to another chirotope needs only the distinct

\[
(L,\{a,b,c,d\},\text{BIG perfect matching})
\]

conditions occurring in the proof.

The perfect-matching formulation is useful because it removes an easy source
of sign mistakes. For \(a<b<c<d\), the three terms correspond to the three
partitions

\[
ab\mid cd,\qquad ac\mid bd,\qquad ad\mid bc.
\]

An arbitrary element permutation transports the two-set \(L\), the four-set,
and this perfect matching. Reorientation multiplies all three GP terms by one
common sign and therefore leaves BIG unchanged.

`core_pilot.py` exhaustively searches all relabellings, but shares the search
over all targets using a Python-integer bitset. A branch is discarded as soon
as the GP conditions whose six elements have been assigned leave no compatible
target. Every emitted match retains the explicit source-to-target permutation.

`verify_core_pilot.py` imports neither the producer nor any project GP code. It
rebuilds colex bases and GP relations, verifies every source positive
dependence, transports every weighted certificate through the recorded
permutation, and verifies it against the target. Thus each pointer is an exact
subtree-pruning certificate. It also rejects six deliberate corruptions,
including a sign-flipped realizability witness.

The checker certifies every *reported positive match*. It does not reproduce
the producer's exhaustive search for unreported matches. That asymmetry is
safe for this negative measurement: a missed match can only understate reuse.
The exact 3-core maximum is with respect to the complete pointer set emitted
by the exhaustive producer.

---

## 3. Result: emitted circuits are almost private

There are 69 verified pointers: 64 self-pointers and five cross-class
pointers. The five are

```
16 -> 34
27 -> 28
28 -> 27
36 -> 29
58 -> 55
```

with indices in `data/core_minimal_sample.jsonl`. Only the middle pair is
mutual. There are no literal cross-matches; every cross-match uses a
nontrivial relabelling.

The deterministic SHA split puts 28 sources in training and 36 in test. The
training cores cover only test rows 28 and 55: **5.56% held-out coverage**.
This is not an estimate with a useful confidence interval; it is a canary
against mistaking self-coverage for generalization, and it fails.

The 206 realizable controls have zero matches under all relabellings. This is
required by soundness, not evidence of power: one false match would invalidate
the matcher.

---

## 4. Stronger test: search the common system, not the emitted proofs

The negative result above might merely reflect an arbitrary LP choice. Class
\(A\)'s emitted BFP may fail on class \(B\) even though some *other* BFP uses
conditions common to both.

`shared_core_pilot.py` tests that stronger statement for every one of the
\(\binom{64}{2}=2016\) pairs in their fixed canonical labelling:

1. retain every GP relation whose BIG term agrees in both classes;
2. include both BIG-to-SMALL rows for each retained relation; and
3. apply Gordan's alternative to this complete common row system.

The result is exact:

| exact alternative on the common system | pairs |
|---|---:|
| positive circuit: a BFP valid for both | **1** |
| strict integer \(u\) with \(v\cdot u>0\) for every common row | **2,015** |

`data/core_shared_literal.json.gz` contains all 2,016 certificates. The
standard-library `verify_shared_core_pilot.py` rebuilds the common system for
every pair and accepts all 2,015 strict witnesses and the one positive
circuit. Therefore, in the fixed labelling, only **1 of 2,016 pairs admits
any BFP core at all on its common BIG conditions**. This rules out the
"arbitrary LP output" explanation in that labelling.

The limitation is important: this second experiment does **not** try all
\(9!\) relative relabellings for each pair. The first experiment tries all
relabellings for the 64 emitted cores; the second considers all alternative
BFPs but only at the identity alignment. Combining both quantifiers remains
the strongest unrun core experiment.

---

## 5. Interpretation

The measured picture now has a sharp split.

* The easy ~91% of non-realizable \(UOM(4,9)\) is compressed by the already
  known 24 non-realizable deletions at \((4,8)\). That is genuine and useful,
  but it is not a new generating structure.
* On the minor-minimal population, naturally emitted BFPs are dense and
  almost class-specific, even modulo all relabellings.
* Searching the full literal intersection of two classes' inequality systems
  almost never recovers an alternative shared certificate.

So the attractive headline "a small BFP-core library generates the hard
remainder" has acquired substantial negative evidence. Running the same raw
experiment on 1,758 or ~10^4 classes would mostly manufacture a larger lookup
table.

What is **not** proved:

* no alternative BFP can cover many classes after choosing different relative
  relabellings;
* no higher-degree final-polynomial or Positivstellensatz core compresses the
  population;
* no completion-tree variable order gives a large node reduction; or
* no two-sided extension atlas exists.

---

## 6. The one justified follow-up, then a pivot

If the BFP-core route gets one more experiment, it should combine the missing
quantifiers directly:

> For selected pairs, search relative relabellings that maximize common BIG
> conditions, then run Gordan on the entire common system at those alignments.

This should be bounded before it starts—for example, a fixed set of 128 pairs
and at most 32 preregistered alignments per pair. Every positive circuit is
easy to certify. Every negative conclusion needs strict integer witnesses for
the alignments actually tested and must remain scoped to that alignment
search; it is not exhaustive over \(S_9\) unless all \(9!\) cases are checked.

If that bounded experiment also shows near-zero reuse, stop the BFP-core
program. The more promising target is then a **two-sided single-element
extension atlas**, because 98% of this cell is realizable and negative cores
can never remove the dominant positive work.

There is a small exact fact on which such an atlas can build.

> **Fixed-deletion blocker lemma (standard Gordan/Caratheodory corollary).**
> Fix a realized rank-\(r\) deletion \(Y\), and prescribe the signs of every
> bracket containing a missing column \(x\). If no \(x\in\mathbb R^r\)
> satisfies all resulting strict homogeneous linear inequalities, then
> infeasibility has a nonnegative Gordan certificate supported on at most
> \(r+1\) inequalities. In the present rank-4 problem, at most **five** of
> the 56 extension brackets suffice.

**Proof.** Write the signed constraint normals as rows \(a_i\in\mathbb R^r\).
Gordan's theorem gives \(\lambda\ge0\), \(\lambda\ne0\), with
\(\sum_i\lambda_i a_i=0\). Choose an inclusion-minimal support. Its rows form
a circuit in a vector configuration of rank at most \(r\), so the circuit has
at most \(r+1\) elements. \(\square\)

This lemma certifies failure for **one fixed realization \(Y\)** only. It does
not prove that another realization of the same deletion cannot extend. The
research problem is to cover the deletion realization space by finitely many
charts on which either a symbolic extension exists or one of these at-most-five
blocker types has a certificate valid throughout the chart.

---

## 7. Reproduction

From the repository root:

```bash
PYTHONDONTWRITEBYTECODE=1 python ai/omminor/build_core_sample.py
PYTHONDONTWRITEBYTECODE=1 python ai/omminor/core_pilot.py
PYTHONDONTWRITEBYTECODE=1 python ai/omminor/verify_core_pilot.py
PYTHONDONTWRITEBYTECODE=1 python ai/omminor/shared_core_pilot.py
PYTHONDONTWRITEBYTECODE=1 python ai/omminor/verify_shared_core_pilot.py
```

The two search producers take several minutes and under one minute,
respectively, on the test machine. The independent verifiers take about one
second each and use only the Python standard library.

Files:

| file | role |
|---|---|
| `build_core_sample.py` | deterministic BFP regeneration; non-authoritative producer |
| `data/core_minimal_sample.jsonl` | 64 exact source BFPs |
| `data/core_realizable_controls.jsonl` | 206 frozen exact realizable controls |
| `core_pilot.py` | exhaustive emitted-core matcher modulo \(S_9\) |
| `data/core_minimal_pilot.json.gz` | cores, pointers, permutations and statistics |
| `verify_core_pilot.py` | independent exact pointer checker |
| `shared_core_pilot.py` | all-pairs fixed-labelling common-system search |
| `data/core_shared_literal.json.gz` | 2,016 exact Gordan alternatives |
| `verify_shared_core_pilot.py` | independent exact all-pairs checker |
