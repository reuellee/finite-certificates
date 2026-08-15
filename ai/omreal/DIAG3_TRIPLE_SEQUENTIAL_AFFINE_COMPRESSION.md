# Diagonal three: exhaustive sequential-affine triple compression

## Outcome

The final `1,819,789` triple-factor residue after the affine-reframe,
moving-column, forest-fiber, triangular, role-frame Morse, and frame-1119
constant-plane layers has a new exact positive layer:

```text
  180,886  parent-unit graph + square jointly affine fiber
1,638,903  unresolved after this layer
---------
1,819,789  exact input partition
```

Thus the theorem-safe triple-factor total increases from `77,282,660` to

```text
77,463,546  componentwise-noncompact factor-triple orbits
 1,638,903  unresolved factor-triple orbits
----------
79,102,449  all unordered S8 factor-triple orbits
```

This is a genuine reduction of the first remaining diagonal-three
obligation.  It does **not** close that obligation, prove the exclusive-pair
middle exactness obligation, or change the honest score from `2/9`.

The exhaustive census builder is
`build_diag3_triple_sequential_affine_scan.py`.  It can emit a compact
witness stream; `verify_diag3_triple_sequential_affine_certificates.py`
independently reconstructs and checks every positive identity without using
the scanner's affinity masks.

## 1. The square affine-system theorem, including rank drops

This is the square-affine lemma of Section 1 of
`DIAG3_AFFINE_FIBER_FRONTIER.md`, restated here so that the rank-drop and
open-domain hypotheses used by the new certificates are explicit.

Let `Omega` be a nonempty open subset of `R^n`, with `n>0`, let

\[
                       D\subset\Omega\times\mathbb R^2
\]

be open, and let

\[
                    F(w,z)=A(w)z+b(w),\qquad z\in\mathbb R^2.       \tag{1}
\]

Every connected component of `D intersection Z(F)` is noncompact.  The
singular coefficient locus is part of the theorem rather than a deleted
generic stratum.

Indeed, suppose that `C` is a compact component.  If `C` contains `(w,z)`
with `det A(w)=0`, consistency of (1) makes the fixed-base solution an affine
space of positive dimension.  Its intersection with the open fiber `D_w`
has a noncompact connected component through `z`.  A semialgebraic connected
component is closed in the fixed-base zero set, and the fixed-base zero set
is closed in the full zero set.  Therefore this noncompact component is a
closed subset of `C`, a contradiction.

Consequently `det A` is nonzero everywhere on `C`.  On that locus (1) is the
graph `z=-A(w)^{-1}b(w)` over an open subset of the positive-dimensional
base.  A connected component of an open Euclidean set is noncompact, again
contradicting compactness of `C`.

No parent-unit determinant identity is needed.  Such an identity is a valid
stronger certificate, but the rank-drop paragraph above is precisely what
makes joint affinity sufficient.

## 2. Transfer through a parent-unit anchor

Each of the twelve canonical occurrence formulas has one or more coordinates
`x` in which

\[
                         q_0=A(y)x+B(y),                         \tag{2}
\]

where `A` is exactly a nonzero scalar times a product of parent brackets.
It is therefore nowhere zero in a fixed uniform parent cell `X`.  Graphing

\[
                         x=-B(y)/A(y)                            \tag{3}
\]

identifies `X intersection Z(q_0)` with an open subset `D` of `R^8`: it is
the inverse image of the open parent cell under the continuous graph map.

Clear each of the remaining equations by the appropriate power of `A` before
substitution.  Since `A` is a unit on `X`, this preserves their zero sets.
If the two cleared equations are jointly affine in the same two coordinates
`z=(z_1,z_2)`, they have exactly the form (1) over the remaining six graph
coordinates `w`.  Section 1 then excludes compact components, including
components meeting `det A_2(w)=0` for the new two-by-two coefficient matrix.

This proves componentwise noncompactness for every stored positive witness.
The argument uses exact polynomial identities only and remains valid over
every parent chamber because all bracket factors in the anchor slope are
units there.

## 3. Exhaustive presentation coverage

The scanner tries all of the following for every final-residue row:

1. each of its three factors as the graph anchor;
2. every one of the twelve canonical occurrence formulas in the anchor's
   full `S8` factor orbit;
3. every coordinate whose exact derivative is a parent-bracket unit;
4. the complete stabilizer of that canonical factor; and
5. all `C(8,2)=28` coordinate pairs in the graph variables.

There are exactly `45` canonical `(kind,pivot)` parent-unit graph charts in
step 3.  The count is reconstructed from the exact derivative factorizations,
not supplied as an assumed case list.

An anchor-to-canonical alignment followed by the full canonical stabilizer
exhausts the coset of all simultaneous `S8` reframings with that anchored
formula.  Trying every canonical formula in the factor orbit and all three
anchor orders therefore exhausts the stated presentation family.  The
affinity mask tests the exact condition

