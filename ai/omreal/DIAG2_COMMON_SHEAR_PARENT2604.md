# Diagonal two: exact common-shear screen on 2,604 catalog representatives

## Result

The realizable `UOM(4,8)` certificate ledger contains one exact integer
`4 x 8` matrix for each of the 2,604 realizable parent chirotopes.  At every
one of those matrices, every two distinct bad uniform one-element extension
signatures have a common oriented elementary-shear escape direction.

The complete exact replay gives:

| quantity | exact value |
|---|---:|
| realizable parent representatives | 2,604 |
| valid extension signatures | 174,937,600 |
| complete derived-arrangement topes | 67,979,778 |
| bad extension signatures | 106,957,822 |
| unordered within-parent bad-signature pairs covered | 2,241,206,348,415 |
| parents with pairwise-intersecting escape masks | 2,604 |
| global minimum escape-mask size | 52 |
| global minimum pair overlap | 6 |

No floating-point predicate or sampled extension subfamily enters this
calculation.  This is a point-transversal theorem across all realizable
catalog parent classes.  It includes every bad extension pair, a finite
superset of the proper incomparable pairs required by diagonal two.  It is
not a realization-chamber theorem and does not promote diagonal two.

## Exact finite calculation

For each selected parent the verifier:

1. recomputes all seventy parent-bracket signs from the stored integer
   matrix and checks the catalog chirotope;
2. constructs the 56 derived rows, enumerates every complete tope by exact
   integer recursion, and independently verifies the tope witnesses;
3. enumerates every abstract uniform single-element extension by the exact
   Grassmann--Pluecker backtracker;
4. checks the extension count against the independent
   `extcount_4_9.jsonl` census and proves that the valid signatures partition
   into complete topes and bad signatures;
5. computes the 112-direction moving-witness escape mask of every bad
   signature using the complete-tope restriction criterion; and
6. finds the exact minimum intersection over every distinct pair of bad
   masks.

The Boolean-heavy extension and mask steps are implemented by the C++17
finite kernel `diag2_common_shear_fast.cpp`.  Parent 16 is also pinned
bit-for-bit against the original independent pure-Python calculation: 66,636
valid extensions, 40,524 bad signatures, minimum mask size 52, minimum
overlap 8, and record digest

```text
942d7cac1ce3afff4ff0299c5b9acb382e60c4350616f9b42eb49385fd831737
```

## Margins and derived degeneracies

The minimum-mask histogram over parent representatives is

| minimum escape size | parents |
|---:|---:|
| 52 | 767 |
| 53 | 1,822 |
| 54 | 15 |

The minimum pair-overlap histogram is

| minimum overlap | parents |
|---:|---:|
| 6 | 192 |
| 7 | 45 |
| 8 | 638 |
| 9 | 680 |
| 10 | 792 |
| 11 | 244 |
| 12 | 13 |

Thus the computation has a six-direction margin at every stored point;
mere nonemptiness is not the observed extremal behavior.

Exactly 2,450 representatives have the generic count of 26,112 complete
topes.  The other 154 representatives lie on one or more residual derived
degeneracies and have smaller complete-tope tables; all are retained in the
audit.  The smallest table has 25,260 topes, at catalog parent 440.  Across
all parents the valid-extension range is 54,520 through 97,224 and the
bad-extension range is 28,408 through 71,112.

## Reproduction and provenance

The committed summary uses the strict
`diag2-common-shear-parent2604-v2` schema.  Every record commits the catalog
index and chirotope, the exact matrix digest, the independent expected
extension count, all extrema and witnesses, and the complete sorted
`(signature, escape mask)` record digest.  The aggregate semantic digest is

```text
58b5a8cb8f6e36466efabb6dc6a4ba1b9bf9f812f5899f5138d6abc96c2c8a18
```

The default command validates the full stored summary and exactly replays
catalog parents 16, 860, and 2599:

```console
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/verify_diag2_common_shear_parent2604.py
```

The complete replay is explicit because it is expensive and requires a
C++17 compiler plus OpenSSL `libcrypto`:

```console
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/verify_diag2_common_shear_parent2604.py \
  --full --workers 8 \
  --analysis-output \
  ai/omreal/data/DIAG2_COMMON_SHEAR_parent2604_summary.json
```

Checkpoints are atomic and the strict resume path revalidates their schema,
scope, catalog provenance, independent extension counts, extrema, verdicts,
and aggregate digest before reusing any record.

## Exact scope

One realization does not cover the realization space of its parent
chirotope.  In particular, this audit does not certify every residual sign
chamber, every labeled factor wall, their incidences, or a connected
component-decorated transition graph.  The universal target remains either:

* prove escape-mask pairwise intersection throughout every realizable
  parent chart and its boundary strata; or
* construct sufficient covered transition data to exclude every compact
  decorated cycle.

Accordingly the honest nine-diagonal score remains `1/9`.
