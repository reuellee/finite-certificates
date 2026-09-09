# Independent adversarial audit: source existence does not close D3

Status: **frozen producer handoff; not an acceptance or ledger update**.
Role: adversarial topologist. Base: `fcb64825335245e6e53512bf4eb2c5f5279b75ae`.
Owned surface: `ops/team/ai-d3-reset-falsifier`.

## 1. Results and their precise scope

1. No mathematical counterexample to the five-clause source theorem was found.
   Its compactification, finite triangulation, and literal inclusion claims
   survive the tests below. The omitted residual diagonal in the frame argument
   and the identification of the filtered differential need explicit arguments;
   Sections 2 and 3 supply them. They are proof details, not evidence of falsehood.
2. Source existence, including an integral cover-compatible finite relative
   source, **does not imply D3 even after imposing all the stated singleton
   `H_c^{0,1,2}` and pair `H_c^0` vanishings**. Sections 4 and 5 give three
   exact generic countermodels. Their bad loci are coordinate sections of one
   contractible nine-dimensional open cube. All use one common unsigned
   polynomial `56 x 4` matrix with row signs depending on the signature.
3. The two D3 invariants remain independent under these hypotheses. One model
   fails both; one has no compact triple component but a rank-two pair kernel;
   one has zero pair kernel but one compact triple component.
4. These are **not actual-parent counterexamples**. They do not come from the
   third compound of eight uniform parent columns, and no valid parent-extension
   signatures are supplied. A particularly simple violated parent condition is
   that distinct actual derived normals cannot be proportional; the generic
   matrix has proportional rows. This explicit scope boundary prevents promoting
   the examples to a refutation of 9DVL or concluding that only a deep Koszul
   identity, rather than some weaker parent condition, could exclude them.

The lane's trajectory is `INFORMATIONAL`, with theorem-ledger delta zero.
The exact generic implication is retired. No actual-parent obligation is closed.

## 2. Frame, labels, and boundary: adversarial reconstruction

### 2.1 The frame works, but needs its residual diagonal

Represent a realization by columns `Y=(y_1,...,y_8)`. Fix a chirotope
representative with `chi(1234)=+1`, and use matching extension-sign conventions.
Let

```text
B = (y_1,y_2,y_3,y_4),   v = B^(-1)y_5,
D = diag(1/|v_1|,...,1/|v_4|),   G = D B^(-1).
```

Uniformity makes `det B` and every `v_i` nonzero. The signs of `v_i` are
fixed by the parent brackets. Apply `G`, positively rescale the first four
columns to `e_i`, leave the fifth at `s=(sign v_i)`, and positively rescale
each of the last three columns so the sum of its absolute coordinates is one.
All denominators are positive and continuous throughout every component.

This corrects the draft's compressed wording: after sending the first four
columns to coordinate rays, a scalar rescaling of column 5 alone cannot adjust
its four coordinate magnitudes. The residual **positive diagonal projective
transformation**, followed by positive rescaling of the basis columns, does so.
For example `(1,2,3,4)` cannot become `(1,1,1,1)` by one positive scalar;
this is a counterexample to that literal intermediate sentence, not to the
normalization theorem.

For uniqueness, a linear transformation preserving the four oriented coordinate
rays is positive diagonal. If it also preserves the oriented ray of `s`, whose
four entries are nonzero, it is scalar. The three final norm conditions then
fix the remaining column scales. Consequently this is one semialgebraic
continuous section of the projective/positive-column quotient, with continuous
inverse from its image. It does not choose one component. It includes every
component and gives a homeomorphism of the entire quotient with the indicated
strict sign locus in three fixed open orthants.

If the supplied chirotope representative has negative `chi(1234)`, globally
negate the parent and extension chirotope representatives together before using
these formulas (or use the equivalent signed basis convention). The associated
signature transport must be stated. A silent change of the parent representative
while keeping the meaning of the extension signs undefined is a labeling gap.
It is repairable by this fixed convention and is not a missing realization.

### 2.2 Normal and witness transport is explicit

Use the convention
`a_I(Y)p = det(y_i,y_j,y_k,p)` for an ordered triple `I=(i,j,k)`.
If `y'_l=c_l G y_l` with all `c_l>0` and `det G>0`, then

