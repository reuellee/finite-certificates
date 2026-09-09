# Shared two-triple pencil: conditional theorem and exact obstruction

Status: `EXACT_ROUTE_COUNTERCERTIFICATE / CONDITIONAL_ESCAPE_PROVED /
AWAITING_INDEPENDENT_REVIEW`.
Base: `ee7c110a0862ec2da961a4b8c9987a0b90e03a0a`.
Surface: `ops/team/ai-d3-shared-pencil-constructor`.

The 1,680-case criterion is exactly equivalent to choosing three witnesses
whose union uses a common label in at most two distinct supporting triples.
It is sufficient for a proper path in the triple bad intersection from
the given point. No globally continuous choice of pencils is needed for
the resulting conditional `H_c^0` conclusion.

The universal pointwise criterion, however, has an exact admissible
countercertificate at the third registered point. All 1,680 choices fail
at chart 0 of `seeat_parent2599_upper178.npz`, with signatures

`14988895318912, 3405195891438080, 40418075143643136`.

`OBSTRUCTION.json` contains an integer strict separator for one blocked
signature at every choice, three full-system Gordan witnesses, and exact
realization/incomparability controls. The independent arithmetic checker
within this lane uses only the Python standard library, reconstructs the
source matrices directly from the NPZ arrays, and passes. Research
acceptance remains with the independent referee. The proposed universal
lemma should be retired if that review accepts the certificate. This
does not refute D3, triple noncompactness, or proper escapes using other
motions or more supporting triples.

## 1. Definitions and the exact finite equivalence

Let `Y=[y_1,...,y_8]` be a uniform real rank-four parent realization in
the project's projective quotient. Keep the original labels and use
colex order on the 56 three-element subsets of `[8]`. Define the normal
`a_I` by

`a_I(Y)^T p = det[y_i,y_j,y_k,p]`, `I={i<j<k}`.

For a signature `sigma`, its signed rows are `sigma_I a_I(Y)^T`. A
Gordan witness is a nonzero vector `w>=0` satisfying
`sum_I w_I sigma_I a_I(Y)=0`; positive normalization makes `sum_I w_I=1`.
Its support includes exactly the indices with strictly positive weights.
Coordinates of weight zero are not supporting triples.

For a label `e`, let `Star(e)={I:e in I}`, with cardinality
`choose(7,2)=21`. For `T subset Star(e)` define

`R(e,T)={I:e not in I} union T`.

At a fixed `Y` and signature triple, the following statements are
equivalent:

1. Some `e` and `T subset Star(e)` of size at most two admit a nonzero
   nonnegative dependence in all three signed systems restricted to
   `R(e,T)`.
2. There are normalized witnesses `w_0,w_1,w_2` for which
   `|Star(e) intersect union_j supp(w_j)|<=2` for some common `e`.
3. One of the `8*choose(21,2)=1,680` choices with **exactly two distinct**
   retained `e`-triples admits all three dependences.

To prove `(1)->(2)`, normalize the three witnesses and take their positive
supports. For `(2)->(1)`, take `T` equal to the incident triples in that
union. Pad any `T` of size zero or one to a pair of distinct members of
`Star(e)` to obtain `(3)`; adding rows cannot destroy an existing
dependence. The implication `(3)->(1)` is immediate. No witness is
required to be support-minimal, a circuit, or strictly positive on all
retained rows. The argument is valid at every derived rank-drop stratum.

The strict alternative used by the certificates has an elementary proof.
For any finite signed row family, a normalized nonnegative dependence
exists exactly when zero belongs to its convex hull. If zero is outside
that compact convex hull, a point of the hull nearest zero has strictly
positive scalar product with every row: its squared norm is a positive
lower bound. Conversely, a vector strictly positive on every row has
positive scalar product with every nonzero nonnegative row combination
and therefore excludes a zero combination. This proof does not assume
full rank or general position of the signed normals.

For fixed `e,sigma`, let `G_(e,sigma)` be the graph on the 21 members
of `Star(e)` whose edge `{I,J}` means that the corresponding restricted
system has a nonnegative dependence. The universal lemma would require

`exists e: E(G_(e,sigma0)) intersect E(G_(e,sigma1))
                 intersect E(G_(e,sigma2)) != empty`

at every admissible triple-bad point. This is the precise finite local
combinatorial statement. The number 1,680 is its local choice count,
not a count of parent components or an end-to-end D3 denominator.

## 2. Pointwise proper escape, including all gauge and rank issues

Suppose the equivalent criterion holds. Pad to a pair `T={I_1,I_2}`.
For each `I` through `e`, write `H_I=span{y_i:i in I}`. Uniformity makes
`H_I` a three-dimensional vector hyperplane containing `y_e`.
The two retained hyperplanes are distinct: equality would put the union
of two distinct triples, which contains at least four labels, in one
three-dimensional subspace, contradicting parent uniformity. Hence

`L=H_(I_1) intersect H_(I_2)` has vector dimension two.

For a version with fewer or coincident imposed planes the dimension is
at least two, so it still has a nonzero projective motion direction.
Coincident retained planes cannot occur for the distinct triples in a
uniform parent, but the dimension argument does not depend on pretending
that two equations are independent when they are not.

