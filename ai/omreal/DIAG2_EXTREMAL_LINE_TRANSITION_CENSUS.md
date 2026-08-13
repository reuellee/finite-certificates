# Diagonal two: complete transition census on the critical parent-187 line

## Result

The birth-budget target from `DIAG2_EXTREMAL_UNDOMINATED_BIRTH.md` is now
resolved on the complete standard `e`-coordinate slice through catalog parent
`187`.

The open parent-cell interval contains exactly

```text
1,721 residual roots
1,722 open residual chambers.
```

Every real root of every one of the `26,740` primitive global residual
factors is isolated by exact Sturm arithmetic.  The three extremal
overlap-six atlas pairs are then tracked across every chamber.  Among the
resulting `5,166` pair-chamber observations,

```text
4,159 remain simultaneously bad;
1,007 lose at least one endpoint;
minimum simultaneously-bad overlap = 6;
minimum overlap with a non-singleton separator = 9.
```

No tracked overlap is zero.  More sharply, none of the six walls that changes
the overlap of a still-bad pair has enough loss budget to delete the incoming
common directions.  This is a complete one-dimensional theorem, not
parent-cell coverage and not a proof of diagonal two.  The honest 9DVL score
remains `1/9`.

## 1. Exact wall and chamber coverage

Normalize parent `187` to the standard nine-coordinate chart and vary only
coordinate `e`.  The two endpoints are the first parent-bracket zeros on the
negative and positive rays.  Restricting all primitive residual factors to
this interval gives the exact incidence census

| type | roots | topes exchanged per side |
|---:|---:|---:|
| 36 | 40 | 72 |
| 38 | 11 | 10 |
| 48 | 21 | 4 |
| 49 | 634 | 2 |
| 50 | 657 | 2 |
| 51 | 358 | 2 |

All root boxes are pairwise disjoint.  Thus there is no unimplemented
simultaneous primitive-factor crossing on this line.

The `1,649` type-`49/50/51` roots have one labeled four-row occurrence each.
Their two-tope exchanges are propagated by the exact signed-circuit rule and
checked to be reversible.  A primitive type-`36/38/48` factor controls a
compound incidence, so a tempting decomposition into independent four-facet
mutations is false.  The verifier instead independently enumerates the exact
complete `26,112`-tope table in the destination chamber of each of those `72`
crossings.  Finally, independent exact enumerations of both terminal chambers
agree with the propagated tables.  This supplies an end-to-end check on the
entire ordered chain.

## 2. Complete tracked transition list

Only ten of the `1,721` walls change any of the six tracked signatures:

```text
type 49: factors 22118, 23604
type 50: factors 11045, 13869, 16242, 19971, 23559, 23979
type 51: factors 8421, 10115.
```

Eight walls change a tracked pair observation.  Two are badness status
changes:

```text
type 50: simultaneously bad with overlap 12  <-> one endpoint is a tope
type 51: simultaneously bad with overlap  9  <-> one endpoint is a tope.
```

The other six keep both endpoints bad.  Orient each wall from the
higher-overlap side toward the lower-overlap side and let `L` be the total
number of directions lost by the two endpoint masks.  Their complete census
is

| type | incoming overlap | outgoing overlap | loss budget `L` | walls |
|---:|---:|---:|---:|---:|
| 49 | 15 | 9 | 6 | 2 |
| 50 | 12 | 6 | 6 | 1 |
| 50 | 9 | 6 | 5 | 2 |
| 50 | 9 | 6 | 6 | 1 |

In every row,

```text
loss budget < incoming overlap.
```

The birth-budget lemma therefore rules out a zero-overlap destination at
every still-bad pair transition on the slice.  The two badness births enter
with overlap `12` or `9`, so they are safe as well.

This contains the earlier isolated type-`49` factor `23604` edge, including
its `15 -> 9` transition, but no longer depends on selecting that edge in
advance.

## 3. Reproduction

Run the complete exact census with

```console
python ai/omreal/verify_diag2_extremal_line_transition_census.py --workers 4
```

The pinned semantic digest is

```text
0302dcf1e4ce10980c6133966d42048b45209a0739ae823d67bf7ec891c6845a
```

The digest covers every isolated root box, factor ID, chamber observation,
tracked transition, mutation count, and aggregate extremum.  The verifier
also checks the source-index updates, exact separator reconstruction, simple
wall involutions, all compound destination tope tables, and both terminal
tope tables.

## 4. Proof boundary and next target

The result closes the budget-tight-birth escape hatch only on one complete
coordinate slice of one extremal parent realization.  A compact bad component
could avoid this line or occur in another parent realization cell.

The next useful finite target is consequently two-dimensional rather than a
longer random sample: construct the exact residual-cell disk spanning the
`d/e` directions at parent `187`, retain its wall adjacency, and test the same
birth-budget inequality on every edge.  A passed disk would determine whether
the line theorem survives wall intersections and compound-node routing; a
failure would isolate the first genuinely budget-tight birth.
