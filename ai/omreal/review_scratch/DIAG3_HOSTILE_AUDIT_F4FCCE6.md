# Diagonal-three hostile audit from `f4fcce6`

## Verdict

Diagonal three remains open and the honest score remains `2/9`.
The closed-cover reduction really has two independent invariant obligations:

1. `H_c^0(B_0 intersect B_1 intersect B_2;Q)=0`; and
2. injectivity of the alternating map from the three pair `H_c^1` groups.

The first cannot be cancelled in the spectral sequence
(`DIAG3_ARCHITECTURE_ADVERSARIAL_AUDIT.md`, lines 21--48), and after the
recorded lower vanishings the second is the only remaining associated-graded
piece in total degree two (lines 50--67).  The exclusive-pair/balanced-end
model is an exact model of the second obstruction, not a dispensable cover
artifact (`DIAG3_PAIR_DIFFERENTIAL_ENDS.md`, lines 5--78).

I found no new counterexample to diagonal three.  I did find and repair one
slice-saturation overclaim, found a general countermodel to an inadmissible
triple shortcut, and independently validated the sequential-affine,
unit-Jacobian-minor, and expanded double-graph positive layers.  Their exact
combined triple residue at the double-graph checkpoint is `1,221,055`; the
subsequent direct-final and primitive-final layers reduce it to `1,162,302`.
I also confirmed that the pair master
quotient is an honest conditional compiler rather than a global certificate,
and that the row-2599 root-choice loop obstructs every proposed filler
subordinate to one fixed singleton block.  An exact common proper ray and six
bounded tapered cubes improve that canary.  Exact replay now also proves the
six pair/singleton Gordan-witness seams and the common-apex mass cospan.  It
still does not supply the mixed **base-space** filler, any of the six full
comparison incidences, or the missing `d3` cell.

## Exact positive checkpoint

The full all-canonical-kind/all-parent-unit-pivot sequential scan gives:

| object | exact count or digest |
|---|---:|
| prior unresolved source | `1,819,789` |
| new square-affine closures | `180,886` |
| exact residue | `1,638,903` |
| residue file SHA-256 | `5ba2314c94ba115d5bf5e975e68412e3f4b44e2c65df51b757f6150a3352d4e1` |
| witness file SHA-256 | `7e9ad80ae55c1f51dda7f7dc584dac8eefe41197124914cb83aab3cf0a2b719e` |
| mask semantic digest | `b5e5c3171da1acfd5c47d2ebb793ed1be8cced5f01275e05b68d9e51ef4c3f08` |
| witness semantic digest | `d27735abc8601c04b1114786d2a044af1acf8b99c253aee347ab101c4bb5368b` |
| residue semantic digest | `d78a529cdb3e920b76b4b420114e24065c7e9e7cb2ef2a904b1a1e952c567270` |
| double-graph closures | `107,778` |
| double-graph certificate SHA-256 | `52c9fec437378098e06a37c74396230b8e501b22bf8c7c5df07ef131e9aaa9c0` |
| double-graph semantic digest | `98619fff126cc4e10331735fe691cde7f8e3a4f4983b31c63fbf5cd50616c5c9` |
| type-49 pivot-1/5 extension, disjoint increment | `1,086` |
| extension certificate SHA-256 | `1dc677cd3d46d774c7ba629606ec9b9483e1fda8c97e048033989f4498787873` |
| extension semantic digest | `a00a00cb16f238abecc8c625fa6334fc907f088e8906bada529384a59f5589e3` |
| generic double-graph increment, disjoint from the preceding two | `308,964` |
| generic certificate SHA-256 | `8a61846547b6a8ab1984a7ebe8273fd7326316c8a83c040af377a6251b21937c` |
| generic semantic digest | `b82343d4aaf5225a6c1efaa454f5a8bad2622e4cd24f9d75603456393cbe0a1f` |
| all double-graph rows | `417,828` |
| unit-minor closures, standalone | `117` |
| unit-minor certificate SHA-256 | `9889d40c9fdc4c23817a28e94b311cec1673b4e4dfd3e072dace17ff49ffd97a` |
| unit-minor pair semantic digest | `15b761934f6fb98d036f1820e99b3c6012ea4134ae5746579dac874280537e15` |
| unit-minor row semantic digest | `8dabe7ae8baf1bf6ce7d8dbac7621a4e6810860717fd3c4a39700db018b22e79` |
| unit-minor overlap with all double-graph rows | `97` |
| exact double-graph/unit-minor union | `417,848` |
| exact combined residue | `1,221,055` |

