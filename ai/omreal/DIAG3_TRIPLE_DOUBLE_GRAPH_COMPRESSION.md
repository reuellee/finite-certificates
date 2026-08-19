# Diagonal three: exact double-graph triple compression

## Outcome and honest scope

An exact two-stage graph layer closes `417,828` rows of the `1,638,903`
sequential-affine triple residue. The construction scan traversed all 45
parent-unit first-graph charts across the twelve canonical occurrence
formulas; the tracked certificates prove the positive union, not independent
maximality of the scan's negative answers. Pivot 3
of type 49 closes `107,778`; its pivot-1/5 extension adds `1,086`; the generic
all-chart certificate adds `308,964` disjoint rows.

The independent verifier is
`verify_diag3_triple_double_graph_scan.py`. Its compact certificate is
`data/DIAG3_triple_double_graph_type49_pivot3_certificates.bin`, with the
disjoint pivot-1/5 increment in
`data/DIAG3_triple_double_graph_type49_extension_certificates.bin` and the
other positive charts in
`data/DIAG3_triple_double_graph_generic_certificates.bin`.

This advances the compact-component obligation but does **not** finish it,
prove global exclusive-pair middle exactness, or change the score from `2/9`.
The separate unit-minor-after-graph layer closes 117 rows, 97 of which overlap
the pivot-3 layer. Exactly 20 unit-minor rows remain outside the full
double-graph union. Their exact combined union closes `417,848`, leaving
`1,221,055` after both layers. The counts must not be added without that
overlap correction.

## The double-graph theorem

Let `X` be a fixed uniform parent cell. A recorded factor triple first has

\[
q_1=A_1(w)x+B_1(w),
\]

where `A_1` is a nonzero scalar times a product of parent brackets. Hence
`A_1` is nowhere zero on `X`, and graphing `q_1=0` identifies its zero set
with an open subset of `R^8`. All following restrictions are cleared by the
required power of `A_1`; this multiplication by a unit does not change a zero
set on the graph domain.

On that graph the certificate gives

\[
q_2=A_2(u)y+B_2(u),
\]

where `A_2` is an exact scalar times a product of restrictions of parent
brackets. A parent bracket is nowhere zero on `X`, so its restriction to the
first graph is nowhere zero. Thus `A_2` is a unit on the pulled-back open
domain. Graphing `q_2=0` gives an open subset of `R^7`.

Finally, the record selects a coordinate `z` such that:

1. neither `A_2` nor `B_2` depends on `z`; and
2. the first-graph restriction of `q_3` is affine in `z`.

Substitution `y=-B_2/A_2`, with its unit denominator cleared, therefore
cannot raise the `z` degree. The last equation has the form

\[
C(v)z+D(v)=0
\]

on an open subset of `R^6 x R`. Every connected component of this zero set
is noncompact. Where `C=0`, consistency gives the entire open vertical
fiber; where `C` is nonzero, the zero set is a graph over an open subset of
the positive-dimensional base. This includes the final slope rank-drop
locus and makes no generic-rank deletion.

The two graph homeomorphisms preserve connected components and compactness.
Consequently every certified original triple zero set is componentwise
noncompact.

## Exact coverage and independent replay

For every source row, the construction scan tried each compatible canonical
factor as first anchor, its complete canonical stabilizer, both orders of the
two remaining factors, every second coordinate having an exact
restricted-parent unit slope, and every final coordinate satisfying the two
degree conditions. The first lexicographic hit gives a deterministic positive
record. The certificate replays these positive records exactly; a future
pinned census manifest is needed before treating zero per-chart construction
counts as an independently replayed maximality statement.

The verifier does not trust producer masks. From the global factor
certificate it independently reconstructs:

* the anchor alignment and stabilizer transport;
* both cleared graph restrictions and both reconstruction identities;
* for pivot 3, all 1,450 distinct exact restricted-parent slope products over
  `Z`, 1,526 final-coordinate independence conditions, 5,513 third-factor
  affinity conditions, and 21 explicit final-substitution regressions;
* for the pivot-1/5 extension, all 17 slope identities, 22 independence
  conditions, 499 affinity conditions, and one explicit final-substitution
  regression per used coordinate triple.
* for the generic increment, 4,931 slope identities, 5,526 independence
  conditions, 23,736 affinity conditions, and 116 explicit
  final-substitution regressions.

It also pins the binary layout, EOF, unique-row count and semantic digest.
With `--sequential-residue`, it independently checks that all `108,864` rows
from the type-49 artifacts and all `308,964` generic rows belong to the unique
`1,638,903`-row source.

The exact pins are:

```text
sequential residue rows       1,638,903
sequential residue SHA-256    5ba2314c94ba115d5bf5e975e68412e3f4b44e2c65df51b757f6150a3352d4e1

certificate rows              107,778
certificate bytes             2,936,122
certificate SHA-256           52c9fec437378098e06a37c74396230b8e501b22bf8c7c5df07ef131e9aaa9c0
certificate semantic          98619fff126cc4e10331735fe691cde7f8e3a4f4983b31c63fbf5cd50616c5c9

extension rows                1,086
extension bytes               31,884
extension SHA-256             1dc677cd3d46d774c7ba629606ec9b9483e1fda8c97e048033989f4498787873
extension semantic            a00a00cb16f238abecc8c625fa6334fc907f088e8906bada529384a59f5589e3

generic rows                  308,964
generic bytes                 9,718,836
generic SHA-256               8a61846547b6a8ab1984a7ebe8273fd7326316c8a83c040af377a6251b21937c
generic semantic              b82343d4aaf5225a6c1efaa454f5a8bad2622e4cd24f9d75603456393cbe0a1f

all-family union              417,848
remaining rows                1,221,055
remaining semantic            432854b7f00b57c5cf0009033e3ddfd3f4cb702bafed8fad2e5e69b369f30597
```

## Replay

The tracked, no-argument CI replay takes about one minute on the reference
workspace:

```bash
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/verify_diag3_triple_double_graph_scan.py
```

Replay source membership as well with the regenerable sequential residue:

```bash
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/verify_diag3_triple_double_graph_scan.py \
  --sequential-residue /tmp/diag3-triple-work/diag3_all_unit_anchor_residue.bin
```

The smallest open triple task after combining this layer with the separate
unit-minor layer is exact:

> Exclude compact components for the remaining `1,221,055` source rows by a
> different exact structural/certificate layer. The coordinate double-graph
> construction has no further recorded positive rows, but its negative census
> is not a theorem input without an independently replayable census manifest.
