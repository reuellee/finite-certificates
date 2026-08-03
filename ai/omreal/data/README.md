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

## Chromatic lower-bound certificates

`seeat_parent2599_k6.npz` is the 3.7-KB fast canary proving that five charts
do not suffice.  It contains six exact realizable extension signatures and a
branch-free Grassmann--Pluecker contradiction for each of their 15 pairs.
The six vertices therefore form a clique in the universal nonamalgamation
graph.

SHA-256: `dda21956b807c19c1cdbb44f3bd326874c9e83d12cdc16eaa5bc1ab19ff281e5`

```console
python ai/omreal/verify_seeat_k6.py
```

`seeat_parent2599_width7.npz` is the full 68-KB chromatic certificate.  It
contains:

| array group | meaning |
|---|---|
| parent, signatures, matrices, points | 220 exact realizable extensions of row 2599 |
| graph edges | 3,472 proposed universal incompatibilities |
| GP traces | 64,698 branch-free propagation steps ending in one contradictory GP relation per edge |
| positive control | a complete satisfying 28-sign two-element amalgam |
| coloring proof | a six-clique symmetry breaker and a 14,791-node exhaustive six-color refutation tree |
| `coloring7` | an explicit proper seven-coloring of the graph |

Thus the certified graph has chromatic number exactly seven.  Every chart is
an independent set in this graph, so the parent atlas width is at least seven.

SHA-256: `ec7ef2ad9f37467e00a5ea739d67f90c4c53b304f4d82d47ac72591a58477dc7`

```console
python ai/omreal/verify_seeat_width7.py
```

Both certificates embed their exact realization witnesses.  Their negative
claims use only uniform chirotope GP signs; sampled charts are not part of the
trust boundary.
