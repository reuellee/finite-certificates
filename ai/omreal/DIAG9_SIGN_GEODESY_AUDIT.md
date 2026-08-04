# Diagonal 9: residual sign-geodesy audit

## Verdict

Residual sign-geodesy is a clean sufficient global theorem for diagonal 9,
but it is not proved by the present data.  Three exact diagnostics now delimit
the strategy.

1. The certified row-2599 line, disk, and transverse node have isometric
   factor-sign chamber graphs: respectively `P26`, `K2`, and `Q2`.
2. On all 178 stored exact row-2599 charts, every exact extension-signature
   support trace is an intersection of residual-factor halfspaces on those
   178 points.  This covers all 97,224 signatures and 39,366 distinct support
   traces.
3. The obvious recursive pivot proof is not algebraically closed.  Eliminating
   the thirteen canonical residual pivots against the parent brackets already
   creates 142 irreducible projection factors absent from both the parent
   brackets and the 26,740-factor residual census.

The second statement is a point-set statement, not a graph-convexity
statement.  The 178 charts have neither chamber coverage nor certified
adjacency.  Thus this audit proves neither residual sign-geodesy, a global
partial cube, nor the ninth diagonal.

Replay all three statements with

```console
python ai/omreal/verify_diag9_sign_geodesy_audit.py --workers 7
```

The resultant phase needs SymPy, just as `verify_derived_walls.py` does.
On the nine-core audit workspace, the exact run above took `193.1` seconds:
`0.1` seconds for the local metric audit, `168.1` seconds for the 178 exact
tope/closure audit, and `25.0` seconds for the resultant census.

## 1. The analytic theorem that would suffice

Fix one normalized parent realization cell `X`, and group the 84,840 labeled
residual determinants into the active primitive factors

\[
                         q_1,\ldots,q_m.
\]

Let `G` be the master-chamber graph of the complement of their zero sets.
Each generic edge is labeled by the unique factor that vanishes on its wall
patch.

> **Residual sign-geodesy criterion.** Suppose any two generic points of `X`
> can be joined by a path which avoids multiple-wall strata, is transverse to
> every wall it meets, and meets each geometric factor `q_j=0` at most once.
> Then the factor-sign map embeds `G` isometrically in a hypercube.  Every
> extension signature has convex chamber support, so every nonempty common
> feasibility locus is connected.

Indeed, endpoint signs agree in coordinate `j` exactly when a transverse path
must cross `q_j=0` an even number of times.  Under the at-most-once hypothesis
it crosses no such wall.  If the signs differ, it crosses exactly once.  The
resulting chamber walk therefore has length equal to endpoint Hamming
distance.  Every graph walk has at least that length because a generic edge
flips only one factor.  Thus `G` is an isometric hypercube subgraph, hence a
partial cube, and the two signs of every active factor are convex semicubes.

Now let `A_sigma` be the chambers supporting one extension signature.  If a
generic edge leaves `A_sigma`, the generic gluing theorem and the derived-wall
side theorem put all of `A_sigma` in the entry semicube of that edge's factor.
A hypercube geodesic between two vertices of `A_sigma` cannot leave: it would
have to cross that coordinate once to leave and again to reach its endpoint
in the entry semicube.  Hence `A_sigma` is convex.  Intersections of the
`A_sigma` are convex and connected, and the master-chamber theorem transfers
this to the corresponding `F_S`.

This criterion is stronger than needed for one nine-family—it would prove
connectivity for every finite family—but it isolates the missing geometric
claim without invoking a rank bound or a full COM completion.

## 2. Exact local metric tests

The audit consumes the already proved local roadmap artifacts and independently
checks their factor labels and graph metrics against the global factor census.

| Certified subset of parent 2599 | Graph | Active global factors | Exact metric result |
|---|---:|---:|---|
| Coordinate line | `P26` | 25 | 25 ordered roots flip 25 distinct IDs, so distance is Hamming distance |
| Generic wall disk | `K2` | 1 | its 65 labeled occurrences all have factor ID `16392` |
| Transverse node disk | `Q2` | 2 | the two 65-occurrence branches have distinct IDs `1657`, `12874` |

