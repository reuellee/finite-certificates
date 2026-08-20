# Diagonal three: moving-column symmetry no-go

## Corrected result

The three moving columns have an exact `S3` symmetry at the level of the
**unsigned parent-bracket divisor arrangement**, but the strict signed
row-2599 parent cell is not invariant under any nonidentity moving-column
permutation.

The exact sign-preserving census is

```text
moving-column permutation  signed primitive parent inequalities flipped
(0,1,2)                       0
(0,2,1)                      23
(1,0,2)                      19
(1,2,0)                      22
(2,0,1)                      22
(2,1,0)                      27
```

The 70 labelled parent brackets reduce to 63 distinct primitive signed
polynomials. Earlier comparison by lex-leading-positive primitive keys
identified a polynomial with its negative and therefore proved only
unsigned divisor symmetry. It did **not** prove signed-cell symmetry.

This distinction is decisive. The former unconditional transport of 10,844
wall witnesses to 5,986 additional factors is invalid and is withdrawn. The
valid exact segment theorem leaves 6,980 candidate factors open before the
separate fixed-sign identities are applied.

## Direct witness-segment audit

The correction does not merely reject a global group action. Every one of
the 525 nonidentity transports of the 105 certified parent-safe segments was
replayed against all 70 signed parent brackets by exact rational Bernstein
subdivision. None remains inside the signed row-2599 parent cell:

```text
safe transformed segments       105  (identity only)
unsafe transformed segments     525
wrong-bracket histogram          {19:105, 22:210, 23:105, 27:105}
```

Thus there is no segment-by-segment salvage of the invalid nonemptiness
transport.

Replay:

```bash
PYTHONDONTWRITEBYTECODE=1 python ai/omreal/verify_diag3_pair_fullsupport_block_symmetry.py
```

## What remains usable

Moving-column permutations can still generate polynomial identities. A
transformed identity is used only after every transformed signed parent
factor is matched to an actual row-2599 signed parent factor and all summands
are proved to have one common sign. This conditional algebraic use does not
assume that the parent cell is invariant; it underlies the independent
fixed-sign theorem in `DIAG3_PAIR_FULLSUPPORT_PARENT_PRODUCT_SIGNS.md`.

## Honest ledger

This correction prevents an invalid reduction; it does not close a diagonal.
The global nonrelative master closure complex is still missing and the 9DVL
score remains **2/9**.
