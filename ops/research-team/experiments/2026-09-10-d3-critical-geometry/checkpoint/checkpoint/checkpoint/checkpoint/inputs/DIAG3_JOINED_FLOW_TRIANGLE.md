# Diagonal three: the joined flow-triangle carrier

## Outcome

There is a cover-correct local replacement for a common three-signature
escape direction.  Let three bad blocks be indexed by `0,1,2`.  Choose one
proper elementary-root ray `d_ij` common to each bad pair.  At block `i`,
join its two incident roots in the singleton ordered-root graph: every edge
of this path is an ordered two-root carrier which preserves a positive
`i`-witness.  Then the block-mass triangle, three pair strips, and the three
singleton sector paths form an integral relative carrier with

\[
                    H_0=H_1=0,\qquad H_2\cong\mathbb Z.          \tag{1}
\]

Thus no root common to all three blocks is needed to make the relative
one-skeleton exact.  The construction is the joined block-Gordan analogue
of filling a Cech triangle: pair rays live on the corresponding two-block
faces, while the homotopy between the two rays incident to `i` lives on the
singleton `i`-face.  Zero block masses are part of the construction, not
deleted.  The primitive `H_2` class in (1) is the exact remaining
third-diagonal obstruction: a proof still needs a genuine relative
three-cell whose boundary is that class.

At exact row-2599 chart zero, the valid bad signatures

```text
14988895318912
3405195891438080
40418075143643136
```

have no common elementary root.  Nevertheless the pair roots

```text
d01 = (2 -> 8, -)
d12 = (1 -> 2, -)
d20 = (1 -> 3, +)
```

give a direct-edge flow triangle.  The exact verifier is
[`verify_diag3_joined_flow_triangle.py`](verify_diag3_joined_flow_triangle.py).

This is a local two-skeleton theorem, not the third diagonal.  A global proof
still has to produce the missing three-cell, construct all choices on a
finite coverage-certified subdivision, and specialize their positive
witness faces at every residual wall and parent-boundary face.  Pointwise
root graphs, even exact ones, do not supply that data.

The exact joined face types explain why the three-cell cannot be omitted.
If `r` blocks have positive mass and their internal coordinate-face
dimensions are `k_1,...,k_r`, then the joined face dimension and block
support bounds are

\[
 k=(r-1)+\sum_i k_i,
 \qquad |U_i|\leq5+k_i.                                       \tag{1a}
\]

Through the relative three-skeleton this gives:

| joined dimension | active-block face types | maximum support sizes |
|---:|---|---|
| `0` | `(0)` | `5` |
| `1` | `(1)`; `(0,0)` | `6`; `5+5` |
| `2` | `(2)`; `(1,0)`; `(0,0,0)` | `7`; `6+5`; `5+5+5` |
| `3` | `(3)`; `(2,0)`; `(1,1)`; `(1,0,0)` | `8`; `7+5`; `6+6`; `6+5+5` |

The single-block theorem handles the first type in joined dimensions zero,
one, and two.  Pair circuit corners `(0,0)` and triple circuit corners
`(0,0,0)` are the cover-correct pair and triple terms.  Joined dimension
three is absent from the `E_1` contribution in total degree two, but its
boundary map is exactly what must kill relations among the dimension-two
cells.

## 1. Root-safe rays and sectors

For an oriented elementary root `d=(e -> f,a)`, put

\[
                 g_d(u)=1+auN_{fe},\qquad u\geq0.                \tag{2}
\]

The moving-witness identity transports a signed Gordan form by
`Lambda^3(g_d(u)^(-1))`.  If all generated coefficients stay in the chosen
signed nonnegative orthant, the corresponding block remains bad until the
first parent bracket vanishes or the moving columns have a projective
dependency at parameter infinity.  This makes (2) a proper relative ray.

For two distinct root lines `d,d'`, use the ordered cell

\[
             g_{d,d'}(u,v)=(1+uN_d)(1+vN_{d'}),
             \qquad u,v\geq0.                                  \tag{3}
\]

The inverse exterior transport includes the `uv` term.  An edge in the
singleton ordered-root graph means that one order in (3) has a nonempty
positive Gordan face supported on rows whose full transport is orthant-safe.
That face transports over the whole positive parameter quadrant.

