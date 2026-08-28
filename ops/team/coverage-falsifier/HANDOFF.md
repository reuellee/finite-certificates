# Falsifier handoff: bounded source-skeleton missed-component census

```yaml
track_id: cycle-20260828-falsifier-missed-component
base_revision: ec362dba8a912bc4749c004641aee2da0a88dc05
outcome: inconclusive
summary: >-
  No strict-parent component disjoint from the 40 retained edges was proved.
  Exact replay found zero new factors on the accepted strict-parent half-cube
  and isolated 123 apparent full-cube misses whose opposite corner signs occur
  only at two parent-infeasible vertices; all 123 are exactly root-free on all
  40 retained segments.
artifacts:
  - path: ops/team/coverage-falsifier/diagnose_diag3_pair_missed_component_census.py
    digest: bc805b498efd40b9ae59d8570024ec8bdffcf5221b3d1400e6c7863bae5e2c30
replay:
  command: >-
    PYTHONDONTWRITEBYTECODE=1 python
    ops/team/coverage-falsifier/diagnose_diag3_pair_missed_component_census.py
  result: >-
    exit 0; 17,824 candidates, 10,844 known crossings, 4,450 exact
    half-cube occurrences, 0 half-cube factors outside the known set, 123
    oversized-cube corner candidates, and 0 roots in 123 x 40 exact retained
    closed-segment Sturm tests.
coverage:
  included: >-
    Exact row-2599 candidate and 105-edge reconstruction; the complete accepted
    chart-0/chart-152 strict-parent half-cube; the eight full source-cube
    vertices; and all 40 retained closed segments for the 123 full-cube corner
    candidates.
  excluded: >-
    Full-cube interiors outside the accepted half-cube, the rest of the
    nine-dimensional strict parent cell, connectivity between local witnesses,
    and all global component quantifiers.
canaries:
  positive: accepted strict half-cube reproduces 4,450 occurring factors
  negative: >-
    123 factors have opposite exact full-cube corner signs but are not promoted,
    because every opposite-sign corner is one of parent-unsafe masks 4 or 6
  null: the strict half-cube contributes exactly zero factors beyond the 10,844 known set
  hostile: >-
    any retained-edge endpoint root, identically zero restriction, nonzero
    Sturm count, unresolved half-cube factor, changed count, or changed ID
    digest raises AssertionError
source_accounting:
  used: >-
    Pinned source point/factor-state bank, candidate-factor list, residual
    polynomials, parent catalog, exact 105-edge bank, optimal 40-edge cover, and
    accepted exact half-cube routines at the base revision
  unused_or_missing: >-
    Global master quotient/open object and face atlas were consulted for scope
    only; they supply no missing component theorem and are not replay inputs
open_defects:
  - >-
    The exact census does not order residual roots against the first parent-wall
    event on the unsafe side of the full source cube.
  - >-
    The discovery sampler described below is heuristic and has no theorem effect.
next_action: >-
  For the 123-factor digest below, build an exact boundary-order census on the
  twelve full-cube edges and then adaptive rational boxes adjacent to masks 4
  and 6; compare each first residual root with the first parent-bracket zero.
ledger_change_recommended: none
```

The 123-factor canonical digest is
`16a8aa0c7aa1c49452dfc2b3f557453619027196aa0344f73200e45b114f3eca`.

## Exact result and nonconsequence

The 123 factors are the complete set that are absent from the 10,844-factor
endpoint-crossing bank but have opposite exact signs at vertices of the full
chart-0/chart-152 hybrid cube.  Exact Sturm replay proves that none has a root
on any retained edge, including even-multiplicity or two-root cases that an
endpoint-sign screen could miss.  This makes them the smallest current
boundary-adjacent discriminator, but not counterexamples: the six strict-parent
cube vertices have one common sign for each factor, and every opposite sign is
confined to parent-infeasible masks 4 and 6.

The accepted strict-parent half-cube was replayed independently over all 17,824
restrictions.  All 4,450 occurring factors already belong to the 10,844 known
set.  Therefore that declared source domain contains no missed factor, while
making no claim about distinct components of a known factor.

## Heuristic search (not finite exact evidence)

Two parent-sign-preserving coordinate hit-and-run discovery scans found no
candidate root:

- 24 non-crossed, two-monomial quadratics: 48 chains x 3,000 sweeps;
- all 160 non-crossed total-degree-two factors: 64 chains x 1,200 sweeps.

Coordinate bounds were proposed numerically.  Every prospective hit was gated
on exact rational parent inequalities and exact univariate root isolation, but
no proposal reached that gate.  The absence of proposals is sampling evidence
only and is not used in the exact result above.
