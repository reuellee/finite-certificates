# Row-2599 pair-coverage architecture audit

## Scope and pinned state

This audit is theory/literature reconnaissance at repository revision
`ec362dba8a912bc4749c004641aee2da0a88dc05`.  It proposes no ledger change.
The theorem score remains `2/9`.  The diagonal-three promotion rule still
requires both the pair `H_c^1` injectivity obligation and the independent
triple `H_c^0` obligation.

The exact source-cover certificate has a sharper negative implication than
its 40-edge optimum statement alone suggests.  Its 40 selected chart pairs
form a forest on 48 stored charts with eight connected components, component
sizes

```text
19, 10, 8, 3, 2, 2, 2, 2.
```

Thus its cycle rank is zero and 130 of the 178 stored charts do not occur.
Compiling the remaining 38 selected paths would produce more exact labelled
one-dimensional trees, but by itself it cannot produce a two-cell, a strict
closure three-chain, a parent-cell coverage proof, or a wall-component
coverage proof.  This is a reason to stop treating `38 edges remaining` as
the primary workload measure.

## Selected architecture: profile-universal order-two Hardt--Mayer--Vietoris compiler

The proposed endpoint is weaker than a full sign-invariant arrangement and
stronger than a roadmap graph.  Construct a finite contractible
semialgebraic cover, compatible with genuine parent infinity and all bad-locus
labels, only to the depth needed for the balanced pair complex.  Retain:

1. cover-piece components;
2. components of pairwise and triple intersections;
3. their specialization/incidence maps; and
4. the signature-to-membership-profile map.

Then form the truncated Mayer--Vietoris double complex and run the existing
mod-two middle-rank test.  Projection-critical/Hardt strata are generator
data, not a license to infer coverage.  A roadmap supplies component
connectivity; the pair/triple intersection incidences supply the missing
first-homology information.

### Exact new lemma required

> **Profile-universal order-two cover lemma.**  Let `P` be the compactified
> row-2599 full-support parent cell, `P_infinity` its genuine relative
> frontier, and `B_rho` the closed bad loci of all 97,224 signatures.  There
> is a finite closed semialgebraic cover `U`, subordinate simultaneously to
> `P_infinity` and all `B_rho`, such that the cover pieces are contractible
> and the connected-component incidence diagram of cover pieces, pairwise
> intersections, and triple intersections is naturally chain-equivalent
> through total degree one to the barycentric balanced pair complex for every
> ordered membership-profile triple.

The existence of a semialgebraic triangulation is not enough.  The required
lemma includes an exact finite generator, complete component coverage,
specialization at critical values, the relative-infinity quotient, and
naturality across profiles.  Its payoff is that no complete high-dimensional
cellulation and no arbitrary 40-edge continuation are required.

### Why the recorded no-go results do not kill it

- The component-cosheaf pilot failed because it was given local lift
  manifests without global coverage or incidence.  The proposed lemma makes
  those fields its input contract; the cosheaf is only a post-coverage
  compiler.
- A one-dimensional roadmap does not determine `H_1`.  This architecture
  retains pair/triple intersection components and their incidence, following
  the degree-one Mayer--Vietoris construction.
- The pointwise first-exit counterexample is a Hardt-specialization failure.
  The proposed generator includes projection-critical values and every
  specialization map, rather than gluing pointwise exit intervals.
- All 3,374 proper supports collapse into the relative subspace.  The
  compiler works on full support `(15,15,15)` and carries internal parent
  frontiers as genuine relative faces.
- The chart-0/chart-152 source family misses 5,390 known parent-interior
  walls.  The proposed cover is parent-wide; source triangles are compiler
  canaries, not a claimed global hitting set.
- The 618,120 forced curve-pair intersections on one source square make full
  arrangement materialization unattractive.  Component/intersection
  incidence through order two is exactly the quotient this architecture
  seeks.

## Competing architectures

The score scale is 1--5.  High proof criticality and decisiveness are good;
high cost and failure risk are bad.

