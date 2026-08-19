# Diagonal three: coverage-accounted pair-end atlas seed

## Outcome

The 178 pinned row-2599 minimum-overlap pairs now have a deterministic exact
transport schema.  It contains:

* 178 selected pair point germs;
* 1,471 common-root ray germs with exact parent terminals;
* 4,959 deterministically selected one-order-per-edge two-root sector germs
  with every bivariate parent-bracket polynomial (from 9,756 working ordered
  families before the deterministic choice);
* a 1,293-sector spanning-forest subcomplex with an exact signed integral
  `MN=0` replay and unit pivots;
* the fixed-parent-unit circuit rule for all 84,840 labeled residual
  occurrences; and
* the exact 97,224-signature receiver assignment cover.

This is a **local seed schema**, not a global pair atlas.  The 178 matrices
are exact point germs in 178 distinct sampled factor-sign chambers.  They do
not cover the chambers of the parent realization cell and have no certified
wall adjacency.  The schema records that deficit rather than converting a
point-bank result into a topological claim.

The verifier is `verify_diag3_pair_global_atlas_schema.py`.

## 1. Cell and boundary schema

Every eventual relative atlas record has the following layers.

| layer | exact key | required boundary data |
|---|---|---|
| pair germ `G` | parent chart, two bad signatures | residual sign chamber and incident transport cells |
| ray `R` | `G`, oriented elementary root | bottom `G`, zero-weight walls, triple-relative receiver walls, parent facet or projective infinity |
| sector `S` | `G`, ordered pair of root lines | two axis rays, parent residence cells, receiver-factor arcs, simultaneous-factor vertices, infinity faces |
| residual face `W` | primitive factor and labeled occurrence | fixed-unit circuit support/signs and its zero-weight specialization |
| simultaneous face `X` | set of primitive factors | all incident sectors with multiplicity parity |
| relative face `P/T` | parent facet/infinity or receiver becomes bad | explicit relative tag retained in every incidence column |

The fixed-unit record for a labeled occurrence stores

```text
(occurrence, primitive factor, orbit type,
 circuit support mask, positive sign pattern,
 ordered circuit, fixed-unit coefficient supports).
```

For a signature `rho`, the occurrence is positive exactly when the
restriction of `rho` to the support equals the stored pattern or its
complement.  Thus this table is an exact active-factor classifier for any
future receiver color; it is not a sample-point sign heuristic.

A completed sector record must refine the parameter quadrant into a finite
regular relative complex.  Every cell must list:

```text
parent-bracket sign cell
active receiver-factor sign cell
zero-weight occurrence set
simultaneous primitive-factor set
parent-infinity / parent-facet / triple-relative tags
mod-two incidences to every codimension-one face
```

Only after those fields are populated may duplicate root or occurrence
choices be contracted.

## 2. Exact transport seed

The selected pair at each chart is the pinned minimum elementary-escape
overlap witness from `DIAG2_ESCAPE_SET_atlas178_summary.json`.  Rebuilding
all 26,112 derived-arrangement topes per chart gives the following common
root counts.

| common roots | charts |
|---:|---:|
| 6 | 32 |
| 8 | 81 |
| 9 | 30 |
| 10 | 24 |
| 11 | 11 |

There are 5,477 independent candidate unordered root pairs and 4,959 exact
sector edges admitting at least one working order.  The stored sector uses
one deterministic working order per such edge; it is not the set of all
9,756 working ordered families.  The edge-count histogram is the one already
pinned by the ordered-root audit; the compatibility digest remains

```text
7a3beb589109c8343be17084514eadd778f5eb6ebb918f0d67dafc05120d78ef
```

The new replay additionally determines which order works:

| order truth | sectors |
|---|---:|
| forward only | 84 |
| reverse only | 78 |
| both | 4,797 |

The deterministic choice uses forward whenever possible, hence 4,881
forward choices and 78 reverse choices.

### Parent endpoints

An elementary column shear changes exactly 20 of the 70 parent brackets.
For all 1,471 root germs the first positive terminal is finite and lies on
exactly one parent-bracket facet:

```text
finite single-facet terminals: 1471
projective-infinity terminals:    0
simultaneous parent facets:        0
```

Infinity remains a required schema tag; its count happens to be zero for
these selected rays.

For each ordered sector the checker expands

```text
Y (1 + u N_d) (1 + v N_e)
```

exactly, including the noncommuting `uv` term, and hashes all 70 bracket
polynomials.  The number of brackets with a nonzero `uv` coefficient is:

| `uv` brackets | sectors |
|---:|---:|
| 0 | 1,302 |
| 6 | 3,112 |
| 10 | 258 |
| 20 | 287 |

