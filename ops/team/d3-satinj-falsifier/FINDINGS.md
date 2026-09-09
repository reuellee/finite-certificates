# Parent-unit saturation cannot exclude every support-change event

**Exact scoped negative; NULL for the original pair-map obligation.**
The admitted row-2599 flow signatures have a real, rational support-change
point strictly inside their original parent chamber. All three blocks are
Gordan-bad there. A selected five-support witness loses exactly one weight,
and its remaining four normals have rank three. Every parent determinant is
nonzero. Therefore saturation by parent determinants cannot prove absence of
all such events, even when the original proper incomparable labels and the
real nonnegative witness conditions are retained.

This is not a counterexample to injectivity or to an attachment theorem. The
support event may be topologically harmless. No global cohomology class,
frontier incidence, or true-infinity attachment is computed. The ledger stays
2/9, and every original open obligation remains open.

## Exact source and event

The input is chart 0 of `ai/omreal/data/seeat_parent2599_upper178.npz`, with
literal matrix and original signatures also in the pinned historical
`upper_chart_0_flow.json`. Its columns have labels 1,...,8:

```text
Y = [ -94  -25  256  256    42   -3  -78 -101
     -163   54   35 -164   -96  256  256  -21
      256  256  -27  -25   197  160  -83   54
       71  122   19 -204  -256  -61  -93 -256 ]
```

Replace only the second coordinate of column 2 by `54+t`. The three original
signatures and the selected supports, with triples in repository colex order,
are:

| Block | Signature | Support indices | Actual normal labels |
|---|---:|---|---|
| 0 | 14988895318912 | 0,19,21,37,38 | 123,456,137,238,148 |
| 1 | 3405195891438080 | 0,9,27,30,35 | 123,345,257,167,128 |
| 2 | 40418075143643136 | 0,11,17,24,40 | 123,136,256,247,348 |

Define the actual normal by `n_I(Y) p=det(y_i,y_j,y_k,p)`, and set
`a_I^b = sigma_b(I) n_I`. For an ordered five-support S, let

```text
c_j^b(Y) = (-1)^j det(the four rows a_i^b with i in S except S[j]),
lambda_j^b(Y) = c_j^b(Y) / sum_k c_k^b(Y).
```

These are the raw determinant gauge; positive row rescaling to primitive
normals merely changes the witness weights positively and leaves support.
The cofactor for the first block's normal 123 is exactly

```text
q(t) = -1590306865848117591794167506
       +295242861875452277122456470*t.
```

This degree bound is structural: among the four rows 456,137,238,148, only
238 involves moving parent label 2, and that row is affine in t. Hence the
cofactor is affine by determinant multilinearity, not an interpolation guess.
Its unique zero is

```text
t* = 37864449186859942661765893 / 7029591949415530407677535.
```

At this rational parent, the exact replay proves:

* All 70 ordered parent determinants are nonzero and retain the source signs.
* All three normalized weight vectors satisfy their four Gordan equalities,
  and every vector sums to one.
* Block 0 has `lambda_123=0`, and its other four weights are strictly positive.
* Each of blocks 1 and 2 has five strictly positive weights.
* The selected block-0 five-row system has rank 4; its four surviving rows
  have rank 3; its five augmented rows `(a_I,1)` have rank 5.

Thus this is an actual coordinate-face event of an otherwise nonsingular
normalized five-support system. It is not the old sheaf-left-inverse or
strict-coordinate-face-contraction counterexample.

For `epsilon=1/1000000`, both neighboring parents `t* +/- epsilon` remain in
the same strict parent chamber. At the left point the five selected block-0
weights are all positive; at the right they have signs `(-,+,+,+,+)`. The
other two blocks remain bad at both points. Block-0 badness on the right
is **not** established: another support might or might not witness it. The
claim is a selected support change, with triple badness proved at the event
and at the left point. Because every parent bracket is affine in this
single-coordinate motion, the strict endpoint signs also prove the whole
interval from 0 to `t*+epsilon` stays in the parent chamber.

## Binding the original hypotheses

