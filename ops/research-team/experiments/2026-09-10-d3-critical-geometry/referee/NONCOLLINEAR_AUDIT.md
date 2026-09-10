# Independent acceptance: criticality need not imply collinearity

The exact witness in `noncollinear/NONCOLLINEAR_CRITICAL_WITNESS.json`,
SHA256 `54ce3f8b0206e47a43475506d5ec684e42d2da189348a4a170b2952814400041`,
refutes the unqualified implication that dependent vertical gradients force
the three fixed ordinary concurrence points to be collinear.

`verify_noncollinear_independent.py` reconstructs the original parent and
all70 brackets using standard-library rational determinants. It verifies
every ordinary three-row rank, the distinct projective points
(1,2,2,0), (1,2,0,0), (1,7,7,0), and their span rank three. It obtains the
eight-height derivatives from exact quadratic finite differences, without
importing the producer's circuit-gradient routine. One derivative vector
is zero and the other is nonzero, so their rank is one. Relabeling checks
place the three factors in the distinct global kinds48,36,49. Perturbing
the claimed concurrence or a parent coordinate is rejected.

The source's ordinary/global-kind equivalences are inherited inputs; the
exact point and gradient arithmetic are independently rebuilt here.
NONCOLLINEAR_INDEPENDENT_REPLAY.json records the results. No claim that
both individual gradients are nonzero is made.

The checker additionally reconstructs the localization core123/356/378.
It has rank two, annihilates both the P anchor and central parent3, and
therefore places this witness in the proposed closed localization-axis
piece. The point consequently provides a useful failure of the proposed
classification, not a counterexample to global triple noncompactness or
original injectivity. No diagonal promotion or new source-orbit count is
approved by this result.
