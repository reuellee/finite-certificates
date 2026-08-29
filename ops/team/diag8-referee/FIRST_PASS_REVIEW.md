# Diagonal-eight independent referee: first-pass review

Date: 2026-08-29 UTC

Track: `cycle-20260829-diag8-referee`

Role: independent verifier/referee

Canonical evidence base: `5393b03fda623dc6b4552130d13467fae71d31bc`

Canonical tree: `06cc3363a021b8adc59e66865f44bf8eafa66029`

Work-order carrier commit: `e07d7f9dec6bdf432b1ce82669f35201b6aa5e95`

## First-pass disposition

The diagonal-eight strategy reset is mathematically well targeted but has not
yet supplied theorem evidence.  The pinned dual master-cell theorem reduces
the target to a complete, regular, labeled chamber/wall/node complex, and an
exact `C_2 -> C_1 -> C_0` calculation or a proof-carrying label-safe Morse
certificate can settle the resulting `H_1`.  This is genuinely smaller than
the diagonal-three global closure problem.

The reduction does **not** permit promotion from an embedded roadmap, sampled
network, chamber graph, local node census, or connected-support routing
result.  The parent-860 canonical repaired network has 24 vertices, 39 edges,
cycle rank 16, and no two-cells; individual induced supports can contain graph
cycles.  It is therefore training data only for diagonal eight.  Complete
two-cell incidence and geometric coverage are indispensable.

A coordinator-supplied live diagnostic (not independently replayed in this
pass) classifies 26,738 of 26,740 residual factors on one `a/g` bounding
rectangle, leaving factors 16573 and 22629 unresolved, while resolving all 70
parent brackets.  This is useful narrowing, but it is not a polygon-filling
or chamber-coverage certificate.  Until the two residual factors and the
rectangle-to-parent-domain coverage obligation are discharged, G05--G06
remain failed for any theorem-level claim based on that scan.

First-pass outcome: **inconclusive by design; acceptance criteria established**.
No ledger change is recommended.

## Locked target and quantifiers

The exact global diagonal-eight claim is:

> For every realizable uniform rank-four oriented matroid `M` on eight
> elements and every set `S` of exactly eight extension signatures whose
> feasibility regions are nonempty, proper, and pairwise incomparable under
> inclusion,
> `H_1(intersection_{sigma in S} F_sigma; Q) = 0`.

For degree one, ordinary and reduced homology agree.  The quantifier is over
every internal eight-element antichain of proper feasibility regions, not
only globally inclusion-minimal regions.  Equal feasibility regions are one
region class and cannot both occur in an admissible antichain.

A single-parent result must be reported as parent-local.  A global proof must
cover every canonical realizable parent class, or replace enumeration by an
exact transport theorem whose hypotheses, orientation conventions, and
parent-catalog coverage are independently verified.  A counterexample needs
only one parent and one admissible family, but it must establish nonzero
`H_1` in the full feasibility intersection, not in an unproved sampled
subcomplex.

## Canonical theorem audit

### Dual master-cell theorem

`DUAL_MASTER_CELL_PROGRAM.md` correctly makes the following conditional
reduction.  After a simultaneous semialgebraic triangulation/regular CW
refinement of the compactified parent cell, compatible with infinity and all
bad loci, the barycentric dual blocks of feasible interior primal cells form
`D_S` and the given barycentric reweighting retracts `F_S` onto `D_S`.
For `s=8`, only primal codimensions 0, 1, and 2 enter the cellular `H_1`
calculation.

This theorem is a reduction, not a coverage certificate.  A candidate must
instantiate its hypotheses: every connected chamber, every regular open wall
cell, every regular codimension-two cell, all artificial refinement faces,
all incidence maps, and the compactification boundary must be accounted for.
Raw factor sign words or connected zero sets are not automatically regular
cells and do not establish this hypothesis.

### All-strata gluing theorem

