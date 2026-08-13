# Diagonal three: an exact receiver/end table canary

## Outcome

The smallest existing two-dimensional chamber atlas can now populate one
exact local receiver/frontier canary, and its four primitive wall rays can
separately be continued to labeled relative parent-infinity endpoints.

Start with the complete transverse node in
`data/DIAG9_GRAPH_row2599_node_roadmap.npz`.  It has four open chambers, four
open wall rays, one node, and no other residual or parent wall in its closed
square.  The checker
`verify_diag3_pair_receiver_end_canary.py` does four new things.

1. It decorates all eight oriented wall germs for one exact three-signature
   family and finds an exact positive receiver circuit on every loss germ.
2. It verifies the exact three-block all-die canary on both loss rays of
   branch zero.
3. It continues all four linear factor rays beyond the artificial square
   boundary to the first exact parent-bracket wall.  Thus the square boundary
   remains only `scope-infinity`; the continued endpoints are the actual
   relative-infinity labels.
4. It constructs the cellular frontier blocks `b_ij`, assembles the matrices
   `N,M` from (22)--(23) of `DIAG3_PAIR_DIFFERENTIAL_ENDS.md`, and proves a
   unit integral contraction at the middle group.

This is a theorem about one exact local atlas plus its four factor-ray
continuations.  It does not prove balanced-end injectivity globally and does
not promote the third diagonal.

The fixed-parameter-orientation theorem in
`DIAG3_PAIR_FACTOR_ROOT_SWITCH.md` also gives a common root of either chosen
parameter sign at every generic same-factor support pair.  This removes a
pointwise shear-parameter-sign ambiguity in the same-factor retargeting
branch; it does not apply to an unrelated receiver witness.  Numeric source
descent is not relabeling invariant, and the theorem supplies neither a
continuous root selection nor the receiver/end choice used below.

## 1. Exact receiver table

Use the labeled blocks

```text
block 0 =   448607715549184   feasible mask 0011 = q0>0
block 1 =    17527223614444   feasible mask 1001 = q1>0
block 2 =     14988895318912  feasible mask 0000 on this disk
```

The third signing is checked directly against the parent GP relations; its
zero local mask is not an invented signing.  Orient each wall in the
direction in which a block dies.  Exact Gordan circuits give:

| wall | chamber germ | dying block | receiver block | exact receiver support |
|:---:|:---:|:---:|:---:|:---|
| `w0=(0,+)` | `c3 -> c0` | 0 | 2 | `3/19/21/37/38` |
| `w1=(0,-)` | `c2 -> c1` | 0 | 1 | `2/28/32/43` |
| `w2=(-,0)` | `c2 -> c3` | 1 | 0 | `0/18/29/40/48` |
| `w3=(+,0)` | `c1 -> c0` | 1 | 2 | `3/19/21/37/38` |

Every reverse germ is a birth or identity germ.  Formula (3) of
`BLOCK_GORDAN_MONOCHROMATIC_MASS_TRANSFER.md` therefore gives an actual
joined-fiber transfer on all four loss rows.  No unrelated circuit in the
dying block is used.

For comparison, the exact signings

```text
448607715549184
3826331369078784
31604296963587053
```

all have feasible mask `0011`.  Across `w0` and `w1` all three blocks die,
and all three have the positive localization circuit

```text
0/18/40 = 123/356/348.
```

These two rows use the global-factor wall escape, not a nonexistent receiver.

## 2. Exact infinity labels

The square boundary lies strictly inside parent 2599 and is not parent
infinity.  Each primitive node branch is affine, however, so its two rays can
be continued exactly while holding that factor equal to zero.  Along such a
line every parent bracket is affine.  The first zeros are:

| wall ray | factor branch | parameter direction | first parent bracket |
|:---:|:---:|:---:|:---:|
| `w0` | 0 | negative | `3578` |
| `w1` | 0 | positive | `1358` |
| `w2` | 1 | negative | `3478` |
| `w3` | 1 | positive | `1268` |

The checker pins the four exact rational endpoint parameters, not just these
labels.  No parent bracket vanishes in the corresponding open intervals.
On branch zero the common circuit `0/18/40` stays positive toward both ends:
its dependence is the fixed branch equation and its coefficient signs cannot
change before a parent-bracket factor vanishes.  Hence the two all-die rows
now have explicit relative ends `3578` and `1358`.

