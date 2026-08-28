# Triangle-pilot independent referee handoff — 2026-08-28

```yaml
track_id: cycle-2026-08-28-triangle-referee
base_revision: ec362dba8a912bc4749c004641aee2da0a88dc05
candidate_revision: e3989d3f7099b245e31a3223acb02d948a9848af
outcome: finite-exact
summary: >-
  Independent raw-source replay accepts the exact bounded triangle
  classification: all 70 parent brackets are strictly signed on the closed
  triangle; the 17,824 factors partition as 5,665 interior-zero, 12,096
  empty, and 63 unresolved; and exactly 77 witnessed interior-zero factors
  are absent from both accepted edge roadmaps. The result has no global,
  infinity, pair-closure, or theorem-score consequence.
artifacts:
  - path: ops/team/triangle-referee/verify_order2_triangle_pilot.py
    digest: recorded in ops/team/triangle-referee/MANIFEST.sha256
  - path: ops/team/triangle-referee/RESULT_HANDOFF.md
    digest: recorded in ops/team/triangle-referee/MANIFEST.sha256
replay:
  command: >-
    PYTHONDONTWRITEBYTECODE=1 python
    ops/team/triangle-referee/verify_order2_triangle_pilot.py
  result: >-
    exit 0; 70/70 strict parent signs; exact factor partition
    5665+12096+63=17824; 77 exact interior-zero/edge-absent factors; no
    unresolved promotion; 10/10 hostile mutations rejected.
coverage:
  included: >-
    The closed barycentric triangle conv(chart0,chart89,chart113), all 70
    row-2599 parent brackets, all 17,824 pinned candidate residual factors,
    and the complete event-factor sets on compiled edges 27 and 39.
  excluded: >-
    The uncompiled chart89-to-chart113 side as a labelled roadmap; points
    outside the triangle; global wall-component and parent-cell coverage;
    genuine parent infinity; middle-rank replay; pair closure; the triple
    obligation; and promotion from 2/9.
canaries:
  positive: >-
    Exact parent controls, complete status partition, all stored interior
    witnesses, and all 77 edge-absence claims independently replayed.
  negative: >-
    One-signed nonzero controls are required for emptiness; mixed or zero
    controls at the depth limit remain unresolved.
  null: >-
    All 63 depth-limit factors remain in the unresolved set and in neither
    proved class.
  hostile: >-
    Re-sealed unsafe-square, false-infinity, global-coverage, pair-closure,
    3/9, factor-ID, witness-sign, count, input-digest, and parent-digest
    mutations were rejected (10/10).
source_accounting:
  used: >-
    Raw catalog, 178-chart point bank, 26,740-factor census arrays,
    17,824-ID candidate stream, and accepted edge-27, edge-39, and combined
    artifacts at their declared SHA-256 digests.
  unused_or_missing: >-
    The producer module was read only for contract/rule audit and was never
    imported or executed by the referee. No certificate-engineer worktree,
    discovery state, or unpublished candidate was inspected.
open_defects:
  - >-
    No defect in the bounded triangle certificate was found.
  - >-
    Integration metadata defect outside the triangle candidate:
    ops/team/coverage-falsifier/RESULT_HANDOFF.yaml still records the
    pre-determinism artifact/script digests 8baa... and c3adc..., while the
    descendant bytes are 454207f8... and e4ad1b0b... after commit 530baa8.
  - >-
    Minor replay-portability defect outside the triangle candidate: the
    hidden-root generator successfully writes a byte-identical /tmp output,
    then exits 1 because its final ARTIFACT display assumes the output is
    repository-relative. The documented repository-relative invocation is
    unaffected.
next_action: >-
  Integrate the bounded triangle certificate with this verifier after fixing
  the stale falsifier handoff digests. Use the 77 exact interior wall hits to
  design a third-side or two-dimensional component/closure attachment; do
  not infer global parent-cell coverage from this bounded pilot.
ledger_change_recommended: >-
  None to theorem status. Record only a finite exact bounded-triangle result;
  diag3_pair_hc1 remains OPEN and the honest score remains 2/9.
```

## Independence boundary

The verifier does not import or run
`ops/team/triangle-certificate/build_order2_triangle_pilot.py`. It implements
its own:

- integer determinant and Cramer normalization of the raw 4-by-8 matrices;
- sparse polynomial determinant and primitive normalization for the 70
  parent brackets;
- decoding of the raw factor offset/exponent/coefficient arrays and candidate
  binary stream;
- 9-to-2 exact affine substitution;
- simplex-Bernstein conversion, longest-edge subdivision, witness evaluation,
  and status grouping;
- event-factor extraction from the accepted edge artifacts; and
- complete semantic comparison plus re-sealed hostile mutations.

The candidate producer was inspected only to identify the declared
classification rules and artifact schema that the referee was required to
audit.

## Mathematical rule audit

### Empty rule

On a closed simplex, a polynomial is a Bernstein-basis convex combination of
its controls: the basis functions are nonnegative and sum to one. Therefore
strictly positive controls make the polynomial strictly positive everywhere,
and strictly negative controls make it strictly negative everywhere. Either
case proves that the zero set on that leaf is empty.

