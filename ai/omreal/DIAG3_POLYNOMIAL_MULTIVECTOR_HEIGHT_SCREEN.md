# Diagonal three: bounded polynomial-multivector height screen

## Outcome

This is a productionized negative screen, not a new closure.  The exact score
remains `2/9`.

For all six hard canaries, all nine normalized coordinate heights, and every
parent-bracket product of length at most three, the bounded Macaulay test has
zero hits over both `F_2` and `F_3`.  Unlike the earlier degree-nine scratch
run, the production profile raises the two high-degree canaries to degrees ten
and eleven, so **every nonzero height minor is actually present**.  The
semantic digest is

```text
d8e9ad3900d3846ade58ca2fc23feccce1f158e27a46cb334b416fc9420dd38a
```

The modular conclusion is deliberately limited: even simultaneous misses at
2 and 3 are not a characteristic-zero nonmembership proof.  No triple orbit
is added to the theorem-safe closure count.

## 1. Certificate being screened

Fix a coordinate height `x_h` and write `M_J` for the 56 three-by-three
Jacobian minors of `q=(q_1,q_2,q_3)` using three coordinates different from
`h`.  A parent-unit certificate is a polynomial identity

\[
 U=\sum_{i=1}^3 A_iq_i+\sum_J B_JM_J,                 \tag{1}
\]

where `U` is a product of nonzero parent brackets.  On the parent chamber,
`U` never vanishes.  At an extremum of `x_h` on a compact component of
`{q=0}`, the restricted differential has rank below three, so every `M_J`
vanishes.  Evaluating (1) gives the contradiction `U=0`.  Polynomial
coefficients `B_J` are exactly the coordinate coefficients of a polynomial
trivector in `Lambda^3(ker dx_h)`.

For a degree bound `D`, the verifier inserts every monomial multiple of every
generator whose total degree is at most `D`.  Thus it tests the complete
degree-`D` Macaulay piece of the displayed ideal, not only constant
trivectors.  A target whose monomial support is not contained in the union of
the generator-multiple supports is rejected exactly over the integers from
this degree-`D` Macaulay row space.

The remaining linear membership test is modular.  A rational identity of
bounded degree reduces to an identity modulo every prime outside a finite
exceptional set, but a particular prime can divide its cleared target
coefficient.  Therefore:

* a modular hit is only a candidate and requires exact rational replay;
* a modular miss at 2 or 3 is useful falsification data, not a `Q` no-go; and
* only the reported support rejections are exact bounded-degree negative
  statements inside the stated degree-`D` Macaulay row space.

## 2. Fully replayed bounded profile

There are 62 nonconstant parent factors and

\[
 1+62+1953+41664=43680
\]

products with repetition of lengths zero through three.  Every target has
degree at most nine.  The per-canary degree is the cheapest one which also
contains every nonzero restricted minor:

| canary | core kinds | `D` | nonzero minor degrees | largest minor multiplier degree |
|---:|---|---:|---|---:|
| 0 | `(36,51,49)` | 9 | 7 | 2 |
| 1 | `(50,50,51)` | 9 | 8 | 1 |
| 2 | `(50,51,50)` | 9 | 7, 8 | 2 |
| 3 | `(50,50,50)` | 10 | 10 | 0 |
| 4 | `(50,49,50)` | 11 | 10, 11 | 1 |
| 5 | `(48,51,51)` | 9 | 8 | 1 |

The default replay therefore comprises `6*9*2=108` exact finite-field
Macaulay calculations.  It reports no omitted generator, no target which
becomes the zero polynomial modulo either prime, and zero membership hits.
The `F_2` and `F_3` ranks agree in every height.  The `F_3` implementation is
bit-sliced and is cross-checked at startup against an independent dense
Gaussian-elimination self-test.

Run the pinned profile with:

```bash
python ai/omreal/verify_diag3_polynomial_multivector_height_screen.py
```

On the present machine it takes about seven minutes.  A quick representative
replay is:

```bash
python ai/omreal/verify_diag3_polynomial_multivector_height_screen.py \
  --canary 1 --height 0 --prime 2 3
```

## 3. Exact 26-kind residue census

The pinned post-triangular source has SHA-256

```text
1c64017faad2173a3552dd70427d893c6ad4e39f31075ef9941c871f11184949
```

Removing the 65,550 exact Morse rows and 61 disjoint constant-shear rows
leaves 1,819,789 rows in exactly 26 unordered kind triples:

| kinds | rows | kinds | rows |
|---|---:|---|---:|
| `(36,49,50)` | 1,342 | `(36,49,51)` | 748 |
| `(36,50,50)` | 1,820 | `(36,50,51)` | 1,851 |
| `(36,51,51)` | 443 | `(38,50,50)` | 2,473 |
| `(38,50,51)` | 2,731 | `(38,51,51)` | 750 |
| `(48,48,50)` | 85 | `(48,48,51)` | 70 |
| `(48,49,49)` | 1,760 | `(48,49,50)` | 5,086 |
| `(48,49,51)` | 2,838 | `(48,50,50)` | 3,685 |
| `(48,50,51)` | 4,224 | `(48,51,51)` | 1,463 |
| `(49,49,49)` | 33,525 | `(49,49,50)` | 147,535 |
| `(49,49,51)` | 85,032 | `(49,50,50)` | 271,709 |
| `(49,50,51)` | 309,380 | `(49,51,51)` | 86,593 |
| `(50,50,50)` | 233,155 | `(50,50,51)` | 387,200 |
| `(50,51,51)` | 200,916 | `(51,51,51)` | 33,375 |

If the pinned source file is available, replay the factor-kind alignment and
all exclusions with:

```bash
python ai/omreal/verify_diag3_polynomial_multivector_height_screen.py \
  --skip-screen --residue-source /path/to/affine3_union4_after_triangular.bin
```

This command is a census replay only.  The 26 kinds are workload buckets, not
equivalence classes for ideal membership: different relative labeled factors
in one kind triple have different normalized polynomials.

## 4. Full-residue feasibility and next action

The bounded six-row replay already takes about seven minutes.  Scaling the
same Python rowwise construction to 1,819,789 rows and nine heights would be
measured in years, before exact replay of any modular candidate.  A full scan
was therefore not run, and there are no honest closure counts by kind beyond
`0/6` for the named hard canaries.

The cheapest credible full-residue implementation would stream the pinned
rows and use, in this order:

1. the exact monomial-support rejection;
2. one bit-sliced prime as a candidate filter, stopping at the first unit;
3. recursive divisibility/saturation of the surviving quotient subspace,
   instead of materializing all 43,680 products at every height; and
4. exact rational reconstruction for every modular hit.

That needs a compiled sparse/F4-style backend with caching by actual factor
polynomial, not merely by the 26 kind labels.  Until such a backend exists,
the boundary-roadmap route remains strictly higher priority than extending
this negative diagnostic.
