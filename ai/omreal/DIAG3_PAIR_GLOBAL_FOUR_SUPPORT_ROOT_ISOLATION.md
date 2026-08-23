# Diagonal three: ordered root isolation for the four-support base

## Result

The complete second projection produced 2,333 distinct univariate factor
polynomials and 1,693 interior factor-root incidences.  Exact rational root
isolation now proves that those incidences are **1,693 distinct interior
`t` sections**: no two factors share an interior root.

The globally ordered certificate contains:

| section kind | count |
|---|---:|
| exact rational points | 19 |
| irrational roots in rational isolating intervals | 1,674 |
| **total distinct sections** | **1,693** |

Every non-point interval has width at most `2^-48`.  All consecutive closed
point/interval certificates are strictly disjoint.  The smallest certified
gap is stored exactly, and every endpoint numerator and denominator fits in
at most 32 and 33 bits respectively.

## Independent replay

The producer uses exact SymPy root isolation.  The verifier imports neither
SymPy nor the producer.  Starting from the committed second-projection factor
catalog, it:

1. reconstructs a rational Sturm sequence for every one of the 2,333 factors;
2. independently recounts every factor's roots in `0<t<1`;
3. proves that each non-point interval contains exactly one root;
4. substitutes every rational point exactly and checks that its root is
   simple;
5. checks complete per-factor coverage, global strict separation, and the
   total order; and
6. rejects eleven hostile semantic mutations.

The global separation step upgrades the old upper bound: the exact number of
distinct projection sections is 1,693, not merely at most 1,693.

## Consequence and next gate

The `t`-axis CAD now has 1,693 algebraic point sections and 1,694 open
sectors.  The next exact construction is to lift the 114 base factors in `u`
over those cells, followed by the 22 original degree-at-most-two walls in
`v`.  This checkpoint does not yet construct those lifted cells, prove their
regular closure data, or close the diagonal-three invariant.  The honest
9DVL score remains `2/9`.

## Replay

```bash
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/build_diag3_pair_global_four_support_root_isolation.py

PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/verify_diag3_pair_global_four_support_root_isolation.py
```
