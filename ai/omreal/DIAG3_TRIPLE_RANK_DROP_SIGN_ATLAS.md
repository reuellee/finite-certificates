# Diagonal three: rank-drop graph and sign-atlas audit

## Result

This checkpoint sharpens the two-pivot rank-drop branch for the hard
presentation

```text
(5563,16134,19284).
```

It proves that the primitive `P=0` branch is everywhere a transverse graph
in the parent cell.  It also records and corrects an attractive finite-atlas
argument that does not extend to the entire labelled hard-canary orbit.  No
triple orbit is closed.

## Exact transverse graph

After the exact `b` and `a` reductions, the coefficient of `a` in the
`ae` rank-drop equation is

```text
[2357][2458](i-f)P.
```

Put

```text
F = gh-i,
Q = d(h-i)+fh(g-1).
```

Direct integer polynomial arithmetic gives

```text
P = -f[1378]F + c(i-f)Q,
Q-fF = (d-f)(h-i) = [1357][1258].
```

The five displayed factors `f`, `[1378]`, `i-f`, `d-f`, and `h-i` are
parent units.  If `P=Q=0`, the first identity forces `F=0`, while the second
then forces `[1357][1258]=0`.  This is impossible in the open parent cell.
Consequently

```text
P=0  =>  Q!=0  =>  partial(P)/partial(c)=(i-f)Q!=0.
```

Thus `P=0` has no coefficient-drop subbranch: it is an exact smooth `c`
graph.  The complementary `P!=0` branch remains the exact `a` graph already
identified by the rank-drop verifier.

The other primitive factor `L` is quadratic in `h`.  Its leading
coefficient is the parent-unit product

```text
-[1236][1348][2356][1357][2378].
```

Therefore the `L` degree never drops on a uniform parent cell.  Its
discriminant branch remains open.

## Subtraction-free sign subatlas

The same factors have the bracket expressions

```text
F = [1248][3458]+[1258],
Q = [1347][1258]+[1237][1248][3458],
P = -[1237][1378]F-[1236][2378]Q.
```

For each of the 2,604 realizable unlabelled `UOM(4,8)` parent types, there is
an `S_8` frame in which the terms of `F`, the terms of `Q`, and the two terms
of `P` have aligned signs.  A lexicographic bitset cover stops after 199
frames and uses 123 distinct first-witness frames.  Its semantic digest is

```text
98eca8e101e69de8812879c1ccd566d2a14300ae07a597084e644e1ba8d601b0.
```

Every first witness is independently replayed from the stored 4-by-8
integer realization matrix, using exact Cramer normalization and exact
determinants.  The checker also pins the catalog's colexicographic ordering
of its 70 chirotope signs.

## Why the atlas is not a global theorem

The factor-triple action gives the selected presentation a trivial `S_8`
stabilizer.  Once the triple is fixed, an arbitrary reframe changes the
labelled parent/triple pair rather than merely changing coordinates on the
same pair.  Therefore an existential frame for each unlabelled parent type
cannot eliminate `P=0` for the triple orbit.

The exhaustive correction scans all 40,320 frames.  Among the

```text
2,604 * 40,320 = 104,993,280
```

raw frame-parent presentations, the aligned-sign certificate applies to

```text
17,105,952.
```

Every frame certifies between 233 and 693 parent representatives; no frame
certifies all 2,604.  The full frame-census digest is

```text
88b75dc54f3c89bff71899b960534c0bd6199484c67c362917d74e393f97d4dd.
```

This is an exact positive subatlas and an exact warning against a false
orbit-level promotion.  It is not evidence that `P` actually vanishes in
the uncertified cells; it says only that this two-term sign method does not
decide them.

## Bounded branch diagnostics

The hypersurface exporter now supports explicit `P=0` and `L=0` equations,
inversion of either factor, and a hybrid presentation with branch inverses
plus native saturation of the base units.  At prime `1073741827`, bounded
55-second F4 runs gave no modular unit identity:

| branch | last reached degree | pending pairs at stop |
|---|---:|---:|
| `P=0` | 14 | more than 4,226 |
| `L=0` | 15 | more than 3,436 |
| invert `P`, saturate base units | 15 | more than 3,901 |

These are stopping diagnostics, not nontriviality results.

## Replay and next action

```bash
PYTHONDONTWRITEBYTECODE=1 \
  python ai/omreal/verify_diag3_triple_two_pivot_rank_drop.py
PYTHONDONTWRITEBYTECODE=1 \
  python ai/omreal/verify_diag3_triple_rank_drop_parent_atlas.py
```

The next exact calculation should use the two genuine charts rather than
restart a raw orbitwise CAS sweep:

1. on `P!=0`, retain the existing `a` graph;
2. on `P=0`, substitute the transverse `c` graph without adding a `Q=0`
   branch; and
3. treat `L=0` as a quadratic `h` cover with parent-unit leading
   coefficient, isolating its discriminant before any further saturation.

The unresolved triple census remains `1,162,302`, and the nine-diagonal
score remains `2/9`.
