# Diagonal three: one exact boundary-to-boundary concurrence slice cell

## Scope and outcome

This note records an exact critical census and one replayable
boundary-to-boundary cell in the boundary-stratified concurrence roadmap.
Subject to the explicitly isolated `msolve-0.10.1` exact-CAS trust boundary
below, it proves that **every** component of the pinned affine slice in the
selected source parent chamber is noncompact.  The critical computation is
saturated by

```text
[1234] * t * (4t+3) * (20t-3) = 0.
```

but the exact frontier identities below prove that none of the removed loci
contains a uniform-parent solution of this pinned incidence system.  The
result does **not** prove the corresponding statement on the full
nine-variable factor-triple zero set, close its orbit, or close any of the
current `1,162,302` unresolved triple-factor orbits.

For the hard presentation

```text
(5563,16134,19284)
```

the pinned concurrence slice has a real critical point at

```text
t in [0.7879209203118614, 0.7879209203118616].
```

The old certificate proved only that the four-by-four fiber Jacobian has
rank three there.  The new check proves that the full five-by-five Jacobian

\[
 {\partial(F_1,F_2,F_3,F_4,R)\over
  \partial(v_r,v_s,w_r,w_s,t)}
\]

is nonzero and that the second derivative of `t` along the normalized
fiber-kernel direction is strictly negative.  Hence the point is a simple
fold.  The exact local roadmap graph is

\[
  G_-^{(1)}\;---\;\rho\;---\;G_-^{(2)},
\]

where the two regular sheet germs lie on `t<t(rho)` and `rho` is an internal
bivalent vertex.  Ramification is therefore a sheet attachment, not a
boundary leaf.  The continuation below joins those germs respectively to
the source faces `[2678]=0` and `[2467]=0`.

## Frontier separation at the fold

Exact rational interval arithmetic proves all of the following in one
neighborhood of `rho`.

| stratum | exact result |
|---|---|
| fiber ramification | corank one and simple; the full five-equation determinant is strictly negative |
| fold direction | `d^2t/ds^2` lies in `[-53.1898968968,-53.1898968889]` |
| concurrence points | the three coordinate concurrence points are independent |
| occurrence-normal rank | each of the three selected occurrences has a separated rank-three minor |
| column normalization | all eight `h_j` equal `1` in this normalized chart |
| affine gauge | the normalized gauge difference is `1` |
| interpolation charts | `t`, `4t+3`, and `20t-3` are all separated from zero |
| projective fiber infinity | both affine-fiber homogenizing coordinates equal `1`; the four fiber coordinates remain finite |
| source parent boundary | all `70` parent brackets are nonzero; the smallest interval margin exceeds `0.00126104` |
| other residual divisors | exactly factors `5563`, `16134`, and `19284` vanish among all `26,740` factors |

Thus both half-edges incident to `rho` stay, locally, in the same uniform
parent cell and avoid every chart and extra-factor divisor listed above.

## Complete critical census for the pinned slice

Use `t` as height on the five-variable affine slice.  The stored saturated
critical system consists of `F1,...,F4,R`, where `R` is the four-by-four
fiber-Jacobian determinant, together with inverse equations for `[1234]` and
for the interpolation denominators.  An exact `msolve-0.10.1` computation
reports a zero-dimensional ideal of degree `20`, a degree-`20` squarefree
eliminant with `t` as separating form, and exactly six real roots:

| root | rational isolating interval for `t` | positive/negative parent brackets | Hamming distance from fold chamber |
|---:|---:|---:|---:|
| 1 | `(-1/2,-1/4)` | `35 / 35` | `37` |
| 2 | `(-1/50,-1/100)` | `32 / 38` | `36` |
| 3 | `(0,3/1000)` | `36 / 34` | `32` |
| 4 | `(1/10,2/5)` | `36 / 34` | `36` |
| 5 | `(7/10,1)` | `42 / 28` | `0` |
| 6 | `(2,3)` | `49 / 21` | `11` |

The dependency-free replay performs the following logically separate
checks.  Descartes transformations partition the entire real line and prove
that the stored eliminant has exactly these six real roots.  Exact polynomial
remainders prove that all five RUR coordinates satisfy the stored critical
system.  Rational interval arithmetic proves all `70` parent brackets strict
at every root, recomputes the six sign strings, separates a fiber rank-three
minor and the full five-equation Jacobian, and proves a nonzero kernel
contraction at each root.  Thus all six represented real solutions are simple
corank-one folds, and root 5 is the unique one in the selected parent chamber.

The converse claim is kept honest: RUR substitution by itself neither rules
out additional solutions nor positive-dimensional components.  Completeness
of the saturated critical ideal is supplied by the exact Groebner/FGLM run,
not inferred from RUR satisfaction.  Its tracked input is
`data/DIAG3_concurrence_ramification_complete.msolve` (`2,992` bytes), with
SHA-256

```text
a13bd2e95337ff571ff577ec83ed1515c57764e579e28ef61a10bfce3b94f09d
```

The exact command and pinned output digest are

