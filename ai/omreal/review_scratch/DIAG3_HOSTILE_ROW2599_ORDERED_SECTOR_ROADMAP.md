# Row 2599: exact ordered-sector residence and the H0 outer cap

## Scope and result

This is an exact local audit of the five valid ordered singleton sectors in
the row-2599 joined flow triangle.  Compactify the positive parameters by

\[
             u=\frac{x}{1-x},\qquad v=\frac{y}{1-y}.
\]

After multiplying a signed parent bracket by the positive denominator
`(1-x)(1-y)`, each of the 70 walls is bilinear in `(x,y)`.  The no-argument
verifier reconstructs all 70 walls from the pinned chart-zero integer matrix
and determines the whole connected parent-residence component containing the
origin.

For H1 in its valid forward order and for both H2 orders, that component is
exactly the product of the two individual first-wall intervals.  The bounded
first-wall square is therefore the full compactified relative sector.

For both H0 orders it is not.  In forward coordinates `d01,d20`, put

```text
U01 = 1221971981 / 1769366234
U20 =  425791163 / 1286992887
W   = 2076877735 / 5073331504
U*  = 2563735753704858965 / 18122074711096100794.
```

The exact origin component is

\[
 0\le u\le U_{01},\qquad
 0\le v\le \min\{f_{1256}(u),W\},
\]

where `[1256]=0` is the increasing graph `v=f_1256(u)` until it meets
`[1278]=0`, the horizontal wall `v=W`, at `u=U*`.  From there `[1278]`
continues to the vertical wall `[1234]=0` at `u=U01`.  The reverse H0 order
is exactly this description with the two coordinates exchanged.

The verifier proves exhaustiveness, rather than sampling this picture:

- `[1234]` and `[1278]` are global coordinate barriers at the two displayed
  values;
- the coefficient of `v` in signed `[1256]` is strictly negative throughout
  `0<=u<=U01`, its graph is strictly increasing, and its unique intersection
  with `[1278]` is the displayed rational `U*`;
- every other signed parent bracket is strictly positive on the entire larger
  bounding rectangle.  Since each compactified bracket is bilinear, its four
  exact vertex values certify this last assertion exhaustively.

There is no parameter-infinity face in any of these five components: every
component is bounded away from `x=1` and `y=1` by the certified parent walls.

## Exact relative-homology obstruction

Let `Q` be the H0 first-wall square
`[0,U01] x [0,U20]`.  Its relative parent frontier is the right `[1234]`
edge together with the isolated upper-left `[1256]` point.  Thus

\[
              H_1(Q,Q\cap\partial_{parent})\cong\mathbb Z.
\]

The full residence component adds one bounded outer cap.  Its new parent
frontier is the connected arc `[1256]`--`[1278]`--`[1234]`, and the cap's
only nonrelative boundary is the old top interface of `Q`.  It kills the
primitive relative H1 class, giving

\[
 H_*(C,C\cap\partial_{parent})=0.
\]

The exact relative cellular Betti vectors `(H0,H1,H2)` replay as

```text
rectangle sector:       (0,0,0)
H0 first-wall square:   (0,1,0)
H0 square + outer cap:  (0,0,0).
```

Consequently the H0 first-wall-square inclusion is **not** a relative
homology equivalence.  This is an exact attachment witness, not a failure of
the full ordered-sector theorem.  Any comparison three-chain built from the
bounded tapered cube must include the H0 cap (or a chain-equivalent
replacement); otherwise it carries an extra primitive face.

## Witness naturality checkpoint

The old pointwise circuits for H0 and H1 contain row `123`, which is not safe
for their ordered-root transport.  Exact safe-support search gives the
minimal positive replacements

```text
H0: 134/456/137/238/148   (both orders)
H1: 134/345/257/167/128   (forward order)
H2: 123/136/256/247/348   (both orders).
```

All rows in these supports are safe for the corresponding full ordered
third-compound transport.  Direct exact cofactor substitution on the five
bounded tapered cubes gives strict tensor-Bernstein coefficients.  This
repairs the prior pointwise-versus-transport support mismatch on those cubes.

The verifier now also subdivides the H0 outer cap into two exact patches and
sweeps both to the common proper ray.  The upper patch is a rectangle.  The
lower patch uses the exact rational graph of `[1256]=0`; clearing its positive
linear denominator is implemented as a positive rescaling of labelled column
1.  Tensor-Bernstein replay proves all 70 parent signs and the strict
transport-safe H0 circuit on both three-parameter patches.  Their relative
wall censuses are

```text
lower: [1256], [1278], [2467]
upper: [1234], [1256], [1278], [2467].
```

