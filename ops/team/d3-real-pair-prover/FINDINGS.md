# Pair track: arbitrary-block occurrence compression, original map still open

**Original target: NULL. Auxiliary result: exact generic same-factor theorem.**
No original invariant closed, no source orbit was removed, and the honest
diagonal count remains **2/9**. This is a bounded endpoint, not permission to
continue a local atlas or a claim that the pair differential was computed.

Base commit: `cefc495b27247c4a76f88bce04978422161f7ce9`.
Base tree: `c49c2e6625f3ee76d77cc263897366dcf7e037c2`.
Owned surface: `ops/team/d3-real-pair-prover/`.

## Exact new statement

For a generic supported primitive residual factor of a uniform rank-four
eight-label parent, form the occurrence complex from its active small circuit
supports. Keep one vertex for each occurrence support positive in **every**
selected block signing. Keep an edge when the two supports use at most six
normals, and a triangle when its three edges exist and its support union has
at most seven normals. For any nonempty finite number of independently signed
blocks, this common-active occurrence complex has

\[
                         H_1(O_f;R)=0
\]

over every coefficient ring `R`. Arbitrary signings are allowed, so the result
also applies to signings of valid proper incomparable extension families.

The existing theorem in `DIAG3_PAIR_FACTOR_ROOT_SWITCH.md` proves this for
one or two blocks, using the six global factor kinds. The extension to any
number follows from an exact two-signing representation of every finite
intersection of the kind-38 pattern family. No new parent or occurrence
census is being asserted.

The hypotheses remain literal: a fixed generic supported factor, its supplied
generic circuit ranks, and the genuine rank-two pencil in kind 38. The result
does not include extra rank drops, shrunken supports, intersections with other
factors, or parent-infinity specialization maps.

## Why two synthetic signings suffice

Only factor kind 38 requires a new argument. Its two core normals are
`n345,n678`, and its six outer normals are `n12k`, `k=3,...,8`. The latter
annihilate the parent line `12`, hence lie in a rank-two flat. At a generic
supported factor the eight normals span rank three and every selected
four-circuit has nonzero coefficients.

Use a projective coordinate on that pencil and order the six outer rays.
After nonzero rescaling and reorientation, the relevant rank-three form is

\[
 p=(0,0,1),\quad q=(1,w,-1),\quad u_j=(1,t_j,0),
 \qquad j=0,\ldots,5,
\]

where `t0<...<t5` and `w` lies in one of the seven gaps. Actual spacing is
immaterial to the coefficient signs. Consequently the exact finite replay
can use the order-equivalent representative `t_j=j`, `w=gap-1/2`; this is
not an assertion that a projective coordinate sends six arbitrary rays to
six equally spaced points.
If the two core signs do not permit a positive dependence, the whole active
pattern is empty. Otherwise normalize their common polarity to positive.
For `i<j`, the two outer coefficients in a positive core relation are
proportional to

\[
                  w-t_j,\qquad t_i-w.
\]

Thus each outer edge requires one specific bit at each endpoint. Let `P(s)`
be its active-edge mask for the six-bit outer signing `s`, at one fixed gap.
For any list `s0,...,sr`, define bitwise

\[
 d=\bigvee_{j=0}^r(s_0\mathbin{\mathrm{xor}}s_j),
 \qquad s_* = s_0\mathbin{\mathrm{xor}}d.
\]

Then the exact identity is

\[
               \bigcap_{j=0}^r P(s_j)=P(s_0)\cap P(s_*).       \tag{1}
\]

Indeed, an edge inactive for `s0` is absent from both sides. An edge active
for `s0` survives every signing exactly when neither endpoint has a
disagreement bit in `d`. Those are exactly the edges also active for `s*`.
This proof works for any finite number of blocks, without enumeration in
that number.

The representative two-signing set has 180 masks in every gap and is closed
under intersection with each of the 58 one-signing masks. The seven gaps
together give 487 distinct masks. The replay verifies this closure directly,
and also checks (1) on all `7 * 64^3 = 1,835,008` ternary signing inputs.
These are exactly the old two-block pattern counts, not additional coverage.

The synthetic `s*` need not be an original block or a valid global extension
signature. For example, at gap zero, signings `(8,25,26)` have masks
`(580,1728,1549)` and common mask `512`. No pair of those three masks has
intersection `512`; the synthetic pair `(8,27)` does. Consequently (1) is
not a Helly-two theorem for signatures and does not replace the original
three extension labels by two.

## Integral triangle fillers

