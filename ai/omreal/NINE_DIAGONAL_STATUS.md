# Nine-Diagonal Vanishing: proof status and exact remaining targets

## Result ledger

Let `X` be the normalized realization space of a realizable `UOM(4,8)`, let
`F_sigma` be the parent charts supporting extension signature `sigma`, and
put

\[
 F_S=\bigcap_{\sigma\in S}F_\sigma,
 \qquad B_S=X\setminus F_S=\bigcup_{\sigma\in S}B_\sigma.
\]

The Nine-Diagonal Vanishing Lemma asks for

\[
                  \widetilde H_{9-s}(F_S;\mathbb Q)=0
                  \qquad (|S|=s,\ 1\le s\le9).        \tag{1}
\]

Here the nine-diagonal conjecture quantifies over families whose feasibility
regions are proper and pairwise incomparable.  Several reductions below,
including the duality and master-chamber graph theorem, hold for arbitrary
finite `S` and are therefore stated in that stronger form.

Exactly two of the nine entries are currently proved.

| `s` | primal group in (1) | exact dual target | status |
|---:|---|---|---|
| 1 | `H_tilde_8(F_sigma)` | `H_c^0(B_sigma)` | **proved integrally** |
| 2 | `H_7(F_S)` | `H_c^1(B_S)` | **proved integrally**; exchange-saturated support drop excludes every compact component of `B_sigma intersection B_tau` |
| 3 | `H_6(F_S)` | `H_c^2(B_S)` | open; every single-bad group through `H_c^2` vanishes integrally; exact component escapes close `77,940,147/79,102,449` triple-factor orbits, leaving `1,162,302`; at the row-2599 full-support gate, 10,844/17,824 candidate walls are interior-nonempty, 1,177 have exact fixed-sign empty-zero-set certificates, and 5,803 remain unresolved; the pair differential is reduced to an explicit exclusive-pair/balanced-end complex, and mod-two middle exactness would suffice for the rational target, but no coverage-certified global master closure complex exists |
| 4 | `H_5(F_S)` | `H_c^3(B_S)` | open; exact fivefold complex; every omitted-label single piece vanishes through `H_c^3`, leaving only cover-all supports |
| 5 | `H_4(F_S)` | `H_c^4(B_S)` | open; block-Gordan convexity alone is formally insufficient |
| 6 | `H_3(F_S)` | `H_c^5(B_S)` | open; block-Gordan convexity alone is formally insufficient |
| 7 | `H_2(F_S)` | `H_c^6(B_S)` | open; rank-deficient witnesses can be removed without changing the target group |
| 8 | `H_1(F_S)` | `H_c^7(B_S)` | open; rank-deficient witnesses can be removed without changing the target group |
| 9 | `H_tilde_0(F_S)` | `H_c^8(B_S)` | open; parent 860 now has an exact 23-chamber coordinate-star no-go and a 24-chamber all-family CEGIS repair network, but no full-dimensional parent roadmap |

The dual column is valid for all nine entries after importing the published
contractibility statement for realizable oriented matroids on fewer than nine
elements.  The source trace and the independent coverage of 2,546 parent
classes are recorded in `PARENT_CONTRACTIBILITY_AUDIT.md`.  Independently of
that blanket input, contraction-height vanishing plus the direct
seven-label Gordan escape prove the dual column through `s=4`.

## Proved first diagonal

For every realizable uniform rank-`r` oriented matroid `N` on `n` elements
and every element `e`, the contraction-height construction gives

\[
 \mathcal R(N)\simeq G_e(N)\subset\mathcal R(N/e),
 \qquad
 \widetilde H_i(\mathcal R(N);\mathbb Z)=0
 \quad\text{for }i\ge(r-2)(n-r-1).                    \tag{2}
\]

Its fibers are open convex height polyhedra; a partition-of-unity section
and straight-line contraction prove the homotopy equivalence.  Applying (2)
to the rank-four, nine-element extension specified by `sigma` gives

\[
                     \boxed{\widetilde H_8(F_\sigma;\mathbb Z)=0}. \tag{3}
\]

Properness of `F_sigma` is unnecessary.

## Proved second diagonal

Compact-support Mayer--Vietoris gives

\[
0\to H_c^0(B_\sigma\cap B_\tau)\to H_c^1(B_\sigma\cup B_\tau)
\to\ker\!\left[H_c^1(B_\sigma)\oplus H_c^1(B_\tau)
\to H_c^1(B_\sigma\cap B_\tau)\right]\to0.           \tag{4}
\]

A new dual single-bad escape theorem removes the second term entirely.  If
`N` is any realizable uniform rank-four oriented matroid on nine elements,
then

\[
                 \widetilde H_7(\mathcal R(N);\mathbb Z)=0.       \tag{4a}
\]

To prove this, contract the distinguished extension and Gale-dualize the
lift locus.  It becomes a single-extension feasibility locus over a
rank-five/eight-element parent.  At any bad chart, a minimal Gordan circuit
uses at most six four-subset normals, hence at most 24 label incidences.
Some label occurs at most three times.  Moving that column inside the
intersection of its at most three support hyperplanes in projective
four-space preserves every active normal up to positive scale and reaches a
parent wall.  Thus every bad component is noncompact.  Supported duality and
the integral contraction-height vanishing in ambient degrees at least six
give (4a), without the blanket parent-contractibility input.

For the original rank-four/eight-element parent, the same supported-duality
sequence now gives

\[
                         H_c^1(B_\rho;\mathbb Z)=0                 \tag{4b}
\]

for every signature `rho`.  Consequently (4) collapses integrally to

\[
 H_c^1(B_\sigma\cup B_\tau;\mathbb Z)
       \cong H_c^0(B_\sigma\cap B_\tau;\mathbb Z).                \tag{4c}
\]

The exchange-saturated support-drop theorem now proves the remaining
assertion: every simultaneous-bad locus
`B_sigma intersection B_tau` has no compact connected component.  At a
nonstructural minimal three- or four-circuit, an exact all-strata support
classification and conic witness exchange produce a common moving-witness
shear.  If a hypothetical compact component avoided every such circuit,
strict five-circuits and structural small circuits would persist locally,
making the component clopen in the connected noncompact parent space.

The only source-hard finite residue consists of eight localization `3+5`
formulas, three ordinary `4+4` formulas, and ten necessary ordinary `4+5`
supports.  The first two classes are UNSAT.  All ten supports in the last
class are wall-disjoint; conic exchange forces a new positive circuit sharing
one wall triple, a contradiction.  The exact theorem and replay are in
`DIAG2_EXCHANGE_SATURATED_SUPPORT_DROP.md`; the signed certificate has
semantic digest

```text
4546a2e7ba03c1c9dd63abbe65195fc348accf9bf91ccaa773072f1fcae9df38
```

Combining this with (4c) gives

\[
 H_c^1(B_\sigma\cup B_\tau;\mathbb Z)=0,
 \qquad
 \boxed{\widetilde H_7(F_{\{\sigma,\tau\}};\mathbb Z)=0}.       \tag{4d}
\]

The formerly separate restriction-map obstruction is zero.
The quotient-level Gale identification and every orientation, gauge, and
duality step have been independently reconstructed in
`SECOND_DIAGONAL_SINGLE_REGION_H7_AUDIT.md`.

### Historical circuit-cover reductions

The reductions below record the route to the final support-drop theorem and
remain useful for later diagonals; statements of an open compact-component
residue in those checkpoint notes are superseded by (4d).

Gordan and Caratheodory give a finite closed cover of every bad locus by
circuit pieces `C_(rho,Q)`.  Zero-padding makes the size-five pieces cofinal:

\[
                         B_\rho=\bigcup_{|Q|=5}C_{\rho,Q}.       \tag{5}
\]

Every single piece has `H_c^0=H_c^1=0`.  The circuit-cover calculation of the
then-remaining compact-component obstruction was

\[
 H_c^1(B_S)\cong\ker\!\left[
 \bigoplus_{\alpha<\beta}H_c^0(C_\alpha\cap C_\beta)
 \xrightarrow{d_1}
 \bigoplus_{\alpha<\beta<\gamma}
 H_c^0(C_\alpha\cap C_\beta\cap C_\gamma)\right],     \tag{6}
\]

where every index may be a five-support piece.  Pencil/common-apex/common-
light arguments eliminate most summands.  Same-signature circuit exchange
shows that every individual surviving compact pair-component class has a
nonzero `d_1` image, but it does not exclude cancellations among classes.
An exact proper incomparable pair blocks the analogous two-ray exchange for
cross-signature terms.

There is a sharp universal combinatorial refinement.  If the union of two
cofinal five-supports is pencil-rigid, some label has degree three and its
local partner defect is at most two.  Since pencil rigidity excludes defect
zero, the global minimum satisfies `d(U) in {1,2}`.  When `d(U)=2`, the
degree-three label has exactly the matching-star pattern

\[
                         eab,\quad ecd,\quad efg
\]

with six distinct partners.  This is not a formal residue: an exact parent-16
example has two realizable signatures with proper incomparable feasibility
regions and positive minimal `5+5` circuits attaining defect two.  Both
circuits persist along an exact shear until the parent bracket `[1678]`
vanishes, so the exhibited point escapes; the example disproves the tempting
universal one-defect shortcut but is not a compact component.  See
`SECOND_DIAGONAL_DEFECT_TWO.md`.

The word "minimum" is essential.  A separate exact proper incomparable pair
has global defect one but also has a local matching-star label; every one of
the twelve oriented partner rays at that star loses one of the two chosen
strict five-circuit witnesses before a parent wall.  A lower-support pivot
still escapes, so this is only a no-go for a root-free frozen-support argument,
not an obstruction to 9DVL and not an example in the global defect-two class.
See `SECOND_DIAGONAL_MATCHING_STAR_LOCAL_NO_GO.md`.

A moving-witness shear removes the frozen-support failure in a precise
conditional form.  If `T_t=T g_t` is a column shear, transport each signed
Gordan three-form by `Lambda^3(g_t^(-1))`.  The kernel identity then persists
exactly, while replacement triples may acquire nonnegative weight.  One XOR
sign test on the two full signatures and their colored active supports
selects a common parameter ray; that ray stays simultaneous-bad until its
first parent wall, or tends to a parallel-column boundary at infinity.  Thus
any component containing compatible witnesses is noncompact.  Every one of
the 65 stored row-2599 hard occurrences passes (1,244 compatible rays in
total), and the parent-16 defect-two pair has 22 compatible shears.  A proved
low-source count forces some ordered shear to have at most two colored
sources, but arbitrary signings can make all two-source XOR tests conflict,
so universal compatibility still needs the oriented-matroid extension
constraints.  See `DIAG2_MOVING_WITNESS_SHEAR.md` and its exact verifier.

That last qualification is now exact even inside the realizable extension
domain.  A proper incomparable parent-16 pair has one legitimate strict
`5+5` witness choice for which all 56 elementary shears conflict.  Complete
enumeration finds 622 and 1,040 positive minimal circuits and proves that the
displayed pair is the unique incompatible one among all 646,880 choices.
Replacing one circuit triple gives the unique shear `5 -> 8`, which escapes
at `[4567]=0` and `u=533/1228`.  Thus a theorem about arbitrary selected
witnesses is false, while the sharper 112-direction escape-set intersection
target survives strongly in this example.  See
`DIAG2_WITNESS_EXCHANGE_AUDIT.md` and its two exact verifiers.

That 112-direction target now has a circuit-free exact formulation.  For a
fixed oriented shear, delete every transported signed normal whose replacement
coefficient has the wrong direction.  Strict Gordan duality says the shear is
an escape direction exactly when no complete derived-arrangement tope agrees
with the extension signature on all retained rows.  This restriction test
exhausts all 40,524 bad signatures at parent 16 and all 71,112 bad signatures
at each of four hard row-2599 charts; every pair of escape sets intersects.
The minimum sizes are 52 and 53, respectively, so cardinality alone does not
prove the parent-16 case.  This is exact chart evidence and a proof-level
reduction, not the universal chart theorem.  A common direction at one point
already supplies a proper ray inside that point's connected simultaneous-bad
component, so the universal escape-set intersection theorem would finish
diagonal two directly; no additional direction-gluing theorem is needed.
The exhaustive extension of the audit to all 178 stored parent-2599 charts
gives minimum escape-set size 53 and minimum pair overlap 6, with aggregate
digest
`d255845e6b246865ed3c50a61c001ec8701d3b22fffd218087d955ac0854d111`.
This remains a point-bank theorem, not chamber coverage.  See
`DIAG2_ESCAPE_SET_TOPE_REDUCTION.md` and
`DIAG2_ESCAPE_SET_ATLAS178.md`.

