# Saturation and injectivity pilot: an exact exclusion limit, still 2/9

**The combined-method pilot completed its attachment-design gate but did not obtain an injectivity proof. The ledger remains 2/9.** Independent review accepted a conditional local collar lemma and an exact counterexample to removing all witness support changes through parent-determinant saturation. The main F4SAT run was not started: no candidate supplied the required global attachment implication.

Base: `3a7ce7b5d57543d54eace7707659418cea6d69c9`, tree `7e2e958bcc7fef306bfc309c1502a279925b4ab6`. The complete September 9 archive and all its file hashes were verified before work. Historical theorem definitions and ledgers are unchanged.

## What was established

**An admitted support-change stratum cannot be discarded.** In the original row-2599 parent chamber, with the three fixed proper incomparable signatures `14988895318912`, `3405195891438080`, and `40418075143643136`, move the second coordinate of parent column 2 by

`37864449186859942661765893 / 7029591949415530407677535`.

All 70 parent determinants retain their nonzero signs. All three blocks have normalized nonnegative Gordan witnesses. One selected block-0 weight becomes zero while its other four weights remain positive. The five selected normals have rank four, the four surviving normals have rank three, and the augmented witness system has rank five. Thus this support event need not be an augmented-system singularity.

The resulting point annihilates all sixteen generators of the supported-witness event ideal, while every parent determinant is nonzero. Evaluation at that rational point proves that the ideal remains proper after saturation by any product of those parent determinants. An identity excluding all such events cannot exist over the rationals. This conclusion needs no modular solver run.

The event may be topologically harmless. It does not prove a change in the bad loci, a cohomological kernel, or failure of a collar. At nearby points the selected support changes positivity; block-0 badness on the right is not established by this calculation. These distinctions are explicit in the certificate and independent review.

**A conditional local collar is available.** Where one factor of the actual normal minors vanishes smoothly and every other relevant factor stays nonzero, the signs of all minors are constant on the two sides and the zero cell. Consequently the actual bad loci, their pairs, and the triple have a simultaneous local product description. Zero weights remain included. The candidate singularity exclusion is

`<q, partial_1 q, ..., partial_9 q> : u^infinity`.

This is a parametric formula, not a computed ideal instance or saturation certificate. Nonparent factors in u are units only on that restricted branch. Their zero loci, overlaps of factors, global component topology and true parent infinity remain unresolved. The local collar supplies no original global frontier block.

## Why the computation gate did not open

| Examined route | Exact missing input |
|---|---|
| Extend the local collar to the original pair map | A proper global comparison carrying the collar data to oriented frontier blocks, including excluded strata and infinity |
| Certify a mixed comparison prism by saturation | The actual polynomial prism family on the full original domain with all prescribed seams |
| Exclude critical points to prove detector nondegeneracy | A specified global stratified argument connecting that exclusion to every nonzero original pair class |

The direct degree-one cochain test of the combined map D can use degrees zero through two once the genuine global compact-support model is certified. The small normal slice is not that model. The older balanced-end N/M formula also assumes the still-open triple Hc0 vanishing; this pilot did not assume it.

This retires only the universal support-deletion shortcut. It does not disprove narrower saturation-assisted attachment methods. No construction-ready successor was obtained, and increasing the algebraic search budget would not supply the absent geometric input.

## Review and verification

The constructive and falsification tracks used isolated branches. A third agent independently reconstructed the arithmetic with different determinant/rank algorithms and audited the written proof and its scope. Its final verdict is **ACCEPT_AUXILIARY_AND_SCOPED_NEGATIVE_ONLY**.

| Gate | Result |
|---|---|
| Exact base, source and recovery accounting | PASS |
| Conditional local collar and real bad/good witness encodings | Accepted within stated restricted scope |
| Exact original-domain support event | Independently accepted; 70 brackets, 15 weights, 3 admission anchors, 6 noninclusions and 3,780 GP relations checked |
| Independent corruption controls | Altered weight and shifted event rejected; producer additionally has four controls |
| Integrated source, event, independent replay and cycle protocol | PASS |
| Original global attachment / injectivity | NULL; no frontier block or original obligation closed |
| F4SAT / modular runs | Zero; main compute gate NO_GO |

The independent referee is raw commit `113d8d202220e4795b09f164e642407354302e24`, integrated before closing. Eleven candidate files and sixteen inherited sources are pinned. A reversed localization sentence and a timing-related replay write were corrected before acceptance. New exact replays use the Python standard library and leave the checkout clean. Written topology received independent agent review, not proof-assistant or external human certification.

Main independent replay:

```sh
python -B ops/team/d3-satinj-referee/verify_frozen_candidates.py --prover-revision 3c3ccbcac95fe05543a870c86da1b2d29342f526 --falsifier-revision 1f8be67c47679d4283edec4b67ba3ae70c1c4818
```

Full findings, candidate equations, raw discovery provenance, source pins and separate verifier are in the three `ops/team/d3-satinj-*` directories.

## Mandatory solution-convergence verdict

Opening proof-distance vector: `(2/9,1,{pair Hc1,triple Hc0},7,UNKNOWN,UNKNOWN,12,15)`.
Closing proof-distance vector: `(2/9,1,{pair Hc1,triple Hc0},7,UNKNOWN,UNKNOWN,13,16)`.

Mid-cycle convergence check: discovery stopped at the first structural null. The conditional collar lacked global attachment, and the exact event defeated universal support deletion. Subsequent work completed the frozen certificates, independent review and recovery. The saturation budget was neither activated nor expanded.

Trajectory classification: **STALLED** for the theorem endpoint. The auxiliary result is informational. The minimum acceptable decrease was not met: zero original obligations closed, zero certified exhaustive residual decrease. All seven original obligations remain open. Triple source counts stay 77,940,147 settled / 79,102,449 total / 1,162,302 unresolved; these are not component counts. Pair coverage and residual remain UNKNOWN.

Automatic strategy-reset result: retire the precise universal support-deletion candidate; **STOP** this attempt. Same-route continuation justified: **NO** on current inputs. Comparable prior accepted closes had counters 10/13, 11/14 and 12/15 with the same original invariants open.

## Recovery and authority

The complete recovery package preserves the final branch, all raw worker histories, original source data, this report, exact manifests and a clean-restoration replay. The final local revision/tree and measured bundle digest are recorded in its external RECOVERY_MANIFEST.json to avoid a self-referential commit hash. The three delivery volumes reassemble the full package and require no earlier checkpoint.

The branch is `research/d3-saturation-injectivity-20260909`. GitHub remains read-only; no public publication, CI trigger or merge occurred. No human was contacted and no paid compute/API was used. The checkpoint is saved with a recovery mirror under the authorized Projects/research-backups folder.
