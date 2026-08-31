# D8 mask-6 counterexample-guided discriminator cycle

Date: 2026-08-31 UTC

Canonical base revision: `6c7f52b43632072100b67e5f0a9b6221df14d620`

Canonical base tree: `60866cb78e8aea3259cf376a4420e5370ab8c010`

Opening theorem ledger: `2/9`

## Mandatory opening strategy evaluation

Three independent roles compared the live D8, D3, and D9 routes after the
post-PR45 reconciliation. Scores use 5 as favorable except coverage burden
and stagnation risk, where 5 is unfavorable.

| Candidate | Ledger leverage | Quantifier readiness | Coverage burden | Terminality | Structural compression | Independent verification | Resource / information | Stagnation risk | Verdict |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| D8 parent-860 mask-6 discriminator | 3 | 4 | 3 | 5 | 4 | 5 | 5 | 2 | **`CONTINUE` one bounded discriminator** |
| D9 active-sector master graph | 4 | 3 | 5 | 3 | 5 | 3 | 3 | 4 | `STOP` for this cycle |
| D3 `Q3_COMPLETE_PARENT_BOUNDARY_ATLAS` | 5 | 2 | 5 | 2 | 2 | 2 | 1 | 5 | `PIVOT` away for this cycle |

The selected transfer comes from counterexample-guided abstraction refinement
in model checking: regard the graph loop as a potentially spurious abstract
counterexample and refine one fixed rational disk only where exact parent or
residual predicates fail. This adapts the CEGAR architecture of
[Clarke--Grumberg--Jha--Lu--Veith](https://link.springer.com/chapter/10.1007/10722167_15),
not an imported theorem. The acceptance kernel remains exact semialgebraic
geometry and a rational singular-chain boundary.

## Bounded target `D8_M6_CEGAR1`

Lock parent 860 and the loop

```text
4-11-12-14-13-23-4.
```

The nonvacuity gate must first exhibit eight loop-common extension regions
which are globally nonempty, proper, and pairwise incomparable using exact
strict-feasibility and Gordan witnesses. Only then may one deterministic
rational fan be tested.

The fixed-chain gate is the barycentric fan from the six loop vertices. It
must certify all 70 parent brackets and all 26,740 primitive residual factors,
resolve every active wall and node on the parameter disk, attach labels by the
accepted all-strata theorem, and verify that the six radial edges cancel.

Positive endpoint: an exact singular two-chain in the selected `F_S` whose
boundary is the loop. Negative endpoint: an exact parent-boundary crossing
invalidating this fixed fan, or a non-boundary cocycle only in a genuinely
complete relative complex. Null endpoint: failure of nonvacuity or an
unresolved wall/node. Timeout preserves the exact frontier. No endpoint in
this cycle may promote diagonal eight.

## Obligation graph

- `diag8_mask6_nonvacuity`: **finite-exact target**; certify one loop-common
  eight-family is globally nonempty, proper, and pairwise incomparable.
- `diag8_mask6_fixed_fan`: **finite-exact target**, conditional on nonvacuity;
  classify all parent and residual predicates on one rational six-triangle
  disk and reconstruct its complete labelled boundary.
- `diag8_h1`: **open**; this cycle has neither parent-860 coverage nor a
  universal all-family relative complex.
- `diag3_triple_hc0`, `diag3_pair_hc1`, `diag4_sp`, and `diag9_h0`: **open and
  out of scope**.
- theorem ledger: fixed at `2/9`; promotion is prohibited.

## Canonical input accounting

| Input | SHA-256 |
| --- | --- |
| `ops/research-team/PROTOCOL.md` | `7b3fe051677d31748d483de006d9cfc97d26518f5103016371ed7ccee469654c` |
| `ai/omreal/data/CANONICAL_RESEARCH_STATE.json` | `89d1475a43bef01be74e9c8eed62d9caadd8265f262c3aa3dcf0e704f341432c` |
| `ops/team/diag8-dual-prover/DIAG8_PARENT860_GRAPH_H1_CERTIFICATE.json` | `f2c381e99959f98df7ce538d00e6694a37d92b79e5ae89417b1ca3c426592f8b` |
| `ai/omreal/data/DIAG9_GRAPH_parent860_coordinate_star.npz` | `9274371ec45baee318cd160f931344f37dc5031acc13d63c16099534b8896f4b` |
| `ai/omreal/NINTH_DIAGONAL_SAFE_GRAPH.md` | `8af233ced03055881572353d26d6f3a7d931649a9456fe7018cbc31202f4556e` |

## Concurrency and non-overlap

The coordinator alone owns target lock, integration, canonical-state edits,
repository refs, publication, and merge decisions. The opening scout,
falsifier, and referee perform independent read-only selection work. The
nonvacuity and fan producers own only their named `ops/team/diag8-mask6-*`
surfaces. The closing referee owns only `ops/team/diag8-mask6-referee` and
must review a frozen exact head without sharing producer acceptance logic.

## Route exclusions

- no D4-S53 or D4 total-complex continuation;
- no orbit-5563 roadmap, box, collar, macrobox, or clipped-wall continuation;
- no sampled or graph-only homology claim;
- no widening beyond the one family and one fan;
- no theorem-score update.

## Roles

- coordinator: target lock, source accounting, integration, and publication;
- cross-domain scout: analogy mapping and fatal-break analysis, no proof claim;
- nonvacuity prover: candidate discovery and exact witness production;
- geometry prover: exact parent/factor fan certificate;
- falsifier: nonvacuity, omitted-cell, infinity, and scope attacks;
- independent referee: clean exact-head replay and hostile mutations.

Discovery code may use sampling, SciPy, multiprocessing, and SymPy. Published
witnesses are exact integer/rational objects. The nonvacuity verifier does not
trust SciPy; the fan verifier independently reconstructs the complete factor
pullback and singular boundary.

## Resource ceiling

Ordinary local compute only; at most 90 minutes total, with 30 minutes for the
nonvacuity gate and at most eight factor-scan workers. Stop at the first exact
endpoint. A failure does not authorize a wider parent-860 search.

## Publication authority

Every work order carries the standing publication authorization verbatim.
Workers may commit only their assigned surfaces and may not merge or update
the theorem ledger. The coordinator may publish the integrated branch, open
or update the pull request, run or rerun CI, and merge only after a clean
independent exact-head review and every required check pass. Durable recovery
material is limited to Google Drive `Projects/research-backups`.

## Closing requirements

The closing referee must bind its verdict to the exact commit and tree, replay
the producer-independent nonvacuity and all-factor fan verifiers, exercise
hostile mutations, audit source and digest completeness, and confirm the
scope excludes coverage and theorem promotion. The coordinator must record a
post-cycle `CONTINUE`, `PIVOT`, `RETIRE`, or `STOP` verdict. A positive local
filling requires `RETIRE` for this mask-6 discriminator and `PIVOT` to a fresh
independent opening audit; it does not authorize repeating this route.
