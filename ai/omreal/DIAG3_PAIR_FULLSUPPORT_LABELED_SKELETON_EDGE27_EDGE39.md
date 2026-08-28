# Combined labelled source-skeleton candidate: edges 27 and 39

## Exact finite result

This candidate glues the accepted chart-0-to-chart-89 edge `27` and candidate
chart-0-to-chart-113 edge `39` at their unique common stored chart.  Chart `0`
appears exactly once.  The resulting regular-CW complex is a two-branch tree:

| datum | exact value |
|---|---:|
| zero-cells | 6,567 |
| one-cells | 6,566 |
| strict closure pairs | 13,132 |
| two-cells / strict three-cell chains | 0 / 0 |
| rank of integral `d1` | 6,566 |
| integral `H0` / `H1` ranks | 1 / 0 |
| true parent-infinity cells | 0 |
| fully compiled / pending cover edges | 2 / 38 |

Every oriented one-cell has boundary `-left + right`.  Edge 27 is oriented
from chart 0 to chart 89 and edge 39 from chart 0 to chart 113.  Connectivity
together with `E=V-1` proves the signed incidence is a tree and gives the
stated integral ranks.

## Joint signature profiles

The producer authenticates the accepted edge-27 profile catalog and the
edge-39 packed profile artifact, confirms their ascending 97,224-signature
universes agree, and concatenates their chamber bits in stable cell order.
This independently yields **11,719 distinct joint profiles**; that number was
computed, not assumed.

The deterministic packed artifact assigns every ascending signature a
32-bit profile ID.  Each lexicographically ordered profile contains:

- the complete 6,566-bit feasible one-cell bitmap;
- its complemented bad one-cell bitmap with zero padding;
- the 6,567-bit bad zero-cell bitmap derived from incidence.

At the shared chart-0 cell, bad membership is the disjunction of the first
chamber on both branches.  Thus every bad locus is a closed subcomplex of the
two-edge tree.

The joint feasible semantic SHA-256 is
`9fbf7b09ec75b7b27585d83e14fdc7703c21a43c7a37f5cda835df80748f769f`;
the incidence-derived bad-membership semantic SHA-256 is
`e2393519c039b00e7f96bfa5de11a0565bcd900ca04567d12c286b75d5866e76`.

## Authenticated collar attachment

The stable edge-39 cell

```text
row2599:edge:039:event:5236:factor:19069:root:0
```

maps to the accepted collar cell `w_zero`.  Increasing edge parameter is
`+s` from chart 0 to chart 113; the accepted collar wall is oriented `+r`
from `w_minus` through `w_zero` to `w_plus`.  Factor 19069 is positive before
and negative after the transverse edge crossing.  With collar orientation
`(s,r)`, the ordered tangents `(+s,+r)` give authenticated intersection sign
`+1`.

## Canaries and scope

The producer rejects duplicate chart 0, reversed edge-39 orientation, omission
of any of the 236 atoms belonging to two-root factors, splitting a compound
event, a flipped or nonzero-padding joint profile bit, an incorrect
factor-19069 event, invented parent infinity, and promotion of the two-edge
tree to global coverage.

This is exact coverage of two finite retained source paths only.  It is not
coverage of residual components or the row-2599 parent cell, supplies no
two-cells, closes neither diagonal-three obligation, and leaves the honest
9DVL ledger at `2/9`.

## Replay

```console
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/build_diag3_pair_fullsupport_labeled_skeleton_EDGE27_EDGE39.py
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/check_generated_diag3_pair_fullsupport_labeled_skeleton_EDGE27_EDGE39.py
```

The checker is producer-side structural replay, not an independent verifier.
The combined candidate remains fail-closed until a separately embodied
verifier reconstructs its topology, attachment, and joint profile mapping.

Raw artifact SHA-256 values are:

| artifact | SHA-256 |
|---|---|
| combined skeleton JSON | `dcb707220df3e61b1a94eeedcf8e46b6602f30d405f4a92fc542c0f52f672806` |
| joint packed profiles | `cbc8b02f7c4f6840ee267d56403b11a36722291216a69eb0de04d0084627cd1d` |
