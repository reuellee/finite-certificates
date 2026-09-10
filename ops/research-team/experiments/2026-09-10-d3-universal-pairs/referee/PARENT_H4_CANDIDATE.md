# Scoped candidate: parent fourth-homology vanishing

Status: proposed deductive corollary, requiring a different agent's review. The referee is its author and does not independently approve its own claim. It closes no original diagonal. Its purpose is to remove the blanket parent-contractibility dependency from the fifth-diagonal bad-locus formulation.

**Candidate.** Every normalized realization component X of a realizable uniform rank-four oriented matroid M on eight labels satisfies H_4(X;Q)=0.

The only new step is the following seven-label variant of the inherited positive-coordinate-face proof in `checkpoint/checkpoint/inputs/DIAG3_SINGLE_BAD_TWO_SKELETON.md`.

**Seven-label one-bad lemma.** In a normalized realization space D of a uniform rank-four parent on seven labels, the strict-infeasibility locus B for one fixed signed extension system has H_c^0(B;Q)=H_c^1(B;Q)=0.

Use the full normalized positive Gordan resolution, whose projection to B is proper with nonempty compact convex fibers. Filter by positive coordinate supports U and augmented rank, exactly as in the inherited proof. A relative-interior face of dimension k has |U|<=5+k and contributes compact-support degree n through H_c^(n-k)(D_(U,k);O_(U,k)), with its face-orientation system. Only k=0,1 can contribute when n<=1.

For k=0, the support has at most five triples, hence at most fifteen incidences on the seven labels. If any label has degree zero or one, retaining its incident plane when needed gives a full open residence fiber of dimension at least two. There are at least six fixed other labels, so a fixed five-label projective frame is available. Otherwise all seven degrees are at least two. If at most one were equal to two, the incidence count would be at least 2+6*3=20, a contradiction. Thus two labels have degree two. Apply the inherited two-pencil theorem: retain the five other parent columns as a projective frame and all incident support-plane rays. The residence fiber is an open subset of the product of two projective pencil intervals. Every bracket is affine in either parameter separately; its sections are intervals. Every connected fiber component projects onto an interval and has interval sections, hence retracts onto that interval and is a contractible oriented open two-manifold. The proof includes support planes containing both moving labels.

Positive rescaling of the support normals identifies the entire normalized witness face by inverse rescaling of its coordinates followed by normalization. This preserves positive support, face dimension and the orientation local system. Therefore the exact face stratum is fiber-saturated and the orientation system descends. Use an ambient locally closed quotient stratum allowing empty fibers, as in the accepted common-weak proof, instead of assuming an arbitrary projected image is locally compact. Shriek base change gives H_c^j(D_(U,0);O)=0 for j=0,1.

For k=1, at most six triples give at most eighteen incidences. Some label has degree at most floor(18/7)=2. Its full residence motion has positive dimension and reaches the parent-residence boundary. This retains exact positive support and face dimension, so each component of D_(U,1) is noncompact. A compactly supported locally constant section, with the inherited rank-one orientation system, must therefore be zero. Hence H_c^0(D_(U,1);O)=0.

All terms in total degree zero or one vanish. The same finite support/rank closed filtration and proper comparison as in the inherited proof yield the seven-label one-bad lemma. No finite support census is required.

Now delete one label e from M. The normalized deletion realization space D has dimension six and is contractible by duality to the inherited rank-three/seven-label theorem. Insertion of e gives a map from R(M) to its nonempty-insertion locus G in D. After a fixed projective normalization, insertion fibers are open convex residence three-cells; local sections and partition of unity give R(M) homotopy equivalent to G. The complement B=D minus G is exactly the one-block insertion-bad locus considered above. Poincare duality with supports and the homology sequence of (D,G) give

    0 = H_5(D;Q) -> H_c^1(B;Q) -> H_4(G;Q) -> H_4(D;Q) = 0.

Thus H_4(R(M);Q)=0 and hence H_4(X;Q)=0 for each component. The same argument in degree zero repeats the already inherited parent H_5 vanishing and receives no new credit there.

Together with inherited H_i(X)=0 for i>=5, the candidate would validate

    H_4(F_S;Q) = H_c^4(union_(sigma in S) B_sigma;Q)

for |S|=5, without the blanket contractibility statement for exceptional parents. It says nothing about vanishing of this group, and it supplies neither D3 injectivity nor D3 triple noncompactness. It is not a route selection or a theorem-ledger promotion.

Review dependencies: the inherited two-pencil quotient, proper positive-face filtration including augmented-rank changes, rank-one coefficient descent, and the accepted rank-three/seven-label deletion-space contractibility. No additional published blanket small-ground-set contractibility theorem is used.
