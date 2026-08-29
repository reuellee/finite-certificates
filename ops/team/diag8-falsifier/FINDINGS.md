# Diagonal-eight falsifier handoff

## Outcome

The global `diag8_h1` claim remains **inconclusive**.  This track found no
exact admissible geometric eight-family with nonzero `H_1` on the certified
artifacts.  It did obtain three bounded results with distinct evidence
classes.

1. **Geometric finite-exact filling.**  The apparent parent-860 mask-3 loop
   `1-2-3-18-17-1` is not a surviving homology witness.  Its exact `a/g`
   polygon is parent-safe.  Triangle-Bernstein certificates make
   `26,738/26,740` residual factors sign-definite on the polygon; the only
   remaining factors are `16573` and `22629`.  Their exact boundary profile is
   `(16573,22629), (), (16573), (22629)`, and they have exactly one transverse
   intersection in the polygon.  The corresponding node dual two-cell has
   the pentagonal loop as boundary.  All `26,038` stored labels common to the
   loop also label that face by all-strata gluing, so attaching it changes
   the induced complex from `beta_1=1` to `beta_1=0`.

2. **Finite exact null searches.**  The 12 proper support masks on the
   parent-860 repaired network have artifact-internal dominance width `6`.
   Exhausting all `C(12,8)=495` size-eight subsets therefore finds no local
   eight-antichain.  This is not a global dominance theorem because the
   network lacks coverage.  On the exact row-2599 transverse-node complex,
   all ten intersection-closure masks have `beta_1=0`.  The two stored global
   proper nine-antichain certificates supply 18 size-eight subfamilies; every
   one restricts to the empty node subcomplex and hence has local `H_1=0`.

3. **Abstract architecture countermodel.**  `COUNTERMODEL.json` is an
   eight-vertex contractible ambient simplicial complex with eight proper,
   pairwise-incomparable, cell-induced labels.  Their common induced
   subcomplex is the unfilled triangle and has `H_1=Z`.  Every cell label is
   exactly the intersection of its vertex labels, so label monotonicity,
   all-strata gluing, and the no-single-missing-face local rule all hold.
   The model is vertex-minimal in this labelled-simplicial class: nonzero
   simplicial `H_1` needs at least three common vertices, while an eight-label
   antichain needs at least five varying vertices because the maximum width on
   four bits is six.  This is an abstract countermodel only; it does not
   satisfy or encode the third-compound/UOM restrictions.  The repository's
   independent semialgebraic no-go checker remains the stronger geometric
   abstract-axiom regression.

## Surviving geometric discriminator

The parent-860 mask-6 induced graph has the exact cycle

```text
4-11-12-14-13-23-4
```

and one leaf `4-5`, hence `beta_1=1`.  The cycle has `26,038` common stored
labels.  Unlike mask 3, it spans the `a,d,f,g` coordinates and no certified
codimension-two filling is stored.  It is neither a geometric `H_1` witness
nor known to be filled.  The highest-value next experiment is an exact
two-chain search on this six-edge loop: certify a parent-safe spanning disk,
enumerate every residual wall/node cutting it, and compute its label-induced
relative boundary.  Stop immediately if the disk crosses a parent boundary
or returns an exact non-boundary cocycle.

## Scope and nonconsequences

- The parent-860 network is an embedded training network, not a complete
  master complex.  Graph `beta_1` does not imply geometric `H_1`.
- Artifact-internal pattern inclusion cannot certify global properness or
  incomparability.  No pinned parent-860 global eight-antichain witness was
  available in the tested inputs.
- The row-2599 result is local to one transverse node and two previously
  certified nine-antichain families.
- The abstract countermodel falsifies sufficiency of the labelled-complex
  local architecture, not diagonal eight for uniform oriented matroids.
- No ledger, theorem-status, publication, or merge change is recommended.

## Replay

From the repository root:

```console
PYTHONDONTWRITEBYTECODE=1 python \
  ops/team/diag8-falsifier/verify_diag8_falsifier.py
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/verify_ninth_candidate_antichain.py
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/verify_ninth_candidate_generic.py antichain \
  ai/omreal/data/ninth_candidate_37_176_antichain.npz
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/verify_residual_stratum_no_go.py
```

The first command includes the required `known_tree`, `filled_cycle`,
`missing_two_cell`, and `hostile_label_mutation` canaries.
