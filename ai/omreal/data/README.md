# SEEAT certificate data

## Complete diagonal-two residual-pair classification

`DIAG2_PIVOT_pair_classification.npz` is the compact classification of all
`9,476` unordered relative-label residual-factor pair orbits.  It contains
the canonical anchor family, second factor ID, and certificate-mode code for
each orbit in the exact order reconstructed by
`DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY.py`.

SHA-256: `a12680b52ace15096437e5cbcfcbdb6d888c9d61a2bccf8a2d336fa5be6b7025`

| array | meaning |
|---|---|
| `pair_kind` | canonical first-factor orbit label |
| `pair_second_factor` | exact localized second-factor ID |
| `classification` | `0` residue, `1` primary minor, `2` alternate canonical frame, `3` full stabilizer frame, `4` translation, `5` torus |

The 122 mode-zero entries are not unresolved: the independent affine-fiber
checker reconstructs a stabilizer-equivalent graph presentation for every
one and proves the full `9,476/9,476` pair-wall theorem.

```console
python ai/omreal/verify_diag2_pivot_all_pair_fibers.py
```

## Parent-860 counterexample-guided routing pilot

`DIAG9_GRAPH_parent860_coordinate_star.npz` is the complete labeled roadmap
on the nine coordinate segments of radius `10^-4` through the normalized
exact parent-860 chart.  It stores 23 generic chamber labels, all 22 exact
residual root boxes, crossing-factor features, and the shortest disconnected
support witness.

SHA-256: `9274371ec45baee318cd160f931344f37dc5031acc13d63c16099534b8896f4b`

`DIAG9_GRAPH_parent860_coordinate_star_graph.npz` is the corresponding
23-vertex, 22-edge labeled tree quotient.

SHA-256: `b295cceb3d97477f9b8c874b3d22b6a09d13d79bc4d3fa5daf14156bd9a03f55`

`DIAG9_GRAPH_parent860_star_repair.npz` stores the 16 exact CEGIS chords,
their complete residual root isolation, the one new generic chamber label,
and the connected all-family support closure of the resulting network.

SHA-256: `f3ebf1f3a9b458663a12b042e68194aa24c4b55689cf85344e2d98f81aec3d11`

```console
python ai/omreal/DIAG9_GRAPH_parent860_star.py
python ai/omreal/DIAG9_GRAPH_parent860_star_repair.py
```

These files are exact on their embedded one-dimensional network.  They do not
certify coverage of the full parent realization cell.

`seeat_parent2599_realizations.npz` is the compact certificate refuting the
proposed four-chart bound for `UOM(4,8)`.  It contains:

SHA-256: `ed70d5fbcd18f76036223c3977bea59594f64a009fa73632f088b7d0011d9f91`

| array | meaning |
|---|---|
| `format` | scalar string `seeat-parent2599-realizations-v1` |
| `parent_index` | scalar `2599`, indexing `ai/omgamma/data/cat_4_8.txt` |
| `key_hi`, `key_lo` | the 5,902 canonical `(4,9)` child keys |
| `multiplicity` | how many of the parent's 97,224 labeled extension signatures map to each key |
| `matrix` | one exact integer `4x9` realization per child key |

The artifact is not trusted as metadata.  The verifier independently
enumerates all abstract extensions of the parent, canonicalizes them with
`coverage_checker.py`, checks the key set and every multiplicity, and
recomputes all 126 determinants of every matrix in integer arithmetic.

```console
python ai/omreal/verify_four_chart_obstruction.py
```

The realization search can be reproduced separately; its floating-point work
is outside the trust boundary.

```console
python ai/omreal/build_four_chart_obstruction.py --workers 4 --force
```

## Explicit 178-chart upper cover

`seeat_parent2599_upper178.npz` is the complementary exact upper-bound
certificate for the same parent.  It proves that 178 fixed realizations cover
all 97,224 extension signatures.

SHA-256: `3b90799d26b7783e92c2ac697eaaf8b76d26a787f53205873b997657e114180a`

| array | meaning |
|---|---|
| `format` | scalar string `seeat-parent2599-upper-cover-v1` |
| `parent_index` | scalar `2599`, indexing `ai/omgamma/data/cat_4_8.txt` |
| `chart_matrix` | 178 exact integer `4x8` parent realizations |
| `assignment` | for each of the 97,224 signatures, the index of a covering chart |
| `point` | one exact integer 4-vector realizing that signature over its assigned chart |

The certificate does not ask the verifier to trust chamber enumeration or the
heuristic set-cover search.  The checker independently enumerates the
signatures, verifies all 70 parent brackets of every chart, and verifies all
56 derived-bracket signs of every assigned extension point.

```console
python ai/omreal/verify_seeat_upper_bound.py
```

## Chromatic lower-bound certificates

`seeat_parent2599_k6.npz` is the 3.7-KB fast canary proving that five charts
do not suffice.  It contains six exact realizable extension signatures and a
branch-free Grassmann--Pluecker contradiction for each of their 15 pairs.
The six vertices therefore form a clique in the universal nonamalgamation
graph.

SHA-256: `dda21956b807c19c1cdbb44f3bd326874c9e83d12cdc16eaa5bc1ab19ff281e5`

```console
python ai/omreal/verify_seeat_k6.py
```

`seeat_parent2599_width7.npz` is the full 68-KB chromatic certificate.  It
contains:

| array group | meaning |
|---|---|
| parent, signatures, matrices, points | 220 exact realizable extensions of row 2599 |
| graph edges | 3,472 proposed universal incompatibilities |
| GP traces | 64,698 branch-free propagation steps ending in one contradictory GP relation per edge |
| positive control | a complete satisfying 28-sign two-element amalgam |
| coloring proof | a six-clique symmetry breaker and a 14,791-node exhaustive six-color refutation tree |
| `coloring7` | an explicit proper seven-coloring of the graph |

Thus the certified graph has chromatic number exactly seven.  Every chart is
an independent set in this graph, so the parent atlas width is at least seven.

SHA-256: `ec7ef2ad9f37467e00a5ea739d67f90c4c53b304f4d82d47ac72591a58477dc7`

```console
python ai/omreal/verify_seeat_width7.py
```

Both certificates embed their exact realization witnesses.  Their negative
claims use only uniform chirotope GP signs; sampled charts are not part of the
trust boundary.

## Exact eight-coordinate chart-support cube