The same finite theorem has now been replayed at one exact integer
realization of every one of the 2,604 realizable `UOM(4,8)` catalog parents.
It covers 106,957,822 bad extensions and 2,241,206,348,415 unordered
within-parent pairs.  All pairs intersect, with global minimum escape size 52
and global minimum overlap six.  The audit deliberately retains the 154
representatives whose derived arrangements are residually degenerate, as
well as the 2,450 generic ones.  Its matrix- and independent-extension-census
pinned digest is
`58b5a8cb8f6e36466efabb6dc6a4ba1b9bf9f812f5899f5138d6abc96c2c8a18`.
This is a point transversal across parent chirotopes, not coverage inside any
one realization space.  See `DIAG2_COMMON_SHEAR_PARENT2604.md` and its exact
verifier.

Two exact reductions sharpen the surviving universal target.  Global
reorientation of the extension element preserves every mask,
`E_T(-rho)=E_T(rho)`, so finite searches may quotient antipodal signatures.
Independently, nonescape is certified by inclusion-minimal source-local tope
separators.  Each such separator covers at most five of one source's fourteen
directions, and a disjoint pair is exactly an eight-source cover by the two
minimal-separator families.  Parent 16 compresses 2,063,096 raw separators to
287,560 minimal ones, with at most six per signature/source, and has no such
cover.  At that checkpoint, the remaining proof problem was to exclude the
eight-source cover from the extension GP axioms and derived covector
elimination uniformly.  See
`DIAG2_ESCAPE_MINIMAL_SEPARATORS.md` and the antipodal and separator
verifiers.

The complete overlap-at-most-eight residue across all 2,604 parent samples is
now extracted rather than represented only by its minimum.  It contains 1,154
antipodal pair orbits in 875 parents, with overlap histogram
`{6: 212, 7: 50, 8: 892}`.  Every one of the 2,307 distinct endpoint
signatures has exactly four singleton mutation triples as its complete
minimal-separator family; there are no larger minimal separators.  In that
entire four-singleton regime the surviving universal cover is impossible:
a disjoint pair would force a linear three-uniform `8_3` configuration, the
29,400 colored configurations have three symmetry orbits, and the shared-
parent rank-four Grassmann--Pluecker system is UNSAT for each orbit.  Hence a
counterexample must first cross a separator bifurcation, gaining or losing a
mutation neighbor or acquiring a non-singleton separator.  This conditional
theorem does not rule out those bifurcated regimes and does not promote
diagonal two.  See `DIAG2_NEAR_COUNTEREXAMPLE_OBSTRUCTION.md` and its three
exact verifiers.

The first exact separator-bifurcation attack isolates a labeled type-`50`
edge at extremal parent 187.  Every new minimal separator on the bifurcated
side contains an old one, so the separator-dominance lemma makes all six
tracked escape masks monotone; one extremal pair moves from overlap six to
nine and the other two stay at six.  A deterministic `216`-chart survey at
the three parents carrying three overlap-six pair orbits gives `648` tracked
observations: `495` remain simultaneously bad, none falls below six, and all
`65` non-singleton observations have overlap at least nine.  This identifies
undominated separator births as the sharper remaining transition target; it
is not parent-cell coverage and does not promote diagonal two.  See
`DIAG2_EXTREMAL_SEPARATOR_BIFURCATIONS.md` and its two exact verifiers.

The next exact edge reaches that sharper class.  On the same parent-187
`e`-line, reversing isolated type-`49` factor `23604` births singleton row
`1` at sources `1`, `2`, and `4` while size-two separator `{30,33}` remains
at sources `6` and `7`.  The destination is therefore mixed rather than
four-singleton, and the affected escape mask genuinely shrinks `67 -> 61`.
All six lost directions were common with the fixed partner, but nine common
directions survive, so pair overlap changes `15 -> 9`.  The birth-budget
lemma for pairs already simultaneously bad now reduces the transition search
to separator births whose cover-loss budget can meet the incoming overlap.
This is one exact labeled edge, not a classification or a proof of diagonal
two.  See
`DIAG2_EXTREMAL_UNDOMINATED_BIRTH.md` and its exact verifier.

The complete standard `e`-coordinate slice through parent 187 is now covered
wall by wall.  Exact Sturm isolation gives `1,721` residual roots and `1,722`
open chambers.  Across all `5,166` observations of the three extremal pairs,
`4,159` remain simultaneously bad, `1,007` lose an endpoint, the minimum
overlap remains six, and every non-singleton observation has overlap at least
nine.  Only six still-bad pair transitions change overlap; their high-to-low
profiles and total loss budgets are `15 -> 9 / 6`, `12 -> 6 / 6`, and
`9 -> 6 / 5 or 6`, so none can spend the full incoming overlap.  Two other
walls birth or kill a bad pair on sides already carrying overlap 12 or 9.
This closes budget-tight births on one complete coordinate slice, not the
parent cell, and does not promote diagonal two.  See
`DIAG2_EXTREMAL_LINE_TRANSITION_CENSUS.md` and its exact verifier.

The next parent-187 target is now an exact two-dimensional object rather than
an arbitrary rectangle.  The full `d/e` parent-cell slice is a bounded convex
hexagon; all `26,740` residual restrictions have total degree at most two,
and the `24,750` nonconstant equations are pairwise nonproportional.  Exact
parent-unit factorization reduces the ten central-line seed circuits to a
global `164`-membership/`142`-factor link census and an effective disk
frontier of `160` memberships in `139` nonconstant factors.  Ten selected
intersections on six seed factors are isolated in exact rational rectangles:
each contains one transverse two-wall node and no other residual wall, and
the resulting forty complete chamber tables preserve overlap at least six
for the three tracked pairs.  These boxes do not cover a collar or the
hexagon and do not promote diagonal two.  See
`DIAG2_EXTREMAL_TRANSITION_DISK_FRONTIER.md`,
`DIAG2_EXTREMAL_TRANSITION_DISK_SEEDS.md`, and their exact verifiers.

Mutation-stable evidence also survives substantially stronger tests.  At the
generic type-`37/44` square, every pair among 48,770 signatures bad in all
four cells has one shear valid throughout the square; robust masks have size
at least 52 and overlap at least eight.  The independently coverage-certified
parent-2599 node gives 70,968 common-bad signatures, minimum robust size 53,
and minimum robust overlap eleven.  Finally, exact two-sided audits at one
generic edge of every one of the thirteen canonical residual incidence types
cover 557,578 common-bad records and 12,091,441,965 decorated pairs; every
robust pair overlaps in at least nine directions.  Exact local-germ segment
certificates tie the generic samples to their wall germs.  These are local
canonical-incidence theorems, not the 84,840 labeled-occurrence theorem or a
covered parent-cell graph.  See `DIAG2_ROBUST_MUTATION_SQUARES.md` and
`DIAG2_CANONICAL_ROBUST_EDGES.md`.

The generic support-drop obstruction is now reduced much further than the
raw wall-star census.  For localization births, all 32 labeled source-hard
`3+5` partners form eight decorated wall-occurrence orbits, and shared-parent
Grassmann--Pluecker constraints plus conflict on all 56 ordered shears make
all eight exact formulas UNSAT.  For ordinary births, the exact source-hard
support census has 53 wall-stabilizer orbits; signed GP and shear constraints
reduce these to 23, and fixed-unit wall/partner cofactor identities leave ten
necessary `4+5` candidates of types `41,49,50,51`.  The exhaustive ordinary
four-partner scan leaves only three labeled source-hard cases in two orbits;
the strengthened shared-parent signed formulas make all three UNSAT.  The ten
`4+5` candidates' selected wall and partner cofactors
touch exactly 35 primitive residual factors; this is not a full escape-mask
chamber atlas.  Exact uniform generic wall points realize one type-50 and one
type-51 candidate, and both selected circuit pairs have no compatible shear,
disproving the stronger arbitrary-selected-witness theorem.  Exact two-sided
perturbations certify transverse support-drop germs, while reciprocal
same-parent-chirotope child matrices prove that both signature pairs have
nonempty, proper, incomparable feasibility regions.  Their complete escape-mask
intersections have sizes 51 and 80.  At the type-50 point, the original pair
is the unique incompatible choice among all 208,262 positive minimal-circuit
pairs, and one circuit exchange gives twelve compatible shears.  These are
not disjoint-mask pairs.  The final verifier also proves that all ten rigid
`4+5` supports are wall-disjoint; the exchange-saturated theorem uses that
fact to cover simultaneous lower-wall strata and promote diagonal two.  See
`DIAG2_GENERIC_BIRTH_PATTERN_REDUCTION.md`,
`DIAG2_EXCHANGE_SATURATED_SUPPORT_DROP.md`, and their exact verifiers.

Every individual residual factor wall nevertheless has a universal proper
escape.  In an adapted global frame its equation is affine in one pivot with
a nowhere-zero parent-bracket-product slope, so the wall is a graph over an
open subset of `R^8` and has no compact component.  The fixed-minor argument
also rules out compact common-zero components for all 66 pairs and 170
direct-minor triples of canonical residual representatives.  Most
importantly for the block resolution, signatures using different labeled
wall circuits of one global factor remain bad along the whole wall.  This
closes the multi-circuit all-die escape at one factor.  It does not rule out
a compact simultaneous-bad chamber enclosed by several noncompact wall
pieces, and the representative pair/triple tables do not cover relative
`S_8` labelings.  See `RESIDUAL_STRATUM_NONCOMPACTNESS.md`.

The block-Gordan compactification does not make a vertical Bland pivot proof
automatic.  Its convex witness fiber has one degree-zero critical generator,
so a matching confined to that fiber simply reconstructs the bad-locus
indicator sheaf.  Nor can the unsigned support nerve carry the missing data:
two exact rational plane covers have the same two-vertex, one-edge nerve but
compact-support first cohomology of ranks one and zero.  In the genuine
parent-16 defect-two pair, the first exact wall along a candidate shear occurs
at `t=541589/6442906`; the support `123` becomes a positive four-circuit.
The complete wall fan has 45 incoming, three outgoing, and four rank-three
degenerate paddings, and every alternative triple row retains an unpruned
competitor.  Thus the next finite object must retain compact intersection
components and their split--merge/restriction maps.  See
`DIAG2_PIVOT_BLOCK_GORDAN_NO_GO.md`.

That component decoration now gives a universal local wall theorem.  After a
first residual support drop, the 51-spoke integral wall-star incidence matrix
is injective for every compactness decoration except the extreme case in
which its central component and all 51 spoke components are compact.  Only
that decoration retains the one-dimensional transfer kernel.  A spoke is
formally flexible exactly when the four-support/five-support union is
pencil-flexible.  At the exact parent-16 defect-two wall, the central
component has a certified two-stage escape and every spoke component is
noncompact or has a private unit row, so its component-decorated matrix is
unimodular.  This closes that hard wall, not all walls.  The exhaustive
residual support census leaves `112,041` unsigned symmetry orbits after the
unary signed/all-unit rejection, with beta split
`77,649/33,453/938/1`; these are support upper bounds, not realizability or
compactness counts.  See `DIAG2_PIVOT_COMPONENT_GRAPH.md` and
`DIAG2_PIVOT_UNIVERSAL_WALL_THEOREM.md`.

Adding every first-wall padding row cannot remove the exceptional generator.
The complete local matrix is the oriented incidence matrix of `K_52`, with
rank 51 and primitive kernel `Z(1,...,1)`; an exact transverse-plane model
realizes the same compactness axioms.  Geometry nevertheless forces progress:
along the residual wall's canonical pivot coordinate, the incoming cofactor
is affine with fixed nonzero bracket slope and cannot recur.  Therefore every
compact strict spoke must meet a genuine residual wall for a different
cofactor before it can reach the parent boundary.  Each first wall has 30--52
strict paddings.  In that approach the then-remaining target was global
acyclicity of this iterated signed wall graph, not a larger first-wall Euler
calculation.
See `DIAG2_PIVOT_ALL_COMPACT_SECOND_WALL.md`.

Two exact tests delimit that global step.  Every one of the 13 residual types
has a pencil-rigid partner whose degree-one partner label occurs two or three
times in the first wall support, so the wall equation along its motion need
not be linear.  Type 51 realizes a genuine compact ellipse in that motion
plane; 19 parent brackets cut the displayed oval into escaping arcs, but
incidence counting alone does not prove this cutting universally.  Separately,
an exact uniform `44 -> 37 -> 44` canonical-pivot cycle shows that successive
one-coordinate Bland moves need not preserve an increasing set of bad-side
signs.  A successful proof needs a multi-coordinate cone potential or a
direct exclusion of closed realizable transition cycles.

