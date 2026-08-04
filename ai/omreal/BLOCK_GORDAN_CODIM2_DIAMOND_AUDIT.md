# Codimension-two block-Gordan diamonds and the cluster no-go

## Outcome

There is a proof-safe universal codimension-two statement, but it is
conditional on precisely the support premise left open by the codimension-one
audit.

> **Acyclic-carrier diamond.**  Suppose the two composites of chosen
> enlarged-support wall cospans arrive at one codimension-two node and are
> carried, face by face, by nonempty coordinate faces of a common normalized
> Gordan polytope.  Then the composites are integrally chain-homotopic,
> relative to every zero face on which they already agree.  The homotopy can
> be chosen in the union of their supports.

The proof is simply that every nonempty coordinate restriction of a Gordan
polytope is convex.  The acyclic-carrier theorem supplies the homotopy
inductively.  Thus a codimension-two node creates no additional homological
obstruction **after** a common nonempty support carrier has been supplied.
An empty coordinate face is still the exact obstruction from
`BLOCK_GORDAN_RESIDUAL_MUTATION_MAP_NO_GO.md`; convexity cannot define a map
into an empty face.

The exact row-2599 transverse `65+65` node passes the base-level diamond test:

- the two branches meet transversely and contain seven residual types each;
- all `4,225` cross-branch wall pairs share zero or one derived normal;
- every non-full signature pattern is a half-disk controlled by one branch;
- every finite common-feasibility intersection and every finite bad-locus
  union is empty or a disk.

It is therefore a clean commuting node, not a counterexample.  It does not
certify the missing common support carrier: its stored exact labels are topes,
not the coordinate-face maps of all circuit polytopes, and it contains no
quadrant-only signature which changes on both branches.

The suggested cluster/Pluecker interpretation does not provide the missing
universal theorem.  The normalized residual formulas are not homogeneous
cluster exchange polynomials, except for type `42`; type `42` is an arbitrary
`S_8` relabel of the full-support quadratic cluster polynomial but is not a
dihedral relabel in the standard cyclic `Gr(4,8)` cluster structure.  Across
all labeled residual determinants there are `1,554` distinct `Z^8` degrees,
far more than the published list of `174` cubic cluster variables.  More
fundamentally, cluster mutations are subtraction-free birational maps on
cluster tori and are singular on the cluster-coordinate divisor.  Their
square/pentagon coherence does not extend through a sign-changing residual
wall in an arbitrary oriented-matroid cell.

No third-diagonal term is closed by this local result.

The exact verifier is `BLOCK_GORDAN_CODIM2_DIAMOND_AUDIT.py`.

## 1. The conditional universal diamond

Fix a signed derived-normal matrix `A=A_sigma(Y_*)` at a codimension-two
node.  For a coordinate set `U subseteq [56]`, put

\[
 P_U(A)=\{w\in\mathbb R_{\ge0}^{U}:
             \mathbf1^Tw=1,\ A^Tw=0\}.                         \tag{1}
\]

Embedding by zero outside `U` identifies `P_U(A)` with a coordinate face of
the full normalized Gordan polytope.  It is empty or a compact convex
polytope.  In particular,

\[
                 \widetilde H_i(P_U(A);\mathbb Z)=0
                 \quad\text{for every }i                         \tag{2}
\]

whenever it is nonempty.

Let `K` be the cellular source complex for one corner of a two-wall diagram,
and let

\[
                 f,g:C_*(K;\mathbb Z)\longrightarrow C_*(P(A);\mathbb Z)
                                                                    \tag{3}
\]

be the two iterated specialization maps.  Suppose that for every face
`tau subseteq K` there is a support `U(tau)` such that

1. `P_(U(tau))(A)` is nonempty;
2. both `f(C_*(tau))` and `g(C_*(tau))` lie in
   `C_*(P_(U(tau))(A))`; and
3. `U(tau') subseteq U(tau)` when `tau' subseteq tau`.

The assignment `tau -> P_(U(tau))(A)` is an acyclic carrier.  The integral
acyclic-carrier theorem gives `H` with

\[
                         \partial H+H\partial=f-g.                \tag{4}
\]

If `f=g` on a subcomplex, the usual relative induction takes `H=0` there.
This is the precise zero-face compatibility which convexity does provide.
The identical argument applies to the full block-Gordan fiber: replace `A`
by the block-diagonal equations and let `U` include block labels as well as
normal coordinates.  Every such coordinate restriction is again convex.

Once two facewise codimension-one composites are actually defined on one
common subdivision, the carrier premise is automatic: take `U(tau)` to be
the union of all coordinates occurring in the two image chains on faces of
`tau`.  Either image makes that node face nonempty.  Thus there is no new
codimension-two obstruction after a genuinely face-defined codimension-one
system exists.  The unresolved issue is exactly that the dying zero face can
prevent such a codimension-one system from being defined before support
enlargement.

