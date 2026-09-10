# A closed rank filtration for distinct collinear concurrences

## Result and remaining edge

Let Z be a triple intersection of distinct primitive residual factors in any
normalized component X of any realizable uniform rank4 parent on eight labels.
Choose ordinary occurrences for all three factors using the accepted all-six
anchor theorem, and remove the already-proved pairwise-concurrence collision
union. Write p,q,r for the three distinct concurrence points.

The following closed pieces of the collinear locus have H_c^0 equal to zero:

1. The union of the pieces where the common concurrence line contains a parent.
2. After removing that union, the piece where the exact common-line incidence
   matrix defined below has rank at most10.

The rank of that matrix at any remaining actual parent is at most11. Its rank11
part can be populated with zero-dimensional normalized fixed-projection fibers;
an independently reconstructed uniform example is supplied below. That example
is vertically regular. Thus the surviving collinear critical question is
sharply confined to rank11, with all eight parents outside the concurrence line.
No assertion that this critical rank11 locus is empty or noncompact is made.

This theorem concerns full closed pieces of Z, not merely subsets of its
critical locus. Their removal by compact-support localization is therefore
legitimate even though vertical criticality need not be constant on a general
fixed-projection height fiber.

## Parents on the common line

The independently reviewed argument in
`../referee/PARENT_ON_CONCURRENCE_LINE.md` proves the stronger persistence
statement that sliding such a parent along the common line preserves vertical
criticality. The same proof with its criticality section omitted applies to
the full collinear triple locus.

For completeness, fix a parent Y_i on the common line L and reframe using five
of the other seven parents. Hold those seven parents fixed. Every selected
plane containing Y_i also contains its own distinct nonparent concurrence, so
it contains all of L. Moving Y_i on L therefore fixes every selected plane ray
throughout the uniform residence; planes not containing it are fixed outright.
All three concurrence points consequently remain fixed.

A selected P plane whose triple excludes i supplies a fixed linear form ell
with ell(p)=0 and ell(Y_i) nonzero. Normalizing ell(Y_i) to its fixed value
gives an affine chart on L minus p. All prescribed parent signs cut out a full
open interval in this chart. It is a component of the closed fixed-other-parent,
fixed-line slice, and is noncompact. It remains in the original parent
component because it is connected and contains the starting parent. A compact
component of the full collinear parent-on-L piece would contain this closed
noncompact interval, a contradiction.

Collinearity and Y_i in L are closed conditions on the collision-free locus.
Restriction injects H_c^0 of their finite closed union into the direct sum of
the eight individual H_c^0 groups. Hence the union also vanishes and can be
removed. In the remainder every parent has a nonzero projection from L.

## Exact linear incidence model

Normalize the ordered three points on L to

    p=e3, q=e4, r=e3+e4,

and write each parent column as

    Y_i=(g_i,a_i,b_i),  g_i in R2 minus {0}.

For a support triple I=(i,j,k), let its three-sparse row be

    B_I,i=det(g_j,g_k),
    B_I,j=-det(g_i,g_k),
    B_I,k=det(g_i,g_j).

Write B_P,B_Q,B_R for the four rows in each ordered occurrence. The three
concurrence conditions are exactly

    B_P b=0,   B_Q a=0,   B_R(a-b)=0.

They form the12-by16 homogeneous block matrix

\[
M(g)=\begin{pmatrix}0&B_P\\B_Q&0\\B_R&-B_R\end{pmatrix}
\]

on (a,b). Every projected triple rank is included. If its
g-columns have rank1, its three original parent columns span a plane containing
all of L, since they have rank3 and their projected image has dimension1. Its
row B_I is then zero and the incidence is automatic. If the g-columns have
rank2, the equation is the usual exact incidence with the specified point of L.

Each B block annihilates both rows of g. Thus four height shears are in the
kernel of M. The actual uniform lift gives a fifth independent kernel vector:
if it were a shear, all parent columns would have rank at most2. Consequently
rank M is at most11 at every actual parent in this locus.

## A global affine scale chart on each fixed projected fiber

The two varying height rows make the parent brackets quadratic in (a,b).
Their strict sign residence is open; convexity is neither asserted nor needed.
The essential point is to normalize scale by a linear functional that never
vanishes anywhere on the full uniform fixed-g fiber.

At least two of the four P planes fail to contain L. Otherwise three of their
normal rows would lie in the two-dimensional annihilator of L, contradicting
the ordinary-circuit theorem. Choose one such plane J. The choice is valid
throughout the fixed-g fiber: it is characterized exactly by rank(g_J)=2,
which depends only on g.

