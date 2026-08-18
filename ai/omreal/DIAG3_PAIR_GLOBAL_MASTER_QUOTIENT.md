# Diagonal three: the global pair complex from one labelled master subdivision

## Outcome

The receiver/root atlas is not an invariantly necessary intermediate object.
There is a smaller exact global endpoint.

Let a finite regular subdivision of a compactification of one normalized
parent cell be subordinate to

* parent infinity;
* all primitive residual walls and their intersections; and
* the bad loci of all valid extension signatures.

Label every cell by the signatures which are bad on it.  One such labelled
**master subdivision** determines, for every ordered signature triple, the
closed triple complex, the three exclusive-pair complexes, all frontier
blocks, and the balanced matrices

\[
                    C^0\mathop{\longrightarrow}^{N}C^1
                       \mathop{\longrightarrow}^{M}C^2.       \tag{1}
\]

No receiver assignment, elementary-root choice, ordered-root sector, or
Gordan-occurrence choice is needed in (1).  The proper block-Gordan
projection has compact contractible fibers and is functorial under adding or
zeroing signature blocks, so Gordan witness/support choices may be quotiented
**before** the pair differential is formed.  Root and receiver motions are
not fibers of that proper projection; the master route bypasses them by
computing the labelled base complex directly.

There is also no independent integral-lift search after the master closure
poset is known.  Barycentrically subdivide it, orient every simplex by its
face-chain order, and use ordinary signed simplicial incidence.  The
frontier identities and

\[
                              MN=0\quad\hbox{over }\mathbb Z   \tag{2}
\]

then hold formally.  Thus the `integral signed global lift` flag in
`DIAG3_PAIR_GLOBAL_ATLAS_SCHEMA.md` is automatic once an actual
closure-complete regular master complex and its relative infinity subcomplex
have been certified.  It is not satisfied by the current point bank, because
that bank is not such a complex.

This reduction removes the schema's `850,442` receiver-colored ray-frontier
requests, `3,025,948` receiver-colored sector-frontier requests, and
`450,059,243,270` unselected stored-chart pair requests as **separate
geometric coverage tasks**.  Their information is replaced by one master
closure poset with a signature-membership column on every cell.  Constructing
that global poset, including parent infinity, is still open.

The exact extractor and two covered local regressions are
`verify_diag3_pair_global_master_quotient.py`.

## 1. Why the base quotient is exact

For a signature `rho`, let

\[
 P_\rho(Y)=\{\lambda\geq0:\mathbf1^T\lambda=1,
                 A_\rho(Y)^T\lambda=0\}.
\]

The normalized Gordan resolution of a bad intersection is

\[
 \widehat\Gamma_I=\{(Y,(\lambda_\rho)_{\rho\in I}):
                   \lambda_\rho\in P_\rho(Y)\}
       \longrightarrow \bigcap_{\rho\in I}B_\rho.              \tag{3}
\]

Its fiber is a product of nonempty compact convex polytopes.  The map is
proper, and proper base change identifies its derived compact-support
complex with that of the bad intersection.  Zero-padding witness blocks
makes these equivalences functorial in `I`.  Consequently the alternating
restriction map among pair and triple intersections is computed directly on
the base bad loci.  A carrier atlas is one way to construct a contraction of
that base complex, but it is not extra topological data which must remain in
the final certificate.

This quotient is stronger than deleting a selected witness vertex or
occurrence from each sampled graph: it deletes the entire compact convex
witness-choice fiber functorially.  The separate master-cell computation is
unaffected by a tree edge disappearing, a root switch, or a different
receiver motion because it never introduces those motion choices.  Their
geometric effect matters only insofar as it changes the bad-signature label
or closure incidence of a base master cell.

The special third-compound geometry has not disappeared.  It is what makes
the cell labels and their residual-wall attachments computable.  The shared-
normal graph countermodel in `REVIEW_DIAG3_ADVERSARIAL_THEOREM_AUDIT.md`
still applies: arbitrary labelled complexes need not be middle-exact.  The
quotient says where the global incidence must be computed, not what its rank
will be.

## 2. Master cells and exact signature labels

On an open residual sign chamber, the oriented matroid of the 56 derived
normals is constant.  A signature is feasible precisely when it is a tope of
that arrangement, so one exact tope set labels every chamber at once.  The
all-strata gluing theorem gives the interior lower-cell rule:

\[
 \operatorname{Feas}(\tau)
   =\bigcap_{\substack{C\text{ chamber}\\\tau\subset\overline C}}
                  \operatorname{Feas}(C).                        \tag{4}
\]

