# Diagonal-three research decision — 2026-08-22

## Decision

Stop further dyadic refinement of the chart-0/chart-152 source staircase.
Promote the ambient full-hybrid-cube component theorem, preserve the final
eight-box enlargement as a bounded yield certificate, and retire the proposed
universal-incidence theorem for this source family after an exact 5,390-factor
countercertificate.

The honest 9DVL score remains **2/9**.  Neither the pair nor triple invariant
obligation is closed.

## Why the target changed

The five-box staircase occupied exact normalized volume `373/512`, classified
all 89,120 box-factor restrictions, and attached every component to a union of
box boundaries.  Its two weaknesses were:

1. internal seams remained in the declared skeleton; and
2. increasing source volume did not by itself show that every component in the
   nine-dimensional parent cell meets the source family.

A proposed 16-slab refinement was simplified before promotion.  Once the
full `w` interval becomes parent-safe at `u=7/16`, the final nine slabs merge
into one box.  The resulting eight-box object has the same exact volume with
half the factor-restriction workload and eight fewer artificial seams.

Exact replay gives volume `12817/16384`, an increase of `881/16384` over the
five-box staircase.  It finds 5,139 distinct occurring factors, only 33 more
than the previous 5,106.  That is a decisive low-yield result: another dyadic
height layer would optimize a sufficient local reduction while leaving the
invariant global incidence obstruction unchanged.

## Ambient topology pivot

The full hybrid cube is not parent-resident, but parent residence is not
needed to study the topology of the residual polynomials restricted to that
cube.  The exact ambient certificate decides all 17,824 restrictions:

| class | count |
|---|---:|
| zero-free | 12,247 |
| occurring | 5,577 |
| unresolved | 0 |

Graph projection covers 4,898 occurring restrictions.  Adaptive exact
critical systems cover all 679 fully triquadratic restrictions.  Therefore
every occurring full-cube zero-set component meets the cube boundary.

The semialgebraic path-transfer lemma converts this into the missing scope
upgrade for any closed parent-safe source staircase inside the cube: every
component of the restricted wall inside the staircase meets its **true outer
boundary**.  A component avoiding that boundary would lie in the staircase
interior; a path in its ambient full-cube component to the cube boundary would
have to cross the staircase boundary first, a contradiction.

This eliminates internal seams from the source-family theorem.  It does not
show that every global row-2599 wall component meets the source family.

## Universal source incidence refuted

The final falsification check compares the 10,844 factors with exact sign
crossings on 105 certified parent-safe segments against the 5,577 factors
occurring anywhere on the full chart-0/chart-152 source cube.  Exactly 5,454
belong to both sets.  The other **5,390 known parent-interior walls are
zero-free on the entire source cube**.

Factor 5 is the least counterexample: it has opposite exact signs at charts 0
and 2 on a parent-safe segment, while its source-cube Bernstein net is
one-signed at depth zero.  The complete 5,390-factor no-go set has semantic
digest

```text
26cce16d217d55e01081dad817d13778d2c797724659bcebd51555eb66855382
```

Therefore no refinement confined to this hybrid cube can prove that every
global wall component meets the source family.  This is a mathematical
refutation of the proposed sufficient lemma, not merely a low-yield heuristic.
See `DIAG3_PAIR_SOURCE_FAMILY_INCIDENCE_NO_GO.md`.

## Methods result

The reusable research machinery is now a first-class artifact rather than
duplicated implementation detail.  `exact_semialgebraic/` exposes exact
sparse-polynomial affine pullback, canonical integer normalization,
arbitrary-dimensional tensor and simplex Bernstein subdivision, fail-closed
zero-set and system exclusion, and adaptive critical axes.

The analytic canary certificate now exercises tensor boxes and rational
simplices: positive and crossing examples, a subdivision-required circle, a
noncompact 3D zero set whose critical system is empty, and box/tetrahedron
interior spheres whose compact components must remain unresolved.  Ten
hostile semantic mutations are rejected.  The existing source-cube producer
and the first-four-support producer reuse this package; independent verifiers
continue to use separately written logic.

See `EXACT_SEMIALGEBRAIC_CERTIFICATE_METHOD.md` for the complete reusable
procedure and trust-boundary rules.

## Direct four-support checkpoint

The direct roadmap route now has its first coverage-bearing higher-support
result. Opposite signed parent inequalities collapse supports `(3,1,15)` and
`(3,3,7)` from nominal dimension four to the same three-dimensional square
pyramid `0<=g<=a<=1`, `0<=g<=h<=1`. Two rational tetrahedra cover each parent
domain exactly and inherit the completed `(3,1,5)` base. Exact classification
reduces 8,017 mixed restrictions to 94 parent-reduced zero sets and 22 active
interior walls, with no unresolved classes.

The first complete fiber projection then yields one base-only, 20 linear, and
one quadratic wall. Its 255 exact projection obligations quotient to 136
distinct `(u,t)` polynomials of maximum bidegree `(4,5)`, below the pinned
100,000-polynomial ceiling. This validates the architecture but does not yet
construct the base CAD, lifted cells, or global closure complex. See
`DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_GATE.md` and
`DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_PROJECTION.md`.

## Next proof-bearing target

The pair branch now needs one of the following, in priority order:

1. an exact sign-invariant CAD or equivalent roadmap for the 136
   boundary-reduced base polynomials, followed by exact lifting of the 22
   degree-at-most-two fibers and face-compatible gluing of both covered
   square-pyramid supports;
2. a bounded collection of genuinely distinct source families together with
   an exact global incidence theorem for their union; or
3. a different structural reduction that replaces source incidence and
   directly yields the global labelled relative master complex.

Further staircase refinement inside the chart-0/chart-152 cube is retired for
global incidence.  It should be revived only for a different local theorem
whose load-bearing quantity is source volume itself.

The independent triple branch remains unchanged at 1,162,302 unresolved
source orbits.  Its next admissible route remains a boundary-complete
projection-critical or semialgebraic roadmap certificate, not a wider search
in either of the two exhausted algebraic-action languages.