As an independent infinity regression, the complete parent-187 `e`-line has
`1,722` chambers and `1,721` residual crossings between its first bracket
walls:

```text
negative end 4578 at
-6557186031778323968614336 / 80367163670274882423315095

positive end 2567 at
 9701361017377585348692326 / 281522797333298743311269675.
```

This distinguishes a genuine relative parent boundary from an arbitrary
bounded-box endpoint in both source pipelines.

## 3. Actual `N/M` assembly

Relative to the outer square boundary, orient every wall ray from the node
outward.  For the receiver family above, the triple and exclusive-pair cells
are

```text
T:    v ; w1,w2 ; c2
E01:  empty
E02:  w0 ; c3
E12:  w3 ; c1.
```

The exact matrices in the bases constructed by the checker are

\[
N=
\begin{pmatrix}
-1&0\\
-1&0\\
0&-1\\
0&-1\\
1&1\\
0&1
\end{pmatrix},
\qquad
M=
\begin{pmatrix}
-1&1&0&0&0&0\\
0&0&-1&1&0&0\\
0&-1&0&-1&-1&0\\
0&0&1&0&0&1
\end{pmatrix}.                                      \tag{1}
\]

They satisfy

\[
 MN=0,qquad \operatorname{rank}N=2,qquad
 \operatorname{rank}M=4,qquad H^1=0.               \tag{2}
\]

Unit Smith reduction gives unit ranks `(2,4)` for `N` and the reduced
`bar M`.  The checker invokes the same construction as
`verify_diag3_pair_differential_ends.py` and produces the integral contraction

\[
                         h_2M+Nh_1=1_{C^1}.          \tag{3}
\]

Thus the receiver/end table has been connected to the exact algebraic target,
not merely printed as a list of local paths.

## 4. Formal support-compressed row ceiling

The factor stabilizers give the following exact numbers of **ordered**
active-support tuple orbits for one, two, and three changing labeled blocks:

| factor kind | one block | two blocks | three blocks |
|---:|---:|---:|---:|
| 36 | 4 | 54 | 1,147 |
| 38 | 2 | 10 | 83 |
| 48 | 1 | 2 | 4 |
| 49 | 1 | 1 | 1 |
| 50 | 1 | 1 | 1 |
| 51 | 1 | 1 | 1 |
| **total** | **10** | **69** | **1,237** |

On a fixed cooriented generic factor wall, a labeled block is inactive,
persistent, dying, or born.  Only dying and born blocks need a selected
occurrence of the crossed factor; a persistent receiver can use its full
convex Gordan fiber.  If exactly `k` blocks change, there are

\[
                  \binom3k2^k2^{3-k}=8\binom3k       \tag{4}
\]

status words.  Consequently the formal support-compressed candidate table has
the exact ceiling

\[
 24(10)+24(69)+8(1237)=11{,}792                     \tag{5}
\]

cooriented rows, or `23,584` directed rows when both incidence directions
are stored.  These counts are exact for the stated orbit/status-word front
end, but they are not a census of realized chamber-decorated rows.  They are
small enough for an exact table generator.

Equation (5) is not the universal state count of the proof.  It omits
component multiplicity, factor intersections, support-shrink faces, and
infinity subdivisions.  There are already `9,476` unordered distinct
factor-pair orbits available for the intersection registry.  The number of
actual connected end germs cannot be inferred from the 178 point charts and
remains unknown until a covered master subdivision is built.

## 5. Completed four-ray refinement

`DIAG3_PAIR_FOUR_RAY_REFINEMENT.md` and
`verify_diag3_pair_four_ray_refinement.py` complete the proposed
one-dimensional check.  All `26,740` factors are restricted exactly, giving
`4,592` factor-root incidences at `4,546` algebraic parameters.  Exact status
and signed-wall checks find three receiver losses, no all-die row, and no
wall-only bad vertex.

The honest compactified factor-star matrix has

```text
N: 4920 x 4917, full unit Smith rank 4917
M:    0 x 4920,
```

so it leaves a primitive free `Z^3` middle residue.  This is a precise
one-dimensional obstruction, not a failure of the two-dimensional node
canary above: ambient chamber two-cells and the seven tangential directions
were not continued along the long rays and can supply the missing rows of
`M`.

## Replay

```console
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/verify_diag3_pair_receiver_end_canary.py
```

The pinned semantic digest is

```text
7ff91b35ac7f8902f893c89011d94254458d0b3344e6d994db85dc1c1f0021a0
```
