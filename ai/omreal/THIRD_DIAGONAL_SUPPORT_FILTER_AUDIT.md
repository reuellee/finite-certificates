# Independent audit of the third-diagonal support filter

## Outcome

The census in `verify_third_diagonal_support_filter.cpp` is correct.  An
independent Python/SymPy/NumPy implementation reproduces every reported total:

| stage | exact labeled count |
|---|---:|
| generic five-supports | 2,021,992 |
| generic supports covering all eight labels | 1,099,560 |
| covered supports with `delta >= 3` | 339,360 |
| remaining all-unit supports | 0 |
| retained supports | 760,200 |
| retained `S_8` orbits | 45 |

The 45 survivor orbits split as `44` with `beta=0` and one with `beta=1`.
The complete labeled stratification is

| `delta` | `beta` | residual cofactors | count |
|---:|---:|---:|---:|
| 1 | 0 | 3 | 20,160 |
| 1 | 0 | 4 | 5,040 |
| 1 | 0 | 5 | 40,320 |
| 2 | 0 | 1 | 58,800 |
| 2 | 0 | 2 | 260,400 |
| 2 | 0 | 3 | 272,160 |
| 2 | 0 | 4 | 15,120 |
| 2 | 0 | 5 | 85,680 |
| 2 | 1 | 4 | 2,520 |

The independent lexicographic representative of the unique `beta=1` orbit is

```text
123/125/346/378/456.
```

It is isomorphic to the C++ representative
`156/456/137/347/128`; one label map from the latter to the former sends
`12345678` to `37154628`.

## Independence of the check

The audit is implemented in
`verify_third_diagonal_support_filter_independent.py`.  It does not import any
project classifier and does not use the C++ program's list of residual orbit
indices.

1. It constructs the full `S_8` action on the 56 triples and obtains the 52
   four-support orbits directly.
2. On a fresh symbolic `4 x 8` chart, it factors all parent brackets and the
   derived determinant of each orbit representative over `QQ`.  A determinant
   is declared a unit exactly when all its irreducible factors occur in parent
   brackets.  This independently recovers `14` zero, `25` unit, and `13`
   residual orbit types, comprising respectively `58,660`, `223,790`, and
   `84,840` labeled four-supports.
3. It tests five-support genericity with packed integer degree and codegree
   counters, rather than the C++ loops.  It computes `delta` using ordered
   forbidden-edge masks.
4. It recomputes survivor orbits by a vectorized group action and computes
   `beta` from the exact rational rank of each centered incidence matrix in
   SymPy.  Thus the rank result is not a second modular calculation.

## Mathematical audit of the C++ predicates

For five distinct triples, every four-subset is nonstructural exactly when
no vertex has degree at least four and no vertex-pair has codegree at least
three.  Indeed, a structural four-subset either has a common vertex, producing
degree at least four in the five-support, or has a fixed pair in three of its
edges, producing codegree at least three.  The converse is obtained by taking
the four high-degree edges, or the three high-codegree edges plus either
remaining edge.  Hence `generic_five` has neither false positives nor false
negatives.

After the coverage test, every moving label occurs in some edge.  Therefore
the vacuous case in the definition

```text
D_f(Q) = {e != f : every edge containing e also contains f}
```

cannot inflate `delta_of`; its forbidden-edge test is exactly the definition.

Finally, the modular rank routine is exact over `QQ`.  A centered incidence
row is the difference of two three-set indicator vectors and has squared norm
at most six.  Hadamard bounds every square minor of order at most four by 36.
Since `65,521 > 36`, no nonzero integer minor can vanish modulo the chosen
prime, while a nonzero modular minor necessarily came from a nonzero integer
minor.  Thus the modular and rational ranks agree.

## Reproduction

```bash
g++ -std=c++17 -O2 -Wall -Wextra -pedantic \
  ai/omreal/verify_third_diagonal_support_filter.cpp \
  -o /tmp/verify_third_diagonal_support_filter
/tmp/verify_third_diagonal_support_filter

PYTHONPATH=/tmp/diag_high_sympy \
  python ai/omreal/verify_third_diagonal_support_filter_independent.py
```

This audit certifies the finite necessary-condition reduction only.  It does
not establish the topology of the 45 retained generic loci or the gluing of
nongeneric and smaller-support faces, so it is not by itself a proof of the
third diagonal.
