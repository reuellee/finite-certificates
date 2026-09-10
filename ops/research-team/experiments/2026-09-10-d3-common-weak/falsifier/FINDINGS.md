# Falsifier handoff

**No original diagonal-three obligation is closed or refuted.**

Two exact actual-geometry results are proved:

1. The three sign patterns in the previous transverse noninjectivity example lift to the actual original proper antichain with signatures `1115179617623167`, `1110781571112063`, `1115179340274814`. Thus the tangent pattern is not excluded by the original admissibility condition. Three same-parent-component arcs provide one-hot GOOD/BAD separation certificates.
2. A fourth arc in the same original triple-bad locus has a strictly positive rank-four Gordan witness for every signature. None of the three weak-primal cones contains a nonzero vector. This disproves a universal common-weak-projective-point resolution of the entire original triple-bad locus for these actual admissible signatures.

The previous transverse kernel still is not an original compact-support class. Seven omitted parent directions and global attachments remain material. A conventional argument now identifies a four-dimensional open convex height factor in the connected common-zero/sign stratum of the example. This gives Hc vanishing below degree four for that fiber-saturated stratum, and for coefficients locally constant on the height fibers. An exact elimination reduces the five active inequalities near it to four affine halfplanes. A global tubular comparison carrying the original cohomology restriction diagram is explicitly not yet proved; if established, it would place the local degree-one kernel in total degree at least five.

The complete proof discussion and limitations are in `COMMON_ZERO_STRATUM.md`. The acceptance producer is `actual_antichain.py`, with exact polynomial witnesses in `ACTUAL_ANTICHAIN.json`. All four arcs have the full parameter interval `0<t<=1/100000000`; the parent bracket signs are certified also at t=0. Every claimed GOOD/BAD status retains all 56 original inequalities. The first three arcs prove both properness and pairwise incomparability in the same parent component. Positive normalization and a continuous projective frame take the literal matrices to the original normalized parent component.

Smallest discriminating next action: a boundary-only common-weak-point argument must specify precisely which cohomology-support strata it covers, prove the full local restriction diagram is locally constant along the convex height fibers, and account for attachment to other weak-primal patterns and strict triple-bad interior. The fourth arc demonstrates why the resolution cannot simply be applied to all of T.

Input provenance: the explicit parent, base signing, and support labels come from `checkpoint/previous_checkpoint/falsifier/certificate.json`; the transverse map being challenged comes from `checkpoint/falsifier/TANGENT_AUDIT.json`; original scope comes from `checkpoint/inputs/ATLAS_HELLY.md` and `WORK_ORDER.md`. Independent review was requested from the referee; acceptance should follow that review rather than this producer alone.

## Final independent challenge of the common weak-primal theorem

A bounded independent challenge of `pair/COMMON_WEAK_PRIMAL_VANISHING.md` found no load-bearing mathematical fault. This is a challenge report, not a second independent proof. The following points were specifically checked:

- The four signed basis inequalities supply a fixed pointed orthant and a compact simplex; the common weak-primal comparison is proper with compact convex fibers.
- The exact-zero partition arises from a finite closed zero-count filtration. Strata with a fixed zero count and distinct exact zero sets are clopen in that difference, so closed/open localization handles extra-zero attachments.
- Uniformity supplies a projected projective frame even with a parallel pair or loop. The loop case has dimension three after its independent column scaling; the no-loop case has dimension four.
- Every zero projected triple has rank two. Its derived normal varies only by a positive scalar on the full parent height cell, so every simultaneous-badness condition is fiber-saturated. Restricting to one parent component retains whole connected fibers.
- Shriek base change gives the claimed low-degree vanishing without properness of the height projection or an orientation trivialization.
- Excision uses the same closed common-weak subset W in all three pair loci and the triple locus. The localization isomorphisms commute with the restriction maps, so they preserve the original kernel.

Two requested clarifications do not alter that argument. First, the phrase 'Strictly infeasible systems have weak-primal cone {0}' is incorrect if 'strict infeasibility' means simply membership in B_sigma, as in the statement; it should instead directly say that systems with weak-primal cone {0} lie outside W_S. Second, one may take every contraction map into the ambient fixed sign/zero realization stratum and allow empty fibers, avoiding an unnecessary local-compactness assumption on its image. These clarifications were sent to the coordinator. The theorem does not imply the remaining complement vanishes, and the actual fourth arc remains a concrete nonempty complement example.
