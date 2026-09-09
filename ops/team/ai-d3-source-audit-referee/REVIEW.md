# Independent Stage A source-existence review

Frozen review base: `9aefa1d783ffae751406c4e295e228153041772c`.
Source handoffs: `13b54136ba0e226c60f23235e706ffa31e85ab41` and
`76d168e746e6dc3996496bdf1fd08eb83d165b53`, integrated as `286c3ea` and
`d0431c0`. Falsifier integration: `ce71070`.
Owned surface: `ops/team/ai-d3-source-audit-referee`.

**Decision: ACCEPT the explicitly stated five-clause source-existence
theorem, including effective computability in principle.** The source
handoff has no remaining mathematical gap in that scope. The original
draft needs the interpretations listed below; its claimed `7 -> 3`
canonical-obligation decrease is not established. Accept the falsifier's
three generic pair/triple distinctions. No D3 invariant, old carrier
comparison, complete implementation, or theorem-ledger increment follows.
Source-existence development can stop at this proved endpoint. This is
not a decision on the separately authorized Stage B work, which was not read.

## Accepted statement versus the original draft

For every realizable uniform labeled rank-four chirotope on eight elements,
fix its representative with `chi(1234)=+1`. The base is the quotient by
`GL^+(4,R)` and positive column scalings. For any finite signature family
and any finite declared semialgebraic auxiliary family, the exact actual
block-Gordan sources have a simultaneous compact semialgebraic envelope,
finite triangulated pairs, literal zero-padding inclusions, natural integral
compact-support comparison, and the integral closed-cover Mayer--Vietoris
system under the block-support-cardinality filtration. Optional data need
effectively represented real algebraic coefficients for the algorithmic claim.

The following are necessary precision corrections, not newly discovered
counterexamples to the source handoff:

- A positive scalar on column 5 alone cannot normalize its four unequal
  coordinate magnitudes. The residual positive diagonal frame change is
  essential and is included in the handoff.
- A fixed chirotope representative permits `GL^+`; full `GL` requires the
  equivalent `{chi,-chi}` convention and consistent extension-sign names.
  Independent column reorientations and label permutations are not quotiented.
- Clause 1 describes a finite polyhedron **minus a relative subcomplex**.
  A noncompact source cannot be the realization of a finite closed complex.
- The equation envelope may have boundary-only pieces. Density is neither
  proved nor required for the claimed compact-relative cohomology model.
- The finite filtration counts positive blocks. Simultaneously representing
  every real mass threshold as a subcomplex would generally be false.
- A chosen orientation on each simplex does not assert manifold orientability.
  The finite cochains are compared with compact-support cohomology; homology
  chains alone are not silently identified with it.
- Auxiliary labels mean an actual finite declared family. The theorem does
  not certify an unspecified old carrier dictionary or future formulas.

## 1. Independent global gauge and orientation reconstruction

Let `B=(y_1,y_2,y_3,y_4)`, `d=det B`, and write `D_ij` for the determinant
obtained from `B` by replacing column `i` by `y_j`. Cramer's rule gives
`(B^{-1}y_j)_i=D_ij/d`. Uniformity makes `d` and all required `D_ij`
nonzero. The signed coordinates before the last three length normalizations
can therefore be written without a matrix inverse as

```
r_ij = sign(d) D_ij / |D_i5|.
```

The fifth column becomes `sign(r_i5)`; columns 6--8 become
`r_j / sum_i |r_ij|`; the first four are the coordinate vectors. These are
exactly the handoff's coordinates. Their signs are determined by the fixed
chirotope, including the fixed permutation signs in the replacement brackets.

Under `V'=G V diag(c_1,...,c_8)` with all `c_j>0`,

```
d'     = det(G) (product_(l=1)^4 c_l) d,
D'_ij  = det(G) (product_(l!=i,1<=l<=4) c_l) c_j D_ij.
```

Hence `r'_ij=(c_j/c_5)r_ij`, for either determinant sign of `G`; the last
normalizations cancel this positive factor. This proves invariance, not just
invariance on a rational fixture. The positive diagonal matrix
`diag(|(B^{-1}y_5)_i|^{-1}) B^{-1}` followed by the stated positive column
scalings sends every realization to that representative. On the fixed
positive-basis-sign realization space its determinant is positive.