Thus the combined theorem-safe positive checkpoint is
`77,881,394/79,102,449`, not triple closure.  The `117` unit-minor rows must
not be added to the `417,828` double-graph rows: the unit-minor layer
contributes only `20` new rows after the full double-graph layer.  The exact
source replay obtained intersection `97`, union `417,848`, and residue
`1,221,055`.

I independently parsed and symbolically replayed all `180,886` witness
records.  For every record the hostile verifier checked:

* the selected reframe maps the recorded anchor to the claimed canonical
  primitive factor;
* the recorded stabilizer element fixes that canonical anchor and maps the
  other two factors to the recorded targets;
* the anchor graph split reconstructs the primitive polynomial exactly;
* its slope factors into parent brackets and hence is a unit throughout the
  parent cell;
* the coordinate-pair bit is in the exact `8 choose 2` universe; and
* both cleared graph restrictions are jointly affine in that pair.

This replay used `19,807` distinct algebra keys.  An independent source pass
also proved that the `180,886` witness rows and `1,638,903` residue rows are
unique, disjoint, and have union equal to the pinned post-triangular,
post-Morse, post-constant-shear `1,819,789` rows.

### Square-affine theorem audit

I retract the proposed determinant-unit objection.  The lemma in
`DIAG3_PROJECTIVE_COLUMN_FIBER_COMPRESSION.md`, lines 108--127, is sound.
For `F(w,z)=A(w)z+b(w)` on an open domain:

* at a consistent singular `A(w)`, the fixed-base solution is a
  positive-dimensional affine space; the component through the point in the
  open fiber is noncompact, closed in the fixed-base zero set, connected to
  the point, and therefore contained in the same global component;
* away from the determinant locus, the zero set is a graph over a component
  of an open positive-dimensional base, which is noncompact.

The sequential scan exhausts all twelve canonical factor orbits, every
parent-unit graph pivot, all three choices of anchor, and the full stabilizer
coset after one canonical alignment
(`build_diag3_triple_sequential_affine_scan.py`, lines 40, 118--170,
179--217, and 262--307).  The graph pullback of the parent cell is open, and
clearing powers of the nonzero slope preserves the two remaining zero sets.

### Unit-Jacobian-minor theorem audit

The theorem in `DIAG3_TRIPLE_UNIT_MINOR_AFTER_GRAPH.md` is sufficient for
componentwise noncompactness.  After the parent-unit anchor graph, a certified
fixed two-by-two Jacobian minor of the two remaining cleared equations is a
nonzero integer times a product of graph-restricted parent brackets.  Each
factor is nowhere zero on the open graph domain, so the zero set is a smooth
six-manifold and projection to the complementary six coordinates is a local
diffeomorphism.  A semialgebraic connected component is open in that zero
set; if compact, its image would be a nonempty compact open subset of
`R^6`, which is impossible.  This needs neither injectivity nor properness of
the projection.

The stabilized independent verifier reconstructed all `234` integer
identities, with parent-product lengths `4:13`, `5:56`, `6:140`, `7:24`,
and `8:1`.  Full anchor alignment and stabilizer traversal maps them to
exactly `117` unique rows of the pinned sequential residue, at anchor-index
counts `2,12,103`.  The optional source replay checked the residue SHA,
layout, uniqueness, distinct factors, and membership.  This is explicitly a
positive subset, not an exhaustive unit-minor screen.

### Double-graph theorem audit

The theorem in `DIAG3_TRIPLE_DOUBLE_GRAPH_COMPRESSION.md` is also sufficient.
The first equation has a parent-unit graph slope.  On that graph the second
equation is affine in a second coordinate and its slope is an exact product
of restricted parent units.  The chosen final coordinate is absent from both
the second slope and constant, while the first-graph restriction of the third
equation is affine in it.  Substituting the second graph therefore cannot
raise the final degree.  The remaining one-equation affine-fiber lemma on an
open positive-dimensional base includes the final slope-zero/rank-drop locus;
the two unit graph homeomorphisms preserve connected components and
compactness.