\[
                   \alpha_{z_1}+\alpha_{z_2}\leq1               \tag{4}
\]

for every monomial `x^alpha` of each cleared restricted polynomial.

The positive witnesses use twelve `(canonical kind, pivot)` combinations:

| anchor/pivot | rows | anchor/pivot | rows |
|---|---:|---|---:|
| `(36,0)` | `134` | `(37,0)` | `6` |
| `(39,0)` | `535` | `(41,0)` | `138` |
| `(42,0)` | `1,314` | `(48,0)` | `1,034` |
| `(49,1)` | `77,360` | `(49,5)` | `130` |
| `(50,1)` | `91,831` | `(50,3)` | `1,595` |
| `(51,5)` | `6,470` | `(51,6)` | `339` |

The earlier least-kind/single-pivot version closed `178,533` rows.  Exhausting
all canonical formulas and parent-unit coordinate pivots adds `2,353`, giving
the final `180,886`.

## 4. Exact source and semantic pins

The scanner reconstructs the source from the pinned union-degree-four file

```text
rows       1,897,733
SHA-256    54b03c31910de606b80f9dcc448ce3dde93063a8dbc3f2dbcaa7a02901df0303
```

It exactly removes the `12,333` triangular rows, the `65,550` role-frame
Morse rows, and the disjoint `61` frame-1119 constant-plane rows.  This
reconstructs the `1,819,789` input.  The prerequisite artifact pins are

```text
triangular features SHA-256
7fae9da26cf7391d2dc3b00e55faabdf4556d4badc9a2f8c4ace3ecc29d7f136

Morse certificates SHA-256
afe01d6d94bc4b8ce133cbe0d14ceb01d9dd72514f9ed7a59b73d5f6b4299734

frame-1119 constant-shear SHA-256
1cece61ff1a551faaeefc0062267e24266d264d9e19748d40fa5a74db9ce0be3
```

The new layer's final pins are

```text
affinity-mask semantic
b5e5c3171da1acfd5c47d2ebb793ed1be8cced5f01275e05b68d9e51ef4c3f08

witness semantic
d27735abc8601c04b1114786d2a044af1acf8b99c253aee347ab101c4bb5368b

residue semantic
d78a529cdb3e920b76b4b420114e24065c7e9e7cb2ef2a904b1a1e952c567270

exported witness stream SHA-256
7e9ad80ae55c1f51dda7f7dc584dac8eefe41197124914cb83aab3cf0a2b719e

exported residue SHA-256
5ba2314c94ba115d5bf5e975e68412e3f4b44e2c65df51b757f6150a3352d4e1
```

The compact witness stream is tracked as
`data/DIAG3_triple_sequential_affine_certificates.bin`; the much larger
residue is a regenerable construction product.  The builder pins both
digests when they are exported.  The independent verifier checks the tracked
witness stream by default and accepts an explicit regenerated path as an
optional argument.

An independent hostile replay reconstructed all `1,819,789` input rows and
checked that the `180,886` certificates and `1,638,903` residue rows are
unique, disjoint, and exhaustive.  It independently replayed anchor
alignment, stabilizer transport, parent-unit slope factorization, exact graph
restriction, coordinate-pair decoding, and joint affinity for every positive
record (`19,807` distinct algebra keys).  No coverage or theorem-transfer
objection remained.

## 5. Replay

From a clean checkout, first regenerate the pinned union-degree buckets with

```bash
mkdir -p /tmp/diag3-union-buckets
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/verify_diag3_projective_column_fiber_scan.py \
  --bucket-directory /tmp/diag3-union-buckets \
  --workers 8
```

Then regenerate both sequential streams and replay the complete census with

```bash
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/build_diag3_triple_sequential_affine_scan.py \
  --union4 /tmp/diag3-union-buckets/diag3_union_degree4.bin \
  --export-certificates /tmp/diag3_sequential_affine_certificates.bin \
  --export-residue /tmp/diag3_sequential_affine_residue.bin \
  --workers 8
```

Independently replay every positive certificate with

```bash
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/verify_diag3_triple_sequential_affine_certificates.py \
  /tmp/diag3_sequential_affine_certificates.bin \
  --union4 /tmp/diag3-union-buckets/diag3_union_degree4.bin
```

Omitting the positional certificate path checks the tracked compact
certificate and is the mode exercised by `run_all.py`.  Omitting only
`--union4` still replays every
positive identity but does not independently reconstruct its exact place in
the `1,819,789`-row source partition.

The smallest remaining triple obligation is exact and unchanged in nature:

> Exclude compact components for the `1,638,903` rows in the new residue,
> by another structural positive layer or a boundary-complete roadmap.

Sparse constant two-planes after the parent-unit graph anchor are a strict
next extension: for independent directions `u,v`, require
`D_u^2=D_uD_v=D_v^2=0` on both restricted equations.  This goes beyond the
coordinate-pair family proved here and must receive its own exhaustive exact
replay before changing the count.