The multi-coordinate alternative is now exact at first order.  If the
active signed residual gradients, restricted to the witness-preserving
tangent space, have no common strict direction, Gordan's alternative gives a
finite positive Farkas dependence among them.  A realizable proper
incomparable pair on the coincident type-46/type-47 localization wall attains
the smallest obstruction: its gradients are `g` and `-g`.  The common
three-circuit omits label 8, however, and an exact tangent motion of that
label preserves both bad witnesses until `[5678]=0`.  Thus a strict cone
field is false globally, while the certified obstruction itself escapes.
See `DIAG2_PIVOT_CONE_FARKAS.md`.

The former relative-label pair gap is now closed exactly.  The `84,840`
labeled occurrences give `26,740` localized residual factors in six full
`S_8` orbits and `9,476` unordered distinct factor-pair orbits.  Exhausting
all canonical projective frames gives bracket-product `2 by 2` Jacobian
minors for `9,226`; exact common translations settle another `124`, and
weighted-torus escapes settle four more.  A separate saturation theorem
settles the seven type-`(49,49)` cases.  The canonical-presentation
affine-fiber sweep closes another `111` and leaves exactly four conic pairs:
`(50,7861),(50,7977),(50,12128),(50,20046)`.  Finally, stabilizer-equivalent
graph presentations make all four affine as well (with `(50,20046)` reversed
to anchor its type-51 factor).  Thus iterated affine-fiber graphs settle all
122 cases left after the first three certificate families, and every
pair-wall component is noncompact in all `9,476` relative-label orbits, with
no local pair residue.  The perfect-square conic reduction for `(50,7977)`
remains an independently checked partial result, not the argument used for
its final closure.  None of these local pair theorems alone promoted diagonal
two; the universal common-shear intersection theorem was the primary
remaining target.  The later exchange-saturated support-drop theorem closes
that target without decorated transition-cycle acyclicity.
The 66 pairs among the
12 displayed canonical polynomials are the smallest subtable of this result.
Among the 220
canonical triples, 170 have a direct bracket-product `3 by 3` minor and
`(36,38,42)` has a short two-minor saturation certificate.  Four triples
have exact uniform rank-two witnesses—`(37,41,46)`, `(37,46,49)`,
`(39,48,50)`, and `(41,46,49)`—and 45 remain unclassified.  Rank dependence
does not by itself give a positive Farkas dependence: three witnesses are not
on the three relevant oriented halfspaces simultaneously.  The sole common
triple-wall witness, `(39,48,50)`, has the positive gradient relation
`dq39+3dq48+2dq50=0`, but an exact tangent path preserves all three positive
wall circuits and reaches `[2478]=0`.  This is not yet the labeled theorem:
relative labeled triple overlaps are unclassified.  See
`DIAG2_PIVOT_REPRESENTATIVE_GRADIENTS.md` and
`DIAG2_PIVOT_REPRESENTATIVE_TRIPLES.md`, and
`DIAG2_PIVOT_REPRESENTATIVE_TRIPLE_FARKAS.md`; the full pair census and its
three exact certificate families are in
`DIAG2_PIVOT_LABELED_PAIR_THEOREM.md`.

Double contraction also has a sharper exact boundary.  In its six-dimensional
one-row Koszul normal system, an all-bilinear minimal positive circuit has at
most six rows, and a circuit with exactly one contracted-column constant row
is impossible; every seven-circuit therefore has at least two constant rows.
An exact honest parent with two realizable private extensions nevertheless
has an allowed seven-row minimal positive circuit whose alternating
five-form pencil has determinant 9.  Its fixed-weight height is unique, so a
universal Koszul-kernel escape is false.  The surviving route requires
relative fiber vanishing together with Hardt/exit specialization control,
not ordinary fiber homology alone.  See
`DIAG2_PIVOT_DOUBLE_FIBER_KOSZUL.md`.

A separate exact no-go rules out a convex-log shortcut.  In the standard
nine-variable projective-frame gauge, row-2599 charts 0 and 3 have a
coordinatewise free-log midpoint that crosses parent bracket `[5678]`.
More sharply, charts 77 and 85 lie in the same parent cell and on the side
`q_44>0`, while their free-log midpoint keeps all 70 parent signs and has
`q_44<0`.  Thus neither the parent cell nor every residual side is convex in
the nine free logarithms.  Coordinate sections are intervals, but that weaker
orthogonal convexity does not exclude bounded components.  A proof-safe
residue survives: any relatively compact full-dimensional residual chamber
forces a positive dependence

\[
                 \sum_j \frac{\nabla f_j}{f_j}=0.     \tag{6a}
\]

Consequently a signed-gradient rank/kernel census is a valid finite KKT
filter for the `5+5` residue, not a proof of diagonal two.  See
`FREE_LOG_COORDINATE_OBSTRUCTION.md`.

## Exact third-diagonal reduction

The strongest current single-signature theorem is now

\[
                   H_c^q(B_\rho;R)=0
                   \qquad(0\le q\le2)                         \tag{7}
\]

for every coefficient ring `R`.  Filter the proper normalized Gordan
resolution by the **actual coordinate faces** of its convex witness fibers.
A fiber `k`-face uses at most `5+k` normals.  In total degree at most two,
only `k=0,1,2` occur, with support unions of at most five, six, and seven
triples.  Support-plane residence motions kill the corresponding base groups
through degrees two, one, and zero.  Constant-rank kernel charts, the
face-orientation local system, and the support/rank frontier order make this
an integral compact-support filtration argument rather than a cover
heuristic.  See `DIAG3_SINGLE_BAD_TWO_SKELETON.md`.

The total-degree-two circuit-cover row consists of single-piece `H_c^2`,
pairwise `H_c^1`, and triple-intersection `H_c^0` groups.  The first of these
three columns is now proved to vanish in full, not only generically:

\[
                   H_c^q(C_{\rho,Q};\mathbb Q)=0
                   \qquad (q=0,1,2,\ |Q|\le5).        \tag{7a}
\]

If `Q` omits a label, the existing three-dimensional deletion fiber proves
(7a).  If it covers all eight labels, incidence counting supplies a
degree-one label `e` and a label `g` outside its unique triple with degree at
most two.  Moving `e` through its two-dimensional support plane and `g`
through its one-dimensional support-plane pencil gives three-dimensional
fibers with convex two-dimensional sections.  Every fiber component is a
contractible oriented open three-manifold, so compact-support Leray descent
kills all rows below degree three.  This includes structural supports,
residual-wall degenerations, and zero-weight faces.

The earlier exact census of `760,200` generic supports in `45` `S_8`-orbits
is now an audit rather than a residue: the fixed-apex test kills 38 orbits and
the plane-plus-pencil theorem kills the remaining seven, including the
unique `beta=1` orbit.  The pairwise `H_c^1` and triple-intersection `H_c^0`
columns remain.  Exact examples show that the current fiber tests do not
annihilate them termwise, so global constructible-sheaf support and
spectral-sequence differentials are still necessary.  See
`THREE_SHEAR_SINGLE_PIECE_REDUCTION.md` and
`THIRD_DIAGONAL_E1_REDUCTION.md`.

There is now a sharp conditional support-drop theorem for the triple column.
If every connected component of every common zero set of at most three
distinct primitive residual factors is noncompact, then every triple-bad
component is noncompact.  The same nested-component proof applies to three
fixed closed circuit pieces, so the hypothesis would kill `E_1^(2,0)`
termwise.  The hypotheses are proved for zero, one, and two factors, including
all `9,476` relative-label pair orbits.  Burnside reconstruction shows that
the missing three-factor endpoint has `79,102,449` unordered `S_8`-orbits;
the existing pair certificates do not imply it.  Projective reframing,
support-plane forests, triangular unit graphs, and exact parent-unit Jacobian
minors now prove component noncompactness for

\[
                         \boxed{77,940,147}
\]

of those orbits.  The positive replay consists of `74,767,375` jointly affine
orbits, `26,927` moving-column degree-two orbits, `2,410,414` degree-three
forest orbits, `12,333` triangular unit-graph orbits, and `65,550` further
unit-minor orbits.  A separate exact constant-plane replay closes 61 more
orbits in role frame 1119.  The first unit-minor family uses exact identities
from 79 role frames;
the separate maximality search exhausted all 1,120 role frames and has a
304-frame zero tail.  A subsequent exhaustive all-canonical-kind,
all-parent-unit-pivot graph scan closes `180,886` further rows by a square
jointly affine fiber, including every rank-drop fiber.  Its tracked compact
certificate is independently replayed row by row and leaves exactly
`1,638,903` degree-four orbits.  On that residue, canonical type-49
double-graph charts at pivots `1`, `3`, and `5` close `108,864` rows: the
pivot-3 certificate closes `107,778`, and the disjoint pivot-1/5 extension
closes `1,086`.  A generic all-chart double-graph certificate adds `308,964`
disjoint rows, for `417,828` double-graph rows in total.  A graph-restricted
unit-minor layer closes `117`, of which `97` overlap the pivot-3 certificate;
its remaining `20` are outside every double-graph certificate.  The exact
all-family union closes `417,848` and leaves `1,221,055`, with canonical
source-order residue digest
`432854b7f00b57c5cf0009033e3ddfd3f4cb702bafed8fad2e5e69b369f30597`.
On that exact source, the direct-final certificate forms the fully cleared
third equation after two parent-unit graphs and closes a `58,673`-row
priority union by exact final-coordinate affinity.  Unimodular primitive
final-direction extensions on supports two and three add respectively `23`
and `57` disjoint rows.  Their combined `58,753` rows leave `1,162,302`, with
packed source-order residue digest
`a76a7c2cd6631c2d9724b450540bec7f3be6c106a41ae41f1736bbd2755a5ca4`.
Hostile full-record/source replay passed all three artifacts; none of these
positive screens is promoted to a negative maximality theorem.
An exhaustive exponent-difference replay on the final residue now proves
that all `1,162,302` rows have common-weight rank nine already over `F_2`.
Thus no row admits a nontrivial common diagonal scaling in the normalized
coordinates.  A stronger bounded hard-canary calculation gives full rank
`585/585` for arbitrary quadratic vector fields with affine-linear ideal
multipliers on five hard triples.  These are strategy no-go certificates;
they do not reduce the residue or change the theorem score.
See
`DIAG3_TRIPLE_FACTOR_REDUCTION.md`,
`DIAG3_PROJECTIVE_COLUMN_FIBER_COMPRESSION.md`,
`DIAG3_TRIPLE_SEQUENTIAL_AFFINE_COMPRESSION.md`,
`DIAG3_TRIPLE_DOUBLE_GRAPH_COMPRESSION.md`,
`DIAG3_TRIPLE_UNIT_MINOR_AFTER_GRAPH.md`,
`DIAG3_TRIPLE_DIRECT_FINAL_AFFINITY.md`,
`DIAG3_TRIPLE_PRIMITIVE_FINAL_DIRECTION.md`, and
`DIAG3_TRIPLE_PRIMITIVE_FINAL_SUPPORT3.md`, and
`DIAG3_TRIPLE_COMMON_SCALING_NO_GO.md`.

The tested deterministic full colored occurrence/support key gives no
quotient: it was singleton on the `1,819,850`-orbit pre-constant-plane source,
hence also on the current subset.  This does not exclude a different
algebraically sufficient invariant.
On its sparse concurrence chart, the three equations reduce locally to four
bilinear equations over a six-parameter base, but the projection genuinely
ramifies inside the uniform parent cell.  A CAS-produced degree-20 RUR has a
stored branch which is verified exactly and isolates such a corank-one
ramification point with all 70
parent brackets nonzero; outward interval evaluation of all 26,740 primitive
factors proves that only the selected three vanish.  Thus the point is neither
a parent-boundary point nor a forced fourth-factor point.  The concurrence
chart is a useful lower-degree endpoint, not a proof of component
noncompactness or eventual boundary escape.

The corresponding full nine-variable factor-chart critical system is now
tracked for the hard canonical row `(5563,4373,23221)`.  The unique leanest
coordinate height `b` has 52 nonzero degree-eight minors with 14,681 terms,
and an independent sparse determinant implementation replays all 59 formal
equations exactly.  The unsaturated critical ideal contains two
maximum-dimensional coordinate four-spaces, each lying on 23 parent walls, so it is provably not
zero-dimensional.  This is a fail-closed gate: it forces the next computation
to retain explicit parent-wall, chart, rank, extra-factor, and infinity
attachments, and it closes no triple row.  See
`DIAG3_TRIPLE_FULLSPACE_CRITICAL_H1_GATE.md`.

