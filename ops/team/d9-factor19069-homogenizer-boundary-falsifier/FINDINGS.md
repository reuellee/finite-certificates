# Independent falsifier findings: factor-19069 homogenizer boundary gate 1

## Classification

`INDEPENDENT_EXACT_FALSIFIER_BASELINE_PASS_CONSTRUCTOR_CLAIMS_UNEVALUATED_FAIL_CLOSED`

The lane independently reconstructs the exact source and the attack surface,
but it does not evaluate a current-cycle constructor artifact.  Every
constructor-dependent branch classification therefore remains unavailable and
fail closed.  This is not a positive, negative, null, or timeout endpoint for
the governed cycle, and it does not change the `2/9` theorem ledger.

## Exact reconstruction

The affine factor is rebuilt from the pinned mathematical factor source rather
than from constructor output.  It has 108 terms and the pinned sparse digest
`041227c22bc01ca80df8a66a46099b2f703c53a310fe737dac3981bda5ee20c4`.
Sparse integer trihomogenization gives a 108-term polynomial of multidegree
`(2,2,2)` in `Q[a,b,c,u,d,e,f,v,g,h,i,w]`, with exact dehomogenization back to
factor 19069.

All seven boundary types are reconstructed in the prescribed deepest-first
order `uvw, uv, uw, vw, u, v, w`.  Each record contains the full restricted
source polynomial, the twelve derivative-before-restriction specializations
needed for ambient singularity, and the restrict-then-differentiate tangent
derivatives needed for singularity inside the stratum.  The tangent lists are
proved equal term by term.  The normal derivatives are separately retained;
discarding them would conflate ambient and stratum singularity.

At `u=v=w=0`, the exact 11-term identity is

`-h*(a*f-c*d)*(a*e*i-a*f*h-b*d*i+b*f*g+c*d*h-c*e*g)`.

The three factor multiplicities in this polynomial are exactly one.  The
required set-theoretic pair seeds are `(h,a*f-c*d)`, `(h,det)`, and
`(a*f-c*d,det)`.  They are retained as seeds only: no radicality, primary
decomposition, singular-scheme multiplicity, affine pullback, or parent-cell
classification is inferred from the source factorization.

The exact parent reconstruction further proves the signed identities

- `H_08_1248 = h`, so the first displayed factor is `-H_08_1248`;
- `H_22_1367 = -(a*f-c*d)`, so the second displayed factor is `-H_22_1367`;
- `H_34_1678 = a*e*i-a*f*h-b*d*i+b*f*g+c*d*h-c*e*g`.

Their product equals the deepest restriction exactly.  Consequently, every
point of the `uvw` restricted hypersurface—and hence each of its three
required pairwise singular seeds—is excluded from the strict row-2599 parent
domain by at least one of parent factors 8, 22, and 34.  This closes the exact
strict-parent exclusion of the deepest source-factor branches.  It does not
certify a radical/primary decomposition of the deepest ambient singular
scheme and does not say anything complete about ambient singular branches in
the other six types.

The product-chart atlas is reconstructed combinatorially: 64 standard charts,
4,032 directed overlaps, and 279 boundary type–chart incidences.  The incidence
counts in deepest-first order are `27, 36, 36, 36, 48, 48, 48`.  Every directed
overlap records nonempty source and target unit sets.  Any future quotient of
branch representatives must provide those invertible overlap units and the
exact transition identity; no deduplication is accepted merely from matching
labels, dimensions, or sampled points.

All 70 parent factors are reconstructed in source order from the pinned
row-2599 parent record, including exact signed sparse polynomials and node
identities.  No parent exclusion is complete before exact affine contraction,
and no branch may receive a strict-real or connected-parent tag until all 70
parent factors and the relevant residence/component certificates are present.

## Hostile attacks

The deterministic verifier rejects 59 mutations.  The attacks cover source
and revision drift, omission or reordering of boundary types, altered
restrictions, derivative-order reversal, loss of normal derivatives,
conflation of ambient and stratum singularity, dropped factor seeds, changed
factor multiplicity, unjustified radicality, chart or incidence omissions,
deduplication without invertible overlap units, parent-factor omission or
reordering, false affine contraction, incomplete all-70 testing, false
strict-real or connected-parent tags, endpoint inflation, retired routes,
resource-ceiling drift, ledger promotion, Drive use, and GitHub writes.

## Nonconsequences

- No complete seven-type singular decomposition is certified.
- No branch is certified projective-infinity only or as an affine pullback.
- No dimension, degree, or singular-scheme multiplicity is asserted beyond the
  exact source-factor records.
- No strict real survivor or connected row-2599 parent tag is certified.
- No universal diagonal certificate or theorem-ledger promotion is supported.
- No numerical, modular, sampled, network, Google Drive, or GitHub inference
  was used.
