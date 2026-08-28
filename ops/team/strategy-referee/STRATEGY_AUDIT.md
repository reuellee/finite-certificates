# Independent strategy audit: cycle-20260828-verifier-strategy

## Mandate and independence

- Exact audited base: `ec362dba8a912bc4749c004641aee2da0a88dc05`.
- Track: `cycle-20260828-verifier-strategy`.
- Classification: independent strategy review, not a proof and not a
  discovery-side implementation.
- The obligation graph and route ranking below were reconstructed from the
  pinned base before reading any conclusion from another new track.
- No theorem ledger, claim surface, CI file, proof artifact, or producer was
  edited by this track.

## Base and authentication checks

The exact local base is the merge of PR #38:

```text
commit ec362dba8a912bc4749c004641aee2da0a88dc05
tree   c0e742cbe59bd93f495413363b6341e90c883ea0
left   e8600495e70e6f5548cb0c73e0cfd2f33faacc0b
right  2ac0484c1c62ae4337ec0cb2ee6442f709a79cba
```

The GitHub connector independently reports that PR #38 is merged at this
commit, has 29 changed files, and is scoped to edge 39, its exact label
continuation, the edge-27/edge-39 tree, the factor-19069 collar attachment,
standalone verifiers, CI routing, cycle documentation, and the fail-closed
ledger update.  It explicitly claims no component coverage, parent-cell
coverage, pair injectivity, triple noncompactness, or score promotion.

The relevant byte and semantic pins at the audited base are:

| object | authenticated value |
| --- | --- |
| current decision-ledger raw SHA-256 | `7922d769aa30a84c5d208dec92d2e78d5c7744cc6184ea1d42aaeadf947761b3` |
| current decision-ledger Git blob | `6f1c5de236de42c1b0e254943a7d9350e5caf995` |
| pre-PR-38 ledger authenticated by the edge-39 producer | `b87172fb14dc440270436a440468ab4843939e7ac2894ecb266342c63a9025f0` |
| optimal 40-edge cover raw SHA-256 | `19248dd148d1fd002931ed5f48197869dd42c68a513376e1a4d6941389bda307` |
| optimal-cover semantic SHA-256 | `8b7f3ae29406f8b4476c38e4932c7e0016f78856a6dee083ce2db93332c2583c` |
| first labelled skeleton raw SHA-256 | `5430bd79ae9ddee09ce9b393f018389be1210c250a7eb0d5486fab8e1294663d` |
| factor-19069 collar raw SHA-256 | `5930cc19019470fdfdf55d67523f6c4211ccf5b540f5c2bb5df36c64db75d7bd` |
| edge-39 transition / labels / packed profiles | `cb6eebc0df9bfeae8055c81471f09d594f8116e002caf11f62f9e865b0936dd7` / `dc80acaf2f711ee5e0e053e856e4abf858adf90483ba0e5ced13018bdb909170` / `77b042d72e4c28dc5e60145624adfd27b080aaec8aa757cdf10c0d7c5513e6b6` |
| combined tree / packed profiles raw SHA-256 | `dcb707220df3e61b1a94eeedcf8e46b6602f30d405f4a92fc542c0f52f672806` / `cbc8b02f7c4f6840ee267d56403b11a36722291216a69eb0de04d0084627cd1d` |
| combined tree semantic SHA-256 | `c6cfc9fdbe7002add59342d300b701e771fc331db698886636bdeea5392a5ae3` |
| external research-source map SHA-256 | `659a2818f409f01100bcb9886248c23767e65791fe1827ba29ab3a8a4ae093e1` |

The canonical ledger verifier, optimal-cover verifier, and standalone
combined-skeleton verifier pass.  The latter reconstructs `V=6,567`,
`E=6,566`, `rank(d1)=6,566`, `H0=1`, `H1=0`, all 97,224 joint signature
columns, factor-19069 event 5,236, collar orientation `+1`, and nine hostile
rejections.  These checks authenticate the local result and its narrow scope;
they do not upgrade it to global coverage.

One bookkeeping distinction matters.  The current ledger bytes include the
PR-38 layer, while the ledger's self-described `repository.audited_commit`
still names the PR-37 base.  That is compatible with avoiding a self-hash
cycle, but downstream consumers must not confuse the pre-cycle raw ledger
pin `b871...` with the current raw ledger `7922...`.

## Reconstructed obligation graph

Diagonal three can be promoted only when both independent invariant
obligations are closed.

1. **Triple `H_c^0`.**  For every triple source, exclude compact connected
   components of `B0 intersect B1 intersect B2`.  The exact accounting is
   `79,102,449 - 77,940,147 = 1,162,302` unresolved orbits.  The current
   full-space canary proves only that every component inside one rational
   radius-`1/128` nine-box reaches that box's artificial boundary.  It does
   not attach those components to genuine parent infinity or close one orbit.