```bash
/tmp/caslocal/bin/msolve -P 1 -p 256 -v 1 \
  -f ai/omreal/data/DIAG3_concurrence_ramification_complete.msolve \
  -o /tmp/diag3_slice_critical_audit.out
```

```text
msolve 0.10.1 binary:
eaa747952192d0e62a1e29387a6a7dc0ad77e96ff9969d9bcba64179f3e8e207

exact output:
a802303ebdb11bc0985d8445245b7d64726bea398b08b1c127dd6cc3a912464f
```

The ordinary verifier pins the input and output digests and includes a
one-coefficient corruption canary.  Passing `--msolve` reruns the external
CAS and requires the fresh output to match byte for byte.  Without that flag,
the dependency-free algebraic consequences replay, but the complete-slice
theorem remains explicitly conditional on the pinned exact-CAS result.

### Saturation-frontier exclusion

The dependency-free verifier also reconstructs the two inverse equations in
the `msolve` input.  The first is exactly the inverse of the parent bracket
`[1234]` after clearing the interpolation denominators, and the second is
exactly the inverse of

\[
                    t(4t+3)(20t-3).
\]

Thus `[1234]=0` is a parent boundary and is absent from every uniform parent
chamber.  The other three removed divisors require a separate check because
an interpolation pivot can vanish inside a parent chart in general.

At each of `t=0,-3/4,3/20`, the verifier returns to the original twelve
concurrence incidences rather than substituting the singular interpolation
formulas.  It row-reduces over `Q` the four color-two and four color-three
collinearity equations with the affine gauge `z_1=0,z_2=1`.  Both systems have
rank four, and the resulting two-parameter affine kernels exhaust all their
solutions.  Exact polynomial determinants on those kernels give

| removed divisor | identity forced by the original incidences |
|---|---|
| `t=0` | `[1348]=[1578]=0` |
| `4t+3=0` | `P_4=P_8`, hence all `15` brackets containing `{4,8}` vanish |
| `20t-3=0` | `[2578]=0` |

Each row contradicts parent uniformity before the remaining four color-one
incidences are even imposed.  Therefore saturation discards no point of the
unsaturated pinned affine slice inside the selected uniform parent chamber.

## Exact boundary continuation

The data file
`data/DIAG3_triple_fold_boundary_chain.json` pins `322` rational vertices in
the coordinate order `(v_r,v_s,w_r,w_s,t)`, all with common denominator
`10^13`.  Its SHA-256 is

```text
3e665f0923fed4bef65def70ea15c875cd868fede3bfc618c0407380a2cb3301
```

The verifier uses `v_r` as the continuation parameter and replays exact
rational interval arithmetic only; NumPy and SciPy are not imported.  For
each of the two branches it certifies `160` parametric Krawczyk boxes in the
other four variables.  A final Krawczyk box bridges the two near-fold
vertices.  The exact accounting is

| item | exact result |
|---|---:|
| stored rational vertices | `161 + 161 = 322` |
| sheet segments | `160 + 160 = 320` |
| fold bridge | `1` |
| shared endpoint identifications | `159 + 159 + 2 = 320` |
| left radii | `157` at `10^-6`; `3` at `2*10^-6` |
| right radii | `160` at `2*10^-7` |
| bridge radius | `10^-6` |

Adjacent boxes use the literally identical rational predictor vertex.  Their
centered scalar-radius fiber boxes are nested, so Krawczyk uniqueness
identifies the two endpoint roots.  The isolated RUR fold lies inside the
bridge parameter interval and its four local coordinates lie inside the
bridge Krawczyk box.  Thus the local fold cell and the continuation chain are
the same connected slice cell.

Direct determinant interval evaluation proves that no nontarget parent
bracket vanishes on either branch and that all `70` parent brackets are
nonzero on the bridge.  Raw determinant intervals wrap around zero for the
target near its exit, so the verifier instead evaluates exact cleared
numerators.  Their only zero-containing box is segment zero on each branch.
At the two endpoints of those boxes the intervals are

| source face | first endpoint | second endpoint | derivative along root graph |
|---|---:|---:|---:|
| `[2678]` | `[6.13701e-5,6.31999e-5]` | `[-3.21152e-4,-3.19322e-4]` | `[-0.350825277284,-0.326009966641]` |
| `[2467]` | `[-0.154914,-0.154554]` | `[0.0317504,0.0321088]` | `[337.270304123,349.018058317]` |

The derivative enclosure is the exact Schur-complement quotient of a
five-by-five determinant by the four-by-four fiber determinant.  Both
determinants avoid zero, so each displayed sign change is transverse and
unique in its box.  The factors cleared from the two target determinants are
products of `4t` and `136(20t-3)`, already separated from zero on the chain.
Consequently the certified graph is

\[
 [2678]=0\;---\;160\text{ cells}\;---\;\rho\;---\;
 160\text{ cells}\;---\;[2467]=0.
\]

The portion inside the fixed source parent cell approaches two different
parent-boundary faces.  Hence the slice component containing `rho` is
noncompact.

