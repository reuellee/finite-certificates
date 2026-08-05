# A single-variable escape closes all but four of the labeled-pair residue

## Result

`DIAG2_PIVOT_LABELED_PAIR_THEOREM.md` certified 9,361 of the 9,476 unordered
relative-label residual-factor pair orbits as noncompact, leaving a
115-orbit residue entirely inside the pair types `(49,50)`, `(49,51)`,
`(50,50)`, `(50,51)`, `(51,51)`.

A cheaper, more general sufficient condition than any certificate family used
there closes all but four of the 6,890 candidate pairs across those five
factor-type combinations -- a superset of the 115-orbit residue, since most
of the 6,890 already had a certificate from
`DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY.py`. This checker gives an
independent, much cheaper proof that also happens to cover them, and closes
the four-family residue down to an exact four remaining pairs:

\[
 \boxed{(50,7861),\ (50,7977),\ (50,12128),\ (50,20046)}
\]

Every one of these four is independently reconfirmed, via the existing
all-frame certificate audit, to be genuinely unresolved by every prior
mechanism too (direct minor, reframed minor, all-frame minor, translation,
scaling) -- honest residue, not a rank drop or a compact component, exactly
as `DIAG2_PIVOT_LABELED_PAIR_THEOREM.md`'s own convention requires.

The exact checker is

```console
python ai/omreal/verify_diag2_affine_fiber_residue_closure.py
```

## 1. The sufficient condition

Eliminate the first wall's pivot variable using its own residual equation.
Every canonical residual type `q_k` is exactly linear in a fixed pivot
coordinate `p_k` (`a` for eight of the thirteen types, `d` for three, `f` for
one -- the same table `verify_derived_walls.py` uses, independently
re-derived rather than imported here), with `q_k = U*p_k + V` for `U,V`
polynomials in the other eight coordinates. `U` is a signed bracket product,
hence nonzero throughout the uniform realizable cell.

To eliminate `p_k` from a second polynomial `P` (the other wall of the pair)
without introducing fractions, compute

\[
                raw = U^E\cdot P(p_k\to -V/U),\qquad E=\deg_{p_k}P,
\]

