# SEEAT certificate data

`seeat_parent2599_realizations.npz` is the compact certificate refuting the
proposed four-chart bound for `UOM(4,8)`.  It contains:

SHA-256: `ed70d5fbcd18f76036223c3977bea59594f64a009fa73632f088b7d0011d9f91`

| array | meaning |
|---|---|
| `format` | scalar string `seeat-parent2599-realizations-v1` |
| `parent_index` | scalar `2599`, indexing `ai/omgamma/data/cat_4_8.txt` |
| `key_hi`, `key_lo` | the 5,902 canonical `(4,9)` child keys |
| `multiplicity` | how many of the parent's 97,224 labeled extension signatures map to each key |
| `matrix` | one exact integer `4x9` realization per child key |

The artifact is not trusted as metadata.  The verifier independently
enumerates all abstract extensions of the parent, canonicalizes them with
`coverage_checker.py`, checks the key set and every multiplicity, and
recomputes all 126 determinants of every matrix in integer arithmetic.

```console
python ai/omreal/verify_four_chart_obstruction.py
```

The realization search can be reproduced separately; its floating-point work
is outside the trust boundary.

```console
python ai/omreal/build_four_chart_obstruction.py --workers 4 --force
```

## Explicit 178-chart upper cover

`seeat_parent2599_upper178.npz` is the complementary exact upper-bound
certificate for the same parent.  It proves that 178 fixed realizations cover
all 97,224 extension signatures.

SHA-256: `3b90799d26b7783e92c2ac697eaaf8b76d26a787f53205873b997657e114180a`

| array | meaning |
|---|---|
| `format` | scalar string `seeat-parent2599-upper-cover-v1` |
| `parent_index` | scalar `2599`, indexing `ai/omgamma/data/cat_4_8.txt` |
| `chart_matrix` | 178 exact integer `4x8` parent realizations |
| `assignment` | for each of the 97,224 signatures, the index of a covering chart |
| `point` | one exact integer 4-vector realizing that signature over its assigned chart |

The certificate does not ask the verifier to trust chamber enumeration or the
heuristic set-cover search.  The checker independently enumerates the
signatures, verifies all 70 parent brackets of every chart, and verifies all
56 derived-bracket signs of every assigned extension point.

```console
python ai/omreal/verify_seeat_upper_bound.py
```