The first exact boundary-stratified successor localizes at `[1378]=di-fg`
and verifies the full chain-rule equivalence after
`b=(di-fg)/(i-f)`.  Two parent-unit entries,
`H_d=i(i-f)` and `dR2/da=[2357][2458][1267]`, then reduce the 21
parent-cell critical minors to six `M_da*` minors; fifteen exact integer
column identities prove that no complementary critical branch is discarded.
After stripping only named parent-unit factors, the six generators have
3,172 terms in total.  The 341-term `ae` residual rank-drop equation is the
sparsest of the four height-independent two-wall charts, while six exact
etale Jacobians make `[1468]` and `[5678]` simultaneous wall coordinates.
Complete `F3`, `F5`, `F7`, and `F9` censuses support their union as the next
critical attachment, but this remains modular discovery.  The exact open
target is

```text
(Jcrit : U0^infinity) : ([1468][5678])^infinity = <1>,
U0=[1378][2378][1238][2357][2458][1267].
```

The target walls are not included in `U0`, but they are parent units on the
open uniform cell.  A unit certificate for the displayed localization would
therefore prove the narrow no-compact-component statement for this canary;
their separate strata, overlap, and infinity attachments are needed only if
the calculation is promoted into a global residue-wide template.

The factored rank-drop successor now gives two exact charts.  On `P!=0` the
rank-drop equation is an `a` graph.  On `P=0`, the identities

```text
P=-f[1378]F+c(i-f)Q,   Q-fF=[1357][1258]
```

prove that `Q` cannot vanish, so the entire divisor is a transverse `c`
graph with no coefficient-drop subbranch.  The remaining factor `L` is
quadratic in `h` with parent-unit leading coefficient.  An exhaustive sign
atlas covers only `17,105,952/104,993,280` raw frame-parent presentations;
the hard triple has trivial `S_8` stabilizer, so an existential parent
reframe cannot be promoted to an orbit theorem.  See
`DIAG3_TRIPLE_BOUNDARY_STRATIFICATION.md`,
`DIAG3_TRIPLE_RANK_DROP_SIGN_ATLAS.md`, and their exact replays.

The direct quadratic-cover continuation has now been exhausted exactly.
All seven `h` resultants of `L` with the critical generators retain
primitive parts of `5,320` to `59,449` terms after every nonconstant
parent-bracket factor is removed.  On the `P=0` graph, `P=L=0` reduces to a
105-term finite-cover equation; its primitive quadratic-in-`d`
discriminant is positive on 2,162 and negative on 442 of the 2,604 exact
parent representatives.  This retires expanded pairwise resultants and a
universal discriminant-sign proof, while leaving structured simultaneous
syzygies and the topology-first completion route open.  See
`DIAG3_TRIPLE_QUADRATIC_COVER_NO_GO.md`.

The final bounded structure-preserving algebraic pass rewrites
`E=H0+eH1+e^2H2` on `L=0` and verifies all five directional identities
exactly.  None of the ten three-by-three directional minors is a parent-unit
product: their primitive cores have 18,459--37,222 terms.  The complete
degree-14 short-target Macaulay pieces have rank 5,202 and zero hits over both
`F2` and `F3`.  This is not a rational nonexistence theorem, but it triggers
the bounded stop rule and moves active effort to the topology-first route.
See `DIAG3_TRIPLE_FACTORED_KOSZUL_GATE.md`.

Naive Gale complementation does not close this residue.  The six displayed
bracket formulas are normalized-chart identities with unequal column
multidegrees.  Termwise complementary-minor substitution therefore omits the
independent column rescalings required to return the Gale kernel to the
standard chart.  Exact isolated wall centers for all six factor kinds satisfy
the original equation, while the proposed complemented equation is nonzero
after the normalized Gale involution.  A valid dual calculation must instead
transport the full labeled occurrence determinant with every normalization
weight.  See `DIAG3_ARCHITECTURE_ADVERSARIAL_AUDIT.md` and
`verify_diag3_gale_normalization_no_go.py`.

The corrected full-occurrence pullback has also been screened exactly on the
six pinned hard triples.  All `241,920` simultaneous `S_8` images have zero
common three-coordinate affinity blocks and zero triangular unit graphs.
Necessary parent-unit tests leave no survivor among `20,321,280` coordinate
Jacobian minors or `365,783,040` sparse decomposable-minor sums.  These are
bounded no-go results for the existing affine/unit families, not an
ideal-saturation theorem or a proof against boundary-stratified Gale/Coble
methods.  See `DIAG3_TRIPLE_GALE_CANARY_NO_GO.md` and its Python/C++ replay.

The standard coordinate-center Cremona involution is also a bounded no-go.
On the source coordinate torus it is componentwise inversion, so the 17
novel target-nonuniform bracket divisors have singleton fibers rather than
positive-dimensional exceptional fibers.  Exact all-`S_8` screens again find
no square-affine or triangular certificate on the six hard triples.  See
`DIAG3_TRIPLE_CREMONA_FRONTIER_NO_GO.md` and its exact replay.

An unstratified triple-contraction shortcut fails for a different reason.
An honest row-2599 lifted family crosses exactly one rank-one quotient loop
wall while all prescribed brackets remain strict and the three private
columns stay independent.  Moreover, two decomposable alternating three-
forms give a separately convex `6+6+6` model homotopy equivalent to
`SO(3) x SO(3)`, with `H_6=Z`.  Any contraction proof must therefore retain
the loop-specialization complex and exploit the full occurrence coupling.
See `DIAG3_TRIPLE_CONTRACTION_NO_GO.md`.

On the simultaneous-feasible side, the loop faces can be completed exactly.
If the three signature traces meet all four antipodal sign classes, every
realizing private triple is independent and the full oriented-span image is
contractible after all quotient loop faces are retained.  The exact ambient
loop complex has f-vector `(128,352,336,112)`, and the condition holds for
`1,625,014/1,750,540` triples in the stored 220-signature family.  This is a
positive contraction-domain theorem, but it lives over
`F_1 intersection F_2 intersection F_3`; the private cones are empty on the
triple-bad locus, so it does not change `H_c^0(B_1 intersection B_2
intersection B_3)` without a new dual bridge.  See
`DIAG3_PRIVATE_TRIPLE_LOOP_COMPLETION.md`.

The factor-pair endpoint now has a uniform alternate compression: after
graphing either member with a parent-bracket-unit slope, every one of the
`9,476` pair orbits makes the other factor affine in a remaining coordinate.
This reproves pair-stratum noncompactness with one certificate family.  The
graph helper was also audited to preserve the common normalization of
`A*x+B`; independently primitive-normalizing `A` and `B` flips only the
constant for types `36`, `38`, and `51`.  The corrected original 122-orbit
digest is `af0fa699771292f5cca65510f32cf5c007034f4c9fdac5c3c3a49f0dfcd65846`,
and the all-pair compression digest is
`a28270e870ff2cb2a81a25a395f573fa95de63dc46b52a212a22779e92445847`.

That uniform pair graph does not extend to triples.  Four exact triples have
no graph presentation making the two remaining equations jointly affine in
two coordinates; three also have no common affine three-plane and no
affine-linear symmetry preserving the displayed generators' constant span.
In the first case, exact number-field
arithmetic exhibits a sign-changing quadratic discriminant root while all
62 nonconstant parent brackets remain nonzero.  Thus discriminant/resultant
projection walls genuinely cross parent-cell interiors and must be included
in any complete triple classifier.  See `DIAG3_AFFINE_FIBER_FRONTIER.md`.

For the pair column, full ordered two-root transport is materially stronger
than the failed common-light and same-source tests.  On the stored
minimum-overlap bad pair at each of all `178` exact row-2599 charts, the exact
escape-choice graph is connected, has at least nine joint carrier edges, and
has minimum vertex degree two.  A commuting-only graph is disconnected at
chart 57 and is repaired only by the bilinear ordered Bruhat transport.  This
is a point-bank theorem, not parent-cell coverage: face specialization,
proper overlap cofinality, and a degree-one global chain contraction remain
unproved.  See `DIAG3_PAIR_CARRIER_GRAPH_AUDIT.md`.

The remaining pair differential now has an exact algebraic reduction.  Put
`T=B_0 intersection B_1 intersection B_2` and
`E_ij=(B_i intersection B_j) minus T`.  Under the proved pair `H_c^0`
vanishing and the still-required triple `H_c^0` vanishing, its kernel fits in

\[
 0\longrightarrow\bigoplus_{ij}H_c^1(E_{ij};R)
 \longrightarrow\ker H_c^1(D)
 \longrightarrow\ker\beta\longrightarrow0,           \tag{7b}
\]

where `beta` is the signed frontier map from the two balanced copies of
`H_c^1(T)` to the three `H_c^2(E_ij)`.  A finite relative cellular model gives
explicit differentials `N,M`; coefficient-universal vanishing is equivalent
to a split contraction `h_2 M+N h_1=I`.  Pointwise noncompactness, connected
root-choice graphs, and vanishing of the active-boundary union do not imply
this rank condition.  The exact missing input is a proper, chamber-complete
signed end-incidence atlas, including factor intersections and infinity.
See `DIAG3_PAIR_DIFFERENTIAL_ENDS.md`.

The actual target has rational coefficients, so the final algebra can be
smaller.  If the integral cellular matrices satisfy `MN=0` and their
reductions obey

```text
rank_F2(N) + rank_F2(M) = dim_F2(C1),
```

then rational ranks are at least the mod-two ranks while `MN=0` bounds their
sum by `dim C1`; equality, and hence rational middle exactness, follows.
This removes orientation signs and Smith-unit conditions from a sufficient
certificate.  It does not remove coverage, zero witness faces,
specialization parity, triple-relative exits, or parent infinity.  A fixed
triangular label order cannot supply that coverage: one exact GP-valid
type-49 wall has 22 common roots, all ascending for the chosen order, and
`S_8` equivariance transfers the obstruction to every fixed order.  See
`DIAG3_ARCHITECTURE_ADVERSARIAL_AUDIT.md` and
`verify_diag3_pair_fixed_order_no_go.py`.

A single labelled regular master subdivision of the compactified parent base
is now known to be sufficient.  Proper convex Gordan fibers can be quotiented
before forming the pair differential; the barycentric two-skeleton of the
master closure poset then supplies canonical integral signs and `MN=0`.
Only original cells, comparable pairs, strict three-cell chains, complete
bad-signature labels, and the genuine infinity subcomplex are needed.  This
is a structural compiler, not the missing input: an exact closure audit shows
that the existing 178 row-2599 charts have zero certified global adjacency,
closure, or infinity cells and cannot be decoded into that master object.
See `DIAG3_PAIR_GLOBAL_MASTER_QUOTIENT.md` and the machine-readable open
object `data/DIAG3_PAIR_GLOBAL_CLOSURE_OPEN_OBJECT.json`.

The smallest covered two-dimensional normal ribbon still does not supply the
global atlas.  Its relative matrices have sizes `12098 by 4917` and
`7180 by 12098`, with maximal ranks `4917` and `7180` over both `F_2` and
`Q`, leaving one free middle class in the exclusive stratum `E_02`.  A pinned
representative uses 242 edges and records a block-zero birth/end imbalance.
Along its complete attaching end, an exact replay reduces 2,855 stored
segments to 50 witness-support pairs and finds five common oriented shears;
`8 -> 3,+` is transverse with determinant `-63617`.

The missing two-parameter audit is now complete for this canary.  It covers
all 84,840 labeled wall occurrences, restricts all 26,740 residual factors,
and leaves 1,707 active block-1 factors.  Tensor Bernstein coefficients put
their only seven possible zeros on the triple-relative side or the double
parent-wall corner.  Thus the actual residence domain is a proper relative
quadrilateral, and the signed product-strip attachment kills the unique
middle class integrally.  Pointwise first-exit intervals can still jump in
general—the exact rectangle regression realizes the failure—but it does not
occur in this completely audited strip.  A global theorem still needs the
same coverage for every pair component and parent cell.  See
`DIAG3_PAIR_TANGENTIAL_SHIFT_AUDIT.md`,
`DIAG3_PAIR_ATLAS_TANGENTIAL_FILL.md`, and
`verify_diag3_tangential_first_exit_no_go.py`.

## Exact fourth-diagonal reduction

Compact-support Cech descent has a general truncation: diagonal `s` is
determined by the three total degrees `s-2 -> s-1 -> s`, hence by
intersections of at most `s+1` circuit pieces.  Thus `H_c^3(B_S)` is exactly
the middle cohomology of a fivefold complex in total degrees `2 -> 3 -> 4`;
this retains every higher spectral-sequence differential.

