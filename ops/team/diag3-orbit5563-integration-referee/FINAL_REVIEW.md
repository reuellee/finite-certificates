# D3 orbit-5563 final-head integration review

Date: 2026-08-30 UTC

Track: `diag3-orbit5563-integration-referee`

Final verdict: **ACCEPT_FOR_PUBLICATION_AT_EXACT_HEAD**.

Publication may proceed only from published commit
`4af514719fa0a2d08e6cc9c69d4d6538ddb19452`, tree
`e80fd679624a9119dadae7ffdaf46963fe527a6e`, on
`research/diag3-orbit5563-global-exit-20260830`. Any movement of that branch or
of canonical `main` from `aa784af939b55d3503e4782a9d65a9b06cf81ce0`
invalidates this acceptance and requires reconciliation and rereview.

## Exact reviewed identity

| Object | Exact identity |
| --- | --- |
| final candidate, local | commit `fbac5a1828f6a7b980bb1acdc8f09d76c4fe0e77`, tree `e80fd679624a9119dadae7ffdaf46963fe527a6e` |
| final candidate, published | commit `4af514719fa0a2d08e6cc9c69d4d6538ddb19452`, tree `e80fd679624a9119dadae7ffdaf46963fe527a6e` |
| closing referee, local parent | commit `67213be260363948c675bb4a718c3e23cbdd5ad6`, tree `5eee4008f2527d096d34677505d1fb37f7b8194d` |
| closing referee, published parent | commit `409c29a898f0cb8ec7ee64ee3afecf21d222ee20`, tree `5eee4008f2527d096d34677505d1fb37f7b8194d` |
| reviewed worker integration | published commit `af098d1297dd5c82f194d1f4d03a9ac75afafba9`, tree `dcd0e683a33468194f38353a72ebc84c213b0b35` |
| canonical `main`, first and final observations | commit `aa784af939b55d3503e4782a9d65a9b06cf81ce0`, tree `6aa36a92c5e5d2e420ec660a1ad2c2be2b06a561` |

The authenticated GitHub connector resolved the publication branch to the
exact published candidate above. Its sole parent is the exact published
closing-referee commit. The connector comparison is one commit ahead, zero
behind, and adds exactly one file:

`ops/research-team/cycles/2026-08-30-diag3-orbit5563-global-exit/CYCLE_REPORT.md`

with `131` additions and no deletions. The local comparison has the identical
one-file delta, and the local and published candidate content trees are equal.
The report's raw SHA-256 is
`a2baf8cf0a8e0cfdfc845f38569557e95e2953995ad8964b912ef8738ffa7c5f`.

## Independent replay

| Gate | Exact replay result |
| --- | --- |
| strategy/publication protocol | PASS: `3` cycles, `9` authorized work orders |
| closing-referee reconstruction | PASS: `2,604` parents, `40,320` frames, `100,086,840` quotient classes, raw weighted total `104,993,280` |
| prover manifest and transport | PASS expected terminal null; `13/13` canaries |
| falsifier manifest and transport | PASS expected terminal null; hostile mutations rejected |
| hard-triple orbit | PASS: stabilizer is the identity, orbit size `40,320` |
| D3 completion object | PASS: `77,940,147 / 79,102,449`, residue `1,162,302` |
| decision ledger | PASS: honest theorem ledger `2/9` |
| parent/frame atlas scope guard | PASS: exact positive subatlas `17,105,952 / 104,993,280`; explicitly no global closure |
| boundary-stratification scope guard | PASS at declared scope; no primary decomposition or global closure claim |

The independent closing reconstruction yields the parent-automorphism order
histogram

```text
1:2382, 2:183, 3:10, 4:16, 6:3, 8:6, 12:1, 16:1, 24:2.
```

Its quotient-class contributions sum to `100,086,840`, and weighting each
contribution by its automorphism order gives exactly `104,993,280 =
2,604 * 40,320`. Both worker manifests agree with the independent
reconstruction for all `2,604 / 2,604` parent rows and every automorphism
element.

## Scope and report fidelity

The report accurately classifies the cycle as exact domain compression, not
topology or theorem progress. Exact sign, Cramer-chart, and primitive-factor
transport is proved only for every interior point and framed quotient class.
The first absent global object is
`Q3_COMPLETE_PARENT_BOUNDARY_ATLAS`: the complete compactification,
closure-stratum, transition-domain, and attachment atlas over every parent
quotient class.

The report correctly states every resulting nonconsequence:

- no topology computation was authorized or run;
- no component partition, rank-drop attachment, true-infinity coverage,
  global-exit certificate, or compact component was established;
- representative matrices remain sign witnesses, not realization-space
  coverage;
- the unresolved-row count remains `1,162,302` and the theorem ledger remains
  `2/9`.

The closing verdict `ACCEPT_TERMINAL_NULL_WITH_MANDATORY_PIVOT` is reproduced
without inflation. The report requires `PIVOT`, retires another local
box/collar/macrobox/clipped-wall continuation for this residue, and neither
selects nor authorizes a successor target. Pull request, exact-head CI, and
merge fields remain honestly `PENDING_PUBLICATION_STAGE`; the report claims no
completed CI or merge.

## Ownership, authorization, and publication decision

The candidate changes only the coordinator-owned cycle report. It does not
modify worker or referee evidence, a theorem or decision ledger, canonical
status prose, implementation code, or unrelated files. `git diff --check`
passes.

The protocol replay confirms that the standing publication authorization is
copied verbatim into every governed work order and that worker restrictions
are separate. Publication through the authenticated GitHub connector is
authorized for `reuellee/finite-certificates`; workers remain forbidden to
merge or update the theorem ledger.

The artifact, replay, independence, coverage, transport, adversarial, and
ledger gates applicable to this terminal null pass. The repository gate is
not yet claimed: protected CI must pass at the exact accepted final PR head,
and merge must bind to that same independently reviewed head. Subject to those
pending publication-stage gates and no revision movement, publication may
proceed at `4af514719fa0a2d08e6cc9c69d4d6538ddb19452` only.
