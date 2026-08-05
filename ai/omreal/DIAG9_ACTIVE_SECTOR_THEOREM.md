# Diagonal 9: the active-factor sector reduction

## Theorem

Fix one normalized realization cell `X` of a realizable `UOM(4,8)` parent.
Let the complete residual discriminant be grouped into its primitive global
factor classes `q_j`, so every labeled residual determinant is

\[
                         D_E=c_Eu_Eq_{j(E)},
\]

where `c_E` is a nonzero rational constant and `u_E` is a nowhere-zero
fixed-sign parent-bracket unit on `X`.

For an extension signature `sigma`, call a labeled occurrence `E` aligned
when `sigma` is aligned with the exact three- or four-circuit on `D_E=0`.
Call a global factor `j` **sigma-active** if any occurrence in class `j` is
aligned.  The derived-wall side theorem assigns a unique allowed sign
`epsilon_(sigma,j)` to every sigma-active factor for which `F_sigma` is
nonempty:

\[
              F_\sigma\subset\{\epsilon_{\sigma,j}q_j>0\}.
\]

This definition is independent of duplicate labels.  More explicitly, fix
one raw determinant `D_(E_j)` as the orientation of factor class `j`.  For
every other occurrence in that class,

\[
          D_E/D_{E_j}=(c_E/c_{E_j})(u_E/u_{E_j})
\]

has one fixed nonzero sign on `X`.  Translate the allowed side supplied by
the circuit identity through that unit sign.  If two aligned occurrences
produce opposite orientations of the representative, then `F_sigma` is
empty.  If `F_sigma` is nonempty, any feasible chart proves that all
translated orientations agree.  Thus factor multiplicities `2`, `15`, and
`65`, including the common type-46/type-47 localization factor, introduce no
ambiguity.

There is a second multiplicity issue: one labeled occurrence can inherit
several exact fixed-unit circuit identities from different transports of an
orbit template.  It has a sharp dichotomy.

> **Alternative-certificate empty-wall lemma.**  Normalize the circuit
> coefficient signs of every transported identity into sorted circuit order,
> modulo one common sign.  If two patterns disagree, then
> `D_E^{-1}(0) intersection X` is empty.

Indeed, at a zero of an ordinary occurrence the four wall normals have rank
three, so their relation kernel is one-dimensional.  At a localization zero
the distinguished three normals have rank two, with the same conclusion.
All fixed-unit identities would have to give proportional relations.  Two
different sign patterns modulo global sign cannot be proportional.  Since
the coefficient signs are parent-bracket invariants throughout `X`, the
disagreement excludes every zero in the cell.  Equation `D_E=c_Eu_Eq_j`
then excludes the whole primitive factor wall.  Such a factor has constant
sign on connected `X`; for any nonempty `F_sigma` its would-be allowed
literal is automatic and the factor may be omitted from `H_S`.

For a finite family `S`, if some individual `F_sigma` is empty then `F_S` is
already empty.  Assume henceforth that every member is nonempty, as required
for the proper regions in 9DVL.  Inconsistent allowed signs then make `F_S`
empty.  When they are consistent, define its active sector

\[
 H_S=X\cap\bigcap_{j\text{ active for some }\sigma\in S}
                       \{\epsilon_{S,j}q_j>0\}.
\]

> **Active-sector theorem.** `F_S` is a union of connected components of
> `H_S`.  Hence a path in `H_S` starting at a point of `F_S` remains in
> `F_S`.  In particular, if `H_S` is connected and contains one feasible
> point, then `F_S=H_S` is connected.

Equivalently, in the complete master-chamber graph one may contract every
edge whose factor is inactive for all members of `S`; this preserves the
path components of the induced common-support subgraph.

## Proof

The side theorem proves the displayed inclusion and consistency assertion.
It remains to prove that feasibility is constant on each component of
`H_S`.  It is enough to treat one `sigma in S`.

Suppose a path in `H_S` joins a sigma-feasible point to a sigma-infeasible
point.  Because `F_sigma` is open, there is a boundary point `Y` along the
path.  Choose a support-minimal positive Gordan relation among the signed
derived normals at `Y`.  Its support has size at most five.

Supports of size one or two are impossible on a uniform parent.  If the
support has size five, all five four-cofactors are nonzero by minimality, so
the positive circuit and its signs persist in a neighborhood of `Y`.  Thus
`Y` is an interior point of the bad locus, not a boundary point.  The same
argument applies to a structural three- or four-circuit: a nonzero circuit
minor and the structural dependence make its positive signs persistent.

The remaining support is a nonstructural three- or four-circuit.  The exact
residual classification and padding argument put it on a labeled residual
occurrence `D_E=0`, and its positive orientation says precisely that `E` is
aligned with `sigma`.  Consequently its global factor is sigma-active.  But
every active factor is strictly nonzero on `H_S`, contradicting `Y in H_S`.

There is therefore no feasibility boundary inside `H_S`.  Both
`F_sigma intersect H_S` and its complement are open in `H_S`; feasibility is
constant on every connected component.  Intersecting this statement over
`sigma in S` proves the theorem.

The argument takes place in the open parent cell `X`.  It makes no claim
that closures of active sectors in a compactification avoid infinity.  A
roadmap or homology calculation must still cover the projective boundary;
the theorem only says that inactive residual walls are not part of the
feasibility boundary in the interior.