There is also a top-fiber escape beyond the direct common-apex bound.  If a
circuit-support union omits one label and uses a second label at most twice,
then move the omitted column in its three-dimensional residence chamber and
the second label in its support-plane pencil.  After quotienting these four
parameters, every fixed-pencil section is open convex.  Each fiber component
projects to an interval and retracts onto it, so it is a contractible oriented
open four-manifold.  Semialgebraic `R pi_!` descent therefore gives
`H_c^q=0` for all `q<=3`; no properness of `pi` is assumed.  Positive normal
rescaling preserves zero Gordan weights, so the proof includes all closed
lower-support faces.

A single support of at most five triples can therefore contribute to `H_c^3`
only if it covers all eight labels.  The exhaustive all-support audit checks
`4,216,422` supports: `2,500,442` omit a label and are killed, while
`1,715,980` cover all labels (`840/72,380/1,642,760` in sizes `3/4/5`).
Among generic five-supports the retained count is `1,099,560` labeled
supports in `66` of `117` `S_8`-orbits, removing `922,432` in `51` orbits.

Incidence counting gives every cover-all support a degree-one plane motion
and two further light pencils, but this alone does **not** kill the top row.
The constructible orientation/component sheaf can carry a compact
split--remerge class even when every component branch escapes.  Explicitly,
for

\[
 A=\{(t,x):t^2+x^2>1\},\qquad \Omega=A\times\mathbb R^2\to\mathbb R_t,
\]

all fiber components are contractible open three-manifolds and all branches
reach infinity, yet the doubled interval `[-1,1]` supports an anti-diagonal
section of `R^3 pi_! Q` and `H_c^3(Omega;Q)=Q`.  Thus the cover-all column
still requires a no-split--remerge theorem or its exact top-sheaf
differential; four light parameters are not a proof.

This does not prove `s=4`.  Four exact proper pairwise-incomparable row-2599
signatures have simultaneous positive minimal circuits whose union is already
pencil-rigid, so incidence-only deletion cannot empty the retained complex.
The unresolved work is the compactification/restriction differential on the
remaining terms.  The full ledger is `FOURTH_DIAGONAL_FIVEFOLD.md`.

## Block-Gordan resolution and its exact limit

For every finite signature set `S`, allow zero witness blocks and impose only
one total normalization.  The resulting block-Gordan space `Gamma_S` maps
properly to `B_S`.  Its fiber over `Y` is the join of the nonempty normalized
witness polytopes `P_sigma(Y)`, hence is compact and convex, and proper base
change gives a functorial equivalence

\[
             R\Gamma_c(\Gamma_S;R)\simeq R\Gamma_c(B_S;R)       \tag{8}
\]

for every coefficient ring `R`.  This is the correct compactification: it
retains support drops, zero weights, and split--remerge attachments.

It is not by itself a vanishing theorem.  Filtering by the set `T` of
positive block masses gives

\[
 E_1^{p,q}=\bigoplus_{|T|=p+1}
 H_c^q\!\left(\bigcap_{\sigma\in T}B_\sigma;R\right),          \tag{9}
\]

exactly the compact-support Mayer--Vietoris spectral sequence.  Fixed-fiber
shelling therefore cannot remove the unresolved boundary maps.  A formal
exact family for every `s=3,...,8` has nonzero rows, full row span, proper
pairwise-incomparable feasibility regions, singleton normalized Gordan
fibers, and nevertheless nonzero `H_c^(s-1)(B_S;Q)`.  Any successful middle-
diagonal theorem must use the actual third-compound/Koszul identities.

There is one positive actual-OM foothold.  In the hard row-2599 triple, the
three one-exchange witness polytopes have `52/34/52` vertices.  Of their
`91,936` product corners, exactly `18,480` reach a pencil-flexible support,
and every such corner changes all three witness blocks.  An explicit product
of three true edges is a local three-cube whose far corner has degree vector
`(2,5,5,5,4,4,5,3)` and is killed by the pencil lemma.  The remaining target
is a coordinated cubical matching compatible across cofactor walls, zero
faces, and infinity.  Exact continuation of this cube reaches a common pencil
escape at the far corner and proves its entire component noncompact.  The
cofactor audit also finds an endpoint-specific residual wall across which one
chosen circuit dies while another survives.  An exact one-column continuation
now supplies the missing local reroute at that orbit-50 wall: the closed
four-circuit face transports to a replacement five-circuit while the other
two blocks remain strict, and the resulting union still has a two-plane
pencil escape.  This closes the hard endpoint wall for that component, not
the remaining pair/triple columns.  See `BLOCK_GORDAN_AUDIT.md`,
`BLOCK_GORDAN_TRIPLE_WALL_AUDIT.md`, and
`BLOCK_GORDAN_ENDPOINT_WALL_REROUTE.md`.

Five-circuit carrier coordinates provide a second exact chart, but not a
dimension reduction.  Scaling the five signed support normals by their
unique positive dependence fixes them to a projective frame, while label
degrees leave exactly nine carrier parameters.  An exact midpoint example
stays uniform and retains the five-circuit witness but flips four parent
brackets, so the natural carrier sign cell is nonconvex.  Sparse relative
CAD must retain oriented-ray lift chambers and all zero-weight faces; see
`BLOCK_GORDAN_CARRIER_CHART.md`.

For each fixed parent `Y`, the 56 triple-hyperplane arrangement is exactly the
essential discriminantal arrangement `B(8,4,Gale(Y))`: complementary Gale
five-circuits recover the 56 derived normals.  This explains why every fixed
extension-point fiber has a zonotopal, shellable tope complex and a
partial-cube graph.  It does not organize variation in `Y`; the 13 residual
walls are precisely where that discriminantal oriented matroid mutates.  An
exact row-2599 audit rejects every cyclic label order up to reorientation, so
the cyclic higher-Bruhat model does not apply, and its canonical packet wall
is a bracket-unit rather than a residual wall.  The viable replacement is a
constructible diagram of chamberwise zonotopes with explicit facewise
codimension-one mutation maps; higher coherence is handled below.  See
`BLOCK_GORDAN_DISCRIMINANTAL_AUDIT.md`.

The universal codimension-one specialization is now exact for all 13 types.
Nine are ordinary four-circuit walls and four are localization three-circuit
walls.  For a circuit-aligned support, its normalized kernel is a singleton
on the live side, the same singleton with one zero weight on the wall, and
empty on the other side.  Hence live-side-to-wall specialization is canonical
and integral.  There cannot be a direct cross-wall quasi-isomorphism natural
on every zero-weight coordinate face: on `H_0` it would have to send a
generator through a zero group.  The correct object is the cospan
`side -> wall <- side`, enlarged by circuit-elimination cells.  The exact
`Q4 -> P <- S4` reroute is the first such enlargement; see
`BLOCK_GORDAN_RESIDUAL_MUTATION_MAP_NO_GO.md`.

For every chosen opposite-side pair at any of the 13 generic residual wall
types, that enlargement is now universal.  If `P` is the positive wall
circuit and `u,v` are the opposite auxiliaries, positive circuit elimination
produces a support-minimal circuit `R` containing both.  The normalized
closed fibers form the interval cospan

\[
          [Q_-,R]\longrightarrow[P,R]\longleftarrow[Q_+,R],
\]

and both arrows are integral cellular isomorphisms with acyclic mapping
cones.  Ordinary walls require at most six normals and localization walls at
most five.  The exact representative census has 131 certified auxiliaries,
671 auxiliary pairs, and 2,420 persistent-support candidates.  Once such
codimension-one maps are actually defined facewise on a common subdivision,
convex coordinate faces of the block-Gordan polytope give integral coherent
homotopies in every higher codimension by the relative acyclic-carrier
theorem.  Hence there is no independent codimension-two-or-higher coherence
obstruction.  The remaining codimension-one case before allowing
cross-block transfers is a monochromatic wall star, where the fixed signature
supplies no opposite-side auxiliary on the feasible side.  See
`BLOCK_GORDAN_RESIDUAL_ELIMINATION_CELLS.md` and
`BLOCK_GORDAN_ALL_CODIM_COHERENCE.md`.

Monochromaticity is genuine, not a missing circuit search.  Exact uniform
rational examples realize it at every one of the 13 wall types, and Gordan's
alternative proves abstractly that no positive circuit of any support can
persist in the same block on the feasible side of a genuine loss.  There is
nonetheless a universal local pair escape: two one-auxiliary supports based
on one wall circuit use at most six derived triples, hence at most 18 parent
label incidences; among eight labels some degree is at most two.  All such
same-wall pair pieces therefore have a plane-pencil escape.  A strict
row-2599 three-block occurrence with degree vector `(4,4,6,4,5,5,3,5)` is
pencil-rigid, so the analogous triple claim is false.

The full block resolution repairs every codimension-one monochromatic loss.
If another block is bad on the receiving side, all dying mass transfers
linearly to a normalized witness in that block.  If every block dies, convex
retargeting moves each block to its own positive wall circuit.  All labeled
occurrences share the crossed global factor; their fixed bracket-unit
positive dependences persist on its whole wall, and every wall component is
noncompact.  They therefore have a simultaneous proper escape even when the
circuits differ and their union is pencil-rigid.  The exact row-2599 common-
circuit triple remains a small regression case, not a separate hypothesis.
The remaining middle-diagonal problem is a proper, globally acyclic
mass-transfer matching and its incidence cycles—not a multi-circuit all-die
escape or higher-wall coherence.  See
`BLOCK_GORDAN_MONOCHROMATIC_WALL_STARS.md` and
`BLOCK_GORDAN_MONOCHROMATIC_MASS_TRANSFER.md`, together with
`RESIDUAL_STRATUM_NONCOMPACTNESS.md`.

## Surviving strategies

1. **Labeled dual master-cell complex.**  Compactify the nine-dimensional
   parent cell and triangulate it compatibly with the primitive residual
   factors and infinity, retaining a regular refinement and its artificial
   faces.  Label each interior cell by the complete tope set of its derived
   oriented matroid.  For every family `S`, the barycentric dual
   blocks whose labels contain `S` form a complex homotopy equivalent to
   `F_S`.  For `s<=8`, the `s`-th diagonal uses only primal codimensions
   `8-s,9-s,10-s`; diagonal nine instead has the augmented degree-zero graph
   test.  In particular, diagonal eight is a codimension-two problem and
   diagonal seven is a codimension-three problem.  A
   label-preserving or antichain-width-safe discrete Morse matching can
   certify all admissible families at once.  This bypasses the large
   witness-support filtration; its first exact regression strengthens the
   row-2599 transverse-node theorem from connectedness to contractibility for
   every nonempty finite common support.  More generally, the all-strata
   gluing theorem proves that every bad point is the limit of bad generic
   chambers, even at singular or multiple wall intersections.  Hence every
   interior lower-cell label is the intersection of its incident chamber
   labels and no isolated local puncture can occur in the interior.  Infinity
   cells are excluded, not intersection-labeled.  Global cycles, complete
   codimension-two incidence, and infinity are the real
   diagonal-eight targets.  See
   `DUAL_MASTER_CELL_PROGRAM.md` and `verify_dual_master_node.py`.  The first
   parent-860 heuristic-to-exact pilot additionally falsifies connected-tree
   routing with one signature, repairs that obstruction and a subsequent pair
   obstruction by 16 all-factor-certified chords, and obtains connected
   finite intersections on its exact 24-chamber training network.  It is not
   a coverage theorem; see `DIAG9_PARENT860_CEGIS_ROUTING.md`.
2. **Sparse-form quotient plus CAD.**  Column scaling removes all but
   `beta<=4` invariant positive weight ratios from every generic pair orbit.
   The remaining equations ask that fixed sparse three-vectors vanish in a
   four-dimensional quotient.  The finite task is a relative-cohomology/CAD
   computation on these `9+beta` quotient variables, including lower-support
   faces.
3. **Real-tropical compactification after gauge.**  Pure column-torus paths
   are vertical gauge and cannot prove escape in `X`.  After quotienting
   them, nonzero real-tropical cones in the nine parent coordinates, bracket
   slacks, and invariant weight monomials detect genuine ends.  One must then
   compute the boundary incidence in degrees zero and one.
4. **Stratified double contraction.**  A formal second contraction lowers the
   base dimension from `6+2s` to `3+s`, but produces bilinear height fibers.
   Each fixed lift fiber is homotopy equivalent to an open subset of `R^5`,
   but that leaves three total-degree-seven Leray terms.  An exact constant-
   quotient line has feasible ends separated by a whole infeasible interval,
   ruling out linewise acyclicity, and an exact allowed seven-circuit has a
   unique fixed-weight height, ruling out universal kernel escape.  A global
   relative-Leray theorem with exit specialization remains possible.
