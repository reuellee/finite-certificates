# Diagonal 3: boundary-aware roadmap/component-cosheaf pilot

## Decision

**Input-contract no-go for reusing the completed lift manifests as-is;
retain the method as a post-closure compiler and continue targeted roadmap
experiments.**  The honest Nine-Diagonal Vanishing Lemma score remains
**2/9**.  This is not a no-go theorem for boundary-aware critical-point
roadmaps: the pilot does not construct such roadmaps on either support and
does not prove that they cannot generate the missing overlap and two-cell
data more cheaply.

The completed local inventory on supports `(3,1,15)` and `(3,3,7)` contains
exactly 527,533 base cells and 16,935,101 locally lifted cells:

| fiber type | base cells | lifted cells |
|---|---:|---:|
| open `t`, open `u` | 133,828 | 4,496,636 |
| open `t`, algebraic `u` | 132,134 | 4,047,846 |
| algebraic `t` | 261,571 | 8,390,619 |
| **total** | **527,533** | **16,935,101** |

Those artifacts are a complete local fiber inventory.  They are not yet a
global regular complex: they record ordered residual-wall roots and exact
event attachments, but do not contain face-compatible cell identifiers,
strict closure pairs and three-cell chains, complete extension-signature bad
membership, or genuine parent-infinity incidence.  A component cosheaf cannot
recover data that its input diagram does not specify.

## Mathematical contract

Let `X` be a finite regular complex for the retained compactified scope and
let `I` be its true parent-infinity subcomplex.  For every extension signature
`sigma`, the bad locus `B_sigma` must be a closed labelled subcomplex.  The
pilot compiler uses:

1. exact roadmaps or pseudo-critical sets to identify every connected
   component of each relevant `B_sigma` intersection;
2. specialization maps on components along the certified face poset;
3. the signed integral cellular differential of `C_*(X,I)` and the analogous
   bad-intersection subcomplexes;
4. overlap and two-cell data to compute `H_1`, followed by the alternating
   pair-to-triple complex and exact middle rank over `F_2`;
5. optional discrete Morse reduction only after the preceding coverage,
   incidence, label, infinity, and `d^2=0` checks pass.

A roadmap graph supplies connectedness data, not first homology.  In
particular, cycles can be filled by retained two-cells, and a graph that omits
those cells cannot decide whether a one-cycle survives.  The relevant
first-Betti algorithms likewise use component data for intersections together
with an incidence construction; they do not identify `H_1` with the cycle
space of a roadmap.

## Proof-producing pilot

The producer

```console
python ai/omreal/build_diag3_component_cosheaf_pilot.py
```

does two bounded jobs.

First, it compiles four fixed certificate fixtures: the synthetic seven-cell
relative schema canary and the coverage-certified 17-cell transverse node,
81-cell 3-by-3 multibox atlas, and 399-cell first-event atlas.  For all single,
pair, and
triple profile intersections it emits component records, component
specialization maps, signed `d^2=0` checks, and exact `H_0`/`H_1` ranks.  It
recomputes respectively 8, 216, and 216 ordered pair-to-triple rank
calculations for the schema, node, and multibox fixtures, and authenticates and
reuses the accepted 512-case first-event replay, over `F_2` and `Q`.  The
schema and node fixtures use their native
simplicial realizations; the square-cell atlases use their barycentric order
complexes.  The first-event rational replay is exact without rerunning costly
rational elimination: for integral matrices `rank_F2 <= rank_Q`, while
`MN=0` bounds the sum of the rational ranks by the middle dimension; the
certified zero mod-two residue forces equality term by term.  Every fixture
reproduces its accepted histogram, and every middle residue is zero over both
fields.  The synthetic relative schema fixture retains one declared relative
infinity cell and tests the quotient interface; it does not geometrically
certify a parent-divisor stratum.

Second, it authenticates the seven cumulative two-support manifests and
checks whether each exposes the five fields needed by the same compiler:

```text
cells
strict_closure_pairs
strict_three_cell_chains
parent_infinity_subcomplex
signature_profile_source
```

Every manifest is missing all five top-level fields.  The compiler therefore
stops before component specialization and records `BOUNDED_NO_GO`; it never
turns cell counts, samples, continuation paths, or local root orders into a
global coverage claim.

The independent verifier