`seeat_parent2599_shatter8.npz` certifies that the raw chart-support concept
class for row 2599 shatters eight extension signatures.  It contains one
exact `4x8` parent chart for each of the 256 binary patterns, an integer
strict-cone witness for every supported bit, and nonnegative integer Gordan
weights for every unsupported bit.

SHA-256: `d01a03e3222de5b760fd7fec36c03ccbeac820ed1ce7ea47f93001abaf3aadcb`

```console
python ai/omreal/verify_seeat_shatter8.py
```

This certificate concerns raw support states.  It does not assert that the
maximal faces of the compatibility complex shatter the same coordinates and
therefore does not, by itself, lower-bound feasible-COM completion rank.

The same exact artifact supplies a prototype for the Gordan--Koszul reduction
in `ATLAS_HELLY.md`.  On its pattern-zero chart, the following checker proves
that all eight stored infeasibility witnesses are support-minimal positive
circuits in
`ker(Lambda^3 Y)=ker(Y) wedge Lambda^2(Q^8)`, and classifies all of their
four-row cofactors by the 52 derived-wall orbits.

```console
python ai/omreal/prototype_koszul_circuits.py
```

The signed generic-circuit checker applies the single-element-extension
Grassmann--Pluecker axiom and the exact derived-wall factorization before any
CAD.  It proves that all generic three-support pieces are empty, classifies
the six generic structural four-support types and their localization
cofactors, reduces the 73 unsigned shear-rigid `4+4` support-pair orbits to 39
coarse signed types, and then proves that the pencil minimum-degree condition
kills every generic `4+4` pair.  An exact shear-rigid positive pair on the
pattern-zero chart shows why the stronger pencil condition is necessary; it
is not a second-diagonal survivor.
Its reported 95.5-percent unit-XOR rejection rate concerns only the eight
prescribed signatures in this artifact; it is not a universal density
estimate.

```console
python ai/omreal/verify_signed_circuit_filter.py
```

The size-five signed checker classifies all `2,021,992` generic supports by
their number of residual cofactors, rejects the 370,552 all-unit supports,
and verifies exact pencil-rigid positive survivors of both types `4+5` and
`5+5`.  The exhaustive C++ verifier then counts the retained pencil-rigid
support-pair orbits under `S_8` and stratifies them by the exact weight-gauge
modulus `beta`: `4,260` of type `4+5` and `3,810,812` unordered of type
`5+5`.

```console
python ai/omreal/verify_signed_heavy_filter.py
g++ -O3 -std=c++17 ai/omreal/verify_signed_pencil_orbits.cpp -o /tmp/verify_signed_pencil_orbits
/tmp/verify_signed_pencil_orbits
```

Positive parent-column rescaling acts linearly on logarithmic ratios of the
stored Gordan weights.  The exact weight-gauge checker constructs the centered
incidence matrix, verifies
`beta=sum_j(|Q_j|-1)-rank(D)`, and produces primitive balanced exponent vectors
for all invariant Laurent monomials on the 65 pencil-rigid pair occurrences
in the 256 exact charts.  Zero-weight simplex faces are handled as smaller
supports.

```console
python ai/omreal/verify_gordan_weight_gauge.py
```

The artifact also contains sharp fixed-deletion tests for the common-light
exit lemma in `ATLAS_HELLY.md`.  One pair of proper incomparable signatures
has a two-component residence exit, while one proper signature has a connected
exit with first Betti number one.  The checker derives the circuit-cone
inequalities, enumerates every normalized residence vertex over the rationals,
builds the exit-facet nerves from exact face intersections, and computes their
homology without LP or floating-point arithmetic.

```console
python ai/omreal/verify_common_light_exits.py
```

The simultaneous-shear checker proves the common-apex rank-three convexity
mechanism on exact circuits, gives an exact nonconvex two-apex shear slice,
and verifies nine distinct realizable proper signatures with simultaneous
positive circuit pieces at one parent chart.  Every prefix of lengths two
through nine is pencil-rigid and support-plane rigid at that chart.  The last
condition is only an obstruction to plane-preserving shears; it does not
certify a compact component or nonzero compact-support cohomology.

```console
python ai/omreal/verify_simultaneous_shears.py
```

The fourth-diagonal checker reuses the same exact eight-shatter artifact.  It
selects four signatures, verifies all sixteen support patterns, and checks
their positive support-minimal circuits and pencil-rigid prefixes.  Its
independent finite census verifies that every Gordan support of at most five
triples on seven labels has a degree-at-most-two escape label, and reduces the
generic eight-label `H_c^3` single-piece source from `2,021,992` supports in
`117` orbits to the `1,099,560` cover-all supports in `66` orbits.  These are
the certified premises of the direct parent-`H_5` theorem and the fivefold
fourth-diagonal reduction; the retained intersection is a no-go for
incidence-only pruning, not a nonzero-cohomology claim.

```console
python ai/omreal/verify_fourth_diagonal_reduction.py
```

## Exact contraction-fiber nonconvexity

`seeat_parent2599_residence_nonconvex.npz` gives two integer positions of one
deleted row-2599 parent column that support the same extension signature, and
proves with a positive Gordan dependence that their vector midpoint does not.
All three positions independently reproduce the parent chirotope.  The two
positive extension witnesses and the midpoint dependence are checked using
integer arithmetic only.

The verifier derives a second extension column as the difference of the two
endpoints.  It proves that this column has one strict uniform signature over
the endpoints and midpoint, and that contracting it makes all three parent
charts identical; after positive projective scaling, the third lift is the
literal midpoint in that one contraction-height fiber.  Two additional exact
charts, strict witnesses, and sparse Gordan dependences prove that the two
extension regions are proper and incomparable.

SHA-256: `a7c4e85b4be56c078b96c6f6ff0a314c3daf5abc382fa76fdc1da4b7177645a6`

```console
python ai/omreal/verify_seeat_residence_nonconvex.py
```

The same certificate also supports an exact double-contraction regression
test.  Along the affine family `e(u)=2R+u(L-R)`, contracting the first
extension and one fixed parent column gives a constant uniform rank-two
quotient.  The second signature is feasible at the two ends, while exact
Bernstein coefficients keep one positive Gordan circuit throughout
`1/2<=u<=3/2`.  This proves a disconnected line slice of the projected model,
not disconnection of the full double-lift fiber.

```console
python ai/omreal/verify_double_contraction_gap.py
```

The certificate rules out an ordinary convex-Helly proof applied fiberwise
after deleting one parent element and rules out naively iterating the
contraction--height proof for a pair.  It does not disprove the 8--9--10
Extension--Helly Conjecture.

