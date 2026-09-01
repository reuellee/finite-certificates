# Factor-19069 singular-df multihomogeneous constructor findings

## Endpoint

The constructor reaches the preregistered null/stop endpoint
`HASH_PIN_FIRST_UNRESOLVED_MULTIHOMOGENEOUS_SINGULAR_BRANCH`, classified
`EXACT_SOURCE_STRUCTURE_FALSIFICATION_FAIL_CLOSED_NULL`.  The mandatory first
check falsifies the selected route's literal affine source premise: the pinned
108-term polynomial in `Q[a,b,c,d,e,f,g,h,i]` is neither block homogeneous of
degree `(2,2,2)` in `(a,b,c)|(d,e,f)|(g,h,i)` nor multiaffine in those nine
affine coordinates.  The theorem ledger stays `2/9`.

The first unresolved branch is
`MH-B00-AFFINE-SOURCE-STRUCTURE-CONTRACT`, semantic SHA-256
`73be706424b840acac8130f703649621a3092844bfefd3d25aa765e44f49712d`.
The cycle's explicit constructor stop rule says to stop on source drift.  No
characteristic-zero component decomposition or componentwise saturation is
therefore claimed after this failed prerequisite.

## Exact affine source check

The sparse polynomial has total-degree distribution

```text
degree 4: 58 terms
degree 5: 39 terms
degree 6: 11 terms
```

and exact block-degree-vector distribution

```text
(1,1,2): 12    (1,2,1): 20    (1,2,2): 12
(2,1,1): 15    (2,1,2): 12    (2,2,0): 11
(2,2,1): 15    (2,2,2): 11
```

Thus the three block-degree sets are respectively `{1,2}`, `{1,2}`, and
`{0,1,2}`.  Exactly 97 of 108 terms do not have block degree `(2,2,2)`.
The lexicographically first exact counterexample stored in the frontier is

```text
- c*e*h*i, with exponent vector (0,0,1,0,1,0,0,1,1)
and block degree (1,1,2).
```

The per-variable maximum exponents are

```text
a b c d e f g h i
2 1 2 2 2 2 1 2 1
```

Exactly 44 terms contain at least one squared affine variable.  The first
stored counterexample is `c*e^2*i`, exponent vector
`(0,0,1,0,2,0,0,0,1)`.  Consequently the predecessor's stored
`multidegree=[2,2,2]` is an exact coordinatewise block-degree bound in this
affine chart, not an affine block-homogeneity assertion.

For completeness, the artifact constructs the unique termwise
trihomogenization obtained by adjoining one homogenizer per block and raising
every term to block degree `(2,2,2)`.  Setting the three homogenizers to one
recovers the pinned affine factor exactly.  This 12-variable reformulation is
recorded as source structure only; it neither restores affine multiaffinity nor
serves as a primary-decomposition certificate for the original nine-variable
Jacobian ideal.

## Original singular ideal and decomposition frontier

The constructor independently reconstructs all nine exact sparse derivatives
from the factor.  Their term counts in coordinate order are

```text
df/da 54, df/db 44, df/dc 54,
df/dd 50, df/de 50, df/df 50,
df/dg 36, df/dh 61, df/di 36.
```

The exact ten-generator ideal

```text
J = <f_19069, df/da, df/db, df/dc, df/dd, df/de,
     df/df, df/dg, df/dh, df/di>
    subset Q[a,b,c,d,e,f,g,h,i]
```

is stored with semantic SHA-256
`193f7c28db287eaebad524eb9b119d878e70e9d509c2158bc6dcf4f027e24ab2`.
No inverse variables occur in this reconstruction.  The decomposition did not
start after the mandatory source stop: component count, embedded-prime count,
dimensions, degrees, and multiplicities remain null.  Zero components and
zero component-factor pairs are reported as resolved; this is not an emptiness
claim.

## Parent-factor, boundary, and null-frontier preservation

All 70 ordered parent factors are retained with their complete exact sparse
polynomials and source hashes.  Their componentwise incidence and strict-sign
fields remain pending: 70 factor tests are required for each future exact
component, but the number of such components is presently unknown.  The
constructor did not introduce the prohibited 70 inverse variables.

All ten proper nonexcluded boundary candidates, the full 3,375 support-stratum
accounting, the fixed 40-edge/2,800-parent-tag skeleton accounting, and the
accepted predecessor null frontier are copied exactly and separately hash
pinned.  No singular, embedded, or boundary stratum is discarded, and no
edge-39 anchor is promoted to a singular or barrier-critical component.

## Verification and nonconsequences

`build_singular_df_multihomogeneous_frontier.py --check` reproduces the
manifest, frontier, and result byte-for-byte using bundled standard-library
Python.  `verify_singular_df_multihomogeneous_frontier.py` independently
reconstructs the exponent census, all nine derivatives, the natural
trihomogenization, all 70 factor sources, and all preserved boundary/null
records.  It rejects 34/34 hostile mutations covering source, structure,
derivatives, component/embedded claims, parent-factor incidence, strata,
scope, endpoint, resource, and ledger drift.

This result is not a characteristic-zero primary or equidimensional
decomposition, a component invariant certificate, a parent-factor saturation
classification, a strict real-residence result, a connected row-2599 parent
tag, a singular-branch emptiness theorem, a theorem-level counterexample, or
evidence for changing the `2/9` ledger.
