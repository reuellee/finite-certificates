# finite-certificates

A repository of small, explicit, machine-checkable research results. The guiding rule is simple: **search can be heuristic; claims must be exact**. Most theorem-level claims ship with standalone verifiers using integers, rational arithmetic, or exact symbolic computation, plus an adversarial review trail.

The repository currently has three major research fronts: exact discrete geometry, oriented-matroid realizability/topology, and machine-learning theory counterexamples.

## Current headline results

### 1. Maxout polytopes: `max f₀(3,5) = 42`

The maximum number of vertices of a 3-dimensional zonoboxtope with 5 generators is exactly **42**. This refutes tightness of Proposition 6.5 and the odd `n=5` case of Conjecture 6.6.1 in Balakin–Cox–Loho–Sturmfels, *Maxout Polytopes* (arXiv:2509.21286).

The upper bound is backed by **132,560 exact cell-wide certificates**, with an independent standard-library audit and an arXiv-ready note.

- [`ai/maxout/`](ai/maxout/)
- [`ai/maxout/paper/`](ai/maxout/paper/)

### 2. Uniform oriented-matroid mutation graphs are connected for `n <= 9`

Mutation graphs of uniform oriented matroids are connected at every rank for `n <= 9`, including the labelled `(4,9)` level where a counterexample had been suspected. The computation also corrects the number of uniform rank-4 classes on 9 elements to **9,276,595**.

- [`ai/omgamma/`](ai/omgamma/)
- [`ai/omgamma/paper/`](ai/omgamma/paper/)

### 3. Nine-Diagonal Vanishing Lemma: 2 of 9 diagonals proved

The current 9DVL ledger is **2/9**. Diagonals 1 and 2 are proved integrally. Diagonal 3 is the active frontier.

For diagonal 3, the exact research pipeline has now:

