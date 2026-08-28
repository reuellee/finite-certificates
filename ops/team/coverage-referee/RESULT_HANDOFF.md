# Coverage-referee result handoff — 2026-08-28

```yaml
track_id: cycle-2026-08-28-referee-coverage
base_revision: ec362dba8a912bc4749c004641aee2da0a88dc05
outcome: finite-exact
summary: >-
  The frozen cover, two-edge skeleton, collar, ledger, and closure-gap
  certificates replay exactly and state their local scope honestly, but the
  evidence falsifies bulk compilation of the remaining 38 edges as the
  highest-value next action: the complete selected chart graph is an
  eight-component forest, and no certificate transports finite path hits to
  all wall components or to the parent cell.
artifacts:
  - path: ops/team/coverage-referee/RESULT_HANDOFF.md
    digest: recorded in ops/team/coverage-referee/RESULT_HANDOFF.sha256
replay:
  result: >-
    All six primary commands exited 0. A redundant replay of the separate
    edge-39 lower-level referee was stopped at the coordinator's finalize
    instruction after precomputation began; the accepted edge-39 bytes and
    profile map were independently pinned and reconstructed by the completed
    combined-skeleton referee.
coverage:
  included: >-
    Frozen optimal 40-of-105 endpoint-sign cover; edges 27 and 39; their exact
    glued 1-dimensional labelled tree; the factor-19069 two-dimensional
    collar; canonical diagonal-three accounting; and the exact proof that the
    current inventory does not encode a coverage-certified global closure
    object.
  excluded: >-
    Connected components outside the declared collar, global row-2599
    parent-cell coverage, the 5,803 feasibility-unresolved factors, global
    two-cells and strict closure triples, parent-infinity completion,
    middle-rank replay, all 1,162,302 unresolved triple rows, and every claim
    that diagonal three or another diagonal is proved.
canaries:
  positive: >-
    Cover optimum, exact crossings, two-edge tree, joint profile map, collar
    monotonicity/topology, ledger accounting, and closure-gap inventory all
    replayed successfully.
  negative: >-
    The closure-gap replay again returns OPEN at
    coverage_certified_global_cell_universe; the collar keeps artificial
    boundary distinct from parent infinity.
  null: >-
    No global missed-component certificate is present, and no existing
    artifact can be decoded into one.
  hostile: >-
    21/21 cover, 9/9 combined-skeleton, and 20/20 collar hostile mutations
    were rejected.
source_accounting:
  used: >-
    Repository base ec362dba and the four work-order digests listed below.
  unused_or_missing: >-
    No producer branch, producer intention, other worktree, or unpublished
    candidate was inspected. A global component certificate is missing by
    construction.
open_defects:
  - >-
    Publication blocker: no exact implication from endpoint sign crossings
    on the finite source forest to all connected components of any global
    wall, much less all active walls.
  - >-
    Coverage blocker: 5,803 of the 17,824 full-support factors remain
    feasibility-unresolved; the 40-edge cover concerns only the 10,844 known
    crossed factors.
  - >-
    Topology blocker: the full 40-edge selected chart graph has 48 vertices,
    40 edges, 8 components, and cycle rank 0. Compiling it only subdivides a
    forest; it supplies no two-cells or strict three-cell chains.
  - >-
    Metadata defect: the canonical ledger at digest 7922d7... contains the
    PR-38 edge-39 result but still declares audited_commit e8600495... and
    merged_pull_request 37. Its verifier hard-codes and therefore accepts the
    stale pointer at base ec362dba (merged PR 38).
next_action: >-
  Run a preregistered full-parent coverage pilot for mandatory factor 19069:
  inventory every component of its wall in the compactified row-2599 parent
  domain and prove each meets edge 39 or genuine parent infinity, or emit an
  exact missed-component countercertificate. Do not compile another edge
  solely to enlarge the finite path transcript.
ledger_change_recommended: >-
  None to theorem status. After integration only, refresh repository metadata
  to the exact reviewed head; keep both diagonal-three obligations OPEN and
  the score 2/9.
```

## Pin audit

All work-order digests matched the bytes at the pinned base:

| Artifact | SHA-256 |
|---|---|
| optimal segment cover | `19248dd148d1fd002931ed5f48197869dd42c68a513376e1a4d6941389bda307` |
| edge-27/39 combined skeleton | `dcb707220df3e61b1a94eeedcf8e46b6602f30d405f4a92fc542c0f52f672806` |
| factor-19069 collar | `5930cc19019470fdfdf55d67523f6c4211ccf5b540f5c2bb5df36c64db75d7bd` |
| decision ledger | `7922d769aa30a84c5d208dec92d2e78d5c7744cc6184ea1d42aaeadf947761b3` |

