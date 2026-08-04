# Diagonal 9: localized residual factors and the COM question

## Verdict

The exact factor and pivot theorems give a strong **local** conclusion but no
global COM theorem:

> Every genuine residual wall in a fixed uniform parent cell is a smooth,
> cooriented hypersurface and is monotone in at least one normalized
> coordinate.  At an intersection where two residual gradients are
> independent, the local face system is the full two-coordinate oriented
> matroid diamond.

The row-2599 transverse node realizes and verifies such a diamond exactly.

However, nonvanishing pivot derivatives do not imply COM face symmetry,
strong elimination, pseudohyperplane behavior, gated faces, or a partial-cube
global chamber graph.  Two elementary exact polynomial models below show the
logical gaps separately.  No actual COM violation has yet been found for the
localized row-2599 residual arrangement; equally, no COM completion has been
proved.

Replay the exact audit with

```bash
python ai/omreal/DIAG9_GRAPH_verify_com_diamond.py
python ai/omreal/DIAG9_GRAPH_verify_node_factor_link.py
```

## What the pivot theorem really gives

For each of the thirteen residual orbit representatives, the derived-wall
classification exhibits a normalized coordinate `x` such that

\[
  \frac{\partial q}{\partial x}
   =\pm\prod_I [I],
\]

where the factors on the right are parent brackets.  Relabeling, followed by
the corresponding adapted nine-variable normalization, transfers this
assertion to every one of the 26,740 global factor classes in
`DIAG9_GRAPH_GLOBAL_FACTOR_CENSUS.md`.  It does not select one common pivot
coordinate for all 26,740 equations in the fixed standard chart.

Inside a fixed uniform oriented-matroid realization cell, all parent brackets
are nonzero with fixed signs.  Hence:

1. `dq` never vanishes on `q=0`; each residual wall is smooth.
2. The wall has a canonical local coorientation.
3. In the wall's adapted normalization, on every connected fiber obtained by
   holding the other eight coordinates fixed, `q` is strictly monotone and
   has at most one zero.
4. If `q_1=q_2=0` and `dq_1,dq_2` are independent, the inverse-function
   theorem identifies the arrangement locally with the two coordinate axes.
   All four chamber sectors and all nine face sign vectors occur.

The third point also uses that a normalized-coordinate fiber of a fixed
parent cell is an interval: every parent bracket is affine in one matrix
entry, and its prescribed strict sign is a linear inequality on that fiber.

These are meaningful geometric constraints.  They are nevertheless
one-wall or transverse-local statements; COM axioms compare many faces and
many chambers globally.

## The exact row-2599 diamond

The transverse node has two local branches.  The global factor census maps
their 65 labeled occurrences respectively to factor IDs

```text
1657 and 12874.
```

Each global class has multiplicity 65, and the IDs are distinct.  Thus the
node is not a self-intersection of one wall or a plane artifact.

On the two factor coordinates, the exact strata realize

\[
\{-,0,+\}^2.
\]

The four generic chamber topes are

\[
(+,+),\quad(+,-),\quad(-,-),\quad(-,+),
\]

the four open rays are

\[
(0,+),\quad(0,-),\quad(-,0),\quad(+,0),
\]

and the node is `(0,0)`.  Exhaustive finite checks verify the COM covector
axioms

\[
X\circ(-Y)\in\mathcal L
\]

and strong elimination for every ordered pair and every separated
coordinate.  The four-chamber graph is a cycle, and its graph distance is
exactly Hamming distance in the two factor signs.  It is therefore the
expected isometric square, with opposite edges carrying the same factor ID.

All other residual factors have constant nonzero sign on the certified disk,
so appending those fixed coordinates preserves the local axioms.  This is a
complete positive codimension-two test.

## Why smooth pivots do not imply face symmetry

On all of \(\mathbb R^2\), take

\[
q_1(x,y)=y,\qquad q_2(x,y)=y-x^2.
\]

Both have the same constant nonzero pivot derivative
\(\partial q_j/\partial y=1\).  Their complete sign system is

\[
\{(+,+),(+,-),(-,-),(0,-),(+,0),(0,0)\}.
\]

The missing sign `(-,+)` is impossible because
\(y<0<y-x^2\) would imply \(y>x^2\ge0\).  But face symmetry applied to

\[
X=(0,0),\qquad Y=(+,-)
\]

requires

\[
X\circ(-Y)=(-,+),
\]

which is absent.  The failure occurs at a tangency.  Thus even globally
smooth, globally cooriented walls with unit pivot derivatives need not form a
pseudohyperplane arrangement or a COM.

## Why smooth pivots do not imply strong elimination

On the convex open strip

\[
U=(-1/2,1/2)\times\mathbb R,
\]

take

\[
q_1(x,y)=y,\qquad q_2(x,y)=x+y^2-1.
\]

Again each wall has a constant unit pivot:

\[
\partial q_1/\partial y=1,\qquad
\partial q_2/\partial x=1.
\]

The rational points `(0,2)` and `(0,-2)` realize `(+, +)` and `(-, +)`.
Strong elimination in the first coordinate would require a face with sign
`(0,+)`.  Yet `q_1=0` forces `y=0`, and then throughout `U`

\[
q_2=x-1<-1/2<0.
\]

No such face exists.  This model also illustrates that a smooth pivot wall
can have more than one component inside a connected convex domain.

These two examples are implication countermodels only.  They are not claimed
to be residual determinants, to lie in a UOM(4,8) parent cell, or to refute
9DVL.

## What remains to test for the actual factor arrangement

The 26,740-factor census makes a complete exact test finite.  A roadmap for a
fixed parent should attach to every generic chamber its 26,740-bit factor
sign vector and to every wall stratum the corresponding zero signs.  Then:

1. **Codimension two.**  For every nonempty pair intersection, certify the
   parent residence and split it into Jacobian-rank-two and rank-one strata.
   Rank two gives a diamond automatically; rank one requires direct sector
   and face enumeration.
2. **Partial-cube test.**  Check that every generic adjacency flips one factor
   ID and that graph distance equals factor-sign Hamming distance.  Failure
   disproves COM immediately.
3. **Face symmetry and elimination.**  Use the complete stratum sign vectors
   to check both axioms directly.  Pairwise diamonds are necessary but not
   sufficient for these global axioms.
4. **Gated faces.**  If the tope graph passes the partial-cube test, check the
   stronger gated-antipodal-face characterization required for a COM.

The exact row-2599 node completes only the first transverse test.  The factor
census contains equations and duplicate labels, but not a parent-cell
roadmap or the nonempty-intersection stratification needed for the remaining
checks.

Finally, even a COM theorem for the **residual factor arrangement** would not
automatically prove diagonal 9.  Extension-signature feasibility sets are
labeled unions of residual chambers, not known a priori to be COM halfspaces
or gated convex subgraphs.  One would still need either that extra convexity
statement or the already proof-complete antichain-aware tree/cut-SAT test on
the labeled chamber graph.
