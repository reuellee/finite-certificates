# Independent deductive acceptance: the collision-free critical reduction

Reviewed `proof/VERTICAL_CRITICAL_REDUCTION.md`.
SHA256: `e7034f7b3b51fad14e925eeabed3a43cf134e72a1a3689fede5b4ac28b69477e`.

Verdict: ACCEPT as the stated reduction, not as a proof of its remaining
critical-locus hypothesis. It applies to all six factor kinds and all
original parent components through the independently reviewed ordinary
anchor construction.

The regular-locus submersion proof is correct: independent vertical
gradients give an open image in the global open four-dimensional affine
projected-parent base. Every regular semialgebraic component is therefore
noncompact. The proof uses closed/open localization in the correct order:
first remove the full closed union Delta of the three concurrence-collision
loci, then separate the regular and closed critical loci inside Z minus
Delta. It does not assume that K intersect Delta has vanishing Hc0.

The collision proof is accepted separately in
COINCIDENCE_EXCISION_AUDIT.md, including re-anchoring for q=r and all lower
coefficient ranks. The remaining sufficient statement is precisely

    Hc0(K minus Delta; Q) = 0.

The pole-free differential formula is also correct. At rank three the
adjugate of a four-by-four normal-row matrix is a nonzero scalar multiple
of its right kernel times its left kernel. Pairing the adjugate with the
row derivatives gives the displayed circuit-weighted determinants. The
three shears and one scale give four independent gauge directions, each
annihilated by these differentials on the wall. Thus rank in the
eight-height dual space equals rank in the four-dimensional normalized
vertical cotangent space. Unit changes and nonzero choices of kernel
representatives only rescale the individual gradient vectors.

The inherited critical canary was reconstructed independently with integer
determinants. `verify_critical_canary.py` checks all70 parent brackets and
all three ordinary rank-three concurrences. It computes the16 vertical
derivatives by symmetric finite differences, exact here because no parent
occurs more than twice in either occurrence. This avoids importing or
reusing the producer's circuit-gradient routine. A separate sparse integer
polynomial multiplication proves the global q39 syzygy. Output is
CRITICAL_CANARY_REPLAY.json; the canary is a collision and its triple wall
is a pair wall, so it receives zero new triple count.

No implication from vertical criticality to collinearity is proved by the
reviewed text. Even that implication would not by itself give an escape
for distinct collinear concurrences. The rank-six compatibility locus and
the collision-free critical locus remain actual open global targets.
