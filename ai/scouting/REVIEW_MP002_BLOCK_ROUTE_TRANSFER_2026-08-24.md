# Adversarial review: MP-002 block-route transfer

Date: 2026-08-24
Initial result commit: `1095cbb570a67159ee4f5f0b6ce2729a06109ed7`

## Review angles

An independent read-only agent audited the preregistration chronology,
resource contract, exact finite identities, producer/verifier independence,
claim boundary, and repository integration.  The initial review found no
incorrect result census, but it did identify provenance and replay-independence
defects that had to be corrected before publication.

## Findings and resolutions

### Preregistration chronology

Publication through the repository connector cannot preserve the local commit
identifiers used for the registration and prediction freeze.  A deterministic
minimal shallow Git object-store archive now carries those two exact commits
and the 14 required loose objects.  The verifier checks the archive SHA-256,
safe extraction, commit ancestry, exact registration and prediction contents,
the freeze-time producer hash, and absence of all three canonical phase-B
result paths at the prediction commit.

The documentation now states the evidence precisely: repository history proves
absence at those paths, but cannot prove absence of an unrecorded private
calculation.

### Resource accounting and provenance

The registered ceiling applies to one observational exact continuation per
route.  One later independent verification replay is an audit outside that
discovery budget.  The producer and verifier both enforce the registered
worker range `1..6`; an explicit zero is rejected rather than replaced by a
default.

The manifest separates the SHA-256 of the producer at prediction freeze from
the current reproducer.  The only post-result producer change is worker-ceiling
validation; the result files and their semantic hashes are unchanged.

### Independent replay

The first full-replay implementation imported the MP-002 producer.  It now
orchestrates the established wall, mutation, and tope primitives independently,
reconstructs the factor-to-four-set map from the pinned factor census, and
requires exact equality with every committed result record.

The hardened replay also checks the 26,112-tope cardinality after every event,
requires all changed signatures to remain in the pinned 97,224-signature
universe, and compares the exact odd-transition signature set with the endpoint
symmetric difference rather than checking only its cardinality.

### Claims and hostile mutations

The default verifier independently recomputes selection, spectra, tail counts,
transition mass, endpoint parity, antipodal maximizer closure, dominance, and
the Pareto frontier.  Thirteen hostile mutations reject false promotion,
scope expansion, novelty inflation, theorem-score contamination, resource
inflation, prediction leakage, and destruction of the exact counterexample.

The prior-art discussion uses primary sources only and makes no novelty claim.
The exact result remains a bounded refutation of the registered transfer
hypothesis, not a general theorem about block routes or oriented matroids.

## Final review verdict

Content verdict: **PASS**.  The final independent full replay matched all three
result records at semantic SHA-256 values `00b5de19c1fbcbcf34715b387fad479c4e0b6794dd2dff1e47bb82ab9b910bb8`,
`f0351621cddd213bdee0eaaa337793f1eba7618f361201f50ab08c23498a5e0d`, and
`db4afaa6a1d91562d839b10cd5642b97aa565ac906af173a19584e79d94b94e4`.
Publication still requires the exact published head to pass CI.

Order `102` uses 4,228 events but has 824 signatures with alternation at least
three; order `120` uses 4,362 events but has only 476.  Thus the preregistered
prediction is **REFUTED** with tail gap 348.  The honest 9DVL score remains
**2/9**.
