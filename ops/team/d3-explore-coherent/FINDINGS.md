# Flexible witness compatibility at the actual support event

**FINITE EXACT compatibility test; NULL for the original obligation.**

Convex witnesses bypass the strict coordinate-face point-contraction
obstruction by retaining comparison paths and a triangle. The triangle has
three positive block masses in its interior. Its boundary cannot be filled
inside the pair-face layer, even if that layer uses all 56 witness coordinates
in each block. Thus the flexibility works, but its filtration cost is exactly
the inherited joined-fiber/Cech mechanism. No new parent-motion, proper
escape, or compact-support attachment mechanism was found.

Opening revision: `c27a36d6e3f47a2b4c7bb017774cbe5df30abdc2`.
Canonical base: `21a97db6aa66912fd37556d81711c0588c454a7d`.
Owned surface: `ops/team/d3-explore-coherent/`.
The ledger remains `2/9`; all seven original obligations remain open.

## Scope and source accounting

The experiment uses chart zero of the pinned
`ai/omreal/data/seeat_parent2599_upper178.npz`, the three labels

```text
14988895318912, 3405195891438080, 40418075143643136,
```

and the inherited coordinate move `Y[1,1] += t` (zero-based matrix indices).
The event parameter is

```text
t* = 37864449186859942661765893 / 7029591949415530407677535.
```

The new script independently reads the archive's integer matrix, recomputes
all derived normals, rational determinants, circuit weights, and affine
kernel ranks. It imports no producer acceptance logic. The admitted proper
and incomparable status of the three extension labels is inherited from the
pinned detector arithmetic/admissibility audit; this lane does not rerun
that audit or enumerate signatures. Source hashes are in
`SOURCE_MANIFEST.json` and repeated in `RESULT.json`.

The initial test covers exactly `t* - 10^-6`, `t*`, and `t* + 10^-6`.
It is not an interval certificate or a full-parent coverage claim. The
follow-through is at the actual event, followed by a stated elementary
mass-map argument for arbitrary nonempty convex witness fibers. The latter
has no parent-motion or compact-support conclusion.

## Initial test: retaining the whole old edge still fails

For block 0, retain both actual circuit choices from the strict-contraction
no-go:

```text
U = (123,456,137,238,148),
V = (134,456,137,238,148).
```

In colex zero-based indices these are `(0,19,21,37,38)` and
`(2,19,21,37,38)`. Consider the entire six-coordinate restricted normalized
fiber, rather than a chosen circuit vertex.

| Parent parameter | Actual six-coordinate fiber | Exact reason |
| --- | --- | --- |
| `t* - 10^-6` | A closed edge | The augmented equality matrix has rank five; two distinct normalized solutions are positive on their five-supports. |
| `t*` | A singleton | Both endpoints become the same positive four-support witness; the affine null direction has opposite nonzero signs in coordinates `123` and `134`. |
| `t* + 10^-6` | Empty | Each of the two normalized endpoint continuations is negative in its own added coordinate; every normalized solution is an affine combination of them. Nonnegativity would force both affine coefficients nonpositive, although their sum is one. |

All seventy parent determinants retain their original nonzero signs at each
of these points. This is an internal witness event, with no true-infinity
attachment. The two old circuits for each of blocks 1 and 2 remain strictly
positive at all three tested parents.

This strengthens the selected-vertex diagnostic to the full old
six-coordinate face. It does **not** test whether block 0 has some other
witness among all 56 coordinates on the right. That separate full-system
question belongs to the event track. No conclusion here depends on its
answer.

## Exact follow-through: two receiver choices and their compatibility

At the event choose the normalized witnesses `v0,v1,v2` on supports

```text
v0: (123,456,137,238,148), with weight(123)=0,
v1: (123,345,257,167,128), all five weights positive,
v2: (123,136,256,247,348), all five weights positive.
```

Embed each `vi` in its own labeled block of the 168-coordinate joined
Gordan fiber. Their block-mass vectors are exactly the three standard basis
vectors. They are affinely independent; their convex hull is a genuine
embedded two-simplex of the actual joined fiber, including the block-0
zero-coordinate event face.

Transferring a block-0 witness to block 1 gives the segment `e01`; transferring
it to block 2 gives `e02`. The segment `e12` compares the receiver endpoints.
With oriented edges `(01,02,12)`, the comparison loop is

