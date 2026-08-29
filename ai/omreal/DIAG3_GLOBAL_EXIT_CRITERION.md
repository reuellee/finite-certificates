# Diagonal three: finite global-exit criterion

## Result

There is a sharp finite endpoint for the triple noncompactness branch, but it
does not replace the pair master closure complex.

Let `X` be a theorem parent cell, `Xbar` a fixed Hausdorff compactification,
and `I = Xbar \ X` its **true parent infinity**.  For one declared triple-bad
family let `Z` be its closed bad intersection in `X`.  A finite directed
certificate graph `G=(V,E)` is **component-faithful and complete** when:

1. every connected component of `Z` has at least one vertex;
2. every vertex carries a globally unique stable **local-component** identity,
   not merely a wall type, factor label, local root, sample, or clipped-scope
   label;
3. every edge certifies that its two local fragments continue inside the
   closure of one connected component of `Z`; and
4. every `true_parent_infinity` mark is sound: that fragment has a certified
   closure point in `I`.  In particular, an artificial box, collar, chart, or
   work-scope boundary is not in `I`.

The graph need not list every possible continuation edge or every possible
infinity witness.  Those omissions can cause rejection but not a false proof.
Only component coverage, edge soundness, and infinity-tag soundness are needed
for an accepting certificate.

Use the following graph acceptance predicate:

> **Exit condition.** Every vertex reaches a `true_parent_infinity` vertex.

For a finite graph this is equivalent to

> **Sink-SCC condition.** Every sink strongly connected component contains a
> `true_parent_infinity` vertex.

This condition permits directed cycles that have an exit.  It is therefore
strictly weaker than requiring the graph to be acyclic with boundary sinks.

## Abstract theorem

**Theorem (finite component-faithful exit, sufficient direction).** If a complete
component-faithful graph for `Z` satisfies the exit condition, then every
connected component of `Z` has closure meeting `I`.  Consequently no
component of `Z` is compact in `X`, and `H_c^0(Z;Q)=0`.

**Proof.** Let `C` be a connected component of `Z`.  Completeness gives a
vertex `v` representing `C`.  By the exit condition there is a directed path

```text
v = v0 -> v1 -> ... -> vk.
```

Each certified edge preserves the underlying component identity, so every
`vi` represents `C`.  The final vertex has a certified closure point of `C`
in `I`.  Hence the closure of `C` in `Xbar` meets `I`, so `C` is not compact
in `X`.  This applies to every component.  A semialgebraic `Z` is locally
connected and has finitely many connected components, each open and closed.
Its compactly supported locally constant functions are therefore supported
on compact components; absence of compact components gives `H_c^0(Z;Q)=0`.

For the graph equivalence, contract the finite graph to its SCC condensation,
which is a finite DAG.  Every vertex in a finite DAG reaches a sink.  Thus the
graph predicate “every vertex reaches certified true infinity” holds exactly
when every sink SCC contains a true-infinity vertex.  QED.

The converse to the noncompactness conclusion is false in this open-world
certificate model.  Sound continuation edges and infinity witnesses may be
omitted, and several vertices may represent fragments of one actual component.
Consequently rejection means only that this certificate did not prove an exit;
it is **inconclusive**, not evidence that a compact component exists.

## Exact hostile fixtures

`verify_diag3_global_exit_criterion.py` replays seven finite graphs.

* An acyclic graph whose sinks are genuine infinity passes.
* A directed cycle with no genuine infinity makes the graph predicate reject;
  rejection remains inconclusive about the actual component.
* A directed cycle with an outgoing edge to genuine infinity passes, showing
  that acyclicity is unnecessary.
* A path ending only on an artificial scope boundary makes the graph predicate
  reject.
* The repository's exact uniform `44 -> 37 -> 44` canonical-pivot fixture is
  replayed over rational arithmetic and rejected.  It has no true-boundary
  exit, and wall labels are not stable global component identities.
* An omitted-edge canary has two vertices with the same certified global
  component ID.  One touches true infinity, but no graph edge joins the other
  fragment to it.  The actual component is noncompact while the graph predicate
  fails, exactly demonstrating an inconclusive certificate false negative.

The `44 -> 37 -> 44` fixture is not a compact-component counterexample.  It is
an exact counterexample to treating a wall-label potential as the required
component-faithful graph.

## Pair no-go from the same graph

The exit theorem is an `H_c^0` theorem.  It cannot certify the pair branch,
which depends on relative first homology and the alternating middle rank.

The checker constructs two relative CW complexes with the same accepted
component graph and the same one-skeleton.  Relative to one true-infinity
vertex, both have one interior vertex `i`, a path `p` from `i` to infinity,
and a loop `l` at `i`.  Their common first boundary is

```text
d1 = [1 0].
```

The unfilled complex has no two-cell and `dim H1(F2)=1`.  The filled complex
attaches one disk with `d2=(0,1)^T` and has `dim H1(F2)=0`.  Both satisfy
`d1*d2=0`; both pass the global-exit graph criterion.  Therefore component
continuation and true-boundary reachability do not determine pair `H1`.

This is a countermodel to a graph-only pair certificate, not a 9DVL
counterexample.  A pair certificate still needs the master complex's
face-compatible cell IDs, complete strict closure pairs and three-cell
chains, true-infinity subcomplex, complete bad-membership profiles, and
two-cell incidence parity before the mod-two middle-rank test.

## Replay against canonical state

```console
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/verify_diag3_global_exit_criterion.py
```

The checker pins decision-ledger digest
`5841dfbb55aa0d8c580b394b50beff54d607ce86b77683985c2d977c03050e14`,
replays the exact `44 -> 37 -> 44` source verifier, and checks the existing
open objects.  At the pinned base, the triple residue is `1,162,302`; the pair
object has zero certified global adjacencies, closure pairs, closure triples,
or parent-infinity cells; and the completed two-support lift manifests lack
the component/closure input contract.  Hence the theorem currently closes no
declared triple family and no invariant obligation.

## Smallest next discriminating datum

For the triple branch, the next certificate should emit, for one complete
unresolved source family, globally stable local-component identities, exact
same-component continuation edges, and certified true-parent-infinity
witnesses.  The sink-SCC check then gives a final binary decision without any
new local optimization loop.

For the pair branch, the next indispensable datum is different: at least one
globally identified strict three-cell chain / two-cell incidence attached to
the existing labelled source skeleton, together with its true-infinity and
signature-membership tags.  Another component-reachability edge alone cannot
discriminate the filled and unfilled countermodels.
