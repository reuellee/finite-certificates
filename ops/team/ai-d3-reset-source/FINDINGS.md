# Independent audit of the compact relative source draft

Status: `PROVED_WITH_EXPLICIT_INTERPRETATIONS / INFORMATIONAL / AWAITING_INDEPENDENT_REVIEW`.
Input checkout: `fcb64825335245e6e53512bf4eb2c5f5279b75ae`.
Scope: the September 4 five-clause draft; all components of every realizable
uniform labeled rank-four parent on eight elements; any finite signature
family (in particular every ordered proper incomparable triple).

The five mathematical source clauses admit a proof. They require precise
meanings of *projective quotient*, *block-mass filtration*, and *triangulation
of the open complement*. The proof below gives those meanings and supplies
the missing filtered naturality argument. It uses no D3 vanishing conclusion,
no sampled parent component, no continuous choice of a Gordan witness, and
no triangulation theorem for an arbitrary map.

This is an existence and effective-computability result. It is not a
materialized all-parent simplicial certificate, a parent-specific vanishing
lemma, or a proof of either D3 invariant. The asserted `7 -> 3` decrease is
not justified as a decrease in the project's current certificate obligations.
The current seven-node count and `2/9` ledger must remain unchanged pending
independent review of the precise node meanings. The source existence
problem itself can stop here; further source machinery alone cannot prove
the missing topology.

## 1. Exact statement proved

Choose the representative chirotope with `chi(1234)=+1`. Let `R_chi` be the
space of real `4 by 8` matrices with exactly this sign pattern on all 70
four-column determinants. Use the quotient

`Q_chi = R_chi / (GL^+(4,R) x (R_{>0})^8)`.

Equivalently, allow matrices with chirotopes `chi` or `-chi` and quotient
by all of `GL(4,R)` and positive column scalings. Independent negative
column scalings are not in this quotient; the columns are oriented rays.
Labels are fixed. A quotient by label permutations is a different object.

There is a bounded semialgebraic global section `X_chi` homeomorphic to
`Q_chi`, embedded in the product of three open three-simplexes. Let
`Xbar=cl(X_chi)` in the corresponding product of closed simplexes and
`I=Xbar\X_chi`. Define the actual polynomial derived normals in this
section by

`a_J(Y)^T p = det[y_j1,y_j2,y_j3,p]`, `J={j1<j2<j3}`,

and `A_sigma` by the signed rows `sigma_J a_J(Y)^T`. Put

`P_sigma(Y)={lambda>=0 : sum lambda=1, A_sigma(Y)^T lambda=0}`,
`B_sigma={Y in X_chi : P_sigma(Y) is nonempty}`,
`B_R=union_{sigma in R} B_sigma`.

For each nonempty `R subset S`, use the zero-padded compact set

`C_R={(Y,w) in Xbar x Delta^(56|S|-1) : w_sigma=0 for sigma outside R,
       A_sigma(Y)^T w_sigma=0 for every sigma}`,

and `J_R=C_R intersect (I x Delta)`. Write `Gamma_R=C_R\J_R`.
For any finite declared family `D` of semialgebraic subsets of `C_S`
(with real algebraic coefficients for the algorithmic assertion),
there is a finite simplicial complex `K`, a subcomplex `K_I`, subcomplexes
`K_R`, and a semialgebraic homeomorphism `h:|K| -> C_S` such that:

1. `h(|K_R|)=C_R`, `h(|K_R intersect K_I|)=J_R`, and restriction gives
   `|K_R|\|K_R intersect K_I| ~= Gamma_R`.
2. There are natural integral cohomology isomorphisms
   `H^*(K_R,K_R intersect K_I;Z) ~= H_c^*(Gamma_R;Z) ~= H_c^*(B_R;Z)`.
3. Every `R subset R'` is the literal coordinate-face inclusion in this
   single complex. Its induced compact-support cohomology map is the
   proper restriction `H_c^*(B_R') -> H_c^*(B_R)`.
