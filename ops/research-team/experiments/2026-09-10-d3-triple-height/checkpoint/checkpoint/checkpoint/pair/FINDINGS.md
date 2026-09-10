# Pair track: a finite sufficient route and a universal geometric subfamily

Status: the original pair restriction map remains OPEN. Diagonal3 remains
OPEN; ledger2/9. The statements below concern full residual-factor zero sets,
not their generic chamber pieces. They do not claim any original bad-component
count, all-parent cell cover, or completed diagonal.

## 1. A finite sufficient endpoint for the original diagonal

Let X be any normalized parent component in the original scope. Let S be any
finite set of extension signatures (in particular any admissible triple).
For each signature sigma let A_sigma be its finite set of circuit-aligned
primitive residual factors, as defined in
DIAG3_TRIPLE_FACTOR_REDUCTION.md §1. Put

    B = union_(sigma in S) B_sigma,
    W = union_(f in union_sigma A_sigma) H_f,
    H_f = X intersect {q_f=0}.

The fixed-unit circuit theorem gives W subset B. The all-strata persistence
dichotomy gives boundary_X(B) subset W: a point of B not on W has a minimal
positive circuit that is strict5 or structural, hence is interior to its
bad block. Thus B\W is clopen in U=X\W, including on simultaneous walls and
rank strata. There is no choice of witness section in this argument.

Known vanishing of single-wall Hc1 and pair-wall Hc0 implies Hc1(W;Q)=0 by
the finite closed-cover Mayer--Vietoris spectral sequence. The parent
vanishing Hc2(X;Q)=0 then gives Hc2(U;Q)=0 by the open/closed sequence for
W subset X. The clopen summand B\W therefore has Hc2=0. The open/closed
sequence inside B proves a natural injection

    Hc2(B;Q) -> Hc2(W;Q).

Consequently the following two geometric endpoint hypotheses suffice for
original diagonal3, with all original signature quantifiers:

P. Hc1(H_f intersect H_g;Q)=0 for every two distinct global factors.
T. Hc0(H_f intersect H_g intersect H_h;Q)=0 for every three distinct factors.

Indeed single-wall Hc2 is known, and P,T remove all remaining total-degree2
terms of the finite closed-factor-cover spectral sequence for W.

This is a sufficient route, not an equivalence or a claim that P alone solves
original D. T must range over ALL triples among active factors, including
triples aligned to the same signature. The prescribed-signature three-color
matching refinement does not suffice for this argument without a new proof.
The universal79,102,449-orbit triple program is strong enough. P has the
source-derived9476 unordered relative-label factor-pair orbit denominator.
Source DIAG3_PAIR_DIFFERENTIAL_ENDS.md correctly disproves sufficiency of
pair/triple Hc0 plus boundary-union Hc1; our additional hypothesis P is
precisely one degree stronger and excludes its cylinder countermodel.

No claim is made that every factor pair appears in an admissible original
signature triple. The stronger quantification is deliberate and finite.

## 2. Two-dimensional support-plane quotient lemma

Choose one global wall-circuit occurrence U for f and V for g. Localization
occurrences have3 triples; ordinary occurrences have4. Their rank and fixed
unit circuit coefficients are inherited from verify_derived_wall_sides.py and
DIAG3_SINGLE_BAD_TWO_SKELETON.md §4, and remain valid over the whole factor
wall, including other-factor intersections. Let H=H_f intersect H_g and let
d_e count the DISTINCT derived triples in U union V containing label e.

If (a) some d_e<=1, or (b) at least two labels have degree2, then

    Hc^q(H;R)=0 for q=0,1 and every coefficient ring R.

Proof. If d_e=0, forget e while retaining all other columns; the residence
fiber is an open convex projective3-cell. If d_e=1, additionally retain the
normal ray of its one incident plane; its residence fiber is an open convex
projective2-cell. In either case use a projective frame on5 nonmoving labels.

For case(b), take labels e,l and retain the other6 columns and the normal
rays of ALL selected incident planes. The possible e lies in the fixed
intersection of its two distinct incident planes; similarly l lies in a
fixed projective line. Different selected triples have different planes in
any uniform parent. The original point supplies a nonempty open neighborhood
in the product of the two lines. A triple containing both moving labels is
still contained in its retained fixed plane, and uniformity guarantees it
spans that plane until a genuine parent boundary. Thus simultaneous motion
has exactly the two independent residence parameters; a shared plane does
not impose a third equation.

Choose affine line coordinates using the nonmoving frame. Each parent
bracket is affine in either moving column separately, hence is bilinear in
the two parameters. Every nonempty vertical residence section is an open
interval. A connected component projects to an open interval. No vertical
section meets two components, since the whole section is an interval.
Locally persistent sections and a partition of unity give a continuous
section on the projected interval; straight-line vertical interpolation
contracts each component onto that section. Each fiber component is therefore
a contractible open2-manifold. This is precisely the global two-pencil
quotient proof in DIAG3_SINGLE_BAD_TWO_SKELETON.md §2, applied to U union V.

