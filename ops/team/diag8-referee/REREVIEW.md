# Diagonal-eight corrected-candidate rereview

Date: 2026-08-29 UTC

Track: `cycle-20260829-diag8-referee`

Corrected candidate: `fc11aff61ec0a13fa002850091ae33d494b04b8c`

Corrected tree: `161441345f960338b04c61385b8763da25d81a52`

Corrected handoff carrier: `7ce733831178542b9809b2ca88b97edbc8c0c1ef`

Corrected carrier tree: `1027321031588da7a9c57c9763102ab0f7525da7`

Prior rejected candidate: `be7b5953856bb0f8dbb3dc63b5757edfb259268f`

## Disposition

**Accept the corrected evidence candidate for coordinator integration and
publication of the five bounded research claims.**

This acceptance supersedes the pass-two rejection of the prior immutable
candidate.  It does not prove diagonal eight, advance `diag8_h1`, or change
the honest 9DVL ledger from `2/9`.  Protected repository checks at the exact
integrated head remain a coordinator-owned publication gate.

## Correction verified

The corrected source-derived census is exact:

- `26,264` total represented signatures;
- `13` total network support classes;
- one universal class containing `25,960` signatures; and
- `12` proper classes containing `304` signatures in total.

The corrected first-family quantifier now explicitly covers all 12 proper
support-pattern classes and excludes the universal class.  The same census is
stated consistently in the certificate, prover result, proof note, cycle
report, and dual-master program.

The hardened prover reconstructs all five counts from the pinned source NPZ,
compares them with the certificate, and requires

```text
304 + 25,960 = 26,264.
```

Its new fifth hostile canary increments the proper-signature count and is
rejected.  The exact replay exits zero with deterministic output SHA-256

```text
240e2177ba592cbbfa882b891c3997608be011681259b14cd381c81deb3475ed
```

and reports all five hostile mutations rejected.

## Artifact and change audit

All 20 entries in `CANDIDATE_HANDOFF_V2.yaml` match their stated byte sizes
and SHA-256 digests at the corrected immutable tree.

The only mathematical certificate changes are the five source-derived
support-accounting fields.  Direct structural comparison with the rejected
candidate confirms that these objects are unchanged:

- the 24-vertex/39-edge graph;
- all 12 proper patterns, their multiplicities, and representatives;
- the width witness, chain cover, and antichain counts;
- the graph cycle and boundary-rank data; and
- every rational coordinate, witness, and strict control in the `a/d`
  triangle filling.

The falsifier, abstract certificate, and transport artifacts and verifier
sources are byte-identical to those accepted mathematically in pass two.
The `a/g` filling, graph-only no-go, and transport no-go therefore retain the
prior exact replay without a moved input or changed scope.

No unexpected whitespace, YAML, or JSON defect was found in the changed
artifacts.

## Claim dispositions

| Claim | Rereview result | Exact scope |
|---|---|---|
| `parent860_local_support_width` | accepted finite-exact | the 12 proper local classes only; width six, nine empty-support six-antichains, no local eight-antichain |
| `parent860_ad_triangle_filling` | accepted finite-exact | one rational parent-860 triangle and five proper incomparable signatures |
| `parent860_ag_pentagon_filling` | accepted finite-exact | one rational parent-860 polygon and its 26,038 stored boundary-common labels |
| `graph_only_h1_no_go` | accepted abstract no-go | finite regular relative two-complex fixtures, not UOM geometry |
| `unconditional_transport_no_go` | accepted finite-exact no-go | the pinned mutation and deletion fixtures only |

All explicit nonconsequences remain present.  In particular, the local width
result is vacuous for the diagonal-eight quantifier, and no graph cycle is
treated as geometric homology without a certified two-cell.

## Gate result

- G00, G01, G02, G03, G13, and G15 now pass for the corrected bounded claims.
- The bounded polygon geometry, labels, incidences, and rank calculations
  retain their prior passes.
- G04--G14 remain open or inapplicable for a parent-local or global
  diagonal-eight theorem, as explicitly stated by the candidate.
- G16 passes the referee evidence/prose-consistency portion.  Protected checks
  and exact-head repository status remain pending coordinator execution.

There are no actionable referee defects.  The surviving research blocker is
unchanged: the mask-6 cycle `4-11-12-14-13-23-4` lacks either a
coverage-certified spanning two-chain or an exact non-boundary cocycle.

Recommended ledger change: **none**.
