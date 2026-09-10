# Proof-track findings: collinear geometry and whole-height flat blocks

This cycle produced independently reviewed positive theorems, without changing
the original2/9 ledger or assigning a new numerical source-orbit count.

The full collinear triple locus now has H_c^0=0 whenever any factor has global
kind36,38 or48. The two remaining factor kinds in each such triple are arbitrary.
These are all-quantifier theorems for every original uniform rank4 parent on
eight labels and every normalized parent component, including all projected
coincidences, coefficient ranks and concurrence collisions.

For triples entirely among49,50,51, the following full closed pieces can also
be removed: parents on the common line; stacked transverse rank at most10;
and any rank-deficient individual transverse block. The last case is exactly
a selected plane containing the common line. Their noncompactness proofs use
full fixed-projection fibers or open feasible graphs over explicitly
noncompact projected bases, retaining all specialization pieces.

The remaining collinear critical branch is now precise:

* the factors are all49,50 or51;
* the three ordinary concurrences are distinct and their line contains no parent;
* none of the twelve selected planes contains that line;
* all three transverse blocks have rank4;
* their stacked matrix has rank11, equivalently their common row-space stress
  intersection has dimension1;
* the two remaining vertical wall gradients are dependent.

An exact regular rank11 canary was independently reconstructed from original
determinants. All70 parent brackets are nonzero, all ordinary normal circuits
have rank3, and the two vertical gradients have rank2. This demonstrates that
rank11 itself cannot be dismissed, but is not a critical or compactness
counterexample. Replay: `python proof/verify_collinear_rank11.py`.

There is a sharper pair-only discriminator for the remaining critical case.
For the full directional-gradient maps C_Q,C_R, collinear criticality with
point kernels is equivalent to C_R(q)=c C_Q(r), c nonzero. It supplies the
linear polynomial kernel

    (C_Q-t C_R)(q+c t r)=0.

Thus an entire pencil of rectangular gradient maps is singular, with this
specific degree-one kernel. No proof that actual49/50/51 pairs cannot satisfy
this condition has been found. In particular, the common gradient's membership
in row(B_P) has not been established and is not silently used.

The next exact test must start from a tuple authenticated as surviving the
inherited full-triple coverage, then check that its proposed parent lies
outside the new removable pieces. Previously covered witness tuples can refute
an unrestricted conjecture but do not refute the same conjecture restricted
to that inherited residue. The regular rank11 canary here is deliberately
diagnostic and is not being represented as a surviving source record.

A separate positive theorem removes whole-height flat blocks: on the closed
projected coefficient locus where one remaining wall determinant is identically
zero throughout the four-height P residence, the other wall has the established
four-equation/five-height incidence escape. The saturated global36 and38
localization-axis pieces satisfy this condition and are removed rigorously.
A stationary derivative alone, the different kind48 characteristic axis, and
vertically coincident non-flat sections are explicitly outside that theorem.

The artifacts are:

* `COLLINEAR_RANK_ESCAPE.md`: parent-on-line and full rank-at-most10 removal,
  including the proper projected quotient and parent-unit affine scale gauge.
* `ONE_LOW_COLLINEAR_ESCAPE.md`: complete collinear escape with a36/38 factor.
* `TYPE48_COLLINEAR_ESCAPE.md`: complete-quadrilateral proof for a48 factor.
* `RANK_DEFICIENT_BLOCK_ESCAPE.md`: exact49–51 leaf argument and the
  weight3 projected-base escape.
* `FLAT_HEIGHT_BLOCK_EXCISION.md`: coefficient-flat and localization-axis removal.
* `COMMON_STRESS_RANK_IDENTITY.md` and `LINEAR_GRADIENT_PENCIL_GATE.md`:
  exact remaining rank distinctions and the next discriminator.
* `PARENT_SLIDE_REVIEW.md`: independent acceptance of the referee-authored
  parent-on-line critical slide.
* `COLLINEAR_RANK11_REPLAY.json`: independently reconstructed exact canary.

The universal triple theorem and the original injectivity/triple-bad obligations
remain open. The noncollinear critical branch is being handled independently;
none of these proofs assumes that criticality forces collinearity. No broad
sample, missing finite-certificate inventory, or generic dimension inference
is used as a proof.
