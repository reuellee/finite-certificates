# Independent conditional audit: the full affine-fiber gate

Verdict: ACCEPT the conditional topological lemma below. No additional
factor-pair orbit is certified by this file until a globally equivalent
affine presentation is supplied and independently checked.

## Statement

Let B be an open semialgebraic subset of a positive-dimensional Euclidean
space, and let X be an open semialgebraic subset of B times R^3 whose
nonempty fibers C_b are full open convex residence cells. Let

`F_1(b,x)=a_1(b) dot x+c_1(b)` and
`F_2(b,x)=a_2(b) dot x+c_2(b)`

be continuous smooth semialgebraic affine forms in x. Put
`E=X intersection {F_1=F_2=0}`. Then `H_c^1(E;Q)=0`.
The coefficient matrix rank need not be constantly two. If the forms are
only presented after multiplying by units, the claimed equality of loci
must hold on all of X, including coefficient-rank and augmented-rank drops.

## Proof on the rank-two part

Let E_2 be the coefficient-rank-two part. The implicit function theorem
applied in the three x coordinates makes E_2 a smooth submersion with
one-dimensional fibers onto its nonempty-fiber locus U. A feasible point
persists under small base changes, so U is open in B. Each complete fiber
is the intersection of an affine line with C_b, hence one open interval.

Compact-support base change identifies the stalks of R^q p_! Q with the
fiber compact-support cohomology. The interval fibers have only H_c^1,
with rank one. This observation alone about stalk dimensions would not
justify a local-system assertion for an arbitrary map. Here a local
submersion chart supplies the missing natural comparison: choose an open
product box V times I inside E_2 over a neighborhood V of any base point.
Extension by zero from that box gives a map from the constant rank-one
R^1 of its compact-support projection to R^1 p_! Q. On every stalk, the
inclusion of the small open interval I into the complete oriented interval
induces an isomorphism on H_c^1. Consequently that map is an isomorphism
of sheaves over V. Thus R^1 p_! Q is an orientation local system and all
other R^q p_! Q vanish.

No local triviality of the entire nonproper projection was assumed. With
globally ordered affine forms, the cross product a_1 times a_2 orients the
kernel line globally; otherwise the rank-one orientation local system is
sufficient. The compact-support Leray sequence gives

`H_c^1(E_2;Q)=H_c^0(U;L)=0`.

The last vanishing follows because every component of the open positive-
dimensional manifold U is noncompact. A compactly supported locally
constant section is therefore zero, including with a local system L.

## Coefficient-rank drops

Let E_low be the rank-at-most-one part. It is closed in E: rank conditions
depend continuously only on the retained base coordinates. A nonempty
fiber is an affine plane or all of R^3 intersected with C_b, hence an open
convex cell of dimension at least two. Inconsistent affine equations give
an empty fiber, which is allowed. Therefore all stalks of R^q p_! Q for
q=0,1 vanish on E_low, and compact-support Leray gives
`H_c^0(E_low;Q)=H_c^1(E_low;Q)=0` without any smoothness assumption on
the rank-drop base. The closed/open sequence for E_low subset E now proves
H_c^1(E)=0 from the already established vanishing for E_2.

## Original-parent application requirements

For the proposed factor-pair application, B is the normalized seven-parent
realization space, of dimension six, and x is the forgotten parent column.
The full parent-sign residence is convex. Restricting to one connected
component of the original eight-parent space does not cut that residence:
if it contains one residence point, every residence point is connected to
it inside the same parent-sign cell. Thus each fiber is either the whole
residence or empty.

The algebraic gate must show that BOTH original factor equations are
equivalent globally on that full residence to the two affine forms. Every
factor divided out must be a certified nowhere-zero parent-bracket unit.
An identity only along one fixed-parent line, a rational section valid on
one coefficient patch, or deletion of an interior coefficient-rank locus
does not satisfy the gate. Nonempty rank-one/zero fibers and inconsistent
augmented-rank cases must remain covered by the stated equality.

Until that all-parent algebra is frozen and checked, the authoritative
pair-wall coverage remains 8,902 of 9,476, with 574 open.

## Closeout application status

The proposed fixed forget-column8 application did not satisfy this gate.
The independent COLUMN_GATE_REPLAY.json accepts both a complete interval
fiber at the original rational base and a nonsingular conic fiber equation
at a nearby rational base with a certified uniform point. The latter
rules out a global two-affine-form presentation for that fixed projection.
The conditional theorem is retained as a valid sufficient lemma; it has
not removed any additional orbit from the 574-case residue.
