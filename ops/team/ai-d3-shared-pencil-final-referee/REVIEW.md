# Independent final review: shared two-triple pencil

**Decision: ACCEPT the exact route counterexample and the conditional escape
lemma. RETIRE the universal at-most-two-incident-triples criterion.** The
additional open-set robustness corollary is accepted with that same narrow
scope. Cycle research credit is **INFORMATIONAL**: the theorem ledger remains
`2/9`, both D3 invariants remain open, and none of the seven canonical
obligations is discharged.

This replacement referee completed the bounded Stage C work order after the
previous referee's capacity interruption. The preceding checker had no
acceptance report. Its code was inspected and replayed, and an independent
supplement using different exact determinant arithmetic was written here.
Only `ops/team/ai-d3-shared-pencil-final-referee` was modified. No producer
acceptance code was imported or executed, and no search was resumed.

## Frozen inputs and verification

The principal handoff is constructor commit
`7d0efe1c55efff2d17c906569e90f5fb0ae0e371`, integrated as `8b8adb7`.
The audited prior checker reads the identical principal bytes at
`4927d5bcc24d91cf173551b248721b247107073a`. Its original frozen code is at
`97835f3dd9f3e36f11adeb6e5b448e72b7bb9b60:ops/team/ai-d3-shared-pencil-referee/independent_check.py`,
SHA-256 `8f765eee29428b5d575e82e11eee60ae436132142d69da3aa7e14b4d40eef362`.
The independent second producer handoff is
`da1834fd34065fe826d230c26eb0b6b747dc082c`.

`SOURCE_PINS.json` records exact Git objects, byte counts, and SHA-256 pins.
In particular, the principal `OBSTRUCTION.json` is
`77bd316237f6fd7060e964aec1852daa10dfaa065a7d0c4194b0a59929a32afa`, and the
second `upper_chart_0_flow.json` is
`83485ff8bb0a1f8cacffdacbf829cbee5898721b008f8bd54ec2a661ca35e6ab`.
All replay inputs come from pinned Git blobs, including the NPZ arrays; no
sibling worktree or moving producer artifact is required.

The retained referee checker uses combinadic colex indexing and 4-by-4
Leibniz determinants over unbounded integers. NumPy only decodes NPZ arrays.
I checked its signed-row convention, nonnegative-dependence equations,
restriction construction, exhaustive set equality, integer inequalities,
primitive-row rescaling, and catalog/assignment bindings. Its local copy
changes input loading to pinned Git blobs; its arithmetic is unchanged.
`check_robustness.py` independently uses sorted reversed tuples for colex,
3-by-3 normal cofactors, and rational Gaussian elimination. It imports
neither producer code nor the other referee checker.

Both checkers pass. `CHECK_OUTPUT.json` records the full certificate replay;
`ROBUSTNESS_OUTPUT.json` records the separate exact supplement.

| Verified claim | Principal certificate | Second certificate |
|---|---:|---:|
| Distinct covered choices | 1,680 | 1,680 |
| Strict inequalities | 62,160 | 62,160 |
| Minimum integer margin | 6,858,251,431,715 (raw rows) | 162,514,748,513,691 (primitive rows) |
| Full positive Gordan witnesses | 3 | 3 |
| Blocking uses for signatures 0,1,2 | 1,596 / 83 / 1 | 1,596 / 83 / 1 |
| Distinct vectors in the second pool | — | 23 |

The ten inherited hostile mutations are all rejected: missing/duplicate
choices, zero separator, invalid pair, corrupt full witness, signature-bit
drift, anchor-parent drift, normal-order drift, and missing-choice/zero-vector
mutations in the second certificate. Four supplemental mutations also fail:
zero circuit weight, corrupt cofactor ray, a vanished deletion minor, and
incoherent cofactor signs. No solver success or search completeness is an
acceptance premise.

## Exhaustiveness and admissibility

For a label `e`, exactly 21 of the 56 colex triples contain `e`, and 35 omit
it. Every unordered incident pair leaves exactly 37 rows. Independent set
equality proves coverage of all `8 choose(21,2)=1,680` choices, with no
duplicates. At each choice one selected signature has a vector strictly
positive on every retained signed row. Its dot product with a nonzero
nonnegative dependence would be positive, contradicting the zero sum.