## Exact ninth-diagonal stress path

`ninth_candidate_12_37_path.npz` certifies that charts 12 and 37 of
`seeat_parent2599_upper178.npz` lie in one connected component of the common
feasibility locus of nine displayed extension signatures.  The path consists
of 22,711 rational segments: 11,701 one-column updates from chart 12, a
3,009-segment bridge, and the reverse of 8,001 updates from chart 37.

Every segment changes one homogeneous column.  All parent and extension
determinants affected by that segment are therefore affine, so exact strict
positivity at its two endpoints proves strict positivity throughout.  The
verifier reconstructs both endpoint incidences, replays every update using
integer determinants, and independently checks the intervening positive
projective gauge changes.

SHA-256: `8db38e00d9bf8701558c27cd4ede3e024db8953ea3ef9873bf0b4fc65ad6bcda`

```console
python ai/omreal/verify_ninth_candidate_path.py
```

By itself, this artifact refutes only a separator suggested by the finite
178-chart sample.  It does not prove the ninth diagonal or coordinate
reachability for every parent cell.  Its companion below supplies the
separate global properness/incomparability proof for the nine regions.

`ninth_candidate_12_37_antichain.npz` supplies the separate global
properness/incomparability audit for the same nine signatures.  It contains
seven row-2599 chart indices and, for each of their 63 chart/signature
entries, either an integer feasible extension ray or a support-at-most-five
positive integer Gordan relation.  The seven exact feasibility patterns
contain both values in every column and distinguish all 72 ordered pairs.
Thus every region is nonempty and proper, and neither region in any pair
contains the other.

SHA-256: `11ca66549982ec40ce8425d2caed45b418edb73c4eb415a45b39d57e481bd1e4`

```console
python ai/omreal/verify_ninth_candidate_antichain.py
```

Together, the two certificates prove that a genuine proper size-nine
antichain has the displayed charts 12 and 37 in one common-feasibility
component.  They do not prove that this whole common locus, or every
ninth-diagonal common locus, is connected.

## Second exact ninth-diagonal stress path

`ninth_candidate_37_176_path.npz` is an independent stress test selected
after enumerating the 26,112 derived-arrangement topes on each of the 178
stored row-2599 charts.  It joins charts 37 and 176 inside the common
feasibility locus of a different nine-signature family by 22,811 exact
rational one-column segments: 11,701 updates from chart 37, a 3,009-segment
bridge, and the reverse of 8,101 updates from chart 176.

SHA-256: `3c37c3c0d5de159bec9d48eeaaf57bccbe07c2f3aeb0ede9d4b1ddbae2bd3507`

`ninth_candidate_37_176_antichain.npz` independently proves that the same
nine feasibility regions are nonempty, proper, and pairwise incomparable.
Seven exact charts distinguish all 72 ordered region pairs; every one of the
63 entries carries either an integer extension ray or a positive integer
Gordan circuit.

SHA-256: `fe7bb166b5a151262c665875d32de49d7e8a330cf11b26609458af6b2661a59f`

```console
python ai/omreal/verify_ninth_candidate_generic.py antichain \
  ai/omreal/data/ninth_candidate_37_176_antichain.npz
python ai/omreal/verify_ninth_candidate_generic.py path \
  ai/omreal/data/ninth_candidate_37_176_path.npz
```

This second family again refutes only a separator in the finite chart sample.
It is not evidence that the 178 charts form a chamber roadmap and does not
prove the ninth diagonal.

## Exact row-2599 coordinate-line roadmap

`DIAG9_GRAPH_row2599_line_roadmap.npz` is the first geometrically complete
labeled residual roadmap on a scoped subset of a parent realization space.
For the exact line `Y(t)=Y_0+t E_(2,7)`, `-1/2<t<1/2`, it stores disjoint
Sturm isolating intervals for every residual root, the 25 exact crossing
parameters, and the complete signature labels of the resulting 26 cells.
All 84,840 residual determinant occurrences are covered.  Every cell supports
26,112 signatures, the union supports 26,232, and every signature support is
empty, full, a prefix, or a suffix.

SHA-256: `29a4542941a322da6846fcfb2d7eb3d427ac9f7cc4becd95b4b5cd754f3ae16b`

`DIAG9_GRAPH_row2599_line_graph.npz` is the corresponding 26-vertex path
quotient with its 50 nonconstant proper support rows.  It passes both the
sharp pairwise-width tree theorem and the complete cut-SAT test.

SHA-256: `e1c2b82b4da6b2180d1de7e5837d2a58da4dadf159b4631fa4b2810e42df52a5`

The two-cell regression files isolate the exceptional crossing with 65
labeled determinant occurrences:

- `DIAG9_GRAPH_row2599_slice_roadmap.npz`, SHA-256
  `b982fdc600729306b545005ff059e2c6603b4603525745078fd85b630f36a575`;
- `DIAG9_GRAPH_row2599_slice_graph.npz`, SHA-256
  `c0521f59aac563a4d7cbcd0405e90a3d4ae26fcf7b9239c9bfce296c6e031b1b`.

```console
python ai/omreal/DIAG9_GRAPH_verify_row2599_slice.py
python ai/omreal/DIAG9_GRAPH_verify_row2599_slice_jacobian.py
python ai/omreal/DIAG9_GRAPH_verify_row2599_line.py
python ai/omreal/DIAG9_GRAPH_verify_tree_certificate.py \
  ai/omreal/data/DIAG9_GRAPH_row2599_line_graph.npz
python ai/omreal/DIAG9_GRAPH_cut_sat.py \
  ai/omreal/data/DIAG9_GRAPH_row2599_line_graph.npz
```

The 65 gradients have exact rank one and are transverse to the line.  The
separate global-factor certificate below now proves that these 65 occurrences
share one primitive residual polynomial after parent-bracket localization.
The roadmap is nevertheless complete only on this line.  Higher-dimensional
residual roadmaps and then full nine-dimensional coverage remain necessary
for the ninth diagonal.

`DIAG9_GRAPH_row2599_disk_roadmap.npz` upgrades the exceptional crossing to
the embedded projective square
`W(s,u)=W+s E_(2,7)+u E_(1,7)`, `|s|,|u|<=1`.  All 65 center restrictions
share one exact primitive linear gcd on this plane, all quotients are
nonvanishing, and every other residual restriction and parent bracket is
certified nonzero on the full square.  It stores the resulting two convex
cells and their common wall segment.