- reduced the original triple-factor census from **79,102,449** cases to **1,162,302** unresolved triple-factor orbits;
- proved exhaustively that none of those 1,162,302 rows admits a common diagonal scaling escape, and pinned five hard no-go systems for all quadratic vector fields with affine ideal multipliers;
- built an exact row-2599 candidate residual universe of **17,824** factors;
- proved that all **3,374 proper supports** of the `(Delta^3)^3` compactification lie in the relative boundary, removing **52,394 of 70,218** post-parent-gate mixed restrictions from the relative chain-generator obligation;
- certified with **105 exact parent-safe segments** that **10,844** full-support residual walls genuinely meet the strict parent interior;
- caught and corrected a tempting false symmetry reduction: moving-column permutations preserve the unsigned bracket-divisor arrangement but flip **19–27** of the 63 distinct signed parent inequalities, and all **525/525** nonidentity transported witness segments leave the row-2599 cell;
- proved by exact parent-positive polynomial identities that **1,177** of the 6,980 segment-open factors have empty strict-parent zero sets;
- thereby classified **12,021 of 17,824** full-support candidates exactly—10,844 interior-nonempty and 1,177 empty—leaving **5,803 explicitly unresolved**;
- built a complete exact two-parameter source square from chart 0 toward chart 152: all 70 parent brackets stay strict, all 17,824 residual restrictions are decided on the square, and every one of the 3,763 occurring wall components is proved to meet its boundary;
- rejected the naïve three-block source cube at two exact parent-invalid vertices, then certified the parent-safe half-cube `[1/2,1] x [0,1] x [0,1]`, where all 17,824 restrictions are again decided exactly (4,450 occurring and 13,374 zero-free);
- enlarged that volume to an eight-box parent-safe staircase occupying exactly `12817/16384` of the normalized hybrid cube; all 142,592 box-factor restrictions are decided, 5,139 distinct factors occur, and every component meets the true outer boundary by transfer from the exact ambient full-cube topology theorem;
- refuted the tempting global-incidence target for that source family: 5,390 factors with exact parent-interior crossings are zero-free on the entire chart-0/chart-152 hybrid cube, so no finer staircase inside it can cover every global wall;
- covered the first two surviving four-support parent domains `(3,1,15)` and `(3,3,7)` exactly as two-tetrahedron square pyramids, reducing **8,017** mixed restrictions to **94** parent-reduced zero sets and then **22** active wall equations with zero unresolved classifications;
- constructed the complete first fiber projection for those 22 walls: one base-only, 20 linear-fiber, and one quadratic-fiber wall yield **255** projection obligations and only **136** distinct boundary-reduced base polynomials, well below the pinned 100,000-polynomial ceiling;
- completed the second projection of those 136 polynomials: **114** base curve factors yield **6,061** nonconstant obligations and **2,554** distinct squarefree univariate projection polynomials; then isolated and globally ordered all **1,693 distinct interior `t` sections** (19 rational and 1,674 irrational);
- lifted all 114 base curves over all **1,694 open `t` sectors**: **193,116** exact specializations yield **132,134** ordered `u`-root sections and **133,828** strips, or **265,962** certified open-sector base cells; an explicit `u=1` audit found zero missing boundary factors;
- completed **1,022** simple transversal algebraic-section fibers: every adjacent swap has its swapped-pair resultant factor with raw multiplicity one and no coefficient, discriminant, or `u=1` event, yielding **170,610** additional exact base cells and leaving **671** harder sections;
- completed **363** unchanged-stack algebraic fibers with one raw-simple nonboundary event, adding **42,515** exact base cells and reducing the hard algebraic frontier to **308** sections;
- completed **240** simultaneous pure-resultant same-count fibers: 1,549 raw-simple events form 1,390 visible inversions and 549 collision cliques, adding **40,084** exact base cells and reducing the frontier to **68** sections;
- completed **40** regular residual fibers—36 unchanged stacks plus four same-count transitions—using 193 multiplicity-one resultants and four harmless non-leading coefficient events, adding **4,610** exact base cells and reducing the frontier to **28** sections;
- completed the final **28** algebraic fibers by exact ordered-number-field Sturm replay—14 root-count changes, seven exceptional same-count transitions, and seven complex unchanged stacks—adding **3,752** exact base cells and reducing the algebraic `t`-section frontier to **zero**;
- lifted every one of the **133,828** full-dimensional open base cells through the original 22 walls, producing **4,496,636** exact `v`-fiber cells;
- completed the regular algebraic-`u` portion of the `v` lift on **120,174/132,134** sections: **183,374** multiplicity-one raw resultants yield **169,750** visible inversions forming **148,896** exact collision groups and produce **3,739,392** additional cells, leaving an exact **11,960-section** coefficient or endpoint/count-change residue;
- attached all **3,990 endpoint-only count-change algebraic-`u` fibers** exactly: the one-token endpoint ownership and 7,747 interior collision groups produce **120,468** additional cells and reduce the open-`t` residue to **7,970 coefficient-event sections**;
- completed all **3,388 coefficient-only algebraic-`u` fibers** by exact unbounded degree-drop analysis, adding **79,816** cells and reducing the residue to **4,582 coefficient-plus-endpoint sections**;
- completed the final **4,582 coefficient-plus-endpoint algebraic-`u` fibers** by exact bounded degree-drop, endpoint-attachment, and fiber-wide-zero analysis, adding **108,170** cells; all **132,134** open-`t` algebraic-`u` sections are now lifted to **4,047,846** cells with zero residue;
- preserved the main missing obligation honestly: a coverage-certified global nonrelative master closure complex and the final relative middle-rank replay.

The selected route is the coverage-certified nonrelative master-closure compiler. The 5,803-factor residue remains an input gap, but standalone wall classification and further chart-0/chart-152 staircase refinement are subordinated because neither can by itself prove diagonal three.

- [`ai/omreal/NINE_DIAGONAL_STATUS.md`](ai/omreal/NINE_DIAGONAL_STATUS.md)
- [`ai/omreal/DIAG3_PAIR_FULLSUPPORT_SAFE_SEGMENTS.md`](ai/omreal/DIAG3_PAIR_FULLSUPPORT_SAFE_SEGMENTS.md)
- [`ai/omreal/DIAG3_PAIR_FULLSUPPORT_BLOCK_SYMMETRY.md`](ai/omreal/DIAG3_PAIR_FULLSUPPORT_BLOCK_SYMMETRY.md)
- [`ai/omreal/DIAG3_PAIR_FULLSUPPORT_PARENT_PRODUCT_SIGNS.md`](ai/omreal/DIAG3_PAIR_FULLSUPPORT_PARENT_PRODUCT_SIGNS.md)
- [`ai/omreal/DIAG3_PAIR_RELATIVE_BOUNDARY_COLLAPSE.md`](ai/omreal/DIAG3_PAIR_RELATIVE_BOUNDARY_COLLAPSE.md)
- [`ai/omreal/DIAG3_TRIPLE_COMMON_SCALING_NO_GO.md`](ai/omreal/DIAG3_TRIPLE_COMMON_SCALING_NO_GO.md)

