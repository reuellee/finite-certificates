# D9 S12,37 four-support oriented normal-link cycle

Date: 2026-09-01 UTC

Canonical base revision: `c55d896cc5c0370e993b793992a2f05d894e0095`

Canonical base tree: `17299e84397aae158a2111cbe01b52f5be24bfd5`

Opening theorem ledger: `2/9`

## Mandatory opening strategy evaluation

Three independent opening audits compared the live D9, D3, and D8 routes on
the reconciled PR46/PR47 tree. Scores use 5 as favorable except coverage
burden and stagnation risk, where 5 is unfavorable.

| Candidate | Ledger leverage | Quantifier readiness | Coverage burden | Terminality | Structural compression | Independent verification | Resource / information | Stagnation risk | Verdict |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| D9 `D9_S1237_4SUPPORT_NORMAL_LINK_GATE1` | 4 | 5 | 3 | 4 | 5 | 5 | 5 | 2 | **`PIVOT` / `SELECT`** |
| D9 generic seed/projection roadmap | 4 | 5 | 4 | 3 | 3 | 4 | 3 | 3 | `STOP` in favor of the normal-link gate |
| D8 parent-860 global relative complex | 5 | 2 | 5 | 3 | 4 | 4 | 2 | 5 | `STOP`; mask 6 is retired and global coverage is absent |
| D3 `Q3_COMPLETE_PARENT_BOUNDARY_ATLAS` | 5 | 2 | 5 | 2 | 3 | 2 | 1 | 5 | `PIVOT` away; the same all-parent and true-infinity blockers remain |

`CONTINUE` is rejected because the previous D8 target closed positively and
was explicitly retired. `RETIRE` applies to that local D8 discriminator, not
to diagonal eight itself. The selected D9 gate directly tests whether the two
already certified support faces have additional inward normal-link walls that
their tangential restrictions cannot see.

## Bounded target `D9_S1237_4SUPPORT_NORMAL_LINK_GATE1`

Lock parent 2599, the globally nonempty, proper, pairwise-incomparable
`S12,37` nine-family, its exact 3,539 oriented active factor literals, and the
two certified support faces `(3,1,15)` and `(3,3,7)`.

The opening discovery reduces the tangential face-interior restrictions to
eight active factor IDs in four zero sets on `(3,1,15)` and none on
`(3,3,7)`. This is not a collar theorem: each support face has codimension six,
and factors that vanish identically on the face may have nontrivial lowest
normal forms on its five-dimensional projectivized inward link.

The gate must therefore:

1. materialize all 3,539 oriented literals with every occurrence,
   representative, fixed unit sign, and family-allowed orientation;
2. compute exact lowest multihomogeneous inward normal forms for every active
   factor and every parent inequality on both supports;
3. cover every parent-safe projective normal direction, including every
   recursive facet, base, apex, seam, and relevant coface where a leading
   coefficient vanishes;
4. certify exact feasibility/Gordan labels and complete local normal sectors;
5. prove an exact stabilization radius or equivalent Bernstein/Hardt-style
   domination showing that higher-order terms do not change the recorded link.

Positive endpoint: `COMPLETE_ORIENTED_NORMAL_LINK_GATE`, which retires only
the enumerated four-support normal-link obstruction class and authorizes a
later, separately audited collar/cell/mincut target. Negative endpoint:
`NORMAL_LINK_REDUCTION_NO_GO`, with one exact extra link wall, singular link,
missing coface, unstable higher order, or other complete obstruction. Null
endpoint: a fail-closed first unresolved stratum or orientation. Timeout
endpoint: a deterministic hash-pinned frontier. No endpoint proves diagonal
nine, constructs a global separator, or changes the ledger.

## Obligation graph

- `diag9_s1237_family_validity`: **proved at the base**; 63 exact
  nonemptiness/properness/incomparability witnesses for all nine regions.
- `diag9_s1237_active_literals`: **finite-exact at the base**; 3,539 oriented
  active factor classes after 8,916 certified-empty factors are removed.
- `diag9_s1237_tangential_filter`: **finite-exact opening discovery**; eight
  factor IDs / four zero sets on `(3,1,15)`, zero / zero on `(3,3,7)`.
- `diag9_s1237_oriented_normal_link`: **selected finite-exact target**; all
  literals, inward directions, recursive boundary strata, and stabilization.
- `diag9_s1237_collar_complex`: **open and downstream**; prohibited this cycle.
- `diag9_h0`: **open**; no active-sector coverage or separator theorem.
- `diag3_triple_hc0`, `diag3_pair_hc1`, `diag4_sp`, and `diag8_h1`: **open and
  out of scope**.
- theorem ledger: fixed at `2/9`; promotion is prohibited.

## Canonical input accounting