Every parent bracket along (3) has degree at most one in each parameter.
Consequently, at fixed `u` its prescribed-sign locus is an interval in `v`,
and conversely.  A connected component of the parent-sign residence domain
therefore has interval fibers over an interval.  A semialgebraic continuous
section and straight-line contraction in the interval fibers show that the
component is contractible.  Its non-axis frontier consists of parent
bracket walls or parameter-infinity degenerations.  After adjoining the
parent boundary it is a relative open two-cell.  This is the sector used
below.

The parameter-infinity assertion is literal, not an assumed properness of
an arbitrary flow.  If `(u,v)` leaves every compact subset while no parent
bracket tends to zero at a finite parameter, inspect the two directed root
edges.  For disjoint sources, a moving source approaches its target ray.  If
the roots have one source, that source approaches the projective span of the
two target rays.  In the chain and reciprocal cases, the source, intermediate,
and final target approach a common projective two-plane (and in the
reciprocal case two rays become parallel).  In every case some four labeled
limit columns have rank at most three.  Thus every unbounded parameter
sequence approaches the nonuniform parent boundary.  Together with the
finite bracket-wall frontier, this proves relative properness of the ordered
sector parameterization.

Different ray and sector witnesses need not be the same circuit vertex.
Their root-safe normalized faces are convex coordinate restrictions of the
Gordan polytope.  Convex interpolation supplies the required seams.  It may
enlarge support, which is why the theorem belongs to the joined resolution
and is not a contraction of a frozen circuit cover.

## 2. The direct-edge relative complex

Work relative to all parent-boundary and parameter-infinity faces.  The
zero-cells are the three singleton block vertices `v0,v1,v2`.  Orient the
central mass edges cyclically as

```text
e01 : v0 -> v1,   e12 : v1 -> v2,   e20 : v2 -> v0.
```

For each pair root retain a copy at either endpoint.  In the order

```text
e01,e12,e20,r0a,r1a,r1b,r2b,r2c,r0c
```

the relative `C1 -> C0` matrix has rows

\[
 \partial_1=
 \begin{pmatrix}
 -1& 0& 1&-1& 0& 0& 0& 0&-1\\
  1&-1& 0& 0&-1&-1& 0& 0& 0\\
  0& 1&-1& 0& 0& 0&-1&-1& 0
 \end{pmatrix}.                                                \tag{4}
\]

There are seven relative two-cells: the central block-mass triangle `T`,
three pair strips, and three singleton sectors.  Their boundaries are

\[
\begin{aligned}
 \partial T   &=e_{01}+e_{12}+e_{20},\\
 \partial S_{01}&=e_{01}-r_{0a}+r_{1a},\\
 \partial S_{12}&=e_{12}-r_{1b}+r_{2b},\\
 \partial S_{20}&=e_{20}-r_{2c}+r_{0c},\\
 \partial H_0&=r_{0a}-r_{0c},\\
 \partial H_1&=-r_{1a}+r_{1b},\\
 \partial H_2&=-r_{2b}+r_{2c}.
                                                               \tag{5}
\end{aligned}
\]

Equations (4)--(5) give `partial_1 partial_2=0`.  Exact integral reduction
gives

\[
       \operatorname{rank}\partial_1=3,
       \qquad\operatorname{rank}\partial_2=6,                  \tag{6}
\]

and the six nonzero Smith invariants of `partial_2` are units.  Its only
relation is

\[
        -T+S_{01}+S_{12}+S_{20}+H_0+H_1+H_2.                   \tag{7}
\]

Thus (1) follows integrally.  Geometrically, (7) is the fundamental relative
class of the open flow disk.  For the joined relative three-skeleton the
required criterion is

\[
       \operatorname{rank}\partial_2+
       \operatorname{rank}\partial_3=\operatorname{rank}C_2.    \tag{7a}
\]

Here the left side is `6+0<7`.  Consequently the flow disk identifies the
unique column still required from `partial_3`; it does not itself close the
triple total-degree-two term.

## 3. Paths in the singleton graphs