### 4. `(4,9)` non-realizability is not generated by a short obstruction list

About 91% of non-realizable `(4,9)` classes contain one of the 24 known `(4,8)` obstructions as a deletion, but the remaining minor-minimal population extrapolates to roughly `10^4` templateless classes. The repository also contains Proposition R: a non-realizable deletion lifts to a biquadratic final polynomial.

- [`ai/omminor/`](ai/omminor/)

## Active research

The principal oriented-matroid program is the realizability/topology project in [`ai/omreal/`](ai/omreal/). Its long-term goals are the realizability split of all **9,276,595** uniform rank-4 oriented matroids on 9 elements and exact topological certificates strong enough to settle the remaining seven diagonals of 9DVL.

The current diagonal-three frontier is deliberately fail-closed. Of 17,824 candidate full-support residual factors, 10,844 are proved to occur in the strict parent interior, 1,177 have exact fixed-sign emptiness certificates, and 5,803 remain unresolved. A constant sign on stored or exploratory points is treated only as reconnaissance, never as an emptiness certificate.

Current target selection is governed by the machine-checked [`DIAG3_RESEARCH_DECISION_LEDGER.json`](ai/omreal/data/DIAG3_RESEARCH_DECISION_LEDGER.json) and the [`exact-mathematics research operating system`](ai/omreal/RESEARCH_OPERATING_SYSTEM.md). The August 22 decision preserves the exact ambient-topology gain, stops low-yield dyadic staircase refinement, and redirects work to the direct global roadmap/master-complex route; see [`DIAG3_DECISION_2026-08-22.md`](ai/omreal/DIAG3_DECISION_2026-08-22.md).

The procedures developed along this route are also maintained as a research output. The [`exact semialgebraic certificate method`](ai/omreal/EXACT_SEMIALGEBRAIC_CERTIFICATE_METHOD.md) and its standard-library toolkit provide reusable rational affine pullback, tensor Bernstein subdivision, fail-closed system exclusion, analytic negative canaries, semantic certificates, and producer/verifier separation.

The compiler now has three proof-producing local atlases.  The generated [`17-cell exact master-closure object`](ai/omreal/DIAG3_PAIR_MASTER_CLOSURE_NODE_CANARY.md) covers one two-dimensional full-support node disk in row 2599.  The [`3 x 3 exact multi-box atlas`](ai/omreal/DIAG3_PAIR_MASTER_CLOSURE_MULTIBOX_CANARY.md) then glues four no-wall, four one-wall and one transverse two-wall box into an 81-cell object.  The [`64-box first-event atlas`](ai/omreal/DIAG3_PAIR_MASTER_CLOSURE_FIRST_EVENT.md) crosses a genuinely new affine residual branch: 42 no-wall, 20 one-wall and two transverse two-wall boxes glue by 171 exact boundary words into a 399-cell regular-CW object.  Its hostile verifier replays all 84,840 labelled restrictions, all 70 parent brackets, all 97,224 extension signatures and all 512 profile triples, with zero middle residue and 13/13 corruptions rejected.  The artificial boundary and box seams remain distinct from true parent infinity.

The new [`exact chart-0-to-chart-89 source transition`](ai/omreal/DIAG3_PAIR_PARENT_SOURCE_TRANSITION.md) changes the parent germ along the objectively smallest parent-safe chart-zero edge.  Exact Sturm replay screens all 17,824 factors, orders 1,237 simple root crossings, and reconstructs the chart-89 factor state over a 2,477-cell regular CW path.  Its [`complete label continuation`](ai/omreal/DIAG3_PAIR_PARENT_SOURCE_LABELS.md) transports the 26,112-tope set across all 1,238 chambers using 1,179 antipodal simplicial mutations and 58 exact compound updates.  It reconstructs the independently stored raw chart-89 label state and yields 2,458 exact signature profiles.  Global parent-cell coverage remains open, so the honest theorem score is still 2/9.