Equivalently, a closed bad locus contains a lower cell when at least one
incident chamber is bad.  A semialgebraic triangulation subordinate to all
bad loci and parent infinity always exists.  For a machine certificate,
however, existence is not coverage: the source cell universe, closure map,
labels, and infinity subcomplex must be generated and checked exactly.

For one fixed finite master complex, signatures having the same bad-cell
membership column are indistinguishable in the pair calculation.  Define

\[
 \rho\sim\eta
 \quad\Longleftrightarrow\quad
 \{\tau:\tau\subset B_\rho\}
   =\{\tau:\tau\subset B_\eta\}.                              \tag{5}
\]

Every ordered triple of signatures factors through the triple of equivalence
classes in (5).  Thus the final rank replay needs one matrix per membership-
profile triple, with a source-accounting map from every signature.  It does
not need one geometric atlas per signature pair.  The quotient can be
trivial on a sufficiently rich global complex, but it is always exact and
must be measured rather than assumed.

## 3. Canonical signed lift

Let `K` be the barycentric subdivision of the certified regular master
complex and let `K_infinity` be the subdivision of its relative boundary.
For three signatures put

\[
 T=B_0\cap B_1\cap B_2,
 \qquad A_{ij}=B_i\cap B_j,
 \qquad E_{ij}=A_{ij}\setminus T.                              \tag{6}
\]

The `B_i`, `A_ij`, and `T` are subcomplexes.  Compact-support cochains of an
exclusive stratum are the relative simplicial cochains

\[
 C_c^*(E_{ij};\mathbb Z)
   =C^*\bigl(\overline{A_{ij}},
             T\cup(\overline{A_{ij}}\cap K_\infty);\mathbb Z\bigr).
                                                                    \tag{7}
\]

Order the vertices of each barycentric simplex by the dimensions of the
cells in its strict face chain.  If `tau` is obtained by deleting vertex
`r` from `sigma`, its incidence is `(-1)^r`.  In the cell order
`E_ij,T`, the coboundary of `A_ij` has the block form

\[
 d_{A_{ij}}=
 \begin{pmatrix}d_{ij}&b_{ij}\\0&d_T\end{pmatrix}.              \tag{8}
\]

Ordinary simplicial cancellation of twice-deleted vertices gives
`d_A^2=0`, hence

\[
 d_{ij}^2=d_T^2=0,
 \qquad d_{ij}b_{ij}+b_{ij}d_T=0.                              \tag{9}
\]

Insert these blocks into formulas (22)--(23) of
`DIAG3_PAIR_DIFFERENTIAL_ENDS.md`.  Equation (9) gives (2) entry by entry.
This construction works for a nonorientable master space as well: individual
simplices are oriented canonically, and no global manifold orientation is
used.

Therefore an unsigned mod-two master incidence table has a proved integral
lift whenever it comes from a certified regular closure poset.  Storing only
arbitrary parity matrices is still invalid.  The regular-poset and
subcomplex checks are precisely the lift hypothesis.

Once (2) holds, the sufficient rational completion test remains

```text
rank_F2(N) + rank_F2(M) = dim_F2(C1).
```

Rational matrix ranks are at least their mod-two ranks, while (2) bounds
their sum by `dim C1`, forcing rational middle exactness.

Only the two-skeleton of the barycentric subdivision is needed.  Its
vertices are original master cells, its edges are comparable cell pairs,
and its triangles are strict closure chains

\[
                         \tau_0<\tau_1<\tau_2.                 \tag{10}
\]

The matrices `N,M` use no simplex of dimension three or higher.  Moreover a
barycentric simplex belongs to a bad subcomplex exactly when its largest
cell does, because bad loci are closed subcomplexes.  Thus a final
certificate can store the labelled closure poset, its comparable pairs and
strict three-chains, rather than materializing a full high-dimensional
barycentric triangulation.  Equation (9) is checked on each three-chain by
the two opposite deletion orders.

## 4. Covered transverse-node falsification

The exact row-2599 transverse node has four chambers.  Replace its closed
disk by a four-triangle fan and put the outer cycle in the relative
subcomplex.  Its exact signature profile census is

| feasible chamber mask | signatures |
|---:|---:|
| `0000` | `70,968` |
| `0011` | `72` |
| `0110` | `72` |
| `1001` | `72` |
| `1100` | `72` |
| `1111` | `25,968` |

Thus all `97,224` signatures reduce locally to six master-membership
profiles.  The verifier constructs the signed balanced complex for all
`6^3=216` ordered profile triples.  Every one satisfies integral `MN=0`.
Their `(dim C1,rank N,rank M,dim H1)` histogram over `F2` is