Choose five of the seven labels different from `e` as a projective
frame. Choose the order of its first four basis columns to have positive
determinant. A fixed orientation-preserving linear transformation and
positive column scalings put that frame in standard form. These operations
do not vary during the motion because all seven nonmoving columns remain
fixed. The fifth frame column removes the remaining diagonal projective
freedom. Therefore changing the oriented ray of `y_e` in these coordinates
changes the actual projective parent, rather than moving along a gauge
orbit.

Every coordinate of `y_e` in the chosen basis is nonzero. Its sign
`tau_j` is fixed by a parent bracket using three frame columns and `e`.
Normalize its positive ray using

`ell(x)=sum_(j=1)^4 tau_j x_j=1`.

The allowed fixed orthant is the interior of a signed closed simplex
`{tau_j x_j>=0, ell(x)=1}`. Since `y_e in L` and `ell(y_e)=1`, the
intersection `L intersect {ell=1}` is an affine line. The parent-sign
residence domain in that line is

`U={x in L: ell(x)=1, tau_j x_j>0,
       every four-column parent determinant involving x has its original sign}`.

Each determinant is affine linear in `x`. Thus `U` is a nonempty open
convex subset of that line, contains the initial point, and is bounded
by the signed simplex. It is a bounded open interval of positive length.
Choose either endpoint. Every point before it is uniform with exactly
the original parent signs. At the endpoint at least one strict inequality
becomes equality; otherwise all would remain strict in a neighborhood
and it would not be an endpoint. A coordinate-zero equality itself is
a parent bracket zero using three frame columns. Therefore this endpoint
is a genuine nonuniform parent degeneration.

The bounded signed-simplex construction avoids an arbitrary affine
chart's potentially removable boundary. Five nonmoving frame labels
stay fixed and in general position throughout the limit. The endpoint
cannot be repaired into an interior uniform point by changing that frame.

For every retained supporting triple `I` through `e`, the moving column
stays in the original `H_I`. At every finite interior time its three
columns are independent, so

`a_I(Y(t))=c_I(t) a_I(Y(0))`, with `c_I(t)>0`.

Indeed the normal is nonzero and on a fixed one-dimensional normal line;
the scalar varies continuously from `1` and cannot pass through zero
while the parent is uniform. Normals of triples not containing `e` are
constant. The same argument works for a support whose normal matrix was
already rank-deficient: multiplying its columns by positive numbers
preserves its rank and its dependence. No chosen maximal minor, full
witness-polytope dimension, or rank-generic chart is required.

Transport each of the three witnesses separately by

`w_(j,I)(t)=[w_(j,I)(0)/c_I(t)] /
                    sum_K [w_(j,K)(0)/c_K(t)]`,

where `c_I=1` for nonincident support rows. Every denominator is positive.
Zero initial weights remain zero; nonzero initial weights remain positive
at finite times; the signed kernel equations and normalization hold
identically. We need not prescribe the limiting weights. Some may become
zero or a witness rank may change at the parent endpoint. Residual rank
drops elsewhere in the full normal array during the path are harmless.

Reparameterize the interval from the starting point to its chosen endpoint
by `[0,infinity)`. Its limit in the signed compactification is nonuniform,
so every compact subset of the uniform parent quotient has compact
preimage. The path is proper and lies in all three bad loci at every
finite time. This proves the conditional proper-escape lemma at the
individual starting point.

If the criterion held at **every** triple-bad point, this would imply
`H_c^0(B_0 intersect B_1 intersect B_2;R)=0` for every coefficient ring
`R`. A degree-zero compactly supported cohomology class is a compactly
supported locally constant function. If nonzero at a point, it stays
nonzero along the connected proper path from that point, which cannot
be contained in a compact support. This is a contradiction. There is
no requirement to choose the label, pair, or witnesses continuously as
the starting point varies. This argument gives no pair-`H_c^1` contraction
or coherent chain homotopy.

## 3. Universal proof attempt and its exact stopping point

The construction above uses a genuine actual-parent identity:

`a_I(Y)^T y_e=0` whenever `e in I`.

It explains why two retained incident planes leave a projective line.
The common-parent exterior identity also presents all witness forms in
`ker(Lambda^3 T_Y)=ker(T_Y) wedge Lambda^2 R^8`.
These facts by themselves do not supply a common graph edge in section 1.

The attempted constructive route was to start with minimal positive
circuits in the three signed normal systems and use circuit exchanges
inside their normalized nonnegative kernel polytopes to reduce one
label's union incidence to two. Each individual witness can be reduced
to at most five rows by taking a vertex of its normalized polytope, but
three independent such reductions give no common light label. An
exchange which is allowed for one signed orthant may not leave witnesses
available for the other two at the same label and pair. The missing
step would have been a sign-compatible exchange theorem strong enough
to force the three-graph edge intersection. It is stronger than the
unsigned Koszul spanning identity or ordinary circuit elimination.

I tested this step on the three registered points using the exact actual
normal matrices. Linear programming proposed supports; a support was
accepted only after reconstructing its dependence over `Q` and verifying
it against the original integer rows. This found the expected positive
control but found no positive shared pair for the flow triple at upper
chart 0. Solver failure was not treated as a negative proof.

