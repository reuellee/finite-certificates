# Hostile diagonal-three countermodel: pair escapes plus a compact triple

This note is review scratch only.  It supplies an exact logical falsifier for
any proposed bridge of the form

```text
primitive coordinatewise-multiaffine equations
+ every pair zero set component noncompact
=> every triple zero set component noncompact.
```

Work in `R^9` with coordinates `x_1,...,x_9`.  Put

\[
 L_1=\sum_{i=1}^4x_i,\qquad L_2=\sum_{i=5}^9x_i,
\]

and

\[
 Q=-2\sum_{1\le i<j\le4}x_ix_j
   -2\sum_{5\le i<j\le9}x_ix_j-1.
\]

All three polynomials are affine in each coordinate separately.  They are
distinct and primitive.  The quadratic part of `Q` is block diagonal with
blocks `I_4-J_4` and `I_5-J_5`, hence has rank nine; consequently `Q` cannot
factor as a product of affine-linear polynomials (whose quadratic matrix has
rank at most two).

On `L_1=L_2=0`, use

\[
 -2\sum_{i<j}x_ix_j=\sum_i x_i^2-\left(\sum_i x_i\right)^2
\]

in each block.  Therefore

\[
 Z(L_1,L_2,Q)=
 \{L_1=L_2=0,\ \sum_{i=1}^9x_i^2=1\}\cong S^6.
\]

This is a smooth compact connected triple component.  The three gradients
have rank three there: modulo the two block-sum covectors, `dQ=2x`, and `x`
cannot be blockwise constant with both block sums zero on the unit sphere.

Every pair component is nevertheless noncompact:

* `Z(L_1,L_2)` is `R^7`.
* On `L_1=0`, decompose the second block as `v+s(1,1,1,1,1)` with
  `sum(v)=0`.  Then `Q=0` is

  \[
  \|x_{1:4}\|^2+\|v\|^2-20s^2=1,
  \]

  so `Z(L_1,Q)` is homeomorphic to `R x S^6`.
* On `L_2=0`, the analogous first-block decomposition gives

  \[
  \|w\|^2+\|x_{5:9}\|^2-12s^2=1,
  \]

  and `Z(L_2,Q)` is again homeomorphic to `R x S^6`.

The pair intersections are smooth: dependence of `dQ` on the relevant block
sum covector would force every coordinate in both blocks to vanish, contrary
to `Q=0`.

Translation `x=p+y` preserves coordinatewise multiaffinity, and replacing the
constant `1` by `epsilon^2` scales the sphere.  Thus the compact triple can be
placed inside an arbitrarily small ball around any prescribed interior point
of any open parent chamber.  Intersecting the smooth connected pair
hyperboloids with an open chamber cannot create a compact component: every
component is open in the positive-dimensional pair manifold, while compactness
would also make it closed and hence a compact global component.

This model does not satisfy the actual third-compound/Pluecker occurrence
coupling.  Its conclusion is only that a successful all-residue theorem must
use that extra coupling (or an equivalent exact identity); multi-affinity,
smoothness, pair noncompactness, and parent-cell openness still do not suffice.
