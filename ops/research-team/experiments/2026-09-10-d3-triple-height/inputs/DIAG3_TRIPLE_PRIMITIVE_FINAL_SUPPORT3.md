# Diagonal three: support-three primitive final directions

## Honest result

This positive layer starts from the exact `1,221,055`-row post-double source.
The direct-final-coordinate and support-two primitive certificates close a
disjoint union of `58,696` rows.  The present certificate proves **57 more
rows**, with zero overlap, leaving `1,162,302` triple rows open.

This bounded type-51/pivot-6 construction is not a maximality theorem for
primitive directions.  It does not close the triple obligation or the
exclusive-pair middle-exactness obligation, so the score remains `2/9`.

## The exact theorem

On an open uniform parent cell, graph the first residual equation in pivot 6.
Its exact slope is

\[
                       -[1236][2467],
\]

which is a unit.  On that open graph domain, every certified second equation
has the form

\[
                       r_2=A_2(v)y+B_2(v),
\]

where the certificate writes `A_2` exactly as a nonzero scalar times a
product of graph-restricted parent brackets.  Thus the second equation is
another unit graph.

The verifier forms the full cleared third equation

\[
               R=A_2^d r_3(y=-B_2/A_2)
\]

over `Z` and primitive-normalizes it only by a nonzero integer scalar.  Here
`d` is the degree of the first-graph equation `r_3` in `y`.  Since both graph
slopes are units, these graphings and denominator clearings preserve the
original zero-set and its connected components.

Each record selects three remaining coordinates `z_i,z_j,z_k` and signs
`epsilon_j,epsilon_k` in `{+1,-1}`.  It proves the exact polynomial identity

\[
  (D_i+\epsilon_jD_j+\epsilon_kD_k)^2R=0.                 \tag{1}
\]

Use the integral coordinate change

\[
 z_i=u,\qquad z_j=\epsilon_j u+s,\qquad
 z_k=\epsilon_k u+t.
\]

Its three-by-three matrix is lower triangular with diagonal `(1,1,1)`, so it
lies in `GL_3(Z)`.  Its `u` derivative is the directional derivative in (1).
Consequently the fully cleared final equation is affine in `u` on an open
domain in `R^7`.  The one-equation affine-fiber lemma over the complementary
six-dimensional base excludes compact components.  This includes the
final-slope rank drop: a consistent zero-slope fiber contains an open
vertical `u` interval, while off that locus the zero-set is a graph.

## Certificate contract

`data/DIAG3_triple_primitive_final_support3_certificates.bin` stores one
witness for each of the 57 rows.  The independent verifier reconstructs over
`Z`:

1. the canonical anchor alignment and stabilizer transport;
2. the first graph and its exact slope product;
3. all 34 distinct second-slope parent-unit products;
4. all 57 fully cleared final polynomials; and
5. every support-three second directional derivative coefficient.

It parses and pins the frozen direct-final and support-two certificates, proves
that their `58,696`-row union is disjoint from these 57 rows, and optionally
replays source membership and the resulting residue.  The finite-field
two-Hessian calculation was only a candidate screen; every retained identity
is checked over the integers.  No modular rejection or negative exhaustion
claim is used.

## Pinned values

| quantity | exact value |
|---|---:|
| new support-three rows | `57` |
| prior accepted union | `58,696` |
| overlap | `0` |
| combined union | `58,753` |
| distinct second-slope products | `34` |
| full final identities | `57` |
| remaining rows | `1,162,302` |

The 1,771-byte certificate has SHA-256
`c900dd68143d6228847124e4bc5891f440e0d116e2aabbaf2f0e28647f9fdbb3`.
Its record-stream semantic digest is
`71df56d10ebd93be6f4c59f626d38d9a992264b2cbaf74fe0070618fed4a0de0`,
and its sorted-row digest is
`4aa31365ba2f8dd9f429b5dd5ffbbc735f161c68dc5605372a597892da65965b`.

The pinned `1,221,055`-row source has SHA-256
`bdd29e7647a99429f38c7bc20e9e5b9b514dccf7cbf57f9cd9b1b36fec7e7d92`.
After deleting the exact `58,753`-row combined union, the packed source-order
digest of the `1,162,302` remaining rows is
`a76a7c2cd6631c2d9724b450540bec7f3be6c106a41ae41f1736bbd2755a5ca4`.

## Replay

```bash
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/verify_diag3_triple_primitive_final_support3.py

PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/verify_diag3_triple_primitive_final_support3.py \
  --post-double-residue \
  /tmp/diag3-triple-work/diag3_post_double_graph_residue.bin
```
