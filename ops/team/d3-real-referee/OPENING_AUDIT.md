# Independent opening audit of cefc495

**Verdict: ACCEPT the auxiliary graph, genus-one, and complete fixed-base
slice statements, with the exact scope below. No third diagonal or source
orbit is closed.** No actionable defect was found in the mathematical
claims of `ops/team/d3-bracket-chart/REPORT.md` at the requested revision.
This supplies the previously absent independent AI referee acceptance of
those claims; it does not retroactively classify that investigation as
converging.

Base commit: `cefc495b27247c4a76f88bce04978422161f7ce9`.
Base tree: `c49c2e6625f3ee76d77cc263897366dcf7e037c2`.
Role: independent referee, not a discovery worker.
Owned surface: `ops/team/d3-real-referee/`.
The opening audit was completed within its 20 active minute ceiling.

## Inputs and independence

The new replay `audit_cefc495.py` imports no repository producer, verifier,
or acceptance routine, and does not read the candidate's arithmetic output.
It uses standard-library sparse integer polynomial arithmetic, rational
Gaussian elimination for the Sylvester determinant, direct determinant
expansion, and rational sign isolation. It requires no third-party package.

Two coefficient/data inputs are pinned and checked before use:

| Input | SHA-256 |
| --- | --- |
| `ai/omreal/data/DIAG3_triple_fullspace_critical_h1.json` | `c9244a47ded5736e7afe724a9914e75631a22b78653442e88c14f5c397919eb8` |
| `ai/omreal/data/DIAG9_GRAPH_global_factor_census.npz` | `3984ce87e11fd59d804e59568177248e218cd1c7bb07aae0a9f9f746858728bc` |

The source contains 59 equations, including the height-critical minors.
Only the first three factor equations define the source audited here; the
minor equations are **not** imposed. This distinction is essential.

The referee independently decodes the NPZ/NPY data rather than calling the
census loader. The three equation polynomials equal census factors
5563, 16134, and 19284 coefficient for coefficient. The colex-indexed
occurrence map sends them under the recorded permutation to
4373, 5563, and 23221, respectively, hence the recorded canonical unordered
row `(5563,4373,23221)`.

For stronger provenance, one original four-normal determinant is rebuilt
from the normalized parent matrix for each factor. Their triple labels are:

| Factor | Four derived-normal parent triples |
| --- | --- |
| 5563 | 123, 145, 246, 378 |
| 16134 | 126, 257, 367, 458 |
| 19284 | 245, 157, 348, 168 |

These determinants have 4, 40, and 16 terms and equal the respective
primitive factor polynomials up to scalar normalization. None of these
three chosen occurrences strips an additional parent unit. The referee did
not rebuild the complete 84,840-occurrence global census; the acceptance
above is for these three original equations and their recorded transport.
The equation source is an algebraic residual factor presentation, not an
extension-signature-labeled triple-bad component or an exhaustive component
index.

## Accepted graph equivalence

Let `U` be the open normalized parent domain where all 70 four-column
brackets are nonzero. The exact source is
`S = {q5563=q16134=q19284=0} intersect U`.
The direct normalized parent matrix is `[I4 | (1,1,1,1), (1,a,b,c),
(1,d,e,f), (1,g,h,i)]`.

The replay derives `q1=i*d-[b(i-f)+fg]` and, after this first solve,
`i*q2=A*a+B`, `i*q3=C*a+D`. It verifies
`A=i(f-1)(h-1)(bf-ce)` and `N=A*D-C*B` without dividing polynomials.
The denominators have the following direct parent attachments:

| Factor | Parent bracket, up to a nonzero sign |
| --- | --- |
| i | 1238 |
| f-1 | 2357 |
| h-1 | 2458 |
| bf-ce | 1267 |

Thus for every point of `U`, the source equations are equivalent to
`d=[b(i-f)+fg]/i`, `a=-B/A`, and `N=0`, with all 70 original bracket
inequalities pulled back through this graph. No additional rank hypothesis
is used. The resulting graph is a homeomorphism of the corresponding real
semialgebraic domains. Neither equation denominators nor parent
inequalities may be discarded on a nonuniform boundary.

## Accepted genus inference

The reconstructed `N` has 389 terms and bidegree `(2,2)` in `(c,e)`;
its discriminant in `e` has 3,257 terms and degree four in `c`.
The coefficient identity relating `N` to the completed square is checked
exactly. Under the stated base specialization, `N=(64/49)F`, and the
generic discriminant specializes to `(64/49)^2 W`.