The line's multiplicity-65 root is one factor, not 65 coordinates.  The node
has sign order

\[
       (+,+),\quad (+,-),\quad (-,-),\quad (-,+),
\]

and opposite square edges carry the same factor ID.  The verifier includes a
negative canary: a two-edge path that flips one factor twice has equal
endpoint signs but graph distance two and is rejected.

These are genuine adjacency tests because each underlying subset has an exact
coverage and adjacency certificate.  They are local positive tests only.
Shortcuts outside a certified disk are irrelevant to the displayed induced
model, while the model itself cannot certify the full parent graph.

## 3. Exact factor-halfspace closure on the 178 charts

For a signature `sigma`, let

\[
 A_\sigma^{178}=\{c\in\{0,\ldots,177\}:\sigma
                    \text{ is a tope at chart }c\}.
\]

For a residual factor `q_j`, its two sampled halfspaces are

\[
 H_j^\pm=\{c:\operatorname{sign}q_j(c)=\pm\}.
\]

The exact audit proves

\[
 A_\sigma^{178}
 =\bigcap\{H_j^\pm:A_\sigma^{178}\subseteq H_j^\pm\}
                                                        \tag{1}
\]

for every one of the 97,224 signatures.  Equivalently, every outside sampled
chart is separated from the support trace by a factor-sign literal that
contains the whole trace.

The computation does not reuse the floating-point discovery tope matrix.
For each of the 178 integer parent matrices it runs the exact recursive tope
enumerator.  Every reported tope has an integer witness, restriction recursion
proves coverage, and every chart has exactly 26,112 topes.  Their union has
97,224 signatures and 39,366 distinct support traces.  The sorted
signature/178-bit-support table has semantic SHA-256

```text
95c2e2f520e0c3e2535846513e85b1b6b8388efba18ff53380d212bbf9decbb5
```

The factor signs come from the hash-pinned exact factor-state certificate.
Its 26,740 coordinates have 10,789 distinct traces and, after adjoining both
orientations and removing duplicates, 21,526 sampled halfspaces.  A bitset
closure computation checks (1).  A three-point negative canary with one
factor rejects a subset not expressible as an intersection of its two sides.

This result is evidence for the proposed convex-support mechanism, but it has
a strict logical boundary.  The 178 charts are scattered points.  They do not
meet every chamber, do not say which points are adjacent, and cannot detect
two different chambers with the same complete factor-sign word.  In fact any
finite set of observed hypercube vertices can be enlarged inside the full
hypercube, so Hamming triples from this sample alone cannot refute or prove a
partial-cube master graph.

## 4. Exact pivot-resultant closure no-go

For every residual orbit representative, the derived-wall theorem supplies
an adapted coordinate `x` with

\[
                      \partial_x q=\pm\prod_B[B]\ne0
\]

throughout a fixed parent cell.  Holding the other eight coordinates fixed,
the parent cell is an interval in `x` and `q=0` has at most one point.  This
suggests projecting the wall graph over the other eight coordinates.

The first projection boundary already requires new equations.  The wall root
meets an endpoint defined by a pivot-dependent parent bracket `b=0` only when

\[
                         \operatorname{Res}_x(q,b)=0.   \tag{2}
\]

The audit factors (2) over `QQ` for all thirteen canonical residuals and all
pivot-dependent parent brackets, primitive-normalizes every irreducible
factor, and compares it with every normalized parent bracket and every one of
the 26,740 global residual fingerprints.

| Residual type | New | Parent bracket | Existing global residual |
|---:|---:|---:|---:|
| 36 | 9 | 10 | 7 |
| 37 | 9 | 10 | 7 |
| 38 | 15 | 5 | 4 |
| 39 | 9 | 13 | 7 |
| 41 | 9 | 12 | 7 |
| 42 | 15 | 6 | 4 |
| 44 | 9 | 13 | 7 |
| 46 | 9 | 10 | 7 |
| 47 | 9 | 10 | 7 |
| 48 | 13 | 10 | 4 |
| 49 | 14 | 6 | 4 |
| 50 | 16 | 6 | 3 |
| 51 | 15 | 11 | 4 |

