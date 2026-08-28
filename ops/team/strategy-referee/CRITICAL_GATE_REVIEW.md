# Independent referee review: skeleton missed-component critical gate

## Verdict

**ACCEPT**, at exactly the stated one-wall semialgebraic-reduction scope.

The theorem in constructive-prover commit
`4063c3fbe9621c29985932dfbd2e3cf12d33b2c8` is logically sound: the
true-boundary barrier has an interior maximum on the closure of every strict-
parent wall component; the displayed rank-minor locus contains every such
maximum, including singular wall points; exact sampling of every connected
component of that critical locus gives finitely many representatives; and
paths from every representative to the source skeleton are equivalent to
all wall components meeting the skeleton.

This acceptance is not acceptance of row-2599 component coverage.  No
critical representatives or attachment paths were computed.  It is also not
acceptance of an order-two master-complex route: simultaneous-wall strata,
closure incidence, labels, and middle-rank replay remain outside the theorem.

## Reviewed object and digest

- Exact base: `ec362dba8a912bc4749c004641aee2da0a88dc05`.
- Constructive commit: `4063c3fbe9621c29985932dfbd2e3cf12d33b2c8`.
- Reviewed note:
  `ai/omreal/DIAG3_PAIR_SKELETON_MISSED_COMPONENT_CRITICAL_GATE.md`.
- Reviewed note SHA-256:
  `de5268ea4d1f837e82426ac6e1738582c83cd76836975128634bec99128a2000`.
- `git diff --check ec362db..4063c3f`: pass.

All seven declared repository input digests match the exact base, including
the segment cover
`19248dd148d1fd002931ed5f48197869dd42c68a513376e1a4d6941389bda307`
and compactification atlas
`956fbe7e5c7b1e04c8873ed9c0f3de9cb5420e3e06f1d5fae4c60f4e0571b364`.
The attached source-map digest also matches
`659a2818f409f01100bcb9886248c23767e65791fe1827ba29ab3a8a4ae093e1`.

## Quantifier audit

### 1. Parent cell and compact closure

Pass.  The proof defines `P` as the connected component containing the pinned
sample, not merely the possibly disconnected strict sign realization.  Its
closure is taken in the compact product `X=(Delta^3)^3`.  The atlas verifies
that every one of the twelve product-simplex coordinate divisors is a named
row-2599 parent-bracket divisor.  If a limit point of `P` retained all seventy
strict inequalities, it would remain in the same connected component of the
strict sign set.  Therefore

```text
bar(P) minus P subset union_I {H_I=0}.
```

No artificial edge, collar, or box boundary is introduced.

Implementation warning already present in the candidate: `x in P` is not
certified by the seventy signs alone if their realization set is
disconnected.  Every future sampler must carry an exact roadmap/path tag to
the pinned sample.

### 2. Barrier signs, including coordinate divisors

Pass.  For `B=product_I H_I`, every factor is strictly positive on `P`, so
`B>0` there.  Every point of the true boundary zeros at least one parent
factor, including product-simplex coordinate and affine-chart-infinity
divisors, so `B=0` there.  Boundary factors not used as coordinate divisors
cause no problem; the product may vanish on a larger part of the true parent
boundary, which is exactly what the maximum argument needs.

The proposed active-margin implementation is not yet a certificate.  It must
encode all active-factor and tie strata explicitly; the statement that an
auxiliary minimum variable can avoid expanding the product is an admissible
design note, not a completed proof artifact.

### 3. Component closure and the interior maximum

Pass.  A connected component `C` of the semialgebraic set
`W_f=P intersect {f=0}` is closed in `W_f`, and `W_f` is closed in `P`.
Consequently

```text
closure_X(C) intersect P = C.
```

Its closure is compact in `bar(P)`.  The barrier is positive at every point
of `C` and zero on `closure(C) minus C`, so its positive maximum is attained
at a point of `C`.  This covers compact interior components and components
whose closures reach any true parent or coordinate-divisor boundary.

