# D9 S12,37 oriented normal-link certificate contract v1

## Acceptance boundary

This contract covers only `D9_S1237_4SUPPORT_NORMAL_LINK_GATE1` at parent
2599 for family `S12,37` and supports `(3,1,15)` and `(3,3,7)`.  The source
base is commit `c55d896cc5c0370e993b793992a2f05d894e0095`, tree
`17299e84397aae158a2111cbe01b52f5be24bfd5`; the opening lock is commit
`c6bd7a6afeda0888fc950710b941cac6f6c9bf95`, tree
`9c2dbe39a3ea0f36e9e9c8f845e6f72e98526421`.

The five zero homogeneous coordinates on each support and the
parent-transverse coordinate give six inward normal axes.  Projectivizing
gives the required five-dimensional link.  A tangential face restriction is
not normal-link evidence.

The root JSON format is
`diag9-s1237-oriented-normal-link-certificate-v1`.  Artifact paths are
relative to this directory, may not escape it, and carry both a byte SHA-256
and a domain-separated semantic SHA-256 over canonical JSON records.  JSON
objects have exact field sets.  Rationals are reduced strings accepted by
`fractions.Fraction`; polynomial terms are nonzero and strictly ordered by
their exponent vectors.

Version 1 is an endpoint-neutral envelope, not a claim that a nonexistent
producer payload has been checked.  Its command-line acceptance path permits
only the two fail-closed frontier endpoints.  It structurally and arithmetically
preflights complete/no-go records, but refuses to return those mathematical
endpoints until a materialized producer payload identifies its exact partition
and obstruction witness methods and those methods receive a versioned
producer-independent adapter.  This refusal is deliberate: a digest-only
geometry assertion must never become an accepted result.

## Source census

Every endpoint must supply `literal_census.ndjson`.  The independent replay
reconstructs it rather than trusting a producer.  Its 3,539 records are
ordered by the original global factor ID and contain:

- the primitive nine-variable factor polynomial;
- the family-allowed representative orientation;
- every family signature imposing that orientation;
- the lexically first representative occurrence and chart-0 raw sign;
- every global occurrence of the factor, not only a sampled occurrence;
- each occurrence fourset, indices and labels from the 62-element stripped
  parent-unit table,
  fixed sign relative to the representative, and every aligned family side.

The reconstruction replays all 84,840 transported circuit occurrences,
removes exactly 8,916 certified-empty factors, and verifies the S12,37 active
union of 3,539 classes and 5,026 aligned occurrences.  Its semantic digest is
`a1b9d3d9da1e01df83621dc8f1c7959f86ae2e0d9bd3bc457124c561cbac245a`.
Reordering, dropping, duplicating, or flipping any record changes the stream
or fails exact equality.

## Root fields

`scope` is fixed to parent 2599, `S12,37`, the ordered two-support list, a
five-dimensional projective normal link, and ledger `2/9 -> 2/9`.
`source_binding` pins both commits and trees, the source manifest byte digest,
the active-sector semantic digest, and the independently reconstructed census
digest and counts.

`claims.sample_only` must be false.  The prohibited-consequence list is exact
and immutable.  No endpoint may claim that the tangential filter is a
collar, glue through boundary faces of the open realization space, promote
sampled coverage, infer global active-sector topology, decide diagonal nine,
or change the theorem ledger.

Each artifact reference has exactly `path`, `sha256`, `semantic_sha256`, and
`record_count`.  NDJSON is used for large inventories; JSON artifacts expose
their canonical list under `records`.

## Producer evidence

A producer must provide the following exact evidence.  A summary, a count, a
digest without its preimage, or a sample is insufficient.

### `literal_census.ndjson`

The producer must materialize exactly the independent census described above.
The replay compares every JSON value, not only its digest.

### `recursive_strata.json`

Each stratum record has an ID, support ID, kind, dimension, nonempty normal-axis
support, parent/boundary/coface incidence, a nine-polynomial exact chart map,
and a materialized exact rational simplicial-partition witness.  The replay
parses every rational vertex and recomputes the partition semantic digest;
an unmaterialized digest is rejected.  Allowed kinds are `INTERIOR`,
`FACET`, `BASE`, `APEX`, `SEAM`, `COFACE`, and `COEFFICIENT_ZERO`.

For a complete endpoint, both support records must collectively realize every
one of the 63 nonempty subsets of their six named normal axes.  Leading
coefficients that vanish on a facet, base, apex, seam, or coface require a new
recursive stratum; they may not be discarded or assigned the generic parent
label.  All incidence references must exist and stay within one support.
The partition witness must materialize its rational cells and exact boundary
and nonoverlap evidence in the producer artifact; `exact_partition_sha256`
binds that canonical stream.

### `normal_form_inventory.ndjson`

For every recorded stratum, this inventory contains one record for every one
of the 3,539 active literals and each of the 70 parent inequalities.  The 62
stripped brackets in the occurrence-unit table are a different census and do
not replace the complete 70-bracket parent-sign system.  A record
names its support/stratum/source, required orientation, lowest radial degree,
exact lowest multihomogeneous normal form, and the semantic digest of the
exact polynomial pullback identity.

