# Diagonal eight: exact parent-860 graph-interface no-go

## Result

The existing parent-860 repaired network yields one exact proof-bearing
two-dimensional filling, but it cannot yet support a nonvacuous
diagonal-eight matching or boundary-rank conclusion.  Three exact facts make
the boundary sharp.

First, the network represents `26,264` signatures in `13` support classes.
The universal class contains `25,960` signatures.  The remaining `304`
signatures quotient to `12` proper support patterns on the certified
`24`-chamber, `39`-edge network.  Ordered by inclusion, this proper local
dominance poset has width exactly `6`.  A six-element antichain proves the
lower bound; a partition into six inclusion chains proves the upper bound.
Consequently it contains **no** proper pairwise-incomparable eight-family.
Any statement about every eight-antichain represented by this local quotient
is therefore vacuous.

Second, the obstruction is not merely insufficient family diversity.  The
five pairwise-incomparable local patterns with indices

```text
4, 8, 9, 10, 11
```

have common support mask `2065`, exactly the three chamber vertices
`{0,4,11}`.  All three network edges

```text
(0,4), (0,11), (4,11)
```

are present, so the induced one-complex is a triangle.  Its exact cellular
boundary has `rank(d1)=2`, `C1` has rank `3`, and no `C2` datum is present;
therefore

\[
                    \dim_{\mathbb Q} H_1=3-2=1.
\]

Attach one oriented two-cell with boundary `(1,-1,1)` on the ordered edges
above.  Then `d1*d2=0`, `rank(d2)=1`, and the same labeled one-skeleton has
`H1=0`.  Thus the certified vertices, wall crossings, and labels are
compatible with both homology verdicts.  The two completions are exact
finite relative CW countermodels to any interface that tries to infer
diagonal-eight `H1` from the current graph alone.  Neither completion is
asserted to be the geometric parent-860 dual complex.

Third, for this particular triangle the missing geometric verdict can be
decided positively.  Vertices `0`, `4`, and `11` are the exact rational
points in the normalized parent chart with `(a,d)` offsets

```text
(0,0), (79/978402,0), (0,13/526129).
```

The three graph edges are the corresponding straight coordinate segments
and the certified residual-free chord `4--11`.  For each of the five
incomparable representative signatures the certificate supplies one fixed
integer four-vector.  Direct exact evaluation gives `840/840` positive
signed derived-normal controls at the triangle vertices.  The smallest
margin for each signature is recorded in the certificate and is strictly
positive.  All `210/210` parent-bracket vertex controls retain the parent-860
sign.

Every parent bracket and every fixed-witness signed derived inequality is
affine in `(a,d)`: the only changing entries are in the same matrix row, so
no determinant term can contain their product.  The verifier also checks all
`350` mixed coefficients vanish.  Barycentric interpolation therefore proves
strict positivity on the whole closed triangle.  The triangle stays inside
the parent cell and inside the common feasibility locus of the five
signatures.  Its boundary is the certified network cycle, hence this is an
exact geometric null-homology, not merely the formal filled countermodel.

## Exact width certificate

Using the pattern indices stored in the certificate, a width-six witness is

```text
(1,2,3,6,7,9).
```

A six-chain cover is

```text
(0<6<10), (1<5), (2<11), (3<4), (7<8), (9).
```

Here `<` means strict inclusion of the represented chamber-support bitsets.
The verifier additionally enumerates all antichains: there are nine of size
six, every one has empty common support, and there are zero of size eight.

Local incomparability is proof-safe: if two support patterns are
incomparable on this embedded network, the displayed chamber witnesses also
disprove either global region inclusion.  Local equality or inclusion is
not proof-safe in the converse direction because undiscovered chambers may
separate the regions.  This is another reason the width-six calculation
cannot be promoted to a global dominance statement.

## First missing datum

The triangle filling proves that fixed-witness affine disks are a viable
codimension-two schema.  The next discriminating artifact is the analogous
exact filling gate for the non-triangular `a/g` loop
`1--2--3--18--17--1`, followed by an incidence record which installs the
certified disks as relative two-cells and marks true infinity.  It should
first attempt fixed witnesses on the rational polygon; only surviving
signatures require the larger all-factor arrangement classification.

This bounded no-go proves no diagonal-eight instance for the full parent
cell, no other parent, and no true-infinity claim.  `diag8_h1` stays open and
the honest 9DVL score remains `2/9`.

## Replay

```bash
PYTHONDONTWRITEBYTECODE=1 python \
  ops/team/diag8-dual-prover/verify_diag8_parent860_graph_h1.py
```

The verifier uses only the Python standard library.  It checks the pinned
source NPZ byte digest, parses the required NPY members directly, reconstructs
the support quotient, replays exact rational boundary ranks, exhausts the
antichains, and runs positive, negative, null, and hostile canaries.