The two coordinate-axis terminals are checked against the independently
computed root-ray terminals.  What remains missing is the exact CAD/roadmap
of each two-dimensional residence component and its receiver-factor
frontier.

The complete transport digest is

```text
b1c2678eab2ca750a5453611303a752d50eb9e6522112a2923997122c45c5105
```

## 3. Fixed-unit wall coverage

All 84,840 labeled residual occurrences are covered by relabeled ordinary
or localization fixed-unit certificates.  Evaluating their actual
determinant coefficients at charts 0 and 177 gives identical signs.  The
orbit census is:

| type | occurrences | type | occurrences |
|---:|---:|---:|---:|
| 36 | 10,080 | 37 | 5,040 |
| 38 | 1,680 | 39 | 2,520 |
| 41 | 10,080 | 42 | 2,520 |
| 44 | 10,080 | 46 | 6,720 |
| 47 | 10,080 | 48 | 840 |
| 49 | 10,080 | 50 | 10,080 |
| 51 | 5,040 |  |  |

These occurrences group into 26,740 primitive factors with multiplicities

```text
25200 x 1,  420 x 2,  280 x 15,  840 x 65.
```

For the 178 selected pair germs, the materialized active-factor counts have
the following exact ranges:

| census per germ | minimum | maximum |
|---|---:|---:|
| left active factors | 1,336 | 2,038 |
| right active factors | 1,248 | 2,125 |
| union | 1,625 | 3,539 |
| intersection | 438 | 1,360 |
| left positive occurrences | 4,260 | 7,809 |
| right positive occurrences | 4,129 | 8,225 |

The fixed-unit classifier and selected-pair active-set digests are

```text
db5a59d51ca0c5d894fc7688ee83440c004c4742c6b90197020004f1c8c28a17
9772baa6fdad287691c9e5000d58c29a87f3b102ce24cadcfaca90b326e54383
```

This is occurrence-complete active-color data.  It does not assert that a
given active primitive factor meets a particular sector; that is a CAD
question retained as a missing frontier block.

## 4. Receiver-color accounting

The exact upper-cover certificate assigns each of the 97,224 abstract
extension signatures to one of the 178 charts and supplies an integer point
realizing it there.  The schema rechecks all 56 signs of every assignment.
Combining an assigned feasible receiver with the selected bad pair at that
chart yields 97,224 canonical receiver-colored seed requests.

Across every chart, before choosing the canonical assignment, there are

```text
178 x 26,112 = 4,647,936
```

feasible receiver occurrences.  Weighting the root and sector counts by the
actual assignment multiplicities gives the exact unresolved workload:

```text
receiver-colored ray frontiers:       850,442
receiver-colored sector frontiers:  3,025,948
```

The assignment digest, including every signature, chart, selected pair, and
integer witness point, is

```text
9c65caecfd062c44e7a62a3081cc63af1892290fd98dcc423c6d78826034a2c7
```

This receiver cover does not cover all bad-pair choices: the selected pair
changes with the assigned chart.

## 5. Formal aggregate integral incidence regression

Assume, purely for this regression, that every omitted ray subdivision and
receiver endpoint is relative, every non-axis frontier of every selected
sector is relative, and each selected sector has exactly one nonrelative
residence cell.  The resulting formal selected graph has aggregate groups

```text
C0 = Z^178
C1 = Z^1471
C2_formal = Z^4959.
```

In cochain notation let `N:C0 -> C1` send a chart germ to all of its root
rays, and orient every sector row of `M:C1 -> C2` as `-left+right`.  Each
sector has both rays in the same chart, so `MN=0` over the integers, not
merely modulo two.  Exact bit elimination gives

```text
rank N = 178
rank M = 1293
1471 - 178 - 1293 = 0.
```

A lexicographic spanning tree in each of the 178 connected root graphs has
exactly

```text
1471 - 178 = 1293
```

edges.  Deleting non-anchor leaves replays 1,293 signed `+/-1` pivots, while
one ray in each chart gives 178 unit pivots for `N`.  Thus the same local
middle complex is split exact over `Z`; its integral and mod-two rank pairs
are both `(178,1293)`.  The remaining `4,959-1,293=3,666` sectors are
non-tree choices in this formal local graph.  For the 97,224 canonical
receiver assignments, the
formal spanning-forest workload is

```text
receiver-colored tree sectors:      753,218
receiver-colored non-tree sectors: 2,272,730
```

The first number is the exact identity `850,442 - 97,224`.  It is the
smallest selected-germ **choice** complex after a tree has been proved valid
on every refined cell.  It is not permission to discard the other sectors
before the receiver frontier is known: a receiver wall can cut a chosen
tree sector while another sector continues.  All 4,959 parent-sector CADs
remain discovery/coverage obligations until a coverage-safe dynamic forest
or an equivalent structural theorem has been certified.