At a smooth maximizing point, the component is locally open in the smooth
wall (semialgebraic sets are locally connected), so the ordinary constrained
Lagrange condition applies.  The candidate should state this one local-
openness sentence if edited later, but its omission is not a logical defect.

### 4. Lagrange rank-minor formulation

Pass.  The three gradients `dG_6,dG_7,dG_8` are independent.  At a smooth
wall point relative to their affine hull, adding `df` gives constraint rank
four.  The condition

```text
dB in span(dG_6,dG_7,dG_8,df)
```

is therefore equivalent to rank at most four for the five-row Jacobian, or
the vanishing of all `5 x 5` minors.  The theorem does not incorrectly claim
that this critical ideal is zero-dimensional.

### 5. Singular-wall inclusion and multiplicity

Pass.  At an intrinsic singular point of the wall relative to the affine
hull, `df` lies in the span of the three `dG` rows, so the first four rows
have rank at most three.  Adding `dB` has rank at most four, forcing all
displayed minors to vanish.  Thus the singular locus is included rather than
saturated away.

Primitivity does not imply squarefreeness, but the proof remains correct for
a repeated wall: its singular locus may be large, yet semialgebraic component
sampling is still finite at the component level.  No unstated irreducibility
or generic smoothness hypothesis is being used.

### 6. Finite semialgebraic component sampling

Pass as an existence reduction, not as an executed computation.  A
semialgebraic set over `Q` has finitely many connected components; those
components are semialgebraic and contain exact real-algebraic sample points.
Sampling one point from each connected component of `Crit_B(f)` is sufficient
even if the critical locus is positive-dimensional.  Every critical
component is connected inside `W_f` and therefore lies in one wall component;
every wall component contains at least one critical component by the barrier
argument.

No sampler, Thom encoding, RUR, CAD, or roadmap certificate is present in the
commit.  Accordingly the note's classification as a proved *reduction* is
acceptable, while any claim that factor 19069 or all 17,824 factors have been
sampled would be false.

### 7. Representative attachments versus wall coverage

Pass.  If every wall component meets `S`, semialgebraic path connectedness
joins every representative in that component to `S` inside `W_f`.
Conversely, every wall component contains a representative, and a path in
`W_f` cannot leave its connected component, so paths from all representatives
to `S` force every wall component to meet `S`.

The universal quantifier over representatives matters.  Attaching only one
selected representative, or one representative per primitive factor without
proving the critical-component partition, would not meet the theorem's
contract.

### 8. Path connectedness and positive distance

Pass.  Connected semialgebraic sets are semialgebraically path connected.
For a component `C` disjoint from the compact skeleton `S subset P`, distance
zero would give a sequence in `C` converging to a point of `S`.  Equation
`closure(C) intersect P=C` would put that point in `C`, a contradiction.
Thus the stated positive-distance conclusion is valid even when `C` itself
is noncompact in the ambient affine chart.

## Hostile-canary replay

| prior canary | review result |
| --- | --- |
| compact sphere / cylinder | pass; the candidate's smooth irreducible cylinder proves raw nearest-point KKT can be positive-dimensional and is not assumed finite as a point set |
| boundary-to-boundary wall missing a parallel skeleton | pass logically; the barrier still has an interior maximum, so “no projection critical point implies coverage” is never asserted |
| irreducible disconnected real wall | pass logically; the theorem quantifies over every connected component, not every polynomial |
| cusp, isolated singular point, or singular branch | pass; singular points satisfy the rank-minor equations automatically |
| repeated wall | pass at the theorem level; large singular loci are handled by component sampling, not discarded |
| individually anchored walls with a missed wall-pair intersection | outside scope and explicitly still open; this theorem must not be promoted to order-two coverage |
| artificial-infinity transverse-node canary | pass at the stated scope; only `bar(P) minus P` is true boundary, while skeleton endpoints and collar/box faces remain ordinary |
| pointwise first-exit discontinuity | not invoked; the proof uses global barrier maxima or complete stratified distance systems, not a pointwise exit family |

## Defects and required scope guards

