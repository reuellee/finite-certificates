# Exact obstruction to both proposed collinearity implications

## Accepted negative scope

There is an actual uniform parent for which the selected ordinary concurrences p,q,r are distinct and noncollinear, while both remaining vertical wall gradients are nonzero and proportional. Thus both of the proposed implications are false:

* dependent vertical gradients imply collinear selected concurrences;
* dependent, individually nonzero vertical gradients imply collinear selected concurrences.

These are unrestricted counterexamples, not authenticated residual-triple counterexamples. The stronger triple has parent7 in only one distinct selected plane, 378, so the inherited light-label theorem already covers it; it also has the global rational graph proved below. Neither example establishes failure of an implication restricted to the remaining 1,162,302 source triples. Future falsification on that residue must validate survivor membership or the inherited coverage filters first.

This is an original determinant-geometry counterexample to those implications, not a formal tangent model. It is **not** a compact-component counterexample. The exhibited critical fiber is an open convex three-dimensional affine section and has an explicit path to the parent boundary. Original progress remains **2/9**, with no new numerical triple-source credit.

## Strong witness with both gradients nonzero

Use the original normalized parent

```
Y = [1 0 0 0 1  1  1  1]
    [0 1 0 0 1 -1  4  7]
    [0 0 1 0 1  2 -5 -4]
    [0 0 0 1 1  3  2  5].
```

Its 70 four-parent brackets are all nonzero. Select

| Wall | Ordinary support | Global primitive kind | Projective concurrence |
|---|---|---:|---|
| P | 123 / 145 / 246 / 356 | 48 | (1,2,2,0) |
| Q | 123 / 146 / 248 / 378 | 49 | (1,2,-4,0) |
| R | 126 / 145 / 248 / 378 | 50 | (1,-4,-4,-6) |

Each four-normal matrix has determinant zero, rank three, and every three rows independent. Every pair of the displayed points has rank two, and all three together have rank three. Their global primitive factors are distinct because they belong to different authenticated factor orbits.

The canonical ordinary49 support maps to Q under the permutation
(2,1,3,4,8,6,7,5); canonical50 maps to R under
(2,4,8,1,6,5,3,7). Both relabelings are checked directly.

For the representative p=(1/2,1,1,0), differentiate each raw four-normal determinant by moving parent j in the direction p. Both eight-height derivative rows are exactly

    (27,45,0,99,0,-18,0,-9).

They are nonzero and equal. The independent circuit-gradient reconstruction also gives two nonzero proportional vectors. All four gauge directions are annihilated. In the accepted normalized height frame, the free parent labels are 5,6,7,8; both vertical derivative rows become

    (0,-18,0,-9).

Thus this is a collision-free noncollinear point of the actual vertical critical locus with both gradients nonzero.

`verify_nonzero_noncollinear.py` reconstructs every assertion from the explicit parent and supports using only Python standard-library `Fraction`, permutation determinants, and rational row reduction. It imports no discovery or producer acceptance helper. `NONZERO_NONCOLLINEAR_REPLAY.json` records all 70 brackets, all ordinary normal matrices and circuit dependencies, both derivative calculations, and the exact relabeling checks.

## Why this witness still escapes

Fix its P contraction. A quotient map is

    v -> (v2-2v1, v3-2v1, v4).

After the three height shears, height is v3. Keep labels1,2,4 at height0 and label3 at height1. Write the remaining heights as (u,v,w,t), with base value (1,2,-5,-4). Concretely, for j=5,6,7,8 replace Y_j by

    Y_j + p (h_j-h_j(base)).

Exact determinant expansion gives

    rawP = 0,
    rawQ = (3/2)(t+2v)(2t-5w-23),
    rawR = u rawQ.

The factors u and 2t-5w-23 are parent units:

    [1245] = -u,    [1378] = 2t-5w-23.

Consequently the full triple fiber inside the original strict parent residence is exactly the affine section t+2v=0. It is a nonempty open convex set of dimension three. On that entire uniform section both vertical gradients are nonzero and proportional. This is coincidence of two distinct original factors' height sections, not individual flatness of either wall.

For an explicit escape, vary only parent5:

    (u,v,w,t)=(1+tau,2,-5,-4),
    -4/23 < tau < 2/5.

All three selected concurrences remain fixed and noncollinear. This is the maximal parent-sign residence along the line. Its endpoints are [1578]=0 and [1358]=0. Thus the displayed critical point has a path to the original parent boundary while preserving all three walls and avoiding selected concurrence collisions.

`verify_coincident_height_fiber.py` checks these polynomial identities, parent-unit identifications, fixed concurrence kernels, and exact interval bounds. Its output is `COINCIDENT_HEIGHT_FIBER.json`. This finite fiber calculation does not assert global vanishing for a locus of coincident height sections.

