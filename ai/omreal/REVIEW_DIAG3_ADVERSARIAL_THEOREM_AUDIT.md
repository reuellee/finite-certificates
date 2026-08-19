# Diagonal three: adversarial theorem audit and smallest new certificate

## Outcome

The score remains `2/9`.  Three conclusions drive the recommendation.

1. Multi-affinity, squarefreeness, fixed parent-chamber signs, and even
   pairwise-independent gradients do **not** exclude a compact component of
   three common zeros in nine variables.  Section 2 gives a smooth compact
   `S^6` countermodel inside an arbitrarily small chamber ball.
2. There is a genuinely broader, theorem-safe triple certificate which has
   not been exhausted by the existing unit-minor or constant-plane scans.
   It permits an arbitrary, nondecomposable constant trivector in a fixed
   height hyperplane.  Section 1 gives the exact statement.  However, the
   bounded hard-canary coordinate/log screens are now strongly negative:
   exact for product targets of length at most three, with a one-prime
   diagnostic covering the recorded longer successful product shapes and
   degree-five modulo-ideal multipliers.  This remains a valid secondary
   certificate, not the leading hard-canary route.
3. The exact boundary-stratified roadmap has a positive replayable
   boundary-to-boundary simple-fold chain for one slice component of a hard
   source presentation, and the pair work has a coverage-accounted compressed
   incidence seed.  Neither construction is global yet, but extending those
   finite roadmap/quotient objects is now
   smaller than continuing raw coordinate-trivector searches on the hard
   canaries.

The pair obligation cannot be inferred from convex Gordan coordinate faces
or local Koszul identities alone.  A proof without an explicitly named
atlas is possible only if it constructs an equivalent proper global chain
contraction; the invariant finite endpoint is still the mod-two middle-rank
certificate with an integral `MN=0` lift.

On the finite reductions currently recorded in the repository, no switch to
another open diagonal is justified; Section 6 gives the bounded comparison.

## 1. Arbitrary-trivector height certificate

Let `X subset R^9` be one open normalized parent chamber and let

\[
 q=(q_1,q_2,q_3):X\longrightarrow\mathbb R^3,
 \qquad
 \omega=dq_1\wedge dq_2\wedge dq_3.
\]

Fix a nonzero constant covector `h` and a constant trivector

\[
                    C\in\Lambda^3(\ker h).
\]

The trivector need not be decomposable.  Suppose there is a polynomial
identity

\[
                         \omega(C)=U,                 \tag{1}
\]

where `U` is a nonzero scalar times a product of parent brackets.  Then every
connected component of `X intersection q^{-1}(0)` is noncompact.

Indeed, if `K` were a compact component, the linear height `h` would attain
an extremum at some `x in K`.  If `rank(dq_x)<3`, then `omega_x=0`.  Otherwise
the common zero set is a smooth six-manifold near `x`.  The constrained
extremum gives

\[
                    h\in\operatorname{span}
                    \{dq_1(x),dq_2(x),dq_3(x)\}.
\]

Consequently `dq_x` restricted to `ker h` has rank at most two, so
`omega_x` vanishes on all of `Lambda^3(ker h)`, including `C`.  Both cases
contradict (1), since every parent bracket is nonzero on `X`.

There is no hidden boundary or regularity hypothesis.  A compact subset of
the open chamber stays away from every parent wall; singular extrema are the
first rank case, and regular extrema are the second.  Semialgebraic sets are
locally connected with finitely many components, so componentwise
noncompactness gives

\[
                     H_c^0(X\cap q^{-1}(0);R)=0
\]

for every coefficient ring `R`.

It is enough more generally to prove

\[
             \omega(C)=U+a_1q_1+a_2q_2+a_3q_3,         \tag{2}
\]

with polynomial `a_i`, because (2) restricts to (1) on the common zero set.

### 1.1 Why this was not already searched

For a coordinate height `h=dx_j`, the certificate space has dimension

\[
                       \dim\Lambda^3(\ker h)={8\choose3}=56.
\]

The existing role-frame unit-minor sweep tests the 56 coordinate basis
trivectors separately.  The frame-1119 constant-shear layer tests signed
sums of two minors sharing two coordinate directions; these are
decomposable planes of the form

\[
                   e_a\wedge e_b\wedge(e_c\pm e_d).
\]

