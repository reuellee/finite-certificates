# Universal D9 cut reduction: conditional theorem and first coverage gap

## Result

The requested universal reduction does **not** pass the opening gate.  There
is a short deductive reduction from two feasible active-sector components to
a finite minimal edge cut **once** a complete compactified master
stratification is supplied.  The repository does not supply the required
global coverage theorem or certificate, and the 13 residual wall types are
not closed under the first boundary/projection operation needed to build one.

The endpoint is therefore the useful null result
`UNIVERSAL_CUT_SCHEMA_COVERAGE_GAP`, not a proof, disproof, or finite census of
the D9 target.  No theorem-ledger change is recommended.

## 1. Exact quantifiers

Let `M` range over every realizable `UOM(4,8)` parent and let `X_M` be a
connected normalized realization cell.  Let `S` range over every proper,
pairwise-incomparable nine-family whose individual feasibility loci are
nonempty and whose active literals are consistent.  Write

\[
 H_S=X_M\cap\bigcap_{j\in A(S)}\{\epsilon_{S,j}q_j>0\}.
\]

The target quantifies over every ordered pair of distinct components `U,V`
of `H_S` which both meet `F_S`, every labeled/duplicate residual occurrence,
every chart overlap, every multiwall, every recursive parent-boundary
stratum, and every genuine-infinity stratum.  Properness and pairwise
incomparability are D9 input conditions; the graph reduction itself only
uses nonempty feasibility and consistent literals.

## 2. The conditional reduction that is valid

Assume a finite source-reconstructible regular stratification `K_M` of a
compactification of `X_M` with these properties:

1. it is compatible with all parent brackets, all primitive residual factor
   zero sets, chart seams, recursive parent boundary, and true infinity;
2. every connected interior chamber and every connected generic
   codimension-one wall patch occurs exactly once;
3. every signed chamber/wall incidence and chart identification is exact;
4. parent-boundary, recursive-facet, chart-only, and true-infinity cells are
   tagged and deleted from interior adjacency.

Form the finite master multigraph of full-dimensional interior chambers and
generic wall patches.  The committed active-sector theorem makes feasibility
constant on each component of `H_S`.  A path in the open parent cell has
compact image and may be perturbed away from codimension-at-least-two strata;
therefore multiwalls do not create an unrecorded path.  Duplicate labeled
occurrences are first grouped by primitive factor with their fixed-unit
orientation retained.

Choose generic feasible chamber vertices `u in U` and `v in V`.  Deleting all
master edges that cross an active factor disconnects `u` and `v`; otherwise
the graph path would realize a path in `H_S`.  Because the graph is finite,
there is an inclusion-minimal separating subset `Delta`.  Record for every
edge of `Delta` its connected wall patch, primitive factor, all labeled
occurrences and fixed-unit orientations, residual orbit type, aligned Gordan
circuit, signed sides, incident chambers, charts, and closure/boundary tags.
Minimality is checked by a `u-v` path after restoring each edge individually.
This is a finite human-checkable separator witness.

This proves `compactified stratification => finite minimal separator`.  It
does **not** prove or construct the antecedent.

## 3. Why local wall data do not supply global cut coverage

The 13 types classify one residual determinant wall germ and prove that each
wall is smooth and cooriented in the open uniform parent.  Support-minimal
Gordan circuits label feasibility loss at such a germ.  Convex Gordan
carriers give higher homotopies only after a facewise codimension-one system
already exists.  None of these statements enumerates connected components of
factor sign conditions, connected multiwall strata, chamber adjacency,
recursive boundary attachments, or unbounded ends.

The exact first failure occurs already for residual type 36:

\[
 q_{36}=af-cd+c-f,
 \qquad a=[1346].
\]

Eliminating the pivot `a` at the parent facet `a=0` produces, up to sign,

\[
 p=cd-c+f.
\]

The independent checker reconstructs all 70 normalized parent brackets and
loads the pinned 26,740-factor source census.  It verifies that `p` is in
neither catalog.  The already committed full first-layer audit finds 142 such
new irreducibles (degrees `2:23, 3:71, 4:43, 5:5`).  Thus a grammar closed
only under the existing parent brackets and residual factors cannot decide
even this wall-to-parent-facet attachment.  A complete CAD/roadmap may add
projection factors recursively, but no termination frontier, complete
factor list, cell count, or coverage certificate is present, and no bound
under the opening ceiling is proved.