## Specific global rational-graph escape

The stronger support triple also has a global escape proof, independently checked by `verify_global_graph.py` and `GLOBAL_GRAPH_INDEPENDENT.json`. The frozen producer proof `../noncollinear/escape_global_graph.md`, SHA256 `18ad54664a496d827c9120cbc9f8c73b961135a9ac93f439f37d7dfa3c89d5f6`, was read and accepted. In the standard original nine-coordinate parent frame its three raw determinant polynomials are exactly

    P=a+bc-b-c,
    Q=-afh+ahi-bdi+bfg,
    R=-bdi+bfg-bfh+bhi+cdh-cgh.

Put D=bd-bf(b-1)-ah and G=bg-bi(b-1)-ah. Direct polynomial expansion gives

    Q=fG-iD,
    b(R-Q)=ch(D-G)+bh(f-i)P.

All four required units are original parent brackets:

    b=-[1246], c=[1236], h=-[1248], f-i=-[2378].

Therefore P=Q=R=0 is equivalent, on every uniform parent sign residence, to P=D=G=0. It is the rational graph

    a=b+c-bc,
    d=f(b-1)+(b+c-bc)h/b,
    g=i(b-1)+(b+c-bc)h/b

over the six coordinates (b,c,e,f,h,i). The inverse is coordinate projection. Pulling the original strict parent signs and any normalized parent component back along this graph gives an open subset of affine six-space. Its connected components are open and cannot be compact. Fixed frame/reorientation sign sectors preserve these zero loci and the nonzero-unit identities; no parent component or denominator-zero boundary has been discarded beyond original uniformity.

Thus every component of this specific support triple, and every relabeling of it, is noncompact. This is an independently accepted deductive theorem for the specific triple, with no numerical new-coverage credit. It is already consistent with inherited light-label coverage.

## General closed proportional-height excision audit

The theorem `../noncollinear/escape_redundant_height.md`, SHA256 `13fe6f21ab42e3a36a0cfef2a9a529177b1b5425175de9fa2851feb8a99088c3`, was read and accepted independently. Fix parent-unit products U,V with the required coordinate weights. The base locus where U R=V Q as an identity in all four heights is closed, since it is defined by finitely many coefficient equations. Over that locus the full triple fiber equals the entire P/Q fiber, not a chosen factor branch.

For q different from p, retaining the projected q and its private height gives at most four affine equations in five height variables, hence full nonempty fibers are positive-dimensional open convex sets. For q=p the whole four-height cell persists. The closed/open argument gives Hc0=0 for the full closed proportional piece; finite closed unions have the same vanishing. The theorem does not assume a smooth or open coefficient-zero base. Its explicit saturation warning is necessary: a generic gcd or a proper subbranch need not retain the full concurrence fiber.

This validates the general lemma and its application to the explicitly checked witness height fiber. The producer's separate classification of the entire projected critical stratum for this support triple was not independently audited in this track. No claim is made that finitely many such proportional pieces exhaust the authenticated residual critical locus.

## Final bounded directional-gradient pencil test

The coordinator requested one final test of the collinear pencil criterion for the same already-covered Q49/R50 pair, then stopped further covered-parent search. With raw directional maps C_Q,C_R from R4 to R8, each has rank three. Exact reconstruction gives

    C_Q(r)=(-72,72,-144,-216,0,72,0,0),
    C_R(q)=(72,216,0,-72,-144,72,0,0).

They are not proportional. The 24-by-8 rational coefficient system for

    (C_Q-z C_R)(v0+z v1)=0

has rank eight, so there is no nonzero polynomial kernel of degree at most one. At the actual witness parameter z=1, C_Q-C_R has rank three and contains p in its kernel. The noncollinear critical example therefore does not challenge the separate collinear pencil gate.

`verify_gradient_pencil.py` builds all directional derivatives from original determinants without the prover's helpers and writes `GRADIENT_PENCIL_REPLAY.json`. The gate's scaling convention is raw ordinary determinants. Independently scaling either equation rescales the pencil parameter and does not change existence of the required linear kernel.

The algebraic lemma in `../proof/LINEAR_GRADIENT_PENCIL_GATE.md`, SHA256 `74bfe5ff1de09803101ab13d6613c97450521db552b21684da240cda9bc9bc17`, is sound under its explicit point-kernel input: when p=a q+b r with a,b nonzero, C_Q(p)=b C_Q(r) and C_R(p)=a C_R(q). If C_R(q)=c C_Q(r), then (C_Q-z C_R)(q+c z r)=0; expanding the latter identity gives the converse. This is not a structural exclusion of such pairs, and the test here is not on an authenticated survivor triple.

## Earlier independently verified flat-wall witness