Neither search tests an arbitrary linear combination of the 56 minors.
The corrected-Gale sparse-plane screen is likewise explicitly decomposable.

Thus the next exact scan should, for each residual row, role frame, and
coordinate height:

1. form the 56 minors not using the height coordinate;
2. row-reduce their polynomial coefficient span modulo one or more good
   primes;
3. test whether that span contains a parent-bracket product, first exactly
   as in (1), then modulo the ideal `(q_1,q_2,q_3)` as in (2); and
4. replay every modular proposal by an exact integer identity.

Products should be found by recursive divisibility of the whole 56-dimensional
subspace, not by enumerating a small number of bracket products.  A product
may require substantially more factors than the former individual-minor
certificates.

There is a second valid coordinate system.  Since the nine normalized free
coordinates are nonzero parent brackets on a fixed chamber, put
`u_j=log|x_j|`.  Replace each Jacobian column by
`x_j partial/partial x_j` and apply the same theorem to a linear height in
`u`.  For a general nondecomposable `C`, the resulting sums carry different
unit monomial weights and are not equivalent to the prior constant-plane
scan.  This is particularly relevant to triples of types 49 and 50.

### 1.2 Exact bounded log-trivector result

The coordinate-height scan has now also been run in the normalized logarithmic
coordinates, not merely proposed.  For every one of the six hard canaries and
every `h=u_j`, it formed the full 56-dimensional constant span of the log
minors

\[
 \det\left(x_{i_b}\frac{\partial q_a}{\partial x_{i_b}}\right)_{a,b=1}^3,
 \qquad j\notin\{i_1,i_2,i_3\}.
\]

It tested `1` and every product with repetition of one, two, or three of the
62 nonconstant parent brackets.  The exact target accounting is

\[
 1+62+1953+41664=43680
\]

for each of the 54 `(canary,height)` pairs.  There are **no hits**.  This is
an exact support obstruction, not a probabilistic modular conclusion: every
one of the 43,680 targets has a monomial outside the union of the supports of
the 56 log minors.  The auxiliary modular ranks range from 46 through 56 but
are not needed for the no-go.

This excludes all arbitrary, including nondecomposable, constant trivectors
against parent products of length at most three in these 54 frames.  It does
not exclude longer products, the identity modulo `(q_1,q_2,q_3)` in (2), or
other role frames.

A separate one-prime diagnostic did probe the modulo-ideal enlargement.  At
`p=1,000,000,007` it adjoined `q_i m` for all 2,002 monomials `m` of degree at
most five for each `i` (modular span ranks up to about 6,046), then tested the
33,007 distinct parent-product shapes of lengths four through nine which
actually occur in the 65,550 Morse and 61 shear certificates.  All 54
coordinate heights again give zero hits.  Lower degree layers also give zero
against products of length at most three.  This is useful falsification data,
but it is deliberately only a one-prime bounded diagnostic, not an exact
no-go for (2).

There is no additional *individual* affine parent-bracket coordinate hidden
in the list.  Exact enumeration shows that its only nonconstant monomial
brackets are precisely the nine free coordinates, up to sign.  Thus an
individual parent-bracket logarithm is affine in
`u=(log|x_1|,...,log|x_9|)` only in these coordinate cases.  A nontrivial
linear combination of bracket logarithms would be affine only after an exact
multiplicative identity among the bracket polynomials had been exhibited;
none was assumed or counted here.  In particular, the logarithm of a
genuinely binomial parent bracket is a nonlinear height and is not covered by
the constant-covector span calculation above.

## 2. Smooth multi-affine compact-component countermodel

Choose any interior point `p` of any parent chamber.  Write `y=x-p`, put

\[
 S=\sum_{i=1}^8y_i,
 \qquad
 P=\sum_{1\le i<j\le8}y_iy_j,
\]

and choose `epsilon>0` small enough that the set below stays inside a
Euclidean ball contained in the chamber.  Define

\[
 \begin{aligned}
 q_1&=y_9-S,\\
 q_2&=y_9S-2P-\epsilon^2,\\
 q_3&=y_1.
 \end{aligned}                                           \tag{3}
\]

All three polynomials are affine in every coordinate separately.  Translation
by `p` preserves that property.  On `q_1=0`, the elementary identity