| Input | SHA-256 |
| --- | --- |
| `ops/research-team/PROTOCOL.md` | `54f1a15b7774085005707727780b266ffbd4a8edc4687fe14e1e6bc76d229031` |
| `ops/research-team/verify_cycle_protocol.py` | `4d9e16daed0de08af415e95c746803b512ea8b92c452df6df2c9e09fdcd3b7d1` |
| `ai/omreal/data/CANONICAL_RESEARCH_STATE_V2.json` | `508d5433d33eeb5be915e1749838d73541a8bd0055c74fac00bdb74ee28e930f` |
| `ai/omreal/NINE_DIAGONAL_STATUS.md` | `3c360a2f7311bec48a3b5586684b08eadb70fc928530d1287fc68bc5161255ce` |
| `ai/omreal/DIAG9_ACTIVE_SECTOR_THEOREM.md` | `132a51b92a9813947e7ab7a43b52aafa6b2c789126e31cfc8a7f0773ee30b790` |
| `ai/omreal/verify_diag9_active_sector.py` | `8317442e095918748397fe302157212333fd908efadfa9c0ab6b5d175599dfd0` |
| `ai/omreal/DIAG9_SIGN_GEODESY_AUDIT.md` | `64896fa28a76f57344bd246f1546322e1361f6ac57f164ca6199c58938c30903` |
| `ai/omreal/NINTH_DIAGONAL_SAFE_GRAPH.md` | `8af233ced03055881572353d26d6f3a7d931649a9456fe7018cbc31202f4556e` |
| `ai/omreal/DIAG9_GRAPH_TREE_CERTIFICATE.md` | `63966868407713f1977b16b2ae8c435eb186d0569ce6239cc91d623a566ceb2e` |
| `ai/omreal/DIAG9_GRAPH_COM_AUDIT.md` | `4764626a03b1f5f36ee4b7ee53ca2048d3135c1a1f588d79f23d77cbbaa8844c` |
| `ai/omreal/data/DIAG9_GRAPH_global_factor_census.npz` | `3984ce87e11fd59d804e59568177248e218cd1c7bb07aae0a9f9f746858728bc` |
| `ai/omreal/data/DIAG9_GRAPH_row2599_factor_states.npz` | `f44b1fccfb4e61273aeceb8796a18098d82c48473e257556ce3d2a22f99b0bcf` |
| `ai/omreal/data/ninth_candidate_12_37_antichain.npz` | `11ca66549982ec40ce8425d2caed45b418edb73c4eb415a45b39d57e481bd1e4` |
| `ai/omreal/data/ninth_candidate_12_37_path.npz` | `8db38e00d9bf8701558c27cd4ede3e024db8953ea3ef9873bf0b4fc65ad6bcda` |
| `ai/omreal/DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_GATE.md` | `2b955d7b50213e2a0a750c268ccecbf6ac9d5e9ed3a146b3bb0faf7a4739dddc` |
| `ai/omreal/verify_diag3_pair_global_four_support_gate.py` | `90b3d747f71d56245607b281166eca3f43cdfdbe8dff3a49327ad81bf9b3c845` |
| `ai/omreal/data/DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_GATE.json` | `d9a16b39966cb1ce404b3df8362b722052fdc0854db331e5bc12aeec4ef9bcef` |
| `ai/omreal/data/DIAG3_PAIR_GLOBAL_row2599_compactification_atlas.json` | `956fbe7e5c7b1e04c8873ed9c0f3de9cb5420e3e06f1d5fae4c60f4e0571b364` |
| `ai/omreal/data/DIAG3_PAIR_GLOBAL_row2599_parent_face_gate.json` | `cc279d125605b45d25a3a01f462ad051038102f2bf12574f494a9d261bfc7401` |

The exact opening verifier independently reconstructs the 3,539-to-8-to-4
tangential filter and its semantic digest. It treats that filter only as a
target-selection pin.

## Concurrency and non-overlap

The coordinator alone owns this cycle directory, local integration, durable
checkpoints, and any later canonical-state proposal. The constructive prover,
falsifier, and certificate engineer own disjoint `ops/team/diag9-s1237-*`
surfaces. The closing referee is activated only after an integrated local head
is frozen and owns only its referee surface. No worker may use or alter another
producer's acceptance logic.

The old remote D9 opening branch is stale against the reconciled base and is
read-only provenance, not a source branch. No work may be cherry-picked from
it without an exact source and authority audit.

## Roles

- coordinator: target lock, source accounting, local integration, Library
  checkpoint, and Drive recovery mirror;
- constructive prover: complete oriented normal-form and stabilization
  certificate;
- falsifier: independent orientation, omitted-stratum, singular-link, and
  tangential-as-collar attacks;
- certificate engineer: producer-independent schema, manifest, replay, and
  hostile mutation harness;
- independent closing referee: clean frozen-head replay and scope verdict.

Discovery may use SymPy and ordinary local parallelism. Accepted witnesses
must be exact integer/rational artifacts, and the verifier must rebuild every
claimed orientation and link census from pinned sources.

## Resource ceiling

Ordinary local compute only; at most 30 minutes and 12 GiB per worker. Stop at
10,000 unique link polynomials, 100,000 certified link cells, the first exact
obstruction, or the time/memory ceiling. A stopped worker must emit a
deterministic hash-pinned frontier. No paid services or external compute.

## Publication authority

The ChatGPT Library is the canonical durable working branch. Google Drive
`Projects/research-backups` is a recovery mirror. Local scratch is ephemeral
and is not an authority. GitHub is read-only: no push, branch publication,
pull request, CI trigger, or merge is permitted until a new explicit user
instruction. Every work order carries this current authorization verbatim.

## Closing requirements

The closing referee must bind its verdict to an exact local commit and tree,
replay the producer-independent orientation and normal-link verifiers, exercise
all omission and scope canaries, and confirm that a positive result retires
only the four-support obstruction class. The coordinator must record the exact
ledger delta (necessarily `0` absent a theorem-level separator), surviving
global coverage and true-infinity blockers, and a post-cycle `CONTINUE`,
`PIVOT`, `RETIRE`, or `STOP` verdict before any successor cycle.
