# Diagonal three: direct final affinity after two unit graphs

## Honest outcome

This layer starts from the exact `1,221,055`-row residue after the sequential,
double-graph, and graph-unit-minor certificates.  It records a strictly more
general use of the two-unit-graph theorem: instead of requiring the second
graph numerator and denominator to be independent of a final coordinate, it
forms the fully denominator-cleared final equation and tests that equation
directly for affinity.

The ten certified chart blocks contain `128,198` exact witness occurrences.
Their priority union has `58,673` rows, leaving `1,162,382` of the pinned
`1,221,055` source rows.  This remains a partial reduction of the triple
compact-component obligation.  It does not prove the exclusive-pair
middle-exactness obligation and does not change the score from `2/9`.

## Direct-final theorem

Let `X` be one open uniform parent cell.  A certified first residual equation
has the exact form

\[
q_1=A_1(w)x+B_1(w),
\]

where `A_1` is a nonzero scalar times a product of parent brackets.  It is
therefore nowhere zero on `X`, and graphing `q_1=0` identifies its zero set
with an open domain `D` in `R^8`.  Multiplying a restricted equation by the
power of `A_1` used by `graph_restrict` does not alter its zero set on `D`.

On `D`, the certified second cleared equation is

\[
r_2=A_2(u)y+B_2(u),
\]

where `A_2` is a nonzero scalar times a product of restrictions of parent
brackets.  Each restricted parent bracket remains nowhere zero on `D`, so
`A_2` is a unit.  Graphing `r_2=0` gives an open domain `E` in `R^7`.

If the degree of the first-graph restriction `r_3` in `y` is `d`, the
certificate verifier constructs exactly

\[
 R=A_2^d r_3(y=-B_2/A_2).
\]

Primitive integer normalization changes this polynomial only by a nonzero
constant.  Because `A_2` is a unit, `R=0` is precisely the third zero-set on
`E`.  The new condition is simply that this **fully cleared** polynomial is
affine in one remaining coordinate `z`:

\[
R(v,z)=C(v)z+D(v).
\]

The complementary base has dimension six.  The standard affine-fiber lemma
therefore excludes compact connected components, including the locus
`C=0`: a consistent rank drop contains the open vertical fiber, while off
that locus the zero set is a graph over an open base.  The two unit-graph
homeomorphisms preserve components and compactness, proving componentwise
noncompactness of every recorded original triple.

This condition strictly contains the earlier cheap mask
`D_z A_2=D_z B_2=0` plus pre-substitution affinity of `r_3`; neither of those
stronger hypotheses is assumed here.

## Exact certificate and audit scope

`data/DIAG3_triple_direct_final_affinity_certificates.bin` contains one block
per certified canonical chart.  Blocks retain all standalone positive rows,
including cross-chart duplicates, so the verifier independently reproduces
each chart count and semantic digest before taking the stated priority union.
For every record it reconstructs over `Z`:

* the anchor-to-canonical alignment and complete stabilizer transport;
* both graph reconstruction identities;
* both nonzero parent-unit slopes, including the complete second-slope
  scalar and parent-label product;
* the fully cleared third restriction; and
* elimination of both graph coordinates and degree at most one in the
  recorded final coordinate.

The modular two-jet screen was only a candidate producer.  Every retained
record is replayed exactly; no modular negative or maximality statement is
used by the theorem.

The optional source replay pins the unique `1,221,055`-row input, proves that
the priority union is a subset with no duplicate or repeated-factor rows,
and hashes the remaining rows in canonical source order.

## Pinned counts and digests

The priority order is part of the certificate contract.  The three type-48
charts certify the same eight rows and are retained as independent chart
witnesses.  Type-49/pivot-3 is likewise a zero-net corroborating chart after
the type-49/pivot-1 and pivot-5 union, although its position in the pinned
priority order contributes 15 rows before pivot 5 contributes the final six.

| canonical chart | standalone rows | priority increment | second-slope keys | final keys | ordered semantic SHA-256 |
|---|---:|---:|---:|---:|---|
| 48 / pivot 0 | 8 | 8 | 5 | 8 | `96502ea6ad420dc0f5be22da7ee2fa1ca098b21df61f601ad0630404d37ec188` |
| 48 / pivot 1 | 8 | 0 | 5 | 8 | `7eab29363a826b80ad81b175cedd26296417ffb0062c95c52ddaab8b81abda00` |
| 48 / pivot 2 | 8 | 0 | 5 | 8 | `0fa360b83b7e6acb2d2e88dbc998e66ca2e0d7618783ff01f83bc87b073eef13` |
| 49 / pivot 1 | 8,488 | 8,488 | 1,754 | 8,488 | `500518b56a6507307d373d9460ff87c5dda5de731790037fc08ac5e016c9b41e` |
| 49 / pivot 3 | 8,497 | 15 | 1,772 | 8,497 | `0bf7bb84c3ad3ba0e88b864b6764b66fcffacbc4b6288a279aa723c8100ea761` |
| 49 / pivot 5 | 8,503 | 6 | 1,779 | 8,503 | `927a804f85397d6a4f056fb82a29b7e5fcc3237dea80eee62eef8cb93667f3e5` |
| 50 / pivot 1 | 29,963 | 29,846 | 4,520 | 29,963 | `0308f1c3148b7e12af04ffede41673ff91b6db451a9fef4f0908b96b57ffa0bc` |
| 50 / pivot 3 | 30,483 | 527 | 4,645 | 30,483 | `62fef3ec741b71b1a0409f5f23203b93652a4347ba5d7e973e29dc584ecc7c4e` |
| 51 / pivot 5 | 21,161 | 19,573 | 2,269 | 21,161 | `57048240800b06c1687ca627e071b357e507c2f59fd12a20e9d33a0f9dad8e3b` |
| 51 / pivot 6 | 21,079 | 210 | 2,294 | 21,079 | `f8c0579fffb1fbafedcc0f2f4d0e4ddeed5ae66ccd39b9237db2356c1c77a3b5` |

The binary certificate has `4,212,318` bytes and SHA-256
`6ed192d1dd2f814ae914349ec2dbcc654ffb663669b85f1b289fa37feb147f26`.
Its block-stream semantic digest is
`7cd37ee421c651563bb6dbeae45b6711b71839893ba53abfb7240b1e165f2b1a`.

The pinned input has `1,221,055` unique rows, `7,326,334` bytes, and SHA-256
`bdd29e7647a99429f38c7bc20e9e5b9b514dccf7cbf57f9cd9b1b36fec7e7d92`.
Deleting the exact `58,673`-row union in source order leaves `1,162,382`
rows whose packed-body SHA-256 is
`44ff9f5f0ea6c332c0382717533f5fa4b8e4b8af3d72024f9d4b0c74e6448dda`.

The type-51/pivot-6 candidate producer proposed 21 additional rows that
failed the exact final-degree test.  They are absent from the certificate.
This is a positive certificate only: no failure of the modular screen is used
as evidence that an unrecorded row remains open.

## Replay

Exact certificate replay:

```bash
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/verify_diag3_triple_direct_final_affinity.py
```

Replay source membership, priority disjointness, and the resulting residue:

```bash
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/verify_diag3_triple_direct_final_affinity.py \
  --source-residue /tmp/diag3-triple-work/diag3_current_residue_1221055.bin
```

To replay every cross-chart witness rather than one witness per priority-union
row, add `--all-block-records`.  This is the run that pins the algebra-key
columns in the table.

The score must remain `2/9` until this layer's remaining triple residue is
also closed and the independent global pair-middle-exactness obligation is
proved.