\[
                  S^2-2P=\sum_{i=1}^8y_i^2
\]

turns the common zero set into

\[
 \{q_1=q_2=q_3=0\}
 =\left\{y_1=0, \sum_{i=2}^8y_i^2=\epsilon^2,
                    \ y_9=S\right\}
 \cong S^6.                                             \tag{4}
\]

This is a smooth compact component, entirely in the prescribed parent
chamber.  The three gradients have rank three on (4): after restricting to
`q_1=0`, `dq_2` is the nonzero radial covector
`2 sum_i y_i dy_i`, while `dq_3=dy_1` is independent of it along the sphere.
In particular every pair of gradients is independent there.

Therefore none of the following is a sufficient triple theorem:

* multi-affinity or coordinate squarefreeness;
* orthogonal convexity of all coordinate sections;
* fixed parent-bracket signs; or
* pairwise Jacobian independence.

The actual equations have additional structure, but it is not uniform
multi-affinity: type 51 contains `-b^2f` in the standard gauge.  Types 49 and
50 are differences of two products of normalized parent brackets, whereas
type 51 is the exact three-term bracket sum

\[
 q_{51}=[1236][4678]-[1267][2468]-[1367][2468].       \tag{5}
\]

The known exact nonconvexity of the log-bracket image rules out promoting
the 49/50 hyperplane description to a convex-slice theorem without an
additional argument.

## 3. The pair obstruction remains global

The block-mass filtration of the proper block-Gordan resolution is exactly
the compact-support Mayer--Vietoris spectral sequence.  Convex coordinate
faces prove higher coherence after codimension-one maps exist; they do not
compute the cohomology of the resulting global incidence complex.

The smooth graph model already recorded in
`DIAG3_PAIR_DIFFERENTIAL_ENDS.md` has

\[
 B_i\cong\mathbb R^8,
 \qquad
 B_i\cap B_j=T\cong\mathbb R\times S^6,
\]

for all three pairs, while the alternating restriction kernel is
`Z^2`.  Its three regions are proper and pairwise incomparable.  Replacing
the scalar wall functions in the formal 56-by-4 singleton-witness
construction of `BLOCK_GORDAN_AUDIT.md` by these three graph equations also
gives compact convex singleton Gordan fibers, nonzero rows, and full row
span.

There is now a stronger shared-normal version of this countermodel.  On
`X=R^9` with coordinates `(t,u_1,...,u_7,z)`, put

\[
 g=\sum_{r=1}^7u_r^2-1,
 \qquad q_0=z,
 \quad q_1=z-g,
 \quad q_2=z-g(2+g^2).
\]

For `k=0,1,2`, put `d_k=e_k in R^4` and use the cyclic pairs
`(a,b)=(1,2),(2,0),(0,1)`.  In `d_k^perp` take

\[
\begin{aligned}
 b_{k1}&=e_a+e_b,& b_{k2}&=e_a-e_b+e_3,\\
 b_{k3}&=-e_a+2e_b+e_3,& b_{k4}&=-e_a-2e_b-2e_3,
\end{aligned}
\]

and the twelve common unsigned polynomial normals

\[
 n_{kr}=b_{kr}\ (r\leq3),
 \qquad n_{k4}=b_{k4}+q_k^2e_k.                 \tag{6}
\]

Give signature `sigma_k` owner sign `+` on group `k`; on group `j != k`
use the sign of the nonzero number `<b_{jr},e_k>`.  At `q_k=0` the four
owner rows are a support-minimal positive circuit, because they sum to zero
and the first three span `d_k^perp`.  Conversely, with

\[
 c_k=\tfrac35e_a+\tfrac25e_b+\tfrac45e_3,
 \qquad p=c_k+s e_k,
\]

the owner dot products are `(1,1,1,-3+q_k^2s)` and all signed nonowner dot
products become positive for sufficiently large `s`.  Hence the exact Gordan
bad set for `sigma_k` is `B_k=Z(q_k)`.

All three pair intersections and the triple intersection are

\[
 T=\{z=0,g=0\}\cong\mathbb R\times S^6.
\]