```text
a_I(Y') = d_I a_I(Y) G^(-1),
d_I = det(G) product_(l in I) c_l > 0.
```

The signed matrices therefore obey `A_sigma(Y')=D_rows A_sigma(Y)G^(-1)`.
For the globally normalized joined weights the exact transport is

```text
w'_(sigma,I) = (w_(sigma,I)/d_I) / sum_(tau,J)(w_(tau,J)/d_J).
```

It preserves all witness-coordinate zero faces, every positive block support,
and literal zero-padding maps for every `R subset R'`. Its inverse uses `d_I`.
It is a semialgebraic homeomorphism and hence preserves compact supports. The
block-mass filtration in the pinned audit is the **number of positive blocks**,
which this map preserves. No claim that numerical masses are unchanged is
needed. If required, mass itself can also be preserved by normalizing separately
within each positive block and retaining its original total mass; extend by zero
at a zero block. This extension is continuous since its norm is the block mass.

The determinant convention fixes the corresponding sign transport under an
orientation-reversing change. Residual loci and rank labels must be pulled back
as labeled sets, not identified merely because two formulas have similar names.
A finite relative source for the newly normalized geometry does not automatically
certify a numerical matrix previously built in a different atlas.

### 2.3 The closure and the relative boundary survive

After normalization `X_M` is a strict polynomial-sign locus inside the product
of three simplex interiors. It is relatively open there. In its compact closure,
a point with every simplex coordinate and parent bracket nonzero has the same
prescribed signs as nearby points of `X_M`, so belongs to `X_M`. Thus
`I_M=Xbar_M\X_M` is closed and consists of parent degeneration points. This
argument applies simultaneously to all components; it does not assume that the
weak inequalities define the closure.

A residual factor or witness-rank wall at which all parent data stay nonzero
is interior to `X_M`. It must not be put into `I_M` merely because a chosen local
description ends there. The exact closure in the candidate avoids that error.

For each `R`, the extended equations define a compact closed semialgebraic
`Gammabar_R`. Their restriction over `X_M` is exactly `Gamma_R`, since the same
polynomial matrices are used. Additional fibers over `I_M` need not be limits
of interior witnesses. They lie entirely in the relative subspace, so do not
invalidate the relative-pair calculation. The total compactification is not
required to equal the topological closure of `Gamma_R`.

Zero-padding satisfies every added homogeneous block equation, preserves total
mass one, and preserves whether the base point lies in `I_M`. It is a closed
embedding of compact pairs. After compatible triangulation the relative
cohomology of each compact pair is compactly supported cohomology of its open
complement. This uses a triangulated compact pair, not an arbitrary pathological
compact pair. Arbitrarily collapsing or deleting internal residual walls would
break the premise; no such deletion is present in the candidate.

## 3. Triangulation, naturality, and the filtered comparison

### 3.1 Finite triangulation is a mathematical existence claim

Fix the finite lists of parent/signature labels, coordinate supports, residual
sets, and declared rank conditions. All minors of any of these fixed finite
matrices form a finite list. Their sign/zero loci, the finitely many zero-padded
subsources, and the three levels of the support filtration form a finite
semialgebraic family. One can add the finitely many relevant closures and take
a finite Boolean refinement before triangulation. No infinite set of arbitrary
real mass thresholds is intended by the pinned block-mass filtration.

