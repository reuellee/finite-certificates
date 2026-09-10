# Constructive audit

The stable initial reserve/full56 certificate is independently accepted.
`verify_constructive_independent.py` imports no constructive code. It computes
polynomial determinants by permutation expansion from the literal parent.
All70 bracket polynomials and all56 signed-normal polynomials are rebuilt.

The maximal strict parent interval containing zero is exactly
`(-75255/111104, 94285/38192)`. On the certified closed interval
`[-75255/222208, 75255/222208]`, all70 expected signs persist and the smallest
absolute parent bracket is155. This is a full-interval result because the
independently computed bracket polynomials are affine.

The reserve support `[17,24,33,40,54]` avoids the moving parent column.
Its five augmented columns have determinant `82630141776`, and its supplied
constant positive normalized weights satisfy all five equations. Hence its
signed normals have rank four and its reserve is valid for every parameter.

The full56 affine weight vector satisfies the four normal equations as
polynomial identities and has constant total weight one. Every coordinate
is at least `1/1000` on the entire closed interval. Ten independently applied
hostile mutations are rejected, including a wrong interval, derivative,
signature, parent, reserve support, reserve weight and claimed margin.

The original three-row support has exact rank two at zero and exact rank
three at every nonzero parameter, certified by the polynomial minor
`-27081600*t`. The new full56 curve differs from the original three-row
weight vector at zero. It is a robust replacement section, and does not by
itself assert equality to that initial weight vector.

The frozen certificate also supplies a distinct source-matching curve
`h(t)=(u+C|t|q-t v)/(1+C|t|)` with
`C=2205884133/880139125`. Independent replay accepts this added curve:
`h(0)=u` is exactly the original three-row normalized witness; both one-sided
normal identities hold as polynomial identities; normalization is exact;
all reserve slacks `Cq_i-|v_i|` are strictly positive. The denominator is
positive and the numerator is coordinatewise nonnegative for every real t.
Its support is the six-index union away from zero. Its claim within the
original parent chamber remains restricted to the certified interval.
Three additional hostile controls corrupting the correction vector, C, and
the zero-parameter join are rejected. Thirteen constructive hostile controls
pass in total.

## Written selection lemma

The proof in constructive/FINDINGS.md is valid for parent parameters in an
open real domain (or a metric space). A full-row-rank augmented matrix and
one strictly positive full-coordinate feasible vector give nearby feasible
approximants to every initial feasible vector. Compactness of the common
simplex and strict convexity of squared norm then prove continuity of the
unique minimizer. The supplied fixture verifies both hypotheses, including
at its interval endpoints. By the same open-condition argument the statement
holds on some open parent neighborhood around each fixture point; this is
an existential neighborhood statement, not a certified numerical radius.

This is a standard convex-feasibility lemma with a supplied proof, not a
claim of a new general theorem. The explicit full56 witness is not asserted
or checked to minimize norm. Continuity of the actual minimizer follows from
the lemma, rather than sampled optimization results.

The Euclidean selector is defined in the specified literal raw-normal gauge.
Positive row rescalings transport feasible normalized weights continuously,
but do not generally preserve their Euclidean minimum. No gauge-independent
canonical selector is certified here.

## Original target boundary

The result is local to one parent family and one fixed signature. It proves
neither unconditional selection on all bad parents nor compatibility between
multiple signature blocks, true-infinity attachments, compact-support maps,
the joint pair-map injectivity or triple Hc0 vanishing. All original ledger
counts and global obligations remain unchanged at2/9.

Status: **ACCEPT RESERVE/FULL56 CERTIFICATE, SOURCE-MATCHING SUPPORT6 LIFT,
AND CONDITIONAL LEMMA**.