The coverage-oriented source graph now also has an [`exact three-block bridge`](ai/omreal/DIAG3_PAIR_PARENT_SOURCE_BLOCK_BRIDGE.md) from chart zero to chart 152, which was isolated in the 105-edge straight-segment forest.  Replacing moving columns 6, 7 and 8 one at a time keeps all 70 parent brackets strict.  Exact Sturm replay screens all 17,824 residual factors on each segment, orders 5,612 simple crossings, reconstructs the chart-152 factor state and produces an 11,231-cell regular-CW path.  The bridge glues to the labelled chart-0-to-chart-89 path at their exact common chart-zero vertex and raw 26,112-label set.  It embeds one new germ but is not parameter-space coverage; the score remains 2/9.

The bridge now has [`complete exact label continuation`](ai/omreal/DIAG3_PAIR_PARENT_SOURCE_BLOCK_LABELS.md): 5,319 antipodal simplicial mutations and 293 exact compound re-enumerations label all 5,615 generic chambers and reconstruct the raw chart-152 tope set. A separate [`genuine parent-boundary attachment`](ai/omreal/DIAG3_PAIR_PARENT_BOUNDARY_ATTACHMENT.md) continues chart 89 through 1,517 ordered residual crossings to `[1237]=0`. The other 69 parent brackets stay positive, no residual factor vanishes at the endpoint, and all 1,518 open-ray chambers carry exact 26,112-label sets before the endpoint is quotiented as relative infinity. These certificates add exact source and frontier incidence, but not missed-component or global parent-cell coverage; the score remains 2/9.

The first exact [`source-square component-coverage certificate`](ai/omreal/DIAG3_PAIR_SOURCE_SQUARE_COVERAGE.md) now fills two independent block parameters between charts 0 and 152 while fixing the third block at chart 0. Tensor Bernstein replay proves the whole square remains in the strict parent cell and classifies all 17,824 residual restrictions there: 14,061 are zero-free, 3,763 occur, and none remain unresolved. A projection-discriminant audit then proves every occurring wall component reaches the square boundary. Two disjoint boundary-order families already force 618,120 intersecting curve pairs, so full sign-arrangement construction is subordinated to the much smaller component-coverage quotient. This is complete coverage of one square, not of the nine-dimensional parent cell; the score remains 2/9.

The source object now also has exact [`three-parameter half-cube component coverage`](ai/omreal/DIAG3_PAIR_SOURCE_BLOCK_HALF_CUBE_FEASIBILITY.md). The full `[0,1]^3` block cube is false: two hybrid vertices leave the signed parent cell. Its parent-safe replacement `[1/2,1] x [0,1] x [0,1]` overlaps the source square and contains chart 152. Exact tensor Bernstein replay decides all 17,824 restrictions on this volume—13,374 zero-free and 4,450 occurring, with zero unresolved. A graph-projection theorem covers 3,889 occurring surfaces; all 561 remaining triquadratic projection-critical systems are exactly empty. Hence every occurring wall component meets the half-cube boundary. The independent replay rejects 11 hostile corruptions.

That volume was first enlarged to an exact [`five-box source staircase`](ai/omreal/DIAG3_PAIR_SOURCE_STAIRCASE_COVERAGE.md) of normalized volume `373/512`. The new [`ambient full-hybrid-cube topology theorem`](ai/omreal/DIAG3_PAIR_FULL_HYBRID_CUBE_TOPOLOGY.md) decides all 17,824 restrictions on the full three-parameter cube—5,577 occurring and 12,247 zero-free—and proves every occurring restricted-wall component reaches the cube boundary. A semialgebraic transfer lemma therefore removes internal seams from every parent-safe source-staircase claim.

The final [`eight-box source staircase`](ai/omreal/DIAG3_PAIR_SOURCE_STAIRCASE8_COVERAGE.md) occupies exact volume `12817/16384`. All 142,592 box-factor restrictions are decided, 5,139 distinct factors occur, and 12,685 are zero-free on every box. The extra `881/16384` volume adds only 33 factors over the five-box object, so the exact yield gate stops further dyadic refinement. Global row-2599 missed-component coverage remains open and the theorem score remains 2/9.

