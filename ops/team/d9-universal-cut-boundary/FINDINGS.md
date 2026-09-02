# Universal D9 cut: boundary and transport opening result

## Outcome

The universal boundary/transport gate stops at an exact null endpoint:
`UNIVERSAL_CUT_SCHEMA_COVERAGE_GAP`.

The smallest load-bearing lemma is elementary but decisive.

> **Strict-parent separator gate.** Let `X` be the strict normalized parent,
> let `Xbar` be a compactification, and put `B = Xbar \\ X`. If a candidate
> wall `W` is contained in `B`, then `W` is disjoint from `X` and
> `X \\ W = X`. In particular, for every active sector `H` contained in `X`,
> `H \\ W = H`. A wall in a recursive boundary facet is therefore not a
> separator of the strict parent or of its active sector. It can enter a
> separator certificate only after an exact incident coface in `X` has been
> supplied, with chart, orientation, occurrence, and incidence transport.

The proof is the displayed set identity. No smoothness, transversality, or
genericity assumption can replace the missing strict coface.

The pinned row-2599 data supplies an exact hostile instance. Active factor
`8552` for the proper `S12,37` family is `q=d*i-e`, has allowed side `q<0`,
has one labeled occurrence, and has no stripped parent unit. On support
`(3,1,15)`, three rational normal directions give negative, zero, and positive
values of the lowest form `d/4-e`. Their exact lifts likewise give negative,
zero, and positive values of `q`; the zero lift imposes `e=d*i` exactly.

However, every lift keeps `f=0`, equivalently `[1237]=0`. The 64-chart
`(Delta^3)^3` compactification identifies this coordinate divisor exactly
with the genuine parent divisor `[1237]=0`. All 69 other oriented parent
brackets are positive. Thus the data is a residual/parent multiwall inside a
recursive genuine-infinity facet, not a strict-parent crossing.

The missing attachment cannot be supplied by an ordinary common-radial
perturbation. At the same support the parent initial forms `+n4` and `-n4`
have positive Gordan weights `(1,1)`, so the ordinary strict parent link is
empty and the approach is forced into `n4=0`. A valid successor must use a
weighted blow-up and prove an incident coface with `[1237]>0`; none is present
in the canonical inputs.

## Boundary and transport registry

| Obligation | Exact status | Evidence / boundary |
|---|---|---|
| strict parent residence | **fails for the candidate transport** | all three exact lifts have `[1237]=0`; 69 other brackets are positive |
| active orientation | checked for the hostile instance | factor `8552`, family side `d*i-e<0` |
| duplicate occurrence / multiplicity | checked for the hostile instance | one occurrence `(4,9,23,37)`, multiplicity `1`, no stripped unit |
| charts | checked for row 2599 only | pinned 64-chart product-simplex atlas; `[1237]` is column 7, row 4 |
| singular incidence | checked for the hostile instance | opposite parent initial forms make the common-radial strict link empty |
| residual/parent multiwall | checked for the hostile instance | the two-sided `q=0` wall lies in `[1237]=0` |
| recursive facet | checked and kept recursive | the witness is never promoted to an open-parent/global separator |
| genuine infinity | checked for row 2599 | `[1237]=0` is a genuine compactification divisor, not a box boundary |
| every realizable parent and nine-family | **unchecked** | no all-parent/family boundary registry or transport theorem exists in the pinned inputs |
| weighted strict coface attachment | **first unresolved attachment** | requires higher weighted orders and a lift with `[1237]>0` |

## Exact disposition

This result refutes only the transport rule
`RECURSIVE_FACET_WALL_IMPLIES_STRICT_OPEN_PARENT_SEPARATOR`. It does not
refute the abstract existence of a richer finite obstruction schema that
stores exact coface attachments. Because that richer schema and its universal
coverage proof are absent, the opening gate fails closed before the main
obstruction census. The theorem ledger remains `2/9`.

The exact counterexample data is in
`BOUNDARY_TRANSPORT_COUNTEREXAMPLE.json`. Replay with:

```console
PYTHONDONTWRITEBYTECODE=1 python ops/team/d9-universal-cut-boundary/verify_boundary_transport_gate.py
```

The replay hash-pins the cycle and canonical inputs, verifies the row-2599
compactification divisor, recomputes the displayed rational factor values,
replays both predecessor normal-link certificates without the unavailable
historical referee object, and rejects hostile mutations including any claim
of strict-parent or global separation.

## Useful null and next discriminator

The smallest next discriminating experiment is a weighted blow-up at support
`(3,1,15)` retaining the higher orders of parent brackets `1237` and `1367`
and factor `8552`. It must either:

1. produce an exact arc with all 70 parent brackets strictly positive and
   transport the oriented occurrence `q<0` through a named atlas coface; or
2. prove that no such strict coface exists.

Until one of those endpoints is checked, the recursive-facet wall is a
relative end only.
