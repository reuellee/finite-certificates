# Diagonal-four 53-survivor top-sheaf cycle

Date: 2026-08-30 UTC

Canonical base revision: `aa784af939b55d3503e4782a9d65a9b06cf81ce0`

Canonical base tree: `6aa36a92c5e5d2e420ec660a1ad2c2be2b06a561`

Opening theorem ledger: `2/9`

Canonical ledger: `ai/omreal/NINE_DIAGONAL_STATUS.md`, SHA-256
`f4360254e5c7e624b9c9194bb7cb0b3844d5fe3201ec9bc688c2f18d37276782`.

Predecessor publication: merged PR #42 at
`aa784af939b55d3503e4782a9d65a9b06cf81ce0`.  Its accepted B31 theorem
certifies `915,740` of the complete `1,715,980` cover-all supports and `77` of
`130` unsigned `S_8` support-shape orbits.  The exact unresolved class is
`800,240` supports in `53` orbits: `4` size-four and `49` size-five orbits.

## Mandatory opening strategy evaluation

Scores use `5` for favorable ledger leverage, quantifier readiness,
terminality, structural compression, independent verification, and resource /
information return.  For coverage burden and stagnation risk, `5` is
unfavorable.

| Candidate | Ledger leverage | Quantifier readiness | Coverage burden | Terminality | Structural compression | Independent verification | Resource / information | Stagnation risk | Verdict |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| diagonal 4: signed topology on all 53 B31-resistant orbits | 5 | 3 | 3 | 5 | 4 | 3 | 4 | 2 | **`CONTINUE` once** |
| diagonal 3 | 5 | 3 | 5 | 2 | 3 | 3 | 2 | 5 | `PIVOT` reserve |
| diagonal 8 | 5 | 1 | 5 | 2 | 3 | 4 | 2 | 4 | `RETIRE` as primary target |
| diagonal 9 | 5 | 2 | 5 | 2 | 4 | 3 | 2 | 3 | `PIVOT` reserve |

Opening verdict: **`CONTINUE` diagonal four exactly once**.  The predecessor
cycle strictly reduced a complete declared D4-SP domain, so the protocol's
stagnation pivot did not fire.  This successor is different because it is
restricted to the exact B31-resistant class and requires actual signed
topology or an admissible counterexample; another unsigned support statistic
cannot count as progress.  If the complete 53-orbit class is unchanged at
closing, `PIVOT` is mandatory.

## Bounded target

**D4-S53 (signed vanishing on the complete B31-resistant survivor class).**
For every realizable uniform rank-four oriented matroid `M` on labeled `[8]`,
every proper pairwise-incomparable four-signature family `S` in its 9DVL
domain, every `rho in S`, and every cover-all circuit support `Q` whose
unsigned `S_8` support-shape orbit is one of the canonical `53` B31-resistant
representatives with semantic digest
`16b11cba052b49af777354f256a783b419ec6e246d178de70c238807e50ecc11`,
the entire closed circuit piece `C_(rho,Q)`—including zero-weight faces and
all structural/residual-wall specializations inside the normalized
realization cell—satisfies `H_c^3(C_(rho,Q);Q)=0`.

The accepted B31 theorem plus D4-S53 would prove D4-SP, the complete
single-piece `(p,q)=(0,3)` vanishing.  D4-SP still would not by itself prove
diagonal four or change the theorem ledger because the retained multi-piece,
adjacent-degree, compactification, sign-transport, and restriction-map
obligations remain open.

A positive global outcome is a proof of D4-S53 with a small replayable
semantic kernel.  A publishable intermediate outcome must strictly reduce an
explicitly complete subset of the 53 orbits by a universal signed theorem and
list every survivor.  A refutation requires an exact admissible tuple
`(M,S,rho,Q)` and a checked nonzero compact-support class that survives
inclusion into the entire closed `C_(rho,Q)`.  A class on a pinned subset,
abstract split--remerge model, sampled chart, or further unsigned census is a
discriminator only.

The cycle stops at the first publication-grade outcome:

1. a proof of D4-S53;
2. an exact admissible D4-S53 counterexample with the full-piece inclusion
   gate;
3. a universal signed theorem that strictly reduces a completely enumerated
   nonempty subset of the 53 survivor orbits; or
4. the resource ceiling, with complete null/timeout manifests and the exact
   unchanged survivor class.

## Obligation graph

- `diag4_fivefold_reduction`: proved / exact finite reduction.
- `diag4_omitted_label_single_piece_hc3`: proved vanishing.
- `diag4_cover_all_support_census`: finite exact; `1,715,980` supports in
  `130` unsigned support-shape orbits.
- `diag4_B31_four_shear_hc_le3`: proved over `915,740` supports in `77`
  orbits, including closed faces and signed/boundary transport stated in the
  accepted theorem.
- `diag4_s53_support_partition`: finite exact; `800,240` supports in `53`
  B31-resistant orbits, semantic digest pinned above.
- `diag4_s53_top_sheaf_hc3` (`D4-S53`): open; selected edge.
- `diag4_cover_all_single_piece_hc3` (`D4-SP`): open; reduces to D4-S53 only
  because the B31 partition is complete.
- retained two-piece `(p,q)=(1,2)`, three-piece `(2,1)`, and four-piece
  `(3,0)` terms: open.
- adjacent total-degree terms, five-piece outgoing terms, compactification
  faces, orientation/sign transport, and alternating restriction maps: open.
- `diag4_fivefold_restriction_exactness`, `diag4_hc3`, and the diagonal-four
  theorem-ledger entry: open.

