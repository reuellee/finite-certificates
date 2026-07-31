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
* Connectivity verdicts with standalone certificates: **all three graphs
  are CONNECTED for every rank at every n ≤ 9** — including the labeled
  graph $\overline{\mathcal{G}}^{n,r}$, the level where Knauer–Marc
  suspect a counterexample. **There is no counterexample below n = 10.**
  The last open case, (9,4) (≅ (9,5) by duality), was settled by an
  exhaustive BFS over its 9,276,595 isomorphism classes and
  150,561,898 mutation-edge traversals.
* Mass-formula (orbit-stabilizer) completeness certificates; the
  (4,9) class-count discrepancy between Finschi's database / Knauer–Marc
  (9,276,595) and Fukuda–Miyata–Moriyama 2013 (9,276,601) **resolved in
  favour of 9,276,595** by an exact integer identity between two
  structurally different sweeps.
* A dichotomy proposition (`submodules.py`): once π(H) = S_n, the sign
  part of the holonomy is an F₂[S_n]-submodule of {0,1}ⁿ/⟨1ⁿ⟩, which for
  ODD n is irreducible — so #components of the labeled graph is
  2^{n−1} or 1, nothing in between.
* At (9,4): **H = Ḡ**, hence the labeled graph has exactly as many
  components as the isomorphism-class graph (no counterexample at the
  labeled level over what happens at the quotient).

**Verify**: `python verify_omgamma.py` — runs the standalone checkers
(`checker.py` pure python, `checker_fast.py` numpy; zero code shared
with the generators) on the shipped certificates, plus a sabotage
canary. Deeper canaries: `canary_checker.py` (five certificate
corruptions), `canary_resume.py` (six checkpoint corruptions),
`submodules.py` (its own two-method cross-check).
Regenerate everything: `test_core.py`, `test_canon.py`,
`test_extend.py`, `test_flip.py`, `masscheck.py`, `runcat.py`,
`runflip.py`, `ext_count.py`, `runbig.py`.

**Long runs**: `runbig.py <r> <n> <workers> [cap]` checkpoints every
level to `data/big_<r>_<n>/level_*.npz`; `--resume` restarts from the
last checkpoint (state gate + sample re-canonicalization);
`--holopass <lo> <hi>` re-expands a class range for holonomy harvesting
only and doubles as a mutation-closure certificate; `certify.py` builds
a standalone H = Ḡ certificate from any checkpoint;
`export_subcert.py` emits a compact checkable certificate.
