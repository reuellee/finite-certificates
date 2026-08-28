# Row-2599 component-coverage certificate v1

## The decisive distinction

The retained 40-edge source skeleton is an exact cover of **factor classes
known to cross the 105-edge source bank**. It is not a cover of wall
components or of the nine-dimensional strict parent cell. The v1 certificate
therefore never accepts “one crossing per factor” as component coverage.

The exact factor partition at revision
`ec362dba8a912bc4749c004641aee2da0a88dc05` is:

| disposition | factors | current meaning |
|---|---:|---|
| exact strict-interior nonempty | 10,844 | at least one component has a source-bank crossing |
| exact strict-interior empty | 1,177 | no wall in the strict parent cell |
| unresolved feasibility | 5,803 | an undiscovered wall would be missed by all 40 retained edges |
| total | 17,824 | pinned candidate universe |

This makes feasibility of the 5,803 residue the first fail-fast gate. Even
after that gate, every nonempty factor still needs a component-surjectivity
certificate.

## Global acceptance obligations

A `GLOBAL_COMPLETE` v1 object is accepted only if all of the following hold.

1. **Pinned universe.** The parent, support, 17,824 factor IDs, 40 source
   edges, compactification, polynomial inputs, and every auxiliary shard have
   authenticated digests.
2. **Exact disposition.** Every factor is either `EMPTY_STRICT_PARENT` with
   an exact fixed-sign/no-real-zero proof, or
   `NONEMPTY_COMPONENT_QUOTIENT`. No `UNRESOLVED` record is allowed.
3. **Roadmap completeness.** Each nonempty factor has an exact
   projection-critical roadmap, or an equivalent collar atlas plus exact
   complement exclusion, proving that its listed pieces meet every connected
   component. Samples and seeded flood fill alone are insufficient.
4. **Component quotient.** Continuation and chart-seam incidences induce the
   declared component partition, with no unpaired internal frontier.
5. **Source-hit surjectivity.** Every component has at least one exact
   intersection cell on a retained source edge. One hit per factor is not
   enough.
6. **Frontier balance.** Every frontier germ is paired internally, paired
   across a chart seam, or authenticated as a genuine relative escape.
7. **No missed components.** The parent-domain complement of certified wall
   collars is covered by exact factor-nonzero regions, or an equivalent
   roadmap completeness theorem is supplied.

The verifier derives the component quotient and checks these gates. It does
not consume a producer-supplied boolean such as `all_components_hit`.

## Boundary tags

| tag | global meaning | acceptance data |
|---|---|---|
| `INTERNAL_CONTINUATION` | same wall germ continues | unique reverse tag and matching exact germ |
| `CHART_SEAM` | coordinate seam, not relative | inverse chart transition, cocycle, matched germ |
| `GENUINE_RELATIVE_PARENT_FACE` | finite parent-boundary escape | vanishing parent brackets plus all remaining target signs |
| `GENUINE_RELATIVE_PARENT_INFINITY` | compactified relative escape | compactification face, chart cocycle, canonical relative-face ID |
| `ARTIFICIAL_SCOPE_FRONTIER` | local computation stopped | always a dependency gap in a global object |
| `UNCLASSIFIED_FRONTIER` | semantic status unknown | always a dependency gap |

In particular, the `w_minus` and `w_plus` endpoints of the existing
factor-19069 collar are artificial scope boundaries. Relabeling either as
relative is a hostile mutation.

## Compact certificate architecture

The recommended generator is a **frontier-balanced collar roadmap**, not a
global sign CAD:

1. classify the 5,803 feasibility residue first;
2. seed exact wall collars at source-skeleton intersections;
3. propagate collars in compactification charts using Bernstein signs and a
   certified nonzero transverse derivative;
4. isolate singular/projection-critical slices exactly and attach small
   roadmap patches;
5. pair continuation and chart-seam frontiers;
6. cover the complement by factor-nonzero Bernstein regions;
7. emit only the component quotient, source-hit map, frontier tags, and digest
   references to the bulky sharded proofs.

This is output-sensitive and factor-shardable. It still fails closed: seeded
collars without complement exclusion cannot rule out disconnected unseeded
components.

## Resource estimate and stop rule

The candidate degree census is `10, 599, 4198, 8258, 4286, 473` for degrees
one through six. A generic dense projection-critical bound
`sum n_d d(d-1)^8` is **2,732,978,444** complex critical solutions before
parent-boundary strata. This pessimistic bound rules out an unstructured
global solve under the 45-minute/12-GiB cycle ceiling; it is not a lower bound
for sparse or family-batched methods.

Observed clean replays in this worktree were approximately 7–11 seconds and
0.23 GiB for the 105-edge cover, 10 seconds and 0.35 GiB for the local collar,
and 23–25 seconds and 1.49 GiB for the two-edge labelled skeleton. A monolithic
40-edge/profile replay is therefore the wrong memory shape. Use immutable
factor-family shards and a streaming verifier.

The next 45-minute pilot should stop after one of these exact outcomes:

- a new empty/nonempty disposition for a pinned subset of the 5,803 residue;
- a complete factorwise quotient on a low-degree family, including complement
  exclusion and all frontier tags;
- or a pinned surviving set with the first failed acceptance obligation.

No pilot changes the 9DVL ledger.

## Replay

```bash
PYTHONDONTWRITEBYTECODE=1 python ops/team/coverage-certificate/build_coverage_dependency_gap.py > /tmp/coverage-gap.json
cmp /tmp/coverage-gap.json ops/team/coverage-certificate/ROW2599_COVERAGE_DEPENDENCY_GAP.json
PYTHONDONTWRITEBYTECODE=1 python ops/team/coverage-certificate/verify_coverage_dependency_gap.py
```

The generator extracts source facts. The verifier does not import the
generator and independently enforces acceptance and canary logic.