The final tracked verifier passed the original `107,778` records, the `1,086`
type-49 pivot-1/5 extension, and `308,964` generic records.  The three sets are
pairwise disjoint and total `417,828`.  For the generic layer it reconstructed
`4,931` exact second-slope products, `5,526` final-coordinate independence
keys, `23,736` third-factor affinity keys, and `116` explicit final-
substitution regressions.  The corresponding counts for the original layer
are `1,450`, `1,526`, `5,513`, `21`; for the extension they are `17`, `22`,
`499`, `7`.

The hostile full-source replay parsed the pinned `1,638,903`-row residue,
proved membership of all `417,828` double-graph rows, rebuilt the `117`
unit-minor rows, and obtained the exact all-family union/residue
`417,848/1,221,055`.  It independently reconstructed every alignment,
stabilizer transport, equation identity, source row, and algebra key and
obtained the pinned byte and semantic hashes.  The later primitive-direction
lemma also replayed exactly on `21` rows, semantic digest
`68116c422a26d570de424cc510d397f2637cc205dbc6e6d97ba618be6daffd72`,
but every one of those rows is already in the generic certificate, so it has
zero ledger increment.

### Direct-final and primitive-final theorem audit

The later direct-final certificate tests the fully denominator-cleared third
equation after two parent-unit graphs, rather than imposing pre-substitution
coordinate-independence.  Its theorem is sound: both graph operations are
homeomorphisms onto open domains, all clearing factors are nowhere-zero
parent units, and affinity of the final cleared equation in a remaining
coordinate reduces to the same one-equation affine-fiber lemma, including
the slope-zero locus.

The hostile full-record/source replay passed all `128,198` occurrences in
ten canonical chart blocks.  Their priority union contains `58,673` unique
rows of the pinned `1,221,055` source and leaves `1,162,382`; the certificate
SHA-256 is `6ed192d1dd2f814ae914349ec2dbcc654ffb663669b85f1b289fa37feb147f26`,
its stream semantic is
`7cd37ee421c651563bb6dbeae45b6711b71839893ba53abfb7240b1e165f2b1a`,
and its residue semantic is
`44ff9f5f0ea6c332c0382717533f5fa4b8e4b8af3d72024f9d4b0c74e6448dda`.

The primitive-final layer adds `23` disjoint rows.  It constructs the same
fully cleared polynomial and proves
`(D_i + epsilon D_j)^2 R=0` over `Z`.  The change
`z_i=u, z_j=epsilon*u+s` has determinant one and makes this directional
derivative `partial_u`, so the affine-fiber reduction applies on the
transformed open domain.  Exact source replay passed all `23` rows, the
explicit first slopes `+[1456][2468]` and `-[1236][2467]`, eight second-slope
identities, all 23 directional identities, and zero overlap with the direct
layer.  Its SHA-256 is
`af0d1964840975e324d2c0181e732142ccd4e35c88ab4fc2702b6c70e6389bde`.
The combined direct-final/primitive-final union is `58,696`, leaving
`1,162,359` of the post-double source.  These layers are subsequent to the
`77,881,394/1,221,055` checkpoint tabulated above; final bookkeeping must use
the newest residue without mistaking the earlier table for the final total.

The support-three primitive-final extension adds another `57` disjoint rows.
Exact replay passed all `34` second-unit slopes and all `57` fully cleared
identities
`(D_i+epsilon_j D_j+epsilon_k D_k)^2R=0`.  The associated three-coordinate
change is in `GL_3(Z)`, so the same open-domain affine-fiber theorem applies.
The certificate SHA-256 is
`c900dd68143d6228847124e4bc5891f440e0d116e2aabbaf2f0e28647f9fdbb3`.
Full source replay proved zero overlap with the prior `58,696` rows and left
`1,162,302`, with packed source-order digest
`a76a7c2cd6631c2d9724b450540bec7f3be6c106a41ae41f1736bbd2755a5ca4`.

## Pair master quotient audit

The master-quotient construction is mathematically sound but still
conditional on construction of a coverage-certified compactified regular
closure poset.  In particular:

* the lower-cell all-strata rule is stated correctly;
* existence of a subordinate semialgebraic triangulation is explicitly not
  confused with a machine construction
  (`DIAG3_PAIR_GLOBAL_MASTER_QUOTIENT.md`, lines 100--116);
* barycentric face signs canonically provide an integral lift and `MN=0` once
  the regular closure poset and relative infinity subcomplex are certified
  (lines 176--209); and
* the document honestly leaves global cells, labels, closure, infinity, and
  middle ranks open (lines 306--327).