5. **Bounded circuit descent.**  Diagonal `s` needs at most `(s+1)`-fold
   circuit intersections.  For `s=4`, construct relative cellular cochains
   only for the support-sieve survivors and assemble total degrees
   `2 -> 3 -> 4`; this is an exact finite target rather than an `E_1`
   vanishing shortcut.
6. **Ninth-diagonal master-chamber graph.**  Generic two-sided wall gluing is
   now proved, so `pi_0(F_S)` is exactly the component set of the chamber
   graph induced by chambers supporting `S`.  For a spanning tree and a
   cross-pair `u,v`, put `E_uv=T(u) intersection T(v)`.  If every tree
   waypoint `w` missing `d in E_uv` satisfies
   `width(E_uv intersection Inc(d))<=7`, then every proper nine-antichain has
   connected support.  This pairwise-width theorem is exact and its cut-SAT
   encoding is complete for any supplied labeled graph.  The former coarser
   union-cut condition is not complete: an exact finite example satisfies
   the ninth conclusion while every spanning tree fails that test.  The
   unresolved input is geometric, not SAT.  The first complete scoped
   roadmap now exists on the exact row-2599 coordinate line
   `Y(t)=Y_0+t E_(2,7)`, `-1/2<t<1/2`: exact Sturm coverage of all `84,840`
   residual occurrences gives 25 crossing parameters and 26 cells, with
   `26,112` signatures per cell and `26,232` in the union.  Every signature
   support is empty, full, a prefix, or a suffix, so every finite common
   support is empty or connected on this line.  The 65 labels at the
   exceptional crossing have rank-one ambient gradient and are transverse to
   the line.  A genuine embedded projective two-disk through that
   crossing is also complete.  On the disk, all 65 restrictions have exact
   gcd `1401176374297 s+849195472073 u`; its 32 constant and 33 affine
   quotients never vanish, and the other `84,775` residual restrictions and
   all 70 parent brackets remain nonzero.  Hence this disk is exactly two
   convex cells separated by one wall segment, with connected or empty common
   support for every finite family.  A full multivariate audit now proves
   that these 65 equations share the single global cubic
   `-bdi+bfg+cdh-ceg+cei-cfh`, not merely a plane restriction.  The next
   codimension-two test also passes exactly: a rational disk
   contains two coprime branches with `65+65` labeled occurrences and
   rank-two Jacobian.  Exact dominance excludes every other wall; the roadmap
   is a four-cycle of `26,112`-signature cells, four `26,040`-signature wall
   arcs, and a `25,968`-signature node.  Exact lower-stratum labels identify
   every individual support with the whole disk or one strict affine
   half-disk.  Every finite common support is therefore empty or convex, and
   hence contractible when nonempty; both the sharp tree and cut-SAT checks
   also pass.  What
   remains is coverage of all local intersection types and then a
   full-dimensional roadmap for each parent.
   Globally, exact localization reduces the `84,840` labeled residual
   occurrences to `26,740` primitive wall polynomials, with multiplicities
   `25,200 x 1`, `420 x 2`, `280 x 15`, and `840 x 65`.  Evaluating one
   exact representative of every factor on the 178 stored row-2599 charts
   gives 178 distinct sign states; 10,844 factors vary, and the pairwise
   Hamming distances range from 1,125 to 5,600.  This is a rigorous chamber
   lower bound, not adjacency or coverage.  A new exact recursive-tope audit
   strengthens the sampled evidence: all 97,224 signatures give 39,366
   distinct support traces, and every trace is exactly an intersection of
   sampled residual-factor halfspaces.  The certified line, disk, and node
   roadmaps are factor-isometric `P26`, `K2`, and `Q2`.  Neither fact supplies
   missing chamber coverage or adjacency.  Moreover, eliminating the 13
   canonical wall pivots against parent-bracket endpoints produces 142 new
   irreducible projection factors already in the first resultant layer, so a
   projection recursion restricted to the existing bracket/residual catalog
   cannot close without adding new factors.
   The full-support feasibility audit now adds an exact complementary
   theorem.  Positive identities in the target-signed parent brackets prove
   that 1,177 of the 6,980 segment-open candidates have empty zero sets in
   the strict row-2599 parent cell, leaving 5,803 explicit unknowns.  The
   direct parent-product subfamily contains 965 factors; floating-point cone
   search is discovery-only and every accepted identity is replayed by
   literal integer polynomial equality.  An adversarial directed-sign audit
   also corrects a false shortcut: moving-column permutations preserve only
   the unsigned parent-divisor arrangement, flip 19--27 of the 63 distinct
   signed parent inequalities, and send all 525 nonidentity transports of
   the 105 safe segments outside the row-2599 cell.  Hence there is no valid
   994-factor symmetry residue or 264-class quotient.
   See `DIAG9_SIGN_GEODESY_AUDIT.md`,
   `DIAG9_GRAPH_GLOBAL_FACTOR_CENSUS.md` and
   `DIAG9_GRAPH_ROW2599_FACTOR_STATES.md` and
   `DIAG3_PAIR_FULLSUPPORT_BLOCK_SYMMETRY.md` and
   `DIAG3_PAIR_FULLSUPPORT_PARENT_PRODUCT_SIGNS.md`.
   There is now a family-adaptive proof-level reduction before any roadmap is
   built.  A factor is active for a signature exactly when one of its labeled
   wall circuits is aligned with that signature.  Imposing the consistent
   allowed signs of the factors active for a family gives a sector `H_S`,
   and `F_S` is a union of connected components of `H_S`; inactive-factor
   walls cannot change feasibility and may be contracted.  Conflicting
   transported circuit identities first certify 8,916 row-2599 factor walls
   empty, leaving 17,824 candidates; the two hard nine-families then use only
   3,539 and 3,638 candidate-active factors.
   Their endpoints differ on 5,198 and 3,320 full factor signs but on zero
   active signs, explaining why the exact paths safely cross thousands of
   walls.  This does not prove that an active sector is connected or handle
   infinity.  See `DIAG9_ACTIVE_SECTOR_THEOREM.md` and its exact verifier.
   The sorted 17,824-factor complement is now a 71,316-byte hash-pinned input
   independently replayed from the row-2599 integer realization.  The ambient
   compactification is also fixed: the three moving positive projective
   columns give `(Delta^3)^3`, covered by 64 exact gauge charts.  All 262,144
   chart cocycles hold, and the three standard infinity divisors are the
   genuine parent walls `[2346]`, `[2347]`, and `[2348]`.  Canonical
   multihomogeneous Bernstein restriction across all 3,375 support faces now
   eliminates 42,547,692 of 60,156,000 factor--face tasks exactly; 17,608,308
   mixed restrictions remain.  The signed parent-face gate then excludes
   3,364 of 3,375 supports and reduces the mixed residue to 70,218.  Its
   support one-skeleton has two residual-wall-free edges, and the sole
   two-face is the unit square split by `a=h`.  The remaining gap begins with
   the two surviving four-dimensional supports, not the factor universe,
   compactification, face pruning, or support dimensions at most two.  See
   `DIAG3_PAIR_GLOBAL_CANDIDATE_FACTOR_INPUT.md` and
   `DIAG3_PAIR_GLOBAL_COMPACTIFICATION_ATLAS.md` and
   `DIAG3_PAIR_GLOBAL_FACE_BERNSTEIN_ATLAS.md` and
   `DIAG3_PAIR_GLOBAL_PARENT_FACE_GATE.md`.
   Smooth transverse wall pairs supply the expected local four-cycle, but
   exact semialgebraic countermodels show that smoothness alone implies
   neither global COM face symmetry/strong elimination nor support
   convexity.  Finally, deletion of a reducible parent element gives the
   safe equivalence `F_S(M) ~= G_(e,S)` with convex insertion fibers, where
   `G_(e,S)` is the nonempty simultaneous-insertion locus in the restricted
   `S`-indexed private-witness incidence space (duplicate deletion signatures
   are not merged).  An exact proper extension of the
   reducible alternating parent `A(4,8)` shows that this locus can be proper;
   reducibility is not hereditary under extension and therefore does not
   collapse the 2,546 reducible catalog parents by induction.  See
   `DIAG9_GRAPH_COM_AUDIT.md` and `DIAG9_GRAPH_REDUCIBILITY_AUDIT.md`.
   The strongest row-2599 sample separator found so far is now eliminated by
   an exact 22,711-segment coordinate path.  A separate seven-chart
   Gordan/witness certificate proves that its nine signatures really do form
   a proper pairwise-incomparable family; this is not merely sampled
   incomparability.  The coordinate-path theorem proves universally that
   `Z_S -> F_S` preserves components, one-column fibers are convex, and
   rational one-column chains are a complete positive certificate language.
   These results certify the displayed endpoint pair, not connectivity of its
   entire `F_S` or of every ninth-diagonal instance.
7. **Feasible COM completion (a bypass, not a diagonal proof).**  A
   rank-at-most-nine COM containing all maximal feasible support states would
   imply integral `9`-Lerayness of the compatibility complex and the desired
   ten-local Helly conclusion directly.  It would not prove the homology
   groups in (1) vanish.  This is a finite but stronger downstream target;
   existing exact examples rule out several naive partial-cube shortcuts.
8. **Signed-gradient KKT sieve.**  Free-log convexity is exactly false, but a
   relatively compact generic residual chamber must satisfy the
   positive-dependence equation (6a).  For at most nine nonconstant sides,
   full column rank of
   the logarithmic gradient matrix excludes a compact chamber; for ten sides,
   its rank-nine kernel must be strictly positive.  Exhausting those signed
   semialgebraic kernel conditions on the actual `5+5` survivors is a sound
   second-diagonal filter.  It does not handle lower-dimensional boundary
   strata or the global `d_1` incidence map by itself.
9. **Independent-witness frames.**  After projectivizing private columns, the
   rank-at-most-three witness locus has codimension `s-3`.  General position
   identifies the diagonal group with the homology of the full-rank witness
   stratum for `s=7,8,9`.  This is only a reduction.  An exact proper
   incomparable four-signature family has positively oriented independent
   witness frames at both ends of the saved affine line, while one signature
   is Gordan-infeasible on the middle interval.  Thus full-rank restriction
   does not restore projected linewise convexity; fixed-frame compatibility
   remains open.  See `WITNESS_FRAME_STRATIFICATION.md`.

An exact stress test also prevents a false shortcut from entering the graph
program.  Two far-apart row-2599 charts numbered 12 and 37 looked separated
by nine signatures on the available 178-chart sample.  They are in fact
joined inside the common nine-signature feasibility locus by an exact path of
`22,711` rational one-column segments.  Every constrained determinant is
affine on each segment, and the verifier checks strict integer endpoint
signs.  Thus the sampled separator is false.  This does not prove global
ninth-diagonal connectivity; it supplies a reusable exact
coordinate-reachability regression for any chamber enumerator.

A second independently generated stress candidate, charts 37 and 176, is
likewise joined by an exact rational path of `22,811` one-column segments.
Its separate exact Gordan/feasibility certificate proves that the nine
regions are nonempty, proper, and pairwise incomparable.  This confirms that
the first path was not an isolated numerical accident, but it still refutes
only a sampled separator: 178 point charts are not a chamber roadmap.

## Exact artifacts

- `ATLAS_HELLY.md`: full theorem/proof ledger.
- `PARENT_CONTRACTIBILITY_AUDIT.md`: all-nine duality source audit.
- `SECOND_DIAGONAL_COFINAL_COVER.md`: cofinal cover and exchange boundary.
- `DIAG2_PIVOT_DUAL_SINGLE_BAD_ESCAPE.md` and its exact checker: integral
  `H_tilde_7` vanishing for every rank-four/nine-element realization space
  and the resulting `H_c^1(B_sigma)=0` theorem.
- `SECOND_DIAGONAL_SINGLE_REGION_H7_AUDIT.md` and its exact checker:
  independent reconstruction of the Gale quotient, complementary-minor
  signs, sharp escape, and supported-duality degrees.
- `DIAG2_EXCHANGE_SATURATED_SUPPORT_DROP.md` and the exact generic-birth
  support/signed verifiers: the all-strata pointwise exchange theorem,
  clopen compact-component alternative, three ordinary `4+4` UNSAT
  certificates, ten wall-disjoint `4+5` residues, and the integral proof of
  diagonal two.
- `SECOND_DIAGONAL_DEFECT_TWO.md`: matching-star dichotomy, exact proper
  incomparable defect-two pair, and its certified pointwise boundary escape.
- `SECOND_DIAGONAL_MATCHING_STAR_LOCAL_NO_GO.md`: exact warning that a local
  matching star in the global defect-one case need not have a root-free
  frozen-support partner ray; its first useful support pivot still escapes.