2. **Pair `H_c^1`.**  Prove injectivity of the alternating pair-to-triple
   restriction map.  The route in use requires a coverage-certified relative
   master closure complex, complete signature labels, comparable cell pairs
   and strict three-chains, genuine parent-infinity tags, and the final
   profile-triple mod-two rank replay.  Integral signs and `MN=0` then follow
   canonically from the regular closure poset.

For the row-2599 pair pilot, the active full-support inventory is:

```text
17,824 candidate factors
10,844 proved interior-nonempty
 1,177 proved empty
 5,803 feasibility-unresolved
16,647 active-wall upper bound
```

All 3,374 proper supports are relative.  The only possibly nonrelative
support is `(15,15,15)`.  Consequently the 16,935,101-cell local lift over
the first two proper four-support domains is a valuable compiler regression,
but not a source of nonrelative chain generators.

The pair dependency chain is therefore:

```text
complete compactified full-support coverage
  -> wall and simultaneous-wall strata through order two
  -> all 97,224 bad-signature labels and genuine frontier tags
  -> regular closure pairs and strict three-chains
  -> T and exclusive-pair relative complexes
  -> rank_F2(N) + rank_F2(M) = dim(C1)
```

Wall-component incidence with a finite source graph is, at most, an input to
the first two arrows.  It is not a substitute for them.

## Quantitative audit of the 40-edge skeleton

The selected cover has 40 straight edges on 48 stored charts.  Its graph is
not one tree: it is a forest with eight connected components of vertex sizes

```text
19, 10, 8, 3, 2, 2, 2, 2.
```

It has cycle rank zero.  Completing every edge can therefore produce only a
subdivided eight-component forest: no two-cells, no simultaneous-wall face
incidence, no genuine parent frontier, and no global first-homology filling
data.

The 40 edges contain 157,448 exact opposite-endpoint factor incidences.
Edges 27 and 39 account for 1,197 and 5,091 respectively, leaving a hard
lower bound of **151,160 odd root events** on the other 38 edges.  The two
compiled edges contain 6,564 actual events versus 6,288 endpoint incidences,
an even-root overhead of `276/6,288 = 4.39%`.  If that rate were typical, the
remaining paths would contain about **157,795 events**, and the complete
forest about **164,359 events**.  This is an estimate, not a certificate;
the 151,160 lower bound is exact.  The retained-edge endpoint counts range
from 1,197 to 5,232, with median 4,035.

The two compiled edges required 6,213 simple mutations and 351 exact compound
re-enumerations.  Extrapolation would put the remaining compound-event load
on the order of 8,000.  Even successful completion leaves the topological
deficits above unchanged.

## Ranking of the three proposed routes

### 1. Stratified coverage-or-counterexample gate for the source skeleton

**Verdict: conditional accept as the next bounded main cycle; reject as a
standalone pair proof.**

This route has the highest immediate decision value.  One exact missed
component retires bulk edge compilation and saves at least 151,160 event
continuations.  A positive certificate would establish the missing reason
to keep the skeleton as an anchor.  The accepted statement must be no weaker
than:

> Every connected component of every in-scope wall or simultaneous-wall
> stratum either meets the exact selected segment union or has a certified
> attachment to a named genuine parent/compactification frontier.

For wall components alone, the route is necessary but insufficient.  Pair
middle exactness also depends on codimension-two intersections and on their
closure/frontier incidence.  A theorem covering the 10,844 already-crossed
walls but ignoring the 5,803 feasibility-unknown factors is also
insufficient.  Those factors must be proved empty or included.

The most promising exact formulation is a **stratified distance-to-skeleton
KKT certificate**.  Compactify first.  On every wall or wall-pair stratum,
any interior component disjoint from both the finite segment union and the
genuine frontier has a positive minimum distance to that union.  Split the
nearest-point problem into the 40 segment-interior strata and their endpoint
strata.  Exact KKT/rank systems then enumerate all possible missed-component
minima.  Every saturation factor must be attached to a named parent wall,
chart divisor, rank-drop stratum, extra residual factor, or infinity face.
This avoids treating a nonsmooth global `min` distance as a polynomial and
turns coverage into finite falsifiable systems.

The first cycle should use three preregistered canaries:

- factor 19069 on edge 39 as the authenticated positive-control collar;
- factor 17405, the unique mandatory witness forcing non-chart-zero edge 83
  `(2,3)`, as a generic-source control; and
- one maximum-complexity member of the 5,803 feasibility residue, selected by
  a fixed `(degree, term count, factor id)` rule, as the scope-completeness
  control.

