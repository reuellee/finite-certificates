# Falsifier findings: factor-19069 explicit trihomogeneous Jacobian charts

## Verdict

`ACCEPT_EXACT_BOUNDED_TIMEOUT_FRONTIER_FAIL_CLOSED`.

The constructor frontier is exact through the complete 64-chart source and
Jacobian setup, then stops honestly at the first characteristic-zero
decomposition prerequisite, `DEC-JCH-00-a-d-g`.  It does not provide a
complete projective component decomposition, an affine contraction, a
componentwise 70-factor incidence classification, a strict-real/connected
tag, or a theorem-ledger change.

## Independent reconstruction

This lane imports no constructor code or constructor acceptance logic.  From
the pinned row-2599/factor-19069 mathematical source it independently rebuilt:

- the 108-term affine polynomial, sparse SHA-256
  `041227c22bc01ca80df8a66a46099b2f703c53a310fe737dac3981bda5ee20c4`;
- its canonical 108-term `(2,2,2)` trihomogenization in coordinate order
  `a,b,c,u,d,e,f,v,g,h,i,w`, sparse SHA-256
  `6a6e542fe12544e65f1db2fe35da4c5065ec20fa5265447f36b2fbc0d16f2ec5`;
- exact dehomogenization at `u=v=w=1` to the pinned affine polynomial;
- all `4*4*4=64` standard product charts in stable lexicographic pivot order;
- on each chart, `F_chart` and its nine free-coordinate derivatives;
- all 192 pivot-derivative Euler recoveries by the exact degree-two identity,
  with zero sparse residual;
- the affine-chart equality between `<F_chart,nine derivatives>` on
  `JCH-63-u-v-w` and the original affine singular ideal;
- all 70 ordered parent factor records and their pinned source tags.

The independent chart-atlas semantic SHA-256 is
`78d1b298cdaf32d6edf01b5e2b9b5ce6ee649ddf1f7758cb77e71dd985f55aa2`.

## Boundary and overlap attack

A chart whose pivot is an original coordinate is not wholly at infinity.  It
contains an affine overlap where its free homogenizer is nonzero and a
boundary divisor where that homogenizer is zero.  The verifier therefore
rejects chart-level affine/infinity conflation.

For a chart with `k` free homogenizers it requires all `2^k-1` nonempty local
boundary intersections.  The exact census passes: 63 boundary-capable charts,
279 chart-local boundary-stratum records, and all seven global nonempty
subsets of `{u=0,v=0,w=0}`.  No boundary stratum is discarded.  The complete
directed chart-overlap census also passes at `64*63=4032` records.

## Decomposition and incidence guard

The first chart's exact Gröbner prerequisite reached its bounded wall-time
ceiling.  A Gröbner basis was not mislabeled as a primary decomposition.  The
frontier records zero accepted projective components, zero affine
contractions, and zero component-parent factor pairs.  Consequently no
uncontracted or invented component receives a 70-factor test.  The 70 parent
records remain source-tagged pending data rather than false incidence claims.

## Hostile replay

All 53 hostile mutations were rejected.  The mutations cover source drift;
missing charts and pivot swaps; polynomial and derivative deletion/sign/
coefficient errors; Euler coefficient, reconstruction, and residual errors;
affine-transfer mismatch; boundary erasure and infinity conflation; overlap
loss; false complete decomposition; fake component, contraction, and parent
test claims; parent-tag drift; strict-real/connected overclaim; prohibited or
inexact routes; endpoint drift; and ledger promotion.

Mutations are targeted and reversible.  The 21 MiB frontier is parsed and
fully validated once; hostile checks mutate only the relevant field, replay
the exact local invariant, and restore it immediately.  This keeps the audit
within the falsifier ceiling without weakening the tested predicates.

## Nonconsequences

The ledger remains `2/9`.  There is no complete characteristic-zero chart
decomposition, embedded-component census, overlap-deduplicated component
list, accepted affine contraction, componentwise 70-factor classification,
strict-real/connected component, strict-parent singular-emptiness proof,
theorem-level counterexample, diagonal-9 theorem, or 9DVL score change.