SHA-256: `8111a338e2169c4492ad0c5b7e03c9792d5c301c54f0f10a3ce20114db424486`

`DIAG9_GRAPH_row2599_disk_graph.npz` is the corresponding labeled two-cell
graph certificate.

SHA-256: `c0521f59aac563a4d7cbcd0405e90a3d4ae26fcf7b9239c9bfce296c6e031b1b`

```console
python ai/omreal/DIAG9_GRAPH_verify_row2599_disk.py
```

This proves one wall branch on the chosen plane.  The global-factor census
below independently identifies it as the restriction of one common
irreducible residual factor in all nine projective coordinates.  A disk with
two coprime branches is the next local roadmap test.

`DIAG9_GRAPH_row2599_node_roadmap.npz` supplies that two-branch test.  It is a
rational projective disk around a transverse node of two coprime residual
factors.  Exactly `65+65` labeled occurrences lie on the branches, their
Jacobian has rank two at the center, and exact dominance certificates exclude
every other residual and parent wall from the disk.  The roadmap has four
open cells, four wall arcs, and one node, with exact tope counts
`4x26,112`, `4x26,040`, and `25,968` respectively.  All finite common
signature supports are empty or connected on the disk.

SHA-256: `ddec96b052b305d279b543be2af27e12f380f0dedc79ea434616c64b40cd8cea`

`DIAG9_GRAPH_row2599_node_graph.npz` is its exact four-cycle chamber graph;
both the sharp tree theorem and complete cut-SAT check pass.

SHA-256: `b7f48c4f4f421ba88cf551a2ba16cbd024d63d0910ada701118c88e2e2b7e19f`

```console
python ai/omreal/DIAG9_GRAPH_verify_row2599_node.py
python ai/omreal/DIAG9_GRAPH_verify_tree_certificate.py \
  ai/omreal/data/DIAG9_GRAPH_row2599_node_graph.npz
python ai/omreal/DIAG9_GRAPH_cut_sat.py \
  ai/omreal/data/DIAG9_GRAPH_row2599_node_graph.npz
```

This is the first exact codimension-two local roadmap.  It is not a cover of
the full parent realization cell.

`DIAG3_PAIR_MASTER_CLOSURE_MULTIBOX_CANARY.json` refines a strict
branch-coordinate subdomain of that disk into a declared `3 x 3` box atlas.
It records four no-wall boxes, four one-wall boxes, one transverse two-wall
box, 32 atomic boundary sign words, an 81-cell regular-CW closure and complete
signature-profile labels.  Its independent verifier reconstructs the exact
geometry and all 216 barycentric profile-triple ranks and rejects ten hostile
corruptions.  The outer boundary and internal seams are ordinary cells; the
parent-infinity subcomplex is empty.

```console
python ai/omreal/build_diag3_pair_master_closure_multibox_canary.py
python ai/omreal/verify_diag3_pair_master_closure_multibox_canary.py
```

This is a local gluing-method canary, not global row-2599 coverage.

`DIAG3_PAIR_MASTER_CLOSURE_FIRST_EVENT.json` expands the same exact parent
plane to the declared 64-box ceiling and crosses the first residual event
outside the original two-branch disk.  Exact source replay identifies the
unique new affine occurrence at derived rows `(2,8,22,49)` and proves every
other residual event factor and all 70 parent brackets nonzero on the domain.
The 64 boxes comprise 42 no-wall, 20 one-wall and two transverse two-wall
boxes.  Their 171 boundary words glue to a 399-cell regular-CW atlas whose
399/1118/720 barycentric complex has zero middle residue for all 512 ordered
signature-profile triples.  Thirteen hostile mutations are rejected.

```console
python ai/omreal/build_diag3_pair_master_closure_first_event.py
python ai/omreal/verify_diag3_pair_master_closure_first_event.py
```

This proves that the compiler crosses one genuinely new wall without
projection growth.  It is still a local two-dimensional theorem, not a cover
of the nine-dimensional row-2599 parent cell.

`DIAG3_COMPONENT_COSHEAF_PILOT.json` compiles the relative schema,
transverse-node, multibox, and first-event fixtures into explicit component
records, specialization maps, signed `d^2=0` checks, and exact mod-two and
rational pair-to-triple rank histograms.  The synthetic schema fixture retains
one declared relative-infinity cell and tests the quotient interface; it is
not a geometric parent-divisor certificate.  The other three fixtures declare
empty parent-infinity subcomplexes.
Its producer-independent verifier recomputes the first 8+216+216 ranks and
authenticates the accepted 512-case first-event replay; it rejects fourteen
re-sealed mutations.  All tested intersections have at most one component, so
nontrivial split--merge behavior remains an explicit unexercised gate.  The
certificate records 177 intersections, 406 maps, zero disconnected
intersections or many-to-one maps, and 75 intersections with nonzero two-cell
rank (maximum 90).  The same artifact authenticates the
completed two-support lift counts and fails closed because those manifests do
not expose the closure, complete labels, or infinity contract.  This is only
an input-contract no-go for using the manifests as-is, not a no-go for
constructing targeted boundary-aware roadmaps.

```console
python ai/omreal/build_diag3_component_cosheaf_pilot.py
python ai/omreal/verify_diag3_component_cosheaf_pilot.py
```

`DIAG3_PAIR_FULLSUPPORT_SEGMENT_COVER.json` is the exact target-selection and
source-skeleton successor. It proves that both proposed component-cosheaf
stress stars lie on proper supports and therefore add zero generators to the
relative chain complex. On full support it reduces the 105 certified
parent-safe source segments to an optimal 40-edge cover with one exact retained
endpoint witness for each of 10,844 crossed factor classes.
Unique-crossing factors force 34 edges; exhaustive replay of seven maximal
optional incidence patterns proves that six additional edges are necessary and
sufficient. There are 3 maximal-pattern covers and 28 raw six-edge optional
covers. The verifier independently reproduces 412,093 original and 157,448
retained edge-factor incidences, rechecks all parent brackets and exact endpoint
witnesses, and requires a full-record semantic seal. It shares declared,
hash-pinned accepted upstream source modules with the producer; it does not
claim full raw-source independence, global wall-component coverage, or
parent-cell coverage.

```console
python ai/omreal/build_diag3_pair_fullsupport_segment_cover.py
python ai/omreal/verify_diag3_pair_fullsupport_segment_cover.py
```