Command:

```console
sha256sum \
  ai/omreal/data/DIAG3_PAIR_FULLSUPPORT_SEGMENT_COVER.json \
  ai/omreal/data/DIAG3_PAIR_FULLSUPPORT_LABELED_SKELETON_EDGE27_EDGE39.json \
  ai/omreal/data/DIAG3_PAIR_FULLSUPPORT_COMPONENT_COLLAR.json \
  ai/omreal/data/DIAG3_RESEARCH_DECISION_LEDGER.json
```

Result: exit `0`; exact digests above.

## Exact replay record

Each command was run from the pinned worktree with
`PYTHONDONTWRITEBYTECODE=1`.

| Command | Exit | Deterministic terminal result |
|---|---:|---|
| `python ai/omreal/verify_diag3_pair_fullsupport_segment_cover.py` | 0 | optimum 40 edges; 10,844 known crossed factors; 21 hostile mutations rejected; global components open |
| `python ai/omreal/verify_diag3_pair_fullsupport_labeled_skeleton_EDGE27_EDGE39.py` | 0 | `V=6567`, `E=6566`, `H0=1`, `H1=0`, 11,719 profiles; 38 edges pending; 9 hostile mutations rejected |
| `python ai/omreal/verify_diag3_pair_fullsupport_component_collar.py` | 0 | unique factor-19069 component on the declared collar; 17-cell CW; 20 hostile mutations rejected; global gap open |
| `python ai/omreal/verify_diag3_research_decision_ledger.py` | 0 | both invariant obligations open; `2/9`; `10,844+1,177+5,803=17,824` |
| `python ai/omreal/verify_diag3_pair_global_closure_gap.py --manifest ai/omreal/data/DIAG3_PAIR_GLOBAL_CLOSURE_OPEN_OBJECT.json` | 0 | `OPEN ... coverage_certified_global_cell_universe`; no global poset encoded |
| `python ai/omreal/verify_diag3_completion_open_object.py --manifest ai/omreal/data/DIAG3_COMPLETION_OPEN_OBJECT.json` | 0 | triple `77,940,147/79,102,449`; residue `1,162,302`; pair closure missing; `2/9` |

One redundant command,
`python ai/omreal/verify_diag3_pair_parent_source_EDGE39_0_113.py`, entered
its 293-compound-state precomputation but was stopped with exit `130` when the
coordinator requested immediate finalization. No acceptance statement depends
on that incomplete invocation: the completed combined-skeleton referee pins
the transition, label, and profile artifacts byte-for-byte and reconstructs
the edge-39 cells, incidences, joint profiles, scope, and collar attachment.

The independent finite graph/incidence audit used the accepted checkpoint
verifier's input reconstruction, not either candidate producer:

```console
PYTHONDONTWRITEBYTECODE=1 python - <<'PY'
import collections, json, sys
sys.path.insert(0, 'ai/omreal')
import verify_diag3_pair_fullsupport_segment_cover as v
_, candidates, incidence = v.exact_inputs()
proof = v.combinatorial_optimum(candidates, incidence)
for edges in ((27,), (39,), (27, 39), tuple(proof['selected'])):
    mask = incidence[list(edges)].any(axis=0)
    print(len(edges), int(mask.sum()), int(incidence[list(edges)].sum()))
pairs = json.load(open(v.CERTIFICATE))['source_bank']['selected_chart_pairs']
adj = collections.defaultdict(set)
for left, right in pairs:
    adj[left].add(right); adj[right].add(left)
seen, components = set(), []
for vertex in adj:
    if vertex in seen: continue
    stack, component = [vertex], []
    seen.add(vertex)
    while stack:
        current = stack.pop(); component.append(current)
        for neighbor in adj[current]:
            if neighbor not in seen:
                seen.add(neighbor); stack.append(neighbor)
    components.append(component)
print(len(adj), len(pairs), len(components),
      len(pairs)-len(adj)+len(components),
      sorted(map(len, components), reverse=True))
PY
```

Result: exit `0`.

- Edge 27 crosses `1,197` known factors.
- Edge 39 crosses `5,091` known factors.
- Their union crosses `5,526/10,844`; the sum of incidences is `6,288`.
- All 40 cross all `10,844`; the incidence sum is `157,448`.
- The selected chart graph is exactly `V=48`, `E=40`, `components=8`,
  `cycle_rank=0`, with component sizes `19,10,8,3,2,2,2,2`; every component
  is a tree.

