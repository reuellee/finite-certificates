# D9 fixed-domain incidence gate-2 findings

The successor gate terminates before any roadmap critical system is solved.
Two independent authorization conditions fail exactly.

First, simultaneous `S_8` relabeling does not compress the fixed row-2599
`S12,37` active domain.  Exhausting all 40,320 permutations shows that only
the identity preserves the complete set of 3,539 active primitive factors.
Burnside therefore leaves

`C(3539,2) = 6,260,491`

fixed-domain pair orbits, not the 9,476 ambient pair-equation orbits.  The
ambient theorem simultaneously relabels the parent and family; it remains
valid, but it is not a fixed-domain incidence quotient.  The pair budget is
96,461, so symmetry alone misses it by 6,164,030 systems.

Second, the deterministic projection vector
`(1,2,4,8,16,32,64,128,256)` fails the first exact specialization screen.
For every active polynomial `q` of degree at most two, the producer solves the
eight affine polar equations

`d_j(q) - lambda_j d_0(q) = 0`, `j=1,...,8`,

over the rationals and restricts `q` to their affine solution space.  Ten
systems are inconsistent and hence have no critical point.  For 73 systems,
the affine equations have positive-dimensional solution spaces and `q`
restricts identically to zero.  Thus their polar loci are positive-dimensional
over the algebraic closure, so the chosen specialization is nongeneric before
the 3,456 higher-degree factors are reached.

The independent verifier reconstructs the colex triple action directly from
the global factor NPZ, checks factor-action descent on every active occurrence,
uses a separate quadratic-form restriction calculation, and rejects eight
hostile mutations.

This is the second consecutive constructive cycle leaving the complete
fixed-domain incidence blocker open, and this cycle also falsifies the chosen
projection specialization.  The protocol therefore requires `PIVOT` or
`STOP`; another symmetry-only or unfiltered enumeration is not admissible.
The theorem ledger remains `2/9`.
