# Universal D9 feasible-component cut certificate v1

## Acceptance boundary

The root format is `9dvl-d9-universal-cut-coverage-certificate-v1`, schema
version `1`, for target `D9_UNIVERSAL_FEASIBLE_COMPONENT_CUT_GATE1`.  It binds
the cycle opening commit `6cbd1b4a7d3ed61bee268b6b54cbfadeece90f0e`
and tree `84eaf80b30e1f366b8f959bd6435a217762636b3`, separately from
the canonical input commit `cbe84ccd7273252c81fd4da17ee360a284d2a2a6`
and tree `da3cd6feca1052ea14ed5036413c72b8f7fadc2a`.

Version 1 is endpoint-neutral and fail-closed.  It validates the exact shape
and arithmetic obligations for the positive, negative, null, and timeout
endpoints, but registers no live mathematical adapter.  The four records in
`SELF_TEST_FIXTURE.json` use the fixture-only adapter
`SELF_TEST_EXACT_D9_CUT_ADAPTER` and cannot be presented as live evidence.
Any real mathematical endpoint therefore needs a successor schema version
that names and independently replays its exact coverage adapter.  A digest,
producer verdict, sampled graph, or prose proof is never such an adapter.

The certificate engineer does not mutate the theorem ledger.  Even a checked
positive or negative endpoint keeps `ledger_before` and `ledger_after` equal
to `2/9` and only recommends a coordinator action after independent replay.

## Universal quantifiers

Every record carries these exact strings:

- `parents`: every realizable `UOM(4,8)` parent;
- `families`: every proper pairwise-incomparable nine-family;
- `active_literals`: every consistent active-literal assignment;
- `cuts`: every pair of distinct feasible active-sector components;
- `ends`: all charts, multiplicities, multiwalls, recursive strata, and
  genuine infinity.

Changing or weakening one quantifier rejects the record.  A fixed family,
local collar, sampled graph, or single normal link cannot satisfy this field.

## Obstruction grammar and exact coverage

`grammar.atoms` is a unique, lexically ordered registry with at most 10,000
types.  Its atom kinds must collectively include:

1. `RESIDUAL_WALL_TYPE`, with the separate count of 13 pinned;
2. `SUPPORT_MINIMAL_GORDAN_CIRCUIT`;
3. `SIGNED_MULTIWALL_INCIDENCE`;
4. `RECURSIVE_BOUNDARY_STRATUM`;
5. `GENUINE_INFINITY_END`.

Each atom has exactly `id`, `kind`, and `source_ref`.  The exact partition
`covered_atom_ids` / `pending_atom_ids` must be disjoint, duplicate-free,
sorted, and exhaustive.  At most 250,000 exact instances may be claimed.

`preserved_structure` is fixed to sign, duplicate occurrence, chart,
properness, multiwall incidence, recursive facet, and genuine infinity.
These fields are obligations, not booleans that a producer may assert.  A
live adapter must reconstruct their preimages and replay the coverage proof.

### Boundary residence and attachment

`grammar.boundary_contract` is exact and immutable:

- residence must be either strict parent residence or a named boundary
  stratum;
- attachment must be an exact coface witness or an explicit unresolved
  attachment;
- a recursive-facet wall is boundary-only by default and is not a global
  separator;
- strict coface residence requires a separate exact witness.

This gate encodes the exact boundary-track null result: the factor-8552 lifts
remain on `[1237]=0`; the ordinary strict-parent link is empty; and no strict
coface is certified.  The predecessor witness remains a hostile canary, never
a global separator.  The hostile harness mutates this default to
`GLOBAL_SEPARATOR` and requires rejection.

## Root fields

The root object has exactly:

`format`, `schema_version`, `target_id`, `mode`, `source_binding`,
`quantifiers`, `grammar`, `coverage`, `endpoint`, `evidence`, `scope`,
`prohibited_consequences`, and `semantic_sha256`.

`mode` is `SELF_TEST` or `LIVE`.  Self-test mode is accepted only through the
verifier's explicit fixture path.  Live mode requires the byte SHA-256 of
`SOURCE_MANIFEST.json` and a registered independent adapter.

`coverage` has exactly `status`, `adapter`, and `proof_object_sha256`.
The adapter has an ID, positive integer version, status, and evidence digest.
Positive and negative records require `COMPLETE`; null requires `GAP`; timeout
requires `PARTIAL`.