4. All sets in `D`, the witness-coordinate zero faces, and the three closed
   filtration levels
   `F_r C_S={at most r positive block masses}`, `r=1,2,3`, are unions of
   open simplices; every member closed in `C_S` is a subcomplex. The true
   parent remainder is `h(|K_I|)=C_S intersect (I x Delta)`.
5. The relative simplicial cochain complexes, with the closed
   support-cardinality filtration, compute the finite closed-cover
   compact-support Mayer--Vietoris spectral system, including the integral
   alternating restriction maps. This comparison is natural for the
   signature-subset diagram.

For a family with `s` signatures replace three by `s`. The theorem does
not need properness or incomparability of the signatures. Those conditions
select the project's D3 inputs; omitting them here strengthens the source
existence statement without asserting any vanishing.

This is a semialgebraic triangulation of a polyhedron minus a subcomplex.
It does not say a noncompact `Gamma_R` is the underlying space of a finite
ordinary closed simplicial complex. An orientation means a choice of
orientation for each simplex, obtainable by ordering vertices; it does not
assert that the possibly singular source is an oriented manifold.

## 2. Global quotient and continuity, without a component assumption

Let `V=[y_1,...,y_8]` represent a realization. Set

`B=[y_1,y_2,y_3,y_4]`, `c=B^{-1}y_5`,
`H=diag(|c_1|^{-1},...,|c_4|^{-1}) B^{-1}`.

Uniformity implies `det B != 0` and every `c_i != 0`: Cramer's rule
expresses each `c_i` as a nonzero parent bracket divided by `det B`.
The signs `s_i=sign c_i` depend only on `chi`. Use the representative

`N(V)=[e_1,e_2,e_3,e_4,s,n_6,n_7,n_8]`,
`n_j=H y_j / sum_i |(H y_j)_i|`.

The first four columns of `HV` become `e_i` by positive column scalings
`|c_i|`, and the fifth is already `s`. Every coordinate of `Hy_j` is
nonzero for `j=6,7,8`, again by uniformity. Its sign `tau_ij` is fixed by
`chi`. Thus `n_ij=tau_ij u_ij` with `u_ij>0` and `sum_i u_ij=1`.
In these magnitude coordinates the 70 determinants are polynomials.
Exactly their prescribed strict signs define `X_chi`; no other constraints
are imposed. The resulting open semialgebraic set has dimension nine
whenever nonempty.

Here is explicit invariance under the entire stated group. If
`V'=G V diag(d_1,...,d_8)`, `d_j>0`, write `D_B=diag(d_1,...,d_4)`.
Then

`B'=G B D_B`, `c'=d_5 D_B^{-1}c`, `H'=d_5^{-1} H G^{-1}`.

Consequently `H'y'_j=(d_j/d_5)Hy_j`, so normalization gives
`N(V')=N(V)`. This holds also for negative `det G` under the equivalent
`{chi,-chi}` convention. Each `N(V)` belongs to the same permitted orbit
as `V`. Therefore two matrices have equal normal forms if and only if
they lie in the same orbit.

One can also see uniqueness from the stabilizer: a transformation fixing
the first four positive coordinate rays is positive diagonal; fixing the
fifth signed ray forces all its diagonal entries to be equal. The last
three positive length normalizations remove the remaining column scalings.

All displayed operations are continuous and semialgebraic on the full
realization space, since their denominators never vanish there. The
invariant map descends continuously through the quotient topology. Its
inverse is the continuous map taking a point of the section to its orbit.
They are inverse homeomorphisms. This proves component completeness,
continuity, and the quotient's Hausdorff property at once. No connectedness
or contractibility theorem for small oriented matroids is used.

The project's earlier affine frame section has one prescribed nonzero
coordinate of each remaining column normalized instead of its absolute
coordinate sum (`ATLAS_HELLY.md`, section containing `(5e')`). Dividing
by the appropriate positive coordinate magnitude and the reverse division
give a global semialgebraic homeomorphism between these sections. A
homeomorphism is proper as a map of the spaces, so compact supports are
preserved. Column-length factors in a `GL`-only quotient must not be
silently dropped: their compact-support cohomology gives a degree shift.
The D3 base here is the nine-dimensional projective quotient actually
specified in the sources.

