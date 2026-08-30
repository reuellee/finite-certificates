# D3 orbit-5563 post-main reconciliation review

Date: 2026-08-30 UTC

Track: `diag3-orbit5563-postmain-referee`

Final verdict: **ACCEPT_POST_MAIN_RECONCILIATION**.

Pull-request creation and protected CI may proceed only from exact published
head `827959f624a4e2d197f940c066b4baf4a9df5d5e`, tree
`e80fd679624a9119dadae7ffdaf46963fe527a6e`, on
`research/diag3-orbit5563-global-exit-20260830`, while canonical `main` remains
exactly `9332f507996a8594883619cb530565ced79b59eb`. Any movement of either ref
invalidates this acceptance and requires another reconciliation audit.

## Exact identity and reconciliation

The authenticated GitHub connector independently resolved the reviewed refs
and commits as follows.

| Object | Exact identity |
| --- | --- |
| canonical `main` | commit `9332f507996a8594883619cb530565ced79b59eb`, tree `692d173462497cb645127ea1ced6cbe40aba4d5a` |
| reconciled D3 publication head | commit `827959f624a4e2d197f940c066b4baf4a9df5d5e`, tree `e80fd679624a9119dadae7ffdaf46963fe527a6e` |
| reconciled first parent | `4af514719fa0a2d08e6cc9c69d4d6538ddb19452`, the previously accepted D3 final candidate |
| reconciled second parent | `9332f507996a8594883619cb530565ced79b59eb`, merged D4 predecessor and current `main` |
| corresponding local candidate | commit `fbac5a1828f6a7b980bb1acdc8f09d76c4fe0e77`, tree `e80fd679624a9119dadae7ffdaf46963fe527a6e` |
| previous exact-head referee receipt | commit `385d3f3ea9171de040ba2420f3ae29a82e69e3f6` |

The local and reconciled published candidates therefore have identical content
trees. Authenticated comparison from `4af514719fa0a2d08e6cc9c69d4d6538ddb19452`
to `827959f624a4e2d197f940c066b4baf4a9df5d5e` reports no changed files. Its
`ahead_by=2` metadata records the reconciliation merge and the newly reachable
merged-predecessor ancestry; it does not represent a content delta. The
reconciliation is content-neutral relative to the independently accepted D3
candidate.

Authenticated comparison from current `main` to the reconciled D3 head reports
`ahead_by=9`, `behind_by=0`, with merge base equal to current `main`. It lists
exactly twenty-two added paths:

- the D3 cycle control files `CYCLE.md`, `WORK_ORDERS.yaml`, and
  `CYCLE_REPORT.md`;
- the D3 prover's seven proof, manifest, contract, canary, and verifier files;
- the D3 falsifier's five findings, manifest, contract, result, and verifier
  files; and
- the D3 referee's seven opening, rereview, closing, handoff, and verifier
  files.

No D4 file is duplicated. No theorem or decision ledger, canonical status
file, unrelated implementation path, prior worker/referee artifact, or other
unrelated path changes in the main-to-D3 delta.

## Previous referee receipt

The authenticated connector fetched commit
`385d3f3ea9171de040ba2420f3ae29a82e69e3f6` and confirmed that it adds only
`ops/team/diag3-orbit5563-integration-referee/FINAL_REVIEW.md` and
`FINAL_HANDOFF.yaml`. Their Git blob identities are respectively
`e0474b4de80beacc25221704fb920a9db0b84527` and
`11677aa4d49adc83df2232a122b2be71aec20e4b`.

The receipt's verdict is `ACCEPT_FOR_PUBLICATION_AT_EXACT_HEAD` for published
candidate `4af514719fa0a2d08e6cc9c69d4d6538ddb19452`, tree
`e80fd679624a9119dadae7ffdaf46963fe527a6e`. It pins the same terminal-null
counts and scope recorded below. Its old `main` identity was intentionally a
movement stop condition; the present review discharges only that movement by
checking the content-neutral reconciliation. It does not broaden the earlier
acceptance.

