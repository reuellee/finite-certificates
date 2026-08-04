# Universal residual-wall specialization and the zero-face no-go

## Outcome

Every one of the 13 residual derived-wall types has a universal integral
codimension-one **specialization map** for its positive circuit:

\[
             \text{strict circuit on one side}
             \longrightarrow
             \text{wall circuit with one zero weight}.          \tag{1}
\]

There are two exact normal forms:

| residual types | wall circuit | live circuit |
|---|---:|---:|
| `37,38,41,42,44,48,49,50,51` | 4 normals, rank 3 | 5 normals, rank 4 |
| `36,39,46,47` | 3 normals, rank 2 | 4 normals, rank 3 |

However, there is no cross-wall chain-homotopy equivalence which is strictly
natural on every zero-weight coordinate face.  On the support in (1), the
normalized nonnegative kernel is a point on the live side, the same point
with a zero coordinate on the wall, and empty on the other side:

\[
                         H_0:\qquad\mathbb Z\to\mathbb Z\to0.   \tag{2}
\]

This is the minimal exact obstruction requested by the mutation-map audit.
It explains why the successful row-2599 reroute has to enlarge support:

\[
                  Q_4\longrightarrow P\longleftarrow S_4
\]

is joined inside the six-normal face using the persistent circuit `R4`.
There is no direct continuation of the dying `Q4` coordinate face.

The correct universal codimension-one object is therefore a constructible
**specialization cospan**, not a facewise equivalence between the two open
sides.  Context-dependent circuit-elimination cells must be added before a
global Morse cancellation is possible.

The dependency-free verifier is
`BLOCK_GORDAN_RESIDUAL_MUTATION_MAP_NO_GO.py`.  No diagonal is promoted.

## 1. The nine ordinary residual types

Let `E=(e_1,e_2,e_3,e_4)` be a labeled residual four-set of derived normals,
and let

\[
                              D_E(Y)=\det(a_{e_1},\ldots,a_{e_4}).          \tag{3}
\]

For each of the nine ordinary types there is an auxiliary derived normal
`a_u` such that all four replacement determinants

\[
        A_i(Y)=(-1)^{i-1}\det(a_{e_1},\ldots,
                  \widehat{a_{e_i}},\ldots,a_{e_4},a_u)          \tag{4}
\]

are parent-bracket units.  In particular, every `A_i` is nonzero with fixed
sign throughout the parent realization cell.  The five-vector determinant
identity is

\[
                       \sum_{i=1}^4 A_i a_{e_i}+D_Ea_u=0.         \tag{5}
\]

At a generic point of `D_E=0`, the four wall normals have rank exactly three.
Choose a signature aligned with their circuit and absorb its signs into the
columns.  After one common sign change, all four coefficients `A_i` in (5)
are positive.  On exactly one side of the wall, the coefficient of `a_u` is
positive as well.  Hence

\[
                  Q=E\cup\{u\}                                  \tag{6}
\]

supports a unique strict positive five-circuit there.  Its normalized `u`
weight tends to zero as `D_E` tends to zero.  On the opposite side the unique
kernel relation on `Q` has one coefficient of the wrong sign, so the
nonnegative kernel restricted to `Q` is empty.

Using `t=D_E` as the transverse coordinate and applying a linear change of
the four-dimensional normal space plus positive column scalings reduces (5)
to

\[
\begin{aligned}
 v_1&=(1,0,0,0),&v_2&=(0,1,0,0),&v_3&=(0,0,1,0),\\
 v_4&=(-1,-1,-1,t),&u&=(0,0,0,1),
\end{aligned}                                                   \tag{7}
\]

with kernel relation

\[
                          v_1+v_2+v_3+v_4-tu=0.                  \tag{8}
\]

Thus `t<0` is the live side in this orientation, `t=0` has the positive
four-circuit with zero `u` weight, and `t>0` is dead on support `Q`.

The exact 52-orbit checker reconstructs an auxiliary `u` with four unit
replacement types for precisely

\[
                         37,38,41,42,44,48,49,50,51.             \tag{9}

\]

## 2. The four localization residual types

For the four exceptional types, write the residual representative as

\[
                              E=C\cup\{z\},\qquad |C|=3.         \tag{10}

\]

There is an auxiliary normal `a_w` for which `C union {w}` is structurally
dependent, while the three replacement cofactors are fixed parent-bracket
units.  The exact certificates are:

| type | `C` | `z` | structural auxiliary `w` |
|---:|---|---|---|
| 36 | `123/345/367` | `124` | `134` |
| 39 | `123/356/378` | `124` | `135` |
| 46 | `123/145/167` | `246` | `124` |
| 47 | `123/145/167` | `248` | `124` |

Their determinant identity has the form

\[
                            \sum_{i=1}^3 A_i a_{c_i}+D_Ea_w=0,   \tag{11}

\]

with all `A_i` fixed and nonzero.  On `D_E=0`, the three normals in `C` have
rank exactly two and give the positive wall circuit.  Off the wall,
`C union {w}` has rank three and (11) is its unique relation.  After signature
alignment, it is positive on one side and mixed on the other.

The normal form is

\[
\begin{aligned}
 v_1&=(1,0,0,0),&v_2&=(0,1,0,0),\\
 v_3&=(-1,-1,t,0),&w&=(0,0,1,0),
\end{aligned}                                                   \tag{12}
\]

with

\[
                              v_1+v_2+v_3-tw=0.                  \tag{13}
\]

Again the normalized last weight is positive for `t<0`, zero at the wall,
and has the wrong sign for `t>0`.