| architecture | exact new lemma needed | proof criticality | decisiveness | cost | failure risk | verdict |
|---|---|---:|---:|---:|---:|---|
| Profile-universal order-two Hardt--MV cover | The lemma stated above | 5 | 5 | 4 | 3 | **Selected**; it targets exactly the invariant degree-one group and has a useful local canary path |
| Full recursive block-fiber Hardt poset | Projecting `(Delta^3)^3` onto two moving-column blocks, a base stratification subordinate to all parent/residual discriminants plus a face-compatible constant fiber-poset and every specialization has a regular Grothendieck realization whose order-two closure poset equals the master quotient | 5 | 4 | 5 | 4 | Sound fallback, but it constructs substantially more than the truncated rank calculation needs |
| Oriented-matroid mutation-square 2-complex | Every full-support residual chamber is reached by the certified mutation graph, every wall component meets it, and all fundamental relations are generated by certified codimension-two diamonds carrying compatible signature labels | 4 | 3 | 3 | 5 | Deprioritize; mutation connectivity does not imply fixed-parent parameter coverage, the 40-edge forest has no 2-cells, and fixed triangular/partial-cube shortcuts already fail |
| Positive-Grassmannian/cluster network atlas | The row-2599 signed parent cell has a finite network atlas subordinate to all residual zero sets in which every required residual factor is a Laurent unit times a chart coordinate or controlled binomial and transitions extend across those divisors | 3 | 2 | 3 | 5 | Deprioritize; known positive-network parametrizations concern totally nonnegative Grassmannian cells, while the exact project audit already rules out a universal identification of residual types 49/50 with the tested `Gr(4,8)` cluster-variable families |

The second architecture is not killed by the pointwise-exit no-go because it
explicitly retains the discriminant strata where fiber topology changes.
It is nevertheless more expensive: it asks for a regular order-two master
poset before knowing which component incidences survive the truncated
Mayer--Vietoris quotient.

The mutation architecture is not rescued by Roudneff--Sturmfels mutation
connectivity.  That theorem concerns mutation connectivity in the realizable
uniform oriented-matroid setting; the missing claim here is coverage and
wall incidence inside one fixed nine-dimensional realization cell.  The
extension-space literature likewise does not supply the required
profile-labelled fixed-parent 2-complex.

The positive-atlas route is not mathematically impossible.  The exact
cluster audit leaves open higher Laurent rescalings and more general
birational words.  It currently lacks a route from those charts through the
residual divisors, which are precisely the cells the proof must retain.

## Bounded next experiment: a genuine two-cell on accepted edges 27 and 39

Use the normalized matrices `Y_0`, `Y_89`, and `Y_113` from the pinned point
bank and the barycentric triangle

```text
Y(s,t) = Y_0 + s (Y_89-Y_0) + t (Y_113-Y_0),
s >= 0, t >= 0, s+t <= 1.
```

Its two axes are exactly accepted source edges 27 (`0--89`) and 39
(`0--113`).  The experiment has a 45-minute ceiling and must not widen to a
different triangle.

### Exact exploratory preflight

These checks used rational arithmetic at the pinned revision but have not
received an independent verifier, so they are discovery evidence only.

- The naive affine square on the same two directions leaves the row-2599
  parent cell at its fourth corner; nine signed brackets are negative there:
  `[1278]`, `[1368]`, `[1467]`, `[2368]`, `[3468]`, `[3567]`, `[3568]`,
  `[3578]`, and `[3678]`.
- On the barycentric triangle, 69 of 70 signed parent brackets have strictly
  positive triangular Bernstein control nets without subdivision.
- The remaining bracket `[5678]` is strictly positive after one midpoint
  subdivision into four triangles.  Thus the triangle has a compact exact
  parent-residence proof candidate, unlike the square.
- A stopped reconnaissance prefix of 4,000 candidate factors at triangular
  Bernstein depth four classified 2,670 as zero-free and found exact
  rational sign witnesses for 1,329; one remained unresolved.  This prefix
  is not an artifact and is not accepted evidence.

### Formal 45-minute contract

1. Independently replay strict parent residence for all 70 brackets, with
   the `[5678]` four-subtriangle certificate as a canary.
2. Restrict all 17,824 candidate factors to the triangle.  Use adaptive
   triangular Bernstein certificates for zero-free restrictions and exact
   rational sign-changing segments for nonemptiness.
3. Compare every nonempty factor ID with the exact rooted-factor sets of
   edges 27 and 39.
4. Emit the sorted factor IDs that have a certified zero in the triangle
   interior but no zero on either compiled boundary edge, plus a residue
   digest for anything undecided at the ceiling.