## Independent replay

The following commands were run from the clean assigned worktree at local
candidate `fbac5a1828f6a7b980bb1acdc8f09d76c4fe0e77`:

```text
PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 python3 ops/research-team/verify_cycle_protocol.py
PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 python3 ops/team/diag3-orbit5563-referee/verify_closing_referee.py
git diff --check
```

The protocol replay passed with three governed cycles and nine work orders,
each carrying the exact standing publication authorization and separate worker
restrictions. The closing verifier independently reconstructed:

- `2,604` realizable unlabelled parent types and `40,320` frames per type;
- `100,086,840` exact quotient classes;
- weighted raw multiplicity `104,993,280 = 2,604 * 40,320`;
- parent automorphism histogram
  `1:2382, 2:183, 3:10, 4:16, 6:3, 8:6, 12:1, 16:1, 24:2`;
- identity stabilizer and orbit size `40,320` for the pinned hard triple;
- agreement of both worker manifests for all `2,604 / 2,604` parent rows and
  every automorphism element;
- exact open-cell transport only, with
  `Q3_COMPLETE_PARENT_BOUNDARY_ATLAS` still missing; and
- rejection of all `7/7` independent hostile mutations.

The replay emitted GF(2) mask-stream digest
`43860334dd86422923a51a4018f3205cf4df1fb296a3d2b8b00b2e824910ae84`
and closing semantic digest
`0ae6a0662872e78d31d116c53c77ec2df0efcee6d6f01dc39e16ca32235a5050`.
`git diff --check` also passed.

## Terminal-null scope

The post-main reconciliation changes ancestry only. The accepted scientific
result remains a terminal null:

| Item | Exact state |
| --- | --- |
| quotient classes | `100,086,840` |
| weighted raw presentations | `104,993,280` |
| smallest missing obligation | `Q3_COMPLETE_PARENT_BOUNDARY_ATLAS` |
| unresolved D3 rows | `1,162,302 -> 1,162,302` |
| theorem ledger | `2/9 -> 2/9` |
| topology computation | `NOT_AUTHORIZED_NOT_RUN` |
| component or compact-component conclusion | none |
| strategy close | mandatory `PIVOT` |
| successor target | neither selected nor authorized |

The exact quotient compression and all-interior-point transport do not supply
a complete normalized compactification, boundary atlas, closure attachments,
component partition, rank-drop transport, true-infinity tags, global-exit
graph, compact component, row removal, or theorem. Representative matrices
remain sign witnesses and do not cover full realization spaces. The ledger and
canonical status remain unchanged.

## Gate decision

The identity, ancestry, content-neutrality, ownership, replay, independence,
coverage-scope, transport-scope, hostile-canary, authorization, and ledger
honesty gates all pass for the exact reconciled head. No candidate content was
modified during this audit. Protected CI and merge have not been claimed and
remain publication-stage gates. Accordingly, PR creation and CI may proceed at
`827959f624a4e2d197f940c066b4baf4a9df5d5e` only. Merge remains permissible
only after required checks pass at that same independently reviewed head.

## Publication authorization and role restriction

The user explicitly authorizes this 9DVL cycle to publish research code and
artifacts to the public GitHub repository `reuellee/finite-certificates`;
create and update named research branches and pull requests; push commits;
run or rerun CI; and merge only after required checks pass at the exact
independently reviewed head.  The user also authorizes durable recovery
checkpoints only in the Google Drive `Projects/research-backups` area.  This
authorization does not permit publishing secrets or private unrelated files,
modifying any other repository, using paid external compute or paid APIs,
changing repository visibility or settings, force-pushing, deleting history
or data, or taking other irreversible actions without separate approval.
Use the authenticated GitHub connector for GitHub publication operations;
do not substitute `gh`.

Workers may prepare and push their assigned branches when the work order says
so, but they may not merge or update the theorem ledger.
