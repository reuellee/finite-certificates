# Diagonal three: primitive final directions after two unit graphs

## Honest result

This positive certificate starts from the exact `1,221,055`-row residue after
the sequential, coordinate double-graph, and graph-unit-minor layers.  The
direct-final-coordinate certificate closes `58,673` of those rows.  The
present layer proves **23 additional and disjoint rows**, leaving
`1,162,359` triple rows open.

This is not a maximality claim for primitive directions and it does not close
the triple obligation.  It also does not address the independent global
exclusive-pair middle-exactness obligation, so the honest score remains
`2/9`.

## Primitive final-direction theorem

Fix an open uniform parent cell `X`.  The first certified residual equation
has the exact form

\[
q_1=A_1(w)x+B_1(w),
\]

where `A_1` is a nonzero scalar times a product of parent brackets.  Hence
`A_1` is nowhere zero on `X`; solving `q_1=0` is a graph homeomorphism onto an
open domain `D` in `R^8`.  Every denominator clearing performed by
`graph_restrict` multiplies by a power of this unit and preserves the zero
set.

On `D`, the second cleared equation is

\[
r_2=A_2(v)y+B_2(v),
\]

and the certificate writes `A_2` exactly as a nonzero scalar times a product
of graph-restricted parent brackets.  Those brackets remain nowhere zero on
`D`, so the second graph is an open domain `E` in `R^7`.

If the degree of the first-graph third equation `r_3` in `y` is `d`, the
verifier constructs the full cleared equation

\[
R=A_2^d r_3(y=-B_2/A_2)
\]

over `Z`, then primitive-normalizes it only by a nonzero integer scalar.
Because `A_2` is a unit, `R=0` is exactly the third zero-set on `E`.

Each record selects two remaining coordinates `z_i,z_j` and a sign
`epsilon` in `{+1,-1}`.  It verifies the exact integer identity

\[
                 (D_i+\epsilon D_j)^2R=0.                 \tag{1}
\]

Make the integral coordinate change

\[
                 z_i=u,\qquad z_j=\epsilon u+s.
\]

The corresponding two-by-two matrix is

\[
\begin{pmatrix}1&0\\ \epsilon&1\end{pmatrix},
\]

which has determinant one.  Extending it by the identity gives a
`GL_7(Z)` homeomorphism, with `partial_u=D_i+epsilon D_j`.  Identity (1)
therefore says that the **fully cleared** final equation is affine in `u`.
The standard one-equation affine-fiber lemma over the complementary
six-dimensional open base excludes compact connected components.  This
includes both final rank drops: when the `u` slope vanishes and the constant
does not, the fiber is empty; when both vanish, the open vertical `u` fiber
is contained in the zero-set.  The two unit-graph homeomorphisms and the
unimodular change preserve components and compactness, so every certified
original triple has no compact component.

Notice that this theorem tests the final cleared polynomial itself.  It does
not assume that `A_2`, `B_2`, or the pre-substitution third equation is
independent of the primitive direction.

## Exact artifact and independent replay

`data/DIAG3_triple_primitive_final_direction_certificates.bin` stores one
witness for each of the 23 rows.  Six use the canonical type-51/pivot-5 first
chart and 17 use type-51/pivot-6.  For every record, the verifier reconstructs
over `Z`:

1. the anchor alignment and stabilizer transport;
2. both graph equations and both denominator-clearing operations;
3. the complete nonzero scalar and restricted-parent-bracket product for the
   second slope;
4. the full cleared final polynomial; and
5. the recorded second directional derivative, coefficient by coefficient.

It also parses the frozen direct-final certificate, pins its SHA-256 and
`58,673`-row union, and proves zero overlap.  With the optional source replay,
it checks all 23 rows against the unique post-double source and hashes the
remaining rows in canonical source order.

The modular two-Hessian screen was only a candidate producer.  Every retained
row is replayed over the integers.  No modular rejection and no unrecorded
primitive direction is used as mathematical evidence.

## Pinned counts and digests

| quantity | exact value |
|---|---:|
| primitive rows | `23` |
| pivot-5 / pivot-6 rows | `6 / 17` |
| distinct second-slope identities | `8` |
| full final-polynomial identities | `23` |
| direct-final overlap | `0` |
| direct plus primitive union | `58,696` |
| remaining triple rows | `1,162,359` |

The primitive artifact has `711` bytes and SHA-256
`af0d1964840975e324d2c0181e732142ccd4e35c88ab4fc2702b6c70e6389bde`.
Its record-stream semantic digest is
`8917815ae6b4c65c83b74e09d5ee8f3f18f237d9bd493fce04094ca3d8f0f055`,
and its sorted-row digest is
`a1af2ac4e6ff2b9e9037ebc8f9bf969485acda4ce5f50adaeb0ab24f96a4e971`.

The frozen direct-final dependency has SHA-256
`6ed192d1dd2f814ae914349ec2dbcc654ffb663669b85f1b289fa37feb147f26`.
The `1,221,055`-row source has SHA-256
`bdd29e7647a99429f38c7bc20e9e5b9b514dccf7cbf57f9cd9b1b36fec7e7d92`.
After removing the exact `58,696`-row combined union, the packed source-order
digest of the `1,162,359` remaining rows is
`6c477d76ec0173ab340db4c9f5b783d3638393d0714e58440bae35b143b02b6a`.

## Replay

Exact certificate and dependency-disjointness replay:

```bash
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/verify_diag3_triple_primitive_final_direction.py
```

Add exhaustive source membership and residue replay:

```bash
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/verify_diag3_triple_primitive_final_direction.py \
  --post-double-residue \
  /tmp/diag3-triple-work/diag3_post_double_graph_residue.bin
```