- `DIAG2_PIVOT_BLOCK_GORDAN_NO_GO.md` and `DIAG2_PIVOT_VERIFY.py`: exact
  failure of vertical/support-only pivot matchings and the complete
  parent-16 defect-two wall fan.
- `DIAG2_PIVOT_COMPONENT_GRAPH.md`,
  `DIAG2_PIVOT_UNIVERSAL_WALL_THEOREM.md`, and their exact verifiers: the
  component-decorated 51-spoke wall theorem, exact parent-16 unimodular
  escape, and the exhaustive residual support-orbit bounds.
- `DIAG2_PIVOT_ALL_COMPACT_SECOND_WALL.md` and its exact verifier: primitive
  `K_52` first-wall kernel and the theorem forcing every compact strict spoke
  to a different residual wall.
- `DIAG2_PIVOT_CONE_FARKAS.md` and its exact verifier: a realizable proper
  incomparable opposite-gradient obstruction, together with its exact
  omitted-label tangent escape.
- `DIAG2_PIVOT_REPRESENTATIVE_GRADIENTS.md` and its exact verifier: all 66
  bracket-product Jacobian certificates for distinct canonical residual
  pairs, with the labeled-pair and triple boundary stated explicitly.
- `DIAG2_PIVOT_LABELED_PAIR_THEOREM.md` and its exact verifier: all 9,476
  unordered relative-label factor-pair orbits, 9,226 projective-frame
  bracket-minor certificates, 128 affine/torus escapes, and the exact
  122-orbit affine-fiber closure.
- `DIAG2_PIVOT_ALL_PAIR_FIBERS.md` and its exact verifier: complete
  `9,476/9,476` pair-wall noncompactness, including all former
  factor-family-49--51 residues.
- `DIAG2_PIVOT_49_PAIR_SATURATION.md` and its exact verifier: localized
  critical ideals equal to one for all seven type-`(49,49)` residues and
  their componentwise fiber-linear noncompactness theorem.
- `DIAG2_PIVOT_49_50_PAIR_SATURATION.md` and its exact verifier: the same
  saturation for four of the six type-`(49,50)` residues, and the
  affine-fiber argument for the other two.
- `DIAG2_AFFINE_FIBER_RESIDUE_CLOSURE.md` and its exact verifier: a
  single-variable refinement of the fixed-minor lemma that closes 6,886 of
  6,890 candidate pairs across all five hard factor-type families at once,
  reducing that canonical-presentation verifier's residue from 115 to the
  exact four pairs `(50,7861),(50,7977),(50,12128),(50,20046)`; the stronger
  stabilizer-aware all-pair theorem above subsequently closes all four.
- `DIAG2_CONIC_FACTORIZATION_ESCAPE.md` and its exact verifier: a genuine
  partial reduction, not a closure, for pairs whose restricted polynomial is
  a plane conic in two coordinates rather than affine in one; shows
  `(50,7977)`'s conic discriminant is an exact perfect square (ruling out a
  bounded ellipse) but documents, rather than closes, the remaining gap (the
  natural escape ray is a transversal probe, not a path on the zero locus)
  after adversarial review caught an earlier overclaimed version.  This
  checker leaves the same four method-local exceptions, all of which are
  subsequently closed by `DIAG2_PIVOT_ALL_PAIR_FIBERS.md` using different
  stabilizer-equivalent affine presentations.
- `DIAG2_PIVOT_REPRESENTATIVE_TRIPLES.md` and its exact verifier: 171
  canonical rank-three certificates, four exact uniform rank-two witnesses,
  and the 45-triple saturation residue.
- `DIAG2_PIVOT_REPRESENTATIVE_TRIPLE_FARKAS.md` and its exact verifier: exact
  dependence signs for all four rank drops and the tangent escape of the only
  common positive canonical triple wall.
- `DIAG2_PIVOT_RANK3_PROGRAM_AUDIT.md`: exact bookkeeping no-go for treating
  the two height rows as a rank-three Euclidean oriented-matroid program.
- `FREE_LOG_COORDINATE_OBSTRUCTION.md` and
  `verify_free_log_nonconvex.py`: exact failure of parent/residual free-log
  convexity, surviving coordinate-section theorem, and the KKT residue.
- `THIRD_DIAGONAL_E1_REDUCTION.md`: exact 45-orbit generic reduction,
  beta-one survivor, stabilizer test, and sharpness ledger.
- `THREE_SHEAR_SINGLE_PIECE_REDUCTION.md`: all-support proof that the full
  third-diagonal single-piece column vanishes below compact-support degree
  three, the safe omitted-support degree-three upgrade, and the exact
  split--remerge obstruction to extending it to cover-all supports.
- `DIAG3_SINGLE_BAD_TWO_SKELETON.md` and its verifier: the proper
  coordinate-face filtration proving `H_c^q(B_rho;R)=0` for `q<=2`, every
  ring, plus the same low-degree theorem for every primitive residual wall.
- `THIRD_DIAGONAL_SUPPORT_FILTER_AUDIT.md`: independent symbolic/rational
  reconstruction of the generic support census.
- `DIAG3_TRIPLE_FACTOR_REDUCTION.md` and its exact Burnside verifier:
  nested support-drop reduction of triple compact components to at most
  three primitive factor walls, plus the exact `79,102,449`-orbit endpoint.
- `DIAG3_PROJECTIVE_COLUMN_FIBER_COMPRESSION.md`,
  `DIAG3_TRIPLE_SEQUENTIAL_AFFINE_COMPRESSION.md`,
  `DIAG3_TRIPLE_DOUBLE_GRAPH_COMPRESSION.md`,
  `DIAG3_TRIPLE_UNIT_MINOR_AFTER_GRAPH.md`,
  `DIAG3_TRIPLE_DIRECT_FINAL_AFFINITY.md`,
  `DIAG3_TRIPLE_PRIMITIVE_FINAL_DIRECTION.md`, and
  `DIAG3_TRIPLE_PRIMITIVE_FINAL_SUPPORT3.md`, their replayers, and compact
  data: exact positive component escapes for `77,940,147` triple orbits,
  leaving `1,162,302`, with negative-search maximality kept separate from
  the replayed identities.
- `DIAG3_TRIPLE_COMMON_SCALING_NO_GO.md` and its two exact replayers:
  exhaustive full-rank rejection of common normalized-coordinate scalings on
  all `1,162,302` final rows, plus five full-rank hard-canary rejections of
  quadratic ideal-preserving vector fields with affine multipliers.
- `DIAG3_CONCURRENCE_NORMAL_FORM.md` and its verifier: the four-bilinear
  generic concurrence chart, exact degree-20 internal ramification RUR, and
  the all-26,740-factor proof that the ramification point has no fourth
  residual factor.
- `DIAG3_PAIR_DIFFERENTIAL_ENDS.md` and its verifier: the exclusive-pair and
  balanced-end exact sequence, explicit relative cochain matrices `N,M`, and
  coefficient-universal split-contraction criterion.
- `DIAG3_PAIR_LOCAL_ROOT_SWITCH.md` and
  `DIAG3_PAIR_FACTOR_ROOT_SWITCH.md`, with their exact SAT/cellular replays:
  universal single-wall root switching and generic same-factor two-signing
  root/occurrence contractions, with frontier and higher-cycle scopes kept
  explicit.
- `DIAG3_PAIR_FOUR_RAY_REFINEMENT.md`,
  `DIAG3_PAIR_RECEIVER_END_CANARY.md`, and their exact verifiers: the complete
  one-dimensional factor-star/end census and its primitive free residue.
- `DIAG3_PAIR_TANGENTIAL_SHIFT_AUDIT.md` and its exact ribbon replay: the
  two-dimensional `E_02` survivor, sharp local-product no-go, and sufficient
  proper-filtration replacement.
- `DIAG3_PAIR_GLOBAL_MASTER_QUOTIENT.md` and its exact replayers: the
  master-poset quotient, canonical barycentric integral lift, covered local
  rank regressions, and machine-readable proof that the existing row-2599
  records contain no global closure/infinity complex.
- `DIAG3_ARCHITECTURE_ADVERSARIAL_AUDIT.md` and its exact regressions: the
  invariant triple/pair obligations, the sufficient mod-two pair criterion,
  fixed-order root no-go, and normalized-Gale zero-locus no-go.
- `DIAG3_TRIPLE_GALE_CANARY_NO_GO.md` and its Python/C++ replay: corrected
  full-occurrence Gale pullbacks and all-`S_8` hard-canary no-gos for the
  existing square-affine, triangular, coordinate-unit, and sparse-plane
  certificate families.
- `DIAG3_PAIR_ATLAS_TANGENTIAL_FILL.md` and its exact verifiers: the complete
  bottom-edge and two-parameter frontier audit, the genuine proper
  row-2599 strip contraction, and the retained generic first-exit jump
  regression.  This fills one canary, not the global pair complex.
- `DIAG3_TRIPLE_CREMONA_FRONTIER_NO_GO.md` and its exact verifier: the full
  standard-Cremona target-bracket classification, source-uniform frontier
  witnesses, torus-isomorphism obstruction, and bounded hard-canary screens.
- `DIAG3_TRIPLE_CONTRACTION_NO_GO.md` and its exact verifier: the
  decomposable alternating `H_6` model and the honest one-loop specialization
  showing why a contraction proof needs the complete loop-face complex.
- `DIAG3_PRIVATE_TRIPLE_LOOP_COMPLETION.md` and its exact verifier: the
  four-trace private-independence theorem, complete 928-cell ambient loop
  complex, catalog census, and explicit good-locus/triple-bad scope firewall.
- `DIAG3_JOINED_FLOW_TRIANGLE.md` and its verifier: the integral local
  flow-triangle two-skeleton, its primitive top relation, and the proof that
  the missing mixed three-cell cannot bypass triple-intersection
  noncompactness.
- `DIAG3_ROW2599_P01_TANGENT_COLLAR.md` and its verifier: an exact nonradial
  four-stage repair of the exceptional `p01` relative pair-wall collar.  All
  three pair edges now have local relative collars.
- `DIAG3_ROW2599_P01_COMPARISON_PRISM.md` and two independent exact verifiers:
  five rational bivariate patches certify the first complete singular
  comparison incidence with boundary
  `+K(p01)-Q(p01,block0)+Q(p01,block1)`.
- `DIAG3_ROW2599_PAIR_COMPARISON_PRISMS.md` and two independent exact
  verifiers: two patches each certify the `p12` and `p20` incidences.  The
  pair-edge comparison subtotal is `3/6`; the next bullet records the first
  singleton gluing.
- `DIAG3_ROW2599_H2_COMPARISON_PRISM.md` and two independent exact verifiers:
  four trivariate patches join the two block-2 pair laterals literally.  The
  local count is `4/6`; `H0`, `H1`, and the mixed `d3` cell remain open.
- `DIAG3_DOUBLE_CONTRACTION_LERAY_AUDIT.md`: the dimension-matched
  multiconvex-fiber audit and sharp `S^6` obstruction to inferring the target
  homology from fixed-row convexity.
- `DIAG3_STRATEGY_CHECKPOINT.md`: the bounded route/tooling audit, retired
  shortcuts, and the two finite frontier-aware certificates still required.
- `DIAG3_TRIPLE_QUADRATIC_COVER_NO_GO.md` and its exact verifier: all seven
  direct `L` resultants expand after parent-factor stripping, and the
  reduced `P=L=0` discriminant has both signs on the exact parent atlas.
- `DIAG3_TRIPLE_FACTORED_KOSZUL_GATE.md`: exact three-function directional
  reduction, exhaustive ten-minor audit, and the bounded algebraic stop rule.
- `DIAG3_PAIR_GLOBAL_CANDIDATE_FACTOR_INPUT.md`,
  `DIAG3_PAIR_GLOBAL_COMPACTIFICATION_ATLAS.md`, and
  `DIAG3_PAIR_GLOBAL_FACE_BERNSTEIN_ATLAS.md`: independently verified
  17,824-factor generator input, the exact 64-chart `(Delta^3)^3`
  compactification with genuine parent-wall infinity, and exact deletion of
  42,547,692 of 60,156,000 factor--face subdivision tasks.
- `DIAG3_PAIR_GLOBAL_PARENT_FACE_GATE.md`: exact exclusion of 3,364 of 3,375
  compactification supports, reduction to 70,218 mixed restrictions, the
  residual-wall-free support one-skeleton, and the diagonal two-face
  cellulation.
- `DIAG3_PAIR_CARRIER_GRAPH_AUDIT.md` and its exact verifier: full ordered
  two-root `Lambda^3` carrier graphs on all 178 stored minimum-overlap pairs,
  including the chart-57 commuting-only disconnect and bilinear repair.
