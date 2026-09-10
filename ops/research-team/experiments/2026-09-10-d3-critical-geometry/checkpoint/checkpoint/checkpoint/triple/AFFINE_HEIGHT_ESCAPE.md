# Affine height escape, including rank drops

This is a conventional deductive statement. It requires no enumeration of
orbits and no pointwise numerical certificate. The general argument is inherited: `inputs/DIAG3_TRIPLE_SEQUENTIAL_AFFINE_COMPRESSION.md`, Section1, gives the same square-affine proof in two coordinates, citing `DIAG3_AFFINE_FIBER_FRONTIER.md`. The proof below applies that argument in three coordinates to the new fixture. It is not claimed
to close an original diagonal-three obligation.

## 1. General affine-fiber lemma

Let `W` be an open semialgebraic subset of `R^b`, with `b>0`, and let
`Omega` be an open semialgebraic subset of `W x R^d`. Suppose every nonempty
fiber `Omega_x` is convex. Let

`Z = {(x,h) in Omega : A(x)h = c(x)}`,

where `A,c` are continuous semialgebraic coefficient functions and `A` has
`m<=d` rows. Then every connected component of `Z` is noncompact.
Consequently `H_c^0(Z;R)=0` for every coefficient ring `R`.

**Proof.** Suppose `C` were a nonempty compact connected component. Take
`(x,h) in C`. The full fixed-base fiber

`Z_x = Omega_x intersect {h' : A(x)h'=c(x)}`

is a nonempty convex relatively open subset of an affine space of dimension
`d-rank A(x)`. It is connected, contains `(x,h)`, and therefore is contained
in `C`. It is also closed in `Z`, being the inverse image of the closed
singleton `{x}` under the projection. Hence it is closed in compact `C` and
must be compact. A nonempty open subset of a positive-dimensional affine
space is not compact. Therefore `rank A(x)=d` at every point of `C`.

If `m<d`, this is already impossible. If `m=d`, `A(x)` is invertible at every
point over `C`. In a neighborhood of each such point, `Z` is the graph of the
continuous semialgebraic function `A(x)^{-1}c(x)` over an open subset of `W`.
Choose a small connected base neighborhood whose graph remains in `Omega`;
its graph lies in `C`, since it is connected and meets `C`. Thus the image
`pi(C)` is open in `W`, and therefore open in `R^b`. The image is compact by
continuity of `pi`. A nonempty subset of `R^b`, `b>0`, cannot be both open and
compact. This is the final contradiction.

All rank drops were included in the first paragraph. No properness of the
whole projection, constant-rank assumption, or unproved specialization map
was used. Full fixed-base fibers and their closedness in `Z` are essential:
a noncompact subset alone need not contradict compactness of its containing
component. QED.

## 2. Parent-contraction application

Let `X` be any normalized connected realization component of a uniform
rank-four oriented matroid on eight labels. Fix a parent label `e`.
Normalize it to the last coordinate vector and write the other columns as
`y_j=(a_j,h_j)`, where `a_j in R^3`.

The contracted parent is uniform of rank three on seven labels. A fixed
projective frame identifies its realization space with an open subset `W`
of `R^6`. The lift heights have seven entries. Removing the three-dimensional
linear-functional height gauge and fixing the positive height scale by one
prescribed nonzero parent bracket leaves three affine height coordinates.
All remaining parent-bracket inequalities are affine in these coordinates.
Thus the full parent-sign residence fiber is an open convex polyhedron in
`R^3`. If it meets `X`, connectedness of that fiber puts the entire fiber in
`X`; restricting to a parent component does not cut the fiber into pieces.
The resulting contraction presentation has precisely the hypotheses on
`Omega` of Section 1.

For a parent triple `I`, let `a_I(Y)` be its derived normal. If `e in I`, its
last coordinate is zero and its other coordinates are independent of the
heights. If `e notin I`, its last coordinate is independent of the heights,
and its other coordinates are linear in the heights.

Take a quartet `E` of derived normals with **at least two triples containing
e**. Its determinant `D_E` is affine in the heights. Indeed, expand in the
last coordinate. With exactly two height-independent horizontal rows, any
nonzero term takes the last coordinate from one of the other two rows; its
remaining horizontal determinant contains two constant rows and one linear
row. With three or four constant horizontal rows, the conclusion remains
true (the determinant is height-independent or identically zero).

For a residual occurrence the source certificate gives

`D_E = u_E q_f`,

where `u_E` is a nowhere-zero parent-bracket unit on `X`. The unit may depend
on the heights. One must retain the affine equation `D_E=0`, rather than
silently claiming that the primitive quotient `q_f` is affine. Their zero
sets on `X` are nevertheless exactly equal.

**Application.** Choose at most three primitive residual factors, and for
each choose a certified occurrence quartet containing one common parent
label `e` at least twice. Then their common zero set in `X` has no compact
connected component.

Apply Section 1 with `b=6`, `d=3` to the affine equations `D_E=0`. Repeated
factors, redundant equations, identically zero specialized rows, and every
rank-drop fiber are included. The statement is uniform over parent
components and all parameter values; its proof uses no fixed Gordan witness,
continuous witness selector, or deleted boundary stratum.

If those factors are aligned with specified signatures, their common zero
set lies in the corresponding simultaneous bad locus by the inherited
fixed-unit circuit theorem. This settles those factor strata. It does not
assert that every compact component of the original triple-bad locus
reaches a factor triple admitting this common-label certificate.

## 3. The new rigid-boundary example satisfies the criterion

The three occurrence quartets are

- `123 / 145 / 246 / 357`;
- `127 / 158 / 234 / 357`;
- `236 / 248 / 456 / 578`.

Parent label `2` appears exactly twice in each quartet. Thus the application
settles their common factor-zero locus on every uniform parent component,
even though the displayed exact point has no common weak-primal vector and
its unique witness-support union has no label of degree at most two.

At the exact normalized quotient coordinates

`(b,c,e,f,h,i)=(7,6,5,-4,2,-2)`,

the occurrence determinants in the height row `(a,d,g)` are

`d-31`,
`-16d+45g+26`,
`7a-48d+150g-109`.

Their Jacobian determinant is `315`, so this fixed base fiber is a single
point. Noncompactness comes from variation of the six quotient coordinates;
requiring an additional fixed-base height motion here would be an unnecessary
strengthening. On all other bases the rank-drop part of Section 1 supplies
the missing case automatically.

This example also distinguishes that parent contraction from a different
attempt which freezes all three weak-primal points. The latter has a
rank-seven linear system on eight heights, leaving only projective height
scale. That failed stronger contraction does not invalidate the parent
contraction above.

## 4. Scope and audit need

The original triple-bad compactness question remains open. No census count
has been changed. Independent review should check the full-fiber closedness,
normalization/gauge dimension, and affine determinant calculation. The general affine argument is inherited, and no novelty or new orbit-coverage count is assigned to it.
