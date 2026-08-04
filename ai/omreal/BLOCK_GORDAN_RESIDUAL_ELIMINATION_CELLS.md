# Enlarged-support elimination cells for all residual walls

## Outcome

At a generic point of any one of the 13 residual derived-wall types, every
**chosen pair of circuit births on opposite sides** has a canonical minimal
enlarged-support carrier.  In the two residual normal forms it is

\[
 \begin{array}{ccl}
 \text{ordinary:}&|P|=4,&U=P\cup\{u,v\},\quad |U|=6,\\
 \text{localization:}&|P|=3,&U=P\cup\{u,v\},\quad |U|=5.
 \end{array}                                                    \tag{1}
\]

Here `P` is the positive wall circuit, `Q_-=P union {u}` is positive on the
negative side, and `Q_+=P union {v}` is positive on the positive side.  The
two auxiliary columns have opposite transverse signs.  Positive circuit
elimination produces a circuit `R` which contains both auxiliaries, persists
on both sides of the wall, and has support at most five in the ordinary case
and at most four in the localization case.  At a simple wall the three
normalized nonnegative-kernel fibers are intervals

\[
       [Q_-,R]\ \longrightarrow\ [P,R]\ \longleftarrow\ [Q_+,R].       \tag{2}
\]

Both specialization arrows in (2) are integral cellular isomorphisms.  Their
mapping cones are acyclic over `Z`.  This is the uniform codimension-one
filling of the specialization cospan that the strict zero-face no-go leaves
open.

The theorem is conditional on an opposite-side partner in the same witness
block.  A signature can make every certified auxiliary live on the same
side, and global badness may then be continued only by a circuit unrelated to
`P`.  This result alone also does not construct common homotopies around
intersecting walls.  The later acyclic-carrier theorem in
`BLOCK_GORDAN_ALL_CODIM_COHERENCE.md` supplies all such higher homotopies once
a facewise codimension-one system exists.  Monochromatic codimension-one
stars and global matching acyclicity remain, so no new diagonal follows.

The exact, dependency-free verifier is
`BLOCK_GORDAN_RESIDUAL_ELIMINATION_CELLS.py`.

## 1. Exact orbit-representative census

For an ordinary residual representative `P`, call a derived normal `u`
certified when all four determinants obtained by replacing one member of
`P` by `u` are fixed bracket units.  For a localization representative
`P union {z}`, call `u` certified when `det(P union {u})` is structurally zero
and its three replacement cofactors are fixed bracket units.  These are
exactly the hypotheses used by the two residual specialization identities.

The exhaustive 52-orbit calculation gives the following census.  `m` is the
number of certified auxiliaries, `pairs` is `binom(m,2)`, and `R candidates`
counts the generic supports obtained by dropping one wall-circuit element
from `P union {u,v}`.

| type | class | `m` | pairs | `R` candidates |
|---:|---|---:|---:|---:|
| 36 | localization | 12 | 66 | 198 |
| 37 | ordinary | 14 | 91 | 364 |
| 38 | ordinary | 2 | 1 | 4 |
| 39 | localization | 12 | 66 | 198 |
| 41 | ordinary | 14 | 91 | 364 |
| 42 | ordinary | 2 | 1 | 4 |
| 44 | ordinary | 12 | 66 | 264 |
| 46 | localization | 12 | 66 | 198 |
| 47 | localization | 12 | 66 | 198 |
| 48 | ordinary | 16 | 120 | 480 |
| 49 | ordinary | 8 | 28 | 112 |
| 50 | ordinary | 3 | 3 | 12 |
| 51 | ordinary | 4 | 6 | 24 |
| **total** |  | **131** | **671** | **2,420** |

This is an orbit-representative support census, not a count of realized
opposite pairs for a prescribed signature.  The signature signs decide which
certified auxiliaries live on which side.  Every unordered pair can be made
opposite by some aligned sign assignment, but an arbitrary fixed signature
need not use both colors.  There can also be non-unit auxiliaries outside
this certified list.

## 2. Universal elimination lemma