The subsequent [`source-family incidence no-go`](ai/omreal/DIAG3_PAIR_SOURCE_FAMILY_INCIDENCE_NO_GO.md) makes that stop structural. Of 10,844 factors with exact crossings on 105 certified parent-safe segments, only 5,454 occur on the full chart-0/chart-152 source cube; the other 5,390 are exactly zero-free there. Thus universal incidence with this source family is false. The pair branch must add genuinely distinct sources with a coverage theorem or construct the global roadmap/master complex directly.

The [`optimal full-support segment cover`](ai/omreal/DIAG3_PAIR_FULLSUPPORT_SEGMENT_COVER.md) now compresses those 105 exact segments to a proved-minimum 40 while preserving one exact retained witness for each of 10,844 crossed factor classes. The original bank has 412,093 edge-factor crossing incidences and the retained bank has 157,448. Forty-nine unique-crossing factors force 34 edges; an exhaustive seven-pattern residue proves that six more are necessary and sufficient, with 3 maximal-pattern covers and 28 raw six-edge optional covers. The same audit restores theorem scope: the section-960 and section-550 stars lie wholly on proper supports and therefore contribute zero relative chain generators. They remain compiler diagnostics, while the proof-bearing pair target stays in full support. Global component coverage remains open and the score remains 2/9.

The [`first labelled full-support skeleton`](ai/omreal/DIAG3_PAIR_FULLSUPPORT_LABELED_SKELETON.md) now compiles selected cover edge 27 (charts 0 to 89) into 1,239 stable zero-cells, 1,238 oriented one-cells, all strict faces, empty true parent infinity, and complete bad-membership profiles for all 97,224 extension signatures.  The artifact fails closed on the other 39 cover edges, which still lack complete ordered residual roadmaps and compound-event label continuation.  This is exact source-skeleton structure, not parent-cell or wall-component coverage, and the score remains 2/9.

The direct route now has its first coverage-bearing higher-support checkpoint. On supports `(3,1,15)` and `(3,3,7)`, opposite signed parent brackets force `g=i` and `d=g`; both weak parent closures become the same square pyramid `0<=g<=a<=1`, `0<=g<=h<=1`, covered exactly by two rational tetrahedra. The [`four-support gate`](ai/omreal/DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_GATE.md) compresses 8,017 mixed restrictions to 22 active walls. The two projection layers produce 114 base curves and 1,693 ordered `t` sections. The [`open-sector lift`](ai/omreal/DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_OPEN_SECTOR_LIFT.md) certifies 265,962 cells over all 1,694 open sectors. The [`simple-section lift`](ai/omreal/DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_SIMPLE_SECTION_LIFT.md) completes 170,610 cells on 1,022 transversal fibers, the [`constant-stack lift`](ai/omreal/DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_INVISIBLE_SECTION_LIFT.md) adds 42,515 cells on 363 raw-simple invisible fibers, the [`multi-crossing lift`](ai/omreal/DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_MULTI_SECTION_LIFT.md) adds 40,084 cells on 240 simultaneous same-count fibers, the [`regular-residual lift`](ai/omreal/DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_REGULAR_RESIDUAL_SECTION_LIFT.md) adds 4,610 cells on 36 unchanged plus 4 same-count fibers, and the [`final-section lift`](ai/omreal/DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_FINAL_SECTION_LIFT.md) resolves all remaining higher-multiplicity and count-changing fibers with 3,752 cells. All 1,693 algebraic `t` sections are complete at the base level. The [`open-base-cell v lift`](ai/omreal/DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_OPEN_CELL_V_LIFT.md) adds 4,496,636 cells over all 133,828 full-dimensional open base cells. The four algebraic-`u` checkpoints—the [`regular`](ai/omreal/DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_REGULAR_U_SECTION_V_LIFT.md), [`endpoint-only`](ai/omreal/DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_ENDPOINT_U_SECTION_V_LIFT.md), [`coefficient-only`](ai/omreal/DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_COEFFICIENT_ONLY_U_SECTION_V_LIFT.md), and [`coefficient-plus-endpoint`](ai/omreal/DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_COEFFICIENT_ENDPOINT_U_SECTION_V_LIFT.md) lifts—cover all 132,134 sections over open `t` sectors and add 4,047,846 cells. The three algebraic-`t` checkpoints—the [`open-u-strip`](ai/omreal/DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_ALGEBRAIC_T_OPEN_U_STRIP_V_LIFT.md), [`regular-u-point`](ai/omreal/DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_ALGEBRAIC_T_REGULAR_U_POINT_V_LIFT.md), and [`final coefficient/endpoint-u-point`](ai/omreal/DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_ALGEBRAIC_T_COEFFICIENT_ENDPOINT_U_POINT_V_LIFT.md) lifts—cover all 261,571 remaining base cells and add 8,390,619 cells. Thus the complete local inventory is 527,533 base cells and 16,935,101 lifted cells with zero unresolved local `v` fibers. The [`component-cosheaf pilot`](ai/omreal/DIAG3_COMPONENT_COSHEAF_PILOT.md) proves that this inventory still lacks face-compatible closure, complete bad-signature labels, and true-infinity incidence, so global gluing and the pair middle-rank replay remain open and the score remains 2/9.

