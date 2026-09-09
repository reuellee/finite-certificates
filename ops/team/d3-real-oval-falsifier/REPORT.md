# A compact fixed-base source oval survives all 70 parent brackets

The proposed extrapolation from the cefc495 example is **false**: a smooth
compact real oval of this fixed-base factor source can lie entirely inside
one uniform parent sign cell. This is an obstruction to universal escape
with these five base coordinates fixed. It supplies no compact component
of the full six-dimensional source or of the actual triple-bad locus.
The diagonal ledger remains **2/9** and the residual source count is unchanged.

Base commit `cefc495b27247c4a76f88bce04978422161f7ce9`, tree
`c49c2e6625f3ee76d77cc263897366dcf7e037c2`. The original source is
`ai/omreal/data/DIAG3_triple_fullspace_critical_h1.json`, SHA-256
`c9244a47ded5736e7afe724a9914e75631a22b78653442e88c14f5c397919eb8`,
named presentation `(5563,16134,19284)`. No surrogate equations are used.

## Quantified counterexample and exact graph

Let the parent matrix be

```text
Y = [1 0 0 0 1 1 1 1]
    [0 1 0 0 1 a d g]
    [0 0 1 0 1 b e h]
    [0 0 0 1 1 c f i].
```

The 70 parent brackets are the determinants of its four-column submatrices,
using increasing labels from 1 through 8. Fix

```text
(b,f,g,h,i) = (-11/3,-11/4,-5/3,3/2,17/4),
d = -253/51.
```

The original first equation `bf-bi+di-fg=0` holds identically. On the uniform
parent domain the second equation has the exact graph

```text
a = (27648c²e - 27648c² + 78364ce - 324544c
     + 131648e - 224213) / (9180ce - 92565).
```

Its denominator is `-9180[1267]`, because
`[1267]=bf-ce=121/12-ce`. It is a genuine parent bracket. The second
equation's a-coefficient is `(f-1)(h-1)(bf-ce)` and its non-bracket factors
are nonzero at this base. Substituting this graph into the third original
equation gives a nonzero constant multiple of `F/denominator`, where

```text
F(c,e) = (18255348c² + 20097264c + 90639648)e²
       + (46586700c² - 152831855c + 517911460)e
       - 69493248c² - 776709769c + 789818062.
```

The checker verifies these polynomial identities directly from source
bytes. Thus `F=0` and denominator nonvanishing are equivalent to the three
original equations on this fixed-base uniform domain; no rank stratum is
discarded beyond that actual parent boundary.

## The complete compact oval

Write `F=C2(c)e²+C1(c)e+C0(c)`. Then

```text
C2(c) = 204(89487c²+98516c+444312) > 0 for every real c,

W(c) = C1(c)²-4C2(c)C0(c)
     = 7244814320451216c⁴
       + 48063061558815336c³
       + 101573872480197601c²
       + 59803333510239176c
       - 18123044095557104.
```

Positivity of `C2` follows from its positive leading coefficient and
negative discriminant; both are checked over the rationals. The four
real roots `r1<r2<r3<r4` of `W` are simple, with isolating intervals

| Root | Lower bound | Upper bound |
| --- | --- | --- |
| r1 | -676/249 | -695/256 |
| r2 | -676/319 | -89/42 |
| r3 | -127/63 | -764/379 |
| r4 | 11/51 | 118/547 |

The checker verifies opposite endpoint signs, one root by Sturm count in
each disjoint interval, and a constant last nonzero Sturm remainder for
squarefreeness. Degree four exhausts all roots. Its positive leading
coefficient implies `W>0` on `(r2,r3)` and `W=0` at the endpoints.

Consequently the two graphs

```text
e±(c) = (-C1(c) ± sqrt(W(c)))/(2C2(c)),  r2 ≤ c ≤ r3
```

join at their two endpoints and nowhere else. Their union `O` is a compact
connected curve homeomorphic to a circle. It is smooth: away from the
endpoints `F_e=±sqrt(W)` is nonzero. At an endpoint, differentiating the
discriminant identity gives `W'=-4C2 F_c`, because `F_e=0` there, so `F_c`
is nonzero by squarefreeness. The other affine components occur over
`(-infinity,r1]` and `[r4,infinity)` and are separated from `O` by gaps with
no real points. Thus `O` is a complete connected component of `F=0`.

## Every bracket is nonzero on the whole oval

The closed rational interval

```text
J = [-53/25,-403/200]
```

contains `[r2,r3]` strictly and no other root of `W`. The certificate
addresses all 70 original brackets, including their constants and coordinate
factors, with no sign-cell sampling assumption.

