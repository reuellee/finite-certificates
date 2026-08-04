# A realizable Farkas obstruction to strict residual-wall descent

## Outcome

A multi-coordinate pivot repairs the exact `37 -> 44 -> 37` coordinate
cycle: at that double wall there is a direction which increases both signed
bad-side functions.

It does **not** repair the wall descent universally.  The coincident residual
types 46 and 47 support an exact proper incomparable signature pair whose
signed bad gradients are `g` and `-g`.  The primitive positive Farkas
certificate is `(1,1)`, so no tangent direction can strictly increase both.
This is an actual realizable extension pair, not an abstract choice of wall
orientations.

The obstruction is nevertheless harmless at the certified point: on the
common wall both signatures are excluded by the same positive three-circuit,
which omits label 8.  Moving label 8 tangentially preserves that witness and
reaches the parent wall `[5678]=0`.  Thus the strict cone field fails, but its
smallest exact failure has a boundary escape.

The remaining plausible mechanism is a **stratified** field: use a strict
common cone where it exists, and when Farkas produces an opposite coincident
wall, descend tangentially using the common lower-support circuit.  No global
well-founded potential or compatibility theorem for those local choices is
proved here.  Diagonal two remains open.

## 1. The exact cone alternative

Let `L` be the tangent space left after imposing any first-order equations
needed to preserve active lower-support witnesses.  For signed bad-side
functions `p_1,...,p_m`, write

\[
                \bar g_j=dp_j|_L\in L^*.
\]

The desired strict cone is

\[
        C=\{v\in L:\bar g_j(v)>0\text{ for every }j\}.             \tag{1}
\]

Gordan's strict alternative gives exactly one of

\[
 C\ne\varnothing,
 \qquad\text{or}\qquad
 \sum_j\lambda_j\bar g_j=0
 \quad(\lambda_j\ge0,\;\lambda\ne0).                              \tag{2}
\]

Thus a failed cone is not a numerical optimization issue: it has a finite
positive-gradient certificate.  For two nonzero gradients, failure is
possible precisely when they are oppositely proportional.  For three, it is
possible only after their projected rank drops to at most two and the origin
lies in their positive cone.

This criterion is local.  Even when `C` is nonempty, it does not by itself
give a continuous field, completeness, or termination at the parent
boundary.

## 2. The 37/44 coordinate cycle has a combined cone

At the exact uniform double wall from
`DIAG2_PIVOT_ALL_COMPACT_SECOND_WALL.md`, put

\[
(a,b,c,d,e,f,g,h,i)=
\left(\frac12,-3,-1,\frac14,-1,2,2,3,-3\right).
\]

With `x=a-1/2`, `y=d-1/4`, orient the two bad sides as

\[
                 p_{37}=3x-2y,
       \qquad    p_{44}=-6x+12y.                                   \tag{3}
\]

The individual canonical directions fail: increasing `a` decreases `p_44`,
and increasing `d` decreases `p_37`.  But the combined direction

\[
                         (\dot a,\dot d)=(1,1)                     \tag{4}
\]

has

\[
                         \dot p_{37}=1,
             \qquad      \dot p_{44}=6.                            \tag{5}
\]

Hence the earlier wall-label cycle is a no-go only for one-coordinate Bland
pivots.  It is not a positive-gradient obstruction.

## 3. An exact proper incomparable opposite-wall pair

Use the common type-46/type-47 localization wall

\[
 q=af-bf-cd+ce=0                                                   \tag{6}
\]

at

\[
(a,b,c,d,e,f,g,h,i)=
\left(2,3,5,7,\frac{46}{5},11,13,17,19\right).                     \tag{7}
\]

All seventy parent brackets are nonzero.  Set `epsilon=1/100` and let
`Y_-`, `Y_+` be obtained by replacing `a=2` with `2-epsilon`,
`2+epsilon`.  Their parent chirotopes agree with the wall chirotope.

The exact signatures are

\[
 \sigma=35958702884521921,
 \qquad
 \tau=54112465834733631.                                          \tag{8}
\]

They are realized by the following extension points:

\[
 x_\sigma=(3290,10000,9935,65)\quad\text{over }Y_-,
\]

\[
 x_\tau=(-7,-993,-1000,7)\quad\text{over }Y_+.                    \tag{9}
\]

On the opposite sides, exact Gordan circuits exclude them:

\[
 Q_{46}=123/145/167/246/235
\]

