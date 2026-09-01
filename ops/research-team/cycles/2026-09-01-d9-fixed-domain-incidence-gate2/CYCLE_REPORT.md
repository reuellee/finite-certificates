# Cycle report: D9 fixed-domain incidence gate 2

## Canonical base and target

- Base revision: `32e2b37bf54c53982cb58a3b8d026734f9ab1113`
- Base tree: `689d1a5fb981fd2d52f7adb88721d9c7d3a01228`
- Frozen candidate: `527e1fa16f65fab40a6b67e4e657f4a657b43e57`
- Frozen candidate tree: `585c13a9ec3f9f11c265e13b9c70d3c716a16c81`
- Opening ledger: `2/9`
- Closing ledger: `2/9`
- Selected target: `D9_FIXED_DOMAIN_INCIDENCE_GATE2`

## Strategy evaluation

The cycle selected one final bounded `CONTINUE` test of the roadmap route:
compute the exact symmetry stabilizer of the complete active factor set and
screen the low-degree source factors against the chosen projection.  This was
preferred to a 6.26-million-pair enumeration and to importing the ambient
9,476-orbit theorem without a fixed-domain invariance proof.

## Role assignments and handoffs

| Role | Surface | Classification | Endpoint |
| --- | --- | --- | --- |
| coordinator | cycle directory | exact integration | scope and anti-stagnation enforced |
| constructor | `d9-fixed-domain-incidence-constructor` | exact negative | trivial stabilizer; nongeneric projection |
| falsifier | `d9-fixed-domain-incidence-falsifier` | fatal witnesses | factor 26 maps outside; factor 57 polar locus |
| certificate verifier | `d9-fixed-domain-incidence-certificate` | independent ACCEPT | 8/8 hostile mutations rejected |
| closing referee | `d9-fixed-domain-incidence-referee` | frozen-head ACCEPT | `PIVOT` required |

## Exact findings

All 40,320 label permutations were exhausted.  Only the identity preserves
the complete fixed-domain set of 3,539 active primitive factors.  The exact
fixed-domain unordered-pair quotient is therefore still 6,260,491, above the
96,461 remaining pair-system budget.  The global 9,476 pair-orbit theorem is
not contradicted; it is an ambient simultaneous-relabeling theorem and does
not preserve this fixed parent/family active set.

The deterministic projection vector fails earlier.  Of all 83 active factors
of degree at most two, ten have inconsistent polar equations and 73 have
positive-dimensional polar loci.  Factor 57 is an explicit witness: the
polar affine equations have rank four and a five-dimensional solution space,
and the wall polynomial restricts identically to zero there.

## Gate table

| Gate | Result |
| --- | --- |
| predecessor source pins | `PASS` |
| all 40,320 label permutations | `PASS` |
| factor action on all active occurrences | `PASS` |
| pair quotient below 96,461 | `FAIL`: 6,260,491 |
| ambient 9,476 quotient preserves fixed domain | `FAIL` |
| 83-factor low-degree projection screen | `PASS` as an exact audit |
| selected projection generic on low-degree factors | `FAIL`: 73 positive-dimensional polar loci |
| independent replay | `PASS` |
| hostile mutations | `PASS`: 8/8 certificate and 6/6 closing mutations rejected |
| critical enumeration | `DENIED`; zero systems solved |
| ledger promotion | `DENIED`; remains `2/9` |

## Obligation-graph delta

- Closed: exact fixed-domain active-set stabilizer.
- Closed: exact low-degree projection specialization screen.
- Falsified: reuse of the full ambient `S_8` quotient as a fixed-domain pair
  quotient.
- Falsified: the deterministic powers-of-two projection specialization.
- Unchanged: complete source-derived parent-residence multiwall incidence.
- Unchanged: higher-degree projection or replacement projection selection.
- Unchanged: fixed-domain roadmap, connectivity, diagonal nine, and theorem
  ledger.

The result reduces end-to-end burden by retiring two invalid authorization
shortcuts, but it is not theorem progress and does not add local coverage that
can be promoted.

## Mandatory post-cycle strategy evaluation

The complete fixed-domain incidence blocker survived the preceding preflight
and this successor.  This cycle additionally falsified its chosen projection.
The protocol's two-cycle anti-stagnation rule therefore forbids another
`CONTINUE` based on symmetry-only compression or unfiltered pair enumeration.

| Successor candidate | Ledger leverage | Quantifier readiness | Terminality | Main risk | Verdict |
| --- | ---: | ---: | ---: | --- | --- |
| exact fixed-domain counterexample CEGAR | 5 | 4 | 5 | exact realization of proposed cuts | **PIVOT tournament leader** |
| projection-free adaptive component decomposition | 4 | 3 | 4 | complete parent-residence invariant | **PIVOT tournament challenger** |
| choose another projection and retry the same roadmap | 3 | 3 | 2 | incidence blocker unchanged | `RETIRE` as immediate successor |
| unfiltered or ambient-orbit pair census | 2 | 1 | 1 | invalid quantifier transfer | `STOP` |

Closing verdict: **`PIVOT`**.  The next admissible action is a strategy
tournament between exact fixed-domain counterexample CEGAR and a
projection-free adaptive decomposition.  No successor is silently selected.

## Publication revision and backup manifest

The frozen local candidate is `527e1fa16f65fab40a6b67e4e657f4a657b43e57`.
GitHub was not written, CI was not triggered, and no pull request or merge was
created.  No outbound Drive mirror was made; this checkout is the local
checkpoint, and external mirroring remains subject to the standing explicit
authorization boundary.
