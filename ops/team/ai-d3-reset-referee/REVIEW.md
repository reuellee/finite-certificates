# Independent review of the full-dimensional generic countermodel

Reviewed candidate: `96d2cafda5c3588d0754780d18b92c694a843b54`.
Referee branch: `research/ai-d3-reset-referee-20260905`.
Authority: this cycle's AI-only independent-review work order. No human was
consulted. The producer's Python module was neither executed nor imported.

**Decision: accept the mathematical generic no-go, with the independent
proof supplement below and two nonblocking evidence/exposition corrections.**
It is not an actual-parent example, a proof of D3, or progress on the 2/9
theorem ledger. The precisely retired route is deduction of D3 solely from
the generic package listed in the candidate. No broader route is retired.

## Findings against the frozen candidate

1. The producer's `halfline_product` computes ranks over `Fraction` and
   subtracts those ranks from chain dimensions. That proves rational
   acyclicity, not integral acyclicity by itself: `Z --2--> Z` has the same
   ranks as `Z --1--> Z` but different integral cohomology. The output line
   claiming an integral check exceeds that routine's verification scope.
   The actual candidate complexes are integrally acyclic. The written
   unit-differential argument, and the explicit integer contraction checked
   independently here, establish this without a torsion assumption.
2. The sentence referring to the filtered comparison "as in the source
   audit" does not identify a frozen source-audit artifact. There is no
   `ops/team/ai-d3-reset-source` directory in this candidate. The old pinned
   block-Gordan audit provides definitions; its acceptance conclusions are
   not relied upon. Section 5 below reconstructs the comparison and its
   integral attachment maps explicitly for this family. The candidate
   should use that argument or a precise frozen reference in a later revision.

Neither issue furnishes a mathematical counterexample to the candidate's
stated generic construction. Acceptance is of the construction together
with this independent justification, not of every scope claim printed by
the producer's script. Producer files were not changed.

## 1. The common matrix and the three feasible regions are exact

Temporarily regard the three numbers `g_0,g_1,g_2` as arbitrary real
parameters. The four columns of the unsigned matrix are three disjoint
`(1,-1)` coordinate pairs, followed by the column
`(g_0,g_0,g_1,g_1,g_2,g_2,1,...,1)` with fifty final ones.
The specified signatures change only the odd row of each inactive pair.
Every row has a fixed nonzero coordinate. The minor with zero-based row
indices `0,2,4,6` is

```
1 0 0 g_0
0 1 0 g_1
0 0 1 g_2
0 0 0 1
```

so has determinant one at every parameter. The full row span is four.

For signature `i`, each extra row requires `p_4>0`, and the sum of its
active pair of strict inequalities requires `2 g_i p_4>0`. Thus feasibility
implies `g_i>0`. Conversely take `p_4=1`, active coordinate zero, and each
inactive coordinate `1+|g_j|`. Both inactive margins are at least one and
the active margins equal `g_i`. This is an independent primal proof. The
candidate's polynomial choice `1+g_j^2` also works, by its positive
completed squares; the independent checker verifies those identities.

Substitute `g=(-x,-y,x+y+||u||^2-1)`. This proves exactly the proposed three
feasible regions, not just inclusions or behavior on test points.
The three exclusive-bad rational points are correct. A point exclusively
in `B_i` lies in both other feasible regions and outside `F_i`, so the
three points together prove every directed non-inclusion. The supplied
common-feasible point is also correct. Hence all three regions are nonempty,
proper, and pairwise incomparable.

There is an independent complete description of the normalized dual fiber
`K_i` that is useful below. Its first three equations force the active
weights equal to a number `a` and force each inactive pair to sum to zero.
Nonnegativity therefore makes every inactive weight zero. If `b` is the
sum of the fifty extra weights, the remaining equations are

```
2 g_i a + b = 0,       2 a + b = 1.
```

When `g_i<=0` they give
`a=1/[2(1-g_i)]` and `b=-g_i/(1-g_i)`. The fifty individual extra weights
are arbitrary nonnegative numbers summing to `b`. Thus `K_i` is a point
when `g_i=0`, and an affine copy of the 49-simplex when `g_i<0`. It is empty
when `g_i>0`, as is also clear from the primal argument. The producer's
two active weights one and extra weight `-2g_i`, divided by `2-2g_i`, are
correct. In particular, this is a total-mass normalization, not a
requirement that every signature block have positive mass.