Deterministic longest-edge bisection replaces one triangle by two closed
triangles whose union is exactly the original and whose intersection is their
shared edge. Consequently, one-signed nonzero controls on every terminal leaf
prove emptiness on the whole original closed triangle. A mixed or zero
control hull does not prove a zero exists; the candidate correctly retains
every such depth-limit leaf as `UNRESOLVED`.

### Interior-zero rule

The triangle's three barycentric coordinates are affine and nonnegative at
both endpoints of every candidate witness segment. The open segment lies in
the strict triangle interior exactly when no barycentric coordinate is zero
at both endpoints. Under that checked condition, every open-segment point has
all three coordinates positive. Exact opposite endpoint signs then give a
zero on that open segment by continuity. An exact zero at an explicitly
strict interior point is immediate. These are sufficient conditions; neither
is used as a completeness claim.

The independent replay evaluated every witness against the raw restricted
factor polynomial. It found exactly `5,665` factors with sufficient interior
zero witnesses.

## Exact accounting and edge absence

The raw candidate stream has header
`(D3PFC001, parent=2599, factors=26740, candidates=17824)`, exact EOF, and
strictly increasing unique factor IDs. Independent classification gives:

| Status | Exact count |
|---|---:|
| interior zero | 5,665 |
| empty on closed triangle | 12,096 |
| unresolved at depth 3 | 63 |
| total | 17,824 |

The 63 unresolved IDs are disjoint from both proved classes. No unresolved
factor was promoted.

The accepted artifacts independently yield `1,217` distinct edge-27 event
factors, `5,209` edge-39 event factors, and a union of `5,616`. The event sets
parsed from the individual accepted artifacts equal those parsed from the
combined skeleton. The independently reconstructed set

```text
{interior-zero factors} minus {edge-27 or edge-39 event factors}
```

has exactly 77 members and equals the candidate's ordered 77-ID list. Every
one is linked to a replayed exact witness. This proves absence from the two
compiled roadmaps, not absence from the uncompiled third side and not a
global component statement.

## Exact replay results

### Triangle certificate

```console
PYTHONDONTWRITEBYTECODE=1 python \
  ops/team/triangle-referee/verify_order2_triangle_pilot.py
```

Result: exit `0`.

```text
PASS raw inputs and manifest pinned; charts=(0,89,113); exact closed triangle
PASS 70/70 strict parent signs by complete simplex-Bernstein controls
PASS factor accounting interior=5665 empty=12096 unresolved=63 total=17824
PASS 77 interior-zero factors have exact witnesses and are absent from edges 27/39
PASS no unresolved factor promoted; empty and interior rules are exact sufficient conditions
PASS hostile mutations rejected 10/10
SCOPE bounded triangle only; third edge uncompiled; no infinity/global coverage/pair closure/3-of-9
```

### Descendant-head skeleton no-go

```console
PYTHONDONTWRITEBYTECODE=1 python \
  ops/team/coverage-prover/verify_diag3_pair_skeleton_incidence_no_go.py
```

Result: exit `0`.

```text
PASS exact skeleton-incidence information no-go: parent_brackets=70 edges=40 source_factor=137 sphere=S^8 hostile_rejected=6 actual_claim=OPEN
```

This confirms the integration fix permits verification from descendant head
`e3989d3f...` while retaining mathematical base `ec362dba...`.

### Hidden-root byte determinism

The generator was replayed to `/tmp/triangle-referee-hidden-root.json` with:

```console
PYTHONDONTWRITEBYTECODE=1 python \
  ops/team/coverage-falsifier/prototype_exact_hidden_root_census.py \
  --workers 2 --edge-indices 0,39 \
  --output /tmp/triangle-referee-hidden-root.json
```

It completed the exact build and printed:

```text
OUTCOME NULL_EXACT_BOUNDED_CENSUS
EXACT_FACTOR_SEGMENT_PAIRS 13960
HIDDEN_ROOT_INCIDENCES 0
SEMANTIC_SHA256 071133c821c6b94fe6160ec19dba75b68ce342e3daeaf00b4b72132cc62b6950
```

It then exited `1` only in its final repository-relative display, as recorded
above. Byte comparison was independent and successful:

```console
cmp /tmp/triangle-referee-hidden-root.json \
  ops/team/coverage-falsifier/EXACT_HIDDEN_ROOT_CENSUS_EDGES_0_39.json
sha256sum /tmp/triangle-referee-hidden-root.json \
  ops/team/coverage-falsifier/EXACT_HIDDEN_ROOT_CENSUS_EDGES_0_39.json
```

Result: `cmp` exit `0`; both files have SHA-256
`454207f808ae41eb25c8b9e7c29dfa58a53942fff6acf229c7cef6f4de95ed9f`.
The hidden-root census is byte-deterministic.

## Publication decision

Accept the triangle artifact as a **finite exact bounded classification**
after independent verifier integration. Do not advance the ledger. The
triangle supplies new off-tree wall hits and a concrete next attachment
target, but it is neither a global coverage certificate nor a closure of the
pair invariant.