### Normal and witness transport

For a triple `J`, the determinant identity gives

`a_J(G V diag(d)) = (prod_{j in J} d_j) det(G) G^{-T} a_J(V)`.

The common invertible covector transformation and positive row factors
preserve strict feasibility after the corresponding invertible change of
the extension variable. They preserve the named signature bad loci.
If `q_J=prod_{j in J}d_j>0`, the joined witness transformation is

`w'_(sigma,J)=(w_(sigma,J)/q_J) /
                sum_(rho,L)(w_(rho,L)/q_L)`.

Its denominator is positive, its inverse multiplies by the same factors
and renormalizes, and it commutes with zero-padding. It preserves every
zero-coordinate face and the set of positive blocks. It need not preserve
the numerical values of the block masses. This is why the filtration in
the theorem is explicitly support cardinality.

`verify_identities.py` certifies the universal cofactor formula by symbolic
polynomial expansion. It also checks exact rational normalizations under
both determinant signs, distinguishes an independent reorientation, and
checks the joined rescaling and its inverse on actual parent cofactors.
Those finite checks support the algebra; the universal quotient and
continuity proof is the preceding argument.

## 3. Exact parent closure and relative boundary

Let `D=(Delta^3)^3`. The first-order formula

`z in cl_D(X) iff z in D and
  forall epsilon>0 exists x in X: sum_i (x_i-z_i)^2 < epsilon^2`

defines the actual Euclidean closure, not the weak-inequality relaxation.
Quantifier elimination makes it semialgebraic. It is closed in compact
`D` and hence compact. Since `X` is open in `D`, it is open in `Xbar` and
`I=Xbar\X` is closed.

At a point of `Xbar`, all fixed-sign inequalities are weakly satisfied
by continuity. If all simplex coordinates and parent determinants are
nonzero there, they have their strict prescribed signs, and the point is
in `X`. Conversely every point of `X` has all of them nonzero. Thus

`I=Xbar intersect (union coordinate-zero loci union parent-bracket-zero loci)`.

In fact a zero coordinate of `n_6,n_7,n_8` is itself a vanishing parent
bracket using three basis columns. There is no uniform point in `I` and
no chart overlap removed from the interior. Residual factors and witness,
occurrence, or concurrence rank drops with all parent brackets nonzero
belong to `X`; they are not relative infinity. The argument concerns the
whole closure and is unchanged if there are multiple components whose
closures touch at boundary points.

The cofactor matrices are polynomial in the signed section coordinates,
so they extend over `Xbar`. Every `C_R` is defined by continuous equalities
inside a compact product and is compact. `J_R` is closed, and restriction
to `X` is literally the original joined system. Consequently
`C_R\J_R=Gamma_R` exactly. The zero-padding equations prove all pair
inclusions without any inferred continuation through a witness wall.

There is a terminology limitation in the draft: `C_R` is a compact
*envelope*, and `Gamma_R` need not be dense in it. Equation-only witness
fibers can occur exclusively at a degenerate parent. In a generic scalar
example `X=(0,1)`, `A(x)=[x]`, the normalized source is empty but the
extended equation has `w=1` at `x=0`. This is not an actual-parent
counterexample. It shows why density is not a formal consequence of
extended equations. The draft expressly allows such fibers, and relative
cohomology is still correct: every extra point lies in `J_R`.

If a later argument needs every boundary point to be approachable from
the source, replace `C_R` by the exact closure of `Gamma_R` in the compact
ambient and `J_R` by its intersection with parent infinity. These finitely
many closures remain semialgebraic, compact, nested under zero-padding,
and have the same open complements. Density should be required only for
that stronger end-space interpretation, not inferred for the equation
envelope. Neither construction makes an interior witness wall an end.

## 4. Finite family and simultaneous triangulation

