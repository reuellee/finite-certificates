# MP-002: block-route event-count transfer

## Result in one sentence

The preregistered transfer candidate is **refuted**: on the mechanically
selected held-out chart-0-to-chart-66 route class, the minimum-event order
`102` has 824 signatures with alternation at least three, while order `120`
has only 476 despite using 134 more wall events.

This is an exact held-out counterexample on three pinned routes.  It does not
assert a law for other routes or oriented matroids, claim mathematical
novelty, or change the honest 9DVL score of **2/9**.

## Preregistered holdout

MP-001 retrospectively found that order `102` minimized the exact wall-event
count, transition mass, and every nonzero alternation tail on all three
parent-safe chart-0-to-chart-152 block routes.  MP-002 tested whether the
event-count part transferred.

Before any new label history was constructed, the holdout object was selected
by this exact rule:

1. exclude the two endpoints already used by MP-001;
2. retain chart endpoints admitting at least two parent-safe three-block
   orders;
3. minimize endpoint residual-factor-state Hamming distance; and
4. break a tie by chart index.

Exact enumeration leaves 13 eligible endpoints and selects chart 66 at
Hamming distance 1,812, with precisely the valid orders `102`, `120`, and
`210`.  The registration is pinned at Git commit
`c818dd8415ffa3c1286f2d3200f93276f10ce98b`.

Phase A then generated exact wall events without constructing extension-label
histories.  Order `102` was frozen as the prediction at commit
`4ddd987d4f2cbc55459f557fc578ee7dec55806e`.  A pinned minimal Git object-store
archive preserves that commit and its registration parent across connector
publication.  It proves that none of the three canonical phase-B result paths
existed at the freeze; as with any preregistration protocol, repository
history cannot prove the absence of an unrecorded private calculation.

| order | exact events | compound events | segment event census |
|---|---:|---:|---|
| `102` | 4,228 | 171 | 2,011, 1,491, 726 |
| `120` | 4,362 | 183 | 2,011, 757, 1,594 |
| `210` | 4,958 | 223 | 859, 2,505, 1,594 |

The registered success condition was that the minimum-event route weakly
minimize every nonzero alternation tail, with a strict improvement at least
once.  A single lower rival tail was registered as a refutation.

The registered one-replay ceiling applies to the observational phase-B
continuation: each held-out route was observed once.  The later independent
verification replay is an audit outside the discovery budget.  Both producer
and verifier now reject worker counts outside the registered range `1..6`.

## Exact held-out result

All three routes were continued exactly on the same 97,224-signature universe
after the prediction freeze.

| order | transition mass | max `a_x` | maximizers | tail >=1 | >=2 | >=3 | >=4 | >=5 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `102` | 33,192 | 5 | 2 | 22,512 | 9,794 | **824** | 60 | 2 |
| `120` | 34,864 | 5 | 2 | 23,696 | 10,604 | **476** | 86 | 2 |
| `210` | 41,712 | 5 | 26 | 25,948 | 13,824 | 1,624 | 290 | 26 |

Thus `102` is better than `120` at thresholds 1, 2, and 4, equal at 5, and
worse at 3.  Both strictly tail-dominate `210`.  The exact tail Pareto
frontier is therefore `{102, 120}`, and the restricted minimax alternation is
five.  Event-count order and transition-mass order happen to agree here, but
neither scalar order captures the tail comparison.

## Certificate and replay boundary

The independent verifier:

- reconstructs the complete 13-endpoint selection frontier from the exact
  chart bank and all 70 signed parent inequalities;
- proves the registration commit precedes the prediction-freeze commit and
  that no phase-B record existed at the freeze;
- checks every pinned input, producer, prediction, and result hash;
- validates signature census, transition mass, endpoint parity, maximizer
  histories, antipodal closure, all tail counts, dominance, and the Pareto
  frontier without trusting stored verdict booleans; and
- rejects 13 hostile mutations, including false promotion, scope expansion,
  novelty inflation, score contamination, and destruction of the exact
  counterexample.

With `--full-replay`, an orchestration independent of the MP-002 producer also
regenerates each exact event sequence and label history in memory from the
established wall, mutation, and tope primitives, then requires equality with
the committed record.  This is a finite certificate for the stated
counterexample, not an explanation of why the threshold-three reversal
occurs.

## Application

Wall-event count remains useful for estimating exact replay work, but MP-002
shows that it cannot be used alone when the certificate cost depends on the
exceptional-history tail.  Later route selection should retain at least two
coordinates:

- event count for replay cost; and
- the complete nonzero alternation-tail vector for history compression.

The exact route class then has a two-point Pareto frontier instead of a false
single winner.  This prevents a 134-event saving from concealing 348 extra
threshold-three exceptional histories.

## Prior-art and novelty boundary

Pareto-efficient path sets are standard in multiobjective shortest-path
optimization; exact algorithms explicitly retain nondominated cost vectors
([Maristany de las Casas--Sedeño-Noda--Borndörfer](https://opus4.kobv.de/opus4-zib/files/7971/main.pdf)).
Bottleneck labelled graph optimization is also established and asks paths or
other subgraphs to control their use of edge-label classes
([Hassin--Monnot--Segev](https://hal.science/hal-00917828/document)).

MP-002 is adjacent to, but not an instance of, the usual additive-vector
shortest-path model: each threshold coordinate counts signatures whose total
number of membership flips reaches that threshold.  It is likewise not the
single-label-per-edge bottleneck model because an event may change many
signature labels.  No novelty is claimed for Pareto dominance, alternation,
or labelled-path optimization.  The retained contribution is the exact,
preregistered counterexample and its concrete certificate-design consequence.

## Reproduction

From the repository root:

```bash
python ai/scouting/explore_block_route_transfer.py phase-a
python ai/scouting/explore_block_route_transfer.py phase-b 102 --workers 6
python ai/scouting/explore_block_route_transfer.py phase-b 120 --workers 6
python ai/scouting/explore_block_route_transfer.py phase-b 210 --workers 6
python ai/scouting/build_mp002_holdout_history_archive.py
python ai/scouting/build_mp002_block_route_transfer_manifest.py
python ai/scouting/verify_mp002_block_route_transfer.py
python ai/scouting/verify_mp002_block_route_transfer.py --full-replay --workers 6
```

The machine-readable quantifiers, chronology, exact counterexample, finite
class, scope exclusions, hashes, and application are in
`ai/scouting/data/MP002_BLOCK_ROUTE_TRANSFER_MANIFEST.json`.