```text
z = e01 - e02 + e12.
```

The complete explicit filler is

```text
F(a0,a1,a2) = a0*v0 + a1*v1 + a2*v2,
ai >= 0, a0+a1+a2 = 1.
```

Linearity of each block's Gordan equations makes every point a valid
normalized joined witness. Restricting `F` to an edge gives exactly the three
specified transfers, so their compatibility is not an uninstantiated
acyclic-carrier premise. At the barycenter all three block masses equal
`1/3`.

The exact boundary matrices, also stored in the replay, are

```text
d1 = [[-1,-1,0], [1,0,-1], [0,1,1]],
d2 = [1,-1,1]^T.
```

Thus `d1*d2=0`. Solving the three integer equations for `ker d1` gives
exactly `Z*(1,-1,1)`. The pair-face boundary has `H1=Z`; adjoining this
primitive triangle column kills it. The filler is compact because its
parameter simplex is compact, but it lies over one interior parent point.
Compactness here supplies no relative chain at true parent infinity.

## The filtration cost survives enlargement to the entire fiber

This argument quantifies over **any** three nonempty normalized Gordan
witness fibers `P0,P1,P2` at one fixed parent. Let `Gamma=P0*P1*P2` be their
joined fiber, and let `Gamma_pair` be its closed subspace with at most two
positive block masses. Taking block masses defines

```text
m : Gamma_pair -> boundary(Delta^2).
```

The chosen witnesses supply a continuous section
`s:boundary(Delta^2)->Gamma_pair`, with `m*s=id`. Hence the loop `s(z)` is
nonzero in integral `H1(Gamma_pair)`: applying `m` to a hypothetical filling
would fill the generator of the circle. This rules out a filling of this
particular loop anywhere in the entire pair-face fiber, not merely inside
our small triangle. In particular, no contraction of `Gamma_pair` exists.

The full convex joined fiber does fill the loop, through three-block points.
The ordinary contraction toward `v1` already displays the cost: an interior
point of edge `02` acquires positive block-1 mass before either of its old
block masses disappears. It leaves the pair layer immediately.

This is a fiberwise obstruction to preserving the block-mass filtration in
this proposed contraction. It is **not** a global pair-cohomology
counterexample, an obstruction to every mixed carrier, or a proof that
filtered complexes cannot have useful coherent comparison maps. A filtered
chain construction can account for the triangle in the next layer; it still
has to construct the actual parent-dependent differential and its boundary
attachment.

## Novelty audit and useful null

`BLOCK_GORDAN_ALL_CODIM_COHERENCE.md` already proves conditional integral
higher coherence from nonempty convex carriers once facewise maps and a
common subdivision exist. `DIAG3_SINGLE_BAD_TWO_SKELETON.md` already uses the
proper normalized convex witness projection. Those results encompass the
fiberwise mechanism above. This lane adds an exact source-event instance and
an explicit filtration check, not a new general construction.

The test answers the intended cheap discovery question: flexible choices
can repair the strict point-choice incompatibility, but convexity alone pays
for the repair with the triple mass face. It does not produce the geometric
nonzero trace required by the canonical detectors or settle their
nondegeneracy, which the detector source proves equivalent to the original
pair obligation.

The next discriminating question is a different geometric one: can an actual
parent-dependent mixed carrier attach the required triangle coherently to
true parent infinity while implementing the existing labeled block-mass
filtration? Repeating convex witness contractions or all-codimension
coherence identities will not answer it. This lane supplies no bounded
universal route to that attachment and therefore recommends **STOP** here,
with trajectory **INFORMATIONAL** and theorem-distance change zero.

## Replay and resource record

```console
python -B ops/team/d3-explore-coherent/verify_coherent.py
```

The replay checks frozen JSON equality and rejects wrong boundary orientation,
labeling a three-block interior point as a pair face, and labeling this
interior witness event as parent infinity. It completes in under one second
in the supplied environment. Discovery used one initial test and one exact
follow-through, no new dependencies, no large census, no external writes,
no subagents, and far less than the ten-CPU-minute ceiling. Discovery froze
at the decisive/midpoint finding; later work only recorded and replayed it.
There are no ledger, historical-source, or protected-verifier edits.