The representative is unique: preserving the four oriented coordinate rays
forces a positive diagonal frame map; preserving the fifth signed ray, with
all entries nonzero, makes it scalar. The last three length conditions then
remove the remaining column scales. The normalization map is continuous
semialgebraic everywhere on the realization space. It descends continuously
to the quotient topology; the inclusion of the section followed by the
quotient map is its continuous inverse. Thus the whole quotient, including
every component, is homeomorphic to the strict 70-bracket-sign locus in
three simplex interiors. It is an open nine-dimensional semialgebraic set.
No connectedness, contractibility, quotient proper-action theorem, or parent
census is assumed.

For the normal convention `a_J(V)^T p=det(V_J,p)`, determinant
multiplicativity and multilinearity give

```
a_J(G V diag(c)) = det(G) (product_(j in J)c_j) G^{-T} a_J(V).
```

For positive `det G`, take the extension vector to `Gp`; every signed
margin gains a positive factor. With negative `det G`, either flip the
global extension-sign representative together with the parent representative
and again use `Gp`, or keep the formal row signature and use `-Gp`.
These are explicit conventions, not loss of an extension region. The theorem
itself works in the fixed positive-basis-sign convention.

Writing `q_J=product_(j in J)c_j>0`, the normalized joined-witness map is
the positive diagonal projective map
`w_(sigma,J) -> (w_(sigma,J)/q_J)/sum_(rho,L)(w_(rho,L)/q_L)`.
The inverse multiplies by `q_J` and renormalizes. It preserves every
coordinate zero face, every positive-block set, and zero-padding.
Its numerical block masses may change. This proves precisely the required
support filtration invariance. The earlier affine section in
`ATLAS_HELLY.md`, equation `(5e')`, differs by positive coordinate
normalizations and is globally homeomorphic to this section. Such a
homeomorphism is proper as a map of the two base spaces. This argument
does not assert that the gauge extends to a homeomorphism of two chosen
boundary compactifications. Nor does it drop the seven positive length
factors of a `GL`-only quotient in a compact-support calculation.

## 2. Clauses 1--4: closure, envelopes, finite pairs, and inclusions

Take the actual closure of the strict sign locus `X` in the compact product
of three closed simplexes. The epsilon/nearby-point formula in the handoff
defines that closure exactly and makes it semialgebraic by quantifier
elimination. It is not obtained by replacing all inequalities with weak
ones. Since `X` is relatively open in that product, `I=Xbar\X` is closed.
Continuity of the defining polynomials shows that every point of `Xbar`
with nonzero simplex coordinates and parent brackets is still in `X`.
Thus `I` consists exactly of the corresponding zero loci inside `Xbar`.
Internal derived-residual or witness-rank walls with nonzero parent brackets
remain interior. All components are handled at once.

Actual derived normals are polynomial on this bounded section. The
zero-padded block equations, nonnegativity, and total mass one define closed
sets `C_R` in `Xbar x Delta^(56|S|-1)`. Their relative subsets `J_R` over
`I` are closed, and `C_R\J_R=Gamma_R` literally. Added zero blocks obey
every homogeneous equation and preserve mass, so `C_R -> C_R'` are closed
inclusions of compact pairs. This is the requested literal diagram.

Boundary-only solutions do not invalidate relative cohomology. For a compact
triangulable pair `(C,J)`, compact-support cohomology of `C\J` is its relative
cohomology. The exact open complement and closedness of `J` are the needed
hypotheses; density is not. Equivalently, collapsing all of `J` gives the
one-point compactification of the complement (with the usual separate empty
and compact cases). No boundary point is used as an interior witness.

Triangulate the one compact total set compatibly with all `C_R`, all `J_R`,
the finitely many support-cardinality levels, coordinate faces, and the
declared sign/rank sets. The precise needed finite-family theorem appears
on page 237 of Shiota's [primary paper](https://impan.pl/shop/en/publication/transaction/download/product/84789).
A closed compatible set is a subcomplex because it contains every face of
each of its included open simplices. Taking inverse images of the `C_R`
therefore makes the entire zero-padding diagram literal within one finite
complex. This proves clauses 1, 3, and 4 and the first comparison in clause 2.
It does not furnish a triangulation of an arbitrary map or an old prescribed
cell parameterization.

