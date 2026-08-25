# Diagonal three: exact no-go to one-source-family global incidence

## Refuted target

The following proposed pair-side lemma is false:

> Every row-2599 parent-interior residual wall meets the full normalized
> three-parameter hybrid cube joining charts 0 and 152.

Exact comparison finds **5,390** counterexample factors.  Each has an exact
sign crossing on one of the 105 certified parent-safe chart segments, hence a
zero in the strict row-2599 parent cell, while tensor Bernstein subdivision
certifies the same factor zero-free on the entire chart-0/chart-152 source
cube.

Consequently no component of any of those factors meets this source family.
Refining the staircase inside that cube cannot repair the failure.

This refutes a sufficient route, not the pair obligation itself.  The global
labelled relative master complex and its middle-rank replay remain open, and
the honest 9DVL score remains `2/9`.

## Exact census

The two independently certified sets compare as follows:

| set | count |
|---|---:|
| candidate full-support factors | 17,824 |
| walls crossing 105 exact parent-safe segments | 10,844 |
| walls occurring on the full source cube | 5,577 |
| known parent walls also meeting the source cube | 5,454 |
| known parent walls zero-free on the source cube | **5,390** |
| source-cube walls not crossed by the 105 segments | 123 |

The exact identities are

```text
5,454 + 5,390 = 10,844
5,454 +   123 =  5,577
5,577 + 12,247 = 17,824.
```

The semantic factor-ID digests are

```text
known parent walls     f9a66e8f5ffd14dc6b34f9998b82c26422e2f9e1475f4466840f1e8e74b45d5a
intersection           ef52b6bf65c9eda5b5a198c1e9e15ed275d90c7dffa083b9e928e294e60a2d66
parent but source-free 26cce16d217d55e01081dad817d13778d2c797724659bcebd51555eb66855382
source-only             16a8aa0c7aa1c49452dfc2b3f557453619027196aa0344f73200e45b114f3eca
```

## Smallest counterexample

Factor 5 already refutes the universal claim.  Its values at exact charts 0
and 2 have opposite signs:

```text
chart 0: -5942693761781748559302426261917373873341022883136
         /156789202497608619096004927663680072772461575232025

chart 2:  21596804186712527155375843113579392967471575575910976
         /193862553041661978582623048285724306587858705805075715
```

The chart-0/chart-2 segment is one of the 105 paths whose 70 signed parent
brackets are exactly positive throughout.  Continuity therefore gives a
strict-parent zero of factor 5 on that segment.  In contrast, its restriction
to the full chart-0/chart-152 source cube has a one-signed Bernstein control
net at depth zero, so it has no zero anywhere in that cube.

This single factor is a compact review witness.  The full 5,390-factor digest
prevents the no-go from being reduced to an anecdote or revived after a data
change.

## Strategic consequence

The target

```text
PROVE_EVERY_GLOBAL_WALL_COMPONENT_MEETS_CHART0_CHART152_SOURCE_FAMILY
```

is retired.  The eight-box yield stop is therefore stronger than an economic
decision: no subdivision or enlargement confined to the same full hybrid
cube can cover the 5,390 source-free known walls.

The replacement pair-side routes are:

1. add genuinely distinct source families whose union has an exact global
   incidence or coverage theorem; or
2. construct a direct semialgebraic roadmap/master complex in the parent cell
   without routing every wall through this one source family.

The second route remains the selected architecture unless a bounded
multi-source canary supplies a credible coverage invariant.

## Replay

Build the compact record with

```bash
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/build_diag3_pair_source_family_incidence_no_go.py
```

and run the independent hostile replay with

```bash
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/verify_diag3_pair_source_family_incidence_no_go.py
```

The verifier rechecks all 105 segments against all 70 signed parent brackets,
reconstructs the exact endpoint-crossing set, independently classifies all
17,824 source-cube restrictions, and evaluates exact opposite endpoint values
for every one of the 5,390 no-go factors.  It does not import the producer
core.
