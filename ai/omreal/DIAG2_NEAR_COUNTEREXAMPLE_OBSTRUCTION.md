# Diagonal two: the near-counterexample atlas and four-singleton obstruction

## Result

The exact common-shear census on one realization of every realizable
`UOM(4,8)` parent has a very small extremal residue.  After quotienting the
proved antipodal symmetry `E_T(-rho)=E_T(rho)`, there are exactly `1,154`
signature-pair orbits with escape overlap at most eight:

| overlap | antipodal pair orbits | raw signature pairs |
|---:|---:|---:|
| 6 | 212 | 848 |
| 7 | 50 | 200 |
| 8 | 892 | 3,568 |
| **total** | **1,154** | **4,616** |

They occur in `875` of the `2,604` exact parent representatives.  The pair
graph is almost a matching: its `2,308` endpoints contain `2,307` distinct
within-parent signatures, with only one signature occurring in two retained
pairs.

Every one of those `2,307` signatures has the same decisive separator form:

* exactly four complete chart topes differ from it in one derived row;
* its complete inclusion-minimal separator family consists only of those four
  singleton rows; and
* the four mutation triples are linear and have label degree at most two.

Thus every extremal endpoint has exactly twelve source-local separator
occurrences.  Across the whole atlas the separator-size histogram is

```text
{1: 27,684}
```

with no separator of size two or larger.  There are two mutation-hypergraph
types: `2,201` signatures have degree sequence
`(1,1,1,1,2,2,2,2)`, and `106` have
`(0,1,1,2,2,2,2,2)`.

The accompanying universal result rules out overlap zero throughout this
four-singleton regime.

> **Four-singleton obstruction theorem.**
>
> Let `rho, eta` be uniform rank-four one-element extensions of one common
> uniform rank-four oriented matroid on eight old labels.  At a fixed parent
> chart, suppose each signature has exactly four distinct singleton mutation
> triples, with their three source occurrences, as its complete
> minimal-separator data.  Then their moving-witness escape masks intersect.

Consequently a genuine counterexample cannot arise by continuously squeezing
one of the observed extremal pairs to zero overlap while its separator type
stays unchanged.  Before overlap can vanish, at least one endpoint must gain
or lose a mutation neighbor or acquire a non-singleton minimal separator.

This is a universal conditional theorem plus a complete extremal point atlas.
It is not a universal proof that every bad pair remains four-singleton in all
residual chambers, so it does not promote diagonal two.

## 1. Complete overlap-at-most-eight extraction

`diag2_near_counterexample_fast.cpp` reconstructs exactly the same complete
bad-signature escape-mask table as the all-parent screen.  It independently
checks every record digest, verifies antipodal invariance, chooses the smaller
signature in each antipodal orbit, and enumerates every quotient pair with
overlap at most eight.

The set-theoretic lower bound

\[
 |E(\rho)\cap E(\eta)|\ge
 |E(\rho)|+|E(\eta)|-112
\]

makes the enumeration short after sorting by mask size; it does not sample or
discard any pair which can meet the threshold.  Because eight is below the
global minimum mask size `52`, each quotient pair represents exactly four raw
unordered signature pairs.

The compressed atlas pins:

```text
semantic SHA-256
377ca807cd8a3034677638ed55431ef83cce4cffa237834f3c530ec838f742ee
```

The default verifier validates the complete stored artifact and exactly
replays parents `16`, `860`, and `2599`.  The full extraction is explicit:

```console
python ai/omreal/verify_diag2_near_counterexample_atlas.py \
  --full --workers 8 \
  --analysis-output \
  ai/omreal/data/DIAG2_NEAR_COUNTEREXAMPLE_atlas8.json.gz
```

## 2. Exact separator profiles

For every retained endpoint, the separator verifier rebuilds the complete
derived-arrangement tope table from the exact parent matrix.  For each source
it constructs all source-local disagreements, takes their inclusion
antichain, and records each separator's row support, label carrier, and exact
14-direction nonescape cover.  The reconstructed masks reproduce all `1,154`
stored pair overlaps.

The complete profile census gives:

| quantity | exact value |
|---|---:|
| active parent representatives | 875 |
| antipodal pair orbits | 1,154 |
| distinct within-parent endpoint signatures | 2,307 |
| singleton source-separator occurrences | 27,684 |
| non-singleton occurrences | 0 |
| source families of size 0 | 106 |
| source families of size 1 | 9,016 |
| source families of size 2 | 9,334 |

The total `27,684 = 12 * 2,307` has a direct explanation.  A singleton
separator is one mutation triple, and it occurs in the source family of each
of its three labels.  Thus twelve source occurrences mean exactly four
distinct mutation triples per signature.

