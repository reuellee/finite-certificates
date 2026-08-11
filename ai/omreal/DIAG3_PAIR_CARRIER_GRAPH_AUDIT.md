# Diagonal three: exact ordered-root carrier graph audit

## Outcome

For the minimum elementary-escape-overlap bad-signature pair stored at each
of the 178 exact row-2599 point charts, the full ordered two-root
escape-choice graph is connected.  Every graph has at least nine exact
rank-two carrier edges, and every vertex has degree at least two.

The word **ordered** is essential.  The inverse third-compound transport has
a genuine bilinear term when two elementary roots do not commute.  At chart
57 the graph obtained by retaining commuting root pairs is disconnected; two
reciprocal-root ordered carriers repair it.

This is a finite theorem about 178 stored points and one selected pair at each
point.  It is not an audit of every bad pair, the point bank is not a
coverage-certified atlas of the parent cell, and no face-specialization or
proper carrier-cover theorem is proved here.  Consequently this audit does
**not** prove the pair `H_c^1` column or the third diagonal.

The exact checker is
[`verify_diag3_ordered_root_atlas178.py`](verify_diag3_ordered_root_atlas178.py).

## 1. The ordered third-compound rule

An oriented elementary root is

\[
                         d=(e\longrightarrow f,a),
 \qquad e\ne f,\quad a\in\{-1,+1\}.
\]

Let `N_d` send the source basis vector to `a` times the target basis vector
and kill the other basis vectors.  For two roots use the ordered Bruhat cell

\[
 g_{d,d'}(u,v)=(1+uN_d)(1+vN_{d'}),\qquad u,v\ge0.             \tag{1}
\]

Its inverse acts in the order

\[
                 g_{d,d'}^{-1}=(1-vN_{d'})(1-uN_d).            \tag{2}
\]

For every parent triple `I`, the checker expands (2) exactly and then takes
its third exterior power:

