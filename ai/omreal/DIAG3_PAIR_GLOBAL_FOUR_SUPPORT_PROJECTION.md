# Diagonal three: bounded fiber projection for the first four-support walls

## Result

The 22 exact interior wall equations on the two covered square-pyramid parent
domains admit a bounded fiber architecture. Use cube coordinates

```text
a = t + (1-t)u,
g = t,
h = t + (1-t)v,
```

with `0<=u,t,v<=1`. For `t<1` this is an exact bijection onto the pyramid
interior, with inverse

```text
u=(a-g)/(1-g),  t=g,  v=(h-g)/(1-g).
```

The cube top `t=1` collapses to the pyramid apex. It is boundary, not an
ordinary interior seam. Nineteen transformed equations contain the factor
`1-t`; removing it preserves their interior zero sets. The 22 equations remain
distinct.

## Fiber census

After the exact cube pullback and boundary-factor quotient:

| fiber dependence | walls |
|---|---:|
| independent of `v` | 1 |
| linear in `v` | 20 |
| quadratic in `v` | 1 |
| degree greater than two | 0 |

Thus twenty walls are rational graph candidates over the `(u,t)` square, one
wall already lies in the base, and only one fiber requires a quadratic
discriminant.

## Complete projection family

The exact projection preflight constructs:

| obligation | count |
|---|---:|
| nonzero fiber coefficients | 44 |
| linear/linear resultants | 190 |
| linear/quadratic resultants | 20 |
| quadratic discriminants | 1 |
| total nonzero obligations | 255 |

No pair resultant vanishes identically. After canonical scalar, monomial, and
square-boundary factor quotients, only **136 distinct `(u,t)` polynomials**
remain. Their maximum bidegree is `(4,5)`. This is far below the pinned
100,000-polynomial projection ceiling, so the projection architecture passes
its declared stop gate.

## Consequence

The next exact construction is now sharply defined:

1. factor and project the 136 polynomials to the `t` axis (**complete**);
2. isolate and order the resulting `t` sections and lift the 114 base curve
   factors in `u`;
3. lift the one base-only, twenty linear, and one quadratic fiber walls in `v`;
4. identify the collapsed `t=1` boundary with the pyramid apex;
5. glue the result to the completed `t=0` base and between the two parent
   supports;
6. emit regular cells, closure pairs, three-cell chains, and wall labels.

This certificate chooses and validates the projection architecture. It does not
yet construct the base CAD, lifted arrangement, or global master complex. The
honest 9DVL score remains `2/9`.

The first item is now complete in
`DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_BASE_PROJECTION.md`: 114 base factors yield
2,554 distinct squarefree univariate projection polynomials, 2,333 factor
polynomials, and at most 1,693 interior `t` sections. Exact root isolation,
ordering, and lifting remain open.

## Replay

```bash
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/build_diag3_pair_global_four_support_projection.py

PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/verify_diag3_pair_global_four_support_projection.py
```