This also excludes supports using zero or one incident triple: pad their
union to a pair and retain the same witnesses with zero weights on the added
rows. Conversely, any three retained-row dependences give three witnesses
whose positive supports meet the common label in at most two triples.
Thus the finite predicate is exactly the proposed union-of-positive-supports
condition. Neither minimal circuits nor positivity on every retained row is
assumed. The equivalence does not require a rank hypothesis.

The counterexample parent is literally upper chart 0 in the pinned NPZ,
with signatures `14988895318912`, `3405195891438080`, and
`40418075143643136`. All 70 brackets are nonzero and match zero-based catalog
row 2599 with the original labels and positive basis orientation. The 56
normals are reconstructed from `a_I(Y)^T p=det[y_i,y_j,y_k,p]`. Both raw and
positive-gcd-primitive conventions are accounted for exactly.

Full badness is checked separately by three positive integer dependencies.
Upper charts 3, 14, and 2 supply, respectively, a strict feasible point for
signature 0, 1, and 2 and positive dependencies for each of the other two.
Each anchor has the same 70-bracket labeled parent sign pattern, and the
second certificate binds its feasible point to the exact stored point and
assignment arrays. These anchors establish nonempty, proper, pairwise
incomparable feasibility regions, including all six ordered noninclusions.
They also realize each uniform rank-four extension signature, which suffices
for validity. The supplement independently verifies all 3,780 relevant
three-term GP sign relations for the three target signatures.

The designated positive control, shatter pattern 0, has three valid restricted
witnesses at label 1 and triples 134/127. Shatter patterns 1, 16, and 8 bind
its signatures' admissibility. Upper chart 7 is correctly ineligible:
signature `58432476850159616` is strictly feasible on all 56 rows. No
replacement point was introduced, and the unused claim of exactly three
successful positive-control pairs is not accepted or needed.

## Conditional proper escape: accepted

Suppose the common-label support condition holds at a uniform parent. Pad
the retained triples to two distinct triples through `e`. Their spans are
distinct vector hyperplanes: equality would put at least four parent labels
in one three-dimensional space. Their intersection `L` has dimension two
and contains `y_e`.

Five of the seven fixed labels form a projective frame. Order the first four
to have positive determinant, and use fixed orientation-preserving linear
and positive column changes to normalize that frame. Its stabilizer on
oriented rays is only scalar, so varying the ray of `y_e` changes the actual
parent quotient. This frame remains valid at the proposed limit.

Every moving-column coordinate has a fixed nonzero sign `tau_j` determined
by a parent bracket. Normalize its positive ray by
`ell(x)=sum_j tau_j x_j=1`. Inside this fixed signed simplex,
`L intersect {ell=1}` is an affine line. The original parent signs impose
finitely many strict affine linear inequalities on it. Their residence set
is a nonempty bounded open interval containing the initial point. At an
endpoint at least one inequality vanishes. A coordinate-zero wall is itself
a bracket wall using three frame columns. The endpoint therefore is a
genuine nonuniform parent; it is not a removable affine-chart boundary.

Along the interior, each retained incident triple continues spanning its
original hyperplane. Its nonzero normal is consequently a positive scalar
`c_I(t)` times its initial normal; continuity prevents a sign change before
nonuniformity. Nonincident normals stay constant. Transport each witness by
`w_I(t)=(w_I(0)/c_I(t))/sum_K(w_K(0)/c_K(t))`, taking `c_I=1` for nonincident
rows. This preserves nonnegativity, normalization, and every dependence.
Zero weights stay zero. Positive rescaling preserves the rank of each
supported row system, including a rank-deficient initial support; ranks of
other derived subsystems impose no obstruction. Limiting weights or ranks
at the excluded parent endpoint need not be prescribed.

Reparameterizing the segment toward the endpoint by `[0,infinity)` gives a
proper path in the triple bad intersection. In the fixed nonmoving-frame
quotient chart it converges only to a nonuniform boundary point, so it
eventually avoids every compact subset of the uniform parent quotient.
This also justifies properness in the project's equivalent normalized
section. The map is continuous and its compact-set preimages are closed and
bounded.

If this pointwise condition held everywhere in a triple bad intersection,
any compactly supported locally constant degree-zero class nonzero at a
point would stay nonzero on its proper path, contradicting compact support.
Thus the stated *conditional* `H_c^0=0` consequence is correct. A continuous
choice of labels, pairs, witnesses, or paths over starting points is not
required for this argument. No pair-`H_c^1` conclusion follows. The actual
counterexample prevents applying this universal sufficient criterion.

