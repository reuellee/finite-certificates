# Coverage falsifier: endpoint parity obstruction

Base revision: `ec362dba8a912bc4749c004641aee2da0a88dc05`.

## Exact obstruction

The optimal 40-edge cover is an exact set cover for **opposite endpoint
signs**.  That incidence is not the root incidence of the restricted wall
polynomials, even on a retained edge.

On retained edge 39 (charts 0--113), factor `1118` has the exact primitive
restriction stored in `EXACT_HIDDEN_ROOT_CENSUS_EDGES_0_39.json`.  Its two
endpoint values have the same nonzero sign, while Sturm replay counts exactly
two distinct roots in the open segment.  Thus it contributes zero to the
endpoint Hamming distance but two actual wall hits.

The complete accepted edge-39 roadmap makes this a 118-factor phenomenon:

| quantity | exact count |
|---|---:|
| endpoint Hamming distance | 5,091 |
| rooted factors | 5,209 |
| distinct interior roots | 5,327 |
| one-root factors | 5,091 |
| two-root factors with equal endpoint signs | 118 |

The 118-factor ID digest under domain
`diag3-edge39-even-root-factor-ids-v1` is
`b2adb224b9385ae05e57269a1ff7257675a8a612257301694dee0d3772586a1e`.

Therefore endpoint-sign membership, endpoint Hamming counts, and the
40-of-105 set-cover optimum cannot supply a component-coverage argument.  A
compiler may recover all roots on a chosen segment by exact Sturm replay, as
edge 39 already does; it still needs a separate theorem that every relevant
global component meets the finite source skeleton.

## Bounded residue census

As a useful null result, the prototype exactly tested every one of the 6,980
endpoint-uncrossed candidates on edge 0 (omitted from the 40-edge cover) and
edge 39 (retained).  All 13,960 restrictions are root-free on the open
segments.  In particular, the 118 edge-39 parity witnesses are already among
the globally endpoint-crossed 10,844, so this cycle does not reclassify any of
the 5,803 feasibility-unknown factors.

The exact scope is two of 105 segments.  The interrupted all-edge run did not
produce an accepted census and is not claimed.

## Replay

```console
PYTHONDONTWRITEBYTECODE=1 python \
  ops/team/coverage-falsifier/prototype_exact_hidden_root_census.py \
  --workers 2 \
  --edge-indices 0,39 \
  --output ops/team/coverage-falsifier/EXACT_HIDDEN_ROOT_CENSUS_EDGES_0_39.json
```

Expected terminal summary:

```text
OUTCOME NULL_EXACT_BOUNDED_CENSUS
EXACT_FACTOR_SEGMENT_PAIRS 13960
HIDDEN_ROOT_INCIDENCES 0
SEMANTIC_SHA256 071133c821c6b94fe6160ec19dba75b68ce342e3daeaf00b4b72132cc62b6950
```

The artifact SHA-256 is recorded in `RESULT_HANDOFF.yaml`.  Positive, null,
and hostile canaries respectively detect a two-root/equal-endpoint
polynomial, accept a zero-free affine polynomial, and reject endpoint roots
and an identically zero restriction.

## Scope and decision

This disproves only the inference that endpoint-sign segment data determine
root or component coverage.  It does **not** prove that factor 1118 has two
global components, that a component is disjoint from all 105 segments, or
that exact compilation of the other 38 retained edges has no local value.
It does not close the pair or triple obligation and cannot change `2/9`.

Recommendation: pause bulk edge compilation until a factor-specific global
coverage bridge is stated and passes a bounded discriminator.  The next
highest-value test is a certified transverse collar or parent-safe
two-parameter patch for a preregistered multi-root factor family, asking
whether all wall components in that patch reach its true outer boundary and
whether the outer boundary maps to already certified source cells.  Failure
would yield the desired missed-component witness; success would expose the
precise additional gluing invariant a global roadmap must carry.