Let `P={p_1,...,p_r}` be a positive circuit of rank `r-1`, where `r=4` for an
ordinary wall and `r=3` for a localization wall.  Write

\[
                         H=\operatorname{span}(P).                \tag{3}
\]

Because `P` has a dependence with every coefficient positive,

\[
                         \operatorname{cone}(P)=H.                \tag{4}
\]

Indeed, adding a sufficiently large multiple of the positive dependence to
any coordinate expression in the `p_i` makes every coefficient nonnegative.

Let `u` and `v` be signed auxiliary normals whose circuits
`Q_-=P union {u}` and `Q_+=P union {v}` live on opposite sides of the wall.
In the ordinary case the quotient of the four-dimensional normal space by
`H` is one-dimensional.  In the localization case every structural
auxiliary lies in the limiting three-space

\[
                L=\lim_{t\to0}\operatorname{span}(P(t)),          \tag{5}
\]

and `L/H` is one-dimensional.  This follows because off the wall `P(t)` has
rank three and every structural determinant `det(P(t),u(t))` vanishes.
Opposite circuit sides say precisely that the images of the signed `u` and
`v` in the relevant one-dimensional quotient have opposite signs.

Consequently there are `alpha,beta>0` for which

\[
                         \alpha u+\beta v\in H.                   \tag{6}
\]

By (4), `-(alpha u+beta v)` is a nonnegative combination of `P`.  Deleting
zero coefficients and then taking a support-minimal nonnegative dependence
gives a positive circuit

\[
                    R\subseteq P\cup\{u,v\},\qquad u,v\in R.     \tag{7}
\]

It contains both auxiliaries because their nonzero quotient classes can
cancel only one another.  The circuit bound gives

\[
             |R|\le5\quad\text{(ordinary)},\qquad
             |R|\le4\quad\text{(localization)}.                  \tag{8}
\]

At a generic point, equality holds and exactly one member of `P` is omitted.
The dependence on `R` is strict at the wall, so its coefficients remain
positive in a neighborhood.  Thus `R` persists on both sides.

This proves existence independently of the rational examples used by the
verifier.  The examples check the complete oriented circuit pattern and the
support bounds with exact arithmetic.

## 3. Why the carrier is exactly an interval

The enlarged columns `U=P union {u,v}` have rank four on an ordinary wall
and rank three on a localization wall.  Hence in either case

\[
                          \dim\ker U=2.                            \tag{9}
\]

Intersecting a two-dimensional kernel with the nonnegative orthant gives a
pointed two-dimensional cone, whose projectivization is an interval.  Its
two extreme rays are exactly the two support-minimal positive circuits.
Near the wall these are

| parameter | first endpoint | second endpoint |
|---|---|---|
| `t<0` | `Q_-` | `R` |
| `t=0` | `P` | `R` |
| `t>0` | `Q_+` | `R` |

The first endpoint is continuous through its zero auxiliary weight, and the
second endpoint stays strict.  After shrinking the transverse interval, the
total normalized nonnegative-kernel family is therefore a rectangle.  In
particular, both arrows in (2) send endpoints to endpoints and the oriented
edge to the oriented edge.

The exact ordinary normal form is

\[
\begin{aligned}
 p_1&=e_1,&p_2&=e_2,&p_3&=e_3,&
 p_4&=(-1,-1,-1,t),\\
 u&=e_4,&v&=(2,3,4,-1).
\end{aligned}                                                    \tag{10}
\]

For `t=-1/10,0,1/10`, its positive circuits are respectively

\[
 \{Q_-,R\},\qquad\{P,R\},\qquad\{Q_+,R\},                       \tag{11}
\]

with

\[
 Q_-=12345,\quad P=1234,\quad Q_+=12346,\quad R=12456.           \tag{12}
\]

The localization normal form is

\[
 p_1=e_1,\quad p_2=e_2,\quad p_3=(-1,-1,t,0),\quad
 u=e_3,\quad v=(2,3,-1,0),                                      \tag{13}
\]

and has

\[
 Q_-=1234,\quad P=123,\quad Q_+=1235,\quad R=1345.               \tag{14}
\]

