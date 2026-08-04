# A second exact ninth-diagonal stress path

## Result

The complete 178-chart row-2599 point sample was labeled by enumerating all
26,112 topes of each chart's derived arrangement.  A greedy antichain-aware
separator search found nine signatures whose common support in that sample
is exactly charts 37 and 176.  These are a different endpoint pair and a
different signature family from the earlier charts-12/37 test.

The apparent separator is false in the actual realization space.  The two
endpoint incidences are joined inside the common nine-signature feasibility
locus by an exact rational coordinate path with

\[
                 11,701+3,009+8,101=22,811
\]

segments.  Every segment changes one homogeneous column.  Every constrained
determinant is therefore constant or affine on that segment, and exact strict
positivity at both endpoints certifies the full closed segment.

The companion antichain artifact uses seven additional exact row-2599 charts.
For each of its 63 chart/signature entries it stores either a strict integer
extension ray or a positive integer Gordan circuit of support at most five.
Its seven truth patterns distinguish all 72 ordered signature pairs.  Hence
the nine regions are globally nonempty, proper, and pairwise incomparable;
this is not merely a property of the discovery matrix.

## Discovery boundary

`build_ninth_sample_topes.py` handles both simple rank-one flats and the
structural non-simple flats of sizes 7 and 21.  It requires exactly 26,112
topes on every one of the 178 charts and writes a packed chart/signature
matrix.  Floating point is used in that builder, so its matrix is a search
aid only.  The theorem above depends exclusively on the independently
checked integer antichain and path artifacts.

This result does **not** prove the ninth diagonal.  The 178 charts cover the
individual extension signatures but do not cover the residual chambers or
their adjacencies.  The result supplies a second adversarial regression for
any proposed master-roadmap algorithm and shows that isolated vertices in the
point-cover support graph are not component certificates.

## Reproduction

```console
python ai/omreal/build_ninth_sample_topes.py --workers 8
python ai/omreal/verify_ninth_candidate_generic.py antichain \
  ai/omreal/data/ninth_candidate_37_176_antichain.npz
python ai/omreal/verify_ninth_candidate_generic.py path \
  ai/omreal/data/ninth_candidate_37_176_path.npz
```
