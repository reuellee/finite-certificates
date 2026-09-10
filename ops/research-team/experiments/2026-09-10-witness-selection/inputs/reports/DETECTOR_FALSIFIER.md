# Actual support geometry excludes strict local detector shortcuts

**Original pair target: NULL. Auxiliary exclusions: exact and narrowly scoped.**
The actual row-2599 canary has an open triple-bad neighborhood on which all
three exclusive-pair frontiers are absent. This makes the missing boundary
information intrinsically global: a left inverse of the pair restriction
cannot exist at the sheaf level. It does **not** rule out a left inverse on
degree-one compact-support cohomology.

Discovery froze at the structural gate. No atlas, signing census, parameter
search, or new global cohomology computation was attempted. The original
ledger stays 2/9, with seven open obligations and unknown global pair coverage.
The auxiliary results receive zero theorem credit.

Base revision: `730fd6c7b6c2c3e8cbbf94ab4da3bc97ba53f095`.
Owned surface: `ops/team/d3-detector-falsifier/`.

## 1. Actual admissible parent anchor

Use chart zero of the hash-pinned `seeat_parent2599_upper178.npz`. Its matrix,
all seventy parent determinants, three signatures, and the exact circuit
weights are recorded in `ARITHMETIC_REPLAY.json`. The signature triple is

```
14988895318912, 3405195891438080, 40418075143643136.
```

The verifier uses only the Python standard library and imports no repository
producer. It reads the NPY members of the pinned archive directly, computes
the seventy determinants and all fifty-six actual derived normals, and checks
3,780 Grassmann--Pluecker sign relations. The normal convention is
`a_I(Y) p = det(y_i,y_j,y_k,p)` in colex triple order; a set signature bit
means the positive normal sign.

Validity, properness, and incomparability are not inferred merely from the
three different bit strings. The separately pinned historical
`admissibility_flow.json` provides anchors at charts 3, 14, and 2,
respectively. Each realizes exactly its designated signature while the other
two have positive Gordan dependencies. The independent replay checks all
seventy parent signs at each anchor, all fifty-six strict signed inequalities,
and all six opposite dependencies, and binds the parents, assignment entries,
and points to the archive bytes. Thus each feasibility region is nonempty
and proper, and all six ordered noninclusions are certified. This is a
bounded replay of existing admissibility witnesses, not additional source
coverage.

The integer parent represents a point of normalized realization space.
Use a local projective gauge slice fixing the first five labeled projective
points to their values and signs at this supplied parent. Their nonzero frame
brackets make them a projective frame. The frame-normalizing projective map
varies continuously near the parent and has a linear lift equal to the
identity there; choose the column scales equal to one there. On a sufficiently
small neighborhood the lift has positive determinant and these scales stay
positive. Thus this local gauge preserves the oriented data without requiring
normalization to an unspecified all-positive frame. Choose local affine
charts for the remaining three projective points; their three coordinates
each give a nine-dimensional local slice. The strict parent bracket signs
define an open subset of this slice, containing a small ball.

Under this local gauge each derived normal is a positive multiple of its
inverse-transpose image. Positive dependencies, strict feasibility, and
their exact zero-coordinate faces are preserved by inverse positive weight
rescaling and normalization. The conclusions therefore descend from the
displayed matrix gauge to a neighborhood in the actual normalized parent
cell, and a sufficiently small such neighborhood is homeomorphic to `R^9`.

## 2. The actual triple-bad set has interior

For blocks 0, 1, and 2 the following five-supports have strictly positive
cofactor dependencies at chart zero:

| Block | Circuit support |
| --- | --- |
| 0 | `123,456,137,238,148` |
| 1 | `123,345,257,167,128` |
| 2 | `123,136,256,247,348` |

Every one of the five deletion determinants is nonzero, so each selected
signed system has rank four and a unique normalized positive circuit. All
seventy parent bracket signs and all fifteen cofactor signs persist on a
sufficiently small open parent neighborhood. The cofactor identities hold
identically, so these signs certify badness throughout that neighborhood;
this is stronger than badness at one sample point.

Consequently there is a small open ball `V` in the normalized parent cell,
homeomorphic to `R^9`, such that