- `FOURTH_DIAGONAL_FIVEFOLD.md`: direct parent `H_5` escape, all-diagonal
  `(s+1)`-fold truncation, fourth-diagonal top-fiber sieve, and exact no-go.
- `BLOCK_GORDAN_AUDIT.md`, `BLOCK_GORDAN_FORMAL_NO_GO.py`, and
  `BLOCK_GORDAN_HARD_TRIPLE_PIVOT.py`: the functorial compact resolution,
  its formal limitation, and the exact coordinated hard-triple pivot cube.
- `BLOCK_GORDAN_TRIPLE_WALL_AUDIT.md`: exact common-pencil escape for that
  cube and the endpoint-specific residual wall that forces rerouting.
- `BLOCK_GORDAN_ENDPOINT_WALL_REROUTE.md`: exact zero-face-coherent
  circuit-elimination reroute through the hard orbit-50 endpoint wall.
- `BLOCK_GORDAN_CARRIER_CHART.md`: strict five-circuit carrier quotient,
  oriented-ray correction, and exact nonconvex carrier-cell obstruction.
- `BLOCK_GORDAN_DISCRIMINANTAL_AUDIT.md`: exact fixed-fiber discriminantal
  identification, cyclic higher-Bruhat exclusion, and the chamberwise
  zonotope mutation target.
- `BLOCK_GORDAN_RESIDUAL_MUTATION_MAP_NO_GO.md`: all-13 integral
  live-side specialization and the zero-face naturality obstruction to a
  direct cross-wall quasi-isomorphism.
- `BLOCK_GORDAN_RESIDUAL_ELIMINATION_CELLS.md`: universal enlarged-support
  interval carriers for every chosen opposite-side pair at all 13 wall types.
- `BLOCK_GORDAN_CODIM2_DIAMOND_AUDIT.md`: relative acyclic-carrier coherence
  at the exact transverse node once the codimension-one face maps exist.
- `BLOCK_GORDAN_ALL_CODIM_COHERENCE.md`: the dimension-independent integral
  carrier theorem and its compact-support/properness qualifications.
- `BLOCK_GORDAN_MONOCHROMATIC_WALL_STARS.md` and its exact verifier: actual
  monochromatic examples for all 13 types, the universal same-wall pair
  escape, and a strict pencil-rigid triple obstruction.
- `BLOCK_GORDAN_MONOCHROMATIC_MASS_TRANSFER.md` and its exact verifier:
  universal receiver-block transfer, common-global-factor all-die escape,
  and the exact proper incomparable row-2599 regression triple.
- `BETA0_MIXED_ESCAPE.md`: exact closed-stratum escape theorem for all three
  stored row-2599 `4+5, beta=0` occurrences.
- `DIAG2_MOVING_WITNESS_SHEAR.md` and its exact verifier: conditional
  simultaneous component escape by inverse-exterior witness transport, the
  low-source XOR reduction, 65 row-2599 hard occurrences, and the parent-16
  defect-two regression.
- `DIAG2_ESCAPE_SET_TOPE_REDUCTION.md`, `DIAG2_ESCAPE_SET_ATLAS178.md`, and
  their exact verifiers: the complete-tope restriction criterion, 112-shear
  masks, and pairwise intersection on all 178 stored parent-2599 charts.
- `DIAG2_COMMON_SHEAR_PARENT2604.md`, its compiled exact kernel, strict
  summary, and verifier: one matrix-pinned representative of all 2,604
  realizable parent chirotopes, 106,957,822 bad signatures, and a global
  six-direction pair-overlap margin.
- `DIAG2_ESCAPE_MINIMAL_SEPARATORS.md` and the antipodal/separator verifiers:
  universal sign-reversal symmetry, minimal source-local separator
  compression, and the exact eight-source-cover obstruction.
- `DIAG2_NEAR_COUNTEREXAMPLE_OBSTRUCTION.md` and its three exact verifiers:
  the complete overlap-at-most-eight atlas, exact four-singleton separator
  profiles, and the shared-parent GP obstruction for all three colored
  linear-`8_3` symmetry types.
- `DIAG2_EXTREMAL_SEPARATOR_BIFURCATIONS.md` and its two exact verifiers:
  separator-dominance monotonicity on an isolated extremal type-50 edge and
  the 216-chart, 648-pair three-parent bifurcation survey.
- `DIAG2_EXTREMAL_UNDOMINATED_BIRTH.md` and its exact verifier: a mixed
  undominated singleton birth on an isolated type-49 edge, the exact
  `67 -> 61` mask loss and `15 -> 9` pair-overlap transition, and the
  birth-budget reduction to potentially gap-closing births.
- `DIAG2_EXTREMAL_LINE_TRANSITION_CENSUS.md` and its exact verifier: complete
  exact coverage of the parent-187 `e`-line, 1,721 residual walls, and no
  overlap below six among the three tracked extremal pairs.
- `DIAG2_EXTREMAL_TRANSITION_DISK_FRONTIER.md`,
  `DIAG2_EXTREMAL_TRANSITION_DISK_SEEDS.md`, and their two exact verifiers:
  the bounded parent-187 `d/e` hexagon, effective 139-factor link frontier,
  and ten wall-exclusive transverse seed nodes with forty complete chamber
  tables, without collar or disk coverage.
- `DIAG2_ROBUST_MUTATION_SQUARES.md` and its exact verifier: fixed-direction
  common shears across two complete four-cell residual squares, including
  wall/node limits and exact local-germ provenance.
- `DIAG2_CANONICAL_ROBUST_EDGES.md` and its exact verifier: all thirteen
  canonical residual incidence types pass a two-sided robust-mask audit,
  covering 12,091,441,965 decorated pairs with minimum overlap nine.
- `DIAG2_GENERIC_BIRTH_PATTERN_REDUCTION.md` and its five exact verifiers:
  the 32-to-eight localization UNSAT quotient, the ordinary
  `53 -> 23 -> 10` signed support reduction, the exact 35-factor selected-pair
  cofactor footprint, the two-orbit distinct-second-wall `4+4` residue, two
  transverse realized selected-witness obstructions with proper incomparable
  signature pairs whose masks intersect in 51 and 80 directions, and the
  exhaustive 208,262-pair type-50 circuit-exchange repair, without universal
  wall-sector closure.
- `TORUS_TROPICAL_ESCAPE.md`: vertical-gauge no-go, exact face cones, and the
  quotient tropical strategy.
- `NINTH_DIAGONAL_SAFE_GRAPH.md`: exact connectivity reduction, finite
  budget-nine separator test, and all-strata theorem reconstructing every
  lower-cell label from its incident chamber germs.
- `NINTH_COORDINATE_PATH_THEOREM.md`: universal incidence/coordinate-path and
  common-cone bridge theorems, with exact scope.
- `NINTH_CANDIDATE_12_37_EXACT_PATH.md`: exact row-2599 proper-antichain audit
  and a 22,711-segment path killing the charts-12/37 sample separator.
- `DIAG9_GRAPH_TREE_CERTIFICATE.md`, `DIAG9_GRAPH_verify_tree_certificate.py`,
  `DIAG9_GRAPH_cut_sat.py`, and `DIAG9_GRAPH_inventory.py`: the sharp
  pair-specific tree theorem, complete cut-SAT layer, coarse-test no-go, and
  exact roadmap inventory.
- `DIAG9_GRAPH_ROW2599_ROADMAP.md` and its exact line, slice, Jacobian, and
  tope verifiers: the complete 26-cell row-2599 coordinate-line roadmap and
  the precise two-dimensional coverage boundary.
- `DIAG9_GRAPH_ROW2599_DISK.md`, its exact verifier, and its two NPZ
  certificates: a projectively embedded two-dimensional disk with complete
  residual coverage and one certified wall branch.
- `DIAG9_GRAPH_verify_row2599_node.py` and its roadmap/graph NPZs: the first
  complete transverse two-wall node with four exact cells and convex-or-empty
  all-family supports.
- `DUAL_MASTER_CELL_PROGRAM.md` and `verify_dual_master_node.py`: the finite
  dual-block truncation and Morse-certificate program, plus an independent
  replay of the exact row-2599 codimension-two contractibility theorem.
- `DIAG9_PARENT860_CEGIS_ROUTING.md`, its two exact checkers, and three NPZ
  artifacts: a 23-chamber coordinate-star no-go to naive tree routing and a
  16-chord, 24-chamber network with connected support for every finite family
  on that network, without a claim of full parent-cell coverage.
- `RESIDUAL_STRATUM_NONCOMPACTNESS.md` and its exact verifiers: global graph
  charts for individual walls, fixed-minor pair/triple noncompactness, the
  common-factor all-die escape, and the sharp arity-eight abstract no-go.
- `DIAG9_GRAPH_GLOBAL_FACTOR_CENSUS.md`, its exact replay, and NPZ: reduction
  of 84,840 labeled residual occurrences to 26,740 primitive global wall
  factors, including the exact common cubic at the 65-label crossing.
- `DIAG9_GRAPH_ROW2599_FACTOR_STATES.md`, its exact replay, and NPZ: 178
  distinct exact residual sign states and the 10,844 varying-factor lower
  bound inside parent 2599.
- `DIAG3_PAIR_FULLSUPPORT_BLOCK_SYMMETRY.md` and its exact verifier: the
  directed-sign correction proving that unsigned moving-column symmetry does
  not preserve the row-2599 parent cell, including the 525-segment no-go.
- `DIAG3_PAIR_FULLSUPPORT_PARENT_PRODUCT_SIGNS.md` and its exact verifier:
  1,177 fixed-sign empty-zero-set certificates, leaving 5,803 full-support
  factors unresolved without a symmetry quotient.
- `DIAG9_SIGN_GEODESY_AUDIT.md` and its exact verifier: factor-isometry of
  the three certified local roadmaps, exact factor-halfspace closure of all
  39,366 support traces on the 178 charts, and the 142-new-resultant no-go to
  a projection recursion restricted to the existing equation catalog.
- `DIAG9_ACTIVE_SECTOR_THEOREM.md` and its exact verifier: the theorem that
  common feasibility is a union of active-sector components, plus the exact
  8,916-factor empty-wall certificate and 3,539/3,638 candidate-active
  reductions for the two hard row-2599 families.
- `DIAG9_GRAPH_COM_AUDIT.md` and its exact verifiers: the transverse local COM
  diamond and exact no-go to inferring global COM axioms from smoothness.
- `DIAG9_GRAPH_REDUCIBILITY_AUDIT.md` and its exact verifier: the safe
  simultaneous-insertion equivalence and a proper-extension obstruction to
  reducibility induction.
- `NINTH_CANDIDATE_37_176_EXACT_PATH.md` with the two corresponding files in
  `data/`: a second exact proper nine-antichain path, with 22,811 segments.
- `DIAG2_WITNESS_EXCHANGE_AUDIT.md` and its two exact verifiers: a realizable
  arbitrary-witness compatibility falsifier, its one-circuit repair, the
  complete 646,880-pair circuit census, and the 112-direction set target.
- `WITNESS_FRAME_STRATIFICATION.md` and
  `verify_witness_frame_stratification.py`: codimension reduction to the
  independent-witness stratum for `s=7,8,9`, plus an exact full-frame affine
  no-go for a proper incomparable four-signature family.
- `verify_ninth_candidate_path.py` with
  `data/ninth_candidate_12_37_path.npz`: exact 22,711-segment path refuting
  the row-2599 sampled ninth-diagonal separator candidate.
- `verify_ninth_candidate_antichain.py` with
  `data/ninth_candidate_12_37_antichain.npz`: 63 exact feasible-ray/Gordan
  witnesses proving the same nine regions are proper and pairwise
  incomparable.
- `DOUBLE_CONTRACTION_FIBERS.md`: the one-row fiber theorem and exact
  disconnected-slice obstruction.
- `DIAG2_PIVOT_DOUBLE_FIBER_KOSZUL.md` and its exact verifier: the seven-row
  constant-row theorem and an honest unique-height obstruction to universal
  Koszul-kernel escape.
- `verify_three_shear_single_piece_filter.py`: exact 45-orbit audit of the
  third-diagonal single-piece theorem.
- `verify_fourth_single_piece_light_count.py`: exhaustive `4,216,422`-support
  audit for the omitted/cover-all fourth-diagonal split.
- `verify_third_diagonal_full_tensor_rigidity.py`: exact colex-aware modular
  rank certificate showing the hard triple has only scalar common tensor
  stabilizers.

No artifact in this list claims that entries `s=3,...,9` are proved.