The exact compatible-triangulation statement is supported by
[Shiota, *Whitney triangulations of semialgebraic sets* (2005)](https://impan.pl/en/publishing-house/journals-and-series/annales-polonici-mathematici/all/87/0/84789/whitney-triangulations-of-semialgebraic-sets).
For a compact ambient, a closed subset that is a union of open simplices is
already a subcomplex: every face of any included simplex lies in its closure.
Choose an orientation for each simplex; no global manifold orientation of the
singular Gordan space is asserted or necessary.

Thus there is no triangulation counterexample here. A finite exact label/rank
dictionary must still be specified before anyone claims that a particular
implementation preserves every datum of a particular old complex. The draft's
algorithmic claim allows exact compatible semialgebraic triangulation as an
operation and asserts no bound. Lack of an installed triangulator or huge size
does not refute that mathematical claim.

### 3.2 Objectwise contractibility is not the whole filtered proof

The joined projection `p_R:Gamma_R -> B_R` is proper with nonempty compact
convex fibers. The constant-sheaf unit is a quasi-isomorphism by stalkwise proper
base change; see [Stacks Project, tag 09V4](https://stacks.math.columbia.edu/tag/09V4).
It yields an isomorphism with compact supports. The zero-padding squares commute,
so their induced proper pullbacks commute with the units. One need not falsely
claim those squares are Cartesian: in general `Gamma_R` is a face of, rather
than the entire inverse image inside, `Gamma_R'` over `B_R`.

To identify the **filtered** differential explicitly, insert the mass-only
resolution, for `S={0,1,2}`:

```text
Z_S = {(Y,t) in X_M x Delta^2 : t_i > 0 implies Y in B_i},
q: Gamma_S -> Z_S,   t_i = sum_I w_(i,I).
```

`Z_S` is closed relative to `X_M x Delta^2`: each forbidden condition is
`Y outside B_i` and `t_i>0`, which is open. The map `q` is proper. At a point
with positive support `T`, its fiber is the product of the normalized nonempty
Gordan polytopes `P_i(Y)` for `i in T`, hence compact and contractible.

Both spaces have the closed filtration by at most `r` positive masses, and
`q^(-1)F_r Z_S=F_r Gamma_S`. Proper base change on the filtration levels and
their open differences identifies their exact triangles. Consequently it
identifies the spectral sequences, including their differentials, rather than
just their final cohomology groups.

`Z_S` is the usual finite closed-cover realization: it is assembled from
`I_T x Delta_T`, where `I_T=intersection_(i in T) B_i`, and the face attachments
are the literal inclusions `I_T -> I_(T\{i})` times simplex faces. Orient
`Delta_T` by the inherited order of its vertices. Its compact-support filtered
complex is therefore the closed-cover Mayer--Vietoris complex, with

```text
E_1^(p,q) = direct_sum_(|T|=p+1) H_c^q(I_T; Z)
d_1       = alternating restriction,
total degree = p+q.
```

This also follows from the augmented constant-sheaf Cech resolution: its stalk
at `Y` is the augmented simplex cochain complex on the nonempty set of bad
signatures at `Y`, and hence exact. The product with each oriented open mass
simplex gives precisely the degree shift `|T|-1`.

For the finite triangulated source, use relative **cochains** (or dualize the
integer cellular boundary matrices); a relative homology chain complex alone
must not be confused with compact-support cohomology. These observations repair
the short argument for clause 5. They do not prove that any previously saved
integer boundary matrix is that complex without its own comparison map.

### 3.3 Exactly what follows for D3

Assume the accepted lower vanishings for this paragraph. In total degree two,
the singleton term is zero. The pair term surviving to infinity is

```text
ker[H_c^1(I_01) + H_c^1(I_02) + H_c^1(I_12)
      --(res_01 - res_02 + res_12)--> H_c^1(I_012)].
```

The triple `H_c^0(I_012)` has no incoming `d_1`, because pair `H_c^0=0`,
and no incoming `d_2`, because singleton `H_c^1=0`. It has no outgoing
differential. There are no higher possible columns. These are exactly the two
associated-graded contributions to `H_c^2(B_0 union B_1 union B_2)`.
Thus both must vanish, separately, for D3. Finite relative source existence
merely makes the groups and maps accessible in principle; it gives no rank or
noncompactness conclusion. Individual injectivity of three restrictions is
also insufficient for injectivity of their alternating direct sum.

## 4. An exact shared-normal realization of the generic bad loci

Let `X=(-1,1)^9`. For a nonempty proper coordinate set `F_i subset [9]`, define

```text
B_i = {x in X : x_j=0 for j outside F_i},
g_i(x) = sum_(j outside F_i) x_j^2.
```

Then `B_i = {g_i=0}` is closed in `X` and is homeomorphic to `R^(|F_i|)`.
Every intersection is the corresponding coordinate section for the intersection
of the sets `F_i`. The empty set of free coordinates gives the single point 0,
not the empty topological space.

Use standard row basis vectors `e_1,...,e_4`. One common unsigned matrix has
rows

```text
a_(2j+1) =  e_(j+1) + g_j e_4,
a_(2j+2) = -e_(j+1) + g_j e_4,        j=0,1,2,
a_7 = ... = a_56 = e_4.
```

Every row is nonzero. The minor on rows `1,3,5,7` is identically one, so the
row span is always four. Signature `sigma_i` gives both rows of module `i`
positive signs. In each other module it gives the first row a positive sign
and the second a negative sign. It gives all rows `7,...,56` positive signs.
Thus **all three signed systems differ only by row reorientation of one matrix**.

If `g_i>0`, take `p_4=1`, `p_(i+1)=0`, and `p_(j+1)=g_j+1` for `j!=i`.
The two target slacks are `g_i`; the other module slacks are `2g_j+1` and `1`;
the remaining slacks are `1`. All are positive. If `g_i=0`, the target rows
require both `p_(i+1)>0` and `-p_(i+1)>0`. Hence infeasibility is **exactly**
`B_i`. No sampling or numerical optimization enters this conclusion.

The normalized nonnegative kernel is equally exact. In each non-target
coordinate its equation is the sum of that module's two nonnegative weights,
so both weights vanish. The target coordinate equates its two weights. The
fourth coordinate then says
`g_i(w_(2i+1)+w_(2i+2)) + sum_(r=7)^56 w_r = 0`.
On `B_i` all tail weights vanish, and total mass one forces the target weights
to be `1/2,1/2`. Off `B_i` there is no normalized solution. In a joined source,
each block is a nonnegative multiple of this same witness whenever it exists.

All signatures are feasible somewhere and bad somewhere. In each model below,
`F_i\F_j` and `F_j\F_i` are nonempty; a point with just one of those coordinates
equal to `1/2` witnesses each direction of incomparability of the bad loci and
therefore of their open feasibility complements. These generic signatures have
proper pairwise-incomparable feasibility regions.

Take `Xbar=[-1,1]^9` and `I=Xbar\X`. The identical polynomial construction
extends to this compact cube. In fact the compact joined source is the finite
union of products `Bbar_T x Delta_T`, embedded by putting mass `t_i/2` on the
two target coordinates of each block. It is a finite polyhedral object, with
literal zero-padding, labeled zero faces, true relative boundary over `I`,
and the exact mass-support filtration. Compatible finite triangulation exists
directly. Any extra finite declared semialgebraic rank/sign family can also be
included. Thus the generic analogues of **all five source conclusions** hold;
the examples do not exploit a missing source or an omitted map.

## 5. Three independent exact topological calculations

All groups here are integral. An open `d`-cube has compact-support cohomology
`Z` in degree `d` and zero in every other degree; a point has `H_c^0=Z`.

| Model | `F_0`; `F_1`; `F_2` | Singleton dimensions | Pair dimensions | Triple dimension | Pair kernel | Triple `H_c^0` | Union `H_c^2` |
|---|---|---|---|---|---|---|---|
| Both fail | `124`; `135`; `236` | `3,3,3` | `1,1,1` | `0` | `Z^3` | `Z` | `Z^4` |
| Pair only | `123`; `145`; `167` | `3,3,3` | `1,1,1` | `1` | `Z^2` | `0` | `Z^2` |
| Triple only | `1234`; `1256`; `3456` | `4,4,4` | `2,2,2` | `0` | `0` | `Z` | `Z` |

In every row the singleton groups in degrees zero, one, and two vanish, and
each pair `H_c^0` vanishes. Each base is the same contractible open nine-cube.

In the first model, pair intersections are three different open axes and the
triple is the origin. The pair-to-triple `H_c^1` target is zero, giving kernel
`Z^3`; the surviving triple group is `Z`. Their extension in total degree two
splits as an abstract group because the quotient is free, giving `Z^4`.

In the second model all pair and triple intersections are literally the same
oriented open first axis. Each individual restriction is the identity on `Z`.
The alternating map is `[1,-1,1]:Z^3 -> Z`, which is surjective and has kernel
`Z^2`. The triple has no compact component. This example specifically refutes
the claim that three individually injective pair restrictions suffice.

In the third model the pair intersections are open two-cubes, so pair `H_c^1`
is zero. The triple is the origin. The sole total-degree-two contribution is
its `Z`; no rank argument involving the pair map can remove it.

### Separate finite chain verification

`verify_countermodels.py` does not merely reproduce the spectral-sequence rank
formula. It constructs the relative cubical chain complex of the **bad-locus
union itself**, using the closed coordinate cubes in `[-1,1]^9` and their
boundary over `I`. Split each free interval at zero. After passing to the
relative complex, a remaining coordinate is either the point zero, the open
negative half-interval, or the open positive half-interval. The boundary of the
negative half-interval contributes `+[0]`; that of the positive contributes
`-[0]`. Orient products by increasing coordinate order.

The exact cell counts and integer boundary ranks over `Q` are:

| Model | Cell counts `C_0,C_1,...` | Ranks `d_0,d_1,...` | Relative Betti numbers |
|---|---|---|---|
| Both fail | `1,12,36,24` | `0,1,11,21` | `0,0,4,3` |
| Pair only | `1,14,36,24` | `0,1,13,21` | `0,0,2,3` |
| Triple only | `1,12,60,96,48` | `0,1,11,48,45` | `0,0,1,3,3` |

The checker constructs these matrices from the coordinate sets, verifies
`d^2=0` coefficient by coefficient, and computes ranks by rational elimination.
It separately checks each of the seven nonempty intersections in every model,
the signed feasibility identities as symbolic polynomials, the constant
rank-four minor, and the nonnegative-kernel elimination coefficients.
It does not compute Smith normal forms. The integral statements in the table
come from the written open-cube and Mayer--Vietoris argument; the independent
matrix calculation verifies their rational consequences, which suffice for D3.

The largest union complex has 217 relative cells. This is a fixed exact
certificate, not an enumeration of parent classes, signatures, or components.

## 6. Scope fence, validation, and research consequence

For an actual uniform rank-four parent, two different triples cannot have
proportional derived normals. Otherwise their three-dimensional spans would
coincide; their union contains at least four parent columns, contradicting
uniformity. The generic matrix already violates this condition in its repeated
tail rows, and each target pair becomes opposite on its bad locus. Therefore
there is an explicit obstruction to interpreting these matrices as actual
parent normals. Merely assigning their rows the 56 triple names changes nothing.

The examples establish a separation theorem for the **formal consequences** of
the source theorem plus lower vanishings. They neither refute its stated
actual-parent theorem nor prove any actual-parent D3 failure. They also do not
show that the full third-compound identity is the minimal needed hypothesis.
Any next actual-parent argument must add a verified condition not present in
the generic abstraction, and show how that condition controls an actual
noncompactness or restriction-map statement. Counting further generic cells
cannot repair this implication.

Validation command, from the assigned worktree:

```text
python ops/team/ai-d3-reset-falsifier/verify_countermodels.py
```

The saved `VALIDATION.json` reports `PASS`, exact arithmetic, and approximately
0.17 seconds for the verification run. No computer algebra library is required.
`SOURCE_PINS.json` records SHA-256 hashes of the local inputs, matches all read
pins from the opening manifest, and lists the two primary literature pages
checked during this audit. Neither another discovery lane nor coordinator
discoveries were inspected. No actual-parent search, global triangulation,
external compute, human contact, push, merge, or canonical edit was performed.

Opening, midpoint, and closing proof-distance vectors are unchanged for this
lane:

```text
(2/9, 1, {diag3_pair_hc1,diag3_triple_hc0}, 7,
 UNKNOWN, UNKNOWN, 9, 12).
```

The lane does not increment cycle-wide streak counters; that is a coordinator
closing decision. The first exact separation was reported at the preliminary
checkpoint; the subsequent frozen models and independent cubical verification
refine its scope without changing the ledger or actual-parent coverage.

Decision: `RETIRE` the implication “compact relative source plus accepted lower
vanishings suffices for D3” in the generic shared-normal setting. This is not
retirement of 9DVL or of the source theorem. No same-route continuation is
justified by this handoff. A parent-specific successor requires a separately
preregistered statement and an independent acceptance decision.