Thus the H0 outer cap is no longer an unverified geometric gap.  What remains
before this becomes a `d3` certificate is a mixed **base-space** filler.
The checker now proves the internal H0 cap interfaces as well: on the lower
patch, clearing the graph denominator is a positive rescaling of labelled
column 1.  Exactly three rows of the H0 support contain label 1, and the raw
cofactor vectors on both sides satisfy the corresponding `D^3/D_i` gauge
identity.  Hence the normalized Gordan sections agree on both the
lower/first-square and lower/upper interfaces.

There is also no remaining mismatch on the six external witness seams.  On
each pair face, the two adjacent singleton cubes restrict to the literal same
polynomial matrix.  Both adjacent block circuits are strict there, their
cofactor sections agree exactly with the singleton endpoint sections, and at
the common endpoint all root amplitudes vanish.  The three endpoint bases are
identical, their only parent wall is `[2467]`, and the surviving joined pair
sections form the literal boundary of the block-mass triangle.  Convex Gordan
interpolation therefore supplies a face-natural witness **cospan on `K(F)`**.
This does not construct a three-chain filling `K(F)`: convexity acts only in
the witness fiber over one fixed base, whereas the six sides of `K(F)` have
different moving bases.

## Signed cone boundary and the exact remaining cell

The signed boundary table is now exact.  Orient the six parent-frontier edges
as

```text
p01 : w0a -> w1a       h0 : w0a -> w0c
p12 : w1b -> w2b       h1 : w1a -> w1b
p20 : w2c -> w0c       h2 : w2b -> w2c.
```

The absolute parent-frontier terms of the six noncentral two-cells are

```text
d S01 = (relative terms) - p01
d S12 = (relative terms) - p12
d S20 = (relative terms) - p20
d H0  = (relative terms) + h0
d H1  = (relative terms) - h1
d H2  = (relative terms) - h2.
```

Applying these to the primitive relation
`-T+S01+S12+S20+H0+H1+H2` leaves the primitive closed hexagon

\[
 F=-p_{01}-p_{12}-p_{20}+h_0-h_1-h_2.                 \tag{1}
\]

Its six-edge boundary matrix has rank five and kernel generated integrally by
the coefficient vector `(-1,-1,-1,+1,-1,-1)`.  For the raw tapered cone
operator `K`, oriented by

\[
             \partial K(C)=C-K(\partial C),
\]

the signed sum of the seven certified raw sweeps has boundary

\[
 -T+S_{01}+S_{12}+S_{20}+H_0+H_1+H_2-K(F).           \tag{2}
\]

All nine non-frontier lateral faces cancel exactly.  This is checked by the
integer boundary matrices, not inferred from a drawing.

Equation (2) also isolates why the raw tapered sweeps are not yet a relative
`d3` cell.  The verifier evaluates an exact rational midpoint in every one of
`K(p01),K(p12),K(p20),K(h0),K(h1),K(h2)` and finds all 70 parent brackets
nonzero.  These six surfaces leave the parent boundary for intermediate cone
parameter and therefore cannot be silently discarded as relative infinity.

The smallest missing local geometric map is now one proper mixed-block
three-chain `J` with the exact signed boundary

\[
                 \partial J=K(F)
 =-K(p_{01})-K(p_{12})-K(p_{20})
   +K(h_0)-K(h_1)-K(h_2).                            \tag{3}
\]

No other local chain-group ambiguity remains: without `J` the swept-frontier
middle kernel has rank one; adding the primitive column (3) changes
`rank(d2)+rank(d3)` from `5+0` to `5+1=6` and kills it integrally.  What is
not yet certified is a semialgebraic bad-locus realization of `J`, including
its zero-block/zero-witness faces and the six face identifications in (3).
Consequently (3) is a machine-checked acceptance boundary, not a constructed
cell.

## Exact no-go for the scalar radial cone

The most tempting way to turn the common-apex cospan into `J` is to multiply
all root amplitudes by one extra scalar `h(s,r)`.  This architecture is
impossible, independently of witness choices.  On the `p01` source edge, the
verifier reconstructs all 70 brackets under radial scale `h` and proves that
the only parent wall is

\[
       \operatorname{sgn}[1234]=2443943962(1-h).
\]

Every other signed bracket is strict for `0<=h<=1`.  Therefore keeping the
new `s=0` face relative forces `h(0,r)=1`.  Collapsing the root amplitudes to
the common-ray block-mass triangle forces `h(s,1)=0` for every `s>0`.  The two
conditions give incompatible limits at the corner `(s,r)=(0,1)`, so no
continuous, hence no semialgebraic, scalar radial filler exists.  If one
ignores that corner, the omitted corner face is precisely another copy of the
original flow disk; the construction is circular.