The pilot replays four certified fixtures, not only the original two: the
synthetic relative schema canary, transverse node, multibox atlas, and
first-event atlas.  The schema canary tests the relative-infinity interface;
it is not a geometric parent-divisor certificate.
Its negative result is narrowly an input-contract no-go for using the lift
manifests as-is; it is not a no-go for constructing targeted boundary-aware
roadmaps that might supply the missing incidence data more cheaply.

## Verification

Requirements for the complete suite are Python 3 plus `numpy`, `scipy`, and `sympy`; see [`requirements.txt`](requirements.txt). Many individual verifiers are standard-library only.

```bash
python3 run_all.py
python3 run_all.py --fast
python3 run_all.py --list-shards 4
python3 run_all.py --ci-delegated --shard 0/4
```

`run_all.py` discovers the repository's `verify_*.py` scripts and fails if a required replay fails. CI uses a deterministic weighted four-shard partition with an independently checked exact union/disjointness contract; the aggregate job retains the stable `verifier suite (complete)` name. Per-verifier progress is unbuffered, and each shard has a 120-minute allowance. Some verifiers regenerate committed artifacts, so a verification run can leave an informational working-tree diff.

Useful diagonal-three replays include:

```bash
PYTHONDONTWRITEBYTECODE=1 python ai/omreal/verify_diag3_pair_global_candidate_factors.py
PYTHONDONTWRITEBYTECODE=1 python ai/omreal/verify_diag3_pair_global_compactification_atlas.py
PYTHONDONTWRITEBYTECODE=1 python ai/omreal/verify_diag3_pair_global_face_bernstein_atlas.py
PYTHONDONTWRITEBYTECODE=1 python ai/omreal/verify_diag3_pair_relative_boundary_collapse.py
PYTHONDONTWRITEBYTECODE=1 python ai/omreal/verify_diag3_pair_fullsupport_safe_segment_walls.py
PYTHONDONTWRITEBYTECODE=1 python ai/omreal/verify_diag3_pair_fullsupport_block_symmetry.py
PYTHONDONTWRITEBYTECODE=1 python ai/omreal/verify_diag3_pair_fullsupport_parent_product_signs.py
PYTHONDONTWRITEBYTECODE=1 python ai/omreal/verify_diag3_pair_parent_source_block_labels.py
PYTHONDONTWRITEBYTECODE=1 python ai/omreal/verify_diag3_pair_parent_boundary_attachment.py
PYTHONDONTWRITEBYTECODE=1 python ai/omreal/verify_diag3_pair_parent_boundary_labels.py
PYTHONDONTWRITEBYTECODE=1 python ai/omreal/verify_diag3_pair_source_square_coverage.py
PYTHONDONTWRITEBYTECODE=1 python ai/omreal/verify_diag3_pair_source_block_cube_feasibility.py
PYTHONDONTWRITEBYTECODE=1 python ai/omreal/verify_diag3_pair_source_staircase_coverage.py
PYTHONDONTWRITEBYTECODE=1 python ai/omreal/verify_diag3_pair_full_hybrid_cube_topology.py
PYTHONDONTWRITEBYTECODE=1 python ai/omreal/verify_diag3_pair_source_staircase8_coverage.py
PYTHONDONTWRITEBYTECODE=1 python ai/omreal/verify_diag3_pair_source_family_incidence_no_go.py
PYTHONDONTWRITEBYTECODE=1 python ai/omreal/verify_diag3_pair_global_four_support_gate.py
PYTHONDONTWRITEBYTECODE=1 python ai/omreal/verify_diag3_pair_global_four_support_projection.py
PYTHONDONTWRITEBYTECODE=1 python ai/omreal/verify_diag3_pair_global_four_support_base_projection.py
PYTHONDONTWRITEBYTECODE=1 python ai/omreal/verify_diag3_pair_global_four_support_final_section_lift.py
PYTHONDONTWRITEBYTECODE=1 python ai/omreal/verify_diag3_pair_global_four_support_open_cell_v_lift.py
PYTHONDONTWRITEBYTECODE=1 python ai/omreal/verify_exact_semialgebraic_toolkit.py
PYTHONDONTWRITEBYTECODE=1 python ai/omreal/verify_run_all_ci_shards.py
PYTHONDONTWRITEBYTECODE=1 python ai/omreal/verify_diag3_completion_open_object.py
```