`verify_event.py` independently reads the frozen NPZ without NumPy and binds
chart 0 literally. It also binds the historical properness/incomparability
anchors to charts 3,14,2 and their stored points. For each anchor it recomputes
all parent signs, verifies a strict primal witness for its designated block,
and exact nonnegative dual witnesses for the two other blocks. This establishes
all six ordered noninclusions and properness of all three original loci. It
also independently checks all 3,780 extension Grassmann--Pluecker sign
relations. The motion preserves the parent chirotope, so the signatures stay
the same admissible original labels.

The calculation is in the integer/rational parent gauge. Passing to a
normalized realization chart uses a nonsingular basis of parent columns,
positive coordinate/column scales and their induced positive normal scales.
Uniformity keeps its denominators nonzero. The nonnegative-kernel and support
statements are invariant under this chart change. No relabeling, synthetic
signing or fixed normalized-base hypothesis is used.

## Explicit failure ideal and the saturation consequence

Let Y denote all moving parent coordinates and let `lambda_I^b` be variables
for the three supports in the table. Put

```text
I_event = < sum_(I in S_b) lambda_I^b a_I^b(Y)_r,
            sum_(I in S_b) lambda_I^b - 1,
            lambda_123^0 >
```

where the first generators range over `b=0,1,2`, `r=1,...,4`, and the
normalization generators range over the three blocks. There are 16 scalar
generators, with the last zero-weight generator counted once. All other
56-row witness coordinates are identically zero. The real region also keeps
`lambda^b>=0` and the original strict signs of all parent brackets. Its
zero-weight branch contains the exact point in `EXACT_REPLAY.json`.

Let `u(Y)` be the product of the 70 parent determinants (or any product of
known nonzero parent determinants). The displayed rational point defines an
evaluation map on the localized coordinate ring because `u(Y*) != 0`.
Consequently

```text
1 is not in I_event : u^infinity.
```

In particular, an identity `u^N=sum_j A_j f_j` proving this event empty
cannot exist over Q. Evaluate it at the exact witness: the right side is zero
and the left side is nonzero. This reasoning also applies if the three
normalization/support constraints are encoded using fewer variables by
verified elimination.

The rational witness reduces modulo every prime avoiding its denominator
and the nonzero parent-bracket numerators. At any such prime the corresponding
localized event ideal still has a point. No modular solver was run here.
Finite-field emptiness, if obtained in an exceptional characteristic, would
not remove this exact real characteristic-zero point.

The event must be retained or proved harmless by an actual comparison or
attachment argument. Adding its cofactor or weight to the saturator would
explicitly delete this admitted stratum and cannot count as full original
coverage without a separate proof for that stratum.

## Gate and limitations

The tested candidate was: **known nonzero parent determinants exclude all
zero-weight/support-change branches that a selected-support frontier model
would otherwise need to attach**. This candidate is false in the original
labeled domain. A narrower candidate that excludes only failures of a
particular collar remains possible, but no such failure-to-global-frontier
implication was supplied in this track. The event is rank regular as an
augmented five-support system, so it does not refute a regular-stratum collar.

No claim is made that all support-change events are singular, that they alter
real cohomology, or that parent-unit saturation is useless for other equations.
This witness does not determine any of the signed frontier blocks `b01,b02,b12`,
does not address their cancellations, and does not compute the canonical
detector's trace. It lies strictly inside the parent cell; genuine parent
infinity remains an uncomputed relative boundary, not this event.

Discovery stopped at this first structural negative. The proposed main F4SAT
calculation remains ineligible on this universal support-exclusion candidate.
No source census, signing atlas, solver installation, paid service, external
write, or ledger update occurred.

## Reproduction

```text
python -B ops/team/d3-satinj-falsifier/verify_event.py
```

The replay uses Python standard-library exact fractions and independent
Gaussian determinant/rank arithmetic. It imports neither the discovery code
nor historical acceptance logic. `EXACT_REPLAY.json` records every rational
weight and parent determinant. Default replay reconstructs and compares every
recorded field except elapsed time without changing files; fresh runtime is
printed only to standard output. Four hostile controls reject a changed weight,
a supported-sign flip, a shifted alleged event parameter, and calling this
strict parent-interior point parent infinity. Runtime was about 0.38 seconds.

`discover_event.py` and `DISCOVERED_EVENT.json` preserve the bounded discovery
provenance; the final verifier does not trust their polynomial arithmetic.
`SOURCE_MANIFEST.json` pins the authoritative base and five original inputs.
The exact pair invariant and original proof-distance coordinates are unchanged.