It should also include one transverse wall-pair fixture.  Success is either
an exact missed-component certificate or a complete KKT/frontier partition
for all registered canaries, independently replayed.  Neither outcome may
promote the theorem score.

### 2. Direct coverage-certified parent-cell master roadmap

**Verdict: accept as the theorem-complete fallback and likely eventual pair
route, but enter it through bounded order-two canaries rather than a raw
nine-dimensional CAD.**

This is the only proposed route whose stated endpoint directly supplies the
pair invariant.  Its naive scale is prohibitive: 16,647 active-wall
candidates have 138,552,981 unordered wall pairs before feasibility and
incidence pruning.  Existing exact local compilers prove the schema is real
(17-, 81-, and 399-cell two-dimensional fixtures), but they do not remove
the global nine-dimensional coverage problem.

The viable architecture is a hybrid of this route with route 1: use the
stratified KKT gate as a lazy, proof-producing incidence oracle; materialize
only witnessed wall and wall-pair strata; certify every excluded stratum by
exact emptiness; then emit the labelled order-two closure object directly.
The source skeleton becomes an anchor set, not a claimed deformation retract.
If route 1 finds a missed component, add it as a new roadmap anchor rather
than discarding the master-roadmap architecture.

### 3. Compile the remaining 38 retained edges

**Verdict: reject as the main research route; retain only as demand-driven
infrastructure.**

This route is exact and comparatively low-risk, but it has the weakest
theorem leverage.  It spends at least 151,160 further root events to produce
an eight-component one-dimensional forest with no two-cells.  It neither
tests the missed-component premise nor supplies the order-two closure data
that the pair differential consumes.  The first two edges already validate
the one-dimensional compiler and compound label continuation.

Further edge compilation is justified only when a coverage certificate needs
a specific edge or when parameterizing the compiler on one generic edge is
required to remove a software bottleneck.  Edge 83 is the best such generic
fixture: it is non-chart-zero, has the largest selected endpoint incidence
count (5,232), and is forced by unique factor 17405.  Do not launch 38
independent edge cycles before the coverage gate.

## Fatal quantifier gaps to reject

Any of the following invalidates a claimed coverage theorem or its use in the
pair proof:

1. Replacing “every connected component” by “at least one zero per primitive
   factor.”
2. Covering only the 10,844 known-crossed factors while omitting the 5,803
   feasibility residue.
3. Proving that wall components meet an artificial box boundary and calling
   that parent infinity.
4. Saturating away parent, chart, rank-drop, extra-factor, denominator, or
   singular components without explicit attachments.
5. Using smooth Lagrange equations without the intrinsic singular locus.
6. Proving individual-wall coverage but omitting simultaneous-wall strata.
7. Inferring a global regular closure poset, or two-cell incidence, from a
   one-dimensional source forest.
8. Treating endpoint Hamming distance as a root roadmap.  Edge 39 already
   shows 118 two-root factors and 236 invisible crossings.
9. Treating a pointwise exit from each fiber as a proper family; first-exit
   endpoints can jump and create ordinary frontier.
10. Treating all eight graph components as one source complex or identifying
    their endpoints without an exact geometric gluing.

## Hostile canaries for a critical-point theorem

Every proposed critical/KKT implementation should reject or correctly
classify these before touching a global claim.

1. **Compact sphere.**  `f=x^2+y^2-1` with a disjoint skeleton.  A missed
   compact component must create a critical/KKT witness.
2. **Boundary-to-boundary miss.**  In a square, `f=y` and a parallel skeleton
   at `y=1/2`.  The wall has no relevant interior projection critical point,
   reaches artificial boundary, and still misses the skeleton.  This forbids
   “no critical point implies skeleton coverage.”
3. **Irreducible disconnected wall.**  `f=xy-1` in a sufficiently large box,
   with the skeleton meeting only the positive branch.  One primitive
   polynomial can have multiple real components.
4. **Singular component.**  `f=y^2-x^3` and the isolated real set
   `f=x^2+y^2`.  Smooth KKT equations alone are incomplete.
5. **Repeated wall.**  `(x^2+y^2-1)^2`.  Squarefree reduction and multiplicity
   accounting must be explicit.
6. **Codimension-two miss.**  Let `f=x`, `g=y`; choose one skeleton segment
   that meets `f=0` away from `(0,0)` and another that meets `g=0` away from
   `(0,0)`.  Both walls are individually anchored while their intersection
   is not.  This rejects promotion from wall coverage to order-two coverage.
7. **Artificial-infinity rank canary.**  Reuse the repository's transverse
   node: tagging its outer scope cycle relative leaves 48 nonexact local
   profile triples, while retaining it as ordinary boundary makes the closed
   disk exact.  Boundary tags must materially affect replay.
