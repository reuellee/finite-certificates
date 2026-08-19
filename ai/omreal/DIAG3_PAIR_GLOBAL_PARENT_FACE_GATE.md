# Diagonal three: exact parent-feasibility gate on the global face atlas

## Result

The row-2599 parent chirotope eliminates `3,364` of the `3,375` relative
support strata of the pinned `(Delta^3)^3` compactification.  The remaining
eleven strata are each proved nonempty by an exact rational weak-parent
witness.

This removes

```text
3,364 x 17,824 = 59,959,936
```

candidate factor--face pairs before any internal subdivision.  Combining
this parent gate with the earlier Bernstein factor gate leaves only `70,218`
mixed residual restrictions on the eleven nonexcluded support strata, down
from `17,608,308` and from the original `60,156,000` factor--face workload.

The exact replay is
`verify_diag3_pair_global_parent_face_gate.py`; its machine-readable manifest
is `data/DIAG3_PAIR_GLOBAL_row2599_parent_face_gate.json`.

## Signed parent normalization

The verifier constructs the seventy primitive bracket polynomials in the
standard normalized variables

```text
(1,a,b,c), (1,d,e,f), (1,g,h,i).
```

Their target signs are obtained by exact Cramer normalization of the stored
catalog realization of parent 2599.  All 178 stored parent-2599 realization
matrices independently replay the identical normalized sign vector.  Its
digest is

```text
1d9b940e2bb954b5c69bcee8b2346f9554b2e15589ea4c5b3c3f8e1e943de701.
```

Each bracket is multihomogenized and restricted to every support stratum.
If the surviving Bernstein coefficients all have the wrong target sign,
the weak parent inequality is strictly violated throughout that relative
stratum.  A canonical first wrong-sign bracket is stored for all 3,364
excluded faces.  The complete parent bracket--face state census is

| state | pairs |
|---|---:|
| identically zero | 70,061 |
| correct sign | 81,648 |
| wrong sign | 38,448 |
| mixed | 46,093 |
| total | 236,250 |

The canonical state-and-witness stream has SHA-256

```text
e4f15408f786c26c34b4d721d7973aedc6e206a7382e5a92ce839f8c732be9f5.
```

## The eleven surviving support strata

Using four-bit homogeneous-coordinate support masks, the exact nonempty list
is

| support | dimension | mixed residual restrictions |
|---|---:|---:|
| `(1,1,1)` | 0 | 0 |
| `(1,1,5)` | 1 | 0 |
| `(3,1,1)` | 1 | 0 |
| `(3,1,5)` | 2 | 335 |
| `(3,1,15)` | 4 | 3,996 |
| `(3,3,7)` | 4 | 4,021 |
| `(3,3,15)` | 5 | 7,366 |
| `(7,7,7)` | 6 | 9,816 |
| `(15,1,15)` | 6 | 9,181 |
| `(15,7,15)` | 8 | 17,679 |
| `(15,15,15)` | 9 | 17,824 |

Every listed support contains the standard row-one gauge coordinate in all
three moving columns.  Thus the row-2599 weak parent closure has no component
on the coordinate-atlas infinity supports.  Internal parent-bracket
frontiers inside the standard chart still form relative boundary and are not
discarded.

## Exact support one-skeleton

The only feasible ambient support vertex is the common point `a=...=i=0`.
The only two feasible support edges are

```text
a in [0,1],  all other variables zero,  boundary equation 1-a;
h in [0,1],  all other variables zero,  boundary equation 1-h.
```

They meet at the common zero point and have distinct endpoints at `a=1` and
`h=1`.  No candidate residual factor has a mixed restriction on either edge.
The exact support one-skeleton therefore has three vertices and two edges.
This is not the complete internal master one-skeleton in higher-dimensional
support strata.

## Exact two-face

The sole surviving two-dimensional support is `(3,1,5)`, with variables
`a,h`.  Its three mixed parent inequalities reduce exactly to

```text
1-a >= 0,
1-h >= 0,
a+h-ah >= 0.
```

For `0<=a,h<=1`, the last expression is
`1-(1-a)(1-h)` and is nonnegative automatically.  Hence the parent domain is
the closed unit square.

The 335 mixed candidate restrictions collapse to sixteen distinct
polynomials: four monomial multiples of each of

```text
a-1,  h-1,  a-h,  ah-a-h.
```

Their factor multiplicities are respectively `113,113,53,56`.  In the unit
square, `ah-a-h` vanishes only at the origin.  The only interior dividing
wall is therefore `a=h`.  The complete regular cellulation is the square
split along its diagonal: four vertices, five edges, and two triangular
faces.

## Consequence and next target

No support stratum of dimension three survives.  The next dimension-ladder
target is the pair of four-dimensional supports `(3,1,15)` and `(3,3,7)`,
with 3,996 and 4,021 mixed restrictions.  They should be attacked together,
first quotienting monomial multiples and identical restricted zero sets, and
then applying face-compatible exact subdivision inherited from the completed
two-face and support edges.

The global master-cell universe, internal parent frontier, signature labels,
strict closure pairs and triples, and middle-rank replay remain open.  The
nine-diagonal ledger remains `2/9`.

## Replay

```bash
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/verify_diag3_pair_global_parent_face_gate.py
```