The exact specialized quartic discriminant is
`4649793772367457417206802405651256329633792`, obtained from the independent
7-by-7 Sylvester determinant. This proves a nonzero generic resultant over
`Q(b,f,g,h,i)`. Therefore the generic quartic is squarefree and not a square
even over the algebraic closure of that field. Any nonconstant common
factor of its three quadratic-in-e coefficients would divide the
discriminant twice, so no omitted vertical curve component undermines the
function-field statement.

For the smooth projective model, the double cover of the c-line has four
simple finite branch points. With `t=1/c` and the square-root coordinate
scaled by `t^2`, the equation at infinity has two distinct nonzero values;
it is unramified there. Characteristic zero makes the cover separable and
the four ramification indices equal to two.

The [Stacks Project, Section 53.12, Riemann–Hurwitz](https://stacks.math.columbia.edu/tag/0C1B)
was checked directly on 2026-09-05. Its formula for smooth proper separable
curves gives `2g-2=2(-2)+4=0`. Applying it to a putative nonconstant map
from the projective line gives an impossibility because ramification has
nonnegative degree. These applications meet the source's smoothness,
properness, separability, and constant-field conditions after passing to
an algebraic closure.

Consequently the generic fixed-base curve has geometric genus one and
admits no nonconstant rationally parameterized arc. The same applies to
the stated squarefree specialized curve. The conclusion is about the
smooth projective model of this curve, not an assertion that a generic
fiber possesses a rational point, that the six-dimensional total source
is nonrational, or that other projections and semialgebraic escapes fail.

## Accepted real entire-slice noncompactness

The fixed base is `(b,f,g,h,i)=(-23/7,-3,-1,2,4)`.
The replay derives `d=-5` and the report's complete rational formula for
`a`. The leading quadratic coefficient `539c^2-28c+1449` is everywhere
positive because its discriminant is `-3123260`.

Independent rational intervals isolating the four real roots of `W` are:

| Root | Interval |
| --- | --- |
| r1 | (-67/25, -267/100) |
| r2 | (-11/5, -219/100) |
| r3 | (-131/100, -13/10) |
| r4 | (43/100, 11/25) |

There is a sign change on every interval; degree four and the nonzero
discriminant exhaust the roots. The two quadratic graphs therefore join
into exactly two noncompact outer components and one compact middle
oval. At simple endpoint roots the affine curve is smooth; away from them
its e-derivative is nonzero. No additional affine branch can occur because
the leading coefficient never vanishes.

The two displayed rational source points are independently checked against
all original equations and all 70 brackets. Their common c-coordinate
`-27/14` lies between `r2` and `r3`; their distinct e-coordinates are the two
roots at that c. Their bracket `1346=a` has opposite signs. The derivative
`F_e=5463/4` at the first point also proves nonvacuous parent-interior
geometry that persists locally as the base varies.

On the complete oval, either `7ce-69` vanishes, removing a genuine parent
unit, or the graph for a is continuous and a vanishes between the two
points. Thus no uniform parent sign cell contains the complete oval.
Intersecting each smooth real curve component with a uniform parent cell
is open. An open connected subset of either noncompact outer component is
an interval; an open connected proper subset of the circle is also an
interval. Consequently **every connected component of the complete source
slice in every uniform parent sign cell it meets is noncompact**. The
source slice is closed relative to that parent cell, since it is defined
by polynomial equalities and fixed coordinates. Hence the missing ends
are genuine parent boundary or coordinate infinity, rather than an
artificial closed-box endpoint.

This does not prove the result for another base, a singular fiber, an
entire source component, or any original triple-bad component. A compact
full-source component can meet this one slice trivially. No full-source
residual row is removed. The alternating direct-sum pair Hc1 map is not
computed. The accepted scope gives no numerical theorem progress beyond
2/9 and does not close any of the seven canonical obligations.

## Hostile controls, replay, and classification

The independently implemented acceptance predicates reject ten mutations:
wrong graph-pivot sign; a denominator not equal to any parent unit; reversed
bracket orientation; corrupted specialized equation; repeated-root quartic;
duplicate root interval; a nonuniform zero source point with zero graph
denominators; an off-source point; repetition of the same oval point; and
same-sign values incorrectly presented as an oval cut.

Run from the repository root:

```text
python -B ops/team/d3-real-referee/audit_cefc495.py
```

`OPENING_ARITHMETIC.json` records the exact reconstructed values and all
canary outcomes. Arithmetic result: **finite exact computation, ACCEPT**.
The graph, genus and real topology deductions above: **proved within their
explicit source and slice quantifiers, ACCEPT**. Global D3: **inconclusive**.
Independent review found no repair necessary. The initial referee
implementation used lexicographic triple indices; the provenance check
rejected them, and the independent decoder was corrected to the
repository's stated colex convention before acceptance.
