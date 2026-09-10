# Independent deductive acceptance: the collinear rank filtration

Reviewed `proof/COLLINEAR_RANK_ESCAPE.md`, SHA256
`c2d23c946339ade1d62a42ad4957492a7388f9d6f076d1f16ba4b8fece1d2443`.

Verdict: ACCEPT the stated full-triple closed-piece vanishing. First remove
the closed collinear pieces whose common line contains a parent; then the
rank-at-most10 collinear piece is closed in the remaining space and has
Hc0=0. The theorem does not prove noncompactness or emptiness of rank11
critical points and does not prove the noncollinear critical-locus theorem.

The proof was reviewed independently as follows.

1. The parent-on-line interval proof is valid for the full collinear locus.
   Its stronger criticality-preserving form was authored in this referee
   directory and independently accepted by the proof track in
   PARENT_SLIDE_REVIEW.md, hash b5b350cd4b5a31277ed8e081d974f1df45fc7df64f55e446db20bef79b4c1294.
2. For parent-free common line L, all transverse g_i are nonzero. The
   equations B_P b=0, B_Q a=0, B_R(a-b)=0 follow exactly from the relevant
   four-column determinants. Projected triple rank one gives a zero row and
   an automatic incidence; it is retained. Four independent shears and the
   actual nonshear uniform lift bound the stacked rank by11.
3. A P plane not containing L exists by independence of every three selected
   normals. Its projected rank-two condition depends only on g. The linear
   height functional b_i-ell_J(g_i) cannot vanish in the uniform residence,
   because that would be an original parent bracket zero. It annihilates
   all four shears and fixes the common scale. The resulting fiber is an
   open subset of affine dimension11-rank(M). Convexity is not needed and
   is correctly not claimed for the two-height parent inequalities.
4. No projected direction has multiplicity four: those parents would span
   at most a three-dimensional subspace. The rank-one-limit argument proves
   properness of PGL2 on the allowed ordered configurations with maximum
   multiplicity three. Hence the quotient is Hausdorff and fixed projected
   fibers are closed, including transitions between choices of three-point
   frame. The remaining finite sign/frame choices do not create compact
   quotients of noncompact affine components.
5. A positive-dimensional open affine fiber component is noncompact and is
   closed in its full fiber. A compact component of the full rank piece
   cannot contain it. The rank condition and the preceding deletion order
   are correct; the proof does not assume that an arbitrary intersection
   of a critical locus with one of these pieces has Hc0=0.

The companion COMMON_STRESS_RANK_IDENTITY.md is a valid linear-algebra
identity: the kernel of (u,v,w)->(v+w,u-w) is the common intersection of the
three row spaces. It correctly retains the rank11 block alternatives
(4,4,4) with common stress dimension1 and (3,4,4) with common stress
dimension0. A low-family root-pair coincidence makes its block rank at
most3; it does not justify assuming all blocks have rank4.

The referee-produced rank11 canary received independent reconstruction by
the proof track, using raw incidence determinants and exact finite
differences rather than the producer's circuit-gradient calculation. Its
all70 uniform brackets, three distinct collinear concurrences, rank11
matrix and rank2 vertical derivative matrix agree. It receives no source
count and refutes only an unconditional collinearity-implies-rank-drop
claim. The stronger critical-plus-collinear rank claim remains unproved.