The alternative track first supplied a weaker example at the same parent:

    P48=123/145/246/356,
    Q36=125/126/356/378,
    R49=123/145/257/348.

Its three concurrences are (1/2,1,1,0), (1/2,1,0,0), and (1/7,1,1,0), hence are distinct and noncollinear. The Q vertical gradient is zero; the R gradient is nonzero. The independent point replay is `verify_noncollinear_independent.py` and `NONCOLLINEAR_INDEPENDENT_REPLAY.json`.

For the same four-height chart, rawP=rawQ=0 identically and

    rawR=(5/2)u(t-2u+w+11).

This gives another open convex three-dimensional fiber. Varying only parent6 yields the exact collision-free escape interval

    (u,v,w,t)=(1,2+tau,-5,-4),
    -1/3 < tau < 8/11,

with endpoints [1467]=0 and [4568]=0. This is checked by
`verify_flat_height_fiber.py` and `FLAT_HEIGHT_FIBER.json`.

The later both-nonzero example is strictly stronger as a refutation of the proposed rank implication. Neither example refutes global triple noncompactness.

## Bounded discovery and discarded deformation route

Before the actual witness was supplied, this track reconstructed 24 selected one-parameter determinant families under the actual P50 projected deformation (2,3,4,s): 22 restrictions remained quadratic, and two were cubic. `deform_quadratics.py` and `DEFORMED_QUADRATICS.json` preserve those exact inputs.

The mixed pair Q=125/136/248/378 and R=135/237/456/678 was checked at seven discriminant-selected rational parameter values: 2,-9/8,3,9,-3,3/5,-9/5. Eliminating y via the Q equation is valid because [1248]=-w is a parent unit. At a critical common zero, the discriminant in z of the remaining quadratic-in-z polynomial and its x,w derivatives must all vanish, including where its z-leading coefficient vanishes. Exact Groebner bases put w^6 in that ideal in all seven cases, excluding uniform critical points there. This bounded null result is recorded in `cubic13_target.py` and `CUBIC13_TARGET_NULL.json`; no claim is made at other s values.

A different cubic, R=146/235/367/458, produced two noncollinear critical points at s=2 and s=-9/8. Both violate [1346]=[3458]=0. `verify_deformation_boundary.py` and `DEFORMATION_BOUNDARY_CANARIES.json` explicitly reject them as original-parent examples. A generic symbolic Groebner exploration was interrupted without a conclusion; no unspecialized claim or artifact is used.

After the first valid flat-wall witness, the coordinator authorized one targeted repair test at that same authenticated nongeneric parent. `nonzero_gamma_search.py` constructs candidate concurrence clusters from the 56 actual parent normals, then selects at most64 ordinary high-family wall occurrences. It found the strong witness after47 checks. No global triple census was rebuilt. `NONZERO_GAMMA_SEARCH.json` records the complete selected list and matching nonzero gradient directions. The separate Fraction replay, rather than the discovery classification alone, validates the accepted witness.

## Inputs, replay, and next target

The authenticated input is commit `52b4a0efdad0c1bf05503f4126b2c6f5dc78c246`, tree `7222302d8ae3ee4e899709309104c5e098cb9363`, under `../checkpoint/` relative to this owned directory. The work order and exact input hashes are recorded in `HANDOFF.json`.

The accepted coordinate/circuit inputs are `../checkpoint/referee/ANCHOR_COVERAGE_AUDIT.md` (SHA256 `e067b7f27de4c70877258a8094ad4003edc71713323d778323f52eb03bb9efe9`) and `../checkpoint/proof/VERTICAL_CRITICAL_REDUCTION.md` (SHA256 `e7034f7b3b51fad14e925eeabed3a43cf134e72a1a3689fede5b4ac28b69477e`). The earlier alternative witness was independently checked against its frozen JSON SHA256 `54ce3f8b0206e47a43475506d5ec684e42d2da189348a4a170b2952814400041`.

The main strong result can be replayed from the cycle root with:

```
python falsifier/verify_nonzero_noncollinear.py
python falsifier/verify_coincident_height_fiber.py
```

The first requires only Python; the second uses SymPy. Both use exact arithmetic. The weaker example has the analogous two scripts listed above. Discovery and deformation files are not needed to accept the strong witness.

A viable continuation on the authenticated residue must justify its source scope before using either a noncollinear reduction or a pencil condition. Removing individually flat walls is insufficient: the strong witness has two nonflat but coincident height sections. One useful next discriminator is whether every remaining critical component, after justified removal of full height-flat and height-coincidence pieces, has an actual source-preserving escape. The fixed-parent-unit proportional-piece removal theorem above is accepted; no exhaustion theorem or remaining critical-locus vanishing is claimed here.