\[
 \Lambda^3g_{d,d'}^{-1}e_I
 =e_I+\sum_{J,(r,s)\ne(0,0)}
        c_{I,J}^{r,s}u^rv^se_J,
 \qquad r,s\in\{0,1\}.                                       \tag{3}
\]

All repeated exterior labels are discarded and all equal target monomials
are collected before signs are tested.  Thus (3) includes cancellation and
the full `u*v` cross term; it is not the union of two one-shear deletion
tests.

For a signature `rho`, call source row `I` safe when

\[
                  \rho_I\rho_Jc_{I,J}^{r,s}\ge0               \tag{4}
\]

for every nonconstant nonzero coefficient in (3).  A nonnegative dependence
supported on safe rows transports throughout the positive parameter cell.
The checker decides existence of that dependence by strict Gordan duality:
it is present exactly when no complete derived-arrangement tope agrees with
`rho` on all safe rows.

For a bad pair `(rho,eta)`, the graph has:

* one vertex for every elementary root which separately transports a
  witness for both signatures; and
* an edge `{d,d'}` when the root lines are independent and either the order
  `(d,d')` or the reverse order has a safe positive dependence for **both**
  signatures.

Requiring one common order matters.  Allowing one signature to use (1) and
the other to use its reverse would not define a simultaneous two-parameter
carrier.

## 2. Exact 178-chart result

At every chart the checker reconstructs and verifies all 26,112 complete
topes, recomputes the two 112-bit elementary escape masks, and checks the
complete ordered graph.  The common vertex counts are:

| vertices | charts |
|---:|---:|
| 6 | 32 |
| 8 | 81 |
| 9 | 30 |
| 10 | 24 |
| 11 | 11 |

The complete joint-edge histogram is:

| joint edges | charts | joint edges | charts |
|---:|---:|---:|---:|
| 9 | 13 | 29 | 2 |
| 11 | 8 | 30 | 4 |
| 14 | 2 | 32 | 1 |
| 15 | 9 | 35 | 7 |
| 22 | 10 | 39 | 5 |
| 24 | 6 | 40 | 8 |
| 26 | 18 | 41 | 7 |
| 27 | 6 | 43 | 4 |
| 28 | 57 | 52 | 11 |

Every one of the 178 graphs is connected.  The minimum edge count is `9`,
the minimum vertex degree is `2`, and the maximum vertex degree is `10`.
The semantic SHA-256 over every chart's two signatures, full 112-bit vertex
mask, and complete ordered edge list is

```text
7a3beb589109c8343be17084514eadd778f5eb6ebb918f0d67dafc05120d78ef
```

Pinning the edge lists, rather than only the connectivity verdict, makes a
missing cross term or an order reversal change the digest.

## 3. Two exact no-go regressions

### Same-source planes are not universal

At pattern zero of `data/seeat_parent2599_shatter8.npz`, the valid bad
signatures

```text
13940505201306607
14522353027604480
```

have elementary escape sets of size `55` and `55`.  Their intersection is
exactly

```text
(1 -> 3, -)  (2 -> 4, +)  (3 -> 1, +)
(4 -> 2, -)  (5 -> 8, -)  (8 -> 5, +)
```

No two common axes have the same source.  Restricting a same-source
two-carrier to either coordinate axis would give two common elementary
escapes, so this pair has no same-source plane carrier.  Exact charts 3 and
6 realize the two opposite feasibility patterns, making the regions proper
and incomparable.  Cross-source commuting carriers do exist, so this is a
no-go for the same-source theorem, not for rank-two carriers.

### Commuting squares are not universal

At stored chart 57 the minimum-overlap pair is

```text
1211253791914816
3827403733557248
```

Its full graph has 9 vertices and 26 edges.  Restricting to commuting root
pairs leaves 24 edges and two components of sizes 8 and 1.  The isolated
root is

```text
(3 -> 6, +).
```

The two omitted, noncommuting edges join it to

```text
(6 -> 3, -)  and  (6 -> 3, +).
```

The checker pins this `8+1` commuting-only split and its repair.  A verifier
which silently deletes the bilinear term, or refuses reciprocal roots, fails
this exact chart.

## 4. What a pair-column theorem would still need

The numerical graph statement is pointwise.  Vanishing of

\[
                         H_c^1(B_\rho\cap B_\eta)
\]

requires a global, proper carrier construction.  A sufficient theorem would
provide a finite regular compactified subdivision of every parent cell with
the following data.

1. On every pair-bad cell, the exact ordered-root choice graph is nonempty
   and connected.
2. Vertex witness faces and edge witness faces specialize monotonically to
   every incident lower cell, after the required circuit-elimination
   reroutes at endpoint-specific walls.
3. Every vertex ray and ordered two-root carrier is proper relative to the
   parent boundary, including all zero-weight and zero-block faces.
4. The augmented carrier cover is exact through degree one.  Equivalently,
   local root choices and their edge homotopies assemble to a compact-support
   chain contraction with no boundary-free monodromy.

Convex block-Gordan faces would then give all higher homotopies by the
existing all-codimension acyclic-carrier theorem.  They do not construct the
codimension-one maps, prove properness, or rule out a global directed cycle.
The 178 points supply none of the required cell coverage or face maps and
test only one pair per point.  Connectivity of these sampled graphs therefore
cannot be promoted to a pair-column theorem.

There is a sharp finite criterion once such coverage has been constructed.
Let the augmented proper carrier complex be the actual two-skeleton of a
finite CW model of the one-point compactification of the block-Gordan
resolution (or, equivalently, map to it by a homology one-equivalence).
Collapse the infinity faces, choose a spanning tree in the resulting
connected one-skeleton, and use the non-tree fundamental cycles as a basis of
`ker(d_1)`.  Write the boundaries of all proper carrier two-cells in that
basis as the columns of an integer matrix `A`.  Then

\[
 H_c^1(B_\rho\cap B_\eta;\mathbb Q)=0
 \quad\Longleftrightarrow\quad
 \operatorname{rank}_{\mathbb Q}A=\#\{\text{non-tree edges}\}.
\]

A rational right inverse of `A` gives the degree-one chain contraction
explicitly; unit Smith invariants give an integral contraction.  Full
rational row rank already implies integral `H_c^1=0` by the universal
coefficient theorem, even if torsion prevents an integral contraction.
This two-skeleton test allows directed receiver loops: a loop is harmless
when it is a boundary column of `A`.  What remains missing is the
coverage-certified labeled complex, including its infinity faces, and the
full-row-rank calculation.  A quotient by only the 13 local wall types cannot
substitute for that global incidence data.

## 5. Verification

A two-chart smoke replay is:

```console
python ai/omreal/verify_diag3_ordered_root_atlas178.py --limit 2
```

The complete pinned audit is:

```console
python ai/omreal/verify_diag3_ordered_root_atlas178.py --workers 4
```

The checker consumes the already committed exact point bank and the pinned
minimum-overlap summary.  Its successful final scope line explicitly says
that the stored points are not a parent-cell coverage theorem.
