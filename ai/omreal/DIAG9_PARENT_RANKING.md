# Diagonal 9: proof-safe first-roadmap parent ranking

## Result

The first complete diagonal-nine roadmap should be built for catalog parent
`860`.  It is the unique realizable `UOM(4,8)` catalog parent minimizing the
current proof-safe upper bound on residual walls that can meet the parent
cell:

| catalog parent | certified-empty factors | candidate factors |
|---:|---:|---:|
| **860** | **10,320** | **16,420** |
| all 2,604 realizable parents | `8,916`--`10,320` | `16,420`--`17,824` |
| 2599 | 8,916 | 17,824 |

The maximum `17,824` is attained by the four catalog representatives
`2599`, `2600`, `2601`, and `2602`.  The count is an upper bound: failure to
certify a factor wall empty does **not** prove that the wall meets the parent
cell.

An exact realizing matrix for parent 860 is

```text
 5 -4  3  8  1  4  0  8
 1  8 -2  4  4 -5  8  1
-8 -4  5  4  8  1  1 -2
-4 -3 -8 -5  3  8  4  3
```

This gives the smallest certified input before projection closure and
compactification are introduced.

## Empty-wall certificate

The alternative-certificate lemma in `DIAG9_ACTIVE_SECTOR_THEOREM.md` is
catalog-wide.  A labeled residual occurrence can inherit several transported
fixed-unit circuit identities.  Normalize their circuit coefficient signs in
sorted support order, modulo one global sign.  If two normalized patterns
disagree at a parent chirotope, the residual determinant cannot vanish
anywhere in that parent realization cell.  Every primitive global factor
containing that occurrence is therefore nowhere zero on the cell.

The fixed coefficients are signs of four-normal determinants.  The 25 fixed
orbit identities have invariant homogeneous form

\[
          \det(n_{I_1},n_{I_2},n_{I_3},n_{I_4})
               = \prod_{k=1}^3 [B_k],
\]

with a positive global orientation in the canonical representatives.  Their
three-bracket monomials are determined by the already verified normalized
identities and column multidegree; a moment-curve evaluation fixes the
orientation.  Relabeling transports these formulas to all `223,790` fixed
foursets.  Consequently their signs on all 2,604 parent cells can be evaluated
directly from the 70 parent chirotope bits.  No sampled residual sign is used.

For every one of the `84,840` residual occurrences, the verifier retains all
2--24 transported ordinary/localization identities, compares their circuit
patterns as chirotope formulas, and ORs every proved conflict into the pinned
`26,740` primitive-factor partition.  Parent 860 has

```text
31,380 conflicting labeled occurrences
10,320 certified-empty primitive factor walls
16,420 remaining candidate factors.
```

An independent direct replay recomputes all `223,790` fixed four-normal
determinants from the displayed integer matrix and recovers the same
`31,380/10,320/16,420` census.  This catches a sign, relabeling, or bitset
error in the catalog-wide evaluator.

## Consequence and boundary

Parent 860 is now the justified engineering target for the first
proof-carrying master roadmap.  The next calculation must still:

1. add the projection resultants and boundary equations needed for a complete
   compactified cell decomposition;
2. prove coverage and adjacency, rather than sampling chambers;
3. compute exact derived-arrangement tope labels on every generic chamber;
4. run the sharp pairwise tree certificate or complete cut-SAT test; and
5. retain any candidate factor until geometry, not absence of a conflict,
   proves it empty.

The ranking therefore reduces the first roadmap input by 1,404 primitive
factors relative to parent 2599.  It does not prove the ninth diagonal for
parent 860 or for the catalog.

## Exact verification

Run:

```console
python ai/omreal/verify_diag9_parent_ranking.py
```

The checker reconstructs the invariant formulas, all transported identities,
the full 2,604-parent ranking, and the direct parent-860 determinant replay.
Its semantic digest pins the ordered `(catalog index, empty-factor count)`
table:

```text
1d5c239bd64a59514bc20e4b09244bbab9b00898384f3d39d67b5cf147ff6f65
```