`DIAG3_PAIR_FULLSUPPORT_COMPONENT_COLLAR.json` is the first exact
missed-component pilot on a proof-bearing full-support wall.  A deterministic
rule selects factor 19069, the degree-six, 108-monomial factor uniquely
witnessed by retained edge 39.  All seventy parent brackets are strictly
positive on an embedded rational two-dimensional collar, and exact
tensor-Bernstein inequalities make the wall one monotone graph.  Its single
component meets edge 39 and both artificial collar ends.  The stored 17-cell
regular-CW roadmap has complete closure chains, signed incidence with
`d^2=0`, and empty parent infinity.  The separately embodied structural
verifier hard-pins and exactly authenticates the c692 segment cover and rejects
twenty re-sealed hostile semantic mutations, including coupled cover/collar
substitution.  Producer and
verifier share the transition, safe-wall, parent-gate, labelled-factor, and
Sturm modules plus near-parallel exact substitution/Bernstein logic; full
implementation independence is not claimed.  An external SymPy reconstruction
was an additional review audit, not a persisted repository verifier.  This is
complete only on the declared collar; global components outside it and all
extension-signature labels remain open.

```console
python ai/omreal/build_diag3_pair_fullsupport_component_collar.py
python ai/omreal/verify_diag3_pair_fullsupport_component_collar.py
```

`DIAG3_PAIR_FULLSUPPORT_LABELED_SKELETON.json` and the deterministic packed
profile catalog `DIAG3_PAIR_FULLSUPPORT_LABELED_SKELETON_PROFILES.json.gz`
compile selected minimum-cover edge 27 (row-2599 charts 0 to 89) into 1,239
stable zero-cells, 1,238 oriented one-cells, all 2,476 strict faces, empty true
parent infinity, and the complete 97,224-signature/2,458-profile bad-membership
contract.  The artifact fails closed on the other 39 cover edges, listing each
missing regular refinement explicitly; this is source-skeleton coverage only,
not parent-cell or component coverage.  Profile IDs are assigned by the
canonical lexicographic order of feasible-cell bitmaps.  The independent
verifier hard-pins the accepted cover/transition/labels, checks the label-to-
transition SHA-256 cross-pin and every event factor/multiplicity, and rejects
16 hostile corruptions including re-sealed coupled-dependency and profile-ID
permutation attacks.

```bash
python ai/omreal/build_diag3_pair_fullsupport_labeled_skeleton.py
python ai/omreal/verify_diag3_pair_fullsupport_labeled_skeleton.py
```

`DIAG3_PAIR_PARENT_SOURCE_TRANSITION_0_89.json` is the complete exact residual
roadmap on the minimum-Hamming certified parent-safe segment leaving chart 0.
It proves that all 70 parent brackets remain strict, screens all 17,824
candidate factors by exact Sturm counts, and orders 1,237 rationally isolated
sign crossings.  Replaying those flips reconstructs the stored chart-89 factor
state.  The path has 2,477 regular-CW cells, 1,179 single-occurrence events and
58 compound events.  It does not by itself claim global parent-cell coverage.

```console
python ai/omreal/build_diag3_pair_parent_source_transition.py
python ai/omreal/verify_diag3_pair_parent_source_transition.py
```

`DIAG3_PAIR_PARENT_SOURCE_LABELS_0_89.json` continues the complete 26,112-tope
label set across all 1,238 open chambers of that path.  It applies exact
antipodal simplicial mutations at all 1,179 single-occurrence events and
re-enumerates the arrangement only after the 58 compound events.  The final
state equals the independently stored raw chart-89 labels.  The 97,224
extension signatures give 2,458 path profiles, with feasibility-transition
census `87208, 9490, 512, 14` for zero through three changes.  This is complete
one-path label continuation, not global row-2599 coverage.

```console
python ai/omreal/build_diag3_pair_parent_source_labels.py
python ai/omreal/verify_diag3_pair_parent_source_labels.py
```

`DIAG3_PAIR_PARENT_SOURCE_BLOCK_BRIDGE_0_152.json` is the first exact source
bridge beyond the 105-edge straight forest.  It audits that forest's 73
components and selects chart 152 among six direct block-bridge candidates by
minimum three-segment length and then minimum endpoint factor-state Hamming
distance.  Replacing moving columns 6, 7 and 8 one at a time keeps all 70
parent brackets strict and connects chart zero to a previously isolated germ.

All 17,824 factors are screened on each segment.  The certificate records
5,612 ordered simple crossings, a reconstructed chart-152 factor state, an
11,231-cell regular-CW path, and exact overlap with the existing labelled path
at chart zero.  It does not claim global parent-cell coverage or parent
infinity.

```console
python ai/omreal/build_diag3_pair_parent_source_block_bridge.py
python ai/omreal/verify_diag3_pair_parent_source_block_bridge.py
```

`DIAG3_PAIR_PARENT_SOURCE_BLOCK_LABELS_0_152.json` continues all 26,112
extension labels across the bridge's 5,612 residual events. It records 5,319
antipodal simplicial mutations, 293 exact compound re-enumerations, 5,615
generic chamber label digests, two preserved equal-label waypoint seams and
9,326 complete signature profiles. The replay reconstructs the independently
stored raw chart-152 tope set and rejects 12 hostile corruptions.

```console
python ai/omreal/build_diag3_pair_parent_source_block_labels.py
python ai/omreal/verify_diag3_pair_parent_source_block_labels.py
```

`DIAG3_PAIR_PARENT_BOUNDARY_ATTACHMENT_89_1237.json` is the first exact source
attachment to genuine parent infinity. It selects the unique parent-safe finite
coordinate ray from labelled charts 0, 89 and 152, proves that `[1237]` alone
vanishes while 69 parent brackets remain positive, isolates 1,517 residual
crossings, and proves that no candidate residual factor vanishes at the
endpoint.

`DIAG3_PAIR_PARENT_BOUNDARY_LABELS_89_1237.json` transports the complete label
set through all 1,518 open-ray chambers using 1,454 simple mutations and 63
compound re-enumerations. It independently reconstructs the last incident
chamber near the endpoint and places `[1237]=0` in the relative infinity
subcomplex.

```console
python ai/omreal/build_diag3_pair_parent_boundary_attachment.py
python ai/omreal/verify_diag3_pair_parent_boundary_attachment.py
python ai/omreal/build_diag3_pair_parent_boundary_labels.py
python ai/omreal/verify_diag3_pair_parent_boundary_labels.py
```

## Exact global residual-factor census