The two roots incident to a singleton block need not themselves span one
ordered sector.  Choose a path of length `L_i` between them in its
singleton ordered-root graph and add one ray for every path vertex and one
sector for every path edge.  Put `L=L_0+L_1+L_2`.  The relative ranks are

| group | rank |
|---|---:|
| `C0` | `3` |
| `C1` | `6+L` |
| `C2` | `4+L` |

The singleton sector columns first eliminate all consecutive ray
differences.  The three pair-strip columns then eliminate the remaining
mass/root differences.  These are unit pivots, so

\[
 \operatorname{rank}\partial_2=3+L
       =\dim\ker\partial_1,                                   \tag{8}
\]

with only unit Smith invariants.  There is again one top relation.  Hence
connected singleton ordered-root graphs suffice for integral exactness
through `C1`; no direct edge is required.  They do not supply the missing
`C3 -> C2` boundary.

## 4. Exact no-common-root canary

The verifier reconstructs all `26,112` complete derived-arrangement topes
at exact row-2599 chart zero and applies strict Gordan duality to the safe
row sets.  For the three signatures above it obtains elementary escape-set
sizes

\[
                              56,\quad56,\quad60,                \tag{9}
\]

but their threefold intersection is empty.  Each displayed `d_ij` belongs
to the two required escape sets.  At every singleton block, the two incident
roots admit an ordered two-root carrier; block 1 requires the displayed
order, which also checks that order is not being silently discarded.

The same script checks that all three signatures satisfy every exact
rank-four Grassmann--Pluecker extension axiom, are absent from the complete
tope table at this chart, and verifies (4)--(7) over the integers.

## 5. A nerve cocycle obstructs every singleton-root filling

The missing three-cell cannot be obtained merely by allowing longer ordered
root words while keeping one fixed bad block on each parameter simplex.
This has a coefficient-independent Cech obstruction.

Let `E_i` be the elementary roots which transport some positive witness for
block `i`, and let `K_i` be **any** root-carrier complex whose every simplex
uses one fixed block `i`.  An actual ordered `q`-root carrier gives such a
simplex because each of its coordinate-root faces transports the same
block.  Suppose

\[
 E_0\cap E_1\cap E_2=\varnothing,                              \tag{10}
\]

and choose `d01,d12,d20` as above.  On the vertices of `K_1`, define

\[
 \phi(v)=
 \begin{cases}
 0,&v\in E_0,\\
 1,&v\in E_2,\\
 0,&v\notin E_0\cup E_2.
 \end{cases}                                                   \tag{11}
\]

The first two cases cannot conflict by (10).  Define an integral one-cochain
on the union of the singleton complexes as follows.  It is zero on every
edge belonging to `K_0` or `K_2`, and it is
`phi(target)-phi(source)` on an edge belonging only to `K_1`.  This is
well-defined on shared edges.  Indeed, the endpoints of an edge shared by
`K_0,K_1` both lie in `E_0 intersection E_1`, where `phi=0`; the endpoints
of one shared by `K_1,K_2` both have `phi=1`.

The cochain is closed on every singleton simplex: it is zero on `K_0,K_2`
and is the coboundary of `phi` on `K_1`.  Yet on the oriented root-choice
loop

\[
          d_{01}\longrightarrow d_{12}\longrightarrow d_{20}
                   \longrightarrow d_{01}                       \tag{12}
\]

its value is `1`.  Thus (12) does not bound over `Z`, `Q`, or any coefficient
ring in which `1` is nonzero.  Coning root parameters identifies (12) with
the flow-disk class (7).  Pair mapping strips only identify shared
singleton faces and map to zero under this cocycle, so they do not change
the conclusion.

> **Singleton-root no-go.**  When the triple elementary-root intersection is
> empty, the primitive flow-disk class cannot be the boundary of any chain
> assembled from ordered higher-root cells which transport one fixed block
> at a time, even if every possible singleton root simplex is adjoined.

The chart-zero canary satisfies (10).  Therefore its missing `partial_3`
column must be a genuinely **mixed-block** carrier: its interior must use
block-mass transfer and/or witness exchange in a way which is not subordinate
to one fixed singleton root-safe complex.  Searching larger singleton root
cliques cannot close this example.

