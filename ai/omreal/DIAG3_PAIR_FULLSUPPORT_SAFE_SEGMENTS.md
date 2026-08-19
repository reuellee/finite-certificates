# Diagonal three: exact full-support interior wall witnesses

## Result

After the relative-boundary collapse, only the full support `(15,15,15)` can contribute nonrelative chain generators. Its candidate residual-wall universe has 17,824 factors.

A deterministic family of 105 straight segments between the 178 stored exact row-2599 interior realizations certifies that **10,844 of those 17,824 factors genuinely meet the strict parent interior**.

For every one of the 105 segments, all seventy target-signed parent brackets are proved strictly positive on the entire segment by exact rational Bernstein subdivision. For every certified residual factor, exact rational endpoint evaluations have opposite signs on one of those parent-safe segments. The intermediate value theorem then gives an interior zero of that residual factor.

The remaining **6,980 factors are retained as open**. This certificate makes no emptiness claim for them. Their canonical sorted-ID digest is

```text
72de0ff0ba439e00a54e8fdb16a1505d4d7a8fbfaf7f42c00030f1c1a7149930
```

Replay:

```bash
PYTHONDONTWRITEBYTECODE=1 python ai/omreal/verify_diag3_pair_fullsupport_safe_segment_walls.py
```

## Independent reconnaissance

The 6,980-factor residue has one constant sign on all 178 stored interior realizations. A deterministic rational interior walk added 2,322 additional exact row-2599 points by single-coordinate parent-safe steps and found no new sign crossing among those 6,980 factors. This is evidence only, not an infeasibility proof, and is deliberately excluded from the theorem certificate.

A first exact positive-cone search using signed parent brackets, including positive monomial multipliers within the residual multidegree envelope, did not certify the initial residue cases. Thus the next target should be a stronger algebraic sign-implication certificate or a direct exact feasibility attack on symmetry representatives of the 6,980-factor residue, not additional point-bank path search.

## Accounting

- full-support candidate factors: 17,824
- exact interior-nonempty factors: 10,844
- unresolved factors: 6,980
- relative-boundary mixed restrictions already removed from the chain-generator obligation: 52,394
- 9DVL score: **2/9**

This advances the full-support feasibility frontier but does not construct the global nonrelative chamber complex and does not prove diagonal three.
