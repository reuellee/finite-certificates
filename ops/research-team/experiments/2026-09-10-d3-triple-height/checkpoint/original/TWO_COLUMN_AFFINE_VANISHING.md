# Two-column affine elimination for the balanced pair residue

## Statement and support hypothesis

Let X be any normalized component of a uniform rank-four parent on eight
labels. Consider two four-triple residual-wall occurrences P,Q with two
distinct parent labels e,j satisfying these conditions:

1. Both e,j occur in P only in one common triple {a,e,j}. The normals of
   the other three P triples are independent, with common projective kernel
   point z, and z differs from the parent point a.
2. Q consists of triples

       {e,j,k}, {e,b,c}, {j,d,f}, L,

   where L is a fixed parent triple excluding e,j; all triples have distinct
   entries; the second and third triples contain respectively e only and j
   only among the moving labels.

Then the full intersection of the two residual walls in X has

    H_c^q=0 for q=0,1.                                      (1)

For the inherited balanced type50/type51 residue, the hypothesis applies to
27 of the 45 records remaining after the one-column affine theorem. The
independence and noncoincidence condition in item1 is a parent-unit fact for
the type50 occurrence used here; it is proved below. The argument is
deductive and includes all coefficient rank drops and all parent components.

## 1. Retain three plane pencils

Normalize a projective frame among the six nonmoving parent labels. Their
realization chart U is open in R^3. Its coordinates, their column rays, and
the fixed point z are quotient data.

For an actual pair-wall point retain the three planes

    Pi=span(a,e,j), He=span(e,b,c), Hj=span(j,d,f).

The P equation says that Pi contains z, so Pi belongs to the pencil through
the fixed line az. He belongs to the pencil through bc, and Hj to the pencil
through df. Thus this quotient has six dimensions: three for U and one for
each of the three plane pencils.

Every pencil has a global affine chart on the actual residence locus. For
He choose any fixed parent g_e distinct from b,c. Uniformity forces
He(g_e) !=0, since {e,b,c,g_e} is a parent basis. Normalize its covector by
He(g_e)=1. Similarly choose g_j distinct from d,f and normalize Hj(g_j)=1.
For Pi choose a fixed parent g_Pi distinct from a. Uniformity forces
Pi(g_Pi) !=0 and normalize it to1. In particular a,z,g_Pi are independent
whenever the incidence is nonempty: otherwise every plane through az would
contain g_Pi. Exclude the empty configurations where they are dependent.

In these normalizations, each pencil is an affine line in covector space.
Their product is an affine-three-bundle over an open subset of U. Its
components are noncompact. One can obtain global line coordinates by taking
the least-norm particular covector and the nonzero cross product of the
three fixed vectors defining its kernel, in the fixed oriented four-space.
Only an open six-dimensional ambient manifold with noncompact components
is needed below.

## 2. The common point of the three retained planes is forbidden

On an actual uniform incidence, Pi,He,Hj are linearly independent as
covectors. Indeed Pi=He or Pi=Hj would put four distinct parent points in one
plane. If the three distinct planes had rank two, their intersections with
Pi would be the same line, containing both e and j. Then He would contain
e,j,b,c, again contrary to uniformity.

Restrict the six-dimensional quotient to this open rank-three locus and let
S be a continuously normalized nonzero vector spanning the common kernel of
Pi,He,Hj. Their ordered exterior product gives such a global vector in the
fixed parent frame. The two lines

    Le=Pi intersect He, Lj=Pi intersect Hj

meet at the projective point S. Neither moving parent can equal this point:
Hj(e) and He(j) are nonzero parent-bracket ratios.

Their signs are fixed on X. More explicitly,

    Hj(e)=a_(jdf)(e)/a_(jdf)(g_j),
    He(j)=a_(ebc)(j)/a_(ebc)(g_e).

Both numerators and denominators are prescribed nonzero parent brackets.
Write their fixed signs as epsilon_e,epsilon_j. Positive and unique column
rescalings therefore normalize

    Hj(e)=epsilon_e, He(j)=epsilon_j.                         (2)

This is essential: it uses positive rescaling of the actual oriented parent
columns, rather than introducing an arbitrary projective sign chart.

## 3. Two affine coordinates and cancellation of the mixed term

In the gauge (2), the two moving columns have the form

    e(s)=E+sS, j(t)=J+tS,          (s,t) in R^2,               (3)