All JSON field sets are exact.  SHA-256 values are lower-case 64-character
hex strings.  Rationals are reduced strings accepted by `fractions.Fraction`.
The root semantic digest is SHA-256 of the domain
`9dvl-d9-universal-cut-certificate-v1\0` followed by compact sorted-key ASCII
JSON after replacing `semantic_sha256` with 64 zeroes.

## Exact endpoints

### Positive: `UNIVERSAL_D9_CUT_OBSTRUCTIONS_UNSAT`

Coverage is complete, every atom is covered, and the endpoint adapter proves
the universal reduction.  `evidence.instances` contains at most 250,000 exact
linear obstruction records.  Every record materializes its linear forms and
strictly positive Gordan multipliers; the verifier recomputes that their
weighted coefficient sum is exactly zero.  The theorem and obstruction
registry have separate semantic digests.

The endpoint consequence is diagonal nine proved, pending coordinator
integration.  It does not itself change `2/9`.

### Negative: `EXACT_D9_TWO_COMPONENT_SEPARATOR`

Coverage is complete.  The record identifies one exact parent and admissible
nine-family, materializes every strict active constraint, and supplies two
exact rational feasible points with distinct component labels.  It also
materializes a coverage-certified separator polynomial.  The verifier
evaluates all active constraints at both points and requires strictly opposite
separator signs.

The endpoint consequence is an exact diagonal-nine counterexample, pending
coordinator integration.  A recursive-boundary wall without strict residence
cannot fill the separator field.

### Null: `UNIVERSAL_CUT_SCHEMA_COVERAGE_GAP`

Coverage is `GAP` and pending atoms are nonempty.  The record names the first
uncovered atom and exactly one mode among cut, multiwall, transport, recursive
facet, or infinity.  It includes an exact witness digest, a complete sorted
survivor manifest, the next discriminating experiment, and a tokenized resume
command.  Diagonal nine and the ledger remain open.

### Timeout: `HASH_PINNED_D9_CUT_SCHEMA_FRONTIER`

Coverage is `PARTIAL` and pending atoms are nonempty.  The evidence repeats
the exact processed/pending partition, binds a checkpoint, and records a
reached ceiling: 12 wall-hours, 64 CPU-hours, 16 GiB, 10,000 obstruction
types, or 250,000 exact instances.  `observed` must meet or exceed the exact
limit.  A timeout is not mathematical evidence for another endpoint.

## Prohibited consequences

Every endpoint preserves the exact rejection list:

- local coorientation implies global connectivity;
- all-strata gluing implies global connectivity;
- a recursive-facet wall is a strict open-parent separator;
- fixed-family connectivity proves diagonal nine;
- a sampled graph is global coverage;
- the certificate engineer mutates the theorem ledger.

## Portable predecessor replay

The immutable V3 state records historical referee identifier
`ca730426cdd5847ae262ddc29c6f4ae98369eba3` and tree
`56fe7f95a4e20dea581736cb5539abb502e05a63`.  The commit object is absent.
`PORTABLE_PREDECESSOR_ADAPTER.json` records that fact without claiming the
object exists and forbids dereferencing it.

The successor adapter instead authenticates the V3 bytes and replays the
reviewed mathematical head `5efbd07a25b818306f9fd22597fd81a0f2091309`
through the SHA-pinned independent referee kernel.  It calls only the
source-manifest, census, exact-geometry, certificate-boundary, closing, and
hostile entrypoints.  It does not call the referee's mutable `main` wrapper,
the repository-wide cycle audit, the V3 verifier, or producer acceptance
logic.  The reconstructed endpoint remains the finite-exact local
`NORMAL_LINK_REDUCTION_NO_GO`; weighted links, strict open-parent crossing,
universal cut coverage, diagonal nine, and ledger promotion remain open.

## Replay

Contract, fixture, and fail-closed live-adapter gate:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 python \
  ops/team/d9-universal-cut-certificate/verify_universal_cut_certificate.py
```

Hostile mutations:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 python \
  ops/team/d9-universal-cut-certificate/run_hostile_mutations.py
```

Fast portable binding check and full source-derived predecessor replay:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 python \
  ops/team/d9-universal-cut-certificate/verify_portable_predecessor.py --manifest-only

PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 python \
  ops/team/d9-universal-cut-certificate/verify_portable_predecessor.py
```