Thus every exclusive pair stratum is empty, every restriction
`H_c^1(B_i cap B_j)->H_c^1(T)` is the identity on `Z`, and the alternating
map is `[1,-1,1]`, with kernel `Z^2`.  Equivalently
`H_c^2(B_0 union B_1 union B_2;Z)=Z^2`; Alexander duality gives
`H_tilde_6(X minus union B_k;Z)=Z^2`.  The owner-0 rows realize all four
antipodal trace classes across the three signatures, so the usual sign-shatter
private-independence hypothesis also holds.

Normalized Gordan fibers and every coordinate restriction in this model are
compact convex polytopes, with all zero-block faces retained.  Therefore
private contraction, quotient-loop faces, a full Gordan simplex, and
fiberwise Koszul exactness still preserve the global `Z^2` class.  The model
deliberately lacks only the actual Pluecker occurrence coupling
`n_I=*(y_a wedge y_b wedge y_c)` for the 56 triples of one uniform `4 x 8`
parent.  Any surviving atlas-free theorem must use that global coupling to
construct a proper colored chain contraction.  Generic Gordan, convexity,
loop, or sign-shatter data are insufficient.

The dependency-free exact replay is
`verify_diag3_atlas_free_gordan_no_go.py`.

The special third-compound identity of the actual rows remains a possible
source of a new global theorem.  But a proof using it must still construct a
proper end map or a chain contraction with the same information.  Pointwise
Koszul identities, local root connectivity, and all-codimension convex
carriers do not specify split--merge incidence or parent infinity.

The sharp necessary-and-sufficient finite endpoint over `Q` is therefore:

1. a coverage-certified finite relative cell complex for the triple and
   exclusive-pair strata;
2. an integral signed lift with `MN=0`; and
3. the mod-two identity

\[
       \operatorname{rank}_{\mathbb F_2}N+
       \operatorname{rank}_{\mathbb F_2}M=\dim C^1.    \tag{7}
\]

Any purported atlas-free proof should be tested by extracting from it the
chain homotopy or frontier map that implies (7).  If no such map exists, the
argument has omitted the invariant pair obligation.

## 4. Exact cluster-web audit

The full homogeneous occurrence determinants, rather than their dehomogenized
chart factors, have been compared with the 120 quadratic and 174 cubic
`Gr(4,8)` cluster variables tabulated in Zhang--Tang--Zhao,
arXiv:2507.18432, Tables 3--4.  Convenient exact bracket expressions
for the three core support representatives are, up to one global sign,

\[
\begin{aligned}
 F_{49}&=[2346][1245][1357]-[1345][1246][2357],\\
 F_{50}&=[2346][1245][1378]-[1345][1246][2378],\\
 F_{51}&=-[1245][1236][4678]-[1345][1267][2468]
          +[1245][1367][2468].                         \tag{8}
\end{aligned}
\]

Their column multidegrees are respectively

\[
 (2,2,2,2,2,1,1,0),\qquad
 (2,2,2,2,1,1,1,1),\qquad
 (2,2,1,2,1,2,1,1).                                   \tag{9}
\]

The outcome is asymmetric.

* `F_49` is not cubic-cluster: every published cubic has four entries `2`
  and four entries `1`, while (9) has an isolated label and five entries
  `2`.  Testing all `7,200` degree-compatible arbitrary `S_8` relabels of
  the three quadratic representatives also finds no identity
  `F_49=[I]Q` with a single parent-bracket factor.
* `F_50` has an admissible cubic multidegree, but exact comparison with all
  `8,064` degree-compatible arbitrary `S_8` relabels of the fourteen
  published cubic representatives gives no match.  The stronger
  bracket-times-quadratic superset has `63,360` candidates and also gives no
  match.
* `F_51` is genuinely in an arbitrary-`S_8` orbit of a cubic cluster
  variable.  For example, applying the one-based relabeling
  `(6,2,3,1,5,4,8,7)` to the second printed cubic representative gives

\[
 [1458][1246][2367]-[1458][1236][2467]
 -[1456][1267][2348]-[1245][1468][2367]=F_{51}.        \tag{10}
\]

  The equality is exact in the Grassmannian coordinate ring.  The canonical
  labeling itself is not a dihedral translate of a printed representative;
  it becomes cluster only after the non-dihedral `S_8` reframe.

The hard-row kind accounting is

```text
(36,51,49) (50,50,51) (50,51,50)
(50,50,50) (50,49,50) (48,51,51).
```

