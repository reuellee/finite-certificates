# Outside consult on the (4,9) sweep — GPT-5.6 Sol, 2026-08-02

The running sweep, the completion-LP tool, the minor-closure picture and the
BFP-completeness question were put to GPT-5.6 (17 min of reasoning) with an
explicit invitation to answer "the sweep is already near optimal". Summary,
with our assessment. **Nothing here has been implemented; items are ranked
by what survives scrutiny.**

## Its bottom line: let the sweep finish

No symmetry or duality theorem removes enough of the realizable 98% to
justify replacing a working, auditable computation with nine hours left. We
agree, and this matches the theory-first rule: the cut has to be worth more
than the run it replaces.

Explicitly ruled out by it, each correctly:
* reorientation symmetry — already exhausted by the catalog quotient;
* (4,9)/(5,9) duality — gives the *other* cell free (as FMM13 did for
  (3,9)→(6,9)) but does not halve this one;
* mutation-tree ancestry — realizability is **not** inherited along edges,
  so a subtree under a non-realizable parent cannot be cut;
* one failed fixed-deletion LP — excludes one realization, not the class.

## It independently confirmed our own correction

On the completion LP: "Feasibility over A proves M realizable. Infeasibility
proves only: *this particular realization A of D cannot be extended.*" It
adds the moduli count — a uniform 8-point configuration in RP³ has
8·3 − dim PGL₄ = 24 − 15 = 9 moduli, and a fixed chirotope imposes open sign
conditions, not equations, so no projective-uniqueness shortcut exists. This
is the same limitation the GPT-5.6 code review found and that
`OPEN_ATTACK.md` now records; two independent derivations agree, and it
notes our use is sound because every outcome was feasible.

## Worth doing — ranked

**1. Component cut as a POST-SWEEP CROSS-CHECK (our repurposing, high
value).** It proposed: let B be the certified non-realizable set; in G − B
every realizable vertex lies in the component of a known realizable seed,
because the realizable induced subgraph is connected (Roudneff–Sturmfels),
so every *other* component is non-realizable en masse. Verified by us as
valid reasoning. It offered this as a *speedup* needing full mutation
adjacency, which we do not want to build mid-run — but as a **verification**
it is excellent: once the sweep finishes, the non-realizable set should be
exactly the complement of the seed's component. That is a whole-catalog
consistency check of the final split, independent of every certificate,
and it reuses our own connectivity theorem. **Do this after the sweep.**

**2. Certificate cores instead of minors (best answer to the ~10⁴
minor-minimal residue).** Reduce each BFP/Gordan certificate to an
inclusion-minimal positive dependence (an extreme ray of the nonnegative
kernel), keep only the bracket signs actually used, canonicalize that
partial signed pattern under relabeling/reorientation, then apply it to
every catalog class matching those signs. One core can refute many
chirotopes. This reframes the omminor negative result: the minor-minimal
classes are templateless *as minors*, but may collapse into few **core
orbits**. Suggested clustering invariants: minimal BFP support size, the
coloured incidence hypergraph of its GP relations, Euclidean status,
deletion multiset, automorphism group. Richter-Gebert's classification
programme proposed something similar. **This is a real research direction
and supersedes part of `ai/omminor` §7's pessimism.**

**3. Deletion-fiber chamber flooding (park for om410, not for now).** Fix a
realizable deletion D = M∖p with exact realization A ∈ ℤ^{4×8}; the 56
hyperplanes ℓ_I(x) = det(a_i,a_j,a_k,x) partition RP³ into chambers, and
**every** uniform extension realizable over A is exactly one chamber. At
most 2·Σ_{j≤3} C(55,j) = 55,552 cones, 27,776 after ±identification. So one
realization can mark thousands of catalog classes realizable at once, with
a rational witness each. Break-even ≈166 core-seconds for an average
deletion class. Correctly flagged as not worth building with nine hours
left — but this is a *generator* for realizable (4,10) classes and belongs
in `ai/om410/SCOPING.md` as a sampling primitive.

**4. Lift the 24 stored certificates rather than re-running the BFP LP.**
This is our Proposition R; it independently derived the same lifting, and
adds the **contraction** case we had ruled out as unusable: replace each
minor bracket [i₁…i_{r−1}] by [e i₁…i_{r−1}]. Worth checking against
`MINOR_THEORY.md` §3.

## The sharpest item, and it is unverified

It reports Richter-Gebert (Doc. Math. 1 (1996), Thm 5.1): if χ₀, χ₊, χ₋
differ in exactly one basis with values 0, +, −, and χ₀ and χ₋ are
realizable while χ₊ is not, then **χ₊ has no BFP** — and claims the proof is
pure three-term GP bracket algebra that "generalizes verbatim to arbitrary
rank by replacing the common index τ with an (r−2)-tuple".

If that generalization holds, two consequences:

* a **targeted search** for rank-4 BFP failures — look for a one-zero
  mutation wall whose two uniform perturbations differ in realizability —
  instead of enumerating UOM(4,10);
* a **corollary of our own result**: if every non-realizable (4,9) class has
  a BFP, then no such one-sided realizable wall exists on nine elements.

**Neither the theorem statement nor the generalization has been checked
against the primary source.** See the scope caveat in `LITERATURE.md`:
DS4 calls Richter-Gebert's Ω⁺₁₄ *non-uniform*, which may mean uniform
BFP-incompleteness is not established in the literature at all. Read the
paper before any of this is used.

## Claims to verify before reuse

* "Among the 24 non-realizable uniform (4,8) classes only 18 are
  non-Euclidean; the other six are Euclidean and still have BFPs." Specific
  and checkable; we do not compute Euclideanness today.
* Its rank-4 threshold prediction — no failure at (4,9), modal first failure
  n = 11, range 10–13 — rests on a moduli-dimension heuristic
  (dim = (r−1)n − (r²−1); rank 3 at n=12 gives 16, rank 4 gives 15 at n=10
  and 18 at n=11). Explicitly offered as a heuristic, not a theorem.
