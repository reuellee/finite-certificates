# Direct triple-bad proof track

## Result and original status

The original statement `H_c^0(B_0 intersect B_1 intersect B_2;Q)=0` remains
open. This track closes no original obligation, changes no source-orbit
count, and does not advance the ledger from2/9.

A new exact example separates three proposed proof restrictions from the
original geometry. It is an **actual proper pairwise incomparable triple**,
not an abstract or tangent model. At its common bad boundary point:

1. the three weak-primal cones are three independent rays;
2. each full normalized Gordan witness polytope is a singleton;
3. the unique support union has minimum parent-label degree three; and
4. a natural fixed-three-weak-point height contraction has no motion after
   projective scale is removed.

Despite all four restrictions, the inherited affine-height argument proves
noncompactness of the selected common factor-zero locus on every uniform
parent component. Thus the example is not a compactness or9DVL counterexample.
It shows why a proof must permit weak-primal points to move, and why neither
common weak points nor light-label witness choices can be universal
prerequisites.

## 1. Exact original-scope example

Use the normalized parent matrix

```
[1, 0, 0, 0, 1,    1,  1,    1]
[0, 1, 0, 0, 1, 13/3, 31, 94/9]
[0, 0, 1, 0, 1,    7,  5,    2]
[0, 0, 0, 1, 1,    6, -4,   -2].
```

All70 parent brackets are nonzero. The project **colex** signature integers
(bit1 means a positive sign) are

- `5019905080784346`;
- `68833058600159780`;
- `59311597535541546`.

The fixture stores both lex and colex encodings, explicitly declares its
row order, and the verifier checks the conversion. Earlier producer messages
used lex encodings; those are not project signature IDs.

The exact zero-normal supports and weak rays are:

| block | zero-normal support | positive generator of weak ray |
|---|---|---|
|0|123/145/246/357|`(-1,-7,-7,0)`|
|1|127/158/234/357|`(0,24,5,-4)`|
|2|236/248/456/578|`(-9,-14,-18,-54)`|

For every block the four signed normals have rank3 and a strictly positive
Gordan dependence. Their dependence forces every weak-primal vector to
annihilate all four rows. The rank makes that common kernel a line, and at
least one strict signed value selects the displayed ray. The three ray
generators are linearly independent, so their intersection contains only0.

Conversely, pair a nonnegative Gordan witness with the displayed weak primal.
Every row having strictly positive signed value must have zero witness
weight. Exactly the four displayed rows have zero value. Their rank3 and
positive dependence therefore imply that the **full** normalized witness
polytope is a singleton. This is not merely a claim about a selected circuit
inside a larger polytope.

The union of those supports has label degrees

`(4,6,4,5,5,3,3,3)`.

Thus no alternate witness choice at this point can produce a degree-zero,
degree-one, or degree-two label.

## 2. Actual validity, properness, antichain, and boundary

`ACTUAL_UNIQUE_HARD_THREE_BOUNDARY_SIGNATURES.json` contains three exact
nearby parent matrices and private vectors. Anchor `j` realizes signature
`j` strictly on all56 derived normals while the other two signatures retain
positive four-circuit witnesses. All70 parent signs agree with the center.
Each anchor path changes only the second matrix row, so every parent bracket
is affine along the straight segment; agreement of the endpoint signs proves
the entire segment remains in the same connected parent component.

The anchors prove individual realizability and both directions of every
incomparability. The common bad point proves properness.

The stronger assertion that the center is a topological boundary point is
also checked. `BOUNDARY_CURVES.json` gives polynomial private curves `p_j(t)`
of degree at most3 along the corresponding straight parent paths. On the
four selected rows,

`N_j(t)p_j(t) = t diag(1,2,3,5) sigma_j`,
`det N_j(t) = t`.

The stdlib verifier proves these polynomial identities by five evaluations
of degree-at-most4 polynomials. Every one of the168 signed-normal polynomials
has positive first nonzero coefficient. They are all strictly positive for
one sufficiently small positive interval, so each signature is feasible
arbitrarily close to the center. The limiting private vector is a positive
multiple of the displayed weak ray.