For kind 38, all occurrence vertices are joined: two four-supports use at
most six normals. A triangle is absent only when its three outer edges form
a perfect matching on all six outer labels. In the 180-mask family every
active matching has a fourth active outer edge `h`. This is checked exactly
in all seven gaps; the total is 105 active matching instances.

For matching vertices `a,b,c`, the oriented chain

\[
           [a,b,h]+[b,c,h]+[c,a,h]
\]

has boundary equal to the boundary of `[a,b,c]`. Each displayed triangle
uses at most five outer labels and therefore at most seven normals. The
checker verifies the signed boundary, not just a mod-two rank. Every graph
cycle in a complete graph is a sum of triangle boundaries, so these unit
fillers prove `H1=0` over every coefficient ring.

For kind 36, the existing proof already works for an arbitrary active subset:
three ten-vertex families have full two-skeleta, with no edges between
families, and the active central vertex cones them. Kind 48 has two supports
whose union is eight and hence no edge. Kinds 49, 50, 51 have one support.
These arguments already permit intersections of any number of active sets.
The new identity (1) supplies precisely the formerly two-block kind-38 case.

## Actual parent anchor and replay boundary

The standalone verifier imports no repository producer. It independently
reconstructs the deterministic rational type-38 parent used by the existing
robust-edge source, computes all 70 parent brackets, and confirms they are
nonzero. It computes all derived normals by determinants and checks:

* the six actual `n12k` normals have rank two;
* those six and the two core normals have rank three;
* every one of the 15 core-plus-pair supports has a full rank-three circuit;
* all 256 reorientations of the eight normals give precisely the 58 patterns
  of the gap-one line model after the source's stated line order.

The representative is an arithmetic anchor for the normal-form argument.
It is not all-parent coverage by sampling. The six-kind global occurrence
classification and its genericity scope are explicitly inherited from the
hash-pinned original theorem. That full classification is not rerun here.

The replay checks source hashes and rejects five hostile controls: deletion
of a required closure mask, an unsupported matching-only triangle, reversal
of a signed filler coefficient, promotion to global pair-map injectivity,
and deletion of the generic-factor limitation. The matching-only fixture is
a logical control, not a newly discovered parent-realized counterexample.

Run from the repository root:

```text
python -B ops/team/d3-real-pair-prover/verify_arbitrary_block_occurrences.py
```

Its completed output is `ARITHMETIC_REPLAY.json`. These are arithmetic checks
and a deductive handoff; independent AI acceptance remains the referee's job.

## Bounded null for the authorized target

The searched route was to exploit actual shared-normal sign structure to
remove cancellation in

\[
 D:\bigoplus_{i<j}H_c^1(B_i\cap B_j;\mathbb Q)
      \longrightarrow H_c^1(B_0\cap B_1\cap B_2;\mathbb Q),
 \qquad D(x)=r_{01}x_{01}-r_{02}x_{02}+r_{12}x_{12}.
\]

Source auditing identified one potential extra discrete obstruction: the
existing occurrence theorem had only a one-/two-block scope. The finite
intersection-closure test decisively removes that obstruction for any number
of signings. It does not make the original `D` injective.

**First unresolved implication:** a pointwise contraction of occurrence
choices on a generic factor has not been promoted to a proper chain map
compatible with actual factor-to-factor attachment, zero weights, all original
extension labels, and genuine parent infinity. Equation (1) is especially
unsuited to silently supplying that map: its synthetic signing may vary with
the chosen factor, gap, and chart, and need not be an original extension.

**Best exact discriminator:** after this discrete compression, retain the
original factor-end blocks `b01,b02,b12` of equation (17) in
`DIAG3_PAIR_DIFFERENTIAL_ENDS.md`. A candidate must provide their actual
oriented parent-stratum incidences and true-infinity attachments, then pass
the rational middle-rank equality

\[
                 \operatorname{rank}N+\operatorname{rank}M
                    =\dim C^1,\qquad MN=0.
\]

The absent datum is those geometric frontier blocks. Another list of active
occurrences, a common-root graph, or a single escape adds no entry to them.
The existing two-dimensional ribbon's surviving class also cannot supply
those global blocks by itself. This handoff therefore certifies no successor
based on more signing enumeration or local atlas expansion.

The structural midpoint stops this route: its discrete obstruction is gone,
but the same global frontier-attachment blocker survives. Classification is
**INFORMATIONAL / NULL for the original pair target**. All seven original
obligations remain open; triple residual `1,162,302`, settled count
`77,940,147`, total `79,102,449`, and the first six proof-distance coordinates
are unchanged. No arbitrary convex-fiber countermodel is reissued as new,
and no original 9DVL counterexample is claimed.
