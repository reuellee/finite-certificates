# Generic selected-edge compiler: exact phase-A frontier

Track: `cycle-20260828-certificate-generic-edges`  
Role: certificate engineer  
Base: `ec362dba8a912bc4749c004641aee2da0a88dc05`

## Outcome

The edge-27 and edge-39 root/event layer is architecturally compatible with a
single parameterized compiler.  The new generator compiled an exact phase-A
census for all 40 edges of the pinned minimum segment cover and emitted a full
proof-producing roadmap for one pending edge, edge 17 (charts 0 to 66).  It did
not materialize any 97,224-signature label bitmap.

Every selected edge passed the generator's fail-closed phase-B eligibility
gate:

- all 70 signed parent brackets are strictly positive on the oriented closed
  segment;
- there are no endpoint roots or identically-zero restricted factors;
- there are no repeated/tangential roots and no coincident distinct-factor
  events in this exact 40-edge census;
- every multi-root factor has a separate indexed root atom;
- every multi-occurrence event is marked as a compound label event;
- all event boxes are exactly ordered; and
- odd-multiplicity event toggles reconstruct the oriented target factor state.

The all-edge census contains 168,680 exact interior root atoms/event groups,
9,264 compound label events, and 5,616 multi-root-factor incidences.  Per-edge
event counts range from 1,237 to 5,872; compound counts range from 58 to 323.

## Pending-edge pilot and next batch

Edge 17 has 1,856 ordered events, 77 compound label events, 22 multi-root
factors, endpoint Hamming distance 1,812, and exact target-state replay.  Its
full 1,856-event witness list is embedded in the artifact.

The deterministic ranking key is
`(compound events, ordered events, multi-root factors, edge index)`.  Excluding
the already label-compiled edges 27 and 39, it selects:

1. edge 17, charts 0 to 66: 77 compound / 1,856 events;
2. edge 4, charts 0 to 19: 98 compound / 2,070 events;
3. edge 21, charts 0 to 74: 134 compound / 3,139 events;
4. edge 52, charts 0 to 151: 169 compound / 3,065 events.

This chart-zero batch is also the lowest-risk phase-B refactor frontier because
it preserves the source normalization convention already exercised by edges
27 and 39.  Later nonzero-source edges require dynamically solving and recording
the source reorientation mask.  The generic label compiler must additionally
parameterize profile headers/domains and make collar attachment optional; the
root/event interface itself needs no edge-specific semantics.

## Runtime and replay status

Measured generation on this host:

- edge-17 preliminary serial pilot: 80.221 seconds;
- all-40 compact census with eight workers: 1,049.698208 seconds;
- deterministic full edge-17 artifact replay during generation: 100.302448
  seconds;
- artifact size: 624 KiB.

The independent checker is separately written and imports none of the generic
generator/core.  It is designed to authenticate the compact manifest, replay
all 40 orientations/parent-residence certificates and exact endpoint nonzero
conditions, and fully replay all phase-A roots/events on edge 17.  Its first run
was intentionally interrupted after 180 seconds at the coordinator's stop
rule; it produced no PASS summary before interruption. A coordinator replay
repeated that bounded result, remaining silent through 180 seconds before
exit 130. Therefore the checker is **syntax-checked but unverified-by-run**,
and no independence/publication
gate is claimed.  Do not describe the all-edge root census or pilot as
independently accepted until this command exits successfully:

```console
PYTHONDONTWRITEBYTECODE=1 python \
  ops/team/generic-edge-compiler/verify_generic_phase_a.py
```

Regenerate the deterministic artifact with:

```console
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/diag3_pair_parent_source_generic_census.py \
  --workers 8 --batch-size 4
```

## Exact limitations

This is a finite exact generator-side phase-A result.  It does not continue
the 97,224 extension labels on edge 17 or any other pending edge, independently
replay every nonpilot root census, prove source-skeleton or parent-cell
coverage, classify wall components, close a diagonal-three obligation, or
change the honest 9DVL score from 2/9.

Artifact byte SHA-256:
`b9c7c67908bae7e98766ca3212f9d6f4e85e9f90d65447940302e8fb73d7b63c`.
Artifact semantic SHA-256:
`d130963882a18146d489e644fda4c2793657731266037d344b53daef2a7f0c87`.