For the graph formulation, a generic crossing of an inactive factor changes
none of the signatures in `S`.  A path in the complement of the active
discriminant can be perturbed to cross inactive factors only at generic wall
points, giving exactly the contraction of inactive-factor edges.  Conversely
each such edge is realized by a local path.  The all-strata gluing theorem
excludes a label change supported only at a multiple-wall stratum.

## Exact row-2599 audit

`verify_diag9_active_sector.py` independently transports the thirteen exact
wall-circuit templates under all `S_8` relabelings, obtaining all 84,840
labeled residual occurrences and all 2--24 transported identities on each.
It orients every circuit using exact integer derived-normal determinants at
chart 0, applies the alternative-certificate lemma, groups occurrences using
the pinned 26,740-factor census, and then tests the two committed hard
nine-families.

Run with:

```console
python ai/omreal/verify_diag9_active_sector.py
```

Exactly `27,944` occurrences have conflicting fixed-unit patterns: `20,112`
ordinary and `7,832` localization occurrences.  They certify `8,916`
primitive factors whose wall sections are empty in parent 2599.  This leaves
`17,824` **candidate** factors.  Absence of a conflict does not prove that a
remaining factor actually meets `X`; the candidate count is an upper bound.

After removing the certified-empty classes, the proof-safe family counts are:

| row-2599 family | active occurrences | candidate active factors | candidate inactive factors |
|---|---:|---:|---:|
| charts 12/37 family | 5,026 | 3,539 | 14,285 |
| charts 37/176 family | 5,554 | 3,638 | 14,186 |

Per-signature active-factor counts are respectively

```text
791,656,628,541,548,622,647,503,510
684,595,689,562,591,681,587,607,785.
```

The semantic digests include the sorted certified-empty factor list, the
per-signature factor literals, and the active occurrence indices:

```text
6de7ff2716b65853c04b9a08f44eb98ad8966e1f3525887ffafde0a3b805c154  12/37
5cede059d413bffdd18e98ca8a261ec9b2174e558ea4c4bc51a27decaf40a3ee  37/176
```

Thus a family-adaptive exact roadmap for either stress family can discard
about 86% of the raw global factor equations before projection closure or
cell construction.  The 8,916 certified-empty factors have no walls; no
extension-tope enumeration is needed on walls of the family-inactive
factors.

The same alternative-certificate calculation has now been evaluated from
chirotope formulas on all 2,604 realizable catalog parents.  Parent 860 is the
unique minimum of the resulting proof-safe candidate count: 10,320 factors
are certified empty and 16,420 remain candidates, versus 17,824 candidates at
parent 2599.  A direct determinant replay at the stored integer parent-860
matrix independently reproduces the count.  See
`DIAG9_PARENT_RANKING.md` and `verify_diag9_parent_ranking.py`.

The endpoint pairs differ in 5,198 and 3,320 complete factor coordinates.
All of those differing factors are inactive for the corresponding family,
as the theorem requires; the committed exact incidence paths cross only
label-safe walls.

## Limit

This reduction does not prove that `H_S` is connected.  A set cut out by
allowed sides of smooth noncompact graph hypersurfaces can be disconnected;
the existing polynomial countermodel in `ATLAS_HELLY.md` already has this
property even when every individual wall is a connected global graph.  The
remaining diagonal-nine target is therefore one of:

1. prove every nonempty admissible active sector `H_S` is connected;
2. build a family-adaptive exact roadmap for its roughly 3,500--3,700
   candidate active factors;
3. find two feasible components of one such sector and certify their
   separation.

For the literal ninth diagonal, the complete residual roadmap can therefore
be replaced, family by family, by the following exact task: for every proper
pairwise-incomparable nine-family with consistent literals, enumerate the
components of `H_S` and prove that at most one of them is feasible.  Proving
`H_S` connected is a stronger sufficient certificate.  A falsifier must put
exact feasible incidences in two different components and give a complete
semialgebraic separator for those components.

The theorem itself holds for every finite `S`, so inactive walls may also be
removed from a family-specific calculation for diagonals 2--8.  It does not
by itself vanish any higher homology group: a selected component of `H_S`
may carry cycles.  In the universal dual-master-cell program, which handles
all families at once, inactive walls for one family can still be active for
another; the reduction trades one universal cellulation for smaller
family-adaptive sectors.

## Assumptions and audit boundaries

The proof uses five already committed inputs which should remain explicit in
any repository version:

1. the exhaustive structural/fixed/residual four-set classification;
2. the ordinary and localization side identities for every labeled residual
   occurrence;
3. support-minimal Gordan relations have size at most five, with sizes one
   and two excluded by parent uniformity;
4. the all-strata padding/rank argument for a nonstructural three-circuit;
   and
5. the exact global localization census
   `D_E=c_E u_E q_j`, where `c_E` is a nonzero rational scalar and `u_E` is
   either `1` or one parent bracket.  This makes the orientation recovered at
   one exact chart constant throughout the parent cell.

The new verifier replays (1)--(2), retains all `S_8` transports, proves the
alternative-certificate dichotomy, audits duplicate-factor orientations,
and checks both family counts.  For (5) it consumes the pinned global-census
artifact and checks its complete assignment, polynomial, factor/unit, and
state schemas, together with nonvanishing of all recorded units at the
orientation chart.  Rebuilding all 84,840 polynomial factorizations remains
the responsibility of `DIAG9_GRAPH_global_factor_census.py --replay`.  The
committed exact path artifacts independently prove that both displayed
families are nonempty and their endpoints feasible.  The verifier does not
certify that any of the remaining 17,824 candidate walls meets `X`, active-
sector connectivity, roadmap coverage, or a diagonal.