8. **Pointwise first-exit canary.**  Reuse the stored rectangle model whose
   terminal endpoint jumps; its ambient closure has relative `H1=Q`.
   Fiberwise interval exits do not imply a proper global collar.

## Exact stop rules

### Pair coverage-or-counterexample cycle

Stop with a useful negative result on the first of:

- an exact component or order-two stratum disjoint from both the selected
  segment union and every genuine frontier;
- a registered saturation factor with no certified attachment;
- a positive-dimensional critical residue after the declared stratification;
- a hostile canary accepted incorrectly;
- a need to call an artificial box face parent infinity;
- the declared resource ceiling without a finite replayable object.

Stop with a bounded positive result only when the exact KKT/source/frontier
partition for all preregistered canaries is complete, all singular and tie
strata are included, and a separate verifier reconstructs it.  Do not infer
global coverage from that bounded result.

### Direct master-roadmap route

Require an order-two schema from the start.  Stop or redesign if a pilot
stores only wall points/paths, if excluded wall pairs lack exact emptiness
certificates, if any closure face lacks a unique ordinary/relative tag, or if
the emitted poset fails regularity, closed-bad-subcomplex, `d^2=0`, or the
hostile node canary.  The smallest success object is one coverage-certified
full-dimensional box atlas with complete wall and wall-pair strata, labels,
and genuine/artificial boundary separation—not another isolated path.

### Edge compiler

Compile at most one additional generic edge before the coverage decision.
Stop on the first exact endpoint root, repeated event, coincident-factor group
unsupported by the schema, parent-residence failure, or unbounded compound
re-enumeration.  A pass changes infrastructure readiness only.

## Parallel triple roadmap obligation

The triple branch must continue independently; no pair certificate can cancel
it.  The current local projection canary has a 147-term Jacobian pivot that is
strictly negative on one radius-`1/128` nine-box, but all 18 terminal faces are
artificial.  The next bounded, proof-producing triple cycle should construct
an **adaptive pivot-box chain** for the same preregistered hard presentation
`(5563,16134,19284)`:

1. Cover adjacent boxes by one of the 84 residual `3x3` Jacobian minors with
   exact interval sign.
2. Glue shared faces literally and retain all 70 parent signs.
3. Where no pivot is sign-definite, insert a projection-critical box and
   retain singular, rank, denominator, extra-factor, and chart strata.
4. Continue until every terminal face is a named genuine parent/chart/infinity
   face or an exact obstruction is found.
5. Only after one orbit is boundary-complete, attempt compression across the
   1,162,302-row residue using a proved feature signature and full stabilizer
   and `S8` transport accounting.

Preregister a finite box/term/resource ceiling.  Publication success is one
complete orbit roadmap with no artificial terminal face, or an exact finite
obstruction explaining why the pivot atlas cannot close.  A longer chain of
boxes ending on artificial faces is not a theorem advance.

The separate rational-Nullstellensatz target from the height-`b` gate remains
valid as an alternative canary: certify

```text
U0^m ([1468][5678])^n = sum_j A_j g_j
```

with every integer term independently replayed.  Previous bounded F4 runs
reached degree 14--16 without a unit identity, so the adaptive roadmap should
be preferred unless a new sparse reconstruction lowers that frontier.

## Smallest publication-worthy coordinated cycle

The smallest honest coordinated cycle has two products:

1. **Pair:** a preregistered stratified distance-to-skeleton KKT gate on
   factors 19069, 17405, one deterministically selected 5,803-residue factor,
   and one transverse wall pair, yielding either an exact counterexample or a
   complete bounded frontier partition.
2. **Triple:** a preregistered adaptive pivot-box extension of the existing
   hard canary, ending either at genuine frontier or at an exact obstruction.

This cycle is publication-worthy even if both results are negative, because
it decides whether the source skeleton can anchor a coverage theorem and
whether the local triple pivot can scale past artificial boundary.  It does
not change the `2/9` ledger unless, in a later global cycle, both invariant
obligations pass their complete independent gates.

## Final recommendation

Adopt the coverage-or-counterexample cycle as a **falsification-first gate**,
not as a claimed shortcut to pair injectivity.  Preserve the direct master
roadmap as the theorem-complete architecture and feed it new anchors whenever
the gate finds missed components.  Subordinate bulk edge compilation until
this decision is made.  In parallel, extend the triple canary only through a
boundary-complete adaptive roadmap or exact obstruction.

If no critical system on the registered canaries finishes within the bounded
cycle, the useful null is still decisive: the 40-edge skeleton has no proved
coverage advantage over a generic anchor set, while its full compilation has
an exact 151,160-event lower bound.  Under that null, switch pair effort to a
direct order-two master-roadmap canary rather than compiling the remaining
edges.
