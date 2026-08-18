# Diagonal three: quadratic-cover elimination no-go

## Decision

The immediate plan of exploiting the parent-unit quadratic factor `L` by
direct resultants is retired.  This is an exact, finite method-level result,
not a timeout diagnosis.

The checker forms the `h` resultant of `L` with every one of the seven
hypersurface critical equations.  It then removes every exact factor among
the 62 nonconstant normalized parent-bracket polynomials and verifies that
no such factor remains.  Every primitive eliminant is much larger than its
source:

| equation | source terms | raw resultant | primitive terms | exact parent factors removed |
|---|---:|---:|---:|---|
| `E` | 594 | 48,086 | 19,806 | `[2357][2367][2378][3458]` |
| `E_c` | 421 | 50,655 | 27,800 | `[2378]^2[3458]` |
| `E_e` | 359 | 13,360 | 5,320 | `[2357][2367][2378][3458]` |
| `E_h` | 424 | 22,938 | 18,232 | `[2378]` |
| `G_f` | 886 | 83,413 | 59,449 | `[2378][3458]` |
| `G_g` | 505 | 58,593 | 38,653 | `[2367][2378]` |
| `G_i` | 815 | 87,712 | 49,757 | `[2367][2378][3458]` |

Thus none of the seven direct pairwise eliminations is a compression after
localization at the parent units.  Continuing this family would convert a
60-term cover and 359--886-term equations into primitive polynomials with
5,320--59,449 terms before the remaining equations are even used.

## Exact intersection of the two genuine charts

The calculation also resolves what happens when the transverse `P=0`
`c`-graph meets `L=0`.  Write

```text
P = p0 + c p1,
p0 = -f[1378]F,
p1 = (i-f)Q,
F = gh-i,
Q = d(h-i)+fh(g-1).
```

If `L=L0+cL1+c^2L2`, exact denominator clearing gives

```text
L0 p1^2 - L1 p0 p1 + L2 p0^2
  = [1237][1378][2378] F S.
```

On `P=0`, all four displayed factors outside `S` are nonzero: the three
brackets are parent units, and `F=0` would contradict
`Q-fF=[1357][1258]`.  Hence the intersection is exactly `S=0` there.

The primitive `S` has 105 terms, degrees 5 through 9, and is quadratic in
`d`, quartic in `g`, and cubic in `i`.  Its two useful top coefficients are

```text
coefficient_g^4(S) = -[1237]^2[1248][2357][2458],
coefficient_i^3(S) =  [1347]^2[2357][2458][3458].
```

Thus `S=0` is another bounded finite cover, not an empty branch or a graph
with a degree-drop escape.

## The discriminant-sign route is also false

As a quadratic in `d`, `S` has

```text
disc_d(S) = [1237]^2 D,
```

where primitive `D` has 315 terms, degrees 6 through 14, no parent-bracket
factor, and no `F` factor.  The verifier evaluates `D` by exact rational
arithmetic on the stored realization of every one of the 2,604 realizable
uniform rank-four parent types in the identity frame:

```text
positive  2,162
negative    442
zero          0
```

The source-index/sign digest is

```text
bb697652bb4c85974e832af698a58c6861a46b7586e1c410585fb92ec9bbda91.
```

The two nonempty signs are exact counterexamples to any claim that this
reduced discriminant has one universal sign throughout all parent cells.
The census does not assert sign variation inside a fixed cell and does not
infer the existence or absence of real roots from samples.

## Consequence for research effort

This certificate rules out a whole neighborhood of tempting next moves:

1. expand a critical equation modulo the quadratic `L`;
2. take any one of the seven direct `L` resultants and continue with the
   primitive expansion; or
3. try to discard the `P=L=0` intersection by a universal sign for
   `disc_d(S)`.

It does **not** rule out a factored simultaneous syzygy or a topology-first
proper-escape proof.  The next algebraic work, if retained at all, should be
a bounded search for a low-degree unit-minor/Koszul identity using the full
factored system; it should not construct another expanded eliminant.  If
that bounded structural test fails, the research should move to the other
already identified completion route: the coverage-certified global master
closure poset and its infinity incidence.

The honest score remains `2/9`, with `1,162,302` triple orbits unresolved.

## Replay

```bash
PYTHONDONTWRITEBYTECODE=1 \
  python ai/omreal/verify_diag3_triple_quadratic_cover_no_go.py
```
