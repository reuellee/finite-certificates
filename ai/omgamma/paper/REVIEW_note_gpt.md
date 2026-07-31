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

---

## Postscript — re-review after the coverage fixes (2026-07-31)

### Verdict: NEEDS FIXES

The revision is much stronger. In particular, the Knauer--Marc attribution is
now fair; the non-free reduction is written out; the universal stabilizer claim
has been cut back to what the compact certificate actually contains; and the new
coverage artifact plus standalone checker close the former audit gap on the
*left-hand side of the class-count mass identity*. I do not find a new numerical
discrepancy or a defect in the restricted canonicalization algorithm.

It is not yet submit-ready, however. The coverage artifact contains class keys
and stabilizer orders, but no mutation spanning tree (or equivalent reachability
witness) for the 9,276,595 quotient vertices. Consequently it certifies the
catalog side of the count, not the claim that all those vertices were reached in
one component. The latter still relies on reproducing or trusting the disk BFS.
The new honesty section says that only the extension target is
reproducible-only, so it leaves a material trust boundary undisclosed. There are
also three smaller but definite overstatements: the unqualified mass-certificate
language in the abstract and Introduction, the unconditional odd-`n` dichotomy
in the abstract, and an inaccurate description of what the six canaries catch.

I reread the revised TeX, `coverage_checker.py`, `MANIFEST.json`, the local
full-run log, and the relevant tracked/untracked status. The local log records a
FULL run over all 9,276,595 rows: 18 checks passed, 0 failed, in 510 seconds,
after 22,544,370 admissible relabellings; its histogram and mass agree with the
manifest. Python was not available on the re-review shell, so I could not
independently rerun even sampled mode in that pass. This does not affect the
source audit below, but the log itself is ignored and is not an immutable
verification record.

### Disposition of the original findings 1--11

1. **RESOLVED (originally SERIOUS) — Knauer--Marc attribution and novelty.**
   Abstract lines 32--43, Introduction lines 81--115, computation lines 338 and
   354--359, and “Relation to [KM23]” lines 502--512 now say explicitly that
   Knauer--Marc proved labelled rank 3 for every `n`. The revision identifies the
   genuinely new labelled cases exactly as `(8,4)`, `(9,4)`, and the dual
   `(9,5)`. The quotation of their lack of knowledge beyond rank 3 and their
   suspicion of a counterexample remains faithful. Minor drafting point only:
   abstract lines 40--42 should add “elementary rank 2” to the cases accounted
   for; the displayed list of new cases is nevertheless correct.

2. **RESOLVED (originally SERIOUS) — published versus publicly archived.**
   Lines 506--510 now accurately call Knauer--Marc's computation published and
   distinguish the absence of publicly archived code, data, or certificates.
   Lines 93--115 and 510--512 restrict the claimed answer to `n <= 9` and do not
   purport to settle the global labelled question.

3. **NOT RESOLVED (originally SERIOUS) — coverage/count trust boundary.**
   The principal count-side defect *is* fixed: the 62,185,111-byte NPZ contains
   9,276,595 strictly ordered 126-bit keys and stabilizer orders; its container
   and raw arrays are hash-pinned by the tracked manifest; and the standalone
   checker verifies validity, restricted canonicality, distinctness, exact
   stabilizers, and the left-hand orbit mass without importing project code.
   That is a real certificate for the enumerated catalog.

   It is not, however, a coverage certificate for quotient-graph connectivity in
   the sense used at lines 379--380 and 396--399. Neither the NPZ nor
   `coverage_checker.py` contains or checks a parent edge or mutation path for
   each listed class. The checker computes mutability only to form the colouring;
   it never checks that the 9,276,595 keys form a connected mutation graph, or
   even that each non-root key has a certified path to the root. The compact
   holonomy certificate contains root paths for only the few hundred classes used
   by its generators (lines 430--434). Thus the artifacts show “these are all
   classes” conditional on the extension target, while “the BFS reached them all
   from one root” remains a reproducible search assertion. Lines 414--416 and
   481--483 currently imply otherwise.

   There is also a distribution issue to settle before submission. Local `HEAD`
   was two commits ahead of `origin/main` during review; the checker and tracked
   manifest were not in the inspected remote tip, the NPZ is deliberately
   gitignored, and the manifest says only “the archived release attached to the
   repository” without an exact release URL, tag, DOI, or asset name. I could not
   identify an immutable release from the information recorded in the manuscript
   or manifest. If the release already exists, cite its exact locator and pin it
   to this checker/manifest; if it does not, lines 51--54 and 436--444 must not yet
   say “public” or “published.”