The profile artifact has semantic digest

```text
543fed1a543f9a596e243548c2d05b0b3f4f20da5d82116f3136b1936413a16e
```

and is replayed by:

```console
python ai/omreal/verify_diag2_near_counterexample_separators.py
```

## 3. Why a disjoint singleton pair forces an `8_3` configuration

Let `M_rho` and `M_eta` be the two four-element mutation-triple sets.  For an
ordered source-target pair `(e,f)`, a singleton mutation triple `I` can block
one of the two oriented shears only when

\[
                     e\in I,\qquad f\notin I.                 \tag{1}
\]

The blocked orientation is fixed by the transport sign

\[
 \alpha_\rho(I;e,f)
 =-\epsilon(I;e,f)\rho_I\rho_{I-e+f}.                        \tag{2}
\]

If the two escape masks were disjoint, both orientations of every `(e,f)`
would have to be blocked.  Hence at least two triples in
`M_rho union M_eta` must satisfy (1).

Write `d_e` for the degree of label `e` in the eight triples, and `m_ef` for
the number of triples containing both `e` and `f`.  The number satisfying (1)
is

\[
                         d_e-m_{ef}.                           \tag{3}
\]

It must be at least two.  A value `d_e <= 2` is impossible: if `d_e=2`, take
one of the partner labels in either incident triple and (3) is at most one.
But the total degree is `8 * 3 = 24`, so every one of the eight labels has
degree exactly three.  Equation (3) then gives `m_ef <= 1`; the eight triples
form a linear 3-uniform `8_3` configuration.

They use 24 of the 28 label pairs.  Each label has six distinct neighbors,
so the four missing pairs form a perfect matching.

The verifier enumerates all such configurations directly.  There are `840`
labeled configurations and one uncolored `S_8` orbit.  Coloring four triples
by `rho` and four by `eta`, modulo swapping the colors, gives `29,400`
labeled colorings in exactly three `S_8` orbits, of sizes

```text
2,520, 6,720, 20,160.
```

Thus three canonical colorings exhaust every possible four-singleton cover.

## 4. Shared-parent Grassmann--Pluecker obstruction

For each canonical coloring, introduce Boolean signs for:

* the 70 parent brackets on eight labels;
* the 56 extension brackets of `rho`; and
* the 56 extension brackets of `eta`.

The verifier constructs every rank-four three-term Grassmann--Pluecker
predicate for the two nine-element chirotopes, sharing the same 70 parent
variables.  A GP predicate forbids its three signed products from being all
equal and is expanded exactly to CNF.

For each of the 56 ordered pairs `(e,f)`, equations (1)--(2) provide two or
three candidate transport signs.  Covering both oriented shears means those
candidate signs are not all equal.  These conditions are expanded to the same
exact CNF form.

The simultaneous global chirotope sign, eight old-label reorientations, and
two new-element reorientations induce a rank-ten gauge action (one displayed
generator is redundant).  The verifier checks directly that every GP and
cover predicate is invariant and that ten selected bracket coordinates have
full gauge rank, then fixes those coordinates without loss of generality.

Each canonical coloring expands to `34,112` distinct CNF clauses.  All three
full systems are UNSAT.  Their pinned semantic formula digests are

```text
f69aa665307c55909c8c80790be1e29ee6d9bef857f69dbfc74d0a068fa44da6
5502fd73fca593c1536d2fbffcab527c82546e3ccfd043fd979a8e8aea0e0999
8a9f94cb13808bff3e18a3aa33c3ba762c98bc824c38fd329e1eae282190899a
```

The repository's dependency-free deterministic watched-literal CDCL checker
constructs and refutes the full formulas directly; it does not trust an
external solver or a stored opaque core.  It uses first-UIP resolvents,
restarts, and deletion only of unlocked learned clauses.  The verifier also
independently re-enumerates the `840` configurations and all three color
orbits before running those refutations:

```console
python ai/omreal/verify_diag2_singleton_four_obstruction.py
```

## 5. Exact scope and next target

The theorem closes the regime occupied by every currently known extremal
point, but a chart can change its minimal-separator antichains across residual
walls.  A hypothetical counterexample may therefore use:

* five or more singleton mutation triples at an endpoint;
* one or more non-singleton minimal separators; or
* a boundary degeneration where the source-local tope families change.

The next structural target is to classify the first separator bifurcations
out of the two observed four-edge hypergraph types and prove that each new
separator either preserves a common direction or forces a proper wall escape.
That is much narrower than arbitrary nine-dimensional chamber enumeration.

The honest nine-diagonal score remains `1/9`.
