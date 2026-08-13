# Diagonal three: triple contraction needs loop specialization

## Verdict

Neither repeated deletion nor literal triple contraction presently bypasses
the two invariant diagonal-three obligations.  There are two sharp reasons.

First, three normalized height rows with convex fibers in each row separately
can already carry the target group even when every defining trilinear form is
decomposable and alternating.  An exact model in `R^6 x R^6 x R^6` is
homotopy equivalent to `SO(3) x SO(3)` and therefore has

\[
                              H_6\cong\mathbb Z.                 \tag{1}
\]

This is the exact `6+6+6` row format produced by contracting three parent
columns.  It is stronger than a dimension warning: every one-row fiber is an
open halfspace or the empty set.

Second, the extra alternating-minor structure does not permit one to work
over a single uniform triple-contraction stratum.  On an honest uniform
rank-four/eight parent, three distinct realizable private extensions admit a
line segment which preserves every parent bracket and every prescribed
single-private bracket.  The private triple stays independent.  Nevertheless
exactly one unprescribed bracket

\[
                         [p_1p_2p_3y_1]                          \tag{2}
\]

changes sign, while the other seven brackets `[p_1p_2p_3y_j]` do not.  After
contracting the private rank-three set, parent label `1` passes through a loop
and changes its rank-one quotient sign.  Deleting the loop face splits the
segment into two contraction strata.

Thus a contraction proof must retain the rank-one loop faces and construct
their codimension-one specialization maps.  Convex block-Gordan carriers can
fill higher coherences only **after** those maps exist.  They do not create a
map across an omitted loop face.

This note is a no-go for unstratified contraction, not a counterexample to the
third diagonal.  The trilinear model has the local decomposable
alternating-minor/Koszul algebra, but is not asserted to be the complete lift
fiber of one 9DVL parent.  A theorem using the global coupling among all
actual occurrence forms and all loop specializations remains logically
possible.

The exact replay is
[`verify_diag3_triple_contraction_no_go.py`](verify_diag3_triple_contraction_no_go.py).

## 1. Why the lifted private-point space does not lower the target

For a fixed parent realization `Y`, let

\[
 C_i(Y)=\{p\in\mathbb R^4:
          \sigma_{i,I}\,p\mathbin\cdot a_I(Y)>0
          \text{ for every parent triple }I\}.
\]

Each nonempty `C_i(Y)` is an open convex cone.  The lifted three-extension
incidence has fiber

\[
                         C_1(Y)\times C_2(Y)\times C_3(Y),       \tag{3}
\]

so forgetting the three private columns is a homotopy equivalence over the
simultaneous-feasibility locus.  Merely adjoining the private points therefore
does not change `H_6`.

To contract all three private columns, one restricts (3) to independent
triples and records the rank-one quotient coordinates

\[
                         d_e=[p_1p_2p_3y_e].                     \tag{4}
\]

None of the `d_e` is prescribed by the original three extension signatures:
each contains all three private labels.  Uniform contraction charts delete
the walls `d_e=0`.  The exact example in Section 3 proves that these are real
internal walls of (3), not formal boundary divisors.

This also explains why the joined block-Gordan resolution does not remove the
issue.  Its coordinates resolve positive dependences among the single-private
forms `p_i dot a_I(Y)`.  Equation (4) is not one of those coordinates.  The
all-codimension convex-carrier theorem supplies homotopies among already
defined face maps, but a cospan

```text
positive quotient sign  ->  loop face  <-  negative quotient sign
```

must first be present in the relative complex.

## 2. A decomposable alternating model with nonzero `H_6`

Split every row into two three-vectors,

\[
 x=(x_A,x_B),\qquad y=(y_A,y_B),\qquad z=(z_A,z_B)
 \quad\text{in }\mathbb R^3\oplus\mathbb R^3,
\]

and put

\[
 Z=\{(x,y,z):
       \det(x_A,y_A,z_A)>0,\quad
       \det(x_B,y_B,z_B)>0\}.                           \tag{5}
\]

Both defining tensors are decomposable alternating three-forms:

\[
 dx_1\wedge dx_2\wedge dx_3,
 \qquad
 dx_4\wedge dx_5\wedge dx_6.                           \tag{6}
\]

In particular every contracted normal annihilates the other two row vectors,
which is exactly the local Koszul identity.  With any two rows fixed, (5)
cuts the third row by two strict linear inequalities in disjoint
three-coordinate blocks.  The fiber is open convex or empty.

Regrouping the coordinates into the two matrices with columns
`(x_A,y_A,z_A)` and `(x_B,y_B,z_B)` gives the literal homeomorphism

\[
                         Z\cong GL^+(3,\mathbb R)^2.             \tag{7}
\]

Polar decomposition retracts each factor to `SO(3)`.  Since `SO(3)` is a
closed connected orientable three-manifold,

\[
                         H_6(Z;\mathbb Z)
                         \cong H_3(SO(3);\mathbb Z)^{\otimes2}
                         \cong\mathbb Z.                         \tag{8}
\]

Thus even separate convexity plus decomposable alternation and the repeated-
row Koszul identity do not prove the degree-six vanishing.  A positive theorem
must use additional coupling among the complete family of actual occurrence
forms and its specialization faces.