4. **NOT RESOLVED (originally SERIOUS) — mass-identity qualifications.**
   Computation lines 363--385 are now excellent: “structurally independent” is
   the right term; all four hypotheses are stated where the identity is used;
   the first three are tied to the coverage checker; and the extension target is
   expressly not certified. Honesty lines 473--483 also describe the target-side
   limitation accurately. But abstract line 47 still says the count is
   “certified by an exact mass identity,” and Introduction lines 127--132 still
   call the target “computed independently” and say without qualification that a
   missed-class search “cannot overshoot.” Those summaries are stronger than the
   proof's own trust statement. They should say “structurally independent” and
   either carry the hypotheses and target limitation or use “computed/proved by”
   rather than unqualified “certified.”

5. **RESOLVED (originally SERIOUS) — all-rank case split.**
   Lines 329--352 now dispatch degenerate ranks mathematically, give an elementary
   rank-2 model and connectivity argument, invoke Knauer--Marc for rank 3, and
   state the explicit dual chirotope formula. The rank-2 sentence is terse: for
   maximal clarity it could say that a mutation swaps the corresponding adjacent
   antipodal pair in the signed cyclic order. That is an exposition improvement,
   not a remaining computational-coverage gap.

6. **RESOLVED (originally SERIOUS) — non-free reduction.**
   Lines 230--246 define voltage ambiguity, root transport, and the two generator
   families. Lines 249--270 give the needed two inclusions and the telescoping
   factorization, including terminal stabilizers. Lemma 1 is left as standard
   quotient-path lifting, but the non-free part on which the paper depends is now
   proved at a publishable level.

7. **RESOLVED (originally MINOR) — reorientation-component formula.**
   Lines 278--285 now explicitly identify components of the reorientation
   quotient as the normal sign-subgroup orbits and derive
   `Gbar : Rbar H = S_n : pi(H)`.

8. **RESOLVED (originally MINOR) — group action and kernels.**
   Lines 182--207 supply the semidirect multiplication, write the sign action
   unambiguously, restrict the reduction to `2 <= r <= n-2`, and use only that
   `K_4` acts trivially. The degenerate cases are handled separately.

9. **RESOLVED (originally MINOR) — odd-`n` module argument and computation.**
   Lines 297--307 now give the elementary transposition proof of irreducibility.
   Lines 309--319 correctly distinguish the weight-span computation for
   `n=5,...,10` from exhaustive RREF enumeration only through `n=7`, and lines
   321--325 say the proposition is explanatory rather than load-bearing.

10. **RESOLVED (originally SERIOUS) — stabilizer parity.**
    Lines 388--395 make exactly the supported statement: the 73
    stabilizer-derived generators *in the shipped certificate* are even and
    generate `A_9`, one odd edge voltage supplies the other coset, and no claim
    is made about complete family (i). This matches the artifact scope and
    removes the former universal assertion.

11. **RESOLVED (originally NOTE) — degenerate ranks, duality, and resume.**
    Lines 329--352 include the empty-GP/folded-cube argument and explicit duality
    formula and explain mutation transport. Lines 401--409 correctly preserve
    the one-sided resume logic: the harvested subgroup is a lower bound, and a
    lower bound equal to the ambient group proves the positive result but could
    not prove a negative one.

### Audit of the new certificate language

The two principal qualifications at lines 463--483 are technically accurate.