`NINTH_DIAGONAL_SAFE_GRAPH.md` supports reconstruction of each *interior*
wall/node label as the intersection of its incident full-dimensional
chamber-germ labels.  It does not authorize assigning such a label to an
infinity cell, using a coarse global zero/sign component in place of its
regular germ refinement, or omitting unobserved incident germs.  The
three-support combinatorial padding check replayed successfully, while its
own output correctly records that the geometric theorem still depends on
the canonical derived-wall rank and side theorems.

### Master-chamber graph theorem

The chamber graph is complete for `H_tilde_0`, not for `H_1`.  A cycle in a
supporting chamber graph can be filled by a codimension-two dual cell.
Conversely, a graph-only connectedness certificate gives no information about
whether graph cycles survive the `C_2` boundary.  Diagonal-nine routing
artifacts may seed discovery but cannot pass a diagonal-eight gate without a
proved extension to the complete two-skeleton.

### Local and abstract regressions

The exact row-2599 node verifies that one local disk has only empty or convex
common-feasibility loci.  It is a positive local regression, not global
coverage.  The exact annulus no-go verifies that all-strata gluing,
noncompact smooth common-zero components, and fixed unit Jacobian minors do
not imply diagonal eight abstractly.  Any proposed proof using only those
properties must be rejected unless it adds a third-compound-specific global
topology argument.

## Canonical input accounting

All digests below are SHA-256 of the file bytes at the canonical base tree.

| Input | SHA-256 |
|---|---|
| `ai/omreal/NINE_DIAGONAL_STATUS.md` | `0c2bbc543a51399ad27c605432a615e1fe60f18650778e2943d11364ee1137f8` |
| `ai/omreal/DUAL_MASTER_CELL_PROGRAM.md` | `bac5bcaab0542069cff3e014c13e6a01f1d940c015796fc16591d88d0a00043e` |
| `ai/omreal/NINTH_DIAGONAL_SAFE_GRAPH.md` | `8af233ced03055881572353d26d6f3a7d931649a9456fe7018cbc31202f4556e` |
| `ops/team/diag8-referee/WORK_ORDER.yaml` | `d7e5332ab378b1a1cd84ca366479c7750b3bde701dd314a68aad9ed990bbb0a1` |

The first three files are pinned by tree
`06cc3363a021b8adc59e66865f44bf8eafa66029`.  The work order is carried by
the later coordination-only commit named above and is not part of the
mathematical evidence base.

## First-pass canonical replays

Environment: CPython 3.12.13; `PYTHONDONTWRITEBYTECODE=1`; clean referee
worktree before and after replay.

| Command | Exit | Referee interpretation |
|---|---:|---|
| `python ai/omreal/verify_generic_wall_gluing_combinatorics.py` | 0 | 560/27,720 structural common-pair triples and at least 35 nonstructural paddings for every other triple; geometry remains separately assumed. |
| `python ai/omreal/verify_dual_master_node.py` | 0 | Local chamber/wall/node labels, convex intersection closure, and corrupted-wall canary pass on the pinned row-2599 disk. |
| `python ai/omreal/verify_partial_mutation_fiber_disconnected.py` | 0 | Hostile regression: global mutation connectivity cannot replace fiber-specific coverage. |
| `python ai/omreal/verify_residual_stratum_no_go.py` | 0 | Hostile regression: the abstract hypotheses permit an annular eightfold support with `H_1 = Z`; third-compound structure is necessary. |

The explicit pass-two gates are in `GATE_TABLE.yaml`.  Missing or ambiguous
evidence fails closed; a failed sufficient certificate is inconclusive about
the theorem unless it supplies an exact counterexample.

## Exact pass-two request

The coordinator must supply the manifest listed in
`PASS2_REQUIREMENTS.yaml`.  In particular, the referee needs a pinned
candidate revision, immutable artifact digests, the exact claim list and
scope, clean replay commands, independent-verifier entry points, a complete
cell/incidence manifest (including infinity), the admissible-family census,
and every transport edge claimed to replace direct parent coverage.

The referee will not repair candidate evidence.  Any candidate whose replay
requires discovery-side state not included in its manifest, exceeds the
agreed resource ceiling, changes target quantifiers, or lacks a complete
`C_2 -> C_1 -> C_0` or sufficient Morse certificate will be rejected for
integration in this cycle.