The producer must materialize the pullback preimage behind that identity:
the nine compactified factor coordinates, the five zero-coordinate normal
axes, the parent-transverse axis, the radial variable, and the tangential
chart.  The replay independently composes the pinned primitive factor or
parent polynomial with the nine substitution polynomials, compares the full
pulled polynomial, extracts its first nonzero radial coefficient, and compares
that coefficient to the stored normal form.  A polynomial evaluated only at
test points is not an identity witness.

### `link_sectors.json`

Every sector names one recursive stratum and gives its complete exact sign
constraints.  A feasible sector supplies a rational point that the replay
evaluates in every strict/equality polynomial.  A linear-infeasible sector
supplies a nonnegative, nonzero Gordan multiplier vector whose exact weighted
coefficient sum is zero.  Nonlinear infeasibility requires a separately
versioned exact witness kernel; it cannot be relabeled as Gordan evidence.
Sector IDs are unique, adjacency is closed, and a complete endpoint has at
least one exact feasible sector on every stratum plus the producer's complete
sign-pattern coverage partition.

### `stabilization.ndjson`

For every literal on every stratum, the producer gives a positive rational
radius, positive leading margin, nonnegative tail bound, radial degree gap,
and the digest of the exact bound witness.  The replay checks

`radius^radial_gap * tail_bound < leading_margin`.

The record materializes all leading Bernstein controls and aggregated absolute
tail controls.  The replay requires a single nonzero leading sign, recomputes
the margin as the minimum absolute leading control, and recomputes the tail
bound as the maximum supplied absolute tail control.  An asserted decimal
radius or unmaterialized digest is not evidence.  Parent-residence inequalities
require the same treatment even though only residual-literal rows are counted
in the stabilization census.

## Endpoints

### `COMPLETE_ORIENTED_NORMAL_LINK_GATE`

All five main artifacts are mandatory.  Recursive strata, parent-safe link
coverage, and exact stabilization flags are true.  The complete normal-form
matrix has 3,539 literal and 70 parent rows on every stratum.  This endpoint
only retires the enumerated four-support normal-link obstruction class and
authorizes a fresh audit for a later collar target.

### `NORMAL_LINK_REDUCTION_NO_GO`

The source census and one exact obstruction artifact are mandatory.  Partial
normal-form/stratum/sector/stabilization artifacts may accompany it.  The
obstruction is one of `EXTRA_LINK_WALL`, `SINGULAR_LINK`, `MISSING_COFACE`,
`UNSTABLE_HIGHER_ORDER`, or `SOURCE_CONTRACT_CONTRADICTION`, and its consequence
is exactly `NORMAL_LINK_REDUCTION_NO_GO_ONLY`.  It does not prove a global
separator or nonseparator.

### `UNRESOLVED_NORMAL_LINK_STRATUM`

The source census and one frontier artifact are mandatory.  The frontier
names the first exact unresolved obligation, disjoint processed and pending
sets, a processed semantic digest, and an exact resume command.  Pending work
must be nonempty.

### `HASH_PINNED_NORMAL_LINK_FRONTIER`

This has the same artifact rules as the unresolved endpoint and additionally
records the reached time, memory, 10,000-polynomial, or 100,000-cell ceiling.
It is a timeout record, never mathematical evidence for another endpoint.

## Deterministic digests

Semantic streams use compact sorted-key ASCII JSON followed by newline and a
domain prefix `9dvl-d9-s1237-<artifact>-v1\0`.  The root certificate digest is
SHA-256 of `9dvl-d9-s1237-certificate-v1\0` followed by canonical JSON after
replacing its own digest with 64 zeroes.  Byte digests bind exact files;
semantic digests make harmless whitespace changes distinguishable from a
mathematical mutation.

## Hostile gates

The shipped self-test rejects missing source, literal, occurrence, and
stratum records; literal reordering; orientation flip; duplicate sector;
false stabilization; false collar; false topology; and false `3/9` ledger
consequences.  The full replay also rejects path escape, source drift,
artifact digest mismatch, duplicate source/stratum rows, incomplete 63-face
normal closure, missing parent rows, unsupported infeasibility witnesses,
dangling incidence/adjacency, and sample-only claims.

## Replay

Contract/source replay with the intentionally incomplete template:

```bash
PYTHONDONTWRITEBYTECODE=1 python \
  ops/team/diag9-s1237-normal-link-certificate/verify_normal_link_certificate.py
```

Replay after a producer materializes a payload (frontiers can be accepted by
v1; mathematical endpoints require the documented adapter/version bump):

```bash
PYTHONDONTWRITEBYTECODE=1 python \
  ops/team/diag9-s1237-normal-link-certificate/verify_normal_link_certificate.py \
  --certificate ops/team/diag9-s1237-normal-link-certificate/NORMAL_LINK_CERTIFICATE.json
```

The optional `--emit-literal-census` path must remain inside this track.  It
exists to make the independently reconstructed producer input material; it
does not create a mathematical endpoint.