## Open-set obstruction: accepted with exact scope

For each five-row signed support, write its ordered rows as `r_0,...,r_4`
and set `d_k=(-1)^k det(r_0,...,omit r_k,...,r_4)`. The identity
`sum_k d_k r_k=0` holds identically. The supplement verifies that all five
minors are nonzero, the cofactors have one coherent sign, and the supplied
positive weights are proportional to them. Hence every support has rank
four and is a positive circuit. This holds for all three supports in each
producer certificate, not merely for the principal three.

For the principal raw supports, the minimum absolute deletion determinants
are, respectively:

```
1590306865848117591794167506
51411140948915064241372106
708385986150582662615629300
```

The supplement also constructs the exact rational normal form
`[e_1,e_2,e_3,e_4,s,n_6,n_7,n_8]`, where `s=(-1,1,-1,1)` and each last column
lies in a fixed open signed three-simplex. Its coordinates are recorded in
`ROBUSTNESS_OUTPUT.json`. All 56 normal covariance identities, all three
principal positive circuit conditions, all 70 parent signs, and all 62,160
separator inequalities are verified in this normalized gauge.

Keep the normalized separator vectors fixed. The parent brackets, their
signed row evaluations, and the circuit cofactors are continuous polynomial
functions of the nine free normalized coordinates. The same finite list of
strict signs therefore holds on a neighborhood of this point. The cofactor
identity supplies positive full-system dependencies throughout that
neighborhood, and the separators continue blocking all 1,680 choices.
Intersecting these finitely many open conditions gives a **nonempty open
subset of the nine-dimensional parent space** with both properties. This
is a continuity consequence of exact strict certificates, with no new
sample or search. No explicit radius or maximal obstruction region is
claimed.

Here and throughout, “absence of pencils” means failure of witnesses whose
union uses a common label in at most two distinct incident triples. Three
or more incident planes can still have a two-dimensional vector
intersection. Such rank-two-star pencils, other motions, and paths that
first move to another point are not excluded.

## Research credit, resources, and freeze

The exact actual-parent counterexample settles the selected intermediate
universal lemma negatively. The conditional escape lemma remains useful
where its hypothesis holds, but neither it nor the open obstruction proves
the existence of a compact triple-bad component or refutes D3/9DVL. No
compactly supported cohomology class is constructed. Source existence and
generic countermodels retain only the scopes already independently accepted
at `ed10cbd5580e7266128cb477f5553bd122ee6805` and
`0de26f6a6561705b37d59dfb5d3886857ab96bd3`; they were not reopened here.

The opening proof-distance snapshot is
`(2/9,1,{diag3_pair_hc1,diag3_triple_hc0},7,UNKNOWN,UNKNOWN,9,12)`.
The theorem-relevant fields are unchanged. All seven obligations remain
open: `global_gluing`, `extension_labels`, `strict_closure`,
`relative_infinity`, `middle_rank_replay`, `diag3_pair_hc1`, and
`diag3_triple_hc0`. This referee does not edit ledger or administrative streak
counters. Exact theorem delta: zero. Cycle trajectory: INFORMATIONAL.
Investment decision: RETIRE precisely this universal shared-two-triple
route and stop discovery at the decisive endpoint; no successor route is
opened by this review.

`RESOURCE_ACCOUNTING.json` and `RUN_RESOURCES.json` record timing, storage,
and observed process memory. The two final replay processes took about
1.92 and 1.66 seconds and peaked at approximately 55.5 and 21.9 MiB working
set. The lane stayed within the inherited deadline, 16 GiB RAM, and 300 MiB
new-artifact limits. There was no human consultation, paid/external compute,
new cohort, push, merge, or canonical edit.

Replay from any checkout containing the pinned Git objects:

```
python -B ops/team/ai-d3-shared-pencil-final-referee/independent_check.py
python -B ops/team/ai-d3-shared-pencil-final-referee/check_robustness.py
```

The first command needs NumPy for decoding; the second is standard-library
only. The bundled Python path used for this run is in resource accounting,
not embedded as a replay dependency. The local commit containing this
report, outputs, scripts, and pins is the frozen referee handoff; its full
SHA is returned to the coordinator separately to avoid a self-referential
commit hash in these files.
