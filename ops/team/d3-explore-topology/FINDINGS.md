# Complete actual triple-bad chord, with a transverse escape

**Finite exact auxiliary geometry; no theorem credit.** For the source-admitted
row-2599 triple, the complete horizontal triple-bad slice is a compact interval
strictly inside its maximal parent chord. Every point of that interval lies in
one actual triple-bad component with an explicit transverse proper escape to a
genuine parent boundary. Thus a compact slice can coexist with an escaping
ambient component. No compact ambient component or hole was found or certified.
The global ledger stays 2/9; no original obligation or exhaustive residual closes.

Opening revision: `c27a36d6e3f47a2b4c7bb017774cbe5df30abdc2`.
Mathematical base: `21a97db6aa66912fd37556d81711c0588c454a7d`.
Only `ops/team/d3-explore-topology/` is changed. Sources are hash-pinned in
`SOURCE_MANIFEST.json`. This is the initial two-coordinate test plus its one
exact follow-through, now frozen. Independent acceptance belongs to the referee.

## Actual parent and original labels

Take the exact `upper_chart_0_flow.json` parent Y and signatures
14988895318912, 3405195891438080, 40418075143643136. Define
Y(u,v) by adding u to its row-1, label-8 entry and v to its row-2, label-8
entry (rows and labels here are one based). Every other entry remains fixed.
The replay binds Y to chart zero of the original 178-chart bank, verifies all
70 strict parent signs, 3,780 extension GP relations, the three strict primal
properness anchors at charts 3, 14, 2, and six ordered noninclusion duals.
These are the original proper incomparable extension labels, not arbitrary
normal signings. Normals use `n_I dot p = det(Y_I,p)`; signature bit 1 means
positive and bit 0 negative. Support indices below are zero based in colex
order of the 56 increasing triples, as in the source.

## Complete horizontal membership

At v=0 the maximal strict parent interval is

    L < u < H,
    L = -57869127/931628,
    H = 1094609/751872.

Let alpha be the unique root in this interval of

    996183819917173743324 u^2
    + 3195199993385149386840451 u
    + 37864449186859942661765893 = 0.

It is isolated by `-11894526/1000000 < alpha < -11894525/1000000`,
and alpha is approximately -11.89452588236. Set

    beta = 25705570474457532120686053/90789965179380319561365368
         ≈ 0.283132286962.

Here B means actual badness of a complete 56-normal block and G its strict
primal feasibility:

| Full parameter interval | Block 0 | Block 1 | Block 2 |
| --- | --- | --- | --- |
| `(L,alpha)` | G | B | B |
| `[alpha,beta]` | B | B | B |
| `(beta,H)` | B | G | B |

The replay proves this over the full indicated real intervals, including both
algebraic support-loss boundaries. Hence the horizontal triple-bad intersection
is precisely the compact connected interval `[alpha,beta]`, inside the strict
parent. This is a component of the slice; the ambient assertion is below.

For badness, alternating 4-by-4 cofactor polynomials of these five-row supports
are certified nonnegative, nonzero, and identically in the signed-normal kernel:

| Block | Support | Badness range proved |
| --- | --- | --- |
| 0 | `(9,19,21,37,38)` | `[alpha,H)` |
| 1 | `(9,16,27,30,35)` | `(L,beta]` |
| 2 | `(11,16,17,24,40)` | `(L,H)` |

At alpha the block-0 weight on index 9 vanishes. At beta the block-1 weight on
index 16 vanishes. The other four weights are strictly positive. These interior
zero-weight events are retained; neither is parent infinity.

On `(L,alpha)`, a Cramer numerator built from block-0 rows `(19,21,37,38)`
has four signed dot products equal to the boundary determinant q and all 52
others strictly positive. q is strictly decreasing with exactly one in-chamber
root; every other dot product has positive Bernstein coefficients over the
rational enclosing interval `[L,-11894525/1000000]`.

On `(beta,H)`, the recorded block-1 primal is affine in
`z=(u-beta)/(H-beta)`. Its z=0 vector is the exact kernel of rows `(9,27,30)`;
its z=1 vector is the recorded rational endpoint `P1`. All 56 signed dot products
have nonnegative Bernstein coefficients on `[0,1]`, with at least one positive
coefficient each. They are therefore strictly positive for `0<z<1`. These are
whole-block primal certificates, so no omitted positive circuit can change the
claimed G regions. The replay regenerates every polynomial from the parent.

## The component containing the interval escapes

