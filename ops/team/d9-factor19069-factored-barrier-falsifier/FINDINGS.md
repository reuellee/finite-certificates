# Factor-19069 factored-barrier falsifier findings

## Disposition

The frozen constructor frontier at revision
`2878addcc5d9c863ed5b2d518552b0298f08a64c`, tree
`3b6b3e563ca85782d76acfa0e3a48fc8aa031ec6`, survives independent
falsification only as the preregistered fail-closed null
`HASH_PINNED_FACTORED_BARRIER_CRITICAL_COMPONENT_FRONTIER_WITH_FIRST_UNSAMPLED_COMPONENT`.
The classification is
`EXACT_SCOPE_REJECTION_CONFIRMS_FACTORED_BARRIER_NULL`.  This falsifier does
not certify the constructor or issue the cycle's independent certificate.
The theorem ledger remains `2/9` with no recommended change.

## Independent circuit attack

The verifier never imports `build_factored_barrier_frontier.py` or the
constructor verifier.  From immutable repository sources it reconstructs the
seventy ordered sign-normalized parent factors, their 209 sparse terms, and
the degree-90 product circuit.  It independently reconstructs the primitive
degree-six, multidegree `(2,2,2)`, 108-term polynomial for factor 19069.

All nine derivative coordinates retain all seventy terms
`dH_I product_(J != I) H_J`.  The 630 stored derivative summands match the
correct differentiated factor and complementary-product provenance, including
zero derivatives.  All nine `df` derivatives and all 36 ordered coefficients
of `dB wedge df` have the correct memberships and input order.  Missing,
reordered, altered, or expanded factor data are rejected even after the
artifact's semantic hashes are adversarially resealed.

The strict-interior frontier honestly samples no connected component.  It
keeps possible dimensions zero through eight, singular wall pieces, positive-
dimensional pieces, all seventy strict parent inequalities, and an exact path
selector for the pinned parent component.  Consequently neither a generic
root list nor the raw critical equations can be promoted to component
coverage.

## Exhaustive true-boundary and path attack

An independent enumeration of all `15^3 = 3,375` nonempty product-simplex
supports re-evaluates every signed parent restriction.  Exactly 3,364 supports
have a Bernstein-wrong parent factor.  The remaining eleven are the ten proper
supports stored by the constructor plus full support.  Thus no true proper
boundary candidate is omitted.  On factor 19069, eight proper restrictions
are identically zero and two are Bernstein-mixed.

Every stored weak-sign witness is evaluated exactly.  The linear path to
support `(15,7,15)` is independently proved to keep all seventy signed parent
factors positive for `0 <= t < 1`.  This establishes residence in the closure
of the pinned parent component for that witness only.  It does not classify a
boundary wall germ or an interior wall component.

For support `(1,1,1)`, the prescribed linear path first fails at signed parent
factor `2578`: after exact removal of its endpoint zero, the reduced endpoint
sign is negative.  The same exact first-rejection data replay for the other
eight uncertified witnesses.  These failures reject those linear paths; they
do not prove that alternative exact paths are absent.  All ten boundary wall
residence records therefore correctly remain `UNCLASSIFIED_FAIL_CLOSED`, with
`(1,1,1)` the first unresolved support.

## Skeleton and attachment attack

The verifier uses independent rational univariate arithmetic to replay all
2,800 parent tags on the fixed forty-edge skeleton.  It finds one open
factor-19069 root on edge 39 and none on the other thirty-nine edges.  The
edge-39 primitive parameter polynomial, isolating interval, and nine affine
coordinate maps replay exactly.

That root is a local attached wall anchor because it lies on edge 39.  It is
not a sample of the barrier-critical locus and supplies neither a global wall
component count nor attachment completeness.  Attempts to promote the anchor
to a critical sample, global component, or complete attachment certificate
are rejected.

## Hostile mutations and exact scope

The standalone verifier rejects 25/25 semantic-hash-resealed hostile
mutations.  They cover factor loss and reordering, expanded-product insertion,
wrong `dB`/`df` membership and provenance, missing wedge equations,
generic-only and positive-dimensional omissions, singular-piece omission,
false parent selection, invented sampling, omission of `(1,1,1)` or
`(15,7,15)`, false path tags, boundary-class collapse, edge-39 overreach,
false attachment completeness, endpoint promotion, and ledger drift.

The only exact consequence is that the constructor's hash-pinned null has
scope-correct accounting for its first unsampled interior stratum and first
unclassified boundary support.  There is still no connected critical-locus
decomposition, complete boundary-to-interior wall classification, global
factor-19069 wall-component count, or complete component-to-skeleton
attachment classification.  No diagonal-nine claim changes.