## Canonical input accounting

| Input | SHA-256 |
| --- | --- |
| `ai/omreal/NINE_DIAGONAL_STATUS.md` | `f4360254e5c7e624b9c9194bb7cb0b3844d5fe3201ec9bc688c2f18d37276782` |
| `ops/research-team/PROTOCOL.md` | `7b3fe051677d31748d483de006d9cfc97d26518f5103016371ed7ccee469654c` |
| `ops/team/diag4-top-sheaf-prover/PROOF.md` | `9bef2f9e1c4fc2862080ebd83805f488001cb9d3eface0b0fb21bfc838006157` |
| `ops/team/diag4-top-sheaf-prover/RESULT.yaml` | `9dec592379ff05e8210236e2db4d7a56c7808c9154fee8e5a2491ff466e3e7df` |
| `ops/team/diag4-top-sheaf-prover/verify_four_block_line_sieve.py` | `84a717a3df6ca9eabbee3d3645ecb5ffbb78932b34cb54969b97fab9d4015e48` |
| `ops/team/diag4-top-sheaf-falsifier/FINDINGS.md` | `8b31c0455c7336b135370023ae71a0ed55a9551cd38512fcc387941bf7db26af` |
| `ops/team/diag4-top-sheaf-falsifier/RESULT.yaml` | `30867673476264823d2f49449c03015f5a0015c350e2cb45fb1828efe8f9631b` |
| `ops/team/diag4-top-sheaf-falsifier/verify_diag4_top_sheaf_falsifier.py` | `028566e3005ad3c822ddd7fb12821f849cf4683ad9277a359eb2a4e8036ec51b` |
| `ai/omreal/data/seeat_parent2599_shatter8.npz` | `d01a03e3222de5b760fd7fec36c03ccbeac820ed1ce7ea47f93001abaf3aadcb` |

## Concurrency and non-overlap

PR #42 is merged at the canonical base and supplies the only accepted input
from the predecessor cycle.  Its old worker branches are frozen and are not
live inputs.  No other accepted or unpublished cycle owns the D4-S53 artifact
surfaces.  A moved `main`, altered semantic digest, or changed theorem ledger
is a stop-and-reconcile condition before integration.

## Roles

- Coordinator/PI: canonical grounding, target lock, work orders, integration,
  ledger, publication, and recovery checkpoint.
- Constructive prover: universal signed theorem or exact strict reduction over
  the 53-orbit class.
- Falsifier/red team: exact admissible counterexample route, beginning with
  the pinned row-2599 full-piece inclusion discriminator.
- Independent referee: opening strategy audit, then clean candidate replay and
  scope/nonconsequence review after handoffs freeze.

## Resource ceiling

Each discovery track is bounded to one agent turn and at most 90 minutes of
ordinary local compute.  No paid external compute or paid API is permitted.
Null and timeout results must pin the exact searched signed domain, unchanged
survivors, failed hypotheses, and next discriminator.  Broad certificate
sweeps, raw review dumps, and new unsigned-only censuses are outside scope.

## Publication authority

The standing authorization in `ops/research-team/PROTOCOL.md` is copied
verbatim into every work order and every agent prompt.  Workers may commit and
publish only their assigned branches; they may not merge or change the theorem
ledger.  The coordinator may publish the integrated branch, open a PR, run or
rerun CI, and merge only after all required checks pass at the exact
independently reviewed head.  Durable recovery checkpoints are restricted to
Google Drive `Projects/research-backups`.

## Closing requirements

The coordinator report must apply the mandatory post-cycle strategy
evaluation, state the exact ledger and complete 53-orbit delta, classify every
handoff, and issue `CONTINUE`, `PIVOT`, `RETIRE`, or `STOP`.  If D4-S53 is not
proved or refuted and the complete survivor class is not strictly reduced,
the verdict is a mandatory `PIVOT`; no third consecutive D4-S53 cycle may be
started.

## Closing strategy evaluation

The independently replayed prover and falsifier handoffs are complete nulls at
their declared scopes. The complete B31-resistant class is unchanged at
`800,240` labeled supports in `53` unsigned support-shape orbits, split as four
size-four and forty-nine size-five orbits. D4-S53 and D4-SP remain open. The
theorem ledger remains `2/9`.

| Candidate next route | Ledger leverage | Quantifier readiness | Coverage burden | Terminality | Structural compression | Independent verification | Resource / information | Stagnation risk | Verdict |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| diagonal 3: one complete residue-orbit global-exit certificate | 2 | 3 | 5 | 5 | 4 | 4 | 4 | 3 | **`PIVOT` candidate, subject to a new opening audit** |
| diagonal 4: complete alternating total complex | 5 | 1 | 5 | 5 | 5 | 2 | 1 | 4 | `RETIRE` until the global restriction object exists |
| diagonal 8: training-network transport | 2 | 1 | 5 | 2 | 3 | 4 | 2 | 4 | `RETIRE` as the next target |
| diagonal 9: parent-860 active-sector roadmap | 2 | 1 | 5 | 1 | 4 | 3 | 1 | 5 | `RETIRE` until a proper nine-family is registered |

Post-cycle verdict: mandatory **`PIVOT` away from D4-S53**. No further
D4-S53, inner-cube, or unsigned survivor-census cycle may `CONTINUE`. The D3
global-exit candidate is not authorized by this close alone; it requires its
own canonical grounding, bounded work orders, and independent opening referee.
An incomplete global-quantifier gate is `STOP`/fail-closed, not progress.