## Falsification conclusion

The full-40 compilation hypothesis has now passed its engineering canary twice
(edges 27 and 39). A third ordinary edge would chiefly demonstrate the same
compiler on another interval. Full compilation would add exact ordered events
and signature labels on 38 more finite paths, and it would raise known-factor
endpoint-witness coverage from `5,526` to `10,844`. Those are valid finite
facts, but they do not attack the first missing proof edge:

```text
finite path hit  !=  every global wall component hits the path forest
```

The exact full cover graph makes the limitation sharper: it is not a
two-dimensional skeleton awaiting subdivision; it is an eight-component
forest. Subdivision can create more vertices and one-cells but cannot create
the parent-cell cover, two-cells, or closure triples demanded by the master
closure contract. Therefore compiling the other 38 before a coverage theorem
has lower expected information value than trying to prove or refute the
missing transport implication directly.

## Ranked actions

| Rank | Candidate | Referee verdict |
|---:|---|---|
| 1 | coverage-certificate pilot | Highest discriminator. Use factor 19069, already pinned to edge 39 and locally understood, but certify its entire compactified parent-domain component inventory. A missed component immediately refutes the skeleton route; complete hits validate scaling. |
| 2 | direct parent-cell roadmap | Strongest proof-bearing pair route if the pilot fails or reveals uncontrolled components. It directly targets coverage, adjacency, boundary, closure, and labels, at high cost. |
| 3 | triple-roadmap pivot | Independent and proof-bearing; the full-space box canary is real, but scaling to `1,162,302` unresolved rows and genuine parent-boundary exits is less ready than the pair pilot. Keep active as a bounded parallel fallback. |
| 4 | next-edge compilation | Rational only when chosen by the coverage pilot to attach a newly certified component/family or to test a genuinely new singular event class. Not rational as an unconditioned third transcript. |
| 5 | full 40-edge compilation | Defer. It is expensive, yields only a labelled forest, and leaves the globality implication untouched. |
| 6 | diagonal-9 pivot | Lowest near-term probability of the requested `3/9`: its best roadmap remains local and it would require coverage across its own parent program, while diagonal three already has two mature obligation tracks. |

## Acceptance gates for later candidates

### Gate before one further standalone edge

The smallest publication-grade discriminator is a global factor-19069
certificate over the entire compactified row-2599 strict parent domain:

1. pin the parent domain, factor polynomial, edge-39 event, and all input
   digests prospectively;
2. emit a complete exact connected-component inventory of the wall, including
   all chart seams and boundary specializations;
3. prove every component meets edge 39 or a **genuine** parent boundary /
   infinity cell; artificial box or collar boundary does not count;
4. independently replay coverage, disjointness, no-duplicate accounting,
   source-pin orientation, and component-to-hit witnesses;
5. reject re-sealed hostile cases containing an extra missed component, a
   deleted seam, a false parent-infinity label, a duplicate component, a
   moved edge event, and a scope/theorem promotion;
6. on failure, preserve an exact missed-component witness or the smallest
   unresolved projection frontier and pivot to the parent-cell roadmap.

### Gate before bulk compilation of 38 edges

Extend the same global audit to the 49 unique-crossing factors that force the
34 mandatory edges. This is the smallest family tied directly to the cover's
optimality proof. Every component must receive an exact retained-edge or true
parent-boundary hit. One missed component rejects the finite-skeleton coverage
hypothesis; success makes compilation of the corresponding mandatory edges
rational because the label transcripts can then attach to globally certified
components.

### Gate for a theorem-bearing pair candidate

No candidate may advance the ledger unless it additionally:

- resolves or includes the 5,803 feasibility-unknown factors, instead of
  quantifying only over the 10,844 already crossed factors;
- proves a complete global cell universe with coverage, disjointness, and
  no duplicates;
- proves regular-ball dimensions, every strict closure pair and triple, all
  genuine parent-frontier/infinity cells, and face-compatible chart gluing;
- materializes complete labels for all 97,224 extension signatures and proves
  label closure under specialization;
- constructs signed integral boundaries with `d^2=0` and independently
  replays the required middle-rank equality;
- passes positive, negative, null, and re-sealed hostile canaries from frozen
  inputs at the exact reviewed revision.

These gates were not disclosed to or derived from a producer candidate during
this cycle.