The node roadmap is now pinned before use at SHA-256
`ddec96b052b305d279b543be2af27e12f380f0dedc79ea434616c64b40cd8cea`
(`verify_diag3_pair_global_master_quotient.py`, lines 40--44 and 381--389).
Its exact replay has semantic digest
`3fa42824f50159521c1e7a38f9bb56952460a7e4e5f736f76c4403dbe9eb7214`.
The local node deliberately retains `48` nonexact profile triples,
representing `1,628,792,064` ordered signature triples.  This is a valuable
falsification regression: local collars plus `MN=0` do not prove global
middle exactness.

The closure-gap audit passes with observation digest
`27e55460f7bb22f1ec278d67c7441fd06e6a455c32605d00a1bb57b294edf85b`.
It correctly records zero certified global adjacency edges, zero parent
infinity cells, and zero global strict closure pairs or triples
(`verify_diag3_pair_global_closure_gap.py`, lines 445--481).  Straight-line
failure between sampled charts is used only as an observation, not as a
claim that no curved path exists.

### Exact obstruction to a singleton-block filler

The row-2599 canary in `DIAG3_JOINED_FLOW_TRIANGLE.md` has three valid bad
signatures with elementary-root escape-set sizes `56,56,60`, pairwise
connecting roots, and empty triple root intersection.  Its exact integral
relative two-complex has `H_0=H_1=0`, `H_2=Z`; the primitive remaining class
is

```text
-T + S01 + S12 + S20 + H0 + H1 + H2.
```

The section-5 Cech one-cocycle evaluates `1` on its root-choice loop.  Hence
that loop cannot bound over `Z`, `Q`, or `F2` in any complex assembled from
arbitrarily long ordered-root cells that transport one fixed block at a
time.  Pair mapping strips do not change the evaluation.  This is a genuine
no-go theorem for the singleton-block architecture, not a counterexample to
diagonal three.

The smallest load-bearing pair lemma is therefore a coverage-wide,
face-natural, proper **mixed-block** relative three-cell construction whose
boundary is exactly the displayed primitive class.  It must specialize
through zero-block, zero-witness, residual-wall, and parent-infinity cospans,
and the resulting global `partial_3` columns must span `ker partial_2`.
Pointwise triple escape paths do not supply the required disk-level
naturality or global incidence.

### Exact row-2599 bounded checkpoint

`verify_diag3_row2599_common_proper_escape.py` independently replays a
chart-zero proper ray obtained by moving labelled column 7 in direction
`(81,-262,91,86)`.  For physical parameter
`t*23597311/105015122`, all 70 parent brackets keep their prescribed strict
sign for `0 <= t < 1`, the three recorded block circuits remain strict, and
the unique endpoint wall is `[2467]=0`.  This is a sound local `H_c^0`
generator, not a `d3` column.

The common-ray verifier exactly certifies all six ordered, bounded tapered cubes
joining the three elementary root carriers to that ray.  Their reduced
first-wall truncations are
`1221971981/1769366234` at `[1234]`,
`42214994/2183619501` at `[1358]`, and
`425791163/1286992887` at `[1256]`.  Tensor-Bernstein conversion proves weak
parent-sign preservation and a fixed strict block circuit on every cube.

The hostile ordered-sector replay goes further.  It proves the exact full
origin residence components, discovers and certifies the bounded H0 outer
cap, and checks the signed raw-cone boundary.  The leftover is the primitive
hexagon
`-p01-p12-p20+h0-h1-h2`.  Both circuits on each pair face are strict; all six
pair/singleton cofactor sections agree literally; the H0 denominator-gauge
interfaces agree after the exact inverse row gauge; and the common endpoint
is the single wall `[2467]` with the three pair sections forming the boundary
of the block-mass triangle.  Thus witness convexity and seam compatibility
are no longer the local blocker.

At that audit stage the certified comparison-incidence count remained `0/6`.  A
mixed base-space three-chain with the displayed hexagonal boundary is still
absent.  Moreover the simplest radial common-apex cone is rigorously false:
on the `p01` source edge its unique parent wall is
`sgn[1234]=2443943962(1-h)`.  Keeping the source face relative forces
`h(0,r)=1`, while collapsing roots at the common apex forces `h(s,1)=0` for
all `s>0`; continuity fails at the corner.  The smallest local target is now
a nonradial parent-face-natural base map (or an exact bad-locus cap for the
source comparison hexagon), not another witness interpolation.

