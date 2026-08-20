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

A subsequent global exact positive-cone screen certifies 1,177 of the 6,980
segment-open factors as fixed-sign and therefore empty in the strict parent
cell. A proposed moving-column symmetry quotient was rejected because it does
not preserve the signed row-2599 cell. The corrected follow-up theorem and
no-go are recorded in `DIAG3_PAIR_FULLSUPPORT_PARENT_PRODUCT_SIGNS.md` and
`DIAG3_PAIR_FULLSUPPORT_BLOCK_SYMMETRY.md`.

## Merge-gate review

An independent replay rechecked the candidate-factor determinant certificate, compactification atlas, full face-Bernstein atlas, the new 105-segment certificate, and both diagonal-three open-object ledgers. The open ledgers still report the missing coverage-certified global master closure complex and keep the nine-diagonal score at `2/9`. The parent-face replay had already passed before its permanent Drive checkpoint was published; a fresh combined replay exceeded the interactive execution window, so absence of a GitHub status is not described as a successful CI run.

## Accounting

- full-support candidate factors: 17,824
- exact interior-nonempty factors: 10,844
- unresolved factors at this certificate stage: 6,980
- subsequent exact fixed-sign empty factors: 1,177
- current unresolved factors after the sign theorem: 5,803
- relative-boundary mixed restrictions already removed from the chain-generator obligation: 52,394
- 9DVL score: **2/9**

This advances the full-support feasibility frontier but does not construct the global nonrelative chamber complex and does not prove diagonal three.