```text
(0,0,0,0): 16     (2,1,0,1): 12     (2,1,1,0): 24
(3,1,2,0): 36     (4,1,3,0):  3     (5,2,2,1): 36
(5,2,3,0): 24     (6,2,4,0): 52     (7,2,5,0): 12
(8,2,6,0):  1
```

Exactly `48` profile triples retain one middle class.  Accounting for
distinct signatures, these profiles represent

```text
1,628,792,064 ordered triples
  271,465,344 unordered triples.
```

This accounting deliberately applies no global properness or pairwise-
incomparability filter; the node record alone cannot decide those global
properties.  Its purpose is to pin the size of the local incidence residue,
not to count admissible 9DVL source families.

Dihedral symmetry of the four chambers together with permutation of the
three signature colors compresses the 48 nonexact profile rows to only three
orbits:

| representative | ordered profile rows | ordered signature triples |
|---:|---:|---:|
| `(3,3,12)` | `12` | `4,416,768` |
| `(3,6,9)` | `24` | `8,957,952` |
| `(3,12,15)` | `12` | `1,615,417,344` |

These three rows are the smallest hostile regressions for any proposed
node-local pair contraction.

The outer cycle of this fan is only the boundary of the stored node scope;
it is not parent infinity.  The verifier therefore performs a second replay
which retains that cycle as ordinary cells.  All 216 closed-disk profile
triples are then middle-exact.  The 48 classes above are precisely local
relative fundamental classes awaiting attachment outside the stored disk.
This paired replay proves that an artificial chart boundary cannot be tagged
as relative infinity: the infinity ledger materially changes the rank.

This is a deliberate falsification regression.  It proves that a covered
local node, a canonical integral lift, and `MN=0` do not imply relative
middle exactness after an unproved boundary declaration.  Cells elsewhere
in the parent do fill the closed local model and can fill the same classes
globally.  Therefore the result is not a 9DVL counterexample.  It prevents
replacing global closure coverage by a collection of clipped wall collars or
by the formal `MN=0` identity.

## 5. Exact type-49 collar regression

Triangulate the isolated type-49 collar from
`DIAG3_PAIR_RESIDUAL_WALL_ADJACENCY.md` into four triangles.  Its two selected
colors are bad on both halves.  The receiver is feasible in the left open
square and bad on the central wall and right square.  Direct extraction from
these three closed bad subcomplexes gives

```text
dim C1 = 14,   rank_F2(N) = 8,   rank_F2(M) = 6,   H1 = 0.
```

The verifier independently starts from the original two-square regular-CW
closure poset, generates every barycentric face chain, and obtains

```text
dim C1 = 46,   rank_F2(N) = 22,   rank_F2(M) = 24,   H1 = 0.
```

All integral incidence identities hold in both subdivisions, independently
of the original square-cell orientation.  This demonstrates subdivision
invariance and shows how a certified wall collar enters the master model
without storing its root `73`, its five-circuit auxiliaries, or its receiver
witness in the final pair matrix.  Those exact data certify the three base
labels; the master extractor uses the certified labels thereafter.

## 6. Resulting global workload

The pair completion has an exact alternative consisting of four
proof-bearing tasks.  This trades the sector-frontier workload for a full
base master subdivision; it does not claim that constructing the latter is
computationally free.

1. Construct one finite regular compactified master subdivision for each
   parent source orbit, with complete closure and infinity accounting.
2. Label every open chamber by its exact complete-tope set and every lower
   cell by (4), independently checking singular and simultaneous walls.
3. Generate only comparable cell pairs and strict closure three-chains,
   hash the signature-to-membership-profile map, and extract
   `T,E01,E02,E12` for every relevant profile triple.
4. Run the mod-two middle-rank test.  Integral signs and `MN=0` are generated
   canonically from the certified closure poset and are not a fifth search.

The smallest remaining gap is therefore global parent-cell coverage and the
resulting middle ranks, not root-choice coherence.  The current 178-point
bank has zero certified adjacency edges, and the new type-49 collar lives in
a different parent cell, so neither supplies the required master complex.
The honest diagonal score remains `2/9`.

## 7. Exact reconstruction no-go for the existing row-2599 records

There are two different statements which must not be conflated.

The exact negative statement is:

> The pinned row-2599 point bank, factor-state table, scoped roadmaps, and
> selected stress paths do not encode enough incidence or coverage data to
> reconstruct a closure-complete labelled regular poset.  Any such poset
> would require new proof-critical semialgebraic computation.

