# Independent audit: universal pair-wall subfamilies

Verdict: ACCEPT the pair-wall `H_c^0=H_c^1=0` theorem for every pair
containing factor kind 36, 38, or 48, and for every 49+49 pair, under the
inherited global factor classification. This is a new universal application
of the inherited residence-quotient theorem, rather than sampled evidence.
It does not close original D or D3. Five factor-kind pair families remain.

## Global residence geometry

For a chosen occurrence of each factor, retain the nonmoving columns and
the projective normal ray of every selected support plane incident to a
moving column. A frame may be fixed among five nonmoving labels; uniformity
makes its projective normalization global on the parent component.

If one column meets zero or one selected plane, its parent-sign residence
is an open convex projective cell of dimension three or two. If two columns
each meet two selected planes, their respective intersections are fixed
projective lines. Different selected triples define different planes:
otherwise at least four parent columns would be coplanar, contradicting
uniformity. The two lines are independent residence parameters.

The potentially delicate shared-triple case is valid. If both moving
columns occur in a selected triple, each is constrained to that triple's
retained plane. Its third column is fixed. Throughout the parent-sign
residence their three columns remain independent and therefore span the
same retained plane; there is no additional equation coupling the two
parameters. Co-occurrence therefore does not lower the fiber dimension.

Every nonempty vertical section of the joint residence set is an interval,
because each parent bracket is affine in either moving parameter separately.
A connected residence component projects onto an interval. A vertical
section cannot meet two components, since it is connected. Locally
persistent choices and partition of unity produce a continuous section,
and vertical straight interpolation retracts the component to its projected
interval. Thus each component is a contractible open two-manifold even
when the full joint domain is nonconvex.

Each selected normal changes by a positive scalar while its ray is fixed.
Inverse rescaling of witness weights preserves both individual circuit
relations. Conversely, all parent configurations satisfying the quotient
data lie on both factor walls, since the relations force each full global
factor equation. This identifies the full quotient fibers, including at
multiwall intersections. Their compact-support cohomology vanishes in
degrees zero and one. The compact-support Leray sequence therefore proves
the stated global vanishing. This uses the inherited all-strata residence
quotient, not ordinary nonproper homotopy invariance.

## Kind 38: a direct global argument

The cited root-switch note describes its occurrence complex generically.
That generic topological claim alone would not suffice for a theorem on
the whole factor wall. The following independent argument fills that
possible gap and justifies the 15 occurrence choices globally.

Let `L=ann(span(y_1,y_2))`, of dimension two. Put
`u_a=n_(12a)` for a=3,...,8, `c=n_(345)`, and `d=n_(678)`.
Uniformity implies every pair u_a,u_b is a basis of L; its determinant
is a nonzero parent-bracket unit. Hence every determinant
`det(c,d,u_a,u_b)` differs from the canonical one by a nowhere-zero
parent-bracket ratio. Their complete zero sets in X are identical.

On that wall, c and d have nonzero, dependent images modulo L. Thus for
some nonzero scalar alpha, `v=d-alpha*c` belongs to L. For a=3,4,5,
`v(y_a)=d(y_a)` is a nonzero parent bracket; for a=6,7,8,
`v(y_a)=-alpha*c(y_a)` is also nonzero. Since `u_a(y_a)=0`, v is
proportional to none of the six u_a. Expanding v in any basis u_a,u_b
therefore has both coefficients nonzero. The c,d coefficients are also
nonzero. Every chosen four-row occurrence consequently has rank exactly
three and a relation with all four coefficients nonzero on the entire
global wall, including its intersections with other factors. The inherited
unit identities make the signs constant on X. Generic occurrence sampling
is not being used as a global rank assertion.

## Exact support selection

The independent standard-library verifier reads the canonical support
strings from the pinned source and reconstructs all 266 degree patterns
using four-unit deficit multisets. For each pattern it checks the producer's
choice and separately constructs a valid occurrence by selecting the two
outer labels of largest other-support degree. It checks downward closure
under removal of shared support triples. This is exhaustive combinatorial
coverage of the selection lemma, not a parent-chart census.

The remaining geometric arguments require no enumeration: kind36 has at
most 21 combined label incidences; kind48 omits two labels; and two kind49
supports either have a common omitted label or each other's omitted label
supplies the two required light degrees. The support-plane criterion applies
in all three cases. The six kinds have 21 unordered kind pairs with
repetition; these arguments cover 16, leaving exactly
`49/50,49/51,50/50,50/51,51/51`. This ratio is a type count and is not a
fraction of original proof completion or of the 9,476 factor-pair orbits.

The three-regular 50/50 support canary passes as a combinatorial obstruction
to this particular fixed-plane criterion. No claim of an actual nonempty
parent intersection follows from its support data alone.

## Evidence and scope

`verify_pair_templates_independent.py` passes all 266 patterns with five
hostile rejections covering a malformed choice, wrong bound, omitted case,
source mutation, and changed canary. `PAIR_TEMPLATE_REPLAY.json` records the
certificate hash and independent choice digest. No producer acceptance
module is imported. The derived topological statement is justified by the
deductive audit above; the finite script itself checks only its combinatorial
inputs. Original obligations closed: zero. Ledger: 2/9.
