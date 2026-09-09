# Full-dimensional convex countermodel to a generic D3 deduction

Status: coordinator proof candidate; independent review pending.

## Statement

There is a polynomial family of one common unsigned `56 x 4` full-rank
matrix over `X=R^9`, and three fixed row-sign signatures with nonempty proper
pairwise-incomparable strict-feasibility regions, for which:

1. every bad set and every pairwise bad intersection has zero compact-support
   cohomology in every degree, with integer coefficients;
2. the triple bad intersection is compact, connected, and nonempty;
3. `H_c^2(B_0 union B_1 union B_2;Z)=Z`;
4. the total-mass normalized block-Gordan sources have compact convex fibers,
   proper projections, zero-padding naturality, and simultaneous finite
   compact-relative semialgebraic source models.

Thus even these strengthened generic inputs do not imply D3. This is not a
9DVL counterexample: a shared-label rank identity of actual parent-derived
normals fails identically in this model. The exact failure is given below.

## The bad geometry

Write a point of `R^9` as `(x,y,u)` with `u in R^7`, and set

```
f_0 = -x,
f_1 = -y,
f_2 = x+y+sum(u_j^2)-1.
F_i = {f_i>0},     B_i = {f_i<=0}.
```

The three bad sets are closed, convex, full-dimensional, and noncompact:

```
B_0 = {x>=0},
B_1 = {y>=0},
B_2 = {x+y+||u||^2<=1}.
```

Each `B_i` is semialgebraically homeomorphic to `R^8 x [0,infinity)`.
For `B_2` the coordinates are `(x,u,z)` where
`z=1-x-y-||u||^2>=0`, with inverse `y=1-x-||u||^2-z`.
Each pair is homeomorphic to `R^7 x [0,infinity)^2`:

| Pair | Coordinates | Inverse |
| --- | --- | --- |
| 01 | `(u,x,y)` with `x,y>=0` | identity |
| 02 | `(u,x,z)` with `x,z>=0` | `y=1-x-||u||^2-z` |
| 12 | `(u,y,z)` with `y,z>=0` | `x=1-y-||u||^2-z` |

The half-line has compact-support cohomology zero in all degrees: its
one-point compactification is `[0,1]` with relative point `{1}`, whose
relative cellular coboundary is the isomorphism `Z -> Z`. Product with
Euclidean factors shifts degree, and tensoring additional half-line factors
preserves acyclicity. This proves the singleton and pair claims over `Z`.

The triple intersection is

```
T = {x>=0, y>=0, x+y+||u||^2<=1}.
```

It is closed and bounded (`0<=x,y<=1`, `||u||<=1`), hence compact. It is
nonempty and convex, hence contractible. Thus `H_c^0(T;Z)=Z` and its higher
cohomology vanishes. In the closed-cover compact-support Mayer-Vietoris
spectral sequence, singleton and pair terms vanish, and the only triple
term is this `Z` shifted by two. Consequently the bad union has `H_c^2=Z`
and zero compact-support cohomology in other degrees.

There is also a direct description of the common feasible locus:

```
F_0 cap F_1 cap F_2
  = {x<0, y<0, ||u||^2>1-x-y}
  ~= S^6 x (0,infinity)^3.
```

The homeomorphism sends `(theta,a,b,c)` to
`x=-a, y=-b, u=(sqrt(1+a+b)+c)*theta`. Its inverse takes
`a=-x`, `b=-y`, `theta=u/||u||`, `c=||u||-sqrt(1-x-y)`.
Therefore its reduced degree-six homology is `Z`, agreeing with the D3
degree `9-3=6`. No inferred differential or numerical topology is needed.

## One unsigned matrix and three signatures

Let `e_1,...,e_4` be the standard row covectors of `R^4`. The first six
unsigned rows are, for `j=0,1,2`,

```
a_(2j)   =  e_(j+1) + f_j e_4,
a_(2j+1) = -e_(j+1) + f_j e_4.
```

The remaining 50 rows are `e_4`. Every row is nonzero. Rows `0,2,4,6`
form a matrix of determinant one, so the row span is always four-dimensional.

Signature `sigma_i` keeps both rows of module `i` positive. In each other
module it keeps the even row positive and negates the odd row. All 50
additional rows have positive sign. This is one common unsigned family.