Equations (5) and (11) are exactly the two certificate forms in the proved
derived-wall side theorem.  The new verifier reconstructs the `9+4` split
directly from the 52 incidence-orbit table and checks both normal forms over
`Q`; it does not require the unavailable `sympy` package.

## 3. Canonical specialization

Let

\[
 P_Q(t)=\{\lambda\in\mathbb R_{\ge0}^{Q}:
          \mathbf1^T\lambda=1,\ A_\sigma(Y(t))^T\lambda=0\}.    \tag{14}

\]

For the support `Q` in either Section 1 or Section 2, after orienting `t` so
the live side is negative,

\[
 P_Q(t)=
 \begin{cases}
   \{q(t)\},&t<0,\\
   \{p\},&t=0,\\
   \varnothing,&t>0,
 \end{cases}                                                    \tag{15}
\]

where `q(t)` is the normalized cofactor vector and `q(t)->p`.  The last
coordinate of `p` is zero.  The total incidence over `t<=0` is therefore a
closed arc, and limit at the wall defines a canonical integral cellular map

\[
                             \operatorname{sp}_-:C_*(P_Q(t<0))
                             \longrightarrow C_*(P_Q(0)),        \tag{16}
\]

sending the live vertex to the wall vertex.  It is compatible with the
support drop `Q -> Q minus {u}` or `Q minus {w}` because that is exactly the
coordinate which tends to zero.

On a full Gordan fiber, every circuit vertex which collapses to this wall
circuit has the same specialization.  This is the universal part of the
codimension-one mutation rule.  It applies to all 13 residual types.

## 4. No strict zero-face-coherent equivalence across the wall

Suppose one asks for a cross-wall chain map

\[
                    F:C_*(P_\sigma(t<0))\longrightarrow
                         C_*(P_\sigma(t>0))                       \tag{17}

\]

which is:

1. a quasi-isomorphism whenever both full fibers are nonempty; and
2. strictly natural under every coordinate-support inclusion.

Restrict (17) to the support `Q` in (15).  The source is a point and the
target is empty, so the restricted map is zero.  Naturality gives the square

\[
\begin{array}{ccc}
 C_*(P_Q(t<0))&\longrightarrow&C_*(P_\sigma(t<0))\\
 \downarrow 0&&\downarrow F\\
 0&\longrightarrow&C_*(P_\sigma(t>0)).
\end{array}                                                    \tag{18}

\]

Every nonempty Gordan fiber is convex and connected.  The upper horizontal
map in (18) therefore sends the generator of `H_0(point;Z)` isomorphically to
the generator of the full source's `H_0`.  Commutativity forces `F_*` to kill
that generator.  Hence `F` cannot be a quasi-isomorphism.

This obstruction is integral and already occurs on a single vertex.  It is
not removed by shelling the fixed discriminantal zonotope.  Reduced chains
would hide it, but the unresolved third-diagonal term is precisely compact
component `H_c^0`, so discarding the augmentation is not legitimate.

Therefore:

> **Zero-face no-go.**  Every residual wall type has a circuit-aligned face
> diagram which obstructs a universal direct cross-wall chain-homotopy
> equivalence that is strictly natural on all coordinate faces and is
> required to handle all signatures.

This statement does not deny a chain equivalence after adding cells from
larger supports.  It proves that such support enlargement is mandatory.

## 5. Correct mutation object and relation to the hard reroute

The proof-safe universal object is the constructible specialization diagram

\[
 C_*(P_\sigma(t<0))
       \xrightarrow{\operatorname{sp}_-}
 C_*(P_\sigma(0))
       \xleftarrow{\operatorname{sp}_+}
 C_*(P_\sigma(t>0)),                                    \tag{19}

\]

with empty coordinate-face entries retained.  One must take the homotopy
colimit/mapping-cylinder complex of (19), together with circuit-elimination
cells in enlarged supports.  A direct side-to-side map loses the vanishing
face information.

For the exact row-2599 orbit-50 path,

\[
\begin{aligned}
 Q_4&=123/256/127/357/478,\\
 P  &=123/256/357/478,\\
 S_4&=123/134/256/357/478.
\end{aligned}
\]

The two singleton support faces specialize as

\[
                          Q_4\longrightarrow P\longleftarrow S_4.          \tag{20}

\]

The larger six-normal positive face also contains the persistent circuit

\[
                          R_4=134/256/127/357/478,                         \tag{21}

\]

and changes from the interval `[Q4,R4]` to `[P,R4]` to `[S4,R4]`.  That
interval is the additional circuit-elimination cell which makes the local
component reroute possible.  It necessarily leaves the dying `Q4`
coordinate face, exactly as the no-go theorem predicts.

## 6. Remaining finite target

The universal `9+4` specialization theorem reduces, but does not solve, the
cross-wall matching problem.  For every labeled residual occurrence and
every active signature tuple one must still determine whether the wall
circuit has an enlarged-support elimination carrier analogous to
`P/R4`.  Such carriers must then satisfy coherence around simultaneous
codimension-two walls.

The appropriate finite certificate consists of:

1. the specialization cospan (19) for each circuit vertex;
2. an acyclic carrier in the enlarged block-Gordan support complex for every
   dying/appearing vertex;
3. chain homotopies comparing the two carrier composites around every
   codimension-two wall diamond; and
4. a global potential proving that the resulting coordinated matching has
   no directed cycle.

The 13 residual incidence types determine item 1.  They do not determine
items 2--4: those depend on the remaining signed normals, the other active
signature blocks, and compact-component incidence.  This is the precise
point at which a universal higher-Bruhat or fixed-zonotope shelling stops.