* **Restricted canonicalization:** `coverage_checker.py` does not maximize over
  all `S_9`. It derives mutable bases from the GP table (lines 272--282), builds
  the degree/pair-incidence colouring and up to three equivariant refinements
  (285--315), sends each colour class to its designated block and enumerates all
  within-block permutations (318--336), and then maximizes over the independently
  rebuilt sign lattice (354--361). Because mutability is invariant under
  reorientation/global sign and equivariant under relabelling, this normalization
  really is a function of the full `G'`-orbit. Strictly different normalized keys
  therefore certify inequivalent classes even though the keys are usually not
  global lexicographic maxima over `S_9`. The manifest describes the same
  convention. The paper is right that orbit-invariance, not the bare word
  “extremal,” carries the distinctness argument.

* **Target side:** the checker hard-codes the target at lines 69--70. Its
  `--extcount` path (lines 544--569) checks parent IDs, divisibility, and the
  arithmetic sum of the tracked table; it does not recompute any extension count
  or the 2,628-parent catalog. Calling that side reproducible-only is exactly
  right. The disclosure must be expanded, however, to include quotient
  reachability as explained in finding 3.

The abstract's attribution and finite-range novelty claims are now accurate, but
two claims remain too strong. First, “certified by an exact mass identity” is not
consistent with the admitted reproducible-only target unless qualified. Second,
abstract lines 49--50 state the odd-`n` dichotomy unconditionally. Proposition 3
requires the isomorphism quotient to be connected and `pi(H)=S_n` (equivalently,
in this setting, connectivity at the reorientation-class level). Without those
hypotheses an additional permutation index is possible. The abstract should say
“when the reorientation-class graph is connected” or state the proposition's two
hypotheses.

### New defects in the revision

12. **SERIOUS — the new honesty section omits the quotient-reachability trust
    boundary.** Locations: lines 414--416, 430--454, and 481--483. Catalog
    validity/completeness and graph connectedness are different assertions. Add
    a full mutation spanning-tree certificate/check, or state that the assertion
    that the complete catalog was reached from one root is reproducible-only.

13. **MINOR — the six-canary description is false as written.** Locations:
    lines 456--461. The checker source expressly makes canary 6 an exception:
    the stale-hash canary keeps a stale manifest and is intended to be caught by
    check (0). The truncated-array canary deliberately does *not* repair totals
    and is intended to be caught by count/mass arithmetic. Only the first four
    mathematical sabotages have refreshed hashes and repaired totals so that the
    substantive checks must catch them. Replace “Each ... so that none” by this
    three-way description.

14. **SERIOUS — the abstract omits the hypotheses of Proposition 3.** Location:
    abstract lines 49--50. This is a mathematical overstatement, although it does
    not affect the proved `n <= 9` theorem.

15. **MINOR — public availability is not made auditable.** Locations: abstract
    lines 51--54 and honesty lines 436--444. Give the exact immutable release
    locator and asset name/hash, and ensure the commits containing the checker
    and manifest are public before arXiv submission.

The retraction at lines 485--500 remains adequate: it names the omitted generator
family, explains the false negative-looking signal and the code-path gap, states
the corrected result, and does not pretend that the old observation retains
evidentiary value. I would keep it substantially as written. All headline
numbers still agree internally: 9,276,595 classes; stabilizer histogram
`2:9267682, 4:8717, 6:73, 8:106, 12:16, 36:1`; 8,913 nontrivial stabilizers;
mass 1,722,704,635,330,560; and 150,561,898 directed traversals. I found no new
numerical defect.

### Readiness

**NEEDS FIXES**, not rejection. The mathematical strategy and reported positive
result remain credible, and most of the original report has been answered
substantively. Before arXiv:math.CO, disclose or certify full quotient
reachability, qualify the abstract/Introduction mass rhetoric, restore the
dichotomy hypotheses in the abstract, correct the canary paragraph, and provide
an exact public release locator. These are localized changes except for a full
spanning-tree certificate, which is optional if the paper candidly labels that
part reproducible-only.

## Single most important fix after re-review

Do not say that only the extension target is reproducible-only: either publish a
checkable mutation spanning tree (or equivalent reachability witness) covering
all 9,276,595 quotient classes, or state explicitly that the coverage artifact
certifies the catalog/count side but that one-component reachability still relies
on reproducing the disk BFS.
