# Diagonal three: factored Koszul gate and strategy pivot

## Result

The last bounded algebraic continuation of the hard-canary `L=0` branch has
been executed.  It supplies a useful exact reformulation, but it does not
supply a short unit certificate.  Under the predeclared pass/fail rule,
active research should now move to the global master closure object rather
than widen this CAS calculation.

Write the hypersurface polynomial as

```text
E = H0 + e H1 + e^2 H2,   H2=(i-f)L.
```

The exact coefficient census is

| polynomial | terms | degree range |
|---|---:|---:|
| `H0` | 235 | 7--10 |
| `H1` | 256 | 6--9 |
| `H2` | 103 | 5--8 |

For the five vector fields `D_c`, `D_h`, `V_f`, `V_g`, and `V_i`, all five
critical generators are exactly

```text
D(H0) + e D(H1) + e^2 D(H2).
```

Consequently, on `H0=H1=H2=0`, the row `(1,e,e^2)` annihilates the
three-by-five directional Jacobian of `(H0,H1,H2)`.  A nowhere-zero
three-by-three minor would close the whole branch at once.

## Exhaustion of the ten direct minors

All ten minors were formed exactly and divided by every nonconstant parent
bracket as often as possible:

| directions | raw terms | primitive terms | exact parent factors removed |
|---|---:|---:|---|
| `c,h,V_f` | 40,250 | 34,203 | `[2378]` |
| `c,h,V_g` | 33,426 | 20,893 | `[2357][2378]` |
| `c,h,V_i` | 39,682 | 25,372 | `[2357][2378]` |
| `c,V_f,V_g` | 44,865 | 30,805 | `[2378][2458]` |
| `c,V_f,V_i` | 51,187 | 30,113 | `[2378]^2[2458]` |
| `c,V_g,V_i` | 42,265 | 21,437 | `[1238][2357][2378][2458]` |
| `h,V_f,V_g` | 43,718 | 37,222 | `[2378]` |
| `h,V_f,V_i` | 50,825 | 37,084 | `[2378]^2` |
| `h,V_g,V_i` | 38,494 | 18,459 | `[1238][2357][2367][2378]` |
| `V_f,V_g,V_i` | 53,964 | 31,378 | `[1238][2378]^2[2458]` |

No primitive part has a remaining parent-bracket factor or one of the named
`H0`, `H1`, `H2`, or `P` branch factors.  Thus the hoped-for single
unit-minor identity does not exist.

## Bounded combination search

The corrected localization uses four base factors and the transformed
`[1468]` and `[5678]` target walls.  At total degree 14, the verifier tests
each target wall times every base-localizer product which still fits in the
bound.  There are 88 distinct targets in 116,280 monomials.

The complete Macaulay ranks are

```text
field   rows   rank   target hits
F2      5,202  5,202  0
F3      5,202  5,202  0
```

Exhaustive point censuses independently give

```text
field   factored-system points   points surviving all six units
F2      113                      0
F3      1,121                    0
```

Additional complete discovery censuses gave zero localized points over
`F5` and `F7` as well.  A native-localization Buchberger attempt over `F5`
did not find a unit in the fixed window: by degree 11 it had generated
1,008--2,729-term basis elements and an increasing pair queue.  These facts
are useful prioritization evidence, not characteristic-zero theorems.

## Decision

The exact reduction remains reusable, and the lack of small-field points
means the rational saturation might still be true.  But the bounded search
found no short certificate and immediately returned to basis growth.  This
is precisely the stop condition set before the calculation.

Do not enlarge the resultant, minor, Macaulay, or Buchberger bounds now.
The active target becomes the other completion route already isolated in
the strategy checkpoint: construct the coverage-certified labelled regular
master closure poset, including its genuine infinity subcomplex and
barycentric order-two incidence.

This gate closes no triple orbit.  The honest score remains `2/9`, with
`1,162,302` triple orbits unresolved.

## Replay

```bash
PYTHONDONTWRITEBYTECODE=1 \
  python ai/omreal/verify_diag3_triple_factored_koszul_gate.py
```