For all these quotients, selected normals change only by positive scalars.
Inverse positive rescaling of circuit weights preserves both normalized
positive dependences. Hence f=g=0 is preserved throughout the residence
fiber. Conversely the retained nonmoving columns and plane rays impose only
the stated residences, so the restriction to H has those same full fibers.
Fiberwise compact-support cohomology is zero in degrees0,1. The standard
compact-support Leray sequence for the semialgebraic quotient gives the
claimed global vanishing. No orientation trivialization is needed to infer
vanishing below fiber dimension2. All chart transitions are included by the
global frame normalization; finite exits are parent nonuniformity, and
projective infinite parameter ends are genuine parent ends. An artificial
bounded parameter box is never declared relative infinity. QED.

This lemma is a new application of the inherited two-pencil theorem, not a
new proof of the latter. It proves cohomology vanishing, which is strictly
stronger than inherited factor-pair component noncompactness.

## 3. Universal factor-kind families satisfying the lemma

The six global factor kinds are36,38,48,49,50,51. Choose the following
canonical global occurrences; all labels may be simultaneously permuted.

|kind|wall-circuit support|degree information|
|---|---|---|
|36|123/345/367|3 triples|
|38|345/678/12a/12b, a,b distinct in{3,...,8}|15 equivalent occurrences|
|48|123/145/246/356|maxdegree2; two omitted labels|
|49|123/145/246/357|maxdegree2; one omitted label|
|50|123/145/246/378|maxdegree2|
|51|123/145/267/468|maxdegree2|

The kind38 occurrence identity is the source theorem in
DIAG3_PAIR_FACTOR_ROOT_SWITCH.md (the pair of core normals is345,678 and
there are six12k rays). It is an identity of full global factor walls with
nonzero parent-unit circuit coefficients, not a sampling assertion.

* A pair containing kind36 uses at most7 distinct triples, hence at most21
  incidences. Unless a label has degree<=1, all degrees are at least2. If at
  most one were2, total incidence would be at least2+7*3=23, contradiction.
* A pair containing kind48 and no kind36 uses two supports each of maximum
  degree2. At the two labels omitted by the kind48 occurrence, union degrees
  are at most2. Either one is<=1 or both are2.
* For49+49, if the omitted labels coincide the union omits that label. If
  different, each omitted label has union degree at most2. Again the lemma
  applies.
* For a pair containing kind38 and no kind36, the other support has maximum
  degree2 and total incidence12. In canonical kind38 coordinates, its
  occurrence P_ab has degrees2 on1,2,a,b and1 on the other four labels.
  Choose a,b so the componentwise upper bound deg(P_ab)+deg(V) has a label
  <=1 or two labels<=2. The exact266-degree-pattern certificate below proves
  existence for every labeled degree vector in{0,1,2}^8 with sum12. It is
  independent of realizability and of whether the supports share rows.
  Shared rows can only decrease union degrees, preserving the criterion.
  The choice is made from the fixed support labels, once for the entire
  factor pair, so no continuity/selection problem is introduced.

Therefore P is PROVED (independently accepted) for every pair
containing36,38,or48 and every49+49 pair, over every parent and all relative
labelings, including empty/nontransverse/rank-degenerate factor intersections.
No original D claim follows until the remaining factor pairs and T are proved.

The remaining candidate kind pairs are exactly

    (49,50), (49,51), (50,50), (50,51), (51,51).

This is a family list, NOT a count of original components or of the9476
relative-label pair orbits. We have not yet counted those orbits by kind.

## 4. Exact replay and limits

Run python pair/verify_factor_pair_h1_templates.py. It source-checks the
canonical support table, validates the incidence bound, produces an explicit
outer-pair choice for all266 possible labeled maximum-degree2 vectors of
sum12, and records source SHA256 identities. These266 are exhaustive degree
patterns for the selection lemma; they are not a sample of parent cells.

The verifier also supplies a combinatorial discriminator for a harder family:

    P=123/145/246/378, Q=567/158/268/347.

Both are type50 occurrences and the union is3-regular. This defeats any
claim that the present support-plane quotient works automatically for all
remaining pairs. Nonemptiness of this actual pair-wall intersection has not
yet been certified, so this is only a support-geometry canary, not a
counterexample to P or to original D. The exact next step is to produce a
uniform rational point on these two walls, then test a2D motion allowing
some selected planes to rotate while retaining the two factor equations.

The earlier3000 distinct relative-label type49 checks were a discovery
regression only and are superseded by the universal omitted-label proof.
Neither those checks nor the new266 patterns are used as a census of the
full parent/signature theorem scope.

## 5. Ruled-quadric residence fibers (independently accepted)

