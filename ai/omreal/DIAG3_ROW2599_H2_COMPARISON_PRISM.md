# Exact row-2599 `H2` comparison prism

The `H2` origin residence component is an exact first-wall rectangle.  Its
parent frontier has two oriented pieces: one on `[1358]` from the `p12`
endpoint to the double-wall corner, and one on `[1256]` from that corner to
the `p20` endpoint.

For each piece, the verifier subdivides the common-ray sweep into two patches
and interpolates it to a relative surface: first keep the root amplitudes
fixed while reaching `[2467]`, then remove them while staying on `[2467]`.
The four trivariate patches preserve every parent sign and the fixed block-2
Gordan circuit.  Their common-parameter and frontier-corner faces cancel
literally.

Most importantly, the two external frontier faces are exactly—not merely
homologous to—the named block-2 disks from the certified `p12` and `p20`
comparison prisms.  With the chosen orientation the ordinary boundary is

```text
+ K(h2) - Q(p12,block2) + Q(p20,block2).
```

This advances the local row-2599 comparison ledger to **4/6**.  `H0`, `H1`,
the assembled primitive `J`, the global regular master subdivision, and
coverage remain open.

Producer replay:

```bash
PYTHONDONTWRITEBYTECODE=1 python ai/omreal/verify_diag3_row2599_h2_comparison_prism.py
```

Expected semantic digest:

```text
4027e41a519953200e205f4e7ab2453a83122822d6ca2ed60bb649cd60afc7a7
```

Independent reconstruction:

```bash
PYTHONDONTWRITEBYTECODE=1 python ai/omreal/review_scratch/DIAG3_HOSTILE_VERIFY_ROW2599_H2_COMPARISON_PRISM.py
```

Expected independent semantic digest:

```text
55539702e53abdcf15a1173a549699d87427f85881d66db881ff33c98586934b
```

Both replays reconstruct the source
`ai/omreal/data/seeat_parent2599_upper178.npz`, SHA-256
`3b90799d26b7783e92c2ac697eaaf8b76d26a787f53205873b997657e114180a`.
