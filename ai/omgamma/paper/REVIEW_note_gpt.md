# Adversarial referee report on `omgamma-note.tex`

## Verdict: NEEDS FIXES

I found no mathematical contradiction in the central positive result.  The
non-free component/holonomy reduction is sound, the resumed-harvest argument is
sound in the positive direction, the odd-`n` module argument is correct, and the
headline integers agree with the local raw data.  The note is nevertheless not
ready for arXiv in its present form.  It materially undercredits Knauer--Marc's
labelled rank-3 theorem, calls a published computation "unpublished," overstates
what the public compact certificates and standalone checker verify, and makes an
unsupported universal claim about all stabilizers at `(9,4)`.  The current TeX and
PDF are also out of sync, with a visibly broken Roudneff--Sturmfels citation.

Sources checked: the archived Knauer--Marc source
`ai/omgamma/sources/corners_and_simplicity.tex` (matching arXiv:2002.11403v3),
the archived Fukuda--Miyata--Moriyama source
`ai/omgamma/sources/fmm13_OM_classification.tex` (arXiv:1204.0645v2), the
archived Finschi pages, the Roudneff--Sturmfels publication/abstract at DOI
10.1007/BF00151346, all local `(9,4)` JSON/checkpoint artifacts, and the relevant
checker source.  I also ran `python verify_omgamma.py` and `python
submodules.py`; both exited successfully, subject to the scope limitations below.

## Findings

1. **SERIOUS -- Knauer--Marc's labelled rank-3 theorem is undercredited, and the blanket novelty claim is false.**

   Locations: abstract lines 32--37; Introduction lines 75--96; computation
   lines 251--265; "Relation to [KM23]" lines 350--355.

   Knauer--Marc do not merely prove the rank-3 reorientation-class graph
   connected.  Their Proposition 3.2 states
   `\overline{\mathcal G}^{n,3}` connected for every `n`; see the archived source
   lines 552--571.  Their introduction also explicitly advertises that labelled
   theorem (lines 203--205).  The note's sentence at lines 75--78 mentions only
   their weaker middle-level consequence, and line 354 says "Our `\Gb` results
   are new."  That is false for rank 3.  After elementary/dual cases are removed,
   the genuinely new labelled cases in the advertised range are essentially
   `(8,4)`, `(9,4)`, and `(9,5)` (with the last dual to `(9,4)`).  State this
   precisely in the abstract, introduction, and relation section.

2. **SERIOUS -- The note misdescribes a published computation and overstates the extent to which it answers Knauer--Marc's open problem.**

   Location: lines 350--355.

   Knauer--Marc's connectivity computation is reported in their published EJC
   article, with its method described at archived-source lines 613--631.  What is
   absent is public code/data/certificates; the computation itself is not
   "unpublished."  Replace that phrase by something factual such as "reported
   without publicly archived code or certificates."  Likewise, this note rules
   out a labelled counterexample only for `n <= 9`; it does not answer the global
   labelled connectivity question negatively.  The quotation of their suspicion
   is otherwise faithful: archived-source lines 633 and 1307--1308 say exactly
   that beyond rank 3 they know nothing about the labelled graph and suspect a
   counterexample there.

3. **SERIOUS -- The count/coverage claim is not certified by the public standalone artifacts in the sense asserted.**

   Locations: abstract lines 42--48; lines 106--113 and 132--147; computation
   lines 267--283; honesty section lines 306--331; provenance lines 362--367.

   The compact `(9,4)` certificates validate genuine paths and enough holonomy
   generators to prove `H = \Gbar`; they do not validate the 9,276,595 found
   representatives.  This is correctly admitted at lines 327--331.  More
   seriously, the public Git checkout tracks only `level_000.npz` of the twenty
   local `(9,4)` level files.  The full class list and stabilizer array used on the
   left side of the mass identity are therefore not public.  The tracked
   `stabstats.json`, `meta.json`, and `summary.json` merely assert the histogram
   and totals.  The 2,628-row `extcount_4_9.jsonl` is tracked, so the target side
   can be arithmetically reconstructed, but a fresh reader cannot check from the
   shipped data that the left side consists of 9,276,595 distinct valid classes
   with the asserted stabilizers.  `verify_omgamma.py` does not attempt that
   check.

   This directly contradicts "The claims above rest on artifacts, not on trust in
   the search programs" and especially "independent re-verification of every
   serialized artifact."  Publish the full catalog/checkpoints in an immutable
   release or data archive, together with a standalone coverage checker, or
   explicitly say that the count requires rerunning/trusting the enumerator and
   stop calling the count a publicly checkable certificate.

4. **SERIOUS -- "Independently computed" and "cannot overshoot" need explicit qualifications.**

   Locations: lines 106--113, 267--281, and 321--325.

   The two sides of the mass identity are combinatorially different: one is an
   `(8,4)` extension count and the other an orbit mass over a `(9,4)` mutation
   search.  That is valuable independence.  They are not implementation-
   independent.  Both rely on this project's canonicalizer/stabilizer machinery,
   and neither all stabilizer orders nor all extension counts are rederived by a
   standalone checker.  The note later admits this, but the theorem-level prose
   still calls the identity an exact certificate without the necessary
   hypotheses.  A missed class forces a shortfall only provided the reported
   classes are valid and pairwise inequivalent, the stabilizers are exact, and the
   extension target is exact.  A defective list with duplicates or wrong
   stabilizers can overshoot.  Say "structurally independent counting route" and
   state these conditions where the identity is used, not only in the later
   disclaimer.