`DIAG9_GRAPH_global_factor_census.npz` localizes all 84,840 labeled residual
determinant occurrences by the 62 nonconstant parent brackets and stores the
resulting 26,740 primitive factor classes.  Their exact multiplicities are
`25,200 x 1`, `420 x 2`, `280 x 15`, and `840 x 65`.  The certificate also
stores the occurrence-to-factor map, stripped bracket units, the old
65-occurrence crossing, and its common global factor.

SHA-256: `3984ce87e11fd59d804e59568177248e218cd1c7bb07aae0a9f9f746858728bc`

Semantic SHA-256:
`8dd371e34f9af178c49d4d0152864a394a0b2defcf16e673ddf885feb6ec0071`

```console
python ai/omreal/DIAG9_GRAPH_global_factor_census.py
```

The replay re-expands every determinant and parent bracket over exact
rational arithmetic and verifies the stored localization identities.  The
factor census is not a chamber roadmap.

## Exact row-2599 factor states

`DIAG9_GRAPH_row2599_factor_states.npz` evaluates one exact determinant
representative of every global factor on all 178 stored row-2599 charts.  It
stores the packed `178 x 26,740` sign matrix, factor traces, the 10,844
varying factor IDs, and the complete pairwise Hamming-distance matrix.  All
178 states are distinct, with distances from 1,125 through 5,600.

SHA-256: `f44b1fccfb4e61273aeceb8796a18098d82c48473e257556ce3d2a22f99b0bcf`

Semantic SHA-256:
`ab4aeed6eab31d6f4bfa68894b52e8086910076a25d7c7416c806f0529df8f0b`

```console
python ai/omreal/DIAG9_GRAPH_row2599_factor_states.py
```

This proves at least 178 residual sign chambers and at least 10,844 factors
meeting the row-2599 realization cell.  It does not certify adjacency or
coverage.

## Diagonal-two escape sets on all 178 stored charts

`DIAG2_ESCAPE_SET_atlas178_summary.json` stores the exact per-chart summaries
from the complete moving-witness escape-set replay on the same 178 row-2599
charts.  For each chart it records the semantic digest of all 71,112 bad-
signature masks, the minimum mask size and multiplicity, and an exact pair
witness attaining the minimum intersection.  Every one of the
12,657,936 reconstructed masks belongs to a pairwise-intersecting family;
the global minimum mask size is 53 and the global minimum pair overlap is 6.

SHA-256:
`1417b3f1172c469e8072b418f878e5875a29d40a3fe6fe6a404f384aa6c8b36d`

Semantic SHA-256:
`d255845e6b246865ed3c50a61c001ec8701d3b22fffd218087d955ac0854d111`

```console
python ai/omreal/verify_diag2_escape_set_atlas178.py --workers 8
```

The checker recomputes every mask and verifies the stored summary.  As with
the source chart bank, this is an exact point-sample theorem, not a residual-
chamber coverage certificate and not a promotion of diagonal two.

## Diagonal-two overlap-at-most-eight atlas

`DIAG2_NEAR_COUNTEREXAMPLE_atlas8.json.gz` stores every antipodal
bad-signature pair orbit with escape overlap at most eight at the exact
representative of each of the 2,604 realizable parent chirotopes.  There are
1,154 pair orbits in 875 parents, representing 4,616 raw pairs, with overlap
histogram `{6: 212, 7: 50, 8: 892}`.  The record digests are cross-checked
against the complete all-parent screen.

SHA-256:
`73983fbd9eb1a6765ba815af1c3e6af401a235919643903de7ef62a80e8013a1`

Semantic SHA-256:
`377ca807cd8a3034677638ed55431ef83cce4cffa237834f3c530ec838f742ee`

```console
python ai/omreal/verify_diag2_near_counterexample_atlas.py
```

The default replay validates the complete artifact and reconstructs three
sentinel parents exactly.  A `--full` run reconstructs the complete atlas.
This is an exact point transversal, not realization-chamber coverage.

## Diagonal-two near-pair separator profiles

`DIAG2_NEAR_COUNTEREXAMPLE_separators8.json.gz` stores the exact
inclusion-minimal source-local separator profiles of all 2,307 distinct
near-pair endpoint signatures.  Its 27,684 minimal separators are all
singletons: every endpoint has exactly four mutation triples and twelve
source-local occurrences.  The artifact also stores each retained pair's
eight sourcewise common-escape masks.

SHA-256:
`3010b3fbbdb3e914ffb4d7843f92f9162853c2ecb2b7d9e076e68f8ce31c4ad1`

Semantic SHA-256:
`543fed1a543f9a596e243548c2d05b0b3f4f20da5d82116f3136b1936413a16e`

```console
python ai/omreal/verify_diag2_near_counterexample_separators.py
```

The default replay validates the complete artifact and exactly reconstructs
three sentinel parents.  The separator census has the same point-sample scope
as the near-pair atlas.

## Diagonal-three compact Morse certificates

`DIAG3_morse_unit_minor_certificates.bin` stores 65,550 exact role-frame
Jacobian-minor identities.  Each record gives the original factor triple,
one of the 1,120 role-frame indices, three minor columns, the sign, and the
parent-bracket product.  Exactly 79 frames carry witnesses; the exhaustive
screen's last first witness is frame 815.

SHA-256:
`afe01d6d94bc4b8ce133cbe0d14ceb01d9dd72514f9ed7a59b73d5f6b4299734`

`DIAG3_triangular_features.bin` stores the zero-coordinate and exact
parent-unit-derivative masks used to remove 12,333 union-degree-four triples
before the role sweep.

SHA-256:
`7fae9da26cf7391d2dc3b00e55faabdf4556d4badc9a2f8c4ace3ecc29d7f136`

```console
python ai/omreal/verify_diag3_projective_column_fiber_scan.py --morse-only
```

Passing `--morse-union4` with the exported union-degree-four bucket also
rechecks every positive triangular feature, regenerates the pinned
1,885,400-row source, and verifies that all compact Morse records lie in it.
The compact 79-frame artifact proves only its positive closure count; the
claim of maximality for this unit-minor screen comes from the separate full
1,120-frame exhaustion.  The checker records that construction accounting
but does not present it as a replay of the negative search.

`DIAG3_frame1119_constant_shear.json` stores 61 additional exact identities
from signed sums and differences of coordinate minors sharing two columns in
role frame 1119.  The records are distinct in original orbit coordinates and
the checker proves that all 61 fail every affine reframe, have minimum
support-union degree four, fail the triangular test, and are disjoint from
the 65,550 compact Morse records.  This is a one-frame positive artifact, not
an exhaustive constant-`GL9` scan.