For the remaining comparison in clause 2, denote the bad union by `U_R`.
The image of `Gamma_R -> X` is exactly `U_R`: at least one block has
positive mass and normalizes to a single-signature Gordan witness; conversely
one witness zero-pads into the joined source. The projection is closed and
proper since weights range over a compact simplex. Its fibers are nonempty
compact convex sets. Proper base change identifies stalks of `Rp_*Z` with
their integral fiber cohomology, so the constant-sheaf unit is a
quasi-isomorphism. Properness then yields
`R Gamma_c(U_R;Z) ~= R Gamma_c(Gamma_R;Z)`. The needed topological
hypotheses are stated in [Stacks Project, Lemma 20.18.1](https://stacks.math.columbia.edu/tag/09V5).
All spaces here are locally compact Hausdorff and semialgebraic. Proper
pullbacks commute along the actual zero-padding squares; those squares
need not be Cartesian. This proves the naturality asserted in clause 2.

## 3. Clause 5: actual filtered comparison, not just equal groups

For intersections use `D_T=intersection_(i in T)B_i`. Form
`Z_R=union_(nonempty T subset R) D_T x Delta_T`. This is closed in
`X x Delta_R`. The source mass map `m_R` records the base and each block's
total mass. It is proper and onto. Over `(Y,t)`, its fiber is the product
of the nonempty compact convex normalized witness sets for precisely the
positive `t_i`. Moreover,

```
m_R^{-1}({at most r positive masses})
    = {at most r positive blocks in Gamma_R}.
```

This exact preimage equality is the load-bearing fact. Proper base change
applies to the whole map, each closed filtration restriction, and each
locally closed stratum restriction. The canonical units commute with the
localization triangles for these pairs. Hence they identify the exact
couples, including connecting maps. This is stronger than identifying
objectwise cohomology or counting `E_1` dimensions, and requires no continuous
witness selection or triangulation of the mass map. The same constructions
commute with all signature-subset inclusions.

The exact-support stratum of `Z_R` is
`D_T x relint Delta_T`. The oriented mass simplex gives an integral shift
by `|T|-1` with no Tor contribution. Its ordered face attachments are the
literal inclusions `D_T -> D_(T\{i})`; dualizing gives alternating proper
restrictions. Thus

```
E_1^(p,q) = direct_sum_(|T|=p+1) H_c^q(D_T;Z),
delta(alpha_01,alpha_02,alpha_12)
    = res(alpha_01)-res(alpha_02)+res(alpha_12).
```

The closed-cover constant-sheaf resolution is independently exact: at each
point its augmented complex is the simplex on the bad indices present.
Coning to its least vertex is an integer contraction. The checker verifies
`d h+h d=identity` for all seven nonempty bad-index patterns. Compatible
triangulation of the compact source turns its filtration pairs into finite
relative simplicial cochains. Their exact couples consequently give this
same spectral system. No comparison to old numerical boundary matrices is
inferred. In particular, `K_0 intersect K_1` is empty; intersections of bad
sets occur in positive-block strata, not intersections of the union-model
subcomplexes.

## 4. Effectivity and exact limits of obligation credit

The theorem is effectively uniform in finite algebraic input descriptions.
Quantifier elimination supplies closure/feasibility formulas. Compatible
triangulation is effective; the classical algorithm is recalled in
[Basu--Karisani, Section 1.1](https://www.cambridge.org/core/journals/forum-of-mathematics-sigma/article/efficient-simplicial-replacement-of-semialgebraic-sets/C32B4A3FA99FAF864D70274612ADA1C2).
The source's alternative enumerative proof is also valid: enumerate finite
complexes and graph formulas with real algebraic coefficients; first-order
tests decide total bijectivity, continuity, and compatibility with each
prescribed simplex/subset. Existence of a real-coefficient graph of some
finite formula shape implies existence with real algebraic coefficients by
real-closed-field elementarity. Compactness makes the accepted continuous
bijection a homeomorphism, so the enumeration eventually terminates.
This argument does not supply a practical bound, an installed solver, or
computed all-parent complexes. Nonempty universal coverage does not rely
on independently verifying the reported count 2,604.

The five selected-route **existence** tasks are therefore settled: global
frame, exact compact parent closure, compact-relative source pair,
simultaneous labeled triangulation, and filtered compact-support comparison.
This is a mathematical result for actual parents, not merely a failed
computation. It does not establish the proposed four canonical closures.
`9DVL_THEOREM_PROSPECTUS.md`, Target B, requires a coverage-certified complex
containing labeled instances of ten specific witness-face shapes and its
actual lower-skeleton comparison; Target A additionally requires natural
mixed chains and wall specializations. An arbitrary compatible source
triangulation supplies neither those prescribed carriers nor a verified map
from an old carrier complex. The existing V11 node names inherit those
stronger obligations. No such comparison or strictly smaller completed
bypass is supplied. **Reject the original draft's automatic `7 -> 3`
inference; retain seven canonical obligations and the 2/9 ledger.**

## 5. Falsifier distinctions independently checked

Assuming the project's lower vanishings, the filtration gives the integral
conditional exact sequence

```
0 -> H_c^0(D_012) -> H_c^2(U_012)
  -> ker[direct_sum H_c^1(D_ij) -> H_c^1(D_012)] -> 0.
```

The triple term has zero incoming `d_1` and `d_2` sources; the pair term
has only its displayed restriction differential. There are no further
possible columns. Thus the two invariants must vanish separately.

The falsifier's coordinate sets give a direct independent verification.
Each intersection is the open cube on the intersection of its free-axis
sets; zero free axes means a point. Recomputing those sets gives:

| Model | Pair dimensions | Triple dimension | Pair kernel | Triple Hc0 | Union Hc2 |
|---|---|---|---|---|---|
| Both fail | 1,1,1 | 0 | Z^3 | Z | Z^4 |
| Pair only | 1,1,1 | 1 | Z^2 | 0 | Z^2 |
| Triple only | 2,2,2 | 0 | 0 | Z | Z |

Singleton dimensions are at least three. In the pair-only model all pair
and triple intersections are the same oriented axis, so the map is
`[1,-1,1]`; its only nonzero Smith invariant is one. Thus the integral
kernel is Z^2 although each individual restriction is an isomorphism.
For the other models the claimed source/target groups are zero as stated.
The displayed extension splits abstractly because its quotient is free.
The independent checker derives dimensions and integer incidence from free
axes, not from the producer's stored Betti numbers or rank routine.

The shared-matrix construction is exact: nonnegative squared-distance
functions vanish precisely on the coordinate sections; its active pair
forces infeasibility there, and the inactive margins are `1` and
`2g_j+1`. Nonnegativity makes every inactive dual weight and every tail
weight vanish on the bad set, leaving the two active weights `1/2`.
The source is consequently the stated finite polyhedral simplex resolution.
The repeated tail normals exclude actual uniform-parent origin: proportional
normals for two distinct triples would annihilate their union of at least
four parent columns, contradicting uniformity. These are generic separations,
not valid-parent D3 examples. Lower-vanishing theorems themselves were not
reaudited.

## Verification and freeze

The independent checker passed in 4.84 seconds using Python 3.11 / SymPy
1.14. It verifies 88 universal coordinate identities for 22 elementary GL
generators, triple homogeneity, a Cramer-bracket gauge on a distinct rational
uniform fixture, 112 labeled normal transports across both determinant
signs, the joined-weight inverse/zero-support properties and an explicit
mass-change canary, the seven integer augmented-simplex contractions, and
the three generic invariant distinctions. Three deliberate corruptions are
rejected. Producer modules were neither imported nor executed. These checks
support the algebra and incidence; the universal topology/effectivity proofs
are the arguments above, not machine-formalized conclusions of the script.

`CHECK_OUTPUT.json` records ten frozen source hashes. `RESULT.json` fixes
the accepted statement and denies broader promotion. The prior generic
review is untouched. All edits remain in this fresh referee surface;
no human consultation, external compute, push, merge, canonical edit, or
Stage B inspection occurred. The containing local commit is the handoff.