## 2. Singleton and pair compact-support cohomology over Z

The candidate's coordinate changes are genuine global semialgebraic
homeomorphisms. For `B_2`, the slack is
`z=1-x-y-||u||^2`, and `y=1-x-||u||^2-z` is its inverse. The same formula
with `x>=0` gives the `02` pair chart; interchange `x,y` for `12`.
`B_0`, `B_1`, and `01` have the immediate product charts.

Consequently each singleton is `R^8 x [0,infinity)` and each pair is
`R^7 x [0,infinity)^2`. These homeomorphisms automatically preserve compact
supports. Ordinary contractibility alone would not prove the claims.

Here is an integral finite calculation, including the Euclidean shift.
Compactify `R^m x [0,infinity)^k` to the cube `[0,1]^(m+k)`, using an open
interval for each Euclidean factor and a half-open interval for each
half-line. The relative subset is the union of both endpoint faces in
the first `m` coordinates and the upper endpoint faces in the last `k`.
The relative cubical chains have surviving cells `E^m` followed by `k`
symbols from `{L,E}`. Here `L` is the lower vertex and `E` is the oriented
edge; its lower boundary has coefficient `-1`. Product boundary signs
use the number of preceding edge factors.

Define an integer degree-one map `h` to replace the first half-line's
`L` by `E` with coefficient `(-1)^(m+1)`, and to be zero when that symbol
is already `E`. Directly, `d h + h d = identity`. The checker verifies this
identity on every cell for `(m,k)=(8,1)` and `(7,2)`, as well as `d^2=0`.
Dualizing the integer contraction gives a cochain contraction. There is
no rationalization, Smith-rank inference, or possible residual torsion.
All singleton and pair compact-support cohomology groups are zero over Z.

## 3. Triple, union, and common-feasible topology

The triple is
`T={x>=0,y>=0,x+y+||u||^2<=1}`. It is closed and bounded, and contains the
origin. The defining last function is convex, so `T` is convex. It even
contains an open neighborhood of `(1/4,1/4,0)`. Its straight contraction to
zero stays in `T`: for `0<=h<=1`, the left side of the last inequality
after scaling is
`h(x+y+||u||^2)-h(1-h)||u||^2<=1`.
Thus `H_c^0(T;Z)=Z` and every higher group vanishes. This uses compactness
of `T`; no improper homotopy is used to infer compact-support invariance.

The claimed union group can be obtained without interpreting a spectral
sequence. Let `C=B_0 union B_1` and `D=(B_0 cap B_2) union (B_1 cap B_2)`.
Compact-support Mayer--Vietoris first gives `H_c^*(C)=0`. Since the two
members of `D` are acyclic and meet in `T`, its connecting homomorphism
is an isomorphism `H_c^0(T)=Z -> H_c^1(D)`, with all other groups zero.
Applying Mayer--Vietoris to `C union B_2`, whose intersection is `D`, gives
`H_c^1(D)=Z -> H_c^2(B_0 union B_1 union B_2)` as an isomorphism, again
with all other groups zero. Both connecting maps are integral isomorphisms.