SHA-256:
`1cece61ff1a551faaeefc0062267e24266d264d9e19748d40fa5a74db9ce0be3`

```console
python ai/omreal/verify_diag3_frame1119_constant_shear.py
```

`DIAG3_triple_sequential_affine_certificates.bin` stores the `180,886`
positive parent-unit graph plus square-affine-fiber witnesses in the next
triple layer.  The independent verifier reconstructs every label action,
canonical alignment, stabilizer transport, graph equation, parent-unit
slope, and jointly affine residual pair without importing the census
builder's masks.

SHA-256:
`7e9ad80ae55c1f51dda7f7dc584dac8eefe41197124914cb83aab3cf0a2b719e`

```console
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/verify_diag3_triple_sequential_affine_certificates.py
```

`DIAG3_triple_unit_minor_after_graph_certificates.bin` stores `234` exact
type-49/pivot-3 target-pair identities.  Each record gives a fixed two-by-two
Jacobian minor of the two cleared graph-restricted residual equations and its
complete signed product of graph-restricted parent brackets.  These positive
identities map to `117` rows of the sequential-affine residue.  The artifact
does not claim an exhaustive unit-minor search.  Exactly `97` of the `117`
rows also occur in the pivot-3 double-graph certificate below, while none
occurs in its pivot-1/5 extension. The artifact still adds only `20` rows
after the complete positive double-graph union; their exact combined union
closes `417,848` rows and leaves `1,221,055`.

SHA-256:
`9889d40c9fdc4c23817a28e94b311cec1673b4e4dfd3e072dace17ff49ffd97a`

```console
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/verify_diag3_triple_unit_minor_after_graph.py
```

`DIAG3_pair_tapered_ribbon.json` stores the compact factor order and exact
three-signature statuses needed to reconstruct the two-dimensional tapered
normal-slice ribbon.  It intentionally omits the algebraic root isolators,
which are already checked by the four-ray refinement; its theorem is the
signed cellular incidence and rank calculation on that fixed subdivision.

SHA-256:
`7e32badfcdf200fa3bb284db1502c8435bc7732bc973e4e55aa894c81372763f`

```console
python ai/omreal/verify_diag3_pair_tapered_ribbon.py
```
# Diagonal-three double-graph certificates

`DIAG3_triple_double_graph_type49_pivot3_certificates.bin` stores the compact
exact witnesses for the `107,778`-row type-49/pivot-3 double-graph layer.
`../verify_diag3_triple_double_graph_scan.py` independently reconstructs all
integer graph identities and degree conditions. The file has 2,936,122
bytes and SHA-256
`52c9fec437378098e06a37c74396230b8e501b22bf8c7c5df07ef131e9aaa9c0`.
`DIAG3_triple_double_graph_type49_extension_certificates.bin` stores the
disjoint 1,086-row increment from type-49 pivots 1 and 5. It has 31,884 bytes
and SHA-256
`1dc677cd3d46d774c7ba629606ec9b9483e1fda8c97e048033989f4498787873`.
`DIAG3_triple_double_graph_generic_certificates.bin` stores the disjoint
308,964-row positive increment found in the other first-graph charts. It has
9,718,836 bytes and SHA-256
`8a61846547b6a8ab1984a7ebe8273fd7326316c8a83c040af377a6251b21937c`;
its ordered semantic digest is
`b82343d4aaf5225a6c1efaa454f5a8bad2622e4cd24f9d75603456393cbe0a1f`.
The three double-graph artifacts close `417,828` distinct source rows.  With
the `20` unit-minor-only rows above, the exact all-family union closes
`417,848` and leaves `1,221,055`.  Hashing those remaining rows in canonical
source order gives
`432854b7f00b57c5cf0009033e3ddfd3f4cb702bafed8fad2e5e69b369f30597`.

## Diagonal-three direct-final-affinity certificate

`DIAG3_triple_direct_final_affinity_certificates.bin` stores `128,198`
exact witness occurrences from ten canonical charts after two parent-unit
graphs.  Unlike the earlier cheap final-coordinate mask, each witness forms
the fully denominator-cleared third equation and checks its affinity
directly.  Cross-chart duplicates are retained for audit; their exact
priority union contains `58,673` rows of the pinned `1,221,055`-row source
and leaves `1,162,382`.  The artifact has `4,212,318` bytes and SHA-256
`6ed192d1dd2f814ae914349ec2dbcc654ffb663669b85f1b289fa37feb147f26`.
Its block-stream semantic digest is
`7cd37ee421c651563bb6dbeae45b6711b71839893ba53abfb7240b1e165f2b1a`,
and the remaining rows' packed source-order digest is
`44ff9f5f0ea6c332c0382717533f5fa4b8e4b8af3d72024f9d4b0c74e6448dda`.

```console
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/verify_diag3_triple_direct_final_affinity.py \
  --source-residue /tmp/diag3-triple-work/diag3_current_residue_1221055.bin
```

This is a positive construction layer only.  It does not make a maximality
claim for charts not represented in the certificate and does not close the
remaining triple obligation.

## Diagonal-three primitive-final-direction certificate

`DIAG3_triple_primitive_final_direction_certificates.bin` stores `23` exact
rows outside the frozen `58,673`-row direct-final union.  After the same two
parent-unit graphs, each record reconstructs the full denominator-cleared
third equation and proves it affine along a primitive direction
`e_i +/- e_j`.  The associated two-coordinate change is unimodular.  The
artifact has `711` bytes and SHA-256
`af0d1964840975e324d2c0181e732142ccd4e35c88ab4fc2702b6c70e6389bde`;
its record-stream semantic digest is
`8917815ae6b4c65c83b74e09d5ee8f3f18f237d9bd493fce04094ca3d8f0f055`.
The direct-plus-primitive union contains `58,696` source rows and leaves
`1,162,359`, whose packed source-order digest is
`6c477d76ec0173ab340db4c9f5b783d3638393d0714e58440bae35b143b02b6a`.

```console
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/verify_diag3_triple_primitive_final_direction.py \
  --post-double-residue \
  /tmp/diag3-triple-work/diag3_post_double_graph_residue.bin
```

This is a positive 23-row increment, not an exhaustive primitive-direction
search.  The triple obligation remains open.

## Diagonal-three support-three primitive-final certificate

