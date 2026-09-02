# D3 global SREP Q0 topology-falsifier report

Frozen opening: `c50da6c99d465c65b3e54427418d9efe6a3f037e`

Verdict: **`CANARY_PACKAGE_SOUND_PRODUCER_NOT_YET_REVIEWED`**.
The independent canary package passes, and all `23/23` hostile mutations are
rejected.  This is a falsifier-lane result only.  It does not accept a
replacement backend, open Q1, or earn theorem credit.

## M3 compact filled/unfilled pair

Let the standard tetrahedron in `R^3` have barycentric polynomials

```text
lambda_0 = 1-x-y-z,  lambda_1 = x,  lambda_2 = y,  lambda_3 = z.
```

Every fixture face is given by the four weak inequalities
`lambda_i >= 0` and the exact equalities for the complementary vertices.
Thus every term is a closed bounded integer-polynomial formula.  Write
`F_ijk` for a triangular face and `E_ij` for an edge.  The two source
formulas are

```text
X_unfilled = F_012 union F_013 union E_23,
X_filled   = F_012 union F_013 union F_023,
I          = {v_3} (tagged true parent infinity).
```

Both objects have exactly the `K4` one-skeleton and hence the same complete,
accepted exit graph to `v_3`.  The checker regenerates every face and signed
incidence from the formula-indexed maximal faces; it does not accept the
reported chain ranks on trust.  Over `Q`, relative to `I`, it obtains

| model | dim C0 | dim C1 | dim C2 | rank d1 | rank d2 | dim H1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| unfilled | 3 | 6 | 2 | 3 | 2 | 1 |
| filled | 3 | 6 | 3 | 3 | 3 | 0 |

Both products `d1*d2` vanish.  This is a polynomial realization of the M3
warning: an accepted exit graph and a shared one-skeleton do not determine
pair `H1`; the two-cell trace is indispensable.

## M2 tangential first-exit pair

The fixture uses the exact compact rectangle `-1 <= s <= 1`,
`0 <= u <= 2` and the selected formula

```text
(s = 0 and u < 1) or (s != 0 and u < 2).
```

It then adds only the pointwise terminal set `(s=0,u=1) or u=2`.  For every
integer `n >= 1`, `(1/n,3/2)` is selected, while its limit `(0,3/2)` is in
the ambient rectangle but in neither the selected nor terminal set.  Hence
the pointwise union is nonclosed; because the whole base is compact but its
preimage is not compact, the restricted projection is not proper.

The missing central interval `s=0, 1<u<2` is an artificial jump frontier,
not true parent infinity.  The genuine parent-infinity formula is `u=2`.
After ambient closure, the central fiber pair is `([0,2],{1,2})`; its exact
relative chain has two edges, one surviving vertex, boundary rank one, and
`H1 = Q`.  The checker therefore rejects both weak-closure substitution and
relabeling the jump frontier as infinity.

## Single-bad control binding

The package pins and executes
`ai/omreal/verify_diag3_single_bad_two_skeleton.py` at SHA-256
`0ae6a9d54abcddbeb68be882083c52e1e6a9735941cea42eebacdf91ef77bda4`
and pins its theorem memo at
`141da1b6d9fcd4f601e79871aaa5d06cb98721ece928a0d0d5af83518bddf71f`.
An independent bounded-composition replay recovers forced motion dimensions
`3,2,1` for face dimensions `0,1,2`.  The binding is explicitly single-bad
only; mutation of that scope into a pair/triple claim is rejected.

## Hostile pass

The `23` mutations cover all opening-mandated classes and more:

- strict-to-weak closure corruption and inclusion of the missing limit;
- artificial or wrong-vertex infinity tags;
- formula/complex disconnects and a polynomial coefficient drift;
- omitted formula tags, edge faces, and trace faces;
- false ranks, false `H1`, a flipped incidence (`d^2 != 0`), and a duplicate
  simplex ID;
- hand-authored-complex substitution and filled/unfilled conflation; and
- broken single-bad pins, support ranks, and scope.

`RESULT.json` records each mutation and its fail-closed reason.  No producer
file or producer acceptance function was read or imported, no cloud resource
was activated, and no canonical or cycle surface was edited.

## Replay

From the repository root:

```console
python -B ops/team/d3-global-srep-falsifier/falsify_canaries.py
python -B ops/team/d3-global-srep-falsifier/falsify_canaries.py --json
```

The first command exits zero only if the baseline and all hostile mutations
pass.  Expected compact output is preserved in `TEST_OUTPUT.txt`.

## Scope boundary

These exact canaries are necessary tests for a proposed formula-derived
replacement trace.  They are not an implementation of the
Basu--Karisani construction, do not certify the complete global tagged
schema or its forecast, and do not accept any producer output.  Q0 and the
theorem ledger therefore receive no credit from this lane.
