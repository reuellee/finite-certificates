# Independent referee: accepted only as an abstract deletion diagnostic

**Verdict: ACCEPT_ABSTRACT_FULL_COLLISION_DELETION_ONLY.** The original
injectivity theorem remains open, no original obligation is closed, and the
ledger remains 2/9.

I derived the six-line collision locus, low-degree groups, and compactified
product complex before reading the current producer's artifacts. The record
is `OPENING_AUDIT.md`; `verify_independently.py` imports no producer code and
does not use producer acceptance logic. Its exact replay succeeded before
candidate review. After the coordinator froze the candidate, I checked all
three candidate file hashes in `diagnostic/HANDOFF.json`, read the candidate
proof and result, and compared them to the independent output. All seven
full cohomology vectors, the twelve-ray arrangement, and the actual degree-one
map agree. The checked hashes are recorded in `VERDICT.json`.

## Accepted deductions

1. The complete locus consists of h=0 and one of u=0, v=0, u+v=0,
   u-v=0, 2u+v=0, u+2v=0. Moving-to-coordinate-row collisions are included;
   checking only pairs of moving rows would be incomplete. Exhaustiveness
   follows from the explicit second coordinates and elementary coordinate
   comparisons for all row-pair types; rational anchors alone are not
   presented as a proof of exhaustiveness.
2. The correct boundary includes both true radial infinity and every
   deleted collision star times S6. Closed D7 must remain partly present
   over singleton and pair angular interiors. The product CW pair in the
   candidate proof is precisely a compactification of the deleted spaces.
3. The independent cellular differential squares to zero. After quotienting
   the full boundary, there are no degree-zero or degree-one cells. Hence
   every singleton, pair and triple has Hc0=Hc1=0. Singleton Hc2 has
   dimension8; pair Hc2 has dimension4; triple Hc2 is zero. The independent
   replay also obtains the candidate's Hc8 dimensions8,5,2 and verifies all
   remaining groups through degree9 vanish.
4. As the source and target degree-one cochain spaces are themselves zero,
   the actual induced alternating pair-to-triple map is uniquely 0→0. This
   conclusion does not depend on choosing compatible abstract vector-space
   isomorphisms. Independently, the old-to-deleted restriction is injective
   for pairs and an isomorphism for the triple, giving the same result by
   compact-support excision. The old nontrivial kernel is independently
   recovered when the deletion boundary is omitted.
5. Required lower vanishings survive in singleton degrees0,1 and pair/triple
   degree0. Singleton degree2 vanishing fails for every singleton. Therefore
   this deletion cannot convert the frozen model into a counterexample
   satisfying all required lower hypotheses.

## Controls and limitations

The independent checker explicitly distinguishes full deletion from omitting
the coordinate-row collision lines (singleton Hc2 becomes dimension4),
reusing the old boundary (the old pair Hc1 and kernel return), and replacing
the whole cap by an open ball (singleton compact-support groups wrongly all
vanish). Its reconstruction of the old map uses a different target basis,
with matrix `[[1,1,0],[0,1,1]]` and the same primitive kernel `(1,-1,1)`.

This is finite exact rational cellular computation plus an elementary
written identification of the semialgebraic compactification, not a Lean
formalization. The proof uses the previous checkpoint's all-parameter
feasibility elimination as a pinned input. It makes no new claim about
original uniform-parent realizations, actual 56-row derived-normal families,
shared-column or compound identities, or coverage of original source orbits.

No universal implication from nonproportionality to injectivity has been
proved or disproved. The diagnostic establishes what happens for this
particular deletion, including the hypothesis it destroys. There are no
actionable findings against that bounded conclusion.

Replay from the restored bundle using
`python -B collision_diagnostic/referee/verify_independently.py` with the
frozen `injectivity/falsifier/MODEL.json` retained alongside the cycle.
