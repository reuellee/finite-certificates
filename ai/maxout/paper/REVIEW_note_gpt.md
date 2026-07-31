# Verdict: NEEDS FIXES

The core theorem and its certificate accounting survive hostile review.  The
present source is nevertheless not submit-ready: it has two genuine LaTeX
errors, and several ancillary/software and candidate-scope claims are broader
than the supplied artifacts or the written argument support.

1. **[PASS — definition fidelity] The attributions to arXiv:2509.21286 are
   accurate.**  In `bcls.html`, Proposition 6.5 (HTML lines 1612--1635) states
   the bounds \(16,26,44,60\) for \(n=3,4,5,6\), says that they are tight,
   describes the DFS over combinatorial types for the upper bounds, and says
   that extremal zonoboxtopes were found by sampling.  The source's exact
   final sentence is: “Using only 1000 samples for each \(n=3,4,5,6\), this
   method succeeds.”  The current note accurately summarizes this, although
   it does not itself include the 1000-sample sentence.  Part 1 of Conjecture
   6.6 (HTML lines 1643--1657) gives exactly the odd/even formulas printed at
   TeX lines 74--76.  Remark 6.7 (HTML lines 1691--1697) says that all results
   and conjectures in Section 6 apply to zonoboxtope candidates.  The
   candidate definition at HTML lines 411--416 is exactly two zonotopes with
   corresponding parallel generators; independent translations are allowed.
   Equation (24) and the nonnegative \(a_i,b_i\) convention at HTML lines
   1378--1388 also agree with (1) in the note.

2. **[PASS — numerical consistency] The principal counts are mutually
   consistent and agree with the compressed artifacts.**  There are 33,140
   distinct valid labeled patterns.  The four split representatives have the
   following family/explicit counts:

   \[
   \begin{array}{c|r|r}
   A&\text{family}&\text{explicit}\\ \hline
   \varnothing&32,570&570\\
   \{0\}&24,691&8,449\\
   \{0,1\}&8,746&24,394\\
   \{0,2\}&8,916&24,224
   \end{array}
   \]

   Thus the family total is
   \(32,570+24,691+8,746+8,916=74,923\), the explicit total is
   \(570+8,449+24,394+24,224=57,637\), and their sum is
   \(132,560=4\cdot33,140\).  The four prefix shards contain 32,843 distinct
   explicit records (8,449 at \(k=1\), 24,394 at \(k=2\)); the four
   `split02` shards contain all 33,140 patterns exactly once, split as
   8,916/24,224.  The audit report's 132,681 checks are
   \(132,560+121\) redundant prioritized checks, exactly as the note says.
   The erroneous count 84,143 (in any comma/TeX spelling) does **not** occur
   in the note.  The chamber bound \(22=2(1+4+6)\), the cap \(44=2\cdot22\),
   the \(25\times8\) system, the 20 side rows plus 5 positivity rows, and the
   \(2^6=64\) candidate count are all correct.

3. **[PASS — symmetry and instances] The split and instance data agree with
   the repository.**  The exact checkers reproduce 384 uniform rank-3
   chirotopes in one orbit, a stabilizer of order 10, and the four zero-based
   representatives
   \(\varnothing,\{0\},\{0,1\},\{0,2\}\); these are precisely the note's
   one-based
   \(\varnothing,\{1\},\{1,2\},\{1,3\}\).  Proposition 2's \(U,M,a,b\) agree
   coordinate-for-coordinate with `paper/anc/cert_35_42.json` (which is
   byte-identical to the top-level certificate).  The ancillary verifier
   passes in exact `Fraction` arithmetic with 42 vertex witnesses and 22
   nonvertex combinations.  It also passes the stated 110, 104, 58, and 84
   counts.  The conclusion that \((4,6)\) has maximum 104 is valid because
   each of its two four-dimensional, six-generator zonotopes has at most
   \(2\sum_{k=0}^{3}\binom{5}{k}=52\) vertices.

4. **[BLOCKER — LaTeX] The abstract is illegally placed before
   `\begin{document}`.**  TeX lines 25--45 contain the abstract, while
   `\begin{document}` is only at line 47.  The committed log records
   `LaTeX Error: Missing \begin{document}` at line 25, followed by massive
   overfull boxes and an overfull vbox.  A fresh
   `pdflatex -halt-on-error` run exits fatally at this point and produces no
   PDF.  The existing seven-page PDF is an error-recovery output, not a clean
   compilation.  Move `\begin{document}` before the abstract (with
   `\maketitle` in the ordering required by `amsart`).