## 3. An actual one-loop contraction wall

Use the exact parent matrix whose columns are

\[
Y=\begin{pmatrix}
0&-3&-8&-7&-1&-1&5&8\\
-6&-8&1&8&2&-1&2&8\\
-1&4&6&2&2&8&8&2\\
8&1&-4&4&8&2&-6&5
\end{pmatrix}.                                                  \tag{9}
\]

All `70` parent brackets are nonzero.  In the repository's colex order on
the `56` parent triples, take the distinct extension signatures

```text
454112161268235
58432476850159616
13949244655240191
```

and the private columns

\[
\begin{aligned}
p_1&=(-1048,7770,-2258,5819),\\
p_3&=(-3246,5283,6492,4405),\\
p_2^-&=(449,1898,-6928,6982),\\
p_2^+&=(903,2264,-6681,7047).
\end{aligned}                                                   \tag{10}
\]

The signed minima over the `56` prescribed brackets are respectively

```text
2273, 147496, 49632, 1140.
```

Thus both endpoints for `p_2` realize the same second signature.  Every
signed bracket is affine and strictly positive on

\[
                 p_2(t)=(1-t)p_2^-+tp_2^+,
                 \qquad0\leq t\leq1.                            \tag{11}
\]

The eight rank-one quotient coordinates at the two ends are

```text
t=0:
  413089713655  -747753275210  -2585829854324  -1863473622438
  549618851982   668147843790   2293731744432   3753760141212

t=1:
  -48023641259  -961614275203  -2306296425946  -1712807800687
  304575706691   560712995309   2485800701723   3651972965576
```

Only the first sign changes.  Since every coordinate is affine in `t`, the
unique wall parameter is

\[
                       t_0=\frac{413089713655}{461113354914}.    \tag{12}
\]

At `t_0`, the other seven coordinates remain nonzero with their displayed
signs.  In particular the second coordinate stays negative, so
`p_1,p_2(t),p_3` have rank three throughout (11).  The specialization is
exactly one loop in the rank-one contraction, not a loss of rank of the
contracted private set.

For a literal one-wall neighborhood, restrict (11) to

\[
                 t_0-\frac1{100}\leq t\leq t_0+\frac1{100}.     \tag{13}
\]

The exact verifier checks every moving mixed-private bracket: the `56`
brackets using `p_2`, one other private column, and two parents, together with
the eight coordinates (4).  All `64` are nonzero at both ends of (13), and
only (2) has opposite signs.  At the midpoint only (2) vanishes.  Thus (13)
is the smallest relevant failure mode: one private column moves on one line,
one unprescribed alternating minor vanishes once, and every other prescribed
or mixed bracket stays in its fixed stratum.  Any fixed-uniform-stratum
contraction drops the middle face and breaks specialization.

## 4. Consequences for the candidate direct routes

### Repeated deletion

Deleting one parent column from the lifted incidence is safe but insufficient.
Its insertion fiber is an open convex three-cell: parent brackets containing
the deleted label and all three single-private bracket families are linear in
that column.  The base still has dimension `6+3+3+3=15`, so this gives no
degree-six bound.

A second or third simultaneous insertion introduces determinants involving
two or three moving columns.  The fibers are only separately convex.  The
model (5) shows that separate convexity at the final three-row dimensions can
retain `H_6`; specialization data, not another pointwise fiber bound, is
required.

### Triple contraction

Contracting three parent labels yields three normalized six-dimensional
height rows.  Section 2 blocks the dimension/convexity theorem.  Contracting
the three private labels instead introduces the unprescribed coordinates
(4).  Section 3 blocks a reduction to one fixed uniform rank-one quotient.
The loop strata and their exit maps must be retained.

### Leray and Alexander duality

The block-mass filtration already proves that triple-bad component
noncompactness and the balanced pair restriction map are invariant
obligations.  A contraction compactification may compute them, but cannot
remove them.  The exact wall (12) is a codimension-one specialization which
such a compactification must include.  Pointwise ordinary fiber homology
does not determine that map.

### Alternating-minor/Koszul structure

The local alternating and repeated-row identities do not improve Section 2:
model (5) already has both.  Existing double-contraction pruning additionally
uses the common occurrence system to exclude a circuit with exactly one
constant row and to bound all-bilinear supports.  It still does not construct
the loop specialization in Section 3 or exclude the rank-six all-bilinear
kernel case.  A successful theorem would have to combine global occurrence
coupling with a proper all-loop incidence complex.  Neither local Koszul
algebra nor convex carriers alone forces `H_6=0`.

## 5. Replay

```console
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/verify_diag3_triple_contraction_no_go.py
```

The verifier uses integer and rational arithmetic only.  It checks the two
decomposable alternating forms and the top cellular boundary of
`SO(3) x SO(3)`, all parent and extension brackets, both quotient sign
vectors, the unique rational loop parameter, and the nonvanishing of the
other seven quotient coordinates.  It also exhausts all `64` mixed-private
minors on the local interval (13), proving that the canary contains exactly
one specialization wall.
