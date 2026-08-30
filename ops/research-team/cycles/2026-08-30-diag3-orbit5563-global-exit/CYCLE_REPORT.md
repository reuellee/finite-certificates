# Diagonal-three orbit-5563 global-exit cycle report

Date: 2026-08-30 UTC

Canonical base: `aa784af939b55d3503e4782a9d65a9b06cf81ce0`, tree
`6aa36a92c5e5d2e420ec660a1ad2c2be2b06a561`. Opening theorem ledger:
`2/9`.

## Strategy and outcome

The per-cycle strategy gate retired another D4-S53 continuation and the
unready D4-total-complex and D9 routes. It authorized one bounded D3 cycle for
the complete `S_8` orbit of canonical unresolved row
`(5563,4373,23221)`, authenticated by presentation
`(5563,16134,19284)`.

The independent prover and falsifier both passed the exact quotient-manifest
layer and stopped at the same first missing full-space obligation. The closing
referee independently reconstructed the quotient and accepted the handoffs as
**`ACCEPT_TERMINAL_NULL_WITH_MANDATORY_PIVOT`**. No local topology computation
was authorized or started.

This is exact domain compression, not theorem progress. The unresolved-row
count remains `1,162,302`, the theorem ledger remains `2/9`, and no compact
component or global-exit certificate was established.

## Frozen handoffs

| Track | Local revision | Published revision | Identical tree | Classification |
| --- | --- | --- | --- | --- |
| prover | `7b22899b556cd4c8135f324a82be069d238fdd20` | `dd4394c3a6131bfeb9b3d1c1adede830b1941535` | `e5aa65680f388a7a3aaab522d264227c45a532b4` | terminal `null` |
| falsifier | `8be3fdddd7b2266db13cdbfcbea409f728b72559` | `e5bc85923ab0694482219399e626d0d2255bc926` | `0ae7191d74f3a77d343673a5f51b9a2bf22d596f` | terminal `null` |
| closing referee | `67213be260363948c675bb4a718c3e23cbdd5ad6` | `409c29a898f0cb8ec7ee64ee3afecf21d222ee20` | `5eee4008f2527d096d34677505d1fb37f7b8194d` | accepted null; mandatory pivot |

The integrated worker candidate is local
`d4e5a228e5ae5472a838672b54ca074ee0738c25`, published
`af098d1297dd5c82f194d1f4d03a9ac75afafba9`, with identical tree
`dcd0e683a33468194f38353a72ebc84c213b0b35`.

## Exact quotient result

The raw parent/frame domain is

```text
2,604 realizable unlabelled parent types × 40,320 frames
= 104,993,280 raw presentations.
```

After the exact parent-automorphism and hard-triple diagonal action, the
domain has `100,086,840` quotient classes. The class multiplicities sum
exactly to `104,993,280`. The hard-triple stabilizer is the identity and its
orbit has size `40,320`.

| Parent automorphism order | Parent types | Quotient classes of that multiplicity |
| ---: | ---: | ---: |
| 1 | 2,382 | 96,042,240 |
| 2 | 183 | 3,689,280 |
| 3 | 10 | 134,400 |
| 4 | 16 | 161,280 |
| 6 | 3 | 20,160 |
| 8 | 6 | 30,240 |
| 12 | 1 | 3,360 |
| 16 | 1 | 2,520 |
| 24 | 2 | 3,360 |

The closing referee's third implementation agreed with both worker manifests
on all `2,604 / 2,604` parent rows and every automorphism element. Seven
independently resealed hostile mutations were rejected.

## Transport boundary and missing object

Exact sign, Cramer-chart, and primitive-factor relabelling transport holds for
every interior point and framed quotient class. It does not imply closure,
rank-drop, component, attachment, or true-infinity coverage.

The smallest missing obligation is
`Q3_COMPLETE_PARENT_BOUNDARY_ATLAS`: a complete normalized compactification
and closure-stratum atlas over every parent quotient class, with exact chart
transition domains and exhaustive attachments. Until that object exists, the
component partition, rank-drop attachments, true-parent-infinity tags,
global-exit graph, and compact-component test remain blocked.

Representative matrices remain sign witnesses only; they are not finite
coverage of a complete realization space.

## Gate table

| Gate | Result |
| --- | --- |
| signed opening review | `GO` |
| exact quotient manifest | `PASS` |
| quotient multiplicity sum | `PASS_104993280` |
| independent worker agreement | `PASS_2604_OF_2604` |
| all-interior-point transport | `PASS` |
| complete closure-stratum transport | `MISSING_FAIL_CLOSED` |
| topology computation | `NOT_AUTHORIZED_NOT_RUN` |
| exact row removal | `NONE` |
| exact compact component | `NONE` |
| theorem ledger change | `NONE` |
| closing referee | `ACCEPT_TERMINAL_NULL_WITH_MANDATORY_PIVOT` |
| protected CI at final PR head | `PENDING_PUBLICATION_STAGE` |
| exact-head merge | `PENDING_PUBLICATION_STAGE` |

## Post-cycle strategy evaluation

This route met its information-return target by replacing an ambiguous raw
census with a complete exact quotient and by isolating the first missing
global object. It did not meet either terminal topology endpoint. The frozen
stagnation rule therefore applies:

- **`PIVOT`** to a newly bounded target;
- **`RETIRE`** further local roadmap, box, collar, macrobox, clipped-wall, or
  similar continuation for this residue; and
- **`STOP`** any successor whose complete quantifier domain or publication
  gate is unavailable.

A new cycle must repeat the eight-factor strategy evaluation before work is
authorized. This report does not select or authorize that next target.

## Publication and recovery manifest

- publication branch: `research/diag3-orbit5563-global-exit-20260830`
- signed opening published revision: `9e578f6e9d094b3342ca474f0d188428dd44ae7a`
- reviewed integrated revision: `af098d1297dd5c82f194d1f4d03a9ac75afafba9`
- closing-referee published revision: `409c29a898f0cb8ec7ee64ee3afecf21d222ee20`
- pull request, final-head CI, and merge revision: `PENDING_PUBLICATION_STAGE`
- Google Drive integrated-handoffs bundle:
  `1HCt6CmjPWHc0cAYq2F_Gj5j7FFCR3tcN`, `58,797,131` bytes, SHA-256
  `afb0af82f010019c73500bc26d8ffa4a3fbbd04ae829c8e2980cec2bb36dcdeb`
- recovery manifest: `1TEpS3E0Gr1wqfdQSfMeOUjfncHca0PAY`
- ledger promotion: `NONE`