No blocking mathematical defect was found.  The following are non-blocking
but should be resolved before publication or implementation.

1. **Citation/dependency gap.**  The attached source map's cited
   Basu--Pollack--Roy paper `arXiv:math/0603256` concerns component-count
   bounds.  It is not, by itself, the precise source for all facts invoked
   here: compatible finite semialgebraic Whitney stratifications, exact
   algebraic sampling of each connected component, and semialgebraic path
   connectedness.  The handoff field `unused_or_missing: none` is too strong.
   Add a precise primary reference such as the relevant theorems in
   Basu--Pollack--Roy, *Algorithms in Real Algebraic Geometry*, or
   Bochnak--Coste--Roy, *Real Algebraic Geometry*.
2. **No executable completeness certificate.**  The theorem proves that a
   finite representative set exists, but neither computes it nor bounds its
   practical size.  This is correctly listed as an open defect and must
   remain visible.
3. **Nearest-skeleton Section 4 is only a candidate-generator reduction.**
   Sampling its stratified critical systems does not itself prove attachment;
   exact paths to `S` or explicit unattached residues are still required.
4. **One-wall scope only.**  The codimension-two hostile canary remains
   unanswered.  Before this gate can feed a labelled master complex, it must
   be extended to every feasible simultaneous-wall stratum through order two,
   with exact emptiness certificates for exclusions and true-frontier closure
   incidence.
5. **No factor-universe promotion.**  The theorem is parameterized by one
   polynomial.  It neither classifies the 5,803 feasibility residue nor
   supplies representative samples for the 10,844 known-crossed factors.

## Accepted scope

The accepted result is:

> For one nonzero rational full-support residual polynomial on the connected
> strict row-2599 parent cell, the barrier critical locus meets every
> semialgebraically connected wall component.  One exact sample from each
> connected component of that critical locus gives a finite representative
> set, and all wall components meet the retained segment union exactly when
> every representative has a path inside the wall to that union.

The accepted non-consequence is equally important: this commit does not prove
that even one global row-2599 wall component meets the skeleton, does not
produce a component-coverage counterexample, does not construct the
coverage-certified order-two master poset, and does not affect either open
diagonal-three invariant or the honest `2/9` ledger.

## Signed amendment delta review

**Verdict: ACCEPT -- NO CLAIM DRIFT.**

- Review date: `2026-08-28`.
- Reviewer track: `cycle-20260828-verifier-strategy`.
- Exact base remains:
  `ec362dba8a912bc4749c004641aee2da0a88dc05`.
- Previously accepted proof SHA-256:
  `de5268ea4d1f837e82426ac6e1738582c83cd76836975128634bec99128a2000`.
- Amended proof SHA-256:
  `9e4ba87acf73c1ca556e830fd687c9ca0ebad52366b82484c302ae4b282684e0`.

I compared the amended note directly with constructive-prover commit
`4063c3fbe9621c29985932dfbd2e3cf12d33b2c8`.  The mathematical amendment is
limited to the local-openness sentence requested in Section 3 of this review.
It makes explicit why a maximum on the connected wall component gives the
ordinary constrained critical-point condition on the smooth wall; it changes
neither a hypothesis nor a conclusion.

The remaining amendment is dependency accounting: Basu--Pollack--Roy,
Theorems 5.21--5.23, Algorithm 13.11, and Section 5.5 are now identified for
finite semialgebraic components, connected/path-connected equivalence, exact
component sampling for realizable sign conditions, and the optional smooth
stratification formulation.  These citations match the stated uses and close
the prior non-blocking citation gap.  Section renumbering and the revised input
accounting are editorial only.

No definition of `P`, `B`, `Crit_B(f)`, `S`, or `W_f` changed.  No universal or
existential quantifier changed.  The one-wall scope, representative-attachment
equivalence, and all non-consequences remain exactly as accepted above.

Signed-referee-verdict:
`ACCEPT_DELTA_NO_CLAIM_DRIFT/cycle-20260828-verifier-strategy/2026-08-28`.
