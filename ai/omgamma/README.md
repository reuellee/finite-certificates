# omgamma — mutation-graph connectivity of uniform oriented matroids, n ≤ 9

**Target**: the Cordovil–Las Vergnas mutation connectivity question in
the three-level formulation of Knauer & Marc (arXiv:2002.11403, EJC 112
(2023) 103714): the labeled graph $\overline{\mathcal{G}}^{n,r}$, the
reorientation-class graph $\mathcal{G}^{n,r}$ (= the CLV conjecture
proper), and the isomorphism-class graph $\underline{\mathcal{G}}^{n,r}$.
Knauer–Marc settled $\mathcal{G}$ for n ≤ 9 modulo their computation on
$\underline{\mathcal{G}}$, know nothing about $\overline{\mathcal{G}}$
beyond rank 3, and *suspect a counterexample* there.

**Results** (see OMGAMMA.md for statements, proofs, and the full audit
trail; all exact integer arithmetic, stdlib + numpy):

* A lifting theorem reducing connectivity of $\overline{\mathcal{G}}$ and
  $\mathcal{G}$ to connectivity of $\underline{\mathcal{G}}$ plus a
  holonomy-subgroup computation — proved and machine-validated against
  brute-forced labeled graphs at six small (n,r).
* Independent from-scratch catalogs of uniform-OM isomorphism classes
  (extension generation + canonicalization anchored to Finschi's
  published representatives), reproducing every published count and
  exposing a typo in Knauer–Marc's Table 1 (482 → 4382 at (3,9)).
* Connectivity verdicts with standalone certificates: all three graphs
  are CONNECTED for every rank at n ≤ 8, and for ranks 1,2,3 and
  coranks ≤ 1 at n = 9. (9,4)/(9,5): see OMGAMMA.md Section 6/8 (final
  campaign).
* Mass-formula (orbit-stabilizer) completeness certificates; the
  (4,9) class count arbitration between Finschi's database / Knauer–Marc
  (9,276,595) and Fukuda–Miyata–Moriyama 2013 (9,276,601).

**Verify**: `python verify_omgamma.py` — runs the standalone checkers
(`checker.py` pure python, `checker_fast.py` numpy; zero code shared
with the generators) on the shipped certificates, plus a sabotage
canary. Regenerate everything: `test_core.py`, `test_canon.py`,
`test_extend.py`, `test_flip.py`, `masscheck.py`, `runcat.py`,
`runflip.py`, `ext_count.py`, `runbig.py`.