There are 151 new-factor occurrences in the rows of this table; after exact
deduplication, 142 distinct new irreducibles remain.  Their total-degree
census is

| Degree | Distinct new factors |
|---:|---:|
| 2 | 23 |
| 3 | 71 |
| 4 | 43 |
| 5 | 5 |

For the smallest explicit example,

\[
 q_{36}=af-cd+c-f,\qquad [1346]=a,
\]

and

\[
 \operatorname{Res}_a(q_{36},a)=cd-c+f
\]

up to sign.  The quadratic `cd-c+f` is neither a parent bracket nor any of the
26,740 residual factors.

This is a no-go only for a projection recursion restricted to the existing
equation catalog.  A complete CAD or roadmap algorithm will add resultants,
discriminants, and their later projection descendants; exact semialgebraic
algorithms remain finite.  The census says that this closure layer cannot be
skipped or silently identified with the residual walls.

## 5. First missing global axiom

Smoothness is not the first open issue.  Before face symmetry, strong
elimination, or gatedness can be used, one must prove that the complete
factor-sign word determines one chamber.  Equivalently, every realizable
full sign condition

\[
 X\cap\{\epsilon_jq_j>0\text{ for all }j\}
\]

must be connected.  Even the weaker one-factor questions—connectedness of a
wall and of its two sign sides—are not supplied by the pivot derivative.
In adapted coordinates `q=0` is a graph over the set of base points for which
its unique root lies in the parent interval.  Connectivity of that base set
is exactly what the new resultants begin to control.

A sufficient pseudosphere/COM condition can be stated recursively: every
nonempty common zero stratum should be a connected properly embedded
submanifold, and restriction of every remaining factor should either miss it
or cut it into exactly two connected sides, with the same property on all
faces.  Together with regular-ball closure/incidence, this is a recursive
pseudohyperplane arrangement and supplies the COM covector axioms.  The exact
node verifies the first transverse two-wall diamond only.  No certificate in
the repository establishes the first global connected-sign-cell condition.

## 6. Finite fallback and smallest decisive data

One universal exact sign-invariant CAD in the standard nine-variable chart
could, in principle, replace 2,604 unrelated geometric runs.  It must be
sign-invariant for all parent brackets, all 26,740 residual factors, and the
full projection closure exposed above.  Filtering its cells by the 70 parent
signs would recover each parent graph.  Exact tope labels followed by the
existing sharp tree or cut-SAT verifier would then settle the finite problem.

This is a valid global certificate schema, not a realistic size estimate.
The 142-factor first-layer growth and the 10,844 factors already known to vary
inside parent 2599 make a monolithic CAD likely much larger than parent-wise
roadmaps.  The practical pilot remains one complete small-parent roadmap,
followed by exact symmetry transport only where available.

The smallest decisive *countercertificate* to sign-geodesy would be a covered
parent subproblem proving either

* two master chambers with the same complete factor-sign word, or
* two chambers whose certified graph distance exceeds their factor Hamming
  distance.

The smallest decisive *proof certificate* for one parent is its complete
master roadmap with exact factor signs, adjacencies, and tope labels.  The
178-point sample, the local disks, and a bounded collection of coordinate
paths do not provide that coverage.

## 7. Trust boundaries

The verifier recomputes all 178 tope sets and the resultant census.  It
hash-pins, but does not rebuild, four prior certificate layers:

* `seeat_parent2599_upper178.npz`, the 178-chart row-2599 source bank;
* the six local roadmap/graph NPZ files, whose source verifiers certify their
  geometric coverage and labels;
* `DIAG9_GRAPH_row2599_factor_states.npz`, replayed independently by
  `DIAG9_GRAPH_row2599_factor_states.py`;
* `DIAG9_GRAPH_global_factor_census.npz`, replayed independently by
  `DIAG9_GRAPH_global_factor_census.py`.

The new metric and closure conclusions are exact conditional uses of those
already pinned artifacts.  The checker prints separate phase runtimes and an
explicit scope warning on every successful run.