where E,J vary continuously with the quotient data. For example obtain E
and J as the unique solutions of their three plane/evaluation equations
orthogonal to S. These linear systems have full rank.

Every parent bracket is jointly affine in s,t. Brackets involving neither
or only one moving column have this property immediately. A bracket
involving both has no st term because that term contains two equal columns S:

    det(E+sS,J+tS,v,w)
     =det(E,J,v,w)+s det(S,J,v,w)+t det(E,S,v,w).              (4)

Thus all prescribed parent signs define one open convex polyhedron C_u in
R^2. Its dimension is two when nonempty. The positive gauge ensures that
these are the original chirotope inequalities, with no omitted sign sheets.

## 4. The second wall gives one affine equation

The P equation is automatic: a,e,j,z all lie in Pi. The two Q normals
containing only one moving label are

    a_(ebc)(e(s))=kappa_e(s) He,
    a_(jdf)(j(t))=kappa_j(t) Hj.

Their multipliers are the parent brackets obtained by evaluation at g_e and
g_j, hence never vanish on C_u. Dividing by these parent units preserves the
zero set. The Q equation becomes, up to a fixed row-ordering sign,

    det(a_(ejk)(s,t), He, Hj, a_L)=0.                        (5)

The first row in (5) is jointly affine by the same S-wedge-S cancellation
as (4); the other three rows are quotient data. Equation (5) is therefore

    A(u)s+B(u)t+C(u)=0.                                     (6)

No concurrency point of He,Hj,L needs to be chosen. In particular (6)
already retains the cases where those three planes have dependent normals,
where their intersection is a line, or where a proposed marked-point
parametrization degenerates.

Conversely, every point of C_u satisfying (6) reconstructs an actual
pair-wall point. Parent uniformity makes the reconstructed planes exactly
Pi,He,Hj. The quotient description neither covers the same point twice nor
omits a projective end.

## 5. Compact-support calculation

Let Z be the full pair-wall incidence in X, identified with the model above.
On the open subset where (A,B) !=(0,0), its full fiber is either empty or one
open convex interval. Its nonempty-image locus V is open in the six-dimensional
quotient: a strict feasible point of an affine line persists under small
coefficient and base changes. This remains true after restriction to X.
Each connected fiber is wholly inside one parent component, so X selects
whole fibers.

Integration along the interval fibers gives an orientation local system
shifted by one. V has no compact component, since it is open in a
six-manifold whose components are noncompact. Hence H_c^0(V;orientation)=0,
and the rank-one part of Z has H_c^0=H_c^1=0.

The complementary coefficient-rank-zero stratum is closed in Z. Its fibers
are empty when C !=0, and the full open convex two-cell C_u when C=0.
Thus its R^0 f_! and R^1 f_! vanish, regardless of its base topology or
coefficient specialization. The compact-support Leray sequence and then
closed/open localization prove (1).

This argument retains all finite parent-wall ends, unbounded affine ends,
and coefficient-rank changes. It does not infer global cohomology from
pointwise conic rationality or componentwise interval fibers.

## 6. The type50 parent-unit hypothesis

Up to relabeling, the type50 occurrence is

    123/145/246/378,

and its unique triple containing two degree-one labels is 378, with moving
labels7,8 and a=3. The remaining normal rows 123,145,246 are independent:
the first two are independent and annihilate parent1, whereas the third
evaluates nontrivially at parent1 by the unit bracket2461. Their common point
z is not parent3, because normal145 evaluates nontrivially at3. These are
uniform-parent facts, so they hold on every parent component, including
intersections with other residual walls. Relabeling proves item1 for every
candidate used in this application.

## 7. Coverage and original scope

The deterministic support test verifies all remaining source quartets and
records the moving-label choices. It selects17 of the19 remaining type50+50
records and10 of the16 remaining type50+51 records, for27 total. It selects
none of the10 type51+51 records. The resulting stronger pair-wall coverage is

    9,458 of9,476, with18 records remaining.

The18-record residue and exact choices are in TWO_COLUMN_AFFINE_COVERAGE.json.
This is a sufficient auxiliary endpoint for D3. Original injectivity and the
independent triple-bad H_c^0 obligation are not proved by this theorem.

Status: complete candidate proof submitted for independent deductive audit.
Base and predecessor source identities are inherited from the current
work order. The already accepted529-case proof is unchanged.
