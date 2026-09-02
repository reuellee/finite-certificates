# Factor-19069 saturated critical equidimensional constructor findings

## Endpoint

The constructor reaches the preregistered null endpoint
`HASH_PIN_FIRST_UNRESOLVED_SATURATED_IDEAL_BRANCH`, classified
`EXACT_FAIL_CLOSED_SATURATED_EQUIDIMENSIONAL_DECOMPOSITION_NULL`.  The exact
saturated critical ideal is reconstructed as a provenance-preserving inverse
extension, but no critical branch receives a dimension, degree, multiplicity,
or real-component classification.  The theorem ledger remains `2/9`.

The first unresolved branch is
`EQ-B00-SINGULAR-DF-ZERO`, semantic SHA-256
`66f71350e7b0a2578997a388be43ae0547c8786c7206af056806eaaef3e516d9`.
Its exact equidimensional decomposition over `Q`, followed by strict-real
parent-component residence, is the first pending obligation.  Later regular
gradient charts are retained but cannot be reported as a decomposition while
this first branch is unresolved.

## Exact saturation without barrier expansion

The accepted standard-library builder rechecks the frozen predecessor SHA-256,
reconstructs every sparse derivative, and preserves all 70 ordered signed
parent factors.  The degree-90 barrier remains only the ordered product
circuit `B=PRODUCT_i H_i`; it is never expanded.

For each factor the artifact introduces an inverse variable `y_i` with

```text
H_i*y_i - 1 = 0.
```

The resulting extension is exactly
`Q[x_0,...,x_8,(PRODUCT_i H_i)^(-1)]`.  Its nine logarithmic-gradient nodes are

```text
L_k = SUM_i y_i*(dH_i/dx_k).
```

The 36 localized critical equations are

```text
L_i*(df/dx_j) - L_j*(df/dx_i) = 0,  i < j.
```

In the inverse extension, `dB/dx_k=B*L_k`; hence each original wedge
coefficient is `B` times the corresponding localized wedge coefficient.  Since
`B` is a unit there, contraction back to the nine base variables is precisely

```text
<f_19069, coefficients(dB wedge df)> : (PRODUCT_i H_i)^infinity.
```

This is an eliminationally faithful saturation witness, not a geometric
coordinate projection.  The circuit contains 70 inverse relations, 630
source-derived log-gradient summands, nine log-gradient sums, and 36 localized
wedge nodes.

## Singular and regular branch frontier

A replacement of `L wedge df=0` by `L=lambda*df` would lose points with
`df=0` unless it separately retained that singular branch.  The artifact does
not use the lambda replacement.  Its first closed branch has the 80 exact
generators

```text
f_19069;
H_i*y_i-1 for i=0,...,69;
df/dx_k for k=0,...,8.
```

All wedge equations are redundant on this branch, but the branch itself is not
discarded.  The remaining nine locally closed charts use the lexicographically
first nonzero wall derivative: earlier derivatives are set to zero, the pivot
derivative receives an explicit inverse, and the eight pivot wedge equations
are retained.  Together the singular branch and those nine charts give an
exact set-theoretic cover of the localized critical locus.  No scheme-level or
equidimensional decomposition of that cover is claimed.

The raw nonzero degree-six wall equation defines an affine hypersurface of
dimension eight before critical equations and saturation.  That contextual
hypersurface dimension/degree does **not** resolve the dimension or degree of
any critical branch; every critical-branch dimension, degree, and multiplicity
field remains null.

Two exploratory SymPy 1.14 Gröbner probes of the singular generators (one over
`Q`, one modulo 32003) emitted no basis before bounded termination.  Their
processes were stopped, their dependency is absent from the accepted replay,
and they support no dimension, degree, multiplicity, characteristic-zero, or
real-residence claim.  There is no blind algebra-budget escalation.

## Real parent component, boundary, and fixed null frontier

Complex saturation only enforces `H_i != 0`; it does not select the strict real
sign cell or its connected component.  The artifact therefore retains all 70
strict inequalities and the source-derived requirement for an exact path in
that sign set to the pinned row-2599 parent sample.  Any later positive-
dimensional complex piece must still supply an exact real point and that path
certificate before it can count as a real strict critical component.

All 3,375 compactification support strata remain accounted for.  The 3,364
Bernstein-excluded strata and all ten proper nonexcluded candidates are copied
with their exact restrictions and parent-path data; eight candidates have
identically zero factor-19069 restrictions and two have mixed restrictions.
No boundary wall-germ residence is promoted.

The 40-edge skeleton accounting and verified null frontier are also preserved.
Edge 39 still has the unique exact open factor-19069 root, but that point is an
attached wall anchor, not a barrier-critical sample, and it yields no global
component or attachment count.  Connected-component samples remain zero.

## Verification and scope

`build_critical_equidim_frontier.py --check` reproduces the manifest, frontier,
and result byte-for-byte using bundled standard-library Python.
`verify_critical_equidim_frontier.py` reconstructs the sparse derivatives and
localization and rejects 22/22 hostile mutations covering source, factor,
barrier, saturation, wedge, singular, dimension, degree, multiplicity,
boundary, real-residence, edge-39, endpoint, semantic, and ledger drift.

This is not an equidimensional decomposition, a zero-dimensional proof, a
complete real-root frontier, a positive-dimensional real critical component,
a global factor-19069 wall classification, a diagonal-nine theorem or
counterexample, or evidence for changing the `2/9` ledger.
