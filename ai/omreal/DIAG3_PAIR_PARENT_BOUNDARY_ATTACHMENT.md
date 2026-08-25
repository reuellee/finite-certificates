# Exact chart-89 attachment to the parent divisor `[1237]=0`

## Outcome

The labelled row-2599 source skeleton now reaches genuine parent infinity. In
the pinned `(Delta^3)^3` compactification, linearly decreasing normalized
variable 5 at chart 89 reaches the coordinate divisor for moving column 7,
row 4. The compactification atlas identifies that divisor exactly with the
parent bracket `[1237]=0`.

All 69 other parent brackets remain positive at the endpoint. None of the
17,824 candidate residual factors vanishes there. The open ray crosses 1,517
pairwise ordered simple residual roots and its 1,518 generic chambers are all
labelled exactly. The endpoint itself is placed in the relative parent-infinity
subcomplex and contributes no relative chain generator.

This is the first proof-bearing genuine-boundary attachment from the labelled
source complex. It is not global parent-cell coverage and leaves the honest
9DVL score at `2/9`.

## Objective source selection

The producer audits all `178 x 9 = 1,602` finite normalized coordinate-collapse
rays. Exactly 29 stay in the weak parent closure and meet a single parent
divisor; all 29 meet `[1237]=0`. Among the currently labelled source charts
`0`, `89`, and `152`, chart 89 supplies the unique such ray.

## Residual and CW data

| quantity | exact value |
|---|---:|
| candidate residual factors | 17,824 |
| root-free restrictions | 16,307 |
| one-root restrictions | 1,517 |
| endpoint residual zeros | 0 |
| regular-CW zero-cells | 1,519 |
| regular-CW one-cells | 1,518 |
| total cells | 3,037 |
| strict closure pairs | 3,036 |

The root-event semantic digest is

```text
211f60ef3a445c16e35cae40cba270ec5f552152dccc99a1abfbd4c0a84d1bf1
```

## Label continuation

The 1,517 crossings split into 1,454 antipodal simplicial mutations and 63
exact compound re-enumerations:

| factor multiplicity | events | labels lost and gained |
|---:|---:|---:|
| 2 | 16 | 4 |
| 15 | 6 | 10 |
| 65 | 41 | 72 |

Every generic chamber has 26,112 labels in the 97,224-signature universe. A
fresh exact enumeration between the last residual event and the parent endpoint
independently reconstructs the final open-chamber label set. The path produces
3,029 distinct signature profiles. Its profile and event-label digests are:

```text
102a36f099781ba36f8df85c4a042e5bceb72d0abc08be84bcbf8a32fcbf3778
5ce4cd3124c42e8d64e032acaa2e5047c9a6319c0535c1d2607ff58ec08b4812
```

## Replay

```bash
python ai/omreal/build_diag3_pair_parent_boundary_attachment.py
python ai/omreal/verify_diag3_pair_parent_boundary_attachment.py
python ai/omreal/build_diag3_pair_parent_boundary_labels.py
python ai/omreal/verify_diag3_pair_parent_boundary_labels.py
```

The two hostile verifiers replay the compactification-divisor identity, all 70
parent brackets, all 17,824 residual restrictions, every exact label update,
the endpoint-near reconstruction, and the relative-boundary tag. Each rejects
12 targeted corruptions.

## Remaining gap

One relative end proves that the source skeleton has a genuine boundary
attachment; it does not prove that every nonrelative master cell or every
bad-locus component reaches that skeleton. The remaining pair target is a
missed-component certificate or an equivalent structural global-closure
theorem. Diagonal three also retains its independent 1,162,302-row triple
compact-component obligation.
