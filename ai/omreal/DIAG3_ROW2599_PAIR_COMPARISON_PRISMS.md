# Exact row-2599 `p12` and `p20` comparison prisms

Together with `DIAG3_ROW2599_P01_COMPARISON_PRISM.md`, this certificate closes
the comparison-prism gate for all three pair edges in the row-2599 chart-zero
canary.

For `p12` and `p20`, the stored tapered pair sweep is divided into two equal
pieces and interpolated to the previously certified two-stage parent-wall
collar.  Exact tensor Bernstein replay proves on every bivariate patch that
all 70 parent signs are preserved and both incident Gordan cofactor circuits
remain nonnegative and nonzero.  The internal faces cancel, both endpoints
collapse on parent-frontier points, and both opposite faces are relative.

After taking the joined block-mass product, the ordinary integral boundaries
are

```text
+ K(p12) - Q(p12,block1) + Q(p12,block2),
+ K(p20) - Q(p20,block2) + Q(p20,block0).
```

Combined with the earlier p01 prism, this advances the row-2599 comparison
ledger to **3/6**.  The six named singleton lateral disks do **not** cancel:
for each block, its two incident pair-edge disks are distinct.  Constructing
the `H0`, `H1`, and `H2` prisms means joining exactly those three pairs with
the correct orientations.  The primitive mixed chain `J`, a regular global
subdivision, and a coverage certificate also remain open.

Producer replay:

```bash
PYTHONDONTWRITEBYTECODE=1 python ai/omreal/verify_diag3_row2599_p12_p20_comparison_prisms.py
```

Expected semantic digest:

```text
48871bfbc021051f4f672eaf6372ecd5d1d0f0324005648b8d471e130b60e8f8
```

Independent dense-bivariate replay:

```bash
PYTHONDONTWRITEBYTECODE=1 python ai/omreal/review_scratch/DIAG3_HOSTILE_VERIFY_ROW2599_P12_P20_COMPARISON_PRISMS.py
```

Expected independent semantic digest:

```text
930d28e2fbc1990cb68e403b034b3ec7aa440a455b5017a13aa1426e1336dba4
```

Both replays reconstruct the pinned row-2599 source with SHA-256
`3b90799d26b7783e92c2ac697eaaf8b76d26a787f53205873b997657e114180a`.