The search was then replaced by explicit exact dual certificates: for
each of the 1,680 pairs, find a signature and integer vector strictly
positive on its 37 retained signed rows. All were found and verified.
This shows that the missing sign-compatible exchange conclusion cannot
hold on the stated universal domain. GP validity and the actual common
parent do not force the proposed graph edge intersection. No additional
universal search is warranted after this certificate, pending independent
review.

The count-of-triples restriction is also stronger than every possible
one-label pencil condition. Three or more incident support planes can
still share a projective line, for example when their triples have a
common second label. The present obstruction excludes witnesses using
at most two incident triples; it does not exclude all witnesses whose
incident normals have rank at most two, or paths that first move other
labels. This observation is a scope distinction, not an authorized
successor search or a new theorem claim.

## 4. Exact registered-cohort outcomes

| Registered point | Outcome established in this lane |
| --- | --- |
| Shatter pattern 0, bits `(0,4,3)` | Positive shared-pencil certificate with `e=1`, retained triples `134,127`, and three exact nonnegative witnesses. This lane certifies this pair; it does not claim a complete count of positive pairs there. |
| Upper178 chart 7, same signatures | Ineligible: block 2, the original bit-3 signature `58432476850159616`, has an exact integer strict-feasibility vector for all 56 rows. |
| Upper178 chart 0, registered flow triple | Complete negative certificate: all 1,680 choices have a blocked signature with an exact integer strict separator on all 37 retained rows. |

For the negative point, the three full systems are bad by exact normalized
nonnegative dependences. All 70 parent brackets are nonzero, and all
signature Grassmann--Pluecker sign relations pass.

Admissibility is bound using pre-existing stored assignments, not new
parent samples. At upper178 chart 3, signature 0 is feasible and
signatures 1 and 2 are bad; at chart 14, signature 1 is feasible and
the other two are bad; at chart 2, signature 2 is feasible and the
other two are bad. Each feasible point is checked on all 56 strict
inequalities; each badness claim has an exact nonnegative dependence.
Every control parent has the same 70-bracket sign pattern as the
negative parent. Thus each region is nonempty, each is proper because
all are bad at chart 0, and all six ordered failures of inclusion are
certified. Their uniform rank-four extensions are actually realized at
their good controls, not merely abstract GP-valid signatures.

At each negative choice `(e,{I,J})`, exactly 35 triples omit `e` and
two retained triples contain it, so the checker verifies 37 strict
inequalities. The explicit separator gives a contradiction to every
nonzero nonnegative dependence on those rows by taking their scalar
products. Exhaustive coverage is established by set equality against
the independently generated 1,680 choices; it does not rely on the
completeness of the numerical search.

## 5. Verification, provenance, and handoff scope

Run the standalone exact replay:

`python -B ops/team/ai-d3-shared-pencil-constructor/verify_controls.py`

It requires no NumPy, SciPy, SymPy, LP solver, or producer module. A
narrow standard-library NPY reader extracts the integer source matrices
from the NPZ files. The checker independently constructs colex triples,
normals, all parent determinants, and all GP sign tests. It verifies:

- three exact restricted witnesses for the mandatory positive control;
- the full strict-feasibility certificate making chart 7 ineligible;
- 1,680 distinct negative choices and 62,160 strict integer inequalities;
- three full-system Gordan witnesses for the negative point;
- three realized feasibility controls and all six incomparability bindings.

The minimum strict integer separator margin is `6858251431715`; no
tolerance is used. The 11,340 GP checks are 1,260 relations for each
of the three signatures at each registered parent point, including
repeated checks where parent/signature data coincide. Source matrices
and signatures are checked against the registered NPZ arrays.

`search_controls.py` and `certify_obstruction.py` are exploratory proposal
producers, kept separate from `verify_controls.py` and the exact JSON
certificates. The producers use Python 3.11.9, NumPy, SciPy 1.17.1,
and SymPy 1.14.0 at

`C:\Users\reuel\AppData\Local\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0\python.exe`.

No environment was changed. Numerical scans only locate already stored
assignment controls; all saved mathematical assertions are checked
exactly. `SOURCE_MANIFEST.json` pins the base and source bytes, and
`RESOURCE_ACCOUNTING.json` records actual storage and the conservative
wall-time accounting. The old source lane and canonical state remain
unchanged. No active falsifier artifact was inspected or imported. The
coordinator communicated its preliminary independent result after this
lane's unsuccessful positive search; all integer separators and
admissibility controls here were then reconstructed from source inputs
without using that lane's certificate.

Proposed decision after independent acceptance: `RETIRE` the universal
shared-two-triple pencil predicate. Preserve the conditional escape
theorem as a valid sufficient criterion. D3 remains `2/9`, with both
the pair incidence invariant and triple escape invariant open. This
certificate is a counterexample to the selected route, not a compact
triple-bad component or a 9DVL counterexample. Stop this bounded search
at the exact endpoint; do not enlarge the cohort or silently weaken the
predicate to evade its refutation.