an honest integer polynomial in the remaining eight coordinates. This
generalizes the elimination `d = b+f-bf` used in
`verify_diag2_pivot_49_pair_saturation.py` (there `U=1` identically, since
`q_49`'s pivot coefficient happens to be the constant unit) to every pivot,
including the genuinely nonconstant coefficients of `q_50` (`U=i`, i.e. the
bracket `[1238]`) and `q_51` (`U` a longer bracket product).

**The condition:** the restricted polynomial is affine (degree `<=1`,
including the trivial case of not depending on it at all) in *some* one of
its remaining eight variables.

## 2. Why this alone proves noncompactness

Two lemmas already established elsewhere in this repository combine to cover
every point of a hypothetical compact component `C` of the pair's common
zero locus, intersected with the open uniform parent cell `X`:

* **Fixed-minor noncompactness** (`RESIDUAL_STRATUM_NONCOMPACTNESS.md`
  section 1). If the chosen coordinate's partial derivative `A` is nonzero
  at *every* point of `C`, projection dropping that coordinate is a local
  diffeomorphism at each point of `C` (ordinary implicit function theorem,
  using only the one nonvanishing partial -- the other seven partials are
  irrelevant to this step). A local diffeomorphism is an open map, so the
  image of `C` is open in `R^7`; it is also compact, since `C` is compact and
  the projection is continuous. A nonempty open and compact subset of `R^7`
  does not exist, so `C` is empty.
* **Fiber-linear escape** (`DIAG2_PIVOT_49_PAIR_SATURATION.md` section 3).
  If instead `A` vanishes at some point of `C`, the affine identity forces
  the whole coordinate line through that point into the (purely algebraic)
  zero set -- but `C` is a component of the zero set *intersected with* the
  open cell `X`, so intersect first: let `J` be the connected component of
  (line `intersect` `X`) containing that point. `J` is connected, lies in the
  zero set intersected with `X`, and meets `C`, so `J subset C` by maximality
  of connected components. `J` is nonempty (it contains the starting point)
  and open in the line (since `X` is open), so exactly one of two things
  happens: either `J` is unbounded, in which case `C supset J` is unbounded
  too and hence not compact (compact subsets of `R^9` are bounded); or `J` is
  bounded and misses a limit point `x*` where a parent bracket vanishes, in
  which case `x*` is also a limit point of `C` (since `J subset C`) that is
  not in `C` (since `x* notin X supset C`), so `C` is not closed in `R^9` and
  hence, being Hausdorff, not compact.

Together these cover both cases (`A` vanishes somewhere on `C`, or nowhere on
`C`), so "affine in some variable" is on its own sufficient: no ideal
saturation and no smoothness certificate is required. This is strictly
weaker than what `verify_diag2_pivot_49_pair_saturation.py` proves for its
seven cases (there the localized critical ideal is additionally shown to be
the unit ideal, giving the stronger "smooth 7-manifold" conclusion, not just
"noncompact") -- but it is far cheaper to check and, empirically, almost
universal in this family: 6,886 of 6,890 candidates (99.94%) satisfy it, and
the whole sweep runs in single-digit seconds.

## 3. Scope: this does not promote diagonal two

Pair-wall noncompactness -- by any method, including this one -- is
necessary but not sufficient for diagonal two. A compact simultaneous-bad
component could still be assembled by gluing several individually-noncompact
pair-wall pieces together across points where *two different* residual
factors vanish simultaneously -- an internal transition between walls, not a
parent-bracket boundary. Crossing another residual factor's zero locus does
not remove a point from `X` (which is the uniform realizable cell where all
70 parent brackets are nonzero -- see `RESIDUAL_STRATUM_NONCOMPACTNESS.md`
section 2, "All parent brackets are nonzero in a uniform parent cell"), so it
does not by itself constitute an escape; it is exactly
the "decorated transition" mechanism `NINE_DIAGONAL_STATUS.md` section
"Surviving strategies" item 6 and `DIAG2_PIVOT_ALL_COMPACT_SECOND_WALL.md`
describe, and closing that global gluing/cycling question is untouched by
this checker.

## 4. The four true exceptions

`(50,7861)`, `(50,7977)`, `(50,12128)` are type `(50,50)`; `(50,20046)` is
type `(50,51)`. None is affine in any of its eight non-pivot coordinates
after `q_50` elimination, so neither lemma in section 2 applies directly to
them. This does not mean they are compact -- it means every certificate tried
so far (five families from `DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY.py`, plus
this one) fails to settle them. A genuine two-plane/pencil argument (moving
two coordinates jointly, as used for the fourth-diagonal cover-all supports
in `FOURTH_DIAGONAL_FIVEFOLD.md`) or a targeted ideal saturation in the style
of `verify_diag2_pivot_49_pair_saturation.py` are the natural next attempts;
neither is carried out here.

## 5. Exact verification

The checker independently reconstructs the 13 canonical residual polynomials
from scratch (cross-checked against a from-scratch sympy expansion, not
copied from any other file's pinned output), re-derives the pivot/coefficient
split for whichever type is used as each pair's anchor, re-derives the
6,890-candidate census from the same `pair_orbit_representatives` /
`factor_orbit_data` machinery `DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY.py`
itself uses, classifies every candidate by exact integer polynomial-degree
inspection (no floating point anywhere), and independently re-runs the
existing all-frame certificate audit scoped to just the four exceptions to
confirm they are not already resolved by another method. Two canaries confirm
the affine-variable detector itself distinguishes a genuinely degree-1
coordinate from a genuinely degree-`>=2` one before any of this is trusted.

```text
PASS: 13 RESIDUAL dict-polys independently match sympy expansions of the derived-wall formulas
PASS: affine-variable detector canaries (known-affine / known-non-affine) both correct
PASS: 6,890 candidate pairs across the five hard factor-type families: {...}
PASS: 6886/6890 candidate pairs are affine in some non-pivot variable
THEOREM: every one of those 6886 pair-wall common-zero loci is noncompact
STATUS exceptions (not affine in any variable): [(50, 7861), (50, 7977), (50, 12128), (50, 20046)]
PASS: all four exceptions independently reconfirmed unresolved by every prior certificate family
CAVEAT: pair-wall noncompactness (by any method) does not by itself promote diagonal two
CAVEAT: diagonal two still requires global decorated transition-cycle acyclicity
```

## 6. Relation to the six `(49,50)` cases

`DIAG2_PIVOT_49_50_PAIR_SATURATION.md` independently closes the six
`(49,50)`-type residue orbits by the stronger, more expensive route (four by
full ideal saturation to the unit ideal, giving smoothness; two by this same
affine-fiber argument alone, since their bounded saturation search did not
reach the unit ideal within the resource budget used). All six are also among
the 6,886 closed here, as a cross-check: this checker's classification of
those six factor IDs agrees with the dedicated script's.
