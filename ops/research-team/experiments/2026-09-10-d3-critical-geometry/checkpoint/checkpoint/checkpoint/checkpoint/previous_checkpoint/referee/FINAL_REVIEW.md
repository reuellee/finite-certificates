# Independent final review

10 September 2026. Verdict: **ACCEPT AUXILIARY POSITIVE CONTINUATION AND
ACTUAL-PARENT NO-CONTINUOUS-SECTION COUNTEREXAMPLE.**

The original 9DVL pair-map injectivity remains open. The separate triple Hc0
obligation remains open. The ledger is2/9; this cycle closes zero original
global obligations and removes zero original unresolved source records.

## Independent acceptance basis

The referee did not import either discovery track's code. Its three replay
programs use only the Python standard library. Determinants are computed by
permutation sums, including polynomials built from the literal parent, with
exact Fraction arithmetic. Rank is computed by independent row reduction.
The producer used recursive determinant expansion for the constructive result
and SymPy for the falsifier result; neither acceptance implementation was
reused. Supplied success flags are not accepted as proof.

Replay commands from the cycle root:

```
python -B referee/verify_opening.py
python -B referee/verify_constructive_independent.py
python -B referee/verify_falsifier_independent.py
```

Opening replay verifies the inherited three-row fixture and its rank-three
near-singular hostile point. Constructive replay verifies all70 bracket
polynomials, all56 normal polynomials, the constant reserve, full56 positive
section and source-matching support6 lift. Falsifier replay independently
verifies all three new polynomial parent families, the exact central fiber,
the good signature anchor, both positive kernel identities and the derivative
obstruction. There are34 passing hostile checks:9 opening,13 constructive,
and12 falsifier. These include geometric, arithmetic, signature, support,
polynomial, interval, margin and join corruptions.

## Accepted constructive result

For the inherited literal event and signature40418075143643136, a five-row
reserve remains a strictly positive normalized circuit while the original
three-row circuit loses rank. On the interval
`[-75255/222208,75255/222208]`, all70 parent signs persist; the smallest absolute
bracket is155. A full56 affine normalized witness has every coordinate at
least1/1000 throughout. These are polynomial identities and exact interval
inequalities, not sampling claims.

The separate curve
`h(t)=(u+C|t|q-t v)/(1+C|t|)` with
`C=2205884133/880139125` equals the original three-row vector exactly at zero
and enlarges to its six-row union away from zero. The referee verifies both
one-sided normal identities, exact normalization, positive denominator, and
nonnegative numerator for every real parameter. Original-parent scope stays
inside the certified interval.

The written conditional continuity lemma is correct: full row rank of the
augmented matrix and a strictly positive full-coordinate feasible vector
give feasible approximants, and compactness/uniqueness imply continuity of
the Euclidean minimizer. The fixture verifies those hypotheses. This is a
standard local convex-feasibility argument, with no novelty claim and no
global extension assumption. See CONSTRUCTIVE_AUDIT.md for detail.

## Accepted negative result: a continuous selector need not exist

The falsifier supplies a new literal uniform rank-four parent on eight
elements and a single fixed realizable signature1110781293763710. All70
parent brackets are independently nonzero. At the center, all signed
normals evaluated at e4 are positive except rows `[0,19,23,28,42]`, where
they vanish. Every normalized nonnegative dependence therefore has support
within those five rows.

Their exact rank is three, and their normalized feasible fiber is the segment

```
r0 = (200,32,10,25,0)/267
r1 = (1900,152,95,0,200)/2347.
```

Independent nullity and coordinate checks prove this is the complete fiber,
not merely two selected witnesses. The dot product
`r0 dot (r1-r0)=5027435/167315283>0` proves that r0 is its unique Euclidean
minimum.

There are two independently checked bad paths, both inside this same strict
parent chamber for `0<t<=10^-6`. Along each, exact positive five-row kernel
polynomials prove badness throughout the interval. Their alternating minors
are nonzero for positive t, so those five rows have rank four. All51 signed
last coordinates outside the central zero support remain strictly positive.

Let `d=(0,-2,2,2,-2)`. If normalized witnesses along the first path converge
to w at the center, the last-coordinate equality gives
`d dot w<=0`: move the nonnegative outside-support terms to the other side,
divide by positive t, and take the limit. Along the second path the derivative
is `-d+(1/89)1`, so the same argument gives `d dot w>=1/89`. Any continuous
section at the center would have to have the same limit along both paths.
The inequalities are incompatible. Hence:

**There is no continuous normalized nonnegative Gordan-witness section on
any relative neighborhood of this center in its full bad locus.**

In particular, the minimum-norm selector is discontinuous: its central value
r0 has `d dot r0=2/89>0`, excluding even approach along the first bad path.
The no-section theorem is stronger and does not depend on Euclidean norm.

## Admissibility and gauge review

The same fixed signature has an independently verified good path in the
same parent chamber. At t=10^-6, the explicit primal e4 has all56 strict
signed margins positive, with minimum `1999997/2000000000000`. Thus it is
a realized uniform extension signature; the good and bad loci are both
nonempty. Its admissibility is not inferred merely from a bit string. The
connecting good path and both bad paths keep the parent's entire chirotope,
so the constructed anchors are in the same parent component.

The literal proof requires no gauge quotient. The first four parent columns
have positive determinant2 at the center, so ordinary continuous GL4 basis
normalization is valid nearby and transforms all normals by one common
invertible positive-determinant cofactor map. This leaves witness weights
unchanged. Further regular positive column rescalings multiply each triple
normal by a positive continuous factor c_i, with normalized fiber map
`w'_i=(w_i/c_i)/sum_j(w_j/c_j)`. This is a continuous invertible map of fibers.
A continuous selector after such a normalization would pull back to one
before normalization, contradicting the proved obstruction. Consequently
the no-section obstruction survives any such regular local normalization.

No explicit coordinates in the repository's full nine-dimensional canonical
gauge were supplied or numerically checked. The transfer is the written
continuous-fiber-isomorphism argument above. Euclidean minimum itself is
preserved by the common GL4 normal transformation, but is not asserted to
be preserved by nonuniform positive row scaling.

## Precisely excluded route and surviving scope

The result refutes an unconditional premise that one can continuously choose
a normalized Gordan witness locally at every bad parent. It therefore rules
out using such a selector as a universal ingredient without additional
hypotheses. The constructive reserve theorem survives: its strict-positivity
hypothesis fails at the falsifier center, whose feasible vectors have51
forced zero coordinates.

The new parent/signature was not shown to lie in the inherited fixed
three-signature family, and no three-signature antichain was constructed.
It is not a counterexample to the original joint Hc1 restriction map, a
compact component, or diagonal-three vanishing. Acyclic multivalued fibers,
stratified comparisons and homological attachment arguments are not
disproved. No global atlas, original source census, true-infinity model or
cohomology matrix was computed.

The discovery search extent is recorded by the falsifier as1371 derivative
targets on one lifted-grid parent. The referee verifies the final certificate,
not the completeness or exact numerical ordering of that discovery search.
Constructive fixed-family admissibility is inherited from the pinned source;
the distinct new falsifier signature is directly replayed here.

The coordinator must still bind final artifact bytes, save a durable
checkpoint, and perform the separately authorized publication workflow.
This review claims neither a remote update nor completion of those tasks.