For the elementary square, orient the four boundary edges cyclically.  Its
integral cellular matrices are

\[
 d_2=\begin{pmatrix}1\\1\\1\\1\end{pmatrix},\qquad
 d_1=\begin{pmatrix}
 -1&0&0&1\\1&-1&0&0\\0&1&-1&0\\0&0&1&-1
 \end{pmatrix}.                                                   \tag{5}
\]

They have ranks one and three, and `d_1d_2=0`.  Hence the boundary loop is
filled primitively over `Z`.  A node polytope need not have this square as a
single face; (2)--(4) fill it by an integral cellular two-chain in whatever
polygonal subdivision the polytope has.

This proves existence, not canonicity.  Contractibility also supplies higher
homotopies among different fillings.  The hypothesis that all carriers in
(3) are nonempty is indispensable.  On the dying codimension-one face it is
exactly false (`point -> point <- empty`), which is why the enlarged interval
from `BLOCK_GORDAN_RESIDUAL_ELIMINATION_CELLS.md` was needed first.

## 2. Exact classification of the row-2599 node

The node certificate gives two coprime transverse branches.  Each branch has
the same exact residual-type census:

| residual type | occurrences on each branch |
|---:|---:|
| 36 | 12 |
| 37 | 6 |
| 39 | 3 |
| 41 | 12 |
| 44 | 12 |
| 46 | 8 |
| 47 | 12 |
| **total** | **65** |

Thus the node exercises all `28` unordered pairs among these seven types,
but none involving types `38,42,48,49,50,51`.  It covers only `28` of the
`91` formal unordered pairs of the 13 residual types.

Among the `65*65=4,225` labeled cross-branch pairs, the two residual
four-sets have

| common derived normals | labeled pairs |
|---:|---:|
| 0 | 3,990 |
| 1 | 235 |
| 2 or more | 0 |

Anchoring the first four-set at its exact 52-table representative and
quotienting the second by the stabilizer gives `2,145` unordered `S_8`
orbits.  Of these, `121` are one-overlap orbits.  The multiplicity checks are

\[
 2{,}145=2{,}080+65,qquad 121=114+7,                              \tag{6}
\]

where the first summands have multiplicity two in the `4,225` or `235`
node-specific lists, respectively, and the second have multiplicity one.
Consequently a wall-type pair alone is much too coarse to encode a
codimension-two mutation.

## 3. The exact signature diamond

Order the four chambers cyclically as

\[
                         (++),(+-),(--),(-+).                     \tag{7}
\]

The complete exact tope enumeration at the four chambers has only these
support masks:

| mask | multiplicity | local shape |
|---:|---:|---|
| `1111` | 25,968 | whole disk |
| `0011` | 72 | one open-side half-disk plus its generic wall |
| `0110` | 72 | one half-disk |
| `1001` | 72 | one half-disk |
| `1100` | 72 | one half-disk |

Signatures absent from all four chamber lists have mask `0000`; their local
feasibility set is empty and their local bad locus is the whole disk.  Their
multiplicity is not encoded by this node-local union file and is not needed
for the closure calculation.

In integer bit notation these are `15,3,6,9,12`.  In particular there is no
mask `1,2,4,8`: no signature occupies a single quadrant, and none undergoes
independent feasibility losses at both branches.

The intersection closure of the feasibility masks is

\[
                 0,1,2,3,4,6,8,9,12,15.                         \tag{8}
\]

Every nonzero mask in (8) induces a connected subgraph of the four-cycle and
is geometrically a sector, half-disk, or disk.  Dually, the union closure of
the bad half-disks is

\[
                 0,3,6,7,9,11,12,13,14,15.                      \tag{9}
\]

Every nonzero member of (9) is a half-disk, the complement of one open
sector, or the disk.  It is contractible.

The proper block-Gordan projection has compact convex fibers, so the full
resolution over every local bad union in (9) is homologically a disk.  This
proves a base-level and unrestricted-fiber diamond for every finite signature
family on this exact transverse disk.  It does **not** prove a
coordinate-support diamond: the node certificate stores complete tope sets,
but not all circuit vertices, zero-weight faces, and specialization maps for
globally proper signatures which are absent from the disk.

## 4. Why cluster square/pentagon coherence does not apply

### 4.1 The displayed formulas are chart formulas

The 12 displayed residual binomials have the form

\[
                    [A][B]-[C][D].                               \tag{10}
\]

A polynomial exchange relation in the homogeneous coordinate ring of the
Grassmannian is homogeneous for the `Z^8` column grading.  The exact degree
check finds

\[
 \deg[A][B]=\deg[C][D]
 \quad\Longleftrightarrow\quad\text{residual type }42.           \tag{11}
\]

