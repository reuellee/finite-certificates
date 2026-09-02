# Factor-19069 homogenizer-boundary constructor findings

## Endpoint

The constructor reaches the preregistered null endpoint
`FIRST_SOURCE_PINNED_UNRESOLVED_TYPE_OR_BRANCH_CLASSIFICATION`.  It completes
the exact source and Jacobian reconstruction for all seven nonempty
homogenizer boundary types, closes the deepest `u=v=w=0` type by exact pinned
parent-factor exclusions, and extracts one exact positive-dimensional
strict-parent-excluded branch at `u=v=0`.  The first pending branch is
`B-UV-01-unclassified-ambient-components`, semantic SHA-256
`2747fcc6923b44996bfe79c0d06d2f88169f9fedea465cdecaa3c104bcf6b8b5`.
The complete characteristic-zero component census of the remaining `u=v=0`
ambient singular ideal is not proved.  The theorem ledger remains `2/9`.

## Seven exact boundary restrictions

The lane reconstructs the 108-term degree-`(2,2,2)` polynomial solely from
the pinned predecessor frontier.  In required deepest-first order, the exact
restricted-source term counts are:

| zero homogenizers | source terms | inherited chart incidences |
| --- | ---: | ---: |
| `u,v,w` | 11 | 27 |
| `u,v` | 37 | 36 |
| `u,w` | 23 | 36 |
| `v,w` | 23 | 36 |
| `u` | 64 | 48 |
| `v` | 69 | 48 |
| `w` | 47 | 48 |

Thus all seven types and all `279` inherited type-chart incidences are
retained.  Every type record contains its exact sparse restricted source,
all twelve derivatives obtained by differentiating the full source and then
restricting, and the tangent derivatives obtained by restricting first and
then differentiating only in stratum coordinates.  Exact coefficient
equality proves tangent transfer.  The normal derivatives are explicitly not
treated as stratum generators.

No chart representatives are deduplicated.  Accordingly, the artifact makes
zero overlap quotients, supplies no vacuous unit certificate, and makes no
overlap-equivalence claim.  It does not run the retired whole-atlas Groebner
route and uses no numerical or modular inference.

## Deepest type and parent exclusions

The deepest restriction is proved by sparse multiplication to be

```text
F|u=v=w=0 = -h*(a*f-c*d)
              *(a*e*i-a*f*h-b*d*i+b*f*g+c*d*h-c*e*g).
```

The three displayed factors match pinned parent records coefficient by
coefficient:

- `h = H_08_1248`;
- `a*f-c*d = -H_22_1367`;
- the cubic determinant equals `H_34_1678`.

Consequently

```text
V(F|u=v=w=0) = V(H_08_1248) union V(H_22_1367) union V(H_34_1678),
```

so every deepest source branch, and hence every deepest ambient singular
subbranch, is excluded from the strict row-2599 parent domain.  The artifact
also records the exact set-theoretic product singular cover
`V(h,L)`, `V(h,C)`, `V(L,C)`, `Sing(L)`, and `Sing(C)`, without claiming a
primary decomposition, radicality, or scheme multiplicity.  On the first
`V(h,L)` seed, it records the exact normal-remainder identity

```text
dF/dw = quotient*L + e*Q,
```

and the exact cover `V(h,L,e*Q)=V(h,L,e) union V(h,L,Q)`.  These refinements
remain excluded already by `H_08_1248` and `H_22_1367`; no unsupported degree
or multiplicity is inferred.

## Exact `u=v=0` branch and first unresolved residual

The full ambient restricted derivative ideal contains the homogeneous linear
family

```text
u=v=b=c=e=f=0.
```

All twelve restricted full derivatives substitute to the zero polynomial on
this family.  The first two projective blocks are fixed points and the third
block is `P3`, giving exact dimension `3` and degree `1`; no scheme
multiplicity is asserted.  On the standard chart `a=d=w=1`, this is the
three-parameter family with free `g,h,i`.  It is strictly parent-excluded
because `H_22_1367=c*d-a*f` vanishes identically.

This known family is not claimed to exhaust the `u=v=0` ambient singular
ideal.  The residual component census, global component closure versus a
stratum-only branch, any overlap-unit deduplication, affine pullback, and the
ordered 70-parent-factor tests for any future accepted affine pullback remain
fail-closed at `B-UV-01-unclassified-ambient-components`.

## Rebuild, verification, and nonconsequences

The deterministic standard-library builder visits `13,135` exactly defined
sparse algebra nodes, below the lane ceiling of `350,000`; the pinned first
build took `1.093482` seconds.  Its semantic frontier SHA-256 is
`70d980c28c536dd10a679ac086939fadcf78722dd68839658062948c1e0dd5ec`.
`build_boundary_type_frontier.py --check` reproduces the manifest, frontier,
and result byte for byte.  `verify_boundary_type_frontier.py` independently
reconstructs all restrictions, derivatives, incidences, factor identities,
parent matches, the linear `P3` branch, endpoint accounting, and rejects
`42/42` hostile mutations.

This result is not a complete seven-type branch classification, a complete
characteristic-zero component census, an overlap-deduplicated component
atlas, an accepted affine pullback, a 70-factor census for an affine branch,
a strict-real or connected-parent certificate, a theorem-level
counterexample, a diagonal-9 proof or counterexample, or evidence for changing
the `2/9` theorem ledger.
