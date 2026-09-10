# Independent audit: omitted-label ruled-quadric fibers

Verdict: ACCEPT the extension to every 49+50 and 49+51 factor pair. Together
with the support-plane theorem, the entire stronger pair-wall endpoint is
proved outside the three type families 50/50, 50/51, and 51/51. No original
pair-map or diagonal theorem is asserted.

Fix seven parent columns and let C be the full convex projective residence
three-cell of the omitted type49 label e. The type49 equation is independent
of e. If e occurs zero or once in the other selected occurrence, its full
fiber is empty or a convex open cell of dimension at least two. The degree-two
case is the only additional argument.

Let the two incident triples be eab and ecd, the two remaining normals u,v,
and write A=line(ab), D=line(cd), and L=ker(u) intersect ker(v). The support
incidence check below guarantees A skew L after interchanging the incident
triples if needed; parent uniformity guarantees A skew D.

The map sending e to q=span(e,A) intersect L is therefore well-defined.
Restriction of the moving normals to L shows the four-normal determinant
vanishes precisely when det(e,c,d,q)=0. The first restriction is never the
zero functional: a plane containing the skew lines A and L would be all of
projective three-space. Thus the determinant equivalence loses no points.

Choose a fixed parent label z outside a,b. The direction
q0=span(a,b,z) intersect L is forbidden by the actual parent bracket
[eabz] !=0. Hence the q-base is an affine line; a projective-circle base
has not been cut artificially. If L=D the whole residence is allowed.
Otherwise q*=L intersect D is absent or a single direction. For q different
from q*, the fiber line is span(q,A) intersect span(q,D). These planes are
distinct because A and D are skew. Its intersection with C is an open
interval or empty. The regular part is an open subset of a line bundle
over intervals; connected interval fibers imply each component retracts
onto its interval image, exactly as in the earlier two-pencil proof.
Its compact-support groups in degrees zero and one vanish.

If the exceptional direction q* is allowed, its whole fiber is
C intersect span(q*,A), an open convex two-cell or empty. It is closed in
the full wall fiber. The closed/open compact-support sequence shows that
adding it back still leaves H_c^0 and H_c^1 zero. In particular, singular
quadric fibers were not discarded. The forgetting projection need not be
proper: the global conclusion uses compact-support direct image f_! and
its fiberwise base-change theorem.

For the skew-line premise, an edge e of the type50/51 support-incidence
graph always has an endpoint possessing another edge x to one of the two
fixed support vertices. The other label of that moving triple is not in
the first fixed plane, since every pair of selected triples shares at most
one label. Thus A meets that plane exactly at parent point x. The point x
is not in the other fixed plane by uniformity and its degree-two occurrence.
Therefore A cannot meet L. All four endpoint labels a,b,c,d are distinct.
The finite incidence check verifies every doubled label of both canonical
supports; relabeling preserves the argument.

The three remaining factor families have unique global occurrences, so the
independent BFS/union-find enumeration is a complete relative-label orbit
calculation for the support criterion. It yields:

| kinds | all distinct factor-pair orbits | support-plane theorem | residue |
|---|---:|---:|---:|
| 50/50 | 1,411 | 1,154 | 257 |
| 50/51 | 1,272 | 1,023 | 249 |
| 51/51 | 379 | 311 | 68 |

Every one of the 574 producer residue records is independently identified
with a distinct failed orbit, and every failed orbit is represented. Using
the inherited complete total of 9,476 factor-pair orbits, the stronger
universal H_c^1 wall-pair endpoint is therefore certified on 8,902 orbits;
574 remain open. This is proof-schema coverage of a sufficient endpoint,
not original pair-map, parent-component, or diagonal completion percentage.
No full Burnside model for the other factor kinds is needed for this
subtraction: their entire kind families are already proved uniformly.