5. **[BLOCKER — LaTeX] The hyperlink color is undefined.**  TeX line 5 uses
   the `xcolor` mixing expression `blue!60!black`, but `xcolor` is not loaded.
   The committed log contains repeated `Undefined color
   'blue!60!black'` errors at citations and links.  Load `xcolor` before
   `hyperref`, or use a color understood by the base `color` package.  After
   fixing both blockers, recompile with `-halt-on-error` and inspect the two
   remaining reported overfull boxes near TeX lines 311--338 (the long
   monospaced filenames).

6. **[MAJOR — unsupported software claim] The ancillary verifier cannot
   “check any explicit instance in seconds.”**  This claim occurs at TeX
   lines 92--93 and again at lines 353--355.  The program has a hard-coded
   list of five certificate files.  It verifies already-supplied strict
   witnesses and convex combinations; it neither accepts an arbitrary raw
   instance nor computes those certificates.  A proposed 44-vertex instance
   could be checked only after extending the program/input and supplying or
   computing the needed hull certificates (or by using another hull
   implementation).  Narrow both sentences to what this verifier actually
   does.

7. **[MAJOR — candidate-scope proof gap] The artifacts support arbitrary
   relative translation, but the written perturbation lemma is formulated
   only in zonoboxtope parameters.**  TeX lines 93--98 claim the exact maximum
   for all zonoboxtope candidates, while lines 283--293 perturb only
   \((a,b,m)\).  A candidate with equal corresponding widths and an arbitrary
   relative translation need not be representable by common midpoints in
   that parameterization.  The gap is readily repairable: formulate the
   perturbation in candidate coordinates (two independent translations and
   two positive width vectors), keep \(T\) independent, and perturb the width
   differences away from zero.  Alternatively, omit the stronger candidate
   maximum.  Remark 6.7 faithfully motivates the scope, but the citation does
   not prove this new theorem for the note.

8. **[MINOR — overclaim] “Our formalization reproduces every other vertex
   number reported in Section 6” is too broad.**  The repository documents a
   floating-point reimplementation reproducing the other three Proposition
   6.5 values \(16,26,60\); the ancillary exact certificates do not certify
   those three runs, and Section 6 contains more than those three numbers.
   Say precisely that the implementation numerically reproduced the other
   three values in Proposition 6.5.  The proposed floating-point-artifact
   diagnosis is explicitly a suspicion and is acceptable once its supporting
   sentence is narrowed.

9. **[MINOR — overclaim] “Extensive complete-per-instance searches found no
   more” is misleading without the qualification present in the repository.**
   Completeness is only for the remaining systems after fixing a direction
   configuration; the \(U\)-space was not exhausted.  State “exhaustive for
   each fixed sampled direction configuration,” or delete this search-negative
   aside.  The following sentence correctly leaves the odd-\(n\) question
   open.

10. **[MINOR — scope of algebraic claim] “The complete
    coefficientwise-positive mechanism” is too expansive.**  The boundary
    theorem in `STAGE2C2.md` concerns the ordinary-polynomial, no-GP
    equal-pair ansatz.  The quotient-ring certificates themselves also have
    coefficientwise nonnegative multipliers, so the unqualified wording is
    at best confusing.  Replace it by “the complete coefficientwise-positive
    ordinary-polynomial/no-GP mechanism.”

11. **[MINOR — provenance/control overclaims] Two absolute statements should
    be narrowed.**  “Canaries were wired into every search” is stronger than
    the ledger, which says the discipline was instituted after an earlier
    caught bug and was used in every final completion sweep.  Likewise, “No
    mathematical claim ... rests on model output” is literally false because
    the certificates and programs are model-produced; the defensible claim is
    that no result rests on **unverified** model output.  Neither issue affects
    the exact certificates.

12. **[MINOR — self-containedness and prose] Several local edits are needed.**
    In the abstract, write \(\sum_{k=0}^{2}\), not the lower-bound-free
    \(\sum_{k\le2}\).  At TeX line 55, change “The first interesting class ...
    are” to “is.”  “Support vectors” at lines 182--184 is nonstandard for
    normal directions and should be replaced by “objective/normal
    directions.”  The transport shorthand
    \(\tau=\pm\varepsilon\varepsilon\) at lines 275--276 needs indices and the
    pair-order sign.  A polyhedral chamber cone is convex/pointed, not
    “strictly convex” in the usual convex-analytic sense (lines 297--300);
    strict convexity is not needed.  Cite a source for the nontrivial
    realizability statement about rank-3 oriented matroids on at most eight
    elements.  Finally, the end of the proof should preferably use an actual
    `proof` environment rather than a manually appended `\qed`.

Subject to items 4--7 and the straightforward wording corrections, I find no
numerical inconsistency or artifact-level defect that undermines the main
\((3,5)\) theorem.
