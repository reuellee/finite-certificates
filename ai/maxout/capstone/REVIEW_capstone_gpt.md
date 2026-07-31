# Adversarial review of `CAPSTONE.md`

**Verdict: ACCEPT WITH RESERVATIONS.**

The exact certificate obstruction, its specialization semantics, and the
chirotope/split-orbit accounting survive review. I found no counterexample
to the claimed value 42. There is, however, one omitted coefficient boundary
case and a related generic-perturbation omission that should be repaired in
the written proof before it is cited as a theorem.

1. **SERIOUS — the weight/split normalization omits `a_i=b_i>0`.**  
   **Location:** `CAPSTONE.md` §1, lines 20–27 and 36–44; §3.1, lines
   133–138; §3.4–3.5, lines 203–229.

   Put \(\delta_i=a_i-b_i\), absorbing the segment half-length into
   \(|\delta_i|\). The split \(s_i=\operatorname{sign}\delta_i\) and the
   strict row \(w_i>0\) exist only when \(\delta_i\ne0\). Full support of
   both copies does **not** imply this: \(a_i=b_i>0\) leaves both zonotopes
   with that generator but gives residual weight zero. Such an index is
   neither a “copy misses a generator” case in §3.1 nor necessarily a side
   equality. Consequently, the sentence “from here on ... both copies have
   full support” does not justify passage to \(s\in\{\pm1\}^5\), and the
   strict-44 chain as written does not quantify over every coefficient
   pair.

   This appears locally repairable. If a 44-vertex instance existed on this
   boundary, its finitely many strict exposing witnesses would persist
   after a sufficiently small perturbation of the actual \(a,b,m\)
   parameters. One may choose that perturbation so every \(a_i-b_i\ne0\)
   while retaining positivity and simultaneously avoid the finitely many
   side hyperplanes. The result would be a full-residual, strict
   44-instance, already contradicted by §3.4. For a 43-instance the same
   perturbation preserves at least 43 vertices and feeds the parity step.
   This reduction must be stated before §3.2; the current §3.5 perturbation,
   which assumes an existing \(w\in\mathbb R_{>0}^5\), does not itself
   cover the omission.

