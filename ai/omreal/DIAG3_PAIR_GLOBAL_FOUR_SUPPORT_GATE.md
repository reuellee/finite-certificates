# Diagonal three: exact first-four-support parent and wall gate

## Result

The next two support strata in the row-2599 compactification ladder are
nominally four-dimensional:

```text
(3,1,15): 3,996 mixed residual restrictions
(3,3,7):  4,021 mixed residual restrictions
```

They are not four-dimensional inside the weak parent closure. Opposite signed
parent inequalities force `g=i` on the first support and `d=g` on the second.
After either substitution, the exact parent domain is the same square-pyramid
order polytope

```text
0 <= g <= a <= 1,
0 <= g <= h <= 1.
```

The pyramid is covered by two rational tetrahedra. Their common base `g=0` is
the previously completed `(3,1,5)` square, with its inherited `a=h` diagonal.
Thus this checkpoint supplies genuine parameter coverage and face compatibility
for both first four-support parent closures; it is not a point sample.

## Exact two-tetrahedron coverage

The five pyramid vertices in `(a,g,h)` coordinates are

```text
o=(0,0,0), a=(1,0,0), h=(0,0,1), ah=(1,0,1), top=(1,1,1).
```

The two tetrahedra are `(o,a,ah,top)` and `(o,h,ah,top)`. If `a>=h`, the
barycentric weights in the first are

```text
(1-a, a-h, h-g, g).
```

If `h>=a`, the weights in the second are

```text
(1-h, h-a, a-g, g).
```

These formulas prove exact union coverage. Their common triangle `a=h` is an
ordinary internal seam, not parent infinity. All seventy target-signed parent
brackets independently have nonnegative simplex-Bernstein controls on both
tetrahedra; twenty-five vanish identically after the forced equality on each
support and the other forty-five are nonnegative.

## Residual-wall compression

The exact factor accounting is:

| support | ambient mixed | parent-zero | one-signed | mixed after equality | distinct zero sets | interior-empty classes | interior-active classes | interior-active factors |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `(3,1,15)` | 3,996 | 548 | 27 | 3,421 | 68 | 43 | 25 | 328 |
| `(3,3,7)` | 4,021 | 656 | 29 | 3,336 | 40 | 24 | 16 | 197 |

The two supports share fourteen parent-reduced zero sets. After removing
monomial factors, the five true pyramid-boundary factors, and factors proved
strictly nonzero in the pyramid interior, the combined arrangement has only
**22 distinct interior wall equations**. Four occur on both supports. Their
factor-ID union contains 436 of the original 17,824 candidates.

All interior decisions are exact:

- nonemptiness uses a zero or opposite signs at rational points strictly inside
  the pyramid, so convexity supplies a strict-interior zero;
- emptiness uses one-sided exact simplex-Bernstein controls on both tetrahedra
  and their shared internal triangle;
- no class remains unresolved.

This is a reduction from 8,017 factor restrictions to 22 geometric walls, not
the arrangement cellulation of those walls.

## Reusable method extension

The exact semialgebraic toolkit now also supports arbitrary-dimensional simplex
Bernstein conversion and deterministic longest-edge simplex bisection. Positive,
crossing, and compact-sphere hostile canaries prevent a subdivision budget from
being mistaken for an emptiness theorem.

## Next bounded target

Construct a face-compatible exact arrangement of the 22 walls on the two
tetrahedra per support, inheriting the completed base and treating `a=h` as an
ordinary seam. The compiler must stop with an exact `BOUNDED_NO_GO` frontier
before either of these ceilings:

```text
100,000 unique projection polynomials
1,000,000 atomic tetrahedra
```

It may not fall back to sampled adjacency or the refuted chart-0/chart-152
single-source incidence route.

The global master-cell universe, signature labels, strict closure pairs and
triples, and middle-rank replay remain open. The honest 9DVL score is `2/9`.

## Replay

```bash
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/build_diag3_pair_global_four_support_gate.py

PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/verify_diag3_pair_global_four_support_gate.py
```