5. **SERIOUS -- The claimed all-rank computational coverage is not covered by the advertised verifier.**

   Locations: lines 132--144 and 251--265.

   `verify_omgamma.py` checks certificates for `(8,3)`, `(8,4)`, `(9,3)`, and
   compact `(9,4)` holonomy.  It does not check the asserted rank-2 runs for every
   `n <= 9`, nor the smaller rank-4 runs.  There are no shipped rank-2 certificate
   files.  Knauer--Marc's labelled rank-3 theorem plus duality handles many of the
   small cases, but the note as written says they are all direct computations and
   that all claims are checked by the displayed commands.  Supply a short
   mathematical proof for rank 2 (preferable), or ship and manifest the missing
   outputs.  Then rewrite the case split to rely explicitly on Knauer--Marc for
   rank 3 and on duality, rather than asserting unmanifested computations.

6. **SERIOUS -- The central non-free reduction is true but not proved at a publishable level.**

   Locations: Lemmas 4--5, TeX lines 178--206.

   Lemma 4 is correct: quotient-path lifting shows every component maps onto the
   quotient, after which the group acts transitively on components and `H` is the
   component stabilizer.  Lemma 5 is also correct, including the stabilizer
   conjugates required for a non-free action.  But "Both directions are
   elementary" does not supply the converse, which is the substance of the
   reduction.  Give the short factorization proof: lift a quotient walk, compare
   successive lifts by an edge voltage times a terminal stabilizer, and telescope
   to express every element of `H` in the two displayed families.  Also define
   `tau_{c_0}=1`, the recurrence `tau_{c'}=tau_c t` on oriented tree edges, and the
   voltage's ambiguity modulo the target stabilizer.  These details appear in the
   current PDF but are absent from the current TeX, which is itself a source/PDF
   synchronization defect.

7. **MINOR -- The reorientation-component formula needs one missing group-theoretic sentence.**

   Location: lines 208--213.

   The formula
   `#components(\Gm)=[S_n:\pi(H)]` is correct, but it does not follow from Lemma 4
   literally as written.  Components of `\Gb/\bar R` are the `\bar R`-orbits on
   the components of `\Gb`, hence are counted by
   `[\Gbar:\bar R H]=[S_n:\pi(H)]` because `\bar R` is normal.  Include this
   argument.

8. **MINOR -- The group-action setup is imprecise and false in degenerate edge cases.**

   Locations: lines 151--166.

   `G'` is a semidirect product, not merely the displayed Cartesian product unless
   its multiplication is supplied.  The notation
   `|\varepsilon\cap\{x\}|` should mean the set of entries of the tuple.  The
   assertion that the kernel on pairs is exactly `K_4` for every `n >= r+1` fails
   in degenerate small cases (for example rank 0, and the `(n,r)=(2,1)` action has
   additional kernel).  Restrict the reduction to the nondegenerate range where
   it is used and dispatch the remaining cases first, or state only that the
   indicated `K_4` acts trivially and quotient by it without claiming it is the
   full kernel.

9. **MINOR -- Proposition 3 is mathematically correct, but its computational corroboration is overstated.**

   Locations: lines 225--247.

   For odd `n`, the even-weight module is indeed irreducible over `F_2`, so the
   dichotomy follows.  An elementary proof would be clearer than the uncited
   Specht-module assertion: for nonzero even `v`, choose one coordinate in and one
   out of its support; adding `v` to its image under the corresponding
   transposition produces a weight-2 vector, whose orbit spans the even-weight
   space.  The machine run also passed and returned the stated Galois numbers.
   However, method M2 is run only for `n <= 7`; "Both methods return exactly four
   ... for each `n`" is false for `n=8,9,10`.  Say that M1 does so for every listed
   `n`, and M2 agrees where it was run.  Lines 244--247 should also not imply the
   proposition is load-bearing for the final certificate: the checker exhibits a
   full sign span directly; the proposition supplies a conceptual shortcut.

10. **SERIOUS -- The universal stabilizer-parity claim is unsupported by the artifacts and likely stronger than what was computed.**

    Location: lines 285--289.

    The compact certificate proves that its 73 stabilizer-derived permutation
    generators are even and generate `A_9`, and that one odd edge generator raises
    the generated permutation group to `S_9`.  That statement is supported.
    `diag_stabhol.json`, however, scanned only 1,876,681 classes and 2,548
    nontrivial-stabilizer classes; the later certificate used 3,386 flagged
    classes.  The final catalog has 8,913 nontrivial stabilizers, and the main
    engine stops stabilizer harvesting once `H` is full.  Consequently the data do
    not show that *every* stabilizer element of *every* flagged class has even
    permutation part, nor that the complete family (i), over all classes, generates
    only `A_9`.  Replace the claim by the supported certificate-level statement.
    This does not affect `H=\Gbar`.