On B_J b=0 this plane has the equation

    b=ell_J(g),

where ell_J is the linear functional on R2 obtained by solving its values on
two independent projected columns in J. Its coefficients depend linearly on
the height values b_j, with fixed nonzero g denominators. For any parent i
outside J, put

    L_J,i(a,b)=b_i-ell_J(g_i).

This is a linear functional on the full height space, invariant under all
four height shears. It is nowhere zero on the uniform fixed-g fiber: zero
would put the fourth parent i into the selected plane of J. This is precisely
a forbidden parent bracket, not an additional exclusion.

Use two independent projected parents to remove the four shears. Then
normalize L_J,i to1 using the remaining common nonzero scale of a and b.
Both signs of that common scale are legitimate projective changes: the
ambient map diag(I2,tau I2) has determinant tau squared, so it preserves all
parent signs even for negative tau. If one records a positive-scale convention
instead, retain the two sign sectors L_J,i=+1 and-1. They describe the same
nonvanishing affine-chart argument.

The full normalized fixed-g incidence is therefore an open subset of an
affine space of dimension

    dim ker M -4-1 = 11-rank M.

It may have several components. Every component is open in that affine space;
if the dimension is positive, none is compact. A chosen original parent
component retains whole components of this open fiber. No global claim of
convexity or connectedness is being substituted here.

## Why these fibers are closed globally

The projected data are an ordered configuration of eight points of RP1 modulo
PGL2, allowing coincidences. Every parallel class has size at most3: four
parents with the same projected direction would lie in the same
three-dimensional subspace L plus that direction. There are therefore at
least three distinct projected directions.

PGL2 acts properly on this allowed configuration space. To see this directly,
suppose both source and target configurations converge within the allowed
space while projective transformations diverge. After normalizing their
matrices and taking a subsequence, the matrices converge to rank1. Every
source point outside the single kernel direction then converges to the same
image direction. At most3 source labels can lie at that kernel direction;
at least5 target labels would coincide, contradicting their permitted
multiplicity. Thus no such diverging sequence exists. Ordered configurations
with three distinct points have trivial stabilizer, and the quotient is
Hausdorff.

Projection of the collinear parent locus to this quotient is continuous,
using local frames for the two-dimensional quotient by L. A fixed projected
configuration fiber is consequently closed. On that fiber, fixing its ordered
projective representative g leaves exactly the four shears and common height
scale already handled above. The finite parent-sign choices and frame-lift
choices are retained. Their identifications are proper finite maps, so a
compact component downstairs would have a compact inverse image; they cannot
turn these noncompact affine-chart components into compact components.

Now suppose a compact component of the rank-at-most10 collinear piece existed.
Take a point in it and the component of its full closed projected fiber that
contains this point. By the affine scale construction this is noncompact,
since its dimension is at least1. It is closed in the fiber, hence in the
whole rank piece, and lies in the compact component. This is impossible.

The matrix rank is invariant under the projected and height gauge changes and
is upper semicontinuous. Its rank-at-most10 locus is closed in the collinear
parent-free remainder. Collinearity is itself closed in the collision-free
space. Thus the preceding removal of parents on L, followed by removal of
this rank piece, uses closed subsets at each step. Both have H_c^0=0.

## Exact rank11 canary and the remaining critical condition

The referee independently found the following uniform parent. Set g_i=(1,t_i),
where

    t=(0,1,2,3,4,5,6,485/173),
    a=(0,0,-19203/1946,7785/973,13840/973,12975/973,1730/139,624/139),
    b=(0,0,0,-12975/973,-17300/973,-25950/973,692/139,1).

Take

    P=123/145/246/378,
    Q=146/278/348/567,
    R=156/178/245/368.

All70 parent brackets are nonzero. The ordinary concurrences are the three
specified points p,q,r, the stacked matrix has rank11, and the two vertical
wall gradients have rank2. `verify_collinear_rank11.py` reconstructs these
claims from the original parent determinants, independently of the producer's
acceptance logic. This canary is not a critical point and earns no new source
orbit count. It shows why collinearity alone cannot supply a positive-dimensional
normalized fixed-projection fiber.

The precise remaining collinear discriminator is whether an actual uniform
rank11 point can also have dependent vertical gradients. If none can, the
entire collinear critical branch is eliminated by this rank filtration and
the regular-locus theorem. If such a point exists, the rank11 critical
compatibility locus needs its own global escape argument. Neither possibility
is decided here.
