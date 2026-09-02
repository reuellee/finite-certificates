# Factor-19069 singular-df multihomogeneous falsifier

## Verdict

The falsifier lane passes, but the proposed structural premise is **rejected
exactly and fail closed** before decomposition.  An independent replay of the
pinned factor source reconstructs all 108 terms of `f_19069` in
`Q[a,b,c,d,e,f,g,h,i]` and all nine formal derivatives.  The polynomial has
maximum block-degree tuple `(2,2,2)`, but that tuple is only an upper bound:
the three affine block-degree supports are respectively `{1,2}`, `{1,2}`, and
`{0,1,2}`.  Its total-degree support is `{4,5,6}`.  It is therefore neither
total homogeneous nor block multihomogeneous in the stated affine ring.

The coordinate maximum exponents are `(2,1,2,2,2,2,1,2,1)`, so the source is
also not coordinate-multiaffine.  Exact counterterms include
`-c*e*h*i` (total degree 4 and first-block degree 1), `-c^2*e^2`
(third-block degree 0), and `a^2*f*h*i` (a squared coordinate).  A future
homogenized construction might possess useful structure, but no such
construction, chart relation, source map, or preservation proof is present;
this lane does not infer one.

## Singular ideal replay

The original ideal is rebuilt as exactly `J=<f_19069,df/da,...,df/di>`.  The
nine derivative term counts are `54,44,54,50,50,50,36,61,36`, and every sparse
derivative digest is pinned in `RESULT.json`.  This verifies the exact ideal
input without importing constructor code.  It does not certify a decomposition.

Because the mandatory block-structure claim fails, the stop rule fires before
characteristic-zero primary/equidimensional decomposition.  There are no
accepted component equations, embedded-prime claims, dimensions, degrees, or
multiplicities.  Zero of the required component-by-component 70-factor tests
are claimed complete.  Strict real residence and the connected row-2599 parent
tag remain unresolved.  No singular or boundary stratum is discarded.

## Adversarial coverage

The deterministic verifier rejects 59 hostile mutations.  Coverage includes
source pins and identity, derivative membership/terms/digests, false
homogeneity and multiaffinity, component or embedded-stratum loss, invented
dimension/degree/multiplicity, incomplete 70-factor incidence, false strict
real residence or connected-parent tags, prohibited inverse/numerical/sampled
routes, resource-ceiling drift, endpoint substitution, and ledger promotion.

## Endpoint and ledger

This is a null, pre-decomposition structural-premise rejection:
`STOP_BEFORE_DECOMPOSITION_AT_FALSE_BLOCK_STRUCTURE_PREMISE`.  It is neither
the positive singular-emptiness endpoint nor an exact negative singular
counterexample, and it is not a timeout.  Ledger delta is `none`; the honest
theorem ledger remains `2/9`.
