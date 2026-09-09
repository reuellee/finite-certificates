# Backward detector constructive track: canonical maps, no nondegeneracy

**Original target: NULL.** Base
`730fd6c7b6c2c3e8cbbf94ab4da3bc97ba53f095`.
Owned surface: `ops/team/d3-detector-prover/`.

The candidate detector is now canonical: for the single-exclusive stratum
`C_i=B_i minus (B_j union B_k)`, a closed-cover connecting map followed by
localization gives

    tau_i : Hc1(T) -> Hc3(C_i),
    ker tau_i = im r_ij + im r_ik.

It automatically kills both unwanted pair images. The actual alternating
pair map is injective if and only if all three opposite-pair maps
`kappa_i=tau_i r_jk` are injective. The full proof, exact sign conventions,
relative cochain formula, and quantifiers are in `BOUNDARY_DETECTORS.md`.
Only the proved `Hc2(B_i)=0` is needed; the still-open triple `Hc0` theorem
is not assumed.

**What remains:** no geometric proof that a nonzero opposite-pair class has
a nonzero three-dimensional trace in `C_i`. That nondegeneracy condition is
equivalent to the original pair target. The canonical construction is an
auxiliary deductive result, not a strict decrease, and supplies no entries
of the original oriented frontier blocks.

The competing one-boundary route first encounters a genuine variance issue:
the exclusive pair is closed in `B_i minus B_j`, so cohomology restricts
toward it. A selective lift in the reverse direction has the explicit
degree-three localization obstruction and degree-two ambiguity recorded in
the proof. An arbitrary section would not automatically kill both rivals.

A dependency-free exact tiny geometry check establishes that preserving
selected support-plane rays does not preserve omitted normal rays, even in
a uniform eight-column parent and without changing any parent bracket sign.
It does **not** assert an admissible signature, a positive selected Gordan
witness, a feasibility flip, or a D3 counterexample. This is a discriminator
of an extrapolation in the proposed proof, not a detector impossibility
theorem. The falsifier's separate admissible triple-bad-stalk result has its
own independent scope and is not used as a premise of the proof here.

Replay from the repository root:

    python -B ops/team/d3-detector-prover/verify_selected_plane_transport.py

The replay output is `GEOMETRY_REPLAY.json`. It reconstructs all relevant
rational data with the standard library and rejects the false assertion
that the omitted normal remains proportional. Source bytes match every
opening-manifest hash. There is no discovery-side checker for the topology;
that proof requires independent mathematical review.

Discovery stopped at the structural null when no global candidate could
meet the original-obligation decrease. No signing census, new atlas, paid
compute, external write, or subagent was used. Certificate writing and
review preparation continued after that stop. All seven original
obligations remain open; ledger 2/9, pair coverage/residual UNKNOWN, and
triple accounting unchanged.