excludes `sigma` over `Y_+` with positive weights

\[
 \left(\frac{1419}{500},13,1,\frac{11}{100},\frac{33}{100}\right), \tag{10}
\]

while

\[
 Q_{47}=123/145/167/248/234
\]

excludes `tau` over `Y_-` with positive weights

\[
 \left(\frac{673}{250},13,1,\frac{11}{100},\frac{187}{100}\right). \tag{11}
\]

Consequently both signatures are proper, and neither feasibility region
contains the other.

On the wall, both signatures restrict to signs `(+,-,+)` on

\[
                         123/145/167.                              \tag{12}
\]

The three signed normals have rank two and positive dependence weights

\[
                              (13,65,5).                            \tag{13}
\]

Thus both signatures are bad on the wall itself.  Since `q=11(a-2)` on this
slice, the displayed bad sides are

\[
                         p_\sigma=q,
             \qquad      p_\tau=-q.                               \tag{14}
\]

At (7),

\[
 g=dq=\left(11,-11,\frac{11}{5},-5,5,-1,0,0,0\right).             \tag{15}
\]

The signed-gradient matrix therefore has rows `g,-g`, and

\[
                              1g+1(-g)=0.                           \tag{16}
\]

Equation (16) is the smallest possible positive Farkas obstruction.  It
persists after restricting to any witness-preserving tangent space: the two
restricted covectors remain opposites (or both become zero).

## 4. The minimal obstruction escapes tangentially

The common witness (12) omits label 8.  Both the witness normals and the
localization equation (6) are independent of `y_8`.  At (7), hold everything
except `g` fixed and move

\[
                         13\le g<\frac{421}{32}.                    \tag{17}
\]

Every parent bracket is affine in this coordinate.  Exact endpoint
evaluation shows that their signs remain fixed throughout (17), and at
`g=421/32` precisely

\[
                              [5678]=0                              \tag{18}
\]

while the other 69 parent brackets remain nonzero.  The positive dependence
(13) is literally unchanged.  Hence the simultaneous-bad component through
this exact Farkas obstruction reaches the parent boundary.

The same omitted-label statement is invariant under relabeling of the
46/47 localization support.  It supplies the correct local fallback: when
opposite gradients prohibit strict motion, move tangent to their common wall
while retaining the shared lower-support circuit.

## 5. Exact adjacent triple-wall fan

The verifier also exhausts the representative third wall types adjacent to
the common 46/47 residual in this normalization.  Exact uniform rational
points exist with zero set exactly `{46,47,k}` for

\[
                    k=37,38,39,41,42,44,48,49,50.                  \tag{19}
\]

Their nine coordinate tuples are stored directly in the checker.  Each
triple inherits the two-term certificate (16), irrespective of the third
orientation.

The two missing representative triples are algebraically forbidden in the
uniform parent locus.  Dependency-free polynomial expansion verifies

\[
 cf[4567]
 =c(1-e)q_{36}+c(1-d)(q_{46}-q_{36}),                              \tag{20}
\]

and

\[
 q_{51}-c[4678]=(b-h)q_{46}.                                      \tag{21}
\]

Since `c=[1236]` and `f=[1237]` are nonzero in a uniform parent, equations
`q_36=q_46=0` force `[4567]=0`; equations `q_51=q_46=0` force `[4678]=0`.

This is an exhaustive fan calculation for triples containing the coincident
representatives 46 and 47.  It is not an enumeration of all signed, labeled
two- and three-wall occurrences in all 2,604 parent cells.  The size-two
proper-pair obstruction already disproves a universal strict-cone theorem;
the triple fan records how that obstruction meets the other representative
walls.

## 6. Verification and remaining target

Run

```console
python ai/omreal/DIAG2_PIVOT_CONE_FARKAS_VERIFY.py
```

The checker uses rational/integer arithmetic for both extension signatures,
all parent brackets, all circuit dependencies, the cone certificates, the
tangent escape, the nine triple witnesses, and identities (20)--(21).

The exact remaining target is a global stratified continuation theorem:

1. choose a strict common-cone direction whenever (2) has no certificate;
2. convert every positive-gradient certificate into a common lower-support
   tangent escape, as happens for 46/47; and
3. prove that switching between these two modes cannot cycle and must reach a
   parent boundary.

No such global potential is currently proved, so this artifact does not
promote diagonal two.