Under the saturated-critical-ideal completeness boundary, this also excludes
every other compact component of the selected pinned slice.  Indeed, `t`
attains a maximum and a minimum on any compact component.  At either a smooth
extremum the fiber Jacobian has determinant zero; a singular point has the
same conclusion automatically.  A component on which `t` is constant would
give infinitely many critical points unless it were isolated, while every
certified critical point is locally a one-dimensional simple fold.  Therefore
any compact component contains a critical point.  Root 5 is the only critical
point in this parent chamber, and its component is the certified
boundary-to-boundary component.  No compact component remains.  The exact
saturation-frontier exclusion above is what promotes the exact-CAS census
from the saturated chart to the unsaturated pinned slice.

## Exact hard-canary source accounting

The six named hard presentations represent five distinct source orbits:

| named presentation | canonical union-four row |
|---|---|
| `(2277,390,22507)` | `(2277,390,22507)` |
| `(5563,16134,19284)` | `(5563,4373,23221)` |
| `(12985,16183,7196)` | `(5563,4373,23221)` |
| `(20355,5442,5949)` | `(5563,5031,11209)` |
| `(9667,16486,26315)` | `(2267,4271,20520)` |
| `(9758,24338,15810)` | `(13950,4097,17312)` |

The verifier pins an explicit `S_8` label permutation and ordered factor
image for each row.  The five canonical rows have respectively

```text
65, 1, 1, 1, 2
```

occurrence-presentation products, `70` in total.  Their complete occurrence
payload has semantic digest

```text
54bf6637941cfaff91a394d3eaad456a54e1adf74fb22c988454f9eec47f41e2
```

With the pinned union-four bucket supplied, the replay verifies that all five
rows occur in its `1,897,733` records (SHA-256
`54b03c31910de606b80f9dcc448ce3dde93063a8dbc3f2dbcaa7a02901df0303`).
It also proves that every row fails the exact triangular predicate and is
absent from both the `65,550` Morse records and the `61` frame-1119 records.
Thus all five lie in the former `1,819,789` post-Morse/shear residue.  The
later sequential-affine layer closes `(2277,390,22507)` independently.  The
other four canonical rows, including the selected fold row
`(5563,4373,23221)`, lie in the exact `1,162,302`-row residue after the
subsequent all-chart double-graph, graph-unit-minor, direct-final-affinity,
support-two primitive-final, and support-three primitive-final layers as
well.  The complete recorded final-affinity union was checked explicitly
against these four rows.

## Exact remaining obstruction

The critical census removes the missing-component obstruction for this
**pinned affine slice**, conditional on the named exact-CAS trust boundary.
The exact incidence identities above exclude every divisor removed by the
saturation in a uniform parent chamber.  The result does not prove that fixing
the five base-`u` coordinates
preserves the connected-component obstruction of the full nine-variable
factor-triple zero set.  Thus it is not an orbit theorem and does not by
itself change the honest `2/9` score.  The next orbit-closing certificate must
apply the same extremum argument without fixing those base coordinates, or
provide an independent lift from every full component to a certified slice.

There is a shorter possible structural certificate.  If some fixed linear
height `h` and constant three-vector `C in Lambda^3 ker(h)` satisfy

\[
 (dq_1\wedge dq_2\wedge dq_3)(C)=U,
\]

where `U` is a nowhere-zero product of signed parent brackets, then the
restriction of the three differentials to `ker(h)` has rank three everywhere.
At a maximum or minimum of `h` on a compact triple-zero component it would
have rank at most two, a contradiction.  The argument does not require `C`
to be decomposable and has no boundary/corner gap because a compact component
of the open parent cell attains its extrema in that cell.  Such an identity
would close an orbit without a roadmap.  Current constant low-product span
screens on the hard canaries find no such identity; that negative screen is
not a theorem against higher-degree or polynomial-multivector certificates.

Absent such a global submersion identity, a full-space critical census for a
coordinate height is the shortest direct upgrade.  It must solve
`q1=q2=q3=0` together with the rank drop of their differentials on the height
kernel, saturate every parent/chart/extra-factor frontier, classify every real
critical point by parent chamber, and attach each in-chamber critical point to
a noncompact branch.  The present file completes that logic only after the
five-coordinate pinning.

## Replay

The fold, boundary chain, and tracked later-layer exclusions are checked by

```bash
python ai/omreal/verify_diag3_triple_concurrence_local_fold_cell.py
```

Exact membership in the pinned union-four source is added by

```bash
python ai/omreal/verify_diag3_triple_concurrence_local_fold_cell.py \
  --union4 /path/to/diag3_union_degree4.bin
```

The result is a noncompactness theorem for the one certified slice component.
With a matching `msolve-0.10.1` replay, it is also a no-compact-component
theorem for the complete selected pinned affine slice.  It is not an
all-component theorem for the full factor triple, not an orbit closure, and
not a change to the honest `2/9` score.  The all-`26,740` other-factor
separation check remains local to the fold neighborhood; the slice theorem
uses the critical census and parent-wall exits, not a claim of segmentwise
extra-factor separation along the continuation chain.

For a fresh completeness replay use

```bash
python ai/omreal/verify_diag3_triple_concurrence_local_fold_cell.py \
  --union4 /path/to/diag3_union_degree4.bin \
  --msolve /path/to/msolve-0.10.1
```