The three displayed terms for type `51` do not have one common `Z^8` degree
either.  This is not an error in the residual identities: they were derived
after fixing a projective frame.  It proves that the displayed equations for
the other 12 types are chart equations, not global homogeneous cluster
exchange polynomials.

### 4.2 The sole homogeneous binomial is not a cyclic cluster relabel

For type `42`, the chart polynomial is

\[
              q_{42}=[1356][2478]-[1478][2356].                  \tag{12}
\]

The full-support quadratic `Gr(4,8)` cluster polynomial may be represented by

\[
 c=[1234][5678]-[1235][4678]+[1236][4578].                       \tag{13}
\]

Exact reduction on the generic nine-variable frame finds `144` arbitrary
`S_8` permutations taking `c` to `+/-q_42`, but none of the 16 cyclic or
reflection permutations does.  The standard Grassmannian cluster structure
uses the cyclic order; its label symmetries are dihedral, not all of `S_8`.
The published classification says the other seven full-support quadratic
variables are rotations of (13).  Therefore (12) is not one of those eight
variables in the fixed cyclic structure.  See the explicit quadratic list in
[Zhang--Tang--Zhao](https://arxiv.org/abs/2507.18432).

### 4.3 The global count is too large

Before projective normalization, a determinant of four derived normals is an
`SL_4` invariant of total column degree 12, hence Pluecker degree three, with
`Z^8` degree equal to the incidence vector of its four supporting triples.
The exact `84,840`-wall census has `1,554` distinct such degree vectors:

| type | distinct `Z^8` degrees |
|---:|---:|
| 36 | 1,120 |
| 37 | 168 |
| 38 | 70 |
| 39 | 168 |
| 41 | 168 |
| 42 | 70 |
| 44 | 70 |
| 46 | 1,120 |
| 47 | 168 |
| 48 | 28 |
| 49 | 168 |
| 50 | 70 |
| 51 | 70 |

The union has `1,554`, because degree sets overlap across types.  The
published `Gr(4,8)` cluster-variable classification has only `174` cubic
variables.  Distinct `Z^8` degrees are distinct nonzero homogeneous
functions, so not every labeled residual determinant can be a cubic cluster
variable.  This does not exclude an occasional residual factor from being a
cluster variable or cluster monomial; it excludes a universal identification.

### 4.4 Positivity has the wrong domain

Cluster mutation replaces one coordinate by a subtraction-free positive
rational expression.  Cluster variables are positive on the totally positive
Grassmannian; see [Scott](https://arxiv.org/abs/math/0311148) and the positive
atlas discussion in [Le--Fraser](https://arxiv.org/abs/1710.05014).  A
cluster seed is a torus chart, so mutation is not a continuation through the
divisor where the mutated coordinate vanishes.

The 9DVL parent cells are arbitrary uniform oriented-matroid sign cells, not
the totally positive cell.  A residual wall is exactly where its factor
changes sign or vanishes.  Hence square/pentagon relations among positive
cluster charts live on the complement of the wall and do not give the needed
zero-weight specialization through it.

## 5. Exact remaining obstruction and third-diagonal status

At a fixed node, convexity settles the chain-homotopy problem once the common
carrier in Section 1 exists.  The smallest remaining obstruction is therefore
the following Boolean/support condition:

> For every two-wall incidence and every zero face of the chosen
> codimension-one cospans, do the two composites land in one nonempty
> coordinate-restricted node polytope?

The row-2599 node does not falsify this condition, but it does not exhaust it:
six residual types are absent, no wall circuits share two normals, and no
signature has a quadrant pattern.  A decisive next certificate should seek a
node with at least one of those three features and enumerate the actual
circuit-support specializations, not only its tope labels.

For diagonal `s=3`, the unresolved Mayer--Vietoris terms remain the pair
`H_c^1` and triple `H_c^0` columns.  Contractible neighborhoods around one
transverse node do not exclude a global loop of compact pair components or a
global split--remerge triple component.  One still needs a complete wall
complex, common-carrier existence at every incidence, and control at the
boundary of the parent realization space.  Accordingly, no diagonal is
promoted.

## 6. Verification

Run

```console
python ai/omreal/DIAG9_GRAPH_verify_row2599_node.py
python ai/omreal/BLOCK_GORDAN_CODIM2_DIAMOND_AUDIT.py
```

The first command rechecks the exact two-variable residual factorization,
rank-two Jacobian, all cell/wall/node tope sets, and the embedded disk.  The
new audit then checks:

- both exact 65-occurrence residual-type lists;
- all `4,225` cross-branch support overlaps;
- the `2,145/121` `S_8` pair-orbit censuses;
- feasibility intersections and bad-union closures;
- the normalized `Z^8` grading obstruction;
- all `84,840` labeled residual degree vectors;
- the arbitrary-`S_8` versus dihedral orbit test for type `42`; and
- the primitive integral square filler.