```
V subset T,    A01 intersect V = A02 intersect V = A12 intersect V = V,
E01 intersect V = E02 intersect V = E12 intersect V = empty.
```

For the constant sheaves extended by the closed inclusions, the actual pair
restriction on `V` is

```
Q_V^3 --> Q_V,     (x01,x02,x12) |--> x01-x02+x12.
```

Its kernel is the constant rank-two sheaf, with independent sections
`(1,1,0)` and `(0,1,1)`. No morphism of these sheaves, or of their derived
objects, can be a left inverse: a left inverse would split-inject their
degree-zero stalks. This excludes the **literal sheaf-level left inverse of
the direct-sum pair restriction**. It does not assert impossibility for
all conceivable constructions called local detectors.

The closed/open boundary morphisms to the exclusive-pair terms restrict to
zero on `V`, since those terms have empty support there. The same holds for
the prover's secondary boundary morphisms whose targets are
`Ci=Bi minus (Bj union Bk)`. Thus actual boundary detection must depend on
attachment outside this open triple-bad region. This is the geometric content
behind the stalk calculation, beyond an arbitrarily chosen matrix example.

There is no contradiction to the desired global degree-one injectivity:
`H_c^1(V;Q)=0`, as `V` is a nine-dimensional open ball. Local sections of the
rank-two kernel do not thereby produce compact-support degree-one classes.
The signed frontier maps can detect globally assembled classes even though
their sheaf restrictions to `V` vanish. Neither a compact component nor a
nonzero class in the original `ker D` is constructed.

## 3. Exact zero-weight face test, with its limited relevance

In each of the three displayed supports, replace `123` by `134`. Each new
five-support is again a strictly positive rank-four circuit at the same
actual chart. The union of each old and new support has six coordinates.
The augmented matrix consisting of the four signed normal rows and the
normalization row has rank five, independently checked by rational Gaussian
elimination. Its nonnegative normalized kernel is therefore a genuine
one-dimensional coordinate face. The two circuit vertices are its endpoints,
and their convex combination is positive on all six union coordinates.

These are three actual witness edges, not abstract simplices. Their ranks and
strict signs also persist on a smaller choice of `V`. In particular the
coordinate-face inclusions at their endpoints are genuine zero-weight
specializations inside the full Gordan resolution.

The following precise class is excluded. Suppose that for every nonempty
coordinate face `P_U` one has a contraction
`H_U:P_U times [0,1] -> P_U` to a single point, and that all `H_U` commute
strictly with every coordinate-face inclusion. For either singleton circuit
face the homotopy must fix its unique vertex. Naturality makes the homotopy
on the six-coordinate edge fix both different endpoints for all times. Its
time-one map cannot be constant. Equivalently, even on one of these actual
edges there is no contraction to one witness that never enlarges positive
support.

This is a diagnostic for a **strict face-natural fiberwise contraction**, a
stronger requirement than a cohomological detector. No current boundary
candidate is asserted to need this strict contraction. Ordinary convex-fiber
contractions, proper acyclic-fiber pushforward, homotopy-coherent comparison,
and acyclic-carrier constructions remain possible; they may enlarge support
or retain comparison homotopies. The support-plane residence motion in
`DIAG3_SINGLE_BAD_TWO_SKELETON.md` moves the parent while transporting the
polytope by a face-preserving homeomorphism. It is not a contraction of the
entire witness polytope to one vertex, so this result does not conflict with
that theorem.

## 4. Replay and frozen handoff

```
python -B ops/team/d3-detector-falsifier/verify_detector_obstructions.py
```

The result passes three actual witness-edge checks, six strict circuit
checks, all admissibility anchors, and all 3,780 extension sign checks.
Flipping a supported signature bit and altering a kernel coefficient are
rejected by targeted hostile arithmetic controls. Source hashes, all exact
cofactors, the parent data, exclusions, and nonconsequences are preserved in
`ARITHMETIC_REPLAY.json`.

The first original missing input remains the global attachment that makes
boundary detection injective on the opposite-pair image. The existence of
canonical boundary connecting maps, or vanishing of their stalks on `V`,
does not supply that nondegeneracy theorem. No global theorem counterexample
is claimed, and no complete actual-space chain complex is certified.