The first nonradial parent-wall attempt is also decided exactly.  The `p12`
and `p20` source walls admit complete two-stage collars to the shared
`[2467]` base with both adjacent circuits strict.  The `p01` collar does not:
along its `[1234]` wall, block 0 becomes good before the first additional
parent corner `[1367]`.  At an exact rational midpoint, the integer covector
`(10000,177,-7015,368)` realizes all 56 block-0 signs with minimum signed dot
`5966575`.  The subsequent `[1367]`--`[2467]` segment is parent-resident and
bad again (two-circuit `136/167`), so the obstruction is the intervening good
interval.  A successful cap now needs a new parent-tangent generator leaving
the tested two-parameter plane before that witness wall; no such incidence is
present in the tracked atlas.

A subsequent exact tangent construction repairs that local collar without
contradicting the no-go.  At the block-0 witness wall it perturbs labelled
column 6 outside the falsified plane, reaches `[1367]` with both incident
blocks bad, follows `[1367]` to `[2467]`, and follows a positive-denominator
rational `[2467]` graph to the common apex.  All 70 parent signs, both cofactor
kernels, literal seams, and projective-gauge witness transports replay with
semantic digest
`e3df18c1a98ccca9e022832e3656c7e2ae3a9c7c822a153c7fc40e9519e08016`.
An independent dense-univariate implementation replays the same walls,
circuits, and seams with semantic digest
`82dda129bef8f52ce4c41fbc8b31e9a316419953bb89a9eaaf8983f9ab1379f8`.
The local relative pair-collar count is therefore `3/3`, while the complete
comparison-incidence count first advanced to `1/6`.  Five exact bivariate patches join
`K(p01)` to this new relative collar while retaining both incident cofactor
circuits.  The product-boundary audit leaves exactly
`+K(p01)-Q(p01,block0)+Q(p01,block1)`; a separate dense-bivariate implementation
replays the result with semantic digest
`acca3573a369139c9a142592febcaa55ce453eeb10c1d52631ac5b226129127b`.
The two singleton lateral disks are named rather than discarded, and still
must glue to the future `H0` and `H1` prisms.  Exact two-patch producer and
independent dense replays then certify the `p12` and `p20` pair prisms, so the
current count is `3/6`.  The six pair-edge singleton disks are distinct; the
`H2` comparison is now also certified by four exact trivariate patches and a
separate reconstruction: its boundary is
`+K(h2)-Q(p12,block2)+Q(p20,block2)`, with the two pair laterals literal.
The current count is `4/6`; `H0`, `H1`, and the assembled mixed `J` are not
certified.

A tempting common-root shortcut was also falsified exactly.  Recomputing a
fresh circuit after the `(1 -> 3,+)` shear stays positive, but transport of
the fixed block-1 witness demands incompatible orientation exponents at row
30 (`[167]`, alpha `-1`) and row 35 (`[128]`, alpha `+1`).  The empty
triple-root intersection is therefore a genuine naturality obstruction, not
an escape-set implementation bug.  This regression is pinned in both the
local verifier and the machine-readable open object.

## Correctness repairs and certification hardening

These are repairs or trust boundaries, separate from the two open mathematical
obligations.  After the listed repairs I found no remaining correctness defect
in the stabilized sequential, unit-minor, double-graph, or pair-master claims.

1. The local fold computation originally promoted a critical ideal saturated
   by `[1234]t(4t+3)(20t-3)` to an unsaturated slice theorem without checking
   the three interpolation divisors.  The dependency-free exact repair now
   returns to the original incidence equations and proves:
   `t=0` forces `[1348]=[1578]=0`; `t=-3/4` forces `P4=P8` and every
   `{4,8}` bracket to vanish; `t=3/20` forces `[2578]=0`; and `[1234]=0`
   is parent boundary.  The restored theorem is valid only for the pinned
   affine slice, subject to the named exact `msolve-0.10.1` completeness
   boundary.
2. The fold continuation originally suggested separation from all `26,740`
   residual factors along its whole chain.  The verifier only proves that
   separation in the fold neighborhood.  The repaired prose now uses the
   critical census plus parent-wall exits for the slice theorem and does not
   claim global segmentwise residual separation.
