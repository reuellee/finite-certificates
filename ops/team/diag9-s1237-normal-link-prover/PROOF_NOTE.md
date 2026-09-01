# D9 S12,37 oriented normal-link producer

## Endpoint

This track returns the finite-exact negative endpoint
`NORMAL_LINK_REDUCTION_NO_GO` for
`D9_S1237_4SUPPORT_NORMAL_LINK_GATE1`.

It does **not** prove that no inward arcs exist. It proves that the ordinary
common-radial strict parent link is singular on both selected supports, so a
first-order projectivized link cannot be used as the proposed reduction.
Every actual parent-safe approach must instead enter a forced facet and be
resolved by a higher weighted blow-up.

## Complete literal and initial-form frontier

The producer independently rebuilds the exact `S12,37` active sector from the
pinned opening tree. It materializes:

- all `3,539` oriented primitive-factor literals;
- all `6,167` labeled occurrences, their representatives, fixed
  raw-to-primitive orientations, stripped parent-bracket units, unit signs,
  constant scalar signs, and active-signature incidence;
- all `7,078` factor initial forms (`3,539` on each support); and
- all `140` oriented parent-bracket initial forms (`70` on each support).

On `(3,1,15)`, factor radial orders are
`0:1271, 1:1917, 2:349, 3:2`, with `1,443` distinct exact initial forms. On
`(3,3,7)`, they are `0:1186, 1:1963, 2:385, 3:5`, with `1,492` distinct
forms. These inventories are exact multihomogeneous dehomogenizations in
coordinates `(a,g,h,n0,...,n5)`. The sixth normal coordinate breaks the
parent equality inside the ambient four-dimensional support face.

## Exact singular-link certificates

At the exact relative-interior tangent point

```text
(a,g,h) = (3/4, 1/4, 1/2),
```

the independently oriented parent brackets have these first normal forms:

| support | positive label | form | negative label | form | forced facet |
| --- | --- | --- | --- | --- | --- |
| `(3,1,15)` | `1237` | `n4` | `1367` | `-n4` | `n4=0` |
| `(3,3,7)` | `1237` | `n3` | `1278` | `-n3` | `n3=0` |

Both parent inequalities must be strict inside the open parent cell. For
each row, the positive Gordan weights `(1,1)` give an exact zero sum. Thus no
ordinary first-order normal direction can make both forms positive.

The next exact frontier is consequently a weighted blow-up retaining second
and higher orders on `n4=0` for the first support and on `n3=0` for the
second. This track stops at the first exact singularity, as required by the
negative endpoint. It does not promote the opening tangential `8`-ID / `4`
zero-set discovery to a collar statement.

## Replay and scope

```bash
PYTHONDONTWRITEBYTECODE=1 python \
  ops/team/diag9-s1237-normal-link-prover/verify_normal_link_no_go.py
```

The verifier rebuilds every stored artifact, independently differentiates the
four load-bearing parent polynomials from pinned source geometry, checks both
Gordan relations and all orientation signs, and rejects `13/13` hostile
mutations including support, label, sign, unit, omission, fake-radius,
false-no-arc, and false-ledger changes.

No collar, link cellulation, mincut, active-sector connectivity theorem,
separator, or diagonal-nine proof/counterexample follows. The honest theorem
ledger remains `2/9`.
