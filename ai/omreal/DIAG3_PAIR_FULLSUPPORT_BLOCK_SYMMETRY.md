# Diagonal three: full-support moving-column symmetry closure

## Result

The strict row-2599 parent cell is invariant under all six permutations of the three moving columns. This is checked as an exact polynomial identity: after target-sign normalization, the 70 parent brackets reduce to 63 distinct primitive signed polynomials, and every block permutation preserves that set exactly.

Transporting the preceding 10,844 exact interior-wall witnesses through this `S3` action certifies **5,986 additional candidate residual walls**. Therefore

```text
full-support candidates          17,824
105-segment certificate          10,844
new by exact S3 transport         5,986
certified interior-nonempty      16,830
still unresolved                    994
```

The 994-factor residue has canonical sorted-ID digest

```text
c330ba558fedd9b0502c8e96b35cecf179e2ec5b2eb5324893a374c4f09039cf
```

No emptiness claim is made for those 994 factors.

Replay:

```bash
PYTHONDONTWRITEBYTECODE=1 python ai/omreal/verify_diag3_pair_fullsupport_block_symmetry.py
```

The verifier first replays the load-bearing 105-segment theorem, including exact rational Bernstein positivity of all seventy signed parent brackets on every seed segment. It then proves exact `S3` invariance of the strict parent cell, reconstructs the residual-factor action by primitive polynomial equality, and transports the already-certified zero sets.

## Why this is the right reduction

The previous 6,980-factor residue was not invariant under moving-column permutation because the 105 chosen witness segments were not symmetry-complete. The geometry is symmetric even though the witness bank is not. Closing the theorem under the exact parent symmetry therefore extracts information already implicit in the certificate instead of launching a more expensive semialgebraic search.

The surviving 994 factors comprise only multiplicity-1 and multiplicity-15 global factors. All multiplicity-2 and multiplicity-65 candidate factors are now certified interior-nonempty.

## Next target

The next exact target is the 994-factor residue. The efficient route is to quotient it by the same exact `S3` action, attack one representative per surviving zero-set orbit with exact feasibility/sign-implication methods, and transport every result back across its orbit. Point-bank sampling alone should not be used to classify any residue factor as empty.

## Honest ledger

This is an exact nonemptiness reduction, not a chamber decomposition. The global nonrelative master closure complex is still missing and the 9DVL score remains **2/9**.
