# Exact row-2599 `p01` comparison prism

## Result

The nonrelative swept pair face `K(p01)` is joined to the certified nonradial
`p01` parent-wall collar by a five-patch exact semialgebraic homotopy.  Both
incident bad blocks retain explicit nonnegative Gordan cofactor circuits on
every patch, and all 70 parent-bracket signs are preserved.  Taking the
product with the pair block-mass interval gives a singular comparison
three-chain with signed ordinary boundary

```text
+ K(p01) - Q(p01,block0) + Q(p01,block1).
```

The five opposite faces lie on the certified parent frontier, the two endpoint
faces collapse on parent-frontier points, and the four internal patch faces
cancel in pairs.  Thus every face of this one comparison prism is accounted
for.  This certifies **one of six** row-2599 comparison incidences.

It does **not** close the local mixed `d3`: the two named singleton lateral
disks must still be joined to the distinct corresponding lateral faces of the
`H0` and `H1` comparison prisms.  The separate `p12`/`p20` certificate brings
the pair-edge total to three, but all three singleton prisms and the primitive
mixed chain `J` remain missing.  This result also says nothing about the global
compactified master subdivision.

## Construction

The relative boundary is the four-stage tangent collar from
`DIAG3_ROW2599_P01_TANGENT_COLLAR.md`.  Positive projective gauges are inserted
at its two rational seams, producing five literally glued polynomial stages.
The stored tapered `K(p01)` sweep is subdivided into five equal parameter
intervals.  Straight interpolation between corresponding stages gives the
five bivariate patches.

For every patch the certificate verifies, over `Q`:

1. all 70 prescribed parent signs by tensor Bernstein coefficients;
2. the fixed block-0 and block-1 Gordan cofactor kernels and nonnegativity;
3. literal internal seams and collapsed endpoint faces;
4. equality of the `v=0` face with the stored `K(p01)` subdivision;
5. an identically zero parent bracket on every `v=1` face; and
6. the integral product-boundary signs above.

Self-intersection is harmless here: this is a certified singular
semialgebraic chain.  Any later regular master subdivision must subdivide it
compatibly rather than assume it is already a regular cell.

## Replay

Producer replay:

```bash
PYTHONDONTWRITEBYTECODE=1 python ai/omreal/verify_diag3_row2599_p01_comparison_prism.py
```

Expected semantic digest:

```text
0b015361e1c75007f025e90921fa5f295616b0e3e8d4bbf941e5161545e433c7
```

Independent dense-bivariate replay (separate polynomial representation and no
production-prism imports):

```bash
PYTHONDONTWRITEBYTECODE=1 python ai/omreal/review_scratch/DIAG3_HOSTILE_VERIFY_ROW2599_P01_COMPARISON_PRISM.py
```

Expected independent semantic digest:

```text
acca3573a369139c9a142592febcaa55ce453eeb10c1d52631ac5b226129127b
```

The pinned source is
`ai/omreal/data/seeat_parent2599_upper178.npz`, SHA-256
`3b90799d26b7783e92c2ac697eaaf8b76d26a787f53205873b997657e114180a`.
