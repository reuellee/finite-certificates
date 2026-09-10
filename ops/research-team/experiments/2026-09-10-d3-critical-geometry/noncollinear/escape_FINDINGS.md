# Shared-plane witness extension

The new both-nonzero-gradient witness has a global escape. Its full support
triple is an explicit rational graph over an open subset of R6, proved in
`escape_global_graph.md`. Independent falsifier/referee arithmetic agrees.
The same triple already has a light-label/affine-fiber escape, so this is
zero new source coverage and zero original-diagonal credit.

There is a more precise critical classification. In its full ordinary P48
contraction chart, the vertical critical locus is exactly the closed
projected-parent locus{x=2,z=5}, intersected with the Q wall. Over this locus,
[1234]R=-[1245]Q is an identity in every height variable. The proof retains
all uniform parent signs and every projected/height specialization.
`escape_critical_classification.md` states the chart and proof; the exact
coefficient identities are checked in `escape_GLOBAL_REPLAY.json`.

The abstract step `escape_redundant_height.md` proves H_c^0 vanishing for any
closed projected-base piece where two other factors are proportional by
specified parent units as full height polynomials. Retaining the ordinary
concurrence gives at most four affine equations in five heights, so every
nonempty full fiber has positive dimension. Concurrence collision with the
anchor is included separately. Finite closed unions can be excised.

A shared factor alone is insufficient. A componentwise version needs an
explicit closed selected piece containing either the whole concurrence
fiber or none of it. No automatic saturation or new global critical
classification is asserted outside this source triple.

The previous frozen FINDINGS/HANDOFF were left unchanged. These extension
artifacts are separately hashed in escape_HANDOFF.json. Original2/9 and the
unresolved general triple endpoint remain unchanged.
