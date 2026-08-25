# MP-001: extension-path alternation

## Result in one sentence

Among the complete finite class of parent-safe three-block routes from the
pinned row-2599 chart-0 representative to chart 152, order `102` strictly
minimizes every nonzero alternation tail, the event count, and total transition
mass; all three valid orders still have maximum alternation five.

This is an exact retrospective computation on pinned inputs, not a holdout-
validated general law.  Under the prospecting protocol it remains an
`OBSERVATION`.  It does not change the honest 9DVL score of **2/9**.

## Statistic and universal checks

For a finite signature universe `X` and a sequence of open-chamber label sets
`L_0,...,L_m`, define

```text
a_x = number of indices i with x in exactly one of L_i and L_(i+1).
```

The following identities hold for every such finite sequence:

```text
sum_x a_x = sum_i |L_i symmetric_difference L_(i+1)|,
{x : a_x is odd} = L_0 symmetric_difference L_m.
```

They follow respectively by double-counting flips and by parity.  When every
`L_i` is antipode-closed, `a_x = a_antipode(x)`.  The number

```text
(a_x + 1[x in L_0] + 1[x in L_m]) / 2
```

counts runs in the discrete word of open-chamber memberships.  It is not, by
itself, a count of connected pieces in a continuous feasibility trace; that
interpretation requires separately certified wall and waypoint semantics.

## Exact comparison

Exact parent-bracket evaluation of all six block permutations leaves precisely
three parent-safe orders: `012`, `021`, and `102`.  Their endpoints and
signature universe are identical.

| order | events | transition mass | max `a_x` | maximizers | tail >=1 | >=2 | >=3 | >=4 | >=5 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `012` | 5,612 | 48,788 | 5 | 14 | 35,144 | 11,648 | 1,734 | 248 | 14 |
| `021` | 5,970 | 53,436 | 5 | 20 | 36,322 | 13,944 | 2,874 | 276 | 20 |
| `102` | 5,564 | 46,844 | 5 | 2 | 34,234 | 10,794 | 1,684 | 130 | 2 |

Consequently:

1. the restricted block-order minimax is exactly five;
2. order `102` strictly tail-dominates each other valid order at every
   threshold `k=1,...,5`;
3. order `102` also uses strictly fewer wall events and has strictly smaller
   transition mass; and
4. the four reconstructed maximizer sets (the chart-0-to-89 source path plus
   all three chart-0-to-152 routes) are pairwise disjoint.

The last point refutes the motivating retrospective candidate that two
previously committed spectra with 14 maximizers might share an exceptional
signature core.  Equal extremal census did not identify equal extremizers.

## Proof and certificate boundary

The restricted minimax and dominance statements are finite consequences of:

- exact enumeration of the six permutations using all 70 strict signed parent
  brackets at every block waypoint;
- exact Sturm isolation of every candidate-factor crossing on the three valid
  routes;
- exact label continuation through simple mutations and exact compound-event
  re-enumeration;
- recovery of the two previously committed spectra for the source and `012`
  paths as hard stops; and
- structural rechecking of spectra, parity, transition mass, maximizer
  histories, antipodal closure, order completeness, provenance hashes, and
  nine hostile mutations.

The structural verifier deliberately does not pretend to be a second
implementation of the expensive label continuation for `021` and `102`.
Those two records can be rederived using the producer commands below.  The
lack of a pre-registered holdout is why the ledger does not promote MP-001
beyond `OBSERVATION`, despite exact finite arithmetic.

## Application

For any later exact certificate that is permitted to use this same pinned
three-block route class, `102` is the preferred route.  Relative to the
previous `012` choice it removes 48 wall events, 1,944 units of transition
mass, and 118 signatures from the `a_x >= 4` tail; it reduces the maximizer
count from 14 to 2, with a disjoint maximizing pair, without increasing the
bottleneck value.  This reduces replay work and the size of the exceptional-
history appendix.

No claim is made about arbitrary piecewise-linear or curved paths, other chart
representatives, all paths in the row-2599 parent cell, or oriented matroids in
general.

## Prior-art boundary

For a fixed chamber order, the signature histories are rows of a binary
matrix and `a_x` is ordinary rowwise total variation.  A one-run row is the
fixed-order consecutive-ones property; bounded run count is adjacent to the
discrete interval and `d`-interval viewpoints.  Tucker-pattern work provides
certificates for failure of the consecutive-ones property
([Lindzey--McConnell](https://arxiv.org/abs/1401.0224)); `d`-interval
hypergraphs are a developed theory
([Aharoni--Holzman--Zerbib](https://arxiv.org/abs/1605.01942)).

Davenport--Schinzel sequences instead constrain alternating subsequences
between pairs of symbols, so their bounds do not follow from these per-row
membership flips ([Nivasch](https://arxiv.org/abs/0807.0484)).  Minimizing a
maximum label load on a graph is also an established bottleneck-labelled
optimization model; the present events carry multiple signature labels and
are therefore an adjacent multi-label generalization, not the identical model
([Hassin--Monnot--Segev](https://doi.org/10.1007/s00453-008-9261-4)).

Accordingly, MP-001 claims no novelty for alternation counts, run counts, the
double-counting identities, or bottleneck path optimization.  The potentially
useful contribution is the exact oriented-matroid path-selection instance and
its certificate-compression consequence.

## Reproduction

From the repository root:

```bash
python ai/scouting/explore_extension_path_alternation.py source
python ai/scouting/explore_extension_path_alternation.py block --workers 6
python ai/scouting/explore_extension_path_alternation.py order-021 --workers 6
python ai/scouting/explore_extension_path_alternation.py order-102 --workers 6
python ai/scouting/verify_extension_path_alternation.py
```

The pinned inputs, result hashes, exact spectra, tail counts, claim exclusions,
and finite conclusions are in
`ai/scouting/data/EXTENSION_PATH_ALTERNATION_MANIFEST.json`.
