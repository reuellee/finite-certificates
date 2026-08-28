# Constructive prover handoff: exact edge-39 residual roadmap

Track: `cycle-20260827-prover-edge39`
Base: `e8600495e70e6f5548cb0c73e0cfd2f33faacc0b`

## Exact bounded theorem

Let `p0` and `p113` be stored charts 0 and 113 in the pinned exact row-2599
point bank, and let `x(s)=p0+s(p113-p0)` for `0 <= s <= 1`.  Retained source
edge 39 is exactly this segment.  For the exactly 17,824 candidate full-support
residual factor classes in the pinned candidate list:

1. every one of the 70 target-signed parent factors is strictly nonzero with
   the target sign on the entire closed segment;
2. no residual restriction is identically zero, has an endpoint root, or has
   a repeated root;
3. 12,615 factors have no root in `(0,1)`, 5,091 have one, and 118 have two;
4. the resulting 5,327 roots admit pairwise disjoint, globally ordered exact
   rational isolating intervals of width at most `2^-48`;
5. all events are simple sign crossings.  No two different candidate factors
   have coincident segment roots, so every exact event group is a singleton;
6. toggling the factor state at the ordered events reconstructs the pinned
   chart-113 state exactly from chart 0.  The endpoint Hamming distance is
   5,091, as independently implied by the 5,091 one-root and 118 two-root
   factors;
7. every singleton event stores its exact global occurrence multiplicity.
   The 5,327-event multiplicity census is `1:5034, 2:71, 15:43, 65:179`;
8. factor 19069 is event 5,236 (zero based), has degree 6 and occurrence
   multiplicity 1, and its restricted primitive polynomial is byte-for-byte
   the same primitive polynomial used for the accepted collar's central
   `q=0` incidence.  Its roadmap and collar isolating intervals overlap.

The exact factor degree census is
`1:10, 2:599, 3:4198, 4:8258, 5:4286, 6:473`.

## Replay

From the repository root:

```console
PYTHONDONTWRITEBYTECODE=1 python \
  ops/team/edge39-prover/prototype_edge39_roadmap.py --verify
```

The successful discovery/replay run printed:

```text
PASS edge 39 exact full-factor roadmap prototype
PASS root census {'0': 12615, '1': 5091, '2': 118}
PASS ordered events 5327
PASS occurrence census {'1': 5034, '2': 71, '15': 43, '65': 179}
PASS factor 19069 collar event 5236
PASS canaries 5 / 5
SEMANTIC_SHA256 7c85936e4eb3d77001402089eb107f898b46710c586b0dd97bef06d191b28d5b
```

Artifact digests:

```text
65ec954da2ba2f37ed009d42d27916ae99ae7e1e640bccb847f6a1370d05d333  prototype_edge39_roadmap.py
cd4cc32efc2d71a609a01b2747e5d6230b7115a7ee23423b6a3175a71a1cf6c1  EDGE39_EXACT_ROADMAP.json
```

The JSON is 1,605,699 bytes.  Its complete ordered event list has semantic
digest `8fe2bee966b542a3b8af1205883cf6d92ee8261e7b10f716a07a8e56c96b63b5`;
the complete restricted-polynomial stream has digest
`95851166cab3822382ca09fe78ce72f27312f4b51763e6b32c64d3b5f3b00d0c`;
and the ordered factor-state sequence has digest
`6690dc794de0f819de9e2e8730c48e1806c1cd59891f16029c2cf1ada4302f9e`.

## Canary results

The same replay rejects or detects all work-order canaries:

- reversing one signed parent factor fails the parent-residence gate;
- a synthetic endpoint root is detected rather than passed to open-interval
  Sturm isolation;
- a synthetic doubled root is detected by exact polynomial GCD and its lack
  of endpoint sign change;
- two synthetic factor restrictions with a common root are detected by exact
  polynomial GCD;
- changing the collar target from factor 19069 to an invented factor 19070 is
  rejected before incidence attachment.

## Scope and defects

This proves only the exact one-dimensional roadmap for edge index 39 and the
17,824 pinned candidate factors.  It does not continue the 97,224 extension
signature labels across the events, prove parent-cell coverage, control wall
components outside the accepted collar, establish pair injectivity, address
the triple obligation, or advance 9DVL beyond 2/9.

The prototype reuses accepted discovery-side polynomial and exact-arithmetic
helpers.  It is therefore positive constructive evidence awaiting the
certificate and independent-verifier tracks, not by itself a publication
gate.  Recommended canonical-ledger change: none.