These are exact rational representatives of the two universal **oriented
support patterns**.  They are not claimed to remove the projective moduli of
an arbitrary six- or five-column carrier.

## 4. Integral mapping cone

Orient an interval from `q` to `r`, so its cellular differential is

\[
                              d(e)=r-q.                           \tag{15}
\]

For either specialization isomorphism in (2), the mapping-cone groups in
degrees `2,1,0` have ranks `1,3,2`.  With bases

\[
 (e_s),\qquad(e_t,q_s,r_s),\qquad(q_t,r_t),                       \tag{16}
\]

their differentials are

\[
 d_2=\begin{pmatrix}1\\1\\-1\end{pmatrix},\qquad
 d_1=\begin{pmatrix}-1&1&0\\1&0&1\end{pmatrix}.                 \tag{17}
\]

One has `d_1 d_2=0`, `rank(d_2)=1`, and `rank(d_1)=2`; the two nonzero Smith
invariants are units.  Therefore the mapping cone is acyclic over `Z`, with
no torsion qualification.

The conclusion is local and constructible: it concerns the closed carrier
which retains the dying half-face and its zero-weight wall endpoint.  It does
not contradict the strict-face no-go.  Restricting (2) to the coordinate face
`Q_-` still gives `point -> point <- empty`; the rectangle supplies the
missing relative cell only after support is enlarged to `U`.

## 5. Coherence along one simple wall

Suppose `u_1,...,u_m` all live on the same side.  Off the wall `P` is
independent.  The positive circuit relation `q_j` on `P union {u_j}` has a
unique nonzero auxiliary coordinate, so the `q_j` are a basis of the kernel
on `P union {u_1,...,u_m}`.  If a kernel vector is nonnegative, its auxiliary
coordinates express it as

\[
                             \sum_{j=1}^m c_jq_j,qquad c_j\ge0.  \tag{18}
\]

The residual difference is supported on the independent set `P` and hence
is zero.  Thus the normalized positive fiber is the simplex with vertices
`q_1,...,q_m`.  Its edges give homotopies between two same-side choices, its
triangles give homotopies between those homotopies, and so on.  The verifier
checks exact three-auxiliary ordinary and localization normal forms.

This supplies all choice coherence **at one generic residual wall**.  It does
not identify the simplexes obtained by crossing a second wall.  A
codimension-two point can change both the wall circuit and the partition of
auxiliaries, and the two iterated elimination carriers need not yet have a
certified common filling.

## 6. Exact remaining target for diagonals 3--8

The codimension-one mutation problem is now solved whenever an opposite
partner exists: use (2), and use the same-side simplexes to remove dependence
on the partner choice.  Two obstructions remain before these local maps form
a global block-Gordan cellular/Morse system:

1. **Monochromatic wall stars.**  For a fixed signature all certified
   auxiliaries can lie on one side.  If its witness disappears across the
   wall, continuation must use an unrelated circuit or a base-cell
   attachment; the local `P` carrier alone cannot supply it.
2. **Codimension-two coherence.**  Around an intersection of residual walls,
   the two compositions of interval carriers must extend over a common
   two-cell while respecting all zero-block and zero-weight faces.  The
   one-wall simplex lemma does not imply this.

The second item is the smallest genuinely new chain-homotopy obstruction.
An exact next census should enumerate codimension-two intersections of the
13 wall types, attach the minimal union of their two elimination supports,
and compare the two integral specialization composites.  A common convex
nonnegative-kernel carrier would fill the square automatically; otherwise
its first failed orbit is an exact obstruction to the proposed global
matching.

## 7. Verification

Run

```console
python ai/omreal/BLOCK_GORDAN_RESIDUAL_ELIMINATION_CELLS.py
```

The script:

- reconstructs the fixed-unit auxiliary census from the exact 52 wall
  orbits;
- checks all `671` possible certified auxiliary pairs and the `2,420`
  generic persistent-support candidates;
- enumerates every positive support in the rational ordinary and
  localization pair normal forms;
- verifies the same-side simplex normal forms; and
- checks the integral mapping-cone matrices and their ranks.
