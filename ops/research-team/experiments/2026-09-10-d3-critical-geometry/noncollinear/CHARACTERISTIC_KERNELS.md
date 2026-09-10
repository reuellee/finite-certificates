# Characteristic height directions of ordinary factor walls

## Definition and conclusions

At a uniform point on an ordinary factor wall Q, let B_Q be the eight-by-four
map sending a vector v in the parent four-space to the derivative of Q under
independent column motions Y_j -> Y_j+h_j v. Thus B_Q v is the eight-height
gradient gamma_Q, up to the nonzero circuit/adjugate normalization in the
accepted `VERTICAL_CRITICAL_REDUCTION.md`.

Changing to a parent-unit-equivalent occurrence multiplies B_Q by a nonzero
scalar on the wall. Its kernel is intrinsic to the primitive wall, even
though different ordinary occurrences can have different concurrence points.

The following statements hold on every uniform realization of the listed
canonical occurrences, and hence after every parent relabeling.

| Global kind | Kernel of B_Q | Rank | Height consequence |
|---|---|---:|---|
| 38 | plane345 intersect plane678 | 2 | Every direction in this line preserves Q under arbitrary simultaneous height shifts that remain uniform. |
| 48 | span of the two ordinary concurrence points for123/145/246/356 and124/135/236/456 | 2 | Only first-order invariance follows; the exact canary below has nonzero second-order change. |
| 49 | Its unique ordinary concurrence point | 3 | A zero height gradient forces a concurrence collision. |
| 50 | Its unique ordinary concurrence point | 3 | A zero height gradient forces a concurrence collision. |
| 51 | Its unique ordinary concurrence point | 3 | A zero height gradient forces a concurrence collision. |

Global36 and its localization-axis excision are being treated by the
constructive/referee tracks. No unproved global36 classification is needed
for the statements in this note.

## A leaf-row observation

Suppose parent e occurs only in the ordinary triple eab. Its row in B_Q is

    v -> lambda_eab det(Y_a,Y_b,v,q),

up to a fixed sign. If q does not lie on the parent line ab, this is a
nonzero multiple of the normal of plane(eab), because q lies in that plane.
The ordinary circuit coefficient is nonzero by the inherited source theorem.

One convenient uniformity test is that another support triple contains a
but excludes b. If q were on ab, its membership in that other plane would
force q=a. An ordinary concurrence cannot equal a parent, so this is
impossible. This test applies to all leaf rows selected below except the
kind38 leaf in678, whose nondegeneracy follows directly from the skewness
of parent lines12 and78.

## Kinds50 and51

For type50=123/145/246/378, choose leaf rows5,6,7. They are nonzero multiples
of the three ordinary normals145,246,378. Those normals are independent
throughout the uniform wall. Their common kernel is the concurrence q.
Since B_Q q=0, these three rows prove ker(B_Q)=span(q) and rank(B_Q)=3.

For type51=123/145/267/468, leaf rows3,5,7 similarly give the independent
normals123,145,267. The same conclusion follows. The assertion includes
all simultaneous residual-wall intersections, because ordinary three-row
independence is a parent-unit fact, not a generic condition.

## Kind49

Use Q=123/145/246/357. Leaf rows6 and7 are nonzero multiples of the normals
of planes246 and357. Therefore any v in ker(B_Q) lies in their intersection.

Now inspect row2. Its circuit expression has contributions from123 and246.
The246 contribution is zero because v,q,Y4,Y6 lie in plane246. The remaining
contribution is

    lambda_123 det(Y1,v,Y3,q).

The point q cannot lie on line13: plane145 meets that line only at parent1,
and plane246 excludes parent1. Consequently this last covector is a nonzero
multiple of the normal of plane123. Thus v also belongs to plane123. The
three ordinary planes123,246,357 have independent normals and common point
q, so v is proportional to q. Again rank(B_Q)=3 globally.

## Kind38: an axis with full height invariance

Use Q=123/124/345/678. Its concurrence q lies on parent line12. Put

    L=plane345 intersect plane678.

These two planes are distinct. Leaf5 gives a nonzero multiple of normal345.
Leaf6 gives a nonzero multiple of normal678: q cannot lie on line78 because
parent lines12 and78 are skew by the nonzero parent bracket1278. Hence
ker(B_Q) is contained in L.