The interval contains u=0. At u=0, let

    0 <= v < V,  V = 2037283091/10548542.

The three supports `(19,20,21,37,38)`, `(9,16,27,30,35)`, and
`(11,16,17,24,40)` have cofactor weights with **strictly positive Bernstein
coefficients throughout the closed interval `[0,V]`** and identically zero
signed-normal weighted sums. Thus all three blocks stay bad through this whole
vertical path. The 70 affine parent inequalities stay strict until v=V, where
exactly `[3578]=0`. The replay computes the full maximal vertical parent interval
and checks the endpoint, without replacing a support boundary by infinity.

This is genuine parent boundary after normalization. Labels 1 through 5 form a
fixed projective frame throughout the family, so normalizing those five rays
uses one fixed projective transformation; label 8 has nonzero fixed third and
fourth coordinates. More invariantly, the balanced bracket ratio

    R = [3578][1234] / ([1238][3457])

is unchanged by every GL(4) transformation and every independent column scaling.
At v=V its numerator vanishes while

    [1238] = 43095889251278677/10548542,
    [1234] = 2443943962,
    [3457] = 4595799854

are nonzero. On the uniform parent space R is continuous and nonzero; on any
compact subset its absolute value has a positive minimum. Along the vertical
path R tends to zero. The path therefore eventually leaves every compact
subset of the normalized parent space. No alternate chart or gauge removes
this escape. Appending the horizontal segment from any u in `[alpha,beta]` to
0 gives a proper escape within its actual triple-bad component. **Only that
component is shown noncompact.** No assertion covers other components of this
triple or other triples/parents.

## Numerical search and useful negative result

The registered initial test derived the full closed parent slice as a bounded
rational hexagon (70 affine halfspaces, all feasible line intersections, and
exact recession-ray exclusion). Its N=24 rational radial fan has 3,313 distinct
interior nodes. Floating all-56-normal LP tests gave 1,638 GBB, 1,190 BBB, and
485 BGB nodes. Two coordinate chords were sampled at 100 interior nodes each:
the horizontal gave 79 GBB / 20 BBB / 1 BGB; the vertical gave 100 BBB.
All points, margins, dual supports, and primal solver outputs are retained in
`DISCOVERY.json`; the terminal transcript is `DISCOVERY_OUTPUT.txt`.

These samples neither cover the cells between nodes nor establish polygon
connectivity, holes, or numbers of ambient components. No graph-to-topology
inference is made. Exact follow-through was restricted to the two already
sampled coordinate chords and used their existing support data; it did not
launch another support or parameter search.

This is substantively different from the prior unlabeled fixed-base
factor-source oval and failed full-height critical search: actual original
signature badness and a transverse parent-boundary path are both certified.
It is also distinct from the separately owned label-2 support-event family.
The finite negative result is that this apparent compact horizontal component
cannot be a compact ambient component. A next discriminating test would need
an actual labeled bad component with certified obstruction to transverse
parent motion; another compact coordinate slice alone would add little. No
new search or universal transverse-escape principle is proposed as proved.

## Replay, resource use, and scope

From the worktree root:

    python -B ops/team/d3-explore-topology/verify_family.py

The exact replay uses the Python standard library and imports only its local
polynomial arithmetic module. It reconstructs parent/signature admission,
full chord certificates, and genuine boundary; it does not import historical
producer acceptance logic. Four controls reject a shifted beta, a negative
vertical weight, a corrupted primal, and calling the interior origin infinity.
This is an exact producer replay, not independent acceptance.

Optional reproduction of the initial floating search:

    OPENBLAS_NUM_THREADS=1 timeout 90 python -B ops/team/d3-explore-topology/discover_slice.py

It used NumPy 2.3.5 and SciPy 1.17.0, 35.21 CPU/wall seconds and 70,416 KiB
peak RSS. The frozen exact replay used under one CPU second and about 46 MiB
RSS. Discovery stayed below 10 CPU minutes and stopped after the registered
initial test plus one exact follow-through; no census, paid service, external
write, dependency installation, ledger edit, or other surface mutation occurred.
The arithmetic candidate exploration transcript is also retained.

Classification: finite exact auxiliary family; INFORMATIONAL geometry with
unchanged theorem distance. Seven global load-bearing obligations remain open,
triple source residual remains 1,162,302, and pair/global component coverage
remains UNKNOWN. No source orbit is removed and no global `H_c^0` vanishing,
pair `H_c^1` map, middle rank, attachment theorem, or D3 promotion is claimed.