2. **SERIOUS — the parity closure needs a fully generic parameter
   perturbation, not merely removal of side equalities.**  
   **Location:** `CAPSTONE.md` §1, lines 29–34; §3.5, lines 215–230.

   Genericity of \(U\) makes the common normal fan simple, but by itself
   does not exclude coincidences between a support vertex of \(Z^a\) and
   one of \(Z^b\), or other accidental candidate identifications. Strict
   nonzero values on the twenty facet rays are different conditions. The
   literal identity
   \(f_0=22+\#\{\text{bicolored chambers}\}\), and hence the inference that
   odd \(f_0\) is impossible, needs the normal-fan subdivision to have no
   such identifications.

   Again the repair is short: in the perturbation of a hypothetical
   43-instance, preserve one strict witness for each of its 43 distinct
   vertices and also avoid the finite algebraic locus of cross-copy
   candidate coincidences (as well as residual zeros and side
   hyperplanes). Then the perturbed instance has at least 43 vertices and
   is in the regime where the cycle parity applies, forcing 44. A
   44-instance already has 44 distinct contributing candidates, so this
   issue does not affect §3.4.

3. **MINOR — the prose conflates the physical copy swap with the
   row-system flip convention.**  
   **Location:** `CAPSTONE.md` §3.2, lines 166–174;
   `capstone/check_transport.py`, `flip_bits`.

   With fixed geometric ray labels, physically swapping the copies sends
   \((T,s,\sigma)\) to \((-T,-s,-\sigma)\); it does not itself swap the ray
   labels. The implemented involution instead keeps the numerical \(T\)
   coordinate and sends
   \((s,\sigma)\) to \((-s,-\operatorname{swap}(\sigma))\), which is the
   physical swap composed with antipodal ray relabeling. The displayed row
   identity is correct and is all the proof needs. I also checked that this
   flip is an involution and maps the complete 33,140-pattern valid set
   onto itself. Thus this is a convention-description error, not a gap in
   complement-split coverage.

4. **MINOR — the dependency claim in the verification manifest is
   inaccurate.**  
   **Location:** `CAPSTONE.md` §4, lines 241–257.

   `check_transport.py` imports `gp_degree3_search.py`, which imports
   NumPy, SciPy, and SymPy; `check_stage2c2.py` also needs the scientific
   stack. They are not stock-stdlib checkers. The two explicitly marked
   orbit checkers and `verify_c66_new_cases.py` are stdlib-only.

5. **NOTE — independent checks performed.**  
   **Locations:** the §2 artifacts and §4 manifest.

   I reproduced:

   - 384 uniform rank-3 chirotopes in one orbit;
   - stabilizer order 10 and exactly the two claimed 2-subset split orbits;
   - the complete Stage 2c-2 exact checker PASS;
   - `ALL TRANSPORT CHECKS PASS`;
   - the exact stdlib verification of the 42-vertex instance.

   I additionally checked from the compressed artifacts that the prefix
   shards are exactly the non-family complement for \(k=1,2\), that the
   \(k=0\) and \(\{0,2\}\) bundles each contain every one of the 33,140
   valid labeled patterns exactly once, and that the committed full audit
   reports 132,681 audited entries with zero failures. Independently of
   specialization at `U_ints`, the symbolic semantics are sound: the five
   symbolic \(T\)-equations are dot products with the spanning vectors
   \(u_t\), so their vanishing modulo the signed Plücker ideal forces the
   three-vector \(T\)-coefficient to vanish at every realization; positive
   \(D\)'s make every nonzero nonnegative-coefficient multiplier genuinely
   nontrivial. The optional cddlib rerun was unavailable because `cdd` is
   not installed, but the exact stdlib attainment verifier passed.

## Postscript — 2026-07-31: assessment after commit `c4393ff`

1. **Finding 1: RESOLVED.**  
   **Location checked:** `CAPSTONE.md` §1 and the new generic-position
   perturbation lemma in §3.1.

   The lemma now explicitly identifies the residual
   \(\delta_i=a_i-b_i\), acknowledges that the \((w,s)\) normal form
   excludes \(\delta_i=0\), and moves any hypothetical \(f_0\ge43\)
   instance into the nonzero-residual regime before §3.2.

   The proof sketch is adequate. A vertex of a finite polytope has a
   strict exposing functional relative to all other *distinct* candidate
   points. Under a sufficiently small parameter perturbation, the cluster
   of candidate indices formerly representing that vertex remains
   separated by a uniform positive margin from every other cluster; at
   least one maximizer in the cluster is a vertex. Different original
   vertices remain in disjoint neighborhoods, so at least \(v\) vertices
   persist.

   The excluded loci are genuinely proper algebraic subsets. Residual
   zeros and side zeros are nontrivial polynomial equations. For two
   indexed candidates from the same copy, their difference is a nonzero
   polynomial because some differing sign contributes a nonzero \(u_i\);
   for candidates from different copies, the independent \(a,b,m\)
   variables make the difference polynomial nonzero even when their sign
   patterns happen to agree. Thus their coincidence locus is proper, and
   a finite union of these loci cannot fill any parameter neighborhood.
   The lemma's parenthetical justification mentions differing sign
   patterns too narrowly, but this does not affect the argument.

2. **Finding 2: RESOLVED.**  
   **Location checked:** `CAPSTONE.md` §3.1 and rewritten §3.5.

   The perturbation now simultaneously removes residual zeros, side
   equalities, and candidate coincidences while preserving at least the
   original vertex count. Section 3.5 therefore applies the chamber
   identity and cycle parity only in the regime where the count is
   literal. Starting from any \(f_0\ge43\), the nearby strict-generic
   instance still has \(f_0\ge43\); parity and the cap force \(f_0=44\),
   which §3.4 excludes. This closes both the 43 case and non-strict 44
   without assuming the conclusion of the perturbation.

3. **Finding 3: RESOLVED.**  
   **Location checked:** `CAPSTONE.md` §3.2.

   The revised text correctly distinguishes the physical copy swap
   \((T,s,\sigma)\mapsto(-T,-s,-\sigma)\) at fixed ray labels from the
   implemented involution obtained after antipodal ray relabeling. The
   stated row identity is the correct algebraic transport used by the
   proof.

4. **Finding 4: NOT RESOLVED (MINOR).**  
   **Location checked:** `CAPSTONE.md` §4 and the import chains of
   `audit_all_certificates.py` and `check_transport.py`.

   The manifest now correctly says steps 3–5 are not stdlib-only and need
   NumPy/SciPy. It still says only step 3 needs SymPy. In fact steps 4 and
   5 import `gp_degree3_search.py` as well, and that module imports and
   uses SymPy to construct the signed-\(D\) Gröbner basis and normal
   forms. The accurate dependency sentence is that **steps 3–5 require
   NumPy, SciPy, and SymPy**. This is solely a reproduction-instructions
   defect and has no effect on the mathematics.

Because one minor manifest error remains, not all four findings are
resolved. The mathematical reservations are cleared: **the mathematical
verdict is ACCEPT**. The document-level verdict remains **ACCEPT WITH
RESERVATIONS** only until the SymPy dependency sentence is corrected.