Conversely fix any nonzero v in L and shift every parent independently by
an arbitrary multiple of v. Parents3,4,5 stay in their original plane345;
parents6,7,8 stay in their original plane678. Whenever the shifted parent is
uniform these triples still span those same planes.

Before the shift, line12 meets L at q and cannot equal L, since neither
parent1 nor2 belongs to plane345. Hence they span an honest projective
plane H. The two shifted parents1,2 remain in H because v belongs to L.
Their new line therefore meets L. Its intersection gives a common point
of the four shifted support planes, so Q still vanishes. Uniformity
excludes all plane or parent-line degeneracies needed in this argument.

Thus Q is identically zero under the full simultaneous height shifts in
any direction v in L, restricted only by the actual parent inequalities.
Differentiating gives L contained in ker(B_Q); the two containments prove
the kernel and rank statement. This is stronger than first-order flatness.

## Kind48: the line joining its two ordinary concurrences

The two ordinary occurrences are

    K=123/145/246/356,
    K'=124/135/236/456.

In a projective frame normalized by parents1,...,5 their determinants are
opposites, respectively a+bc-b-c and -a-bc+b+c. The exact identity is checked
symbolically by `verify_kind48_axis.py`. Since both determinants have the
same projective and parent-column weights, this proves their equality up
to sign on every uniform parent chart. Both therefore define the same
primitive factor, and their gradient maps have the same kernel.

Let their ordinary concurrences be q and q'. They are always distinct.
If equal, membership in planes123 and124 places the common point on line12.
Membership in145 then forces it to be parent1, which is excluded by246.
This contradicts uniformity. Both q and q' are in ker(B_Q).

The determinant uses only parents1,...,6. Hence the last two rows of B_Q
are zero. Projective invariance gives Y B_Q=0, so its image lies in the
kernel of the four-by-six active-parent matrix. That kernel has dimension2.
Therefore rank(B_Q)<=2.

Every active-parent row of B_Q is nonzero on every uniform wall. For parent6,
normalize the other five active parents as a projective frame; the primitive
formula a+bc-b-c has derivative1 in the first affine coordinate of parent6.
The stabilizer of the four-plane incidence pattern permutes its six parent
labels transitively (they are the six edges of a tetrahedron), so the same
nonvanishing holds for each active row.

Rank1 is consequently impossible. In that case all six nonzero row
covectors would be proportional to one covector ell. Column homogeneity on
the wall says that the jth row annihilates Y_j; ell would therefore
annihilate all six active parent columns, contrary to rank4 uniformity.
Thus rank(B_Q)=2, and its kernel is exactly the two-dimensional vector span
of q,q'.

## The kind48 axis is not fully height-flat

At the inherited uniform parent, the two concurrence representatives are

    q=(1/2,1,1,0), q'=(1/3,1,0,1).

Choose v=q+q'=(5/6,2,1,1), which is distinct projectively from both. It lies
in ker(B_Q). Shift only parents5 and6 by u v and t v respectively. The
exact ordinary determinant becomes

    -(17u^2 t+6u^2-7u t^2+12u t-6t^2)/6.

In particular, at t=0 it equals -u^2. All70 parent signs are retained for
t=0 and |u|<=1/100, proved by the exact affine bracket endpoint inequalities
in `KIND48_AXIS_CANARY.json`. The first derivative vanishes, but the second
derivative is -2. Thus the kind48 characteristic line does not supply the
full-height invariance proved for kind38.

The direction in this diagnostic need not be the concurrence of another
primitive factor. It disproves the proposed implication from the kind48
kernel condition alone to complete height invariance; it is not an
additional actual three-factor critical witness.

## Consequence for the remaining critical problem

After concurrence collisions are removed, a zero individual height gradient
can no longer come from a factor of kind49,50,or51. The zero-gradient
kind38 branch has the full-height structure above; kind36 is handled by its
localization geometry. Kind48 remains an actual higher-order issue.

These statements do not settle dependence of two nonzero height gradients.
That proportional-gradient branch remains even when all factors have kinds
49,50,51. No noncompactness theorem or original diagonal is claimed for it.
