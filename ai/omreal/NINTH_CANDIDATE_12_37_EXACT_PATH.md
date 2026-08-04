# Exact path through the row-2599 charts 12 and 37

## Result

Let `M` be catalog parent 2599 and let `S` be the following nine extension
signatures (the bits use the repository's colex order on the 56 parent
triples):

```text
32577326938880
31532828708796544
3510916511430656
72042742044167295
3476291556529680
2137481474473987
58098186400358399
32444182421504
68557050812244096
```

The exact parent matrices at indices 12 and 37 of
`data/seeat_parent2599_upper178.npz` lie in the same path component of

\[
F_S=\bigcap_{\sigma\in S}F_\sigma.
\]

This refutes the apparent separation of these two charts in the 178-point
sample.  A second exact certificate, described below, proves that the nine
regions are globally proper and pairwise incomparable.  Thus this is a valid
size-nine 9DVL input family, not merely a sampled surrogate.  It does **not**
prove the ninth diagonal: the path certificate concerns one pair of points
for one parent only and does not prove that their full common feasibility
locus is connected.

## Certificate

The certificate is
`data/ninth_candidate_12_37_path.npz`.  It contains exact integer homogeneous
columns for a path in the incidence space

\[
Z_S=\{(Y,p_1,\ldots,p_9):Y\in\mathcal R(M),\ p_i\text{ realizes }\sigma_i\}.
\]

The path has three parts:

| part | rational line segments |
|---|---:|
| chart 12 to canonical incidence A | 11,701 |
| canonical incidence A to canonical incidence B | 3,009 |
| canonical incidence B to chart 37 (reversed) | 8,001 |
| total | 22,711 |

Every ordinary edge replaces exactly one of the 17 homogeneous columns: one
of the eight parent columns or one of the nine extension columns.  Therefore
each prescribed `4 x 4` determinant is either constant or affine along that
edge.  The verifier checks with integer arithmetic that its prescribed signed
value is strictly positive at both endpoints.  Affinity then proves strict
positivity on the entire closed edge.

The two canonicalization steps consist of an orientation-preserving `GL(4)`
change and positive column rescalings.  The verifier reconstructs these
changes independently over `Fraction` and checks equality of the positive
projective rays.  Thus they are gauge identifications, not unverified jumps.
Projection of the resulting path in `Z_S` to its first eight columns gives the
claimed path in `F_S`.

Its SHA-256 digest is:

```text
8db38e00d9bf8701558c27cd4ede3e024db8953ea3ef9873bf0b4fc65ad6bcda
```

## How the middle bridge is certified

After a common positive projective gauge, only parent columns 5, 6, and 7
(zero based) differ.  Their straight interpolation is split into 100 slabs.
Within each slab and for each parent column in turn:

1. For every signature, replace its extension column by an exact rational ray
   feasible for both the current and next parent matrix.
2. Replace the one parent column.

The nine extension replacements and the parent replacement are all
one-column affine edges.  The final nine edges attach the extension rays of
canonical incidence B.  This accounts for
`100 * 3 * (9 + 1) + 9 = 3,009` middle segments.

The builder uses floating-point linear programming only to locate interior
rays.  A candidate ray is retained only after exact determinant checks, and
the verifier does not trust or repeat the floating-point search.

## Verification

Run:

```bash
python ai/omreal/verify_ninth_candidate_path.py
```

The verifier independently checks:

1. both source matrices realize catalog parent 2599;
2. both initial incidences realize all nine signatures;
3. all 19,702 endpoint-chain updates;
4. both exact positive projective gauge identifications;
5. all 3,009 middle-bridge updates; and
6. positive projective equality with the terminal incidence.

Expected final lines:

```text
PASS: exact 3009 segment rational bridge
PASS: every segment changes one column and has positive exact endpoints
THEOREM: charts 12 and 37 lie in one component of F_S (22711 segments)
SCOPE: this refutes only the sampled separator candidate, not ninth-diagonal 9DVL
```

`build_ninth_candidate_path.py` reproduces the certificate.  Its numerical
search is deterministic under the recorded random seeds, but only the exact
certificate and independent verifier are used in the theorem.

## Exact proper-antichain audit

The companion certificate
`data/ninth_candidate_12_37_antichain.npz` records seven exact parent charts.
For each of their 63 chart/signature entries it stores either

* an integer extension ray having all 56 prescribed strict signs, or
* a support-at-most-five positive integer Gordan relation among the signed
  derived normals.

Their feasibility patterns are

```text
001010011
010111100
100101001
011100100
011001011
100010101
100111110
```

Every column contains both symbols, so every region is nonempty and proper.
For every ordered pair of distinct columns `(i,j)`, some row has `1` in
column `i` and `0` in column `j`.  The exact witnesses on that chart disprove
`F_i subset F_j`; doing this in both orders proves pairwise incomparability.
This is a global conclusion from exact witness charts, not an inference that
the 178-chart sample exhausts the parent realization space.

Run:

```bash
python ai/omreal/verify_ninth_candidate_antichain.py
```

The certificate SHA-256 digest is:

```text
11ca66549982ec40ce8425d2caed45b418edb73c4eb415a45b39d57e481bd1e4
```

## General mechanism and remaining gap

This example supplies a reusable exact path language.  The incidence space is
convex in each individual homogeneous column while the other columns are
fixed, so any finite coordinate path is certified by determinant signs at its
vertices.  Moreover, two nearby parent matrices can be joined whenever each
signature has an extension ray common to both endpoint extension cones.

A general ninth-diagonal proof would still have to show that these local
coordinate moves and common-cone overlaps connect every relevant `Z_S` (or at
least its projection `F_S`) for every parent and every size-nine internal
antichain of proper regions.  Separate convexity alone does not imply this
global reachability.  The existing 2,604-parent catalog supplies only one
matrix for most parents, so it cannot by itself certify the required residual
wall chamber graph or all of its overlaps.