Because the additional rows require `p_4>0`, summing the two inequalities
of the active module gives `2 f_i p_4>0`. Hence feasibility implies `f_i>0`.
Conversely choose `p_4=1`, `p_(i+1)=0`, and
`p_(j+1)=f_j^2+1` for `j!=i`. The inactive inequalities are

```
f_j^2+1+f_j = (f_j+1/2)^2+3/4 > 0,
f_j^2+1-f_j = (f_j-1/2)^2+3/4 > 0.
```

The active inequalities both equal `f_i`, and extra rows equal one.
This proves exactly `F_(sigma_i)={f_i>0}`.

For `f_i<=0`, put unnormalized dual weights one on each active row and
`-2 f_i` on row 6. All other weights are zero. Their signed normal sum is
zero, their weights are nonnegative, and total mass `2-2 f_i` is positive.
Division by that mass gives an exact normalized Gordan witness.
The positive-kernel fiber may have many points for `f_i<0`; only compact
convexity is used. No singleton-fiber assertion is made for that interior.

The rational points `(1,-1,2,0,...,0)`, `(-1,1,2,0,...,0)`, and
`(-1,-1,0,...,0)` belong exclusively to `B_0`, `B_1`, and `B_2`, respectively.
They witness all six directed non-inclusions between the `F_i`.
The point `(-1,-1,2,0,...,0)` is feasible for all three. Thus the three
regions are nonempty, proper, and pairwise incomparable.

## Compact-relative source properties

Compactify the base by the closed upper hemisphere
`H={t>=0, t^2+X^2+Y^2+sum(U_j^2)=1}`, with interior `t>0` identified with
`R^9` by `(x,y,u)=(X,Y,U)/t`. The relative boundary is exactly `t=0`.
Multiply each unsigned row by the same positive interior factor `t^2`.
The resulting entries extend polynomially:

```
t^2 f_0 = -X t,
t^2 f_1 = -Y t,
t^2 f_2 = (X+Y)t + sum(U_j^2) - t^2.
```

For every nonempty signature subset, impose the extended block equations
and nonnegative total mass one over `H` times the relevant weight simplex.
This defines a closed subset of a compact semialgebraic set. Its complement
of the `t=0` part is precisely the original source, since multiplication by
`t^2>0` changes no interior equation. Extra boundary fibers are wholly relative.
Zero padding preserves every equation and defines closed inclusions of pairs.

There are finitely many signature subsets, support faces, and support-cardinality
filtration levels. Compatible semialgebraic triangulation gives a simultaneous
finite relative model. Proper projection with nonempty convex fibers gives
the usual compact-support comparison; the block-mass map identifies the
filtered comparison as in the source audit. This is the same *type* of
source conclusion, not an assertion that this family meets the actual
rank-four parent hypotheses or its projective-frame normalization.

## Exact separation from parent geometry

Index the 56 rows by lexicographically ordered triples of `[8]`. Rows
`0,2,4,6` correspond to `123,125,127,134`, all containing label 1.
Their determinant is identically one in our unsigned family.

For actual parent columns, each derived normal `a_I` annihilates every
`y_e` with `e in I`. Four normals whose triples contain one common label
therefore lie in the three-dimensional annihilator of that nonzero column;
their determinant is zero. This remains true under row sign changes,
positive row scalings, and invertible changes of the four-dimensional frame.

Our determinant-one minor is a direct obstruction to this labeled family
being actual parent-derived normals. It identifies a concrete geometric
constraint omitted by the generic source/lower-vanishing argument. It does
not establish that this constraint alone suffices for D3, nor exclude every
possible relabeling of an arbitrary matrix.

## Verification scope and consequence

`check_full_dimensional_countermodel.py` checks polynomial identities,
matrix rank and dual/primal identities, domain coordinate changes, rational
antichain witnesses, and the integral relative cellular complexes for the
half-line products. The global topological proof is the explicit argument
above and must be reviewed independently; a successful script is not itself
a formal proof of all topology.

The new separation result is stronger than the earlier generic block-format
example because it preserves the known lower vanishings, uses one common
unsigned matrix, and has convex full-dimensional bad sets. It is informational
for 9DVL. It neither changes the 2/9 score nor closes one of V11's seven
obligations. It rules out a proof based solely on the listed generic package.
