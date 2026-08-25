# Exact label continuation from row-2599 chart 0 to chart 89

The chart-0-to-chart-89 residual roadmap is now fully labelled on all 1,238 open chambers.  This closes the label-continuation gap on one exact parent-resident source path.  It does not supply global parent-cell coverage, does not close either invariant diagonal-three obligation, and leaves the honest 9DVL score at `2/9`.

## Hybrid exact continuation

The roadmap has 1,179 single-occurrence events and 58 compound events.  Re-enumerating all 26,112 topes in every chamber would require 1,238 complete arrangement runs.  The certified continuation instead uses two exact operations:

1. At a single-occurrence event, the changing four-row basis bounds exactly one antipodal pair of simplicial topes.  The verifier removes that pair and inserts the pair obtained by toggling the four basis signs.  All 1,179 ordinary events pass this local rule.
2. At a compound event, the verifier chooses a rational sample between that event's right isolating endpoint and the next event's left endpoint, exactly enumerates the post-event arrangement, and reorients it back to the raw row-2599 extension convention.  Only 58 complete enumerations are needed.

The exact parent reorientation is independently solved from all 70 parent-bracket signs.  Its 56-bit derived-row mask is pinned in the certificate.  After every update, all labels lie in the independently enumerated universe of 97,224 abstract row-2599 extensions.

## Result

- Every one of the 1,238 generic chambers has exactly 26,112 realizable extension labels.
- Every ordinary event exchanges one antipodal pair: two labels out and two labels in.
- Each of the 13 multiplicity-two compound events exchanges four labels in each direction.
- Each of the six multiplicity-15 events exchanges ten labels in each direction.
- Each of the 39 multiplicity-65 events exchanges 72 labels in each direction.
- The state after event 1,237 equals the independently stored raw chart-89 tope set exactly.
- The 97,224 signatures induce 2,458 distinct path profiles.  Of the signatures, 87,208 never change feasibility, 9,490 change once, 512 change twice, and 14 change three times.
- 66,000 signatures are never feasible on this path, while 21,208 persist through all 1,238 chambers.

The compound counts show why the first multiplicity-65 event could not honestly be treated as 65 unrelated basis flips: it is one structured localization mutation exchanging 72 labels on each side.

## Replay

```bash
python ai/omreal/build_diag3_pair_parent_source_labels.py
python ai/omreal/verify_diag3_pair_parent_source_labels.py
```

The verifier rebuilds the full transition, checks every local mutation, performs all 58 compound enumerations, reconstructs the target endpoint, pins the chamber, event and profile semantic digests, and rejects ten hostile corruptions.

## Next target

The objectively useful next step is no longer another local event rule.  It is source-path coverage: construct a finite graph of exact parent-resident transitions that embeds additional stored germs, records compatible overlaps, and attaches genuine parent-infinity faces.  This path is one certified edge of that future global master complex, not a cover by itself.