Consequently the first five hard canaries cannot have all three occurrence
equations be members of the tested cluster-variable families after any common
`S_8` reframe: each contains a type 49 or 50 equation which fails the cubic
and single-parent-factor quadratic `S_8`-orbit tests above.  This blocks a
direct certificate that requires all three unrescaled occurrence equations to
belong to those tabulated quadratic/cubic cluster-variable orbits.  It does
not rule out higher-degree or Laurent-rescaled cluster coordinates, nor a
more general Coble word whose intermediate functions are not cluster
variables.

The dependency-free replay is `verify_diag3_cluster_web_audit.py`.  In
particular it expands (8) and (10) on a fully generic `4 x 8` matrix, so the
positive type-51 claim is an exact Grassmannian coordinate-ring identity,
not an equality observed only after projective normalization.

## 5. Coble/Weyl words

The strongest positive development is now the exact Krawczyk roadmap cell
for `(5563,16134,19284)`.  Its certified slice graph is

```text
[2678] parent boundary -- 160 regular cells -- simple-fold bridge
                       -- 160 regular cells -- [2467] parent boundary.
```

The replay has 322 rational-box vertices, 321 glued segments, transverse
source-parent exits, and strict separation from the nontarget parent brackets
and the named chart denominators along the chain.  The all-`26,740` residual-
factor separation check is local to the fold neighborhood; other residual
factors have not been excluded segment by segment.  The exact critical census
is saturated by `[1234]t(4t+3)(20t-3)`, but an independent exact incidence
calculation closes that gap: `[1234]=0` is parent boundary, while the three
interpolation divisors respectively force `[1348]=[1578]=0`, `P_4=P_8`, and
`[2578]=0`.  Thus, subject to the pinned `msolve-0.10.1` completeness result,
the unsaturated pinned slice has no compact component.  This is still only
one fixed-base slice, not a closure-complete full-space cell, an all-component
theorem for its source orbit, or a proof of triple `H_c^0` vanishing.  It
nevertheless shows that exact continuation through the formerly ambiguous
fold is viable, which is why completing every full-space chart frontier and
quotienting the resulting roadmap remains a promising triple route.

The depth-one standard-Cremona no-go is not a theorem against longer words.
At depth two, ordered pairs of four-point centers reduce under simultaneous
relabeling to the four nontrivial intersection sizes `0,1,2,3`, so a shallow
word-type screen is finite.  This remains a legitimate discovery experiment.

It is not yet a proof route by itself.  Every state must retain the full
labeled occurrence determinant, its normalization weights, pulled-back
parent divisors, denominators, and internal target-nonuniform frontiers.  A
longer word is biregular only off those divisors.  Finding an
affine presentation on one word chart proves nothing about a component that
closes through an internal word frontier unless the adjacent chart and its
attachment are included.  The false normalized-Gale shortcut is the exact
regression for this bookkeeping.

Accordingly, the exact boundary roadmap and compressed pair incidence complex
outrank both a shallow Coble BFS and further raw arbitrary-trivector scans.  A
shallow Coble BFS remains a boundary-aware discovery tool; even if it closes
the triple endpoint, it does not by itself supply the balanced pair-end map.

## 6. Comparison with the other diagonals

The currently recorded finite reductions do not exhibit a shorter switch.

* `s=4` already requires a fivefold total-degree complex and retains
  `1,715,980` cover-all single supports before its global split--remerge
  differential.
* `s=9` has a clean graph criterion but no full-dimensional chamber roadmap;
  the first projection layer already adds 142 new irreducible factors, and
  coverage is required across 2,604 parent classes.
* `s=7,8,9` have full-rank private-witness reductions, not vanishing
  theorems; their fixed-frame compatibility spaces remain global.

On these recorded certificate sizes, diagonal three remains the best-supported
target.  The priority order from this audit is now:

1. extend the exact Krawczyk/regular-fiber boundary roadmap from the positive
   hard simple-fold chain, while quotienting equivalent occurrence
   presentations only after all frontier incidences are retained;
2. complete the coverage-certified compressed pair incidence complex and its
   mod-two middle-rank test (or construct a global proper chain contraction
   which directly implies it);
3. retain arbitrary-trivector identities as a secondary all-residue modular
   screen, promoting only exact replayed hits; and
4. use shallow Coble words only as a boundary-aware secondary discovery
   layer.