## Results index

| Area | Certified result / current state | Location |
|---|---|---|
| Maxout polytopes | **`max f₀(3,5)=42`**; `(4,4)` and `(4,6)` resolved; `(3,8)` achievability certified | [`ai/maxout/`](ai/maxout/) |
| OM mutation graphs | Connected for every uniform OM rank with `n <= 9`; corrected `(4,9)` class count | [`ai/omgamma/`](ai/omgamma/) |
| OM non-realizability | Minor-closure census, generic minimal obstructions, Proposition R | [`ai/omminor/`](ai/omminor/) |
| Mathematical prospecting | MP-002 exactly refutes transfer from minimum wall-event count to minimum alternation tails on a preregistered three-route holdout; the tail Pareto frontier has two routes | [`ai/scouting/MP002_BLOCK_ROUTE_TRANSFER.md`](ai/scouting/MP002_BLOCK_ROUTE_TRANSFER.md) |
| 9DVL / realizability | **2/9 proved**; the first two four-support domains have a complete local inventory of 527,533 base cells and 16,935,101 lifted cells with zero unresolved local `v` fibers; a proof-producing component-cosheaf pilot reproduces four certified fixtures, including a synthetic relative-infinity interface and the 399-cell first-event atlas, but the lift manifests still lack global closure, complete bad-signature labels, genuine infinity, and the global middle-rank replay; both diagonal-three invariant obligations remain open | [`ai/omreal/`](ai/omreal/) |
| SEEAT | Single-element extension atlas theorem; exact one-chart capacity 26,112; row-2599 atlas width bounded `7 <= width <= 178` | [`ai/omreal/SEEAT.md`](ai/omreal/SEEAT.md) |
| SAE absorption | Exact failures of feature-absorption identification | [`ai/absorption-metric/`](ai/absorption-metric/) |
| SAE identifiability | Conditional-rate and semantic-grounding non-identifiability results | [`ai/sae-unidentifiability/`](ai/sae-unidentifiability/), [`ai/sae-grounding/`](ai/sae-grounding/) |
| Interpretability | Exact minimal networks where common interpretability methods mislead | [`ai/interp-illusions/`](ai/interp-illusions/) |
| Optimizers | Exact scope failures/counterexamples for Muon/Lion-related claims | [`ai/optimizer/`](ai/optimizer/) |
| Jacobian aftermath | Exact consequences and minimal-degree results following the 2026 counterexample | [`jacobian/`](jacobian/) |

The adversarial review archive is in [`reviews/`](reviews/) and, for active 9DVL work, alongside the relevant [`ai/omreal/`](ai/omreal/) certificates.

## Certificate philosophy

A result belongs here when the gap between the mathematical claim and the machine check is small enough to audit. In particular:

1. numerical search may locate a candidate, but theorem claims are replayed exactly;
2. unresolved cases stay unresolved rather than being promoted by sampling;
3. generators and independent verifiers are separated where practical;
4. negative results, failed strategies, and scope limitations are recorded when they change the research frontier;
5. large raw corpora are avoided when a compact deterministic regeneration path or certificate is available.

The deliberate empirical exception is [`ai/coherence-transfer/`](ai/coherence-transfer/), which replicates a third-party empirical result and is labelled accordingly.

## Contributing

Pull requests are welcome. Refutations are especially valuable: if a certificate is wrong, demonstrating that is itself a useful result.

The standards for exact arithmetic, independent verification, controls, honest scope, and contributor credit are in [`CONTRIBUTING.md`](CONTRIBUTING.md).

Licensed under the [MIT License](LICENSE).