11. **NOTE -- Degenerate ranks, duality, and resume/lower-bound reasoning are sound.**

    Locations: lines 251--260 and Remark 6, lines 295--303.

    The three-term GP set is empty when `r<2` or `n<r+2`, and the resulting graph
    on sign pairs is a folded cube.  Oriented-matroid duality carries a basis
    mutation to the complementary-basis mutation and therefore transports all
    three quotient graphs.  The current TeX should restore the explicit dual
    chirotope formula that appears in the PDF and give a one-sentence proof of
    equivariance rather than cite a computation on 135 examples.  The resume
    logic is exactly right: the harvested `H'` is a subgroup of the true `H`, and
    `H'=\Gbar` forces `H=\Gbar`; the same data could not prove a negative result.
    `summary.json` correctly records `holonomy_is_lower_bound: true`.

12. **SERIOUS -- The honesty section contains good disclosures but is internally inconsistent with the paper's strongest rhetoric.**

    Locations: lines 132--147 and 306--369.

    The retraction at lines 333--348 is adequate and unusually specific: it names
    the omitted generator family, explains why the false negative-looking signal
    arose, and states the corrected outcome.  Keep it.  In contrast, "All claims
    are machine-checkable," "claims above rest on artifacts, not on trust in the
    search programs," and "independent re-verification of every serialized
    artifact" are not true for the count/coverage side.  The displayed default
    verifier checks one corrupted-voltage canary, while the five sabotage modes
    require `canary_checker.py`, a command not shown; `--canary` tests missing,
    renamed, and empty required compact artifacts, not the five listed corruptions.
    Rewrite the commands and trust-boundary language so that the scope of each
    check is impossible to misread.  Call the holonomy result certificate-backed;
    call the count a reproducible exact computation unless and until a full
    standalone coverage certificate is published.

13. **MINOR -- The TeX/PDF handoff is not clean despite successful compilation.**

    Locations: citation at lines 63--64; Lemma 5 setup at lines 189--198; duality
    at lines 256--259; files `omgamma-note.tex` and `omgamma-note.pdf`.

    The rendered PDF has six pages, not five, and contains a voltage-definition
    paragraph and an explicit duality formula absent from the current TeX.  It is
    therefore not a faithful render of the submitted source.  It also visibly
    renders the Roudneff--Sturmfels citation as `[?, quoted in]RS88`, caused by the
    malformed `\cite[quoted in][]{RS88}`.  Use the citation syntax supported by
    the loaded packages (normally `\cite[quoted in]{RS88}` here), restore the
    missing source text, rebuild from a clean directory, and inspect the resulting
    bibliography before submission.

14. **NOTE -- Attribution and numerical claims that do check out.**

    * Roudneff--Sturmfels is a fair source for the conjecture attributed to
      Cordovil--Las Vergnas, and their paper proves mutation connectivity for the
      realizable/general-position setting.  It would be more precise to write
      "attributed by Roudneff--Sturmfels to Cordovil and Las Vergnas."
    * FMM13 Table 1 really prints `(9,276,601)` at `(4,9)` and `(5,9)` (archived
      source lines 248--277).  Their definition of reorientation equivalence
      includes relabelling (lines 561--581), so this is the same quotient counted
      by the note.  The wording "print" is appropriately cautious about the
      computational lineage.
    * Knauer--Marc Table 1 really prints `482` at `(9,3)` and `4382` at its dual
      `(9,6)` (archived source lines 585--600).  FMM13, Finschi, and the local
      `cat_3_9.txt` all give `4,382`.  The proposed erratum is justified.
    * The local twenty `(9,4)` level files contain 9,276,595 rows.  Their
      stabilizer histogram gives 8,913 nontrivial classes and orbit mass
      `1,722,704,635,330,560`.  The 2,628 extension rows independently recombine
      to the same integer and have `sum E_c = 176,265,330`.  `meta.json` agrees on
      150,561,898 directed traversals, 20 stored levels numbered 0--19,
      permutation order 362,880, and full holonomy.  Thus every headline number in
      the note matches the local artifacts; the defect is certificate scope, not
      an arithmetic mismatch.

15. **SERIOUS -- arXiv readiness.**

    Location: the note as a whole.

    The central finite-range result appears credible and worth disseminating, but
    submission should wait.  At minimum: correct Knauer--Marc attribution and the
    novelty statement; prove the reduction rather than wave it away; remove the
    universal stabilizer-parity claim; align the public-data and certificate
    rhetoric with what is actually shipped; account rigorously for rank 2; and
    rebuild a synchronized PDF with resolved citations.  With those changes, and
    preferably with an immutable full coverage dataset/checker, the note should be
    suitable for arXiv:math.CO.

## Single most important fix

Publish a complete, independently checkable `(9,4)` coverage/count certificate
(full distinct representatives or equivalent auditable data, exact stabilizers,
and a standalone checker), or withdraw the claim that the mass identity and class
count are publicly certificate-backed; that trust-boundary mismatch currently
affects both the headline correction `9,276,601 -> 9,276,595` and the proof that the
quotient search covered every class.
