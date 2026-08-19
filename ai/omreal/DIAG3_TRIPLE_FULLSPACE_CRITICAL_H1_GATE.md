# Diagonal three: exact full-space height-`b` critical gate

## Outcome

The complete nine-variable critical system is now materialized for the hard
triple presentation

```text
(5563,16134,19284),
```

which maps by the pinned `S8` permutation to the canonical unresolved row

```text
(5563,4373,23221).
```

This advances the earlier dimension-count gate to an exact system object,
but it does **not** close the row.  The raw critical ideal contains two exact
four-dimensional coordinate boundary components.  It is therefore not
zero-dimensional, and any raw Gröbner basis or RUR census would mix boundary
components with interior critical points.  The gate remains `FAIL_CLOSED` and
the theorem score remains `2/9`.

## 1. Complete system

Write the standard normalized parent coordinates as

```text
(a,b,c,d,e,f,g,h,i).
```

For the height `b`, the tracked artifact contains:

* the three exact residual factor polynomials;
* every formal `3x3` Jacobian minor using three of the eight columns other
  than `b`; and
* explicit empty term lists for the four identically zero formal minors.

Thus the artifact has `3+C(8,3)=59` ordered equations.  Of the 56 formal
minors, 52 are nonzero, all have degree eight, and together they have 14,681
nonzero terms.  The four zero column triples are

```text
(a,c,e), (a,c,h), (a,e,h), (c,e,h).
```

The exact sparse system is

```text
data/DIAG3_triple_fullspace_critical_h1.json
```

with SHA-256

```text
c9244a47ded5736e7afe724a9914e75631a22b78653442e88c14f5c397919eb8
```

The builder uses the repository determinant implementation.  The verifier
does not: it reconstructs derivatives, sparse products, permutation signs,
and every `3x3` determinant independently before comparing all coefficients.

## 2. Why height `b`

All nine coordinate heights were enumerated exactly.  Height `b` is the
unique minimum by total nonzero-minor term count.

| height | nonzero minors | total terms |
|---|---:|---:|
| `a` | 55 | 20,176 |
| `b` | 52 | 14,681 |
| `c` | 55 | 17,672 |
| `d` | 52 | 17,658 |
| `e` | 55 | 19,131 |
| `f` | 52 | 15,492 |
| `g` | 52 | 15,738 |
| `h` | 55 | 19,280 |
| `i` | 52 | 16,778 |

This is a workload choice, not a symmetry or genericity claim.

## 3. Exact boundary-component obstruction

The independent verifier exhausts all coordinate subspaces in increasing
codimension.  No subspace obtained by zeroing four or fewer coordinates is
contained in the raw ideal.  Exactly two maximum-dimensional coordinate
subspaces first occur after zeroing five coordinates:

```text
a=b=c=d=f=0,  with free coordinates (e,g,h,i),
b=c=d=e=f=0,  with free coordinates (a,g,h,i).
```

Every one of the 59 equations vanishes identically on each displayed
four-space.  This is an exact polynomial identity, not a point sample or a
finite-field inference.  Each four-space is visibly a parent-boundary object:
the verifier independently finds 23 normalized parent brackets that vanish
identically on it.  The complete bracket lists are pinned in the manifest.

Consequently the unsaturated critical ideal has positive-dimensional
boundary components.  It cannot satisfy the earlier gate's obligation of a
complete zero-dimensional interior critical census.

## 4. Modular feasibility diagnostics

The exact degree-9 Macaulay screen for the chosen height was replayed over
both `F2` and `F3`.  It includes all 52 nonzero minors and all 43,680 parent
products of length at most three.  Both primes give rank 14,342, with 34,788
exact support rejections, 8,892 modular membership tests, and zero hits.

The smaller rank profiles also agree at both primes:

| degree bound | monomials | row-space rank | quotient count at bound |
|---:|---:|---:|---:|
| 8 | 24,310 | 5,927 | 18,383 |
| 9 | 48,620 | 14,342 | 34,278 |
| 10 | 92,378 | 32,637 | 59,741 |

These are exact finite-field ranks.  They are feasibility diagnostics only:
a miss modulo 2 or 3 is not a characteristic-zero nonmembership theorem,
and the displayed filtered quotient counts are not a Hilbert-polynomial or
dimension proof.  The coordinate four-spaces above already give the exact
reason the raw ideal cannot be the desired zero-dimensional object.

## 5. Next admissible object

The next computation must be a component-decorated saturation, not a larger
raw critical solve.  For every discarded component it must record and verify
an attachment to one of:

1. a named parent wall;
2. a normalization or chart divisor;
3. an occurrence-rank or concurrence-rank stratum;
4. an extra residual-factor frontier; or
5. projective infinity.

After those attachments, the remaining interior ideal must be proved complete
and zero-dimensional, its real points isolated and classified, and the
result transferred across the complete `S8` orbit.  Until that object exists,
the hard canary and all `1,162,302` final triple orbits remain unresolved.

## Replay

Regenerate the canonical sparse object:

```console
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/build_diag3_triple_fullspace_critical_h1.py
```

Run the independent exact replay:

```console
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/verify_diag3_triple_fullspace_critical_h1.py
```

Add the bounded modular diagnostics with:

```console
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/verify_diag3_triple_fullspace_critical_h1.py --modular
```

The manifest semantic digest is

```text
3cd9f4106c0a3299a22493f9375791d05d4a9f2ca3bcf17b63b88f83483aefea
```
