# Independent review of common weak-primal excision

Verdict: **ACCEPT THE DEDUCTIVE VANISHING THEOREM AND CANONICAL EXCISION**.
This is a conventional mathematical proof. No finite orbit computation or
formalization is required or used for acceptance.

Reviewed candidate: `pair/COMMON_WEAK_PRIMAL_VANISHING.md`.

For any nonempty finite set S of fixed signed extension systems over any
normalized component X of a uniform rank-four/eight-element parent, let W_S
be the simultaneous bad locus restricted to parents admitting a common
nonzero weak-primal vector. The accepted statement is that W_S is closed
in X and Hc^q(W_S;Q)=0 for q=0,1,2.

## Proper comparison and finite filtration

Using four basis-triple normals is legitimate: they form a basis of the dual
four-space. The inequalities from one fixed signature put every common
weak vector in a pointed closed orthant. Their signed coordinate sum is
strictly positive on every nonzero vector in that orthant. Normalizing this
sum to one produces a fixed compact simplex in the parent basis gauge.
The total weak incidence is closed in X times this simplex because every
bad locus is closed and all weak inequalities are non-strict continuous
inequalities. Projection is therefore proper, with precisely the nonempty
compact convex fibers required by the constant-sheaf unit and proper base
change. This proves both closedness and the compact-support comparison.

At least m zero evaluations is a finite union of closed conditions. These
sets give a finite closed filtration. At an exact zero-count level, specifying
which m rows vanish gives a finite partition into relatively closed subsets,
hence each exact-Z subset is clopen in that level. Outside Z, the evaluation
sign is fixed by the chosen signature. Thus the contraction matroid is
constant on each exact-Z stratum. No global quotient across changing zero
patterns is assumed, and no gluing of local witness selectors is required.

## Projected-frame check

Projection modulo p lowers the rank of any original subset by at most one.
Uniformity therefore implies that every projected parent triple has rank at
least two and every projected four-set rank at least three. Every zero
projected triple has rank exactly two. There is at most one loop, and no
two distinct projected parallel pairs can occur. If there is a loop, the
other seven columns form a uniform rank-three configuration.

A projected projective frame exists. Choose three independent projected
points. If every other nonzero point lies on their three connecting lines,
each line contains at most one additional labeled point, even counting
multiplicities. The union then has at most six nonzero labeled points. There
are at least seven. A fourth point off those lines supplies a projective
frame. The frame predicate depends only on Z, so one labeled choice works
on the whole exact-Z stratum.

Consequently the projective contraction quotient can be put in explicit
semialgebraic coordinates on that stratum. Orientation and positive column
normalizations use fixed signs, not arbitrary sign-changing rescalings.
The frame argument includes the possible projected parallel pair.

## Height-fiber check

Fix vector representatives of the nonzero projected columns. A lift has
eight heights. Parent determinant inequalities are homogeneous linear and
strict in those heights. Use three independent projected columns to remove
three height translations. A fourth parent column then has a nonzero
height relative to those three: otherwise that parent four-set would be
dependent. Its fixed-sign parent bracket normalizes the remaining positive
vertical scale. In the no-loop case this leaves an open convex subset of
an affine four-space.

In the loop case p is a parent point e. The independent positive rescaling
of its zero-projection column fixes h_e to its prescribed nonzero sign.
There are seven remaining heights. Remove three translations and normalize
positive vertical scale using a parent four-bracket excluding e. This
leaves an open convex subset of an affine three-space. Brackets containing
e already have signs determined by the contraction data and the oriented
loop lift. This is why a four-dimensional claim at a parent-point weak ray
would be wrong; the candidate handles it correctly.

All remaining inequalities are strict after these affine gauge equations,
so nonempty fibers have full dimensions three or four. They are connected.
Restricting to one component X retains an entire such fiber or none, since
the normalized lift map carries its connected image into one component.

## Saturation check

For a zero triple I, its projected rank is two. Its full derived normal is
a scalar L_I(h) times the fixed projected plane normal, with zero final
coordinate. Choose a fourth parent label whose projected point is outside
that plane. The parent four-bracket is L_I(h) times a fixed nonzero factor.
Uniformity and the fixed parent chirotope imply L_I(h) is nonzero with
constant sign throughout the entire height residence cell.

Every common-weak badness witness is supported entirely on zero triples:
pair its nonnegative dependence with p and use that every summand is
nonnegative. Conversely a zero-supported dependence is a full witness.
Positive rescaling of each zero-row normal transports the existence of every
such dependence. The weak inequalities outside Z depend only on projected
determinant signs. Thus the simultaneous bad conditions select whole height
fibers, not arbitrary subsets of a convex fiber. This is the key
actual-geometry argument; mere convexity before imposing badness would
not suffice.

## Cohomological descent and excision

Each stratum contraction map has open convex three- or four-dimensional
fibers. Their compact-support cohomology vanishes in degrees0,1,2.
Shriek base change therefore annihilates R^q f_!Q in those degrees.
The compact-support Leray spectral sequence has no negative base degrees,
so each exact-Z incidence stratum has the same low-degree vanishing.
The finite closed filtration passes that vanishing to the total incidence.
The proper convex comparison then passes it to W_S. This proof uses f!
for the nonproper contraction projection; it does not incorrectly substitute
ordinary fiber contractibility for compact-support cohomology.

For S={0,1,2}, the resulting W is closed in T and each A_ij. Localization
gives canonical extension-by-zero isomorphisms in degrees0,1,2 after
removing W from these spaces. The open/closed Cartesian squares make these
isomorphisms commute with the restrictions to T. Hence the alternating pair
map is conjugate to its restriction after deleting W, and triple Hc0 is
unchanged. The same localization argument also preserves Hc2 of the whole
bad union after removing W, since W is closed there.

## Required scope

W is generally a proper subset of simultaneous badness. A positive Gordan
dependence whose support spans R4 forces the weak-primal cone to be{0};
such parents are outside W. This must not be phrased as an assertion about
every infeasible strict system, since boundary bad systems can have nonzero
weak-primal rays.

The theorem applies without signature admissibility or antichain assumptions,
and therefore covers the original admissible family. It does not prove
vanishing on the complement T minus W or injectivity of the remaining pair
map. It removes one geometrically defined subset without changing either
original obstruction. No original third-diagonal promotion follows.