This is the first uncovered recursive-facet mode.  It is a coverage gap, not
an exact D9 counterexample: adding the missing projection closure could
repair it.

## 4. Multiwalls, charts, recursive facets, and infinity

- **Multiwalls.** A generic interior path may avoid codimension two and
  higher, so the cut itself uses codimension-one wall patches.  Nevertheless
  a complete regular refinement and all incident chamber germs are required
  to prove that no patch or adjacency was omitted.  An unordered list of
  local wall types is insufficient.
- **Charts.** Every occurrence must carry its raw-to-primitive orientation,
  and chart overlaps must be identified exactly.  A chart seam is never a
  residual wall.  No complete all-parent chart/overlap cellulation is stored.
- **Recursive facets.** They are outside the strict open parent and cannot be
  promoted to interior separators.  Their attachments still have to be
  classified to prove closure coverage.  The type-36 polynomial above is the
  smallest pinned algebraic gap.  The `S12,37` factor-8552 wall on recursive
  facet `1237` is an exact hostile canary of the same policy.
- **Infinity.** A path between two points of `X_M` has compact image, so it
  never passes through infinity.  Sharing an infinity closure cell therefore
  creates no graph edge.  A source-complete compactification must still tag
  every true-infinity cell and must not relabel an artificial work boundary;
  that global certificate is absent.

## 5. The abstract model is out of domain, but its cut mechanism survives

The exact model

\[
 q_1=y,\quad q_2=(x^2-1)(x^2-4)-y,\quad q_{2+j}=z_j
\]

has nine smooth cooriented graph walls with constant nonzero pivots, proper
pairwise-incomparable regions, and four ordinary transverse `q1=q2=0`
multiwalls.  Yet the common positive sector has three components, over

\[
 x<-2,\qquad -1<x<1,\qquad x>2.
\]

The model is formally rejected as an actual D9 counterexample by the explicit
`D9_SOURCE_REALIZABILITY` hypothesis: its walls are not proved to be the
Plucker-derived 13-type residual arrangement of a `UOM(4,8)` parent.  This
passes the narrow domain check.  It does not provide the load-bearing bridge,
because none of the *proved local* consequences of D9 source realizability
excludes the model's cut mechanism.  To exclude that mechanism one must prove
a D9-specific global consequence absent from the model, for example:

- connectedness of every complete residual-factor sign condition;
- residual sign-geodesy / a partial-cube or COM theorem with support
  convexity; or
- a complete compactified D9 roadmap whose exact cut census is checked.

No such theorem is committed.  Consequently the load-bearing countermodel
mechanism gate, and therefore the opening coverage gate, still fail closed.

## 6. Exact replay and canaries

Run the track-local replay:

```bash
PYTHONDONTWRITEBYTECODE=1 python \
  ops/team/d9-universal-cut-prover/verify_cut_reduction_gap.py
```

It checks every source digest, the conditional-schema guard fields, the
three-component polynomial model and all 72 ordered incomparability
witnesses, the type-36 boundary polynomial against 70 brackets and 26,740
global residual factors, and hostile mutations for false proof promotion,
missing coverage, false boundary gluing, omitted recursive facets, and a
changed component count.

The two required predecessor canaries replay independently:

```bash
PYTHONDONTWRITEBYTECODE=1 python \
  ops/team/diag9-s1237-normal-link-prover/verify_normal_link_no_go.py
PYTHONDONTWRITEBYTECODE=1 python \
  ops/team/diag9-s1237-normal-link-falsifier/verify_normal_link_falsifier.py
```

They remain hostile local/boundary canaries only.  Neither is an interior
global separator.

## 7. Smallest next discriminating action

Generate the complete projection-closure frontier for one residual type
against all parent facets, recursively through chart and infinity closures,
and require a termination/coverage certificate.  The first test is whether
the type-36 facet factor `cd-c+f` and every descendant can be assigned to a
finite regular-stratum incidence grammar below the 10,000-type ceiling.  A
failure gives a sharper non-finite/global-memory obstruction; success defines
the missing generator needed before any all-parent cut claim.