**Positive stop:** at least one new interior factor is proved.  Then this is
the first objectively useful 2-cell attached to the labelled skeleton; the
next cycle computes its projection-critical component incidence and complete
signature labels.

**Null stop:** all triangle-nonempty factors already occur on edges 27 or 39.
This is useful: retire this fan triangle as a coverage expansion and do not
compile its full labels.

**Negative stop:** any parent bracket vanishes or changes sign after
independent replay.  Preserve the exact witness and retire affine
triangle-thickening for this edge pair.

**Timeout stop:** preserve exact decided/undecided factor lists and digests;
do not deepen subdivision or choose another edge pair in the same cycle.

The experiment is decisive about whether the first two compiled edges can be
turned into new two-dimensional incidence.  Success does not claim global
coverage, a wall-component theorem, pair injectivity, or diagonal three.

## Triple obligation and diagonal nine

Neither diversion is objectively better for the next cycle.

- The triple obligation is equally invariant and ultimately unavoidable for
  diagonal three, but the current exact source still contains 1,162,302
  unresolved factor triples.  Its hard-canary critical object has 59 formal
  equations, 14,681 terms across its nonzero minors, and positive-dimensional
  parent-boundary components before saturation.  That is readiness 2, cost
  5, failure risk 5.  Resume it when the pair compiler hits its declared
  resource stop or when a new structural lemma removes a positive fraction
  of the full residue.
- Diagonal nine has a clean connectivity formulation, and parent 860 lowers
  the candidate-factor upper bound from 17,824 to 16,420.  But it still has
  no full-dimensional parent roadmap; even family-adaptive row-2599 sectors
  retain roughly 3,500--3,700 active factors.  A pilot for one parent/family
  would not discharge the universal ninth diagonal.  It is therefore a good
  tool-development track, not the shortest route to `3/9`.

The selected order-two compiler has better cross-obligation leverage: its
component engine can later supply `H_c^0` data for triple intersections and
connectivity data for diagonal-nine active sectors.

## Primary-source accounting

- Basu, Pollack, and Roy, [*Computing the First Betti Number and Describing
  the Connected Components of Semi-algebraic Sets*](https://arxiv.org/abs/math/0603248).
  This is the primary support for computing first Betti number from a
  contractible semialgebraic cover together with components and incidences of
  pairwise and triple intersections.  It does not provide the project-specific
  profile-universal relative cover lemma.
- Basu and Roy, [*Divide and Conquer Roadmap for Algebraic Sets*](https://arxiv.org/abs/1305.3211).
  This supports projection-critical roadmap construction and prescribed-point
  inclusion.  A roadmap gives component connectivity, not the balanced pair
  `H_1` incidence by itself.
- Hardt, [*Semi-algebraic Local Triviality in Semi-algebraic Mappings*](https://doi.org/10.2307/2374240),
  *American Journal of Mathematics* 102 (1980), 291--302.  This supports
  finite semialgebraic trivialization across base strata.  It is an existence
  theorem, not an exact coverage certificate and not permission to omit
  critical-value specializations.
- Kishimoto and Yushima, [*Cellular cosheaf homology are cosheaf homology*](https://arxiv.org/abs/2202.03659).
  This supports cellular-cosheaf/Borel--Moore comparison on a supplied
  simplicial complex.  It does not construct the missing global cell complex.
- Roudneff and Sturmfels, [*Simplicial Cells in Arrangements and Mutations of
  Oriented Matroids*](https://doi.org/10.1007/BF00151346), *Geometriae
  Dedicata* 27 (1988), 153--170.  This is the primary mutation source; no
  fixed-parent residual-component coverage claim is imported from it.
- Sturmfels and Ziegler, [*Extension Spaces of Oriented Matroids*](https://doi.org/10.1007/BF02573961),
  *Discrete & Computational Geometry* 10 (1993), 23--45.  This informs the
  extension-space alternative but does not provide the required labelled
  realization-cell 2-complex.
- Postnikov, [*Total Positivity, Grassmannians, and Networks*](https://arxiv.org/abs/math/0609764).
  This supports network parametrizations and gluing of totally nonnegative
  Grassmannian cells.  Its scope does not establish the proposed cluster
  atlas for row 2599 or continuation through all residual zero divisors.

No secondary source is load-bearing in this audit.
