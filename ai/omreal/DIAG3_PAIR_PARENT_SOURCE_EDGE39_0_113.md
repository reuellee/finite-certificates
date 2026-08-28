# Exact retained source-cover edge 39: charts 0 to 113

## Finite exact result

This generator-side certificate completes the residual roadmap and extension-
signature continuation on retained source-cover edge `39`, the exact straight
segment from stored row-2599 chart `0` to chart `113`.

All 70 signed parent brackets are strictly resident on the closed segment.
Across exactly the 17,824 pinned candidate residual factors, exact Sturm
counting and rational isolation give:

| quantity | exact value |
|---|---:|
| factors with 0 / 1 / 2 interior roots | 12,615 / 5,091 / 118 |
| rooted factors | 5,209 |
| ordered root events | 5,327 |
| endpoint roots | 0 |
| repeated or tangential roots | 0 |
| coincident roots from distinct factors | 0 |
| simple / compound events | 5,034 / 293 |

The ordered flips exactly reconstruct the stored chart-113 factor state.  The
generator does not assume genericity: it computes algebraic multiplicity by
polynomial gcd, groups shared algebraic roots by exact gcd, and contains
hostile self-checks for endpoint, tangential, and coincident roots.

## Complete label continuation

Every simple event exchanges one antipodal simplicial tope pair.  The 293
compound events are not decomposed heuristically: the generator exactly
re-enumerates the post-event arrangement at a rational sample.  Their exact
delta census is:

| occurrence multiplicity | events | lost / gained labels |
|---:|---:|---:|
| 2 | 71 | 4 / 4 |
| 15 | 43 | 10 / 10 |
| 65 | 179 | 72 / 72 |

All 5,328 open chambers have 26,112 labels from the fixed universe of 97,224
extension signatures, and the terminal state equals the independently stored
raw chart-113 state.  The materialized packed artifact has 666 bytes per
signature and 10,571 distinct profiles.  Profile transition counts are 56,054
with zero changes, 35,082 with one, 6,006 with two, and 82 with three.  Exactly
47,624 signatures are never feasible and 8,430 persist through all chambers.

The gzip payload format is stable and simple: eight-byte magic `D3E39P1\0`,
three little-endian `uint32` values (signature count, chamber count, packed row
width), followed by ascending `(uint64 signature, packed chamber bitmap)` rows.
The gzip timestamp is fixed to zero.

## Collar binding and exact scope

Factor `19069` occurs at ordered event `5236`.  Its transition isolating box

```text
[4157447/4194304, 519681/524288]
```

intersects the accepted factor-19069 collar's `w_zero` root box.  This supplies
a stable `row2599:edge:039` interface for a future labelled-skeleton compiler.

The result covers only this one closed segment and the already accepted local
factor-19069 collar attachment.  It does **not** cover the row-2599 parent cell,
does not classify components outside that collar, does not close the pair or
triple obligation, and does not change the honest `2/9` ledger.

## Replay

From repository root:

```console
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/build_diag3_pair_parent_source_transition_EDGE39_0_113.py
PYTHONDONTWRITEBYTECODE=1 DIAG3_EDGE39_LABEL_WORKERS=4 python \
  ai/omreal/build_diag3_pair_parent_source_labels_EDGE39_0_113.py
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/check_generated_diag3_pair_parent_source_EDGE39_0_113.py
```

The last command is a producer-side self-consistency check, not an independent
acceptance verifier.  Publication still requires a separately embodied parser,
root/event replay, label/profile reconstruction, canary suite, and scope audit.

Raw artifact SHA-256 values at this commit:

| artifact | SHA-256 |
|---|---|
| transition JSON | `cb6eebc0df9bfeae8055c81471f09d594f8116e002caf11f62f9e865b0936dd7` |
| label JSON | `dc80acaf2f711ee5e0e053e856e4abf858adf90483ba0e5ced13018bdb909170` |
| packed profiles | `77b042d72e4c28dc5e60145624adfd27b080aaec8aa757cdf10c0d7c5513e6b6` |

Pinned accepted dependencies are the decision ledger `b87172fb...`, segment
cover `19248dd...`, existing partial labelled skeleton `5430bd79...`, and
factor-19069 collar `5930cc19...`.
