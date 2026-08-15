# Diagonal three: unit Jacobian minors after a graph anchor

## Outcome

This note gives a second exact positive layer on the triple-factor side.  It
starts with the pinned `1,638,903`-row residue left by
`DIAG3_TRIPLE_SEQUENTIAL_AFFINE_COMPRESSION.md` and closes `117` more rows:

```text
      117  exact parent-unit two-by-two minors after one unit graph
1,638,786  still unresolved
---------
1,638,903  exact input partition
```

Consequently the theorem-safe componentwise-noncompact count is now

```text
77,463,663  componentwise-noncompact factor-triple orbits
 1,638,786  unresolved factor-triple orbits
----------
79,102,449  all unordered S8 factor-triple orbits
```

This remains a partial reduction of the first diagonal-three obligation.  It
does not close that obligation, address global exclusive-pair middle
exactness, or change the honest score from `2/9`.

These are the standalone counts obtained when this layer is applied directly
after the sequential-affine layer.  The later double-graph certificates close
`417,828` rows of the same input.  Exactly `97` of this layer's `117` rows
occur in the pivot-3 certificate, while none occurs in the pivot-1/5 or
generic increments.  Therefore, in the order sequential affine, double
graph, then unit minor, this layer contributes `20` new rows.  The exact
all-family union has `417,848` rows and the combined residue is `1,221,055`.
The standalone closure counts must not be added without this overlap
correction.  See `DIAG3_TRIPLE_DOUBLE_GRAPH_COMPRESSION.md`.

## 1. Fixed unit-minor theorem

Let `X` be a fixed uniform parent cell and suppose one residual factor has an
exact graph presentation

\[
                       q_0=A(y)x+B(y),
\]

where `A` is a nonzero scalar times a product of parent brackets.  Since `A`
is nowhere zero on `X`, graphing `q_0` identifies `X intersection Z(q_0)`
with an open domain `D` in `R^8`.

Let `r_1,r_2` be the two remaining residual equations after denominator
clearing by `graph_restrict`.  This clearing does not change their zero sets
on `D`.  Assume that for one fixed pair of graph coordinates `(u,v)`, the
two-by-two Jacobian minor satisfies the exact integer identity

\[
 \det\frac{\partial(r_1,r_2)}{\partial(u,v)}
       = c\prod_j \widetilde B_j,                         \tag{1}
\]

where `c` is a nonzero integer and every `tilde B_j` is the denominator-cleared
restriction of a parent bracket.  Each restricted parent bracket is nowhere
zero on `D`: it equals a power of the already-inverted anchor slope times the
original bracket pulled back along the graph, up to a nonzero primitive
scalar.  Thus (1) is nowhere zero throughout `D`.

It follows that

\[
                         Z=D\cap Z(r_1,r_2)
\]

is a smooth six-dimensional manifold.  Projection to the six graph
coordinates complementary to `(u,v)` is a local diffeomorphism, hence an open
map.  Semialgebraic connected components of `Z` are open in `Z`.  If one such
component were compact, its projected image would be a nonempty compact open
subset of `R^6`, which is impossible.  The positive base dimension `6>0` is
essential here.

This argument neither assumes joint affinity nor deletes a rank-drop locus:
the fixed parent-unit minor proves rank two everywhere on the entire graph
domain.

## 2. Exact certificate layer

All `234` stored target-pair identities use canonical type `49`, pivot `3`.
Here the first graph slope is literally `1`.  The target-pair certificate
records

* the two transformed residual-factor identifiers;
* the fixed coordinate pair `(u,v)`;
* the sign; and
* the complete list of graph-restricted parent brackets in (1).

The verifier is independent of the finite-field discovery screen.  It
reconstructs the normalized matrix and all parent brackets directly, loads
the global factor polynomials, performs both cleared graph restrictions over
`Z`, differentiates, and checks literal polynomial equality with the recorded
product.  It deliberately shares the repository's audited graph-restriction
and canonical label-action helpers.  Product lengths are

```text
length 4:  13
length 5:  56
length 6: 140
length 7:  24
length 8:   1
```

The compact artifact pins are

```text
records                          234
artifact SHA-256
9889d40c9fdc4c23817a28e94b311cec1673b4e4dfd3e072dace17ff49ffd97a

exact-pair semantic
15b761934f6fb98d036f1820e99b3c6012ea4134ae5746579dac874280537e15
```

## 3. Exact row correspondence

For every row in the pinned sequential-affine residue, the verifier tries
each of its three factors as the type-49 anchor whenever applicable.  Its
stored anchor-to-canonical map is checked by transforming the anchor back to
the canonical type-49 factor.  The full canonical stabilizer is then
exhausted.  Alignment followed by the stabilizer covers the complete coset of
simultaneous `S8` reframings with that fixed anchored formula.

Exactly `117` distinct rows acquire one of the `234` pair identities.  Their
chosen anchor positions have counts

```text
position 0:   2
position 1:  12
position 2: 103
```

The row pins are

```text
input rows                       1,638,903
input SHA-256
5ba2314c94ba115d5bf5e975e68412e3f4b44e2c65df51b757f6150a3352d4e1

closed rows                      117
row semantic
8dabe7ae8baf1bf6ce7d8dbac7621a4e6810860717fd3c4a39700db018b22e79
```

This row partition depends on the prior sequential-affine verifier for the
construction and pinning of the `1,638,903`-row input.  The optional replay
checks its SHA-256, row count, record length, uniqueness, distinct factors,
and the complete new row map; it does not independently regenerate that
prior residue from the full `79,102,449`-orbit universe.

## 4. Search scope and corrected audit boundary

The identities were discovered with a finite-field line filter and then
replayed exactly over `Z`.  An early diagnostic version incorrectly rejected
minors which became zero modulo `3`; that can omit a valid identity whose
integer scalar is divisible by `3`.  Therefore no negative count or
exhaustiveness claim from that discovery screen is retained here.  The bug
does not affect any stored positive: every one of the `234` identities is
reconstructed and checked directly over `Z` by the independent verifier.

This certificate is deliberately a positive subset.  It does not claim that
type-49/pivot-3 contains no further unit minors or that the other `44`
canonical parent-unit graph charts have been exhaustively scanned.

## 5. Replay

Replay all `234` integer identities from the tracked compact artifact with

```bash
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/verify_diag3_triple_unit_minor_after_graph.py
```

If the regenerable sequential-affine residue is available, also replay the
exhaustive row correspondence with

```bash
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/verify_diag3_triple_unit_minor_after_graph.py \
  --sequential-residue /path/to/diag3_sequential_affine_residue.bin
```

Applied before the double-graph family, the smallest remaining triple-factor
gap after the sequential-affine and unit-minor layers alone is:

> Exclude compact components for the exact `1,638,786` remaining rows.

After taking the exact union with the double-graph family, the actual combined
smallest gap is `1,221,055` rows.

An exhaustive unit-minor continuation must primitive-normalize every integer
minor before modular reduction, pin the content/sign normalization, retain or
correctly classify every modular-zero case, cover all `45` canonical graph
charts and their stabilizers, and replay every positive over `Z`.
