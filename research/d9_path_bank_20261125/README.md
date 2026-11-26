# D9 row-2599 path-bank checkpoint

**Status: finite exact computation; D9 remains open and the 9DVL theorem ledger remains 2/9.** This checkpoint studies only charts 12 and 37 for parent 2599. It does not claim universal coverage, a global separator, or that a new diagonal has been proved. The canonical V10 strategy snapshot remains unchanged.

## Results

The original bank has 142 certified parent-safe three-segment paths. Adding the earlier nine-signature coordinate path gives 143 paths. A signature is feasible at both endpoints but fails somewhere on every path in this bank. An exact positive-dependence certificate supplies the obstruction.

In five subsequent constructions, each new coordinate path preserves all previously identified blockers. After each of the first four additions, a different signature was exactly certified to fail on every path in the enlarged bank:

| Paths in bank | A signature lost on every path | New detour preserving all blockers so far |
| ---: | ---: | --- |
| 143 | `17331133384703` | one-signature path, 2,803 segments |
| 144 | `102950366083904` | two-signature path, 4,804 segments |
| 145 | `114322895077375` | three-signature path, 5,205 segments |
| 146 | `172626814396416` | four-signature path, 7,406 segments |
| 147 | `1228857710465867` | five-signature path, 7,607 segments |

For each bank through 147 paths, the full common-signature fractional path-packing optimum is **exactly 1**: the specified common blocker bounds the total weight by 1, while one path with weight 1 attains it. These are finite-bank statements only. The five-signature path avoids each of the five listed blockers. The full packing optimum of the resulting **148-path bank has not been computed**; there may be a different common blocker.

All five new paths passed independent exact replay: at every one-column update, prescribed determinant signs hold at both endpoints, so they hold throughout the segment; the auditors also check the positive projective gauge joins and reject tampering. These paths preserve their named signatures, not necessarily the earlier hard nine-signature family. The 147-path blocker audit checks endpoint feasibility and exact Gordan dependences covering all 142 stored routes and the five pre-existing coordinate paths, with hostile mutations rejected.

An additional exact census finds 8,638 common endpoint signatures for 12/37 and 13,578 for 37/176. Reversing an extension vector flips all 56 signature bits without changing feasibility, so these form 4,319 and 6,789 antipodal pairs. On the earlier 12/37 coordinate path, five completely enumerated intermediate arrangements show that 798 of the 8,638 signatures fail at one or more sampled vertices. The other 7,840 pass those five point checks; that does not establish survival on the complete path. The full census and sample certificates are in the accompanying archive.

## Public replays

From the repository root, Python 3 and NumPy are required for these path and blocker replays. The original bank audit additionally uses SymPy. Do not use `python -O`: these audit scripts use assertions.

```bash
python ai/omreal/verify_ninth_candidate_path.py
python research/d9_path_bank_20261125/audit_bank.py
python research/d9_path_bank_20261125/audit_path1.py
python research/d9_path_bank_20261125/audit_path2.py --source ai/omreal/data/seeat_parent2599_upper178.npz --catalog ai/omgamma/data/cat_4_8.txt --cert research/d9_path_bank_20261125/two_signature_path.npz
python research/d9_path_bank_20261125/audit_path3.py --source ai/omreal/data/seeat_parent2599_upper178.npz --catalog ai/omgamma/data/cat_4_8.txt --cert research/d9_path_bank_20261125/three_signature_path.npz
python research/d9_path_bank_20261125/audit_path4.py --source ai/omreal/data/seeat_parent2599_upper178.npz --catalog ai/omgamma/data/cat_4_8.txt --cert research/d9_path_bank_20261125/four_signature_path.npz
python research/d9_path_bank_20261125/audit_path5.py --fifth 1228857710465867 --source ai/omreal/data/seeat_parent2599_upper178.npz --catalog ai/omgamma/data/cat_4_8.txt --cert research/d9_path_bank_20261125/five_signature_path.npz
python research/d9_path_bank_20261125/audit_blocker147.py --source ai/omreal/data/seeat_parent2599_upper178.npz --old-path ai/omreal/data/ninth_candidate_12_37_path.npz --new-path research/d9_path_bank_20261125/single_signature_path.npz --two-path research/d9_path_bank_20261125/two_signature_path.npz --three-path research/d9_path_bank_20261125/three_signature_path.npz --four-path research/d9_path_bank_20261125/four_signature_path.npz --routes research/d9_path_bank_20261125/routes.json --label-gate research/d9_path_bank_20261125/label_gate.json --candidate research/d9_path_bank_20261125/universal_147_candidate.json --proof research/d9_path_bank_20261125/universal_147_proof.json
```

The local audit scripts are named `audit_*.py` to avoid accidental registration as whole-repository `verify_*.py` suite entries. See [the previous bounded bank gate](../../ai/omreal/DIAG9_FRACTIONAL_PATH_BANK_GATE_20261125.md) and the [canonical theorem prospectus](../../ai/omreal/9DVL_THEOREM_PROSPECTUS.md).

## Complete reproducibility archive

The [Google Drive research backup](https://drive.google.com/file/d/14Kp5HwnoZIXljAlwwOhD8BKDl51D9Cky/view) includes the full endpoint and intermediate witness censuses, independent region-count replays, discovery scripts, and historical inputs. Access follows the existing Drive permissions. Archive SHA-256:

```
dc8996a907798a9f6390a907fdb3c82add046bf3e321898e59c8a0c9e4fcda61
```

Some discovery scripts retain machine-specific paths, as noted in the archive; its documented verification commands use portable paths. This checkpoint used ordinary numerical LP for proposals and exact arithmetic for verification; it did not implement or run the recently announced strongly polynomial LP algorithm.