`DIAG3_triple_primitive_final_support3_certificates.bin` stores `57` exact
rows disjoint from the prior direct-final plus support-two union of `58,696`.
After two parent-unit graphs, each record reconstructs the fully cleared third
equation and proves it affine along a primitive direction
`e_i +/- e_j +/- e_k`.  The associated three-coordinate change is
unimodular.  The 1,771-byte artifact has SHA-256
`c900dd68143d6228847124e4bc5891f440e0d116e2aabbaf2f0e28647f9fdbb3`
and semantic digest
`71df56d10ebd93be6f4c59f626d38d9a992264b2cbaf74fe0070618fed4a0de0`.
The combined union contains `58,753` rows and leaves `1,162,302`, whose
packed source-order digest is
`a76a7c2cd6631c2d9724b450540bec7f3be6c106a41ae41f1736bbd2755a5ca4`.

```console
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/verify_diag3_triple_primitive_final_support3.py \
  --post-double-residue \
  /tmp/diag3-triple-work/diag3_post_double_graph_residue.bin
```

This is a positive 57-row increment, not an exhaustive primitive-direction
search.  The triple obligation remains open.

## Diagonal-three full-space height-`b` critical gate

`DIAG3_triple_fullspace_critical_h1.json` is the complete deterministic sparse
critical system for the hard presentation `(5563,16134,19284)`, which maps to
canonical row `(5563,4373,23221)`.  It stores the three residual equations and
all 56 formal `3x3` Jacobian minors away from the height column `b`, including
four identically zero minors.  The 364,486-byte artifact has SHA-256
`c9244a47ded5736e7afe724a9914e75631a22b78653442e88c14f5c397919eb8`.

The independent replay reconstructs every sparse determinant and proves that
the raw ideal contains two maximum-dimensional coordinate boundary
components, each lying on 23 parent walls.  This is a fail-closed saturation
gate, not a triple closure; the ledger remains `2/9`.

```console
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/verify_diag3_triple_fullspace_critical_h1.py
```

The manifest semantic digest is
`3cd9f4106c0a3299a22493f9375791d05d4a9f2ca3bcf17b63b88f83483aefea`.

## Row-2599 `p01` tangent collar

The global pair-closure manifest now records an exact four-stage nonradial
relative collar for the previously exceptional `p01` edge.  It carries no
separate data artifact: the verifier derives its rational endpoints from the
pinned row-2599 source and checks every polynomial segment over `Q`.

```console
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/verify_diag3_row2599_p01_tangent_collar.py
```

Its semantic digest is
`e3df18c1a98ccca9e022832e3656c7e2ae3a9c7c822a153c7fc40e9519e08016`.
An independently coded dense-polynomial replay has digest
`82dda129bef8f52ce4c41fbc8b31e9a316419953bb89a9eaaf8983f9ab1379f8`.
All three local pair edges now have relative wall collars, but no complete
mixed `d3` cell is claimed.

## Row-2599 `p01` comparison prism

Five exact bivariate patches join the stored nonrelative `K(p01)` sweep to
the tangent collar.  Tensor Bernstein replay preserves all 70 parent signs
and both transported Gordan circuits.  After taking the block-mass product,
the signed ordinary boundary is exactly
`+K(p01)-Q(p01,block0)+Q(p01,block1)`; the remaining faces are relative, collapsed,
or paired internally.

```console
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/verify_diag3_row2599_p01_comparison_prism.py
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/review_scratch/DIAG3_HOSTILE_VERIFY_ROW2599_P01_COMPARISON_PRISM.py
```

The producer and independent dense-bivariate semantic digests are
`0b015361e1c75007f025e90921fa5f295616b0e3e8d4bbf941e5161545e433c7` and
`acca3573a369139c9a142592febcaa55ce453eeb10c1d52631ac5b226129127b`.
This is one of six local comparison incidences, not a mixed `d3` or global
master-subdivision certificate.  Its two named singleton lateral disks still
need literal gluing to the future `H0` and `H1` comparison prisms.

## Row-2599 `p12` and `p20` comparison prisms

Two exact patches per pair edge join the stored `p12` and `p20` sweeps to
their certified two-stage relative collars.  Producer and independent dense
replays preserve all parent signs and both incident circuits.

```console
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/verify_diag3_row2599_p12_p20_comparison_prisms.py
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/review_scratch/DIAG3_HOSTILE_VERIFY_ROW2599_P12_P20_COMPARISON_PRISMS.py
```

Their semantic digests are
`48871bfbc021051f4f672eaf6372ecd5d1d0f0324005648b8d471e130b60e8f8` and
`930d28e2fbc1990cb68e403b034b3ec7aa440a455b5017a13aa1426e1336dba4`.
The three pair-edge comparison prisms supply six distinct singleton lateral
disks.

## Row-2599 `H2` comparison prism

Four exact trivariate patches join the block-2 disks from `p12` and `p20`
literally, with signed ordinary boundary
`+K(h2)-Q(p12,block2)+Q(p20,block2)`.

```console
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/verify_diag3_row2599_h2_comparison_prism.py
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/review_scratch/DIAG3_HOSTILE_VERIFY_ROW2599_H2_COMPARISON_PRISM.py
```

The producer and independent semantic digests are
`4027e41a519953200e205f4e7ab2453a83122822d6ca2ed60bb649cd60afc7a7` and
`55539702e53abdcf15a1173a549699d87427f85881d66db881ff33c98586934b`.
The local comparison ledger is now `4/6`; `H0`, `H1`, mixed `J`, and global
coverage remain open.

## Chart-0/chart-152 source staircase

`DIAG3_PAIR_SOURCE_STAIRCASE_COVERAGE_0_152.json` records five exact
parent-resident source boxes of total normalized volume `373/512`.  It
classifies all 89,120 box-factor restrictions, with 5,106 distinct factors
occurring on at least one box and 12,718 zero-free on every box.  Exact graph
and coordinate-adaptive critical-system arguments prove every boxwise wall
component reaches the union of the five box boundaries.  Internal seams are
part of that declared source skeleton; global parent-cell coverage remains
open.

```console
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/verify_diag3_pair_source_staircase_coverage.py
```

## Diagonal-three completion open object

`DIAG3_COMPLETION_OPEN_OBJECT.json` is the machine-readable resumption record
for the still-open third diagonal.  It pins the authoritative PR-17 base, the
exact union arithmetic and hashes for all stabilized positive triple layers,
the current residual obligation, the missing global pair-closure
object, both acceptance contracts, and deterministic replay commands.  Its
status is deliberately `OPEN`; it is not a completion certificate and does
not change the honest `2/9` ledger.

```console
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/verify_diag3_completion_open_object.py
```