3. The sequential producer now pins the final counts and semantic/file
   digests above.  It also checks the already available Morse SHA-256
   `afe01d6d94bc4b8ce133cbe0d14ceb01d9dd72514f9ed7a59b73d5f6b4299734`
   and constant-shear SHA-256
   `1cece61ff1a551faaeefc0062267e24266d264d9e19748d40fa5a74db9ce0be3`
   rather than only their parsed shapes and counts.
4. `verify_diag3_triple_sequential_affine_certificates.py` now independently
   reconstructs every witness without the producer masks.  Both it and the
   producer explicitly assert that every chosen alignment maps the anchor to
   `canonical[kind]`.  The standalone replay passed all `180,886` records,
   the 12 used graph anchors, the pinned per-anchor counts, and semantic digest
   `d27735ab...`.
5. Ordinary replay of the slice RUR checks exact stored consequences but does
   not reproduce ideal completeness without `msolve-0.10.1`.  This is an
   honestly named external exact-CAS trust boundary, not a dependency-free
   exhaustive certificate.
6. A pre-publication finite-field unit-minor screen rejected minors that were
   zero modulo `3`.  That is a false-negative bug when the nonzero integer
   scalar in a valid parent-product identity is divisible by `3`.  All
   negative and maximality claims from that screen were withdrawn.  The
   retained `234` positives are unaffected because the verifier reconstructs
   each identity exactly over `Z`.
7. A prototype double-graph binary writer used an 11-field format for 12
   values.  Before publication it was corrected to
   `<HHHBBBBHHBbB`, with an explicit final-coordinate byte followed by the
   signed scalar and label count.  The tracked verifier pins the final byte
   hash, header, count, record metadata, and exact EOF.
8. A prototype double-graph verifier placed `seen.add(row)` in an unreachable
   conditional suite and declared source constants without using them.  The
   stabilized verifier records every row, rejects duplicates and repeated
   factors, validates coordinate ranges and exclusions, and optionally pins
   and parses the entire sequential residue before proving subset membership.
   The corrected tracked replay passed.
9. The final generic double-graph certificate pins `308,964` records,
   `9,718,836` bytes, SHA-256 `8a618465...`, exact semantic digest
   `b82343d4...`, source membership, and disjointness from the original and
   extension layers.  The no-argument replay and the complete pinned-source
   replay both passed.
10. A discovery-time row-2599 common-root claim confused positivity of a
    freshly selected circuit with natural transport of the carrier circuit.
    The claim was withdrawn.  The exact row-30/35 orientation conflict is now
    a required negative regression, and the manifest retains zero certified
    comparison incidences.

The global status, strategy checkpoint, and machine-readable completion open
object have since been reconciled to the exact final positive count/residue
`77,940,147/1,162,302` after all three final-affinity layers.

## Adversarial countermodel to a tempting shortcut

`DIAG3_HOSTILE_MULTIAFFINE_PAIR_TRIPLE_COUNTERMODEL.md` gives three distinct
primitive multi-affine polynomials in `R^9` whose triple zero set has a compact
`S^6` component while every pair zero set is connected and noncompact.  The
third polynomial has rank-nine quadratic part and is irreducible.  Translation
and scaling put the compact component inside an arbitrary open chamber.

Therefore multi-affinity, smoothness, and pair noncompactness do not imply
triple noncompactness.  Any closing triple theorem must use the actual
Pluecker/parent coupling or an exact certificate, not those generic features.

## Open obligations

### Triple

The exact remaining source has `1,162,302` orbits after the sequential,
expanded double-graph, unit-minor, direct-final, and support-two/support-three
primitive-final union.
Every one still needs a direct
component-noncompactness theorem or an exhaustive exact certificate.  The
pinned fold is one fixed-base slice and does not transfer connected components
from the full nine-variable stratum.

The support-drop induction itself is sound
(`DIAG3_TRIPLE_FACTOR_REDUCTION.md`, lines 182--250), and the Burnside universe
of `79,102,449` factor-triple orbits is exact (lines 274--316).  The remaining
gap is its geometric endpoint, not the reduction.

### Pair

No coverage-certified compactified global regular parent cell universe,
closure relation, simultaneous-wall ledger, or infinity subcomplex exists.
Consequently the actual global `N,M`, `MN=0`, and middle rank have not been
constructed.  The integral-lift argument is correct only after that geometric
complex exists (`DIAG3_ARCHITECTURE_ADVERSARIAL_AUDIT.md`, lines 73--133).