This is not a mathematical impossibility theorem for construction.  The 70
parent inequalities and 26,740 stored exact residual polynomials are valid
input to a deterministic exact CAD, roadmap, compatible triangulation, or an
equivalent structural decomposition.  Such an algorithm can in principle
generate a compactified regular poset.  Its cell universe, coverage proof,
regularity proof, closure relations, and infinity tags would be new
certificate data, not a canonical decoding of the present samples.

`verify_diag3_pair_global_closure_gap.py` makes the existing-data obstruction
machine-exact.  It pins every relevant artifact and proves:

* the 178 point charts have 178 distinct residual factor-sign rows, their
  pairwise Hamming distances range from `1,125` to `5,600`, and there is no
  stored or one-factor-sign candidate adjacency between two of them;
* the slice, line, disk, and node roadmaps all have `source_chart = 0` and no
  global cell-ID, continuation, closure, or infinity table;
* the complete coordinate line has 26 chambers and 25 distinct factor-wall
  incidences.  Only one chamber contains chart zero and no other atlas point
  can equal one of the other 25, so the exact generic-chamber lower bound is
  already `178+25=203` rather than 178;
* the two long stored stress paths join only `12--37--176` and retain nine
  selected feasibility colors.  They do not isolate every residual event or
  define master-cell closure incidences; and
* for every one of the six minimum-Hamming chart pairs, the literal straight
  interpolation leaves parent 2599.  Five pairs have 38 parent brackets with
  76 total interior roots, and the sixth has 32 brackets with 64 roots.  This
  falsifies only the simplest deterministic bridge, not the existence of a
  parent-resident path.

The first missing block is therefore not an adjacency guess.  It is the
coverage-certified global cell universe for one compactification of parent
2599.  The machine-readable resumption record
`data/DIAG3_PAIR_GLOBAL_CLOSURE_OPEN_OBJECT.json` names the smallest target as

```text
row2599_compactified_labelled_order2_v1
```

It requires exact compactification coverage, regular-ball cell certificates,
all strict comparable pairs and three-cell chains, the genuine infinity
subcomplex, complete signature labels, and embeddings of every existing
point/local certificate.  That row-2599 object is only a pilot: compatible
objects for every required parent source orbit and the global middle-rank
replay are still required for diagonal three.

The resumption preflight is now more precise.  Exact replay of
`verify_diag9_active_sector.py` certifies that `8,916` of the `26,740`
primitive residual factors have empty wall sections in parent 2599, leaving
`17,824` candidate factor equations for a universal row-2599 generator.  This
is a proof-safe parent-specific reduction; it does not say that all `17,824`
remaining walls meet the cell.  The sorted complement is now exported as the
71,316-byte artifact
`data/DIAG3_PAIR_GLOBAL_row2599_candidate_factors.bin` and is independently
replayed from direct determinants of the stored row-2599 integer realization.
This removes the earlier dependency/export gap.

The compactification choice is now fixed as well.  After normalizing the
first five columns, each of the three moving columns lies in a positive
projective 3-simplex.  Their product `(Delta^3)^3` has 64 gauge charts; all
transition cocycles and all twelve coordinate-divisor/parent-wall identities
are exact.  In particular the standard affine infinity divisors are
`[2346]`, `[2347]`, and `[2348]`, so no artificial infinity face is added.

Thus the first two generator inputs are complete.  The remaining first block
is a deterministic sign-invariant regular-cell generator on the pinned 64
charts and 17,824 factors, followed by independent coverage and regularity
replay.

A bounded standard-chart CAD, a point bank, or a coordinate-path network
still cannot be promoted to the global master poset because it does not
continue every generated cell onto the pinned simplex-face atlas.

The pinned observation digest is

```text
27e55460f7bb22f1ec278d67c7441fd06e6a455c32605d00a1bb57b294edf85b
```

## Replay

```console
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/verify_diag3_pair_global_master_quotient.py

PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/verify_diag3_pair_global_closure_gap.py --manifest \
  ai/omreal/data/DIAG3_PAIR_GLOBAL_CLOSURE_OPEN_OBJECT.json

PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/verify_diag3_pair_residual_wall_adjacency.py
```

Pinned semantic digest for every relative/closed node-profile matrix and both
collar subdivisions:

```text
3fa42824f50159521c1e7a38f9bb56952460a7e4e5f736f76c4403dbe9eb7214
```

The first command proves the quotient, canonical-lift, and local regression
statements.  It does not claim a global parent subdivision or global pair
middle exactness.