```console
python ai/omreal/verify_diag3_component_cosheaf_pilot.py
```

does not import the pilot producer.  It invokes the accepted source replayers
for all four fixtures, reconstructs the component diagram with a separate
union-find and matrix implementation, checks all source SHA-256 pins and the
two-support arithmetic directly, and rejects fourteen re-sealed hostile
mutations, including erased infinity, corrupted specialization, and corrupted
rank data.  The component and `H_0`/`H_1` replay is independently recomputed;
the 512-case first-event pair-rank histogram is dependency authentication, not
a new independent recomputation.  Across the four fixtures there are 177
distinct profile intersections and 406 specialization maps, with 75
intersections exercising nonzero two-cell rank (maximum 90), but zero
disconnected intersections, zero many-to-one component maps, and zero
nonzero-`H_1` intersections.  The certificate records this limitation rather
than treating identity component maps as a split--merge test.
The deterministic certificate is
`data/DIAG3_COMPONENT_COSHEAF_PILOT.json`.

## Promotion and no-go gates

| gate | required for promotion | pilot result |
|---|---|---|
| declared-scope coverage | every retained stratum and face certified | **fail** on the two-support lift objects |
| component reconstruction | exact split, merge, and specialization maps | component/specialization replay passes; every tested intersection has at most one component, so nontrivial split--merge is unexercised |
| bad membership | complete extension-signature profiles on every theorem stratum | pass on the node/multibox/first-event fixtures; schema interface tested separately; unavailable globally |
| infinity | true parent-infinity subcomplex, separate from artificial scope boundary | schema-relative interface passes with one declared cell; genuine two-support infinity remains unavailable; other local fixtures declare infinity empty |
| first homology | signed overlap and two-cell incidence, not a roadmap graph alone | pass on all four fixtures; unavailable globally |
| ranks | integral `d^2=0` and exact `F_2`/`Q` middle ranks | pass on all four fixtures; unavailable globally |
| independent replay | producer-independent source and mutation audit | pass |
| material gain | smaller proof object or removed global obligation | not yet established |

The failed coverage and incidence gates are decisive for the existing lift
manifests: they cannot be promoted as inputs to a global component-cosheaf
proof.  This leaves open whether a targeted boundary-aware roadmap could
construct the missing closure object more cheaply than full CAD.

## Evidence-selected next action

For the pair branch, build a face-compatible closure-and-label microcompiler
on two already exact but topologically delicate stars:

- section 960, where walls 1 and 6 meet at the interior root `v=t` on
  `t^2-3t+1=0`;
- section 550, point 30, where wall 21 is tangent to `v=1` at
  `(t,u)=(1/4,1/3)`.

Each star must emit globally stable cell IDs, all strict face pairs and
three-cell chains, signed incidences, parent-infinity membership, and complete
bad-signature labels.  A successful star replay is the smallest honest test
of split/merge and endpoint specialization before scaling across all 527,533
base cells.  Once that closure contract exists, the component-cosheaf compiler
can be tested as a compression stage.  In parallel, the same stars are the
smallest honest test of whether critical-point roadmaps can generate that
contract without full master-closure construction.

The triple obligation remains independent.  Its next route is still a proper,
boundary-complete projection-critical roadmap certificate for the 1,162,302
unresolved source orbits.  No pair-branch rank can cancel that obligation.

## Literature audit

- Basu, Pollack, and Roy, *Computing the first Betti number and describing the
  connected components of semi-algebraic sets*, arXiv:math/0603248.  Used for
  the component/intersection-incidence architecture; not as a claim that a
  roadmap graph determines `H_1`.
- Basu and Roy, *Divide and Conquer Roadmap for Algebraic Sets*.  Used for the
  critical-point roadmap connectivity contract (meeting every component and
  relevant fiber component); not for cellular incidence.
- Kishimoto and Yushima, *Cellular cosheaf homology are cosheaf homology*,
  arXiv:2202.03659.  Used for the cellular-cosheaf/Borel--Moore framework on a
  supplied regular cell structure; not as a construction of that structure.
- Forman, *Morse Theory for Cell Complexes*, Advances in Mathematics 134
  (1998), 90--145.  Used only to justify post-certificate discrete Morse
  compression.

The exact claim/limitation audit is also recorded in
`ops/corpus/CITATION_AUDIT.md`.