The exact invoked result is Shiota, *Whitney triangulations of
semialgebraic sets*, Ann. Polon. Math. 87 (2005), 237--246, theorem on
page 237: a compact semialgebraic set admits a semialgebraic triangulation
compatible with finitely many prescribed semialgebraic subsets. The
Whitney refinement is stronger than needed here. See the
[primary paper](https://impan.pl/shop/en/publication/transaction/download/product/84789).
No triangulation of a nonproper map is asserted or needed.

A sufficient finite family inside `C_S` is:

- every `C_R`, `J_R`, and the closed support-cardinality levels `F_r C_S`;
- all 168 witness-coordinate zero sets for a triple, whose Boolean
  combinations specify every exact positive support;
- the pullbacks of the 70 parent determinant zero and sign sets, and of
  the finitely many declared residual factor sign sets;
- all declared rank loci. A finite matrix has finitely many minors, so
  including their sign and zero sets represents every rank stratum;
- any additional semialgebraic carrier or chart-domain sets later to be
  used, supplied as a finite input list before this triangulation is used.

The source-theorem data required for degree-two Mayer--Vietoris are already
in the first two items. The residual and rank data are additional compatible
labels; their numerical inventory is not needed for the existence proof.
An implementation claiming that it represents a particular declared list
must actually supply that list and the corresponding formulas. This report
does not certify an unspecified downstream carrier inventory.

There are only seven nonempty signature subsets and three cardinality
levels for a triple. If “all closed mass levels” instead means all real
sublevel sets `{t_0<=c}` simultaneously, the assertion is generally false:
whenever `t_0` has an interval of values these are infinitely many distinct
sets, whereas a finite complex has finitely many subcomplexes. The audited
source `BLOCK_GORDAN_AUDIT.md`, section 3, explicitly uses cardinality, so
the intended finite interpretation is available and unambiguous after the
correction.

Compatibility means that each prescribed set is a union of images of
open simplices. Its Boolean combinations have the same property. The
closure of any such union, since the triangulation is finite and a
homeomorphism, is the union of the corresponding closed simplices and
their faces. Thus closures and iterated Boolean operations cause no hidden
infinite-family requirement. A closed compatible subset is automatically
a subcomplex: if it contains an open simplex it contains all of its faces.
No subdivision is needed for that last assertion.

Apply the theorem once to the single `C_S`; define `K_R=h^{-1}(C_R)`
and `K_I=h^{-1}(J_S)` as subcomplexes. The coordinate-face inclusions are
now literal inclusions. Their compositions along every chain agree
strictly, and the simplicial boundaries carry integral incidence signs.
This supplies coherent incidence for this triangulated source. It does
not supply any previously proposed root-motion map, preferred witness
selection, cubical matching, or prescribed local cell parameterization.

## 5. Compact supports and the missing filtration argument

### Relative comparison and union projection

For a compact triangulable pair `(C,J)` with `J` closed and `U=C\J`,
extension by zero along `j:U -> C` gives

`R Gamma_c(U;Z) ~= R Gamma(C;j_! Z_U)
                ~= R Gamma(C,J;Z)`.

For this polyhedral pair, sheaf and singular relative cohomology agree,
and the finite relative simplicial cochains compute them. One can also
derive the identification from the compact-pair relative long exact
sequence. Compactness, closedness, and the exact complement equality
were proved above; density of `U` is not a hypothesis. All identifications
are natural for maps of these pairs whose restrictions are proper.

The image of `Gamma_R -> X` is `B_R`, by the strict Gordan alternative:
some block must have positive mass, and normalizing that block gives a
member of `P_sigma`; conversely any such member can be zero-padded. The
source is closed in `X x Delta`. Its projection to `B_R` is proper because
the inverse image of a compact set is closed in its product with `Delta`.
In particular `B_R` is closed in `X`, hence locally compact semialgebraic.

At each `Y in B_R`, the fiber is the compact convex polytope

`conv(disjoint-coordinate copies of P_sigma(Y) for sigma with P_sigma(Y)!=empty)`.

It is nonempty and contractible. Proper base change identifies the stalks
of the higher direct image with its fiber cohomology, so the canonical
unit `Z_(B_R) -> Rp_* Z_(Gamma_R)` is a quasi-isomorphism. Since `p` is
proper, this yields the compact-support comparison. The needed topological
theorem, with its closedness and compact-fiber hypotheses, is in
[Stacks, section 20.18](https://stacks.math.columbia.edu/tag/09V4),
especially Lemma 20.18.1 and Theorem 20.18.2. Here all spaces are locally
compact Hausdorff and semialgebraic, so the hypotheses apply over `Z`.

For `R subset R'`, the square of zero-padding and bad-union inclusions
commutes as actual proper maps. Proper pullback is contravariant on
compact-support cohomology, and functoriality makes the comparison square
commute. This does not require that the square be Cartesian. No inverse
or continuous section of `p` is chosen.

### A proper filtered map to the Cech blowup

Use a different symbol for intersections to prevent union confusion:
`D_T=intersection_(sigma in T) B_sigma`. Define

`Z_R=union_(empty!=T subset R) D_T x Delta_T`,

inside `X x Delta_R`, where `Delta_T` is the closed coordinate face.
Equivalently `(Y,t)` belongs to `Z_R` exactly when every positive `t_sigma`
has `Y in B_sigma`. This is a finite union of closed subsets of
`X x Delta_R`. Let `Z_R^(r)` be its subset with at most `r` positive masses.

The mass map

`m_R: Gamma_R -> Z_R`, `(Y,w) |-> (Y,(sum_J w_(sigma,J))_sigma)`

is proper and surjective. For a compact subset of `Z_R`, its parent
projection is compact; the inverse image under `m_R` is closed in that
parent compact set times the weight simplex. At `(Y,t)`, dividing each
positive block by its mass identifies the fiber with

`product_(sigma:t_sigma>0) P_sigma(Y)`.

It is nonempty compact convex. Crucially

`m_R^{-1}(Z_R^(r))=F_r Gamma_R`

for every `r`. Proper base change applies to `m_R`, all of these closed
restrictions, and the restrictions to their locally closed differences.
The canonical quasi-isomorphisms commute with the localization triangles.
They therefore identify the exact couples and spectral systems of the
closed filtrations, including connecting maps, not just their `E_1`
dimensions. They also commute with the zero-padded `R` diagrams.

The space `Z_R` is the geometric closed-cover Cech construction. Its
`r`th stratum is the disjoint union

`coprod_(|T|=r) D_T x relint(Delta_T)`.

Compact-support cohomology of an oriented open `(r-1)`-simplex is `Z`
in degree `r-1` and zero otherwise. The integral Kunneth shift has no Tor
term because this group is free of rank one. Ordering the signatures
orients the simplexes. Attaching a face deletes one signature with the
usual alternating sign and restricts from `D_(T\{i})` to `D_T` on
cohomology. Consequently the filtered system is

`E_1^(p,q)=direct_sum_(|T|=p+1) H_c^q(D_T;Z)
           ==> H_c^(p+q)(B_R;Z)`,

with

`(delta alpha)_T=sum_(j=0)^p (-1)^j alpha_(T\{i_j})|_(D_T)`

when `|T|=p+1`, acting from column `p-1` to column `p`. In particular,
for ordered labels `0<1<2`, the pair-to-triple map is

`delta(alpha_01,alpha_02,alpha_12)
       = alpha_12|_012 - alpha_02|_012 + alpha_01|_012`.

This also follows from the stalkwise exact augmented closed-cover sheaf
resolution `Z_B -> sum_i Z_(B_i) -> sum_(i<j) Z_(D_ij) -> Z_(D_012)`:
at a point, it is the augmented cochain complex of the simplex on exactly
the bad indices present there. The blowup argument identifies this
standard resolution with the actual mass filtration rather than merely
postulating the same `E_1` terms.

On the triangulated compact pair the relevant groups are
`H^*(F_r C_R, (F_(r-1) C_R) union (F_r C_R intersect J_R))`.
Localization identifies these with the stratum compact-support groups.
Thus the finite relative cochains and their filtration have precisely
the above connecting maps. Relative chain boundary matrices are integral;
their transposes are the cochain differentials. Over `Q`, the usual
rank equation in degree two can be stated using either transpose.

**Union labels must not be mistaken for intersections.** `K_{01}` models
`B_0 union B_1`; `K_0 intersect K_1` is empty because their weight blocks
are disjoint and total mass is one. The topology of `D_01` occurs in the
two-positive-block stratum, with a one-degree shift. Likewise the triple
intersection occurs in the three-positive-block stratum. Clause 5, not
an intersection of the `K_i`, supplies the needed D3 diagram.

## 6. Mathematical existence, effectivity, and available certificates

These are three different assertions.

**Mathematical validity.** Sections 1--5 prove the compact-source theorem
with the explicitly finite support filtration and finite declared family.
No all-parent enumeration or source triangulation output is needed for
this quantified existence statement. The construction works for any
realizable uniform labeled chirotope, so it covers the claimed 2,604
classes without independently relying on or rechecking that class count.

**Effective computability.** All standard source coefficients are integers
or rational numbers after the fixed sign choices; optional declared data
must also have effectively represented real algebraic coefficients.
Closure, feasibility,
properness of a region, and incomparability can be expressed in the
first-order theory of real closed fields. For example, strict inclusion
failure is witnessed by a parent satisfying `F_sigma and not F_tau`.
The candidate does not need their census: it can accept any finite list
of signatures, and the D3-specific list can in principle be filtered by
these decidable predicates.

Compatible semialgebraic triangulation is effective, although expensive.
The classical exact triangulation algorithm and its doubly exponential
bound are explicitly recalled in Basu--Karisani, section 1.1 of
[*Efficient simplicial replacement of semialgebraic sets*](https://www.cambridge.org/core/journals/forum-of-mathematics-sigma/article/efficient-simplicial-replacement-of-semialgebraic-sets/C32B4A3FA99FAF864D70274612ADA1C2).
Its efficient replacement theorem is not needed as a substitute for
the literal triangulation used here.

There is also a direct, very inefficient decision-search justification
for the exact finite-family version. Enumerate finite abstract complexes
with standard rational realizations and formulas for graphs of maps to
`C_S` with real algebraic coefficients. First-order tests decide that
such a graph is a total bijection, continuous, and compatible with each
prescribed subset on every open simplex. A continuous bijection from a
compact space to Hausdorff `C_S` is a homeomorphism. This enumeration
terminates by the existence theorem: any semialgebraic triangulation
uses finitely many real coefficients, and its map, continuity, bijection,
and finite compatibility conditions are first-order conditions on those
coefficients. A nonempty semialgebraic parameter set over the rationals
contains a real algebraic point. Thus one of the enumerated descriptions
passes. This proves computability without postulating an installed
compatible-triangulation implementation or silently demanding a map be
piecewise linear.

**Practical certificate availability.** No `Xbar` elimination outputs,
complete signature antichain census, all-parent source simplexes, certified
triangulation homeomorphisms, degree-two maps, or verified middle-rank
matrices are produced by this lane. Its checker certifies a finite
universal algebra identity and exact rational gauge examples only. The
general algorithm does not come with a feasible forecast in this task's
resource limits. A statement that an exact matrix can be computed is not
the computed matrix or a proof of its rank.

## 7. Actual D3 consequences and the first missing edges

The source construction uses the actual parent to justify the global
section and polynomial normal formulas. Once these are supplied, its
topological argument works for arbitrary continuous semialgebraic signed
matrix families. It does not use a special relation among common-parent
normals to force vanishing. The shared-array identity
`A_sigma=diag(sigma) A` and the exterior-power structure of `A` remain
available for a separate structural theorem; the source proof does not
extract their topological consequences.

Assume, as the project currently does, the lower vanishings
`H_c^q(B_i;R)=0` for `0<=q<=2` and `H_c^0(D_ij;R)=0`. This lane does
not independently reprove the support-motion arguments establishing them.
The spectral sequence just proved then gives an exact sequence

`0 -> H_c^0(D_012;R) -> H_c^2(B_0 union B_1 union B_2;R)
   -> ker[sum_(i<j) H_c^1(D_ij;R) --delta--> H_c^1(D_012;R)] -> 0`.

Indeed the only total-degree-two pieces are columns `(2,0)`, `(1,1)`,
and the zero `(0,2)`. The only possible incoming maps to `(2,0)` have
zero sources by the lower vanishings; none leave column two. For `(1,1)`,
the only nonzero candidate map is the displayed `delta`. There are no
further differentials at those bidegrees. This reconstructs the two D3
endpoints separately, including their map rather than only dimensions.

For the rational 9DVL target, both are required:

1. `H_c^0(D_012;Q)=0`. A locally compact semialgebraic set has finitely
   many components, each open and closed. Its `H_c^0` is one copy of `Q`
   for each compact connected component. Therefore this says every
   triple-bad component is noncompact, equivalently its closure in `Xbar`
   meets `I` (the triple bad set is closed in `X`). This report provides
   neither such an escape nor an actual compact component.
2. `delta` is injective on the *direct sum* of the pair `H_c^1` groups.
   Individual pair restrictions being injective does not exclude
   cancellation between their images. Finite integral incidence matrices
   exist; this report does not prove the required rational kernel zero.

The first missing mathematical edge is therefore a common-parent
geometric input proving either of these claims, or an admissible actual
counterexample. It is not a missing choice of compactification or a
missing existential triangulation theorem.

The first missing certificate edge is the construction and checking of
the particular complexes, labels, and maps required by the selected
all-parent proof interface. A generic triangulation has ordinary
simplex dimensions, whereas the saved `(1,0,0)` and related types are
fiber-face shapes. Compatibility with those strata does not produce
the prescribed root carriers or a finite face-natural acyclic matching
of them. It also does not establish a map from any previously proposed
local chain model to the new source. That is a precise limit on what
the present existence proof closes.

### Audit of the claimed seven-to-three reduction

If `global_gluing`, `extension_labels`, `strict_closure`, and
`relative_infinity` mean only “there exists a globally glued labeled
relative simplicial model,” the theorem proves that common existential
statement. There is no residual existence obstruction in those words.
It would be equally incorrect to deny that mathematical result merely
because its algorithm is impractical.

The canonical obligations, however, arose in a requirement for a
coverage-certified complete joined complex and its actual lower-skeleton
or carrier comparisons (`9DVL_THEOREM_PROSPECTUS.md`, Targets A/B;
September 2 replacement cycle). The draft does not show that all of
those meanings are exhausted by the existential model, does not produce
the required comparisons, and does not show a strictly smaller bounded
remaining construction burden. Counting four names as closed would
conflate these two meanings. No independent acceptance or canonical
promotion is made here. Record an existential-source lemma, keep both
D3 invariants and certificate coverage open, and do not claim `7 -> 3`
as measured research convergence from this lane alone.

## 8. Handoff, validation, and decision

`verify_identities.py` completed successfully with Python 3.11.9 and
SymPy 1.14.0. It uses symbolic polynomial expansion and exact rational
arithmetic; no floating-point inference. The stored output is
`TEST_OUTPUT.json`. It certifies the cofactor transformation used in
the proof, all 70 nonzero brackets of its rational parent fixture,
normalization invariance cases, and the joined weight gauge including
its zero block and inverse. It does not test topological claims by
asserting expected result flags.

`SOURCE_MANIFEST.json` records SHA-256 pins for the inputs actually used
and the primary literature references. `RESULT.json` separates proof,
effective-computability, practical output, and theorem-credit statuses.
The final local Git commit is the frozen handoff boundary; no push,
merge, human contact, paid compute, broad CAD, or canonical-state edit
is authorized or performed by this lane. No other active lane was read.

Lane decision: `STOP` source-existence development at the proved endpoint.
Trajectory: `INFORMATIONAL` for D3. A Stage B pivot requires a separately
written common-parent structural hypothesis selected by the coordinator,
not more iterations of generic source construction. The opening,
midpoint, and closing lane vectors retain
`(2/9,1,{diag3_pair_hc1,diag3_triple_hc0},7,UNKNOWN,UNKNOWN,9,12)`;
cycle streak changes and acceptance decisions belong to the coordinator
and independent referee.
