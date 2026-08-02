# Literature and novelty check for the (4,9) program

*2026-08-02. Every quotation below is **verbatim from primary text** held in
our own corpus cache (`ops/corpus/cache/fulltext/`), not from a model
summary. A Gemini web pass suggested most of these leads and was correct on
each one that primary text could check; it is not itself cited here. This
program has twice shipped a bad attribution, so the rule is: quote, or do
not claim.*

## 1. Biquadratic final polynomials are known to be INCOMPLETE

> "Indeed, all non-realizable uniform oriented matroids rank 3 on up to 11
> elements can be shown to be such using bi-quadratic final polynomials. An
> explicit example of a non-realizable oriented matroid Ω−14 without a
> bi-quadratic final polynomial was constructed by Richter-Gebert [RG96b],
> and one on 12 points has been announced by Scheucher."
> — *Oriented Matroids Today*, EJC Dynamic Survey **DS4 v4 (2024)**, §on
> deciding realizability.

So the known landscape **in rank 3** is:

| uniform rank 3 | status of BFP certificates |
|---|---|
| n ≤ 11 | complete — every non-realizable class has a BFP |
| n = 12 | **fails** (announced, Scheucher) |
| n = 14 | **fails** (published, Richter-Gebert [RG96b] = *Two interesting oriented matroids*, Doc. Math. 1 (1996) 137–152) |

Two consequences for how our result must be written:

1. **Never conjecture BFP-completeness in general — it is false.** The
   honest statement is about a specific cell.
2. **Our (4,9) result is a datapoint on where certificate tameness dies,**
   and that is a much stronger framing than "we verified a plausible
   principle". Rank 3 goes wild between n = 11 and n = 12. **Rank 4's
   analogous threshold is unknown, and completeness at (4,9) is the
   largest lower bound anyone has established for it.**

Also worth recording, same passage: general (non-biquadratic) final
polynomials **always exist** for non-realizable OMs by real algebraic
geometry ("by the above [BPR98], there always exists a final polynomial
which however is computationally infeasible to find"). So Weapon B2's
degree/support escalation is a search for a *findable* certificate, never a
question of existence. State it that way.

## 2. Prior classification results — what is actually ours

> "In this paper, we complete the classification of OM(4,8), OM(3,9) and
> OM(6,9) (Theorem 1.1) ... This in turn proves that every non-realizable
> oriented matroid in these classes admits a biquadratic final polynomial
> certificate. **Theorem 1.1** (a) Among 181,472 oriented matroids in
> OM(4,8) (reorientation class), 177,504 oriented matroids are realizable
> and 3,968 are non-realizable. (b) Among 461,053 oriented matroids in
> OM(3,9) ... 460,779 ... realizable and 274 ... non-realizable. (c) Among
> 508,321 oriented matroids in OM(6,9) ... 508,047 ... realizable and 274
> ... non-realizable."
> — Fukuda, Miyata, Moriyama, *Complete enumeration of small realizable
> oriented matroids*, arXiv:1204.0645.

These counts are over **all** oriented matroids (non-uniform included); our
9,276,595 is the **uniform** rank-4 cell on 9 elements. Decisively:
**OM(4,9) is not in Theorem 1.1** — they settle OM(4,8), OM(3,9), OM(6,9).
The DS4 sentence that mentions "rank 4 on 10 elements" is about the same
FMM13 work and reads in full: *"Fukuda, Miyata, and Moriyama [FMM13]
combine the above methods with some ad hoc computations to enumerate the
realizable (non-uniform) oriented matroids of rank 3 on 9 elements and of
rank 4 on 10 elements."* — a different (rank, n) pairing from ours and not
a classification of uniform (4,9). **The (4,9) realizability split remains
unpublished**, consistent with the blank entry in the FFM tables and with a
web pass finding later work still quoting the count without a split.

## 3. The duality corollary has precedent in the same theorem

> "We note here that the classification of OM(6,9) is obtained from the
> classification of OM(3,9) and the duality of oriented matroids [8]."
> — FMM13, immediately after Theorem 1.1.

This is exactly the move recorded in `ai/om410/SCOPING.md`: our (4,9) split
yields the **(5,9)** split for free (dual rank n − r = 5). FMM13 did the
analogous (3,9) → (6,9) step and reported it as part of the theorem, which
both validates the method and shows they would have reported (5,9) had they
had (4,9). Cite [8] of FMM13 for the duality statement when writing it up.

## 4. The four lemmas we rely on (folklore audit)

| | statement | how to write it |
|---|---|---|
| S1 | **Proposition R** — a non-realizable deletion lifts to a BFP of the parent | No explicit statement located in the literature; the lifting principle (a 3-term GP relation on E∖e is one on E, so the certificate transfers verbatim) is folklore. **Write "we record a proof for completeness", never "we prove".** |
| S2 | BFP existence is a relabeling/reorientation class invariant | Standard and used routinely; same phrasing rule as S1. |
| S3 | realizability transports across one mutation | Roudneff–Sturmfels 1988. **Use the wording already fixed in `ai/omgamma/OMGAMMA.md` §4**, which survived two attribution corrections — do not re-derive it here. |
| S4 | realization ⟹ u = log\|brackets\| meets every forced inequality ⟹ no BFP (Gordan) | The soundness half of the BFP method of **Bokowski & Richter-Gebert [BR90b]**, named as such by DS4 ("the 'bi-quadratic final polynomials' algorithm of Bokowski & Richter-Gebert [BR90b] which uses solutions of an auxiliary linear program"). Cite; do not claim. |

## 5. Leads worth following

* **Fukuda, Moriyama, Nakayama, *Every non-Euclidean oriented matroid
  admits a biquadratic final polynomial*, arXiv:math/0510500 (2005).**
  Contrapositive: a non-realizable OM *without* a BFP must be **Euclidean**.
  The entire failure region of the BFP method therefore lives inside the
  Euclidean non-realizable OMs — Ω⁻₁₄ must be Euclidean. If Euclideanness
  is cheap to test per class, this sharpens both the (4,9) completeness
  statement and the om410 sampling design. **Read the paper.**
* Scheucher's announced 12-point example — track whether it is published;
  it moves the rank-3 threshold from 14 to 12.
* DS4 records the rank-3 n = 10 classification (312,356 classes, Bokowski,
  Laffaille & Richter-Gebert) as **"still unpublished"**. Our (3,10)
  calibration in `ai/omminor` describes its ground truth as published —
  soften that wording; our own certified sweep is the actual warrant.
