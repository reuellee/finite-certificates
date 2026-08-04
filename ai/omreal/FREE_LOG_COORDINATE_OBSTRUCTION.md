# Free-log-coordinate obstruction

The standard projective-frame normalization for `UOM(4,8)` is

\[
Y(a,\ldots,i)=
[e_1,e_2,e_3,e_4,(1,1,1,1),(1,a,b,c),(1,d,e,f),(1,g,h,i)].
\]

Inside a fixed sign orthant, write

\[
u=(\log|a|,\ldots,\log|i|).
\]

Passing from the stored catalog charts to this display uses the same fixed
column reorientation at every tested point.  Its signs are determined by
nonzero parent brackets and therefore cannot change within the parent cell.
The verifier independently checks that all normalized endpoints have one
common 70-bracket sign vector.

This note records the exact outcome of testing a possible convex-log proof of
9DVL.  The outcome is negative, already for catalog parent 2599.

## 1. Two exact failures

The checker
[`verify_free_log_nonconvex.py`](verify_free_log_nonconvex.py) normalizes four
integer charts from the tracked 178-chart row-2599 certificate.  It uses exact
rational arithmetic at the endpoints.  A free-log midpoint has coordinates
`sqrt(x_j y_j)`; the checker encloses every square root between exact rational
bounds and propagates those bounds by interval arithmetic.

It proves:

1. Charts 0 and 3 lie in the same parent realization cell, but their free-log
   midpoint reverses the sign of parent bracket `[5678]`.  Thus the parent
   cell is not convex in the nine free logarithmic coordinates.
2. Charts 77 and 85 lie on the side `q_44>0`.  Their free-log midpoint keeps
   the correct strict signs of **all 70 parent brackets**, but satisfies
   `q_44<0`.  Thus even a residual side restricted to the parent cell need not
   be free-log convex.

The second statement is stronger than failure of the parent premise: its
midpoint is still an honest point of the same parent cell.  Residual type 44
has the exact representative

\[
\begin{aligned}
q_{44}={}&aei-ae-afh+af+ah-ai+cdh-cdi-ceg+ce\\
         &+cfg-cf-ch+ci-dh+di+eg-ei-fg+fh.
\end{aligned}
\]

No floating-point sign decision occurs in the verifier.

## 2. What this blocks

The failed implication is

\[
\text{free-log convex parent cell and convex residual sides}
\Longrightarrow
\text{no bounded residual chamber}
\Longrightarrow
H_c^0=0.
\]

Both convexity premises are false.  Therefore one cannot settle the second
diagonal by treating the 13 residual cofactors as convex inequalities in the
nine variables `u`, nor by invoking KKT separation under that premise.  The
certificate does **not** exhibit a compact component of a `5+5` circuit
intersection, does not prove nonzero cohomology, and is not a counterexample
to 9DVL.

## 3. The weaker statement that survives

There is nevertheless an exact coordinate-section theorem.

> **Coordinate-section theorem.**  In a fixed free-coordinate sign orthant,
> every parent realization cell has interval intersection with every line on
> which eight of `u_1,...,u_9` are fixed.  Equivalently, it is orthogonally
> convex in the free-log coordinates.

Indeed, each parent bracket is affine in each matrix entry separately.  With
eight coordinates fixed, every prescribed bracket-sign inequality cuts out a
half-line (or all or none) in the remaining signed coordinate `x_j`.  Their
intersection with the fixed coordinate ray is an interval.  The monotone map
`x_j -> log|x_j|` preserves intervals.

For the twelve residual types other than 51 (`36,37,38,39,41,42,44,46,47,48,49,50`),
every displayed residual polynomial is also affine in each one of the nine
free coordinates.  Hence both sides of those 12 residual walls, after
intersection with a parent cell, have the same coordinate-section property.
Type 51 is quadratic in `b`, so the universal all-coordinate statement does
not follow; its certified pivot `f` is linear, and both type-51 sides are
interval-convex along the `f` coordinate.

This surviving result is too weak for a no-bounded-chamber theorem.
Orthogonal convexity does not imply ordinary convexity and, without a common
escape direction, intersections of coordinate-section-convex sides can be
bounded.  A proof for a `5+5` pair must still establish one of the genuinely
global missing facts: a compatible escape vector field, exclusion of positive
spanning among its active logarithmic wall normals, or injectivity of the
compact-component incidence differential.  The single-wall pivot derivatives
alone provide none of these.

There is a useful proof-safe KKT target.  Let one generic residual chamber in
log coordinates be

\[
C=\{u\in X:f_1(u)>0,\ldots,f_r(u)>0\},
\qquad f_j=s_jq_j(e^u),
\]

with the fixed coordinate signs understood.  If a component of `C` has
compact closure in `X`, then

\[
P(u)=\prod_{j=1}^r f_j(u)
\]

is zero on the boundary of that component and has a positive interior
maximum.  At some interior point `u_*`, therefore,

\[
0=\nabla\log P(u_*)
 =\sum_{j=1}^r \frac{\nabla f_j(u_*)}{f_j(u_*)}.       \tag{1}
\]

Thus a relatively compact generic chamber forces a **positive dependence**
among its signed logarithmic wall gradients.  This gives a sound finite criterion:
exclude solutions of (1) for every realizable `5+5` sign pattern and no such
compact chamber exists.  When `r<=9`, full column rank of the `9 x r` gradient
matrix already excludes (1).  When `r=10`, a rank-nine matrix has a
one-dimensional kernel, so it is enough to show that its kernel vector is not
strictly positive.  Clearing the positive factors `e^{u_k}` and `f_j(u)`
turns this into a semialgebraic determinant-sign test.

Criterion (1) is necessary, not sufficient, and it applies to full-dimensional
generic sign chambers.  Lower-dimensional boundary strata and the incidence
maps between chambers remain part of the second-diagonal problem.  In
particular, the counterexample above rules out replacing (1) by a blanket
convexity assertion, but it does not rule out an exhaustive signed-gradient
certificate on the actual `5+5` residue.

Run the certificate with:

```bash
python ai/omreal/verify_free_log_nonconvex.py
```