## 6. The block-mass filtration forces triple noncompactness

The flow-disk class cannot be removed by a mixed-block cancellation which
avoids the topology of the triple intersection.  This follows formally from
the cover-correct block-mass filtration.

For three signatures its compact-support spectral sequence is

\[
 E_1^{p,q}=\bigoplus_{|T|=p+1}H_c^q(I_T;R)
       \Longrightarrow H_c^{p+q}(B_0\cup B_1\cup B_2;R),       \tag{13}
\]

where `I_T` is the corresponding bad-locus intersection.  The only possible
incoming differentials to

\[
                    E_1^{2,0}=H_c^0(B_0\cap B_1\cap B_2;R)      \tag{14}
\]

are

\[
 d_1:E_1^{1,0}\longrightarrow E_1^{2,0},
 \qquad
 d_2:E_2^{0,1}\longrightarrow E_2^{2,0}.                       \tag{15}
\]

The second-diagonal theorem gives
`H_c^0(B_i intersection B_j;R)=0`, so the first source is zero.  The
single-bad two-skeleton theorem gives `H_c^1(B_i;R)=0`, so the second source
is zero.  There is no outgoing differential from column two.  Therefore

\[
 E_\infty^{2,0}=H_c^0(B_0\cap B_1\cap B_2;R).                  \tag{16}
\]

In particular, third-diagonal vanishing **requires** every triple-bad
component to be noncompact.  Any genuine `partial_3` filler for (7), when
compared with the block-mass filtration, must encode such a proper
triple-bad escape.  Convex mass transfer can organize witnesses and
specializations, but it cannot bypass this term.

The remaining total-degree-two pair contribution is
the kernel of the restriction differential from pair `H_c^1` to triple
`H_c^1`; termwise pair `H_c^1` vanishing is sufficient but stronger than
necessary.  This is the part for which joined ordered-root carriers can
still provide a genuine cancellation.

Consequently the two existing lower-vanishing theorems sharpen the exact
third-diagonal target to

\[
\begin{split}
 H_c^2(B_0\cup B_1\cup B_2;R)=0
 \quad\Longleftrightarrow\quad &
 H_c^0(B_0\cap B_1\cap B_2;R)=0,\\
 &\ker\!\left[
   \bigoplus_{i<j}H_c^1(B_i\cap B_j;R)
   \longrightarrow H_c^1(B_0\cap B_1\cap B_2;R)
 \right]=0.
                                                               \tag{17}
\end{split}
\]

The compact-support long exact sequence for the closed inclusion of the
triple intersection into one pair shows that
`H_c^1((B_i intersection B_j) minus B_k;R)=0` makes that **individual**
restriction map injective.  This is a useful exclusive-pair target: an
ordered-root carrier there may stop when the third block becomes bad,
because that face is a valid relative end.  It is not sufficient for the
second line of (17), however.  Images from different pair groups can still
cancel under the alternating direct-sum map.  The joined flow-triangle
incidence, or an equivalent image-independence theorem, must also exclude
those mixed cancellations.

## 7. What is still missing globally

The local theorem identifies the right cells, but the following are not
formal consequences of convex witness fibers.

1. Every pair-bad cell in a finite subdivision must receive a nonempty
   common-root set, and the singleton ordered-root graphs used for changes
   of choice must remain connected on the whole cell.
2. At a residual wall, a safe witness face may specialize to a zero-weight
   face and disappear on the other side.  The flow triangle must use the
   specialization cospan and an enlarged circuit-elimination face; a direct
   side-to-side continuation is false.
3. The choices must be locally finite and proper after all parent-boundary
   faces are added.  In particular, graph-closure cells must record every
   source-boundary face of (3).
4. A genuine mixed-block relative three-cell must have boundary (7), and
   globally one must verify
   `rank partial_2 + rank partial_3 = rank C2`.  Local flow disks do not
   supply that `partial_3` column or rule out monodromy and compact
   split--remerge cycles.

The exact chart proves that the lack of a triple-common root is not itself
an obstruction.  It does not replace these coverage and specialization
requirements.

## 8. Replay

```console
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/verify_diag3_joined_flow_triangle.py
```