The generator preflight does admit one exact reduction.  Under a temporary
pinned Python `3.12.13` / SymPy `1.13.3` / mpmath `1.3.0` environment,
`verify_diag9_active_sector.py` replays `8,916` certified-empty row-2599
factor walls and leaves `17,824` candidates.  The clean repository runtime
lacks SymPy and the repository pins no dependency version; the verifier also
keeps the sorted empty-factor IDs only in memory.  Thus the next generator
must first pin a finite projective/reciprocal compactification atlas and
export an independently checked candidate-factor list.  A bounded
standard-chart CAD would still omit genuine infinity faces.

### Imported parent dependency

The duality reduction imports contractibility of all normalized parent
realization cells.  `2,546/2,604` are independently traced; the remaining 58
use the blanket statement attributed to Tsukamoto
(`PARENT_CONTRACTIBILITY_AUDIT.md`, lines 5--17).  This dependency is explicit,
not a new diagonal-three defect.

## Ranked closure strategies

1. **Extend unit graphs on the exact combined residue.**  Use the
   independently replayable `1,162,302` rows as the source for the remaining
   canonical graph charts, exact unit-minor identities, double-graph families,
   or a boundary-saturated height-critical pass.  This is the smallest current
   triple target.
2. **One compactified labelled master subdivision for the pair endpoint.**
   Construct its exact cells, closure pairs, strict three-chains, labels, and
   infinity subcomplex.  Then generate signed integral incidence and the
   mod-two middle-rank test canonically.  This avoids coherence problems from
   independently chosen receivers and factor roots.
3. **Boundary-stratified full-space triple roadmap/CAD.**  Extend the fold
   template to all variables and all saturation/infinity divisors, with an
   exact component-to-boundary ledger and symmetry quotient.
4. **Receiver/root atlas only as a fallback.**  It remains valid in principle
   but must add global adjacency, simultaneous-factor, specialization, and
   infinity incidences; the current 178-point bank supplies none of those
   global closure edges.

Do not promote local folds, sampled exits, modular negative screens, local
formal `MN=0`, or unsigned matrices without a certified integral geometric
lift to theorem status.

## Exact hostile replay commands

```text
python ai/omreal/verify_diag3_pair_global_master_quotient.py
python ai/omreal/verify_diag3_row2599_common_proper_escape.py
python ai/omreal/review_scratch/DIAG3_HOSTILE_VERIFY_ROW2599_ORDERED_SECTOR_ROADMAP.py
python ai/omreal/verify_diag3_pair_global_closure_gap.py \
  --manifest ai/omreal/data/DIAG3_PAIR_GLOBAL_CLOSURE_OPEN_OBJECT.json
python ai/omreal/verify_diag3_triple_concurrence_local_fold_cell.py \
  --union4 /tmp/diag3_hostile_f4fcce6/diag3_union_degree4.bin
```

The complete sequential producer command requires the pinned union-four
bucket and should export both artifacts:

```text
python ai/omreal/build_diag3_triple_sequential_affine_scan.py \
  --union4 /tmp/diag3_hostile_f4fcce6/diag3_union_degree4.bin \
  --export-residue /tmp/diag3-triple-work/diag3_all_unit_anchor_residue.bin \
  --export-certificates /tmp/diag3-triple-work/diag3_all_unit_anchor_certificates.bin
python ai/omreal/verify_diag3_triple_sequential_affine_certificates.py \
  /tmp/diag3-triple-work/diag3_all_unit_anchor_certificates.bin
python ai/omreal/verify_diag3_triple_double_graph_scan.py \
  --sequential-residue /tmp/diag3-triple-work/diag3_all_unit_anchor_residue.bin
python ai/omreal/verify_diag3_triple_unit_minor_after_graph.py \
  --sequential-residue /tmp/diag3-triple-work/diag3_all_unit_anchor_residue.bin
python ai/omreal/verify_diag3_triple_primitive_direction_double_graph.py \
  --type50-discovery /tmp/dg50.pkl
python ai/omreal/verify_diag3_triple_direct_final_affinity.py \
  --source-residue /tmp/diag3-triple-work/diag3_post_double_graph_residue.bin \
  --all-block-records
python ai/omreal/verify_diag3_triple_primitive_final_direction.py \
  --post-double-residue /tmp/diag3-triple-work/diag3_post_double_graph_residue.bin
```
