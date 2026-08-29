# Diagonal-four top-sheaf strategy cycle

Date: 2026-08-29 UTC

Canonical base revision: `d047359e7892106021022b0401554f56eb4e4d8a`

Canonical base tree: `af221cc4a3c2d81ce2c58ecb71bdf2e029b4b929`

Opening theorem ledger: `2/9`

Canonical ledger: `ai/omreal/NINE_DIAGONAL_STATUS.md`, SHA-256
`f4360254e5c7e624b9c9194bb7cb0b3844d5fe3201ec9bc688c2f18d37276782`.

Target ledger entry: `s=4`, equivalently
`H_c^3(B_S; Q)=0` for every proper pairwise-incomparable four-signature
family in the stated 9DVL domain.

## Mandatory opening strategy evaluation

Scores use `5` for favorable ledger leverage, quantifier readiness,
terminality, structural compression, independent verification, and
resource/information return.  For coverage burden and stagnation risk, `5`
is unfavorable.

| Candidate | Ledger leverage | Quantifier readiness | Coverage burden | Terminality | Structural compression | Independent verification | Resource / information | Stagnation risk | Verdict |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| diagonal 3 | 5 | 3 | 5 | 2 | 3 | 3 | 2 | 5 | `PIVOT` |
| diagonal 4 | 5 | 2 | 4 | 4 | 5 | 3 | 4 | 1 | **`MODIFY`, then `CONTINUE`** |
| diagonal 8 | 5 | 1 | 5 | 2 | 3 | 4 | 2 | 4 | `RETIRE` as primary target |
| diagonal 9 | 5 | 2 | 5 | 2 | 4 | 3 | 2 | 3 | `PIVOT` |

Opening-referee verdict: `MODIFY`, accepted at
`a112391eab4311a67a88e6aa9447f658226c65bc`, then continue.  The original
contract incorrectly treated the `1,099,560` generic cover-all five-supports
in `66` unsigned `S_8` orbits as the complete domain.  The actual cover-all
single-piece index contains `1,715,980` supports in sizes `3/4/5`, split as
`840 / 72,380 / 1,642,760`.

Selected strategy: attack the exact D4-SP constructible top-component claim,
not a larger local atlas.  The precise obstruction is a possible compact
split--remerge cycle in the component persistence of cover-all residence
fibers.  Light-label escape alone is explicitly insufficient.

## Bounded target

**D4-SP (admissible cover-all single-piece vanishing).**  For every realizable
uniform rank-four oriented matroid `M` on labeled `[8]`, every proper
pairwise-incomparable four-signature family `S` in its 9DVL domain, every
`rho in S`, and every circuit support `Q` with `1 <= |Q| <= 5` and union
`[8]`, the closed circuit piece `C_(rho,Q)`—including every zero-weight face
and every structural/residual-wall specialization inside the normalized
realization cell—satisfies `H_c^3(C_(rho,Q); Q)=0`.

A no-split--remerge statement is useful only if it proves D4-SP over these
quantifiers.  A falsification requires an exact admissible tuple
`(M,S,rho,Q)` and a checked nonzero compact-support class.  Abstract
split--remerge models remain hostile canaries rather than 9DVL
counterexamples.

The cycle stops at the first publication-grade outcome:

1. a proof of D4-SP with a small independently replayable semantic kernel;
2. an exact admissible D4-SP counterexample;
3. a finite exact classification that strictly reduces an explicitly complete
   declared D4-SP subdomain and states every excluded stratum and the next
   discriminator; or
4. the resource ceiling, accompanied by complete null/timeout manifests.

No sampled network, isolated escaping component, or unsigned support count may
be promoted to a global result.

## Obligation graph

- `diag4_fivefold_reduction`: proved / exact finite reduction.
- `diag4_omitted_label_single_piece_hc3`: proved vanishing.
- `diag4_cover_all_support_census`: finite exact; `1,715,980` complete
  cover-all supports in sizes `3/4/5`; its generic five-support subcensus has
  `1,099,560` supports in `66` unsigned symmetry orbits.
- `diag4_cover_all_single_piece_hc3` (`D4-SP`): open; selected bounded edge.
- retained two-piece `(p,q)=(1,2)` terms: open.
- retained three-piece `(p,q)=(2,1)` terms: open.
- retained four-piece `(p,q)=(3,0)` terms: open.
- adjacent total-degree terms, five-piece outgoing terms, compactification
  faces, orientation/sign transport, and alternating restriction maps: open.
- `diag4_fivefold_restriction_exactness`: open; no dependency direction that
  would make it follow from D4-SP is claimed.
- `diag4_hc3`: open; dependent on the complete total complex.
- diagonal-four ledger entry: open until every parent/family quantifier and the
  complete total-complex exactness pass independent review.

Proving D4-SP removes only the unresolved cover-all part of the single-piece
`(p,q)=(0,3)` column.  It cannot by itself promote the ledger.

## Canonical input accounting

| Input | SHA-256 |
| --- | --- |
| `ai/omreal/FOURTH_DIAGONAL_FIVEFOLD.md` | `efac03d2854221b0c8f7dabe2ff6aa3693166b3f8fbacf1bbfaa76aa4c30e2f5` |
| `ai/omreal/THREE_SHEAR_SINGLE_PIECE_REDUCTION.md` | `77dc85c047c3ee8371f1548d59b32f87ced47a5e47c65ff5d8b4b83eb1824de9` |
| `ai/omreal/verify_fourth_diagonal_reduction.py` | `d02d3bfa8994e380cfaa156b76fcc273934c3333abeac3ee3be13401bb8e2b55` |
| `ai/omreal/verify_fourth_single_piece_light_count.py` | `ca7b0128a1eb689cb5e3f6341666e90b72553ef04831a5311578a6038f010bae` |
| `ai/omreal/NINE_DIAGONAL_STATUS.md` | `f4360254e5c7e624b9c9194bb7cb0b3844d5fe3201ec9bc688c2f18d37276782` |

## Concurrency and non-overlap

The last published cycle is merged PR #41 at the canonical base.  Any
unpublished continuation of the parent-860 mask-6 discriminator is outside
this cycle and supplies no accepted input.  D4-SP owns no diagonal-eight or
diagonal-three artifact surface.  If `main` moves before integration, the
coordinator must reconcile and replay at the new exact base rather than infer
compatibility.

## Roles

- Coordinator/PI: canonical grounding, work orders, integration, ledger, and
  publication gate.
- Constructive prover: strongest signed no-split--remerge or top-sheaf
  injectivity theorem.
- Falsifier/red team: minimal exact realizable split--remerge or decisive
  obstruction search.
- Independent referee: strategy audit first; candidate replay and scope review
  only after prover/falsifier handoffs are frozen.

## Resource ceiling

Each discovery track is bounded to one agent turn and ordinary local/GitHub CI
resources.  No paid external compute or API is permitted.  Null results must
pin the searched domain, survivors, failed hypotheses, and next exact
discriminator.

## Publication authority

The full standing authorization in `ops/research-team/PROTOCOL.md` is included
verbatim in every work order and agent prompt.  Workers may commit and push
only their assigned branches; they may not merge or change the theorem ledger.
The coordinator may publish the integrated branch, open a PR, run or rerun CI,
and merge only after the exact head passes independent review and all required
checks.  Recovery checkpoints are limited to Google Drive
`Projects/research-backups`.

## Closing requirements

The coordinator report must apply the post-cycle strategy evaluation in
`ops/research-team/PROTOCOL.md`, state the exact ledger delta, and issue a new
`CONTINUE`, `PIVOT`, `RETIRE`, or `STOP` verdict before any successor cycle.