This is a useful formal local incidence regression: connected ordered-root
graphs kill the selected-graph choice cycles under all three assumptions.
It is not yet the cellular chain group of the ambient atlas.  Missing ray
frontiers, receiver-factor subdivisions, sector CAD cells, chart-wall
transports, and simultaneous-factor cells can add nonrelative faces or
subdivide the aggregate columns and change the global matrices.

## 6. Exact coverage ledger

The point bank supplies no certified residual-wall adjacency.  Its 178
factor states have pairwise Hamming distances between 1,125 and 5,600, so no
two stored germs are adjacent across one primitive wall.  The following
blocks remain open.

| missing block | exact accounted count |
|---|---:|
| stored-chart adjacencies certified | 0 |
| unordered stored-chart pairs | 15,753 |
| known two-sided primitive factors without an adjacency cell | 10,844 |
| unordered candidate pairs of those factors | 58,790,746 |
| ordered-sector parent CADs | 4,959 |
| receiver-colored ray frontiers | 850,442 |
| receiver-colored sector frontiers | 3,025,948 |
| unselected bad-signature pairs at the stored charts | 450,059,243,270 |
| assembled global relative `N,M` block | 1 |

The 58,790,746 figure counts candidate simultaneous-factor slots, not
proved nonempty intersections.  An exact roadmap must decide which slots
exist and attach every surviving face with the correct parity unless it uses
the existing acyclic-carrier diamond theorem.  That theorem removes a
separate codimension-two orbit census once the codimension-one receiver/end
maps are genuinely defined face by face: their two composites then lie in a
common nonempty union-support carrier.  Thus 58,790,746 is a diagnostic upper
bound, not the size of the smallest final matrix.

The verifier also makes the proof gate explicit.  All six global flags are
currently false:

```text
bad-pair family cover
parent-chamber cover
frontier-closure cover
relative-face tag cover
integral signed global lift
global mod-two middle rank
```

The integral local `MN=0` calculation does not satisfy the fifth flag: it is
the signed lift of 178 disconnected choice fibers, not the signed lift of
the balanced exclusive-pair end complex.

The full schema digest is

```text
f7abd2825d6cf28270350bd587fafd988e3154c48110189629eb9e2590328e11
```

Accordingly the checkpoint classification is:

```text
(b) exact local atlas/schema with a complete missing-block ledger;
    not (a) a finite globally coverage-certified end complex;
    not (c) an obstruction to the existence of such a complex.
```

## 7. Smallest coverage-complete certificate

The final certificate need not retain every root, occurrence, or non-tree
sector.  After a coverage-safe contraction, its irreducible data are:

1. a finite source universe for the actual three-signature family, with an
   exact digest and a total map to atlas cells (a proved finite orbit quotient
   may replace literal enumeration);
2. one closure-complete relative cell complex for `T,E01,E02,E12`, retaining
   every zero-weight, simultaneous-factor, triple-relative, parent-facet,
   and projective-infinity face;
3. signed integral coboundaries `dT,dij` and frontier blocks `bij` satisfying
   `dij bij + bij dT=0`; and
4. the assembled balanced cochain `C0 --N--> C1 --M--> C2`, with exact
   integer `MN=0` and

   ```text
   rank_F2(N) + rank_F2(M) = dim_F2(C1).
   ```

The last equality is the smallest algebraic endpoint needed for the rational
9DVL theorem.  Unit Smith invariants would strengthen it to every
coefficient ring but are optional.  There is no honest numerical size for
this reduced global complex yet: the 178 point germs do not determine how
many chamber, split--merge, or simultaneous-factor cells survive the
frontier refinement.

The `450,059,243,270` unselected pair count is therefore a coverage warning,
not a demand for that many matrix columns.  A universal arbitrary-signing
theorem may quotient it, but the quotient map must be proved on all closures
before the final ranks are meaningful.

## 8. Next positive block

The smallest honest extension is not another point sample.  It is one exact
residual-wall adjacency block:

1. choose a certified path between two residual sign chambers;
2. isolate every primitive wall crossing and simultaneous crossing on it;
3. transport the fixed-unit circuit records through all zero-weight faces;
4. compute every receiver-colored two-parameter frontier incident to that
   wall; and
5. append its mod-two columns, checking `MN=0` before contracting choices.

Repeating this until the chamber graph is coverage-certified would turn the
schema into the required global relative complex.  Until then no pair
`H_c^1` or diagonal-three claim follows.

## Replay

Full exact replay:

```console
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/verify_diag3_pair_global_atlas_schema.py --workers 4
```

A one-chart transport smoke test is:

```console
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/verify_diag3_pair_global_atlas_schema.py \
  --limit 1 --workers 1 --transport-only
```
