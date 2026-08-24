# Adversarial review: regular algebraic-`u` `v` lift

Date: 2026-08-24
Initial reviewed commit: `913ae0a52da640ad3b1e1f0cf491967de9dee64e`

## Review angles

Three read-only agent passes audited the checkpoint from distinct angles:

1. certificate engineering and producer/verifier independence;
2. mathematical continuation, collision, and theorem-scope logic; and
3. repository integration, deterministic artifacts, and publication
   readiness.

No reviewer found a false census, missing mathematical case, or dishonest
theorem-score claim.  All blocking, major, and actionable lower-severity
findings were resolved before publication.

## Findings and resolutions

### Producer/verifier independence

The first verifier shared boundary reduction and canonicalization with the
projection producer.  The verifier now contains its own primitive integer
normalization, synthetic division, and `u,t,1-u,1-t` boundary stripping.  It
independently reconstructs the 136-polynomial projection catalog and its
semantic digest, then checks the complete
projection -> base -> roots -> open-sector -> open-`v` source chain.

The engineering re-review reproduced the raw-event digest
`560e5be20b8f11c4df3b3415a28afabc4c654dc86f9c672c4068f055fe2e43ba`
and returned no remaining blocking or major finding.

### Branch continuation and invisible resultants

The mathematical review independently checked all 120,174 accepted sections:
zero changed their bounded branch-token set.  It also checked every one of the
13,624 non-inverting raw-resultant incidences: each has at least one owner
absent from the bounded root stack.

Both facts are now explicit producer and verifier assertions.  Synthetic
canaries additionally reject a bounded invisible resultant, a non-clique
collision component, and an inversion without a raw-resultant owner.

The reviewer confirmed that:

- triple and higher simultaneous collisions are encoded by clique components;
- tangencies are excluded by raw multiplicity one;
- complex-to-real changes and same-wall quadratic collisions are excluded by
  discriminant events;
- degree loss or roots at infinity are excluded by coefficient events; and
- roots at `v=0,1` are excluded by the 44 endpoint factorizations and seven
  endpoint base factors.

### Provenance, canaries, and integration

The hardened verifier checks source links, dependency metadata, the exact
132,134-section resource ceiling, and 20 hostile mutations.  Python patch
version is retained as nonsemantic provenance: the independent-verifier marker
and Python 3.12 family are enforced without making a rebuild depend on one
patch release.

The integration review independently verified every shard path, index, byte
count, SHA-256 value, and canonical gzip encoding.  It also checked README
arithmetic, the decision-ledger checkpoint, both historical blob pointers,
automatic `run_all.py` discovery, and deterministic CI shard coverage.

## Final review verdict

Content verdict: **PASS**.

The exact scope remains a proof-bearing partial lift over regular algebraic
`u` sections in open `t` sectors.  The 11,960-section residue, every
algebraic-`t` `v` lift, global gluing, extension-signature labels, relative
middle-rank replay, and both diagonal-three invariant obligations remain
open.  The honest 9DVL score remains **2/9**.

Publication still requires a green CI run on the exact published head before
merge; that operational gate is not a mathematical claim.