Thus the smallest remaining local object is sharper than “compatible
witnesses”: it is a nonradial, parent-face-natural mixed base map with exact
boundary (3).  Equivalently, one may supply a bad-locus parent-boundary cap
for the source comparison hexagon and a compatible proper extension to the
common `[2467]` endpoint.  At this stage of the audit no such cap or nonradial
map was encoded; the later tangent/prism sections record the exact repair.

## Exact parent-wall collar attempt

A nonradial wall-preserving construction succeeds on two of the three pair
edges.  Keep the first-wall root amplitude fixed, move labelled column 7 in
the common direction until `[2467]`, and then remove the root amplitude while
staying on `[2467]`.  Exact Bernstein replay proves the following two-stage
relative collars, including both adjacent strict block circuits:

| edge | source wall | active blocks | common endpoint wall |
|---|---|---|---|
| `p12` | `[1358]` | `1,2` | `[1358] intersect [2467]` |
| `p20` | `[1256]` | `2,0` | `[1256] intersect [2467]` |

Their second stages end at the same zero-root `[2467]` base already used by
the common-apex mass triangle.

The analogous `p01` collar is rigorously obstructed along this natural
two-parameter plane.  Write `a` for the common-column parameter while the
`d01` root remains at its `[1234]` first-wall value.  Three exact critical
parameters occur in the strict order

```text
block-0 witness wall:
  83503134767238851186305349765512866 /
  43552580189648394406194000441042241

first new parent corner [1367]:
  3797676243957714 / 1934663274435289

fixed-root intersection with [2467]:
  150232380670800142796191902 /
  36368055566722865061946027.
```

At the exact midpoint between the first two values, positive projective
column scalings make the parent matrix integral, and

```text
(10000,177,-7015,368)
```

has the prescribed strict sign against all 56 derived rows of block 0.  The
smallest signed dot product is the pinned positive integer `5966575`.
Therefore block 0 is **good** there by strict Gordan duality; changing its
circuit support cannot repair the collar.

The parent geometry is not itself blocked.  The `[1234]` arc reaches the
`[1367]` corner, and along `[1367]` the root parameter can be changed to

```text
74520518780897 / 5145156267709928
```

to reach `[2467]`.  On that second segment block 0 is bad again, certified by
the strict two-row circuit `136/167`, and block 1 remains strict.  The fatal
feature is the intervening open good point before the parent corner.

Consequently the direct three-edge parent-wall cospan is false, even though
two of its edges are complete.  This does not exclude every higher-dimensional
boundary cap.  It pins the exact additional local datum needed next: before
the block-0 witness wall on `[1234]`, a new parent-tangent generator must leave
this two-parameter plane while retaining a block-0 Gordan face and reach a
different relative corner/cospan.  No such generator was present in that
predecessor checkpoint; the next section supplies it, while local `J` remains
open.

## Nonradial `p01` tangent repair

The missing generator above is now constructed in
[`DIAG3_ROW2599_P01_TANGENT_COLLAR.md`](../DIAG3_ROW2599_P01_TANGENT_COLLAR.md)
and replayed by
[`verify_diag3_row2599_p01_tangent_collar.py`](../verify_diag3_row2599_p01_tangent_collar.py).
At the exact block-0 witness wall it changes the first coordinate of labelled
column 6, reaches `[1367]` before leaving the bad locus, follows `[1367]` to
`[2467]`, and then follows a positive-denominator rational `[2467]` graph to
the common apex.  Exact Bernstein and cofactor replay certifies all parent
signs, both incident bad blocks, the path seams, and the positive projective
column gauges.  Thus all three pair edges now have relative wall collars.

This repairs the pair-edge collar gate.  A subsequent five-patch construction
in [`DIAG3_ROW2599_P01_COMPARISON_PRISM.md`](../DIAG3_ROW2599_P01_COMPARISON_PRISM.md)
joins the nonrelative swept surface `K(p01)` to this path.  Its ordinary
boundary is exactly `+K(p01)-Q(p01,block0)+Q(p01,block1)`, independently
replayed with dense bivariate arithmetic.  The simpler `p12` and `p20`
collars yield two more independently replayed pair prisms.  The certified
comparison-incidence count is now `3/6`; the six pair-edge singleton disks
are distinct.  A four-patch exact `H2` prism subsequently joins the two
block-2 disks literally, advancing the count to `4/6`.  The `H0` and `H1`
prisms and local `J` remain open.

## Replay

```bash
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/review_scratch/DIAG3_HOSTILE_VERIFY_ROW2599_ORDERED_SECTOR_ROADMAP.py
```

The semantic digest is

```text
5941481177b36052e3e59bf08fa44cddadaa415fe761e091a2e8d8b2299ffc1c
```

The result is local to the row-2599 canary.  It neither supplies a global
coverage theorem nor changes the diagonal-three ledger.
