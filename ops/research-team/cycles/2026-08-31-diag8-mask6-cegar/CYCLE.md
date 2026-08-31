# D8 mask-6 counterexample-guided discriminator cycle

Date: 2026-08-31 UTC

Canonical reconciled commit: `6c7f52b43632072100b67e5f0a9b6221df14d620`

Canonical reconciled tree: `60866cb78e8aea3259cf376a4420e5370ab8c010`

Opening theorem ledger: `2/9`

## Opening strategy audit

Three independent roles compared the live D8, D3, and D9 routes after the
post-PR45 reconciliation. Scores use 5 as favorable except coverage burden
and stagnation risk, where 5 is unfavorable.

| Candidate | Ledger leverage | Quantifier readiness | Coverage burden | Terminality | Compression | Independent verification | Resource / information | Stagnation | Verdict |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| D8 parent-860 mask-6 discriminator | 3 | 4 | 3 | 5 | 4 | 5 | 5 | 2 | **`CONTINUE_BOUNDED`** |
| D9 active-sector master graph | 4 | 3 | 5 | 3 | 5 | 3 | 3 | 4 | `NO_GO_NOW` |
| D3 `Q3_COMPLETE_PARENT_BOUNDARY_ATLAS` | 5 | 2 | 5 | 2 | 2 | 2 | 1 | 5 | `NO_GO_NOW` |

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

## Route exclusions

- no D4-S53 or D4 total-complex continuation;
- no orbit-5563 roadmap, box, collar, macrobox, or clipped-wall continuation;
- no sampled or graph-only homology claim;
- no widening beyond the one family and one fan;
- no theorem-score update.

## Roles and trust boundaries

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

## Resource ceiling and stop rule

Ordinary local compute only; at most 90 minutes total, with 30 minutes for the
nonvacuity gate and at most eight factor-scan workers. Stop at the first exact
endpoint. A failure does not authorize a wider parent-860 search.
