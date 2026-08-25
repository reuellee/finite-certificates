# Diagonal three: exact multi-box master-closure canary

## Result

The full-support master-closure compiler now glues a declared finite atlas,
not just one monolithic node disk.  In the two exact residual-branch
coordinates of the row-2599 transverse node, it covers a rational rectangle
by a `3 x 3` box grid:

| box class | count | exact content |
|---|---:|---|
| no wall | 4 | both residual branch signs are constant |
| one wall | 4 | exactly one branch crosses the box interior |
| transverse two wall | 1 | both branches cross at the unique node |
| unclassified | 0 | none |

The atlas has 32 atomic boundary-word segments.  Sixteen are shared by two
boxes, and every shared segment has the same exact open-segment sign word with
opposite boundary orientation.  The outer boundary and all internal box seams
remain ordinary cells.  The true parent-infinity subcomplex is empty.

This is a local two-dimensional theorem.  The honest 9DVL score remains
**2/9**; no global row-2599 coverage or diagonal-three closure is claimed.

## Exact coordinate contract

Let `q0,q1` be the values of the two coprime affine residual branches after
centering at their exact intersection.  Their gradient matrix has nonzero
determinant

```text
105235885034684851065341346040320.
```

The declared branch-coordinate domain is

```text
-3*10^12 <= q0,q1 <= 3*10^12,
```

with box cuts at `-10^12` and `10^12`.  Inverting the exact gradient matrix
maps every domain vertex strictly inside the already certified
radius-`1/1000` source square; the largest absolute centered source coordinate
is approximately `0.000484019`.

Therefore the independent replay of the source disk applies unchanged:

- all `84,840` labelled residual determinant restrictions reduce to the two
  declared branches or a nonvanishing factor;
- both branch quotient families remain nonzero;
- all `70` parent brackets remain nonzero; and
- the two branches remain transverse.

## Global regular-CW refinement

Adding the two residual axes and the two box-seam levels in each coordinate
gives an exact `4 x 4` rectangular refinement:

| dimension | cells |
|---:|---:|
| 0 | 25 |
| 1 | 40 |
| 2 | 16 |
| total | 81 |

The certificate stores all 208 strict closure-comparable pairs, all 128
vertex-edge-face chains, and canonical integral cellular boundary matrices.
Horizontal and vertical edges point in increasing `q0` and `q1`; rectangles
carry the counterclockwise orientation.  The verifier regenerates every
incidence and proves `d^2=0` over the integers.

The barycentric two-skeleton has 81 vertices, 208 edges and 128 triangles.
Using the complete `97,224`-signature profile census from the exact node, the
verifier reconstructs all closed bad subcomplexes and replays every one of the
`6^3=216` ordered profile triples.  All have zero middle cohomology over
`F_2`.  The exact histogram `(dim C1, rank N, rank M, dim H1)` is

```text
(0,0,0,0): 16       (8,8,0,0): 12       (56,24,32,0): 24
(108,44,64,0): 36   (116,52,64,0): 36   (164,68,96,0): 24
(208,80,128,0): 3   (216,88,128,0): 52  (316,124,192,0): 12
(416,160,256,0): 1
```

## Trust separation

The deterministic producer is

```console
python ai/omreal/build_diag3_pair_master_closure_multibox_canary.py
```

and writes
`data/DIAG3_PAIR_MASTER_CLOSURE_MULTIBOX_CANARY.json`.

The independent verifier is

```console
python ai/omreal/verify_diag3_pair_master_closure_multibox_canary.py
```

It reconstructs the exact source geometry, branch-coordinate containment,
box classification, shared-boundary sign words, global closure, signature
profiles, integral incidence and all 216 ranks.  It rejects ten hostile
corruptions: sampled coverage, an unsigned domain expansion, a missing box, a
corrupt boundary word, false parent infinity, incomplete closure, incomplete
signature accounting, a corrupt active-factor digest, nonzero `d^2`, and a
dishonest stop ledger.

## Stop contract and next target

The declared ceiling was nine boxes; all nine are classified, so this run is
inside its ceiling.  It did not automatically enlarge the domain.

The next bounded experiment should expand within this same exact
two-dimensional parent plane only until the **first new residual event not
belonging to the two pinned branches**.  It should use a ceiling of 64 boxes.
Success is either:

1. a second exact event cluster glued into the atlas with the same proof
   object and rank replay; or
2. a preserved, machine-readable first unclassified box or projection-growth
   frontier.

Either outcome is decisive about whether the multi-box backend scales beyond
the node canary without committing to a nine-dimensional decomposition.