Closed-cover Mayer--Vietoris is legitimate here. One-point compactify
these closed semialgebraic subsets in `S^9` and triangulate the finite
family compatibly, including infinity. They become subcomplexes. Their
relative simplicial cochain sequences are the ordinary exact
Mayer--Vietoris sequences for the indicated compact pairs. For the compact
triple, its intersection in the compactification also has the isolated
relative infinity point; this contributes nothing to relative cohomology.
This supplies the compact-support version with no open-cover assumption
silently imposed on the original bad sets. Relative cohomology and proper
homotopy conventions are standard; see Hatcher, Sections 3.1, 3.3, and 3.H
of [Algebraic Topology](https://pi.math.cornell.edu/~hatcher/AT/AT.pdf).

For an independent check on the degree, put `a=-x>0`, `b=-y>0` on the
common-feasible locus. Its inequality is `||u||>sqrt(1+a+b)`, so `u` never
vanishes. The displayed candidate map from
`S^6 x (0,infinity)^3`, with radial slack
`c=||u||-sqrt(1+a+b)>0`, is continuous, bijective, semialgebraic, and has
the stated continuous inverse. Ordinary homology therefore is Z in
degrees zero and six and zero in other degrees. In particular both
`H_6` and reduced `H_6` equal Z. The three open factors contract for this
ordinary homology calculation. This is not a claim about compact-support
homology of the feasible region.

## 4. Compact-relative sources and their exact scope

For nonempty `R subset {0,1,2}`, use the notation
`U_R=union_(i in R) B_i`, reserving intersections for `I_J=cap_(i in J)B_i`.
The source `Gamma_R` consists of nonnegative kernel blocks with the sum
of all their coordinate masses equal to one. Its image is `U_R`:
a positive-mass block exists and normalizes to `K_i`, and conversely a
witness in any `K_i` can be zero-padded into the source. Each fiber is
nonempty compact convex, since it is the intersection of a simplex with
linear equations. The source is closed in `R^9 x Delta^(56|R|-1)`, so its
projection to `U_R` is proper. Zero-padding is a closed inclusion and
commutes exactly with all base projections.

Proper base change identifies the stalk of `Rp_* Z` with the integral
cohomology of its fiber. It is Z in degree zero and zero otherwise, so
the canonical unit `Z_(U_R) -> Rp_*Z_(Gamma_R)` is a quasi-isomorphism.
Since `p` is proper, taking compact supports gives the stated natural
comparison. All spaces are locally compact Hausdorff semialgebraic spaces,
so singular and constant-sheaf cohomology agree. The needed fiber formula
and hypotheses are in the primary [Stacks Project, Lemma 20.18.1,
tag 09V5](https://stacks.math.columbia.edu/tag/09V5).

The hemisphere model is valid. Its dimension is nine: there are ten
coordinates `(t,X,Y,U_1,...,U_7)` and one sphere equation. On `t>0`,
division by `t` is a homeomorphism to `R^9`. Uniform multiplication of
all unsigned rows by `t^2` preserves every interior primal sign and
dual equation. The proposed entries are the exact degree-two homogeneous
extensions; the fixed coordinate and padding entries become `t^2` times
their constants. The extended source is closed in a compact hemisphere
times simplex. Its `t=0` portion is closed, and its open complement is
exactly `Gamma_R`. Zero-padding preserves these compact pairs.

The extended source need not be the closure of its interior, and its
boundary matrices need not remain rank four. Neither assertion is needed
or accepted. Extra pieces wholly in `t=0` are relative. Collapsing the
whole closed relative part gives the usual one-point compactification of
the open complement, even if that complement is not dense in the chosen
compact pair. Thus such pieces cannot add interior compact-support classes.

All seven sub-sources, every block face, every coordinate zero face, and
every block-support-cardinality level form a finite semialgebraic family.
Compatible triangulation of the one compact total source gives a finite
complex with each closed member a subcomplex and each other declared
member a union of open simplices. See the precise compatible statement
in Ohmoto--Shiota, [Theorem 2.2](https://arxiv.org/pdf/1505.03970), page 4.
Compactness makes its locally finite complex finite. This proves an
existence statement, not that a triangulation or all its boundary matrices
have been computed. It does not realize actual-parent sign strata or
the actual-parent projective normalization.

## 5. Self-contained filtered comparison and integral attachments

Define the closed-cover simplex resolution

```
N_R = union_(nonempty J subset R) I_J x Delta_J
      inside U_R x Delta_R.
```

The map `q:Gamma_R -> N_R` records the base and the block masses
`lambda_i=sum(w_i)`. Its support is exactly the set of nonzero blocks.
It is proper: all spaces are closed over the same base with compact
simplex factors. A particularly explicit section is available here. On
`B_i`, define `k_i` by active weights `a=1/[2(1-f_i)]` and give each of
the fifty padding rows weight `b/50=-f_i/[50(1-f_i)]`. Inactive weights
are zero. This is a continuous bounded semialgebraic normalized witness.

For `(v,lambda) in N_R`, set `s(v,lambda)_i=lambda_i k_i(v)` on each
positive-mass block, and zero on each zero-mass block. This is continuous
also at a disappearing block because `k_i` is bounded in a simplex.
Alternatively extend its formula continuously to all base points by
replacing `-f_i` with `max(-f_i,0)`; it is used as a kernel witness only
where `lambda_i>0`, which implies `f_i<=0`.

Then `q s=identity`, and
`H_h(v,w)=(v,(1-h)w+h s(q(v,w)))`, for `0<=h<=1`, is a deformation onto
the image of `s`. It preserves the kernel equations and nonnegativity,
all individual block masses, their exact supports, and every zero-padded
sub-source. It is proper as a homotopy: over the compact base projection
of any target compact set, its domain lies in the compact source over
that base set times `[0,1]`, and the inverse image is closed there.
The section is proper by the same argument. Hence `q` is a proper
homotopy equivalence on every closed block-support filtration level and
on each filtration pair, naturally in `R`.

The stratum of `N_R` with exact support `J` is
`I_J x relint Delta_J`. Orient `Delta_J` by increasing signature order.
Its face boundary has coefficient `(-1)^r` for deleting the `r`-th
vertex, attached by the literal inclusion `I_J -> I_(J\{j_r})`.
Compact-support cohomology reverses that inclusion to restriction. This
gives precisely the integral alternating restriction maps of the
Mayer--Vietoris diagram, with degree shift `|J|-1`. Compatible
triangulation of the base compactification and the product simplexes
justifies the relative cellular interpretation. The proper filtered
comparison above transports it to the source filtration, including
connecting maps, not merely the ranks of its graded groups.

This argument does not assert that the deformation preserves each
individual witness-coordinate zero face: its uniform-padding section
can populate previously zero coordinates. Those faces still occur in
the simultaneous finite source triangulation. The Mayer--Vietoris
comparison is for the block-mass filtration and its block faces. No
stronger refined comparison is inferred.

## 6. The labeled-parent exclusion is rigorous and limited

The primary local definition `a_I(Y)p=det(Y_I,p)` is pinned in
`ai/omreal/ATLAS_HELLY.md`, Section 2. Thus whenever `e in I`, the normal
`a_I` annihilates `y_e`, because that determinant repeats a column.
For a uniform rank-four parent `y_1` is nonzero. The normals for
`123,125,127,134` therefore all lie in the three-dimensional annihilator
of `y_1` and have determinant zero. Lexicographic indexing puts them
exactly at zero-based rows `0,2,4,6`. In the candidate their determinant
is one, so they cannot all annihilate any nonzero vector.

Multiplying rows by nonzero signs or positive scalars only multiplies
this determinant by nonzero factors, as does an invertible frame change.
The contradiction survives all transformations claimed by the candidate.
It excludes this specified labeled family from actual parent-derived
normals at every base point. No search over arbitrary row-to-triple
bijections, no sufficiency theorem for this identity, and no valid-parent
extension-signature assertion is part of the result.

## 7. Independent finite verification and research value

`independent_check.py` uses only the Python standard library. In the matrix
check, all residual identities are polynomials of degree at most three in
each of three independent `g` parameters: rows have degree one, the
polynomial primal witness degree two, and the dual numerators degree one.
Vanishing on four distinct values in each variable certifies the
identities by repeated univariate interpolation. Determinants are
computed by rational elimination, independently of the producer's
permutation expansion. The homogenized residuals have total degree at
most two in ten variables. The 66 points consisting of a translated
origin, its first and second coordinate steps, and its pairwise coordinate
steps determine every constant, linear, and quadratic coefficient. The
positive translated `t` keeps all rational evaluations defined.
Chart identities use independent squared-radius and slack parameters.
The full integer cubical contraction supplies the torsion-sensitive
cellular certificate. Four deliberately damaged versions are rejected.

This is a finite exact checker with manually reviewed degree bounds and
topological arguments, not a machine formalization of the global theorem.
No numerical approximation, random sampling, producer acceptance code,
bulk census, or external compute was used. `CHECK_OUTPUT.json` records
the passing run and seven frozen source hashes; `RESULT.json` records the
scope and the evidence defects. A later producer revision is a different
candidate and is not automatically accepted by this report.

The countermodel preserves stronger lower vanishings than the D3
reduction requires, yet its triple `H_c^0` and union `H_c^2` survive. Its
pair `H_c^1` term is zero, so it does not demonstrate failure of a pair
injectivity map; it isolates the generic triple-escape failure. It shows
why compact-relative source existence and those lower vanishings cannot
alone settle D3. The parent-specific annihilator identity is a concrete
omitted hypothesis, but its ability to force escape remains unproved.

**Theorem ledger delta: zero.** All seven named actual-parent obligations,
global coverage, and the certified exhaustive residual remain unchanged.
This review supports informational credit and retirement of the generic
package-only implication. It supplies no independent reason to continue
that same route and makes no cycle-wide investment decision beyond it.
