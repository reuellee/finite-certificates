# Diagonal three: full-space feasibility gate for `(5563,4373,23221)`

## Decision

The existing boundary-to-boundary concurrence certificate cannot be promoted
from its pinned slice to the full canonical triple orbit.  The feasibility
gate is therefore `FAIL_CLOSED`.  This is a scope decision, not a
counterexample to noncompactness.

The selected presentation

```text
(5563,16134,19284)
```

maps by the pinned `S8` label permutation to the canonical unresolved row

```text
(5563,4373,23221).
```

That map, the slice CAS ring, and the determinantal counts are replayed by a
dependency-free checker.

## Why the slice determinant is insufficient

The certified slice fixes five of the six base `u` coordinates.  Its four
incidence equations live in five geometric variables

```text
(vr,vs,wr,ws,t),
```

so the zero set is a curve.  For the height `t`, one four-by-four fiber
Jacobian determinant is the correct critical equation.  The exact msolve
input adds two inverse variables, giving seven equations in seven variables,
and the stored degree-20 critical census is complete only for that pinned
curve.

There are two equivalent full-space presentations:

| presentation | variables | equations | expected zero-set dimension | one coordinate-height rank test |
|---|---:|---:|---:|---:|
| parent factor chart | 9 | 3 | 6 | `C(8,3)=56` minors |
| concurrence chart | 10 | 4 | 6 | `C(9,4)=126` minors |

The concurrence Jacobian has `C(10,4)=210` maximal minors.  For one selected
coordinate height, the critical locus is cut out by the 126 minors that avoid
that height column.  Across the six base-coordinate choices this gives 756
tagged tests.  The single stored fiber determinant instead cuts the
ramification discriminant of the base projection; in full space it is not a
zero-dimensional Morse critical system.

This dimension mismatch is exactly the missing component-to-slice theorem:
a full compact component need not meet the one five-coordinate pin used by
the certificate.

## Gate acceptance obligations

A future full-space upgrade must provide all of the following in one fixed
height chart:

1. materialize the complete nine-variable/three-equation or ten-variable/
   four-equation critical system;
2. saturate parent walls, chart and interpolation divisors, concurrence-rank
   and occurrence-rank strata, projective fiber infinity, and extra-factor
   frontiers;
3. prove the saturated ideal complete and zero-dimensional;
4. isolate and classify every real critical point by parent chamber;
5. attach every in-chamber critical point to parent boundary or chart
   infinity; and
6. transfer the result across the complete `S8` orbit of the canonical row.

The tracked manifest is

```text
data/DIAG3_triple_fullspace_feasibility_gate.json
```

with semantic digest

```text
874c4895ae17843c6827c1c3a8d528eac0b45fc35dedc9159e4f447786ed2ace
```

## Replay

```bash
PYTHONDONTWRITEBYTECODE=1 \
  python ai/omreal/verify_diag3_triple_fullspace_feasibility_gate.py
```

The check pins the five source artifacts, verifies the named-to-canonical
factor map, confirms the seven-variable slice CAS ring, materializes the 56
and 126 coordinate-height column subsets, and checks that theorem accounting
does not advance.

## Honest status

The exact local fold and its two parent-wall exits remain valid and useful.
They do not close a full component, an orbit, or any part of the final
`1,162,302`-row residue.  The comparison-incidence count remains `4/6` and
the theorem score remains `2/9`.
