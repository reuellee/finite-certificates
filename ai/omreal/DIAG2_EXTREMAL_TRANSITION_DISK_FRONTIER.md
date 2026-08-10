# Diagonal two: exact parent-187 transition-disk frontier

## Result

The next two-dimensional target after the complete parent-187 `e`-line is
now defined exactly.

In perturbation coordinates

```text
x = d - d_0,
y = e - e_0,
```

the complete `d/e` slice of the parent realization cell is a bounded convex
hexagon.  Its six boundary corners are the pairwise intersections

```text
(1347,2678), (2678,4578), (3678,4578),
(2567,3678), (1578,2567), (1347,1578).
```

All seventy parent brackets restrict to affine functions or constants on
this plane.  All `26,740` primitive global residual factors have distinct
restrictions of total degree at most two; `24,750` are nonconstant and no two
of their equations are proportional.  Thus the full target is an exact
conic arrangement in a compact polygon, rather than an arbitrary sampled
rectangle.

Constructing all pairwise conic intersections would obscure the proof
signal.  A link-determinant reduction instead gives an exact exchange-
constancy cut set for each wall occurrence already known to change a tracked
record on the central line.  The ten seed occurrences have `164` global
link-factor memberships representing `142` factor IDs.  Four memberships
are constant and nonzero after restriction to this disk, leaving an effective
disk frontier of `160` memberships and `139` nonconstant factors.

This is the exact geometry and a structural reduction for the line-seeded
wall components.  It is not yet a cell decomposition of the hexagon and does
not prove diagonal two.  The honest 9DVL score remains `1/9`.

## 1. Exact disk geometry

The standard parent chart is

```text
[1 0 0 0 1 1 1 1]
[0 1 0 0 1 a d g]
[0 0 1 0 1 b e h]
[0 0 0 1 1 c f i].
```

Because `d` and `e` occur in one column, every parent bracket is affine in
`(x,y)`.  Orienting its sign toward the normalized parent-187 base gives
thirty nonconstant halfspaces.  The closure of their common open region is
bounded and has six vertices; the remaining inequalities are redundant.  The
central `e`-line theorem is the chord `x=0` between the `4578` and `2567`
boundary edges.

The exact residual degree census is

| degree in `x` | degree in `y` | total degree | terms | factors |
|---:|---:|---:|---:|---:|
| 0 | 0 | 0 | 1 | 1,990 |
| 0 | 1 | 1 | 2 | 2,610 |
| 1 | 0 | 1 | 2 | 2,610 |
| 1 | 1 | 1 | 3 | 7,185 |
| 1 | 1 | 2 | 4 | 4,170 |
| 1 | 2 | 2 | 5 | 3,570 |
| 2 | 1 | 2 | 5 | 3,570 |
| 2 | 2 | 2 | 6 | 1,035 |

The nonconstant factors split by canonical incidence type as

```text
36:   705    38:   270    48:   315
49: 8,700    50: 9,840    51: 4,920.
```

## 2. Link-constancy lemma

Let `S={s_0,s_1,s_2,s_3}` be one labeled four-row occurrence of a
primitive residual factor `q_f`.  At a generic point of `q_f=0`, the four
derived rows form a signed circuit and exchange one antipodal pair of topes.
Choose a three-row basis `B subset S` and an external row `j_*`.

> **Link-constancy lemma.**  Let `A` be a connected open arc of `q_f=0`
> inside the uniform parent cell.  Suppose:
>
> 1. `B` has rank three;
> 2. all four determinants `det(S-s_i,j_*)` are fixed nonzero parent units;
> 3. none of the residual factors in the remaining determinants `det(B,j)`,
>    for `j` outside `S`, vanishes on `A`.
>
> Then the signed circuit, the signs outside `S` of its collapsing tope, and
> the unordered antipodal exchange are constant on `A`.  If the exchange is
> active at one point of `A`, it is active throughout `A`.

The second condition both witnesses the rank of `B` and fixes every circuit
coefficient sign.  The remaining row signs are the signs of the link
determinants `det(B,j)`, so the third condition fixes them.  The exchanged
tope on one side and its replacement on the other differ precisely on `S`;
their antipodes supply the second pair.  No combinatorial datum defining the
local mutation can change before one of the listed determinants vanishes.