## 3. Fixed-three-weak-point height test

Let `U` be the span of the three weak rays. The exact covector

`ell=(-1414/167,-18/167,220/167,1)`

annihilates `U`. Choose

`v=(-167/122,-167/61,-501/122,-334/61)`,

so `ell(v)=1`, and write each parent column `y_k=x_k+v h_k` with `x_k in U`.
Freeze the projected columns `x_k` and the three weak-primal points. The
12 selected zero-incidence equations are linear in the eight heights. The
exact matrix in `MULTIWEAK_HEIGHT_GATE.json` has rank7 and kernel spanned by
the current height vector `h_k=ell(y_k)`.

Scaling that height vector is the projective linear transformation fixing
`U` and scaling `v`; it changes no normalized parent realization. Thus this
particular height projection supplies no non-gauge motion. Rank7 also holds
on a nonempty Zariski-open set of transverse directions, since a7-by7 minor
is nonzero at the displayed direction. Exceptional directions have not been
classified. This is not a no-go theorem for every possible contraction or
for motions allowing the weak points to change.

An initial direction equal to parent column1 gave a two-dimensional kernel;
one dimension was the extra positive scaling of that parent column and the
other was global height scale. That apparent escape was rejected as gauge.

## 4. A surviving argument that settles this example

`AFFINE_HEIGHT_ESCAPE.md` gives the conventional parent-contraction argument,
including all rank drops. A parent label occurring at least twice in each
of three residual occurrence quartets makes their determinants jointly affine
in the three normalized lift heights after contraction by that parent.
The square-affine compactness argument then proves that the common zero set
has no compact connected component.

Parent label2 occurs twice in every quartet above. Thus this argument covers
the selected factor triple uniformly, despite the frozen-witness and
frozen-weak-point rigidity.

At the displayed six quotient coordinates the three determinant equations
in the height coordinates `(a,d,g)` are

`d-31`, `-16d+45g+26`, `7a-48d+150g-109`.

Their Jacobian determinant is315. The fixed-base fiber is a point; escape
comes from the quotient base. If that coefficient rank drops elsewhere, the
full positive-dimensional affine residence fiber is a closed noncompact
subset of its connected zero-set component, supplying the other case.

This square-affine argument is **inherited**, not a new proof method.
`inputs/DIAG3_TRIPLE_SEQUENTIAL_AFFINE_COMPRESSION.md`, Section1, explicitly
states its two-coordinate version and cites `DIAG3_AFFINE_FIBER_FRONTIER.md`.
The dimension-three proof is the same argument. No new census count or
original obligation is credited to this application.

## 5. Remaining exact step

A common-weak-primal resolution can handle only strata where a common weak
point exists. The example proves that even genuine simultaneous boundary
strata need not have one, and unique witness supports need not offer a light
label. A successful direct global proof must cover these distinct-weak-point
strata while permitting their weak points to move, and also retain the
strictly bad strata where weak-primal cones may be empty.

The smallest useful next discriminator is a stratum outside the inherited
common-affine parent-contraction coverage: determine whether its weak-point
incidence projection admits a nontrivial full convex motion after every
projective gauge is removed, or prove that its rank-drop/specialization maps
supply the needed proper escape. Requiring every stratum to use the same
weak point or the same witness support is already disproved by the new
original-scope example.

No claim is made that this remaining discriminator terminates or that the
original statement follows from local motion alone.

## Replay and audit

Run

```
python triple/verify_unique_hard_boundary.py
python triple/verify_boundary_curves.py
```

The arithmetic uses only Python integers and `Fraction`. The first replay
checks three corrupted fixtures and rejects all three. The second replay
checks actual all-small-parameter feasibility. SymPy is used by the optional
producer scripts, not by the acceptance checkers.

Independent referee review was requested and is pending when this note was
written. Source encoding and the boundary-closure issue identified by the
referee were corrected before freezing the final fixture.