For each bracket `p(a,c,e)` after the fixed-base substitution, write
`p=p0(c,e)+a p1(c,e)`. Define its cleared numerator

```text
Kp = p0·denominator + p1·numerator.
```

The checker reconstructs `p` by an explicit 4x4 determinant, reconstructs
`Kp`, and computes the Sylvester determinant
`Rp(c)=Res_e(F,Kp)` using exact rational polynomial arithmetic. It verifies
the stored resultant up to a nonzero scalar and proves by its own Sturm
algorithm that `Rp` has **zero roots on J**. It also rejects an endpoint
root, so this is a closed-interval exclusion. All 70 checks pass. The same
reconstruction and zero-root test hold for `Res_e(F,denominator)`.

If a bracket vanished anywhere on `O`, or if the graph denominator vanished
there, its specialized pair of polynomials would have a common real e-root.
The corresponding Sylvester determinant would vanish at that c. Every such
c belongs to J, contradicting its certified zero-root count. This proves
whole-oval bracket and denominator avoidance, including both branch points.

The graph to the original nine coordinates is continuous and injective on
the compact oval and has projection `(a,b,c,d,e,f,g,h,i)↦(c,e)` as its
inverse. Its image is therefore a compact connected smooth oval in the
original fixed-base factor source. Every parent bracket is continuous and
nonzero on this connected oval, hence has one constant sign there. The
entire oval lies in one connected component of one uniform parent sign
region, giving the stated counterexample.

For an explicit sign anchor, choose `c=-21/10` and the unique root of
`F(-21/10,e)` in

```text
-6285/1546 < e < -7094/1745.
```

The checker isolates this algebraic point by Sturm count and evaluates
rational interval bounds for the denominator and all 70 cleared bracket
numerators. All signs are strict. In lexicographic order of increasing
four-label subsets the signs are

```text
++--+-++-++++--++--+--+-+-++-------------+-++++-+---++-+----+----++++-
```

The same sign string is stored in `verification.json`.

## Scope, acceptance, and stopping decision

The retired statement is: *for every real base `(b,f,g,h,i)`, every compact
real oval of this fixed-base factor source must meet a parent bracket zero
or the graph denominator*. The exhibited base and entire oval contradict
it. In particular the successful cefc495 fixed-base argument does not
extend universally by a change of coefficients.

No assertion is made that this oval is a compact component when base
coordinates move. No point or component here has been independently admitted
to a proper pairwise-incomparable signature triple's actual triple-bad locus.
The full-source component quantifier, actual triple-bad compact support
vanishing, and the alternating pair Hc1 map remain unresolved. Neither the
1,162,302 residual source denominator nor any theorem ledger is changed.

Classification: **INFORMATIONAL** strategy obstruction; the theorem-distance
coordinates remain unchanged. The positive universal fiberwise escape route
is now disproved for this source. Discovery stopped immediately at this
exact candidate; there was no expansion to a broader census or another base.
The coordinator's independent referee must decide final acceptance.

## Reproduction and discovery record

The acceptance checker requires only the Python standard library:

```text
python3 -B ops/team/d3-real-oval-falsifier/verify_certificate.py
```

It imports no producer or historical arithmetic and rejects a corrupted
fiber, an omitted bracket, a corrupted resultant, and a changed base.
`verification.json` records a passing replay and those four rejected controls.
Exact polynomial construction can be regenerated with SymPy 1.14.0 via
`build_certificate.py`; CAS output is not trusted by the independent replay.

Heuristic discovery first examined 4,000 seeded integer-grid bases, of which
1,376 passed fixed-bracket unit checks. It detected 198 candidate compact
ovals, all rejected by sign samples. A second seeded scan of 20,000 Gaussian
perturbations of the historical base detected 5,053 candidate ovals, with
37 finite-sample survivors. Rational approximation of those survivors gave
the displayed small rational base; its coefficients and bracket resultants
were then certified exactly. Search results are heuristic only and do not
exhaust a parameter domain. Their records are `grid8.json`, `local1.json`,
and `rational_survivors.json`; their sampled margins carry no theorem credit.

Each completed symbolic construction or replay used less than one second of
wall time. The local heuristic scan took approximately 23 seconds. There
were no solver timeouts, paid computations, external publication actions,
or mutations of existing research artifacts. An initial environment
probe found SymPy unavailable; the coordinator supplied temporary shared
dependencies. A discovery array-length bug was repaired before either
recorded scan completed; acceptance uses its separate implementation.
