# Diagonal three: exhaustive common-scaling no-go

## Exact result

The regenerated `1,162,302`-row final triple residue admits no nontrivial
common diagonal scaling in the nine normalized parent coordinates.

For a residual factor `q` with exponent support `A(q)`, a positive diagonal
action

\[
                 x_j\longmapsto e^{t w_j}x_j
\]

preserves `Z(q)` whenever every exponent in `A(q)` has the same `w`-weight.
The weight therefore lies in the kernel of the exponent-difference rows
`alpha-alpha_0`.  The verifier reconstructs those rows from the exact global
factor table and proves that their union has rank nine already over
`F_2` for every final-residue triple.  Rank over `Q` is consequently nine,
so the common kernel is zero.

This is exhaustive, not a hard-canary sample.  It is also a negative
checkpoint: it retires one genuine normalized-coordinate torus route but does
not prove compact-component escape and does not change the honest score from
`2/9`.

A second exact bounded regression tests the stronger polynomial-ideal equation

\[
             V(q_i)=\sum_j L_{ij}(x)q_j.
\]

Here every coordinate of `V` has total degree at most two and every `L_ij` is
affine-linear.  For five pinned hard triples, all `585` coefficient unknowns
are independent already modulo `1,000,003`; the rational kernels are zero.
Thus neither a common diagonal action nor this larger low-degree algebraic-flow
language is a viable universal closure theorem.  The second statement is a
hard-canary no-go rather than an all-residue census.

## Exact pins

| quantity | value |
|---|---:|
| final residue rows | `1,162,302` |
| final residue bytes | `6,973,816` |
| rows with rank nine over `F_2` | `1,162,302` |
| rows with a common scaling | `0` |

The pinned residue SHA-256 is

```text
34eee303b7981594805958f5dda79058880af66b54f685035ff9c16ee0073cd9
```

and the rank-stream semantic digest is

```text
d83b42d9a5bd05536829e75e3dd507efa8c2855962a18eed85080c7048e63b9e
```

## Replay

After regenerating the final residue through the pinned union, sequential,
double-graph, direct-final and primitive-direction layers, run

```bash
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/verify_diag3_triple_common_scaling_no_go.py \
  /path/to/diag3_final_residue.bin
```

The theorem-safe conclusion is only the stated no-go.  A future triple
closure must use a projection-critical/roadmap certificate or a strictly
stronger nonlinear structure.

Replay the bounded ideal-flow regression independently with

```bash
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/verify_diag3_triple_quadratic_ideal_flow_no_go.py
```