For the ten central-line seeds, suitable choices make all four circuit
coefficients parent units and supply many fixed-unit rank witnesses.  Hence
rank loss and circuit-sign changes are absent throughout the uniform cell;
only the displayed residual link factors can change the exchanged vector.

| seed factor | type | occurrence rows | link basis | unit row | global/disk links |
|---:|---:|---|---|---:|---:|
| 8421 | 51 | 21,31,40,49 | 31,40,49 | 32 | 17 / 16 |
| 10115 | 51 | 1,31,40,49 | 31,40,49 | 14 | 17 / 16 |
| 11045 | 50 | 1,28,33,49 | 1,28,49 | 19 | 16 / 16 |
| 13869 | 50 | 1,25,31,49 | 1,25,49 | 14 | 16 / 16 |
| 16242 | 50 | 9,16,21,51 | 9,16,51 | 5 | 16 / 15 |
| 19971 | 50 | 1,16,31,40 | 16,31,40 | 10 | 16 / 16 |
| 22118 | 49 | 6,10,26,33 | 6,26,33 | 4 | 17 / 17 |
| 23559 | 50 | 15,16,21,51 | 15,16,51 | 11 | 16 / 15 |
| 23604 | 49 | 2,28,30,49 | 2,30,49 | 5 | 17 / 17 |
| 23979 | 50 | 11,26,33,37 | 26,33,37 | 21 | 16 / 16 |

The constant restricted memberships are `8421 -> 1994`, `10115 -> 1994`,
`16242 -> 13965`, and `23559 -> 14611`.  Exact raw determinant
factorization, followed by exhaustive parent-unit stripping, certifies every
unit and residual classification in the table.  Each seed curve is also
nonsingular and shares no component with any of its listed link factors.

## 3. Query-state consequence

For fixed tracked signatures, retain only complete topes which agree with a
tracked signature away from at least one source star.  This **source-bucket
state** determines badness, every minimal separator, and every moving-witness
escape mask.  A wall germ whose exchanged topes miss all tracked buckets is
therefore transparent to the diagonal-two query.

Along one seed wall, the link-constancy lemma makes the exchanged topes
constant between link cuts.  Bucket relevance can consequently be tested
once per link arc, without constructing the arrangement of every unrelated
conic.  This is the intended relevance filter for the transition disk.

The caveat matters: link constancy fixes the seed exchange, not the entire
background separator state.  A full state theorem must either stop at every
other residual intersection or recursively include every query-active wall.
Unseeded wall components and components entering only through the parent
boundary also require their own activity seed.

## 4. Sharper proof strategy

Only factors `10115` and `16242` among the ten line seeds create or destroy a
tracked bad endpoint.  The other eight alter an already-bad source-bucket
state.  This suggests a shorter structural target than global overlap
monotonicity, but badness births alone are not enough:

1. exclude every generic zero-core-entry wall germ, covering both badness
   births and still-bad budget-tight transitions which could kill the last
   common direction;
2. at codimension two and lower, certify one common direction robust across
   all incident bad cell germs, rather than gluing unrelated cellwise
   directions;
3. show that every zero-core component in the planar cell complex reaches
   the parent-hexagon boundary.

A compact simultaneous-bad component with no common shear would otherwise
need an interior birth boundary or would have to live entirely on a lower
residual stratum.  The transition disk can test both alternatives exactly.

## 5. Reproduction and boundary

Run the exact geometry and link census with

```console
python ai/omreal/verify_diag2_extremal_transition_disk_geometry.py
```

The verifier pins all six rational vertices, boundedness and the central
chord, the complete conic degree and type histograms, the unique occurrences
of the ten seed factors, exact parent-unit rank/circuit witnesses, the global
`164/142` link census, and the effective disk `160/139` frontier.  Its
semantic digest is

```text
8c9a13c315c67da89f45b152b049cef05f71cb00502f592e24bddb69db27f869
```

What remains is to isolate the link cuts and all query-active wall arcs,
attach exact chamber germs, and build the reduced planar cell complex.  No
claim in this note covers that unfinished step.
