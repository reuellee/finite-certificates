# Parent-860 counterexample-guided routing pilot

## Result

The first proof-producing heuristic-to-exact routing loop has now been run on
catalog parent `860`, the proof-safe first-roadmap target.

The initial exact coordinate-star roadmap contains `23` generic chambers and
`22` residual crossings on the union of the nine coordinate segments of
radius `10^-4` through a normalized exact parent chart.  Complete derived
tope enumeration gives `26,264` supported extension signatures and only `12`
distinct proper support patterns on the star.

The simplest rooted-tree rule fails sharply.  Signature

```text
32537047406029546
```

has support mask `30768`, with three connected components on star vertices

```text
{4,5}, {11,12}, {13,14}.
```

Thus even an individual feasibility region need not restrict to a connected
subtree of a natural exact coordinate star.  This is a no-go for naive
geodesic routing, not a disconnectedness theorem for the full feasibility
region: paths outside the star may join the three pieces.

A two-round counterexample-guided repair then adds `16` exact straight-line
chords:

* `10` join repeated complete tope states and are residual-free;
* `5` cross exactly one primitive residual wall; and
* `1` crosses exactly two primitive residual walls and contributes one new
  generic chamber.

After the first `15` chords, every individual signature support is connected.
The smallest surviving obstruction is the pair

```text
32537047406029546, 32598344908487808,
```

whose common support has components `{4,5,11}` and `{23}`.  The final chord
`23--4` crosses only factor `19721` and repairs that pair.  On the resulting
`24`-chamber finite network, every finite intersection of the `12` proper
support patterns is connected.

This is an exact theorem about the embedded network.  It is not a complete
parent-space roadmap and does not promote diagonal nine or change the honest
9DVL score of `1/9`.

## 1. Exact parent-860 coordinate star

Relabel the columns of the stored parent-860 realization by

```text
(6,1,2,4,5,3,7,8)
```

and put the first five columns into the standard projective frame.  The last
three columns are `(1,a,b,c)`, `(1,d,e,f)`, and `(1,g,h,i)`, with

```text
a=40/7729          b=20720/22139       c=-9136/33929
d=14980/50917      e=184820/145847     f=12164/31931
g=-1910/7847       h=9970/22477        i=1962/4921.
```

For each coordinate, restrict every one of the `26,740` primitive localized
residual factors to `-10^-4<t<10^-4`.  Exact Sturm isolation gives the root
counts

```text
(a,b,c,d,e,f,g,h,i) = (5,1,2,4,0,4,3,1,2).
```

The `22` roots split the nine segments into `23` cells after their common
central cell is identified.  The checker also proves that no parent bracket
vanishes on any segment.  One exact tope enumeration per cell supplies the
complete labels; no floating-point sign is in the trust boundary.

Only six primitive factors occur on the star:

| factor | full `S_8` type | labeled multiplicity |
|---:|---:|---:|
| 12604 | 50 | 1 |
| 15250 | 49 | 1 |
| 16249 | 49 | 1 |
| 16573 | 49 | 1 |
| 19721 | 36 | 65 |
| 22629 | 36 | 65 |

The artifact stores these features on every crossing so subsequent matching
or routing searches can use factor type and multiplicity without recomputing
the orbit classification.

## 2. Counterexample-guided repair

The learner first identifies equal complete tope rows.  Ten straight segments
span those equality classes.  The exact verifier restricts every residual
factor and every parent bracket to each segment and proves that all ten have
zero roots, so the endpoints are not merely label-equivalent samples: each
pair lies in one certified chamber.

Five cross-state chords are then chosen by the smallest endpoint tope
differences among the surviving disconnected patterns.  Their complete root
profiles are

| chord | residual roots in order | restricted degrees |
|---|---|---|
| `2--8` | 15250 | 2 |
| `15--17` | 15250 | 1 |
| `1--17` | 22629 | 1 |
| `13--19` | 16573, 16249 | 3, 1 |
| `9--19` | 22629 | 1 |

No chord meets a parent boundary.  A one-root chord has only its two endpoint
chambers; all-strata gluing makes every common endpoint label feasible at the
crossing.  The two-root chord has one intervening generic chamber, whose full
`26,112`-tope label is independently enumerated.  This closes every
one-signature routing failure but exposes the two-signature obstruction above.

The final chord `23--4` has one isolated degree-two root of factor `19721`, no
parent root, and both adversarial signatures in its endpoint labels.  Adding
it makes every nonempty intersection in the complete finite closure of the
`12` proper masks connected.

The rule learned by this pilot is therefore interpretable:

1. quotient certified same-chamber states;
2. rank candidate chords by exact residual-crossing count and endpoint label
   difference;
3. add the lowest-complexity chord selected by the smallest disconnected
   support;
4. recompute the full intersection closure and repeat.

The chord list is discovered data, not a universal theorem.  Its value is
that every heuristic decision is followed by an exact all-factor audit and
the next failure is returned as a minimal certificate.

## 3. Exact verification

Run

```console
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/DIAG9_GRAPH_parent860_star.py
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/DIAG9_GRAPH_parent860_star_repair.py
```

The coordinate-star semantic digest is

```text
391e1ee3c8e416f927d0d9b0dd02f7411e7bf061802b5ffcebf20d2ae60af6a8
```

and the repaired-network semantic digest is

```text
3311c16bd553024891fc2cdcd68f2591135a43911146df221b4e1aa01672076e
```

The stored artifact SHA-256 values are

```text
9274371ec45baee318cd160f931344f37dc5031acc13d63c16099534b8896f4b  coordinate star
b295cceb3d97477f9b8c874b3d22b6a09d13d79bc4d3fa5daf14156bd9a03f55  star graph
f3ebf1f3a9b458663a12b042e68194aa24c4b55689cf85344e2d98f81aec3d11  repaired network
```

The semantic digests, rather than compressed-file bytes, are the primary
reproducibility pins.

## 4. Proof boundary and next target

The repaired network proves that the CEGIS architecture can learn through an
exact failure hierarchy: first a one-signature obstruction, then a pair
obstruction, then complete finite closure on the training network.  It does
not show that the `16` chords cover other chambers, that every parent-860
feasibility component meets the network, or that the same rule works for any
other parent.

The next target is to enlarge this network adversarially and attach its
codimension-two wall/node cells.  A useful rule must compress the discovered
chords into label- and factor-local features, survive new directions, and
then emit a width-safe Forman matching or augmented connectivity certificate.
Only after geometric coverage and infinity are certified can such a rule
contribute to a diagonal-nine proof; codimension-two closure is also the first
real test for diagonal eight.