Let C be the full projective residence3-cell of one parent column e after
fixing the other7 uniform parent columns. All70 prescribed parent signs are
retained. Suppose a selected ordinary wall support contains e in exactly2
triples eab, ecd; the other2 selected normals are u,v, from triples not
containing e. Let A=line(ab), D=line(cd), and L=ker(u) intersect ker(v).
Assume a,b,c,d are distinct and A is skew to L. Uniformity makes A,D skew.
Then the full wall fiber

    E={e in C: det(n_eab,n_ecd,u,v)=0}

has Hc0(E;R)=Hc1(E;R)=0 for every coefficient ring R.

Proof. A parent column e in C is never on A. The plane span(e,A) meets L
in a unique point q(e), because A,L are skew. Restriction of the two moving
normals to L identifies the determinant equation with

    det(e,c,d,q(e))=0.

Choose any other fixed parent label z outside{a,b}. Since A,L are skew,
the plane span(a,b,z) meets L in a single point q0. Uniformity gives
[eabz] !=0, so q(e) !=q0. Thus q takes values in an affine line
L\{q0}, not a projective circle. This uses an actual parent nonzero bracket,
not an artificial cut through the allowed domain.

If L=D, the second displayed equation is automatic and E=C, so the claim
follows from the residence3-cell. Otherwise L intersects D in at most one
point q*. For q !=q*, the permitted e lie in the projective line

    r(q)=span(q,A) intersect span(q,D).

Both planes are defined and are distinct because A,D are skew. These lines
vary continuously as a projective-line bundle over L\{q0,q*}. A fixed
parent hyperplane, avoided by all e in C, supplies a continuous affine chart
on each r(q) which meets C. Its intersection with C is an open interval,
or empty, because C is a convex projective residence cell. The allowed
parameter set is open in this line bundle, hence its q-image is open.
Every component of the allowed set projects to an interval; a connected
vertical fiber cannot meet two components. Local sections and affine
interpolation contract that component to a section over its interval.
Thus the regular part E_reg consists of contractible open2-manifolds,
and Hc0(E_reg)=Hc1(E_reg)=0.

At the possible point q*, the second equation is automatic because q* in D.
The entire exceptional fiber is C intersect span(q*,A), an empty set or an
open convex2-cell. It is closed relative to E; it has Hc0=Hc1=0. The compact-
support open/closed sequence proves the assertion for E. This retains the
singular quadric specialization instead of deleting it. QED.

Application to any pair49+50 or49+51. Choose the canonical type49 wall
occurrence, after relabeling, and let e be its omitted parent label. Its
factor equation is independent of e. Use a global parent frame among5 of
the7 retained labels and project the pair wall by forgetting e.

For the other type50 or51 support, if degree(e)=0 the fiber is the full
residence3-cell; if degree(e)=1 its wall equation is a nonzero affine-linear
plane equation in the affine residence coordinates, or is identically zero,
so the fiber is an open convex2- or3-cell, or empty. If degree(e)=2, the
support incidence graph proves the skew-line premise of the preceding lemma.
Here graph vertices are the4 selected triples; a parent label appearing in2
triples gives an edge between them. For type50 the graph is a triangle with
one leaf; for type51 it is a4-cycle. For every edge e, at least one endpoint
has another incident edge x to one of the other two support vertices. Thus
one of the pairs a,b contains a fixed label x in one fixed plane but not in
the other. Its other label is not in that first fixed plane, since the
canonical type50/51 supports share at most1 label pairwise. The line A
therefore meets the first fixed plane exactly at parent point x, and x is
not in the second fixed plane by uniformity. Hence A is skew to L.
All four a,b,c,d are distinct, again because the two support triples share
only e. The argument is invariant under every relative relabeling.

Each fiber of the forgetting map consequently has Hc0=Hc1=0. The
compact-support Leray sequence for this semialgebraic map gives

    Hc1(H49 intersect H50;R)=Hc1(H49 intersect H51;R)=0.

The forgetting map is not asserted to be proper; the argument uses its
compact-support direct image f!. Its fiber groups, not ordinary homology,
are the groups required by base change. No continuous choice of Gordan
witness is assumed or needed.

The independent referee and falsifier accepted this extension. The stronger
pair-wall endpoint P remains only for type families50+50,50+51,51+51. That still does not solve
the original pair restriction or the independent triple endpoint.

## 6. Accepted final endpoint accounting

The independent referee accepted Sections1–5 and independently reconstructed
the coordinator's exact unique-support orbit list. Together with the
inherited9476 total, the new stronger pair-wall Hc1 theorem covers8902
relative-label factor-pair orbits. The574 remaining source orbits are
257 of type50+50,249 of type50+51, and68 of type51+51. These are equation
pair orbits, not actual parent components or original signature triples.
See coordinator/HARD_PAIR_RESIDUE.json and the independent referee audit.

The remaining parameterized quotient attempt is tested separately in
NEXT_GATE.md. It is not part of the positive theorem proof.
