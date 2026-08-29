# Diagonal-eight parent-certificate transport audit

## Outcome

There is a precise sufficient transport theorem, but neither mutation
connectivity nor reducible deletion supplies its hypotheses.  A universal
route from one parent certificate to all 2,604 realizable parents is therefore
**disproved at the stated label-faithful scope**.

Two exact rank-four/eight-element countermodels locate the failure.

1. Two rational uniform parents joined by one genuine mutation have different
   complete abstract extension universes: `73,712` signatures on one side and
   `74,342` on the other.  Their displayed exact charts also have different
   feasible-tope counts, `26,108` and `26,106`.
2. A realizable lexicographic parent that is reducible by element 7 has
   `25,856` extension topes, but deletion retains only `5,294` labels.
   Exactly `4,964` deletion labels have a nontrivial fiber and one fiber has
   size `282`.

Thus mutation adjacency does not preserve feasibility labels, and a reducible
forgetful map is not a labeled stratified equivalence.  A separate finite
model also shows why true-infinity membership and codimension-two incidence
must be preserved: changing either changes the relevant exact homology.

This result does not disprove diagonal eight.  It removes the proposed
catalog shortcut and leaves the honest 9DVL score at **2/9**.

## 1. The sufficient theorem

For a parent `M`, let `(K_M,I_M)` be a finite regular-CW model of its
compactified master arrangement through primal codimension two, where `I_M`
is the **true** parent-infinity subcomplex.  Let `B_M(sigma)` be the closed
bad subcomplex for every labeled extension signature `sigma`, and retain the
signed cellular incidences.

> **Labeled stratified-pair transport theorem.**  Suppose adjacent parents
> `M_-` and `M_+` admit:
>
> * a bijection `rho` between their complete labeled extension-signature
>   universes; and
> * a dimension-preserving regular-CW isomorphism
>   `phi: K_- -> K_+`
>
> such that `phi(I_-)=I_+`, every signed closure incidence through
> codimension two is preserved, and
>
> `phi(B_-(sigma)) = B_+(rho(sigma))`
>
> for every signature.  Then every diagonal-eight cellular rank certificate
> transports from `M_-` to `M_+` after applying `rho`.

The proof is formal.  For every eight-signature family `S`, `phi` restricts
to an isomorphism of the relevant labeled relative cellular complexes.  In
each degree their boundary matrices differ only by invertible signed
permutation matrices:

```text
D_k(+) = P_(k-1) D_k(-) P_k^{-1}.
```

Consequently `D_(k-1)D_k=0`, all boundary ranks, and every relative homology
dimension agree.  In particular a zero source `H1` certificate gives a zero
target `H1` certificate.  A proper semialgebraic product collar across the
mutation wall, stratified by every active factor and every true-infinity
face, is a sufficient geometric way to produce `phi`.

The theorem is intentionally stronger than a homotopy equivalence of
unlabeled parent spaces.  The certificate consumes labeled subcomplexes,
signed incidence, and a relative infinity pair, so all three belong in the
transport contract.

## 2. Exact mutation obstruction

Use the first seven columns

```text
e1, e2, e3, e4,
(2,-1,-2,3), (3,-6,-7,-7), (-5,5,4,-7)
```

and move column 7 along the rational segment

```text
p_- = (-295,-304,200, 5)
p_0 = (-300,-300,200, 0)
p_+ = (-305,-296,200,-5).
```

Exact evaluation of all 70 parent brackets proves:

* both endpoints are uniform rank-four realizations;
* at `p_0`, the only zero parent bracket is `[0127]`; and
* the endpoint chirotopes differ only at `[0127]`.

This is an exact mutation, not an inferred mutation-graph edge.

First, exact Grassmann--Pluecker backtracking enumerates every abstract
uniform one-element extension of each endpoint chirotope:

| quantity | minus | plus |
|---|---:|---:|
| complete abstract extensions | 73,712 | 74,342 |
| semantic SHA-256 | `860f2c9450cd8a0bb556f8184186da9344ea7ca33ceab79b896e8cf5e8c8a4d6` | `df33e0dbd67ee24bee8b7979733593beb283ff60a6ef98dcb85e98b48e92fdce` |

The universes share `57,508` natural labels, while `16,204` labels die and
`16,834` are born.  In particular, their unequal cardinalities exclude even
an arbitrary bijection between the complete label universes.

Second, for each displayed realization the verifier constructs the 56 exact
derived normals `det(v_i,v_j,v_k,x)` and enumerates every strict sign chamber
by restriction recursion.  Each sign word has an exact integer witness, and
the recursion proves coverage.  The results are:

| quantity | minus | plus |
|---|---:|---:|
| feasible labeled topes | 26,108 | 26,106 |
| semantic SHA-256 | `6430db85192820c6471db6e68669b9786ad7e8eb5a094d9a74c3aa9244bdbe52` | `b1427d54704d6a2612a9d2cbda04f3771c2bcb2ca12c03052ba27484e55a7a07` |

The feasible chart-topes have `21,278` labels in common.  Relative to the
fixed labeled triple coordinates there are `4,830` chart deaths and `4,828`
chart births.  The certificate contains one exact integer witness for each
direction, and the verifier rejects both as falsely claimed common labels.

The unequal complete abstract-extension counts rule out the theorem's label
bijection for this mutation, independently of which realization is selected
inside either parent cell.  The unequal displayed tope counts additionally
rule out pointwise transport along this exact wall-crossing segment.  Thus
mutation adjacency and realizable-mutation connectivity do not imply the
sufficient theorem.  A special edge may still be transportable, but it needs
its own complete collar certificate.

## 3. Exact reducible-deletion obstruction

Take the seven moment-curve columns

```text
v(t)=(1,t,t^2,t^3),  t=1,...,7
```

and adjoin

```text
v_7 = 10^3 v(7) + 10^2 v(6) + 10 v(5) + v(4)
    = (1111,7654,52866,365914).
```

Positive rescaling identifies this with the lexicographic extension

```text
v(7) + epsilon v(6) + epsilon^2 v(5) + epsilon^3 v(4),
epsilon=1/10.
```

The verifier checks all 35 defining triple signs against the first nonzero
term in lexicographic order `(6,5,4,3)`.  This parent is reducible by element
7: for an arbitrary realization of the deletion, the same finite list of
leading determinant signs is fixed by its chirotope, and one sufficiently
small positive `epsilon` preserves all of them simultaneously.

Nevertheless, restricting the `25,856` exact full-parent topes to the 35
coordinates not involving element 7 gives only `5,294` labels.  The verifier
independently enumerates the deletion arrangement and proves that these are
exactly all `5,294` deletion topes.  The map is surjective but highly
noninjective:

| deletion statistic | exact value |
|---|---:|
| nontrivial fibers | 4,964 |
| maximum fiber | 282 |
| full-label digest | `407f13935d4cbd53aa5596014f6e42e4e6f4b003c5999cc3af90eef19a70d1cb` |
| deletion-label digest | `95664f4e88848192db2ba9494de4b196e824ef292d7bf2d3688a24ee1c0eea8d` |

The pinned collision is

```text
0x8f9907320c861b  ->  0x7320c861b
0x8f990f320c861b  ->  0x7320c861b,
```

where the full labels differ only at triple `(0,1,7)`.  Both have exact
integer witnesses.  Hence the unstratified deletion homotopy equivalence in
the parent-contractibility audit cannot transport the complete extension
labels, let alone their wall/node incidence, without a new fiberwise labeled
theorem.

## 4. Incidence and infinity are independent obligations

The finite topology fixture uses a four-cycle.

* With no infinity vertices its relative `H1(F2)` is `1`.
* Marking the two opposite vertices as true infinity changes relative
  `H1(F2)` to `2`.

The identity cell map therefore cannot be a map of pairs.  This is the
`infinity_change` canary.

The same four-cycle is also the dual chamber/wall skeleton for the node
fixture.  Without a dual two-cell its `H1(F2)` is `1`; attaching the node
two-cell along all four edges changes `H1(F2)` to `0`.  Thus the
chamber/wall graph and feasibility labels cannot replace codimension-two
incidence.  This is why the sufficient theorem explicitly preserves signed
node incidence.

## 5. What the canonical inputs do and do not prove

The four work-order inputs replay at their pinned digests.

* `WALK_THEORY.md` supplies connectedness of the realizable mutation graph.
  It supplies paths between parent types, not labeled stratified collars.
* `PARENT_CONTRACTIBILITY_AUDIT.md` supplies parent contractibility and, for
  reducible cases, an unstratified deletion homotopy equivalence.  It does not
  claim naturality for extension-feasibility subspaces.
* `verify_mutation_graph_not_partial_cube.py` already blocks inference of a
  hypercube metric from general mutation graphs.
* `DIAG9_SIGN_GEODESY_AUDIT.md` identifies connected full sign conditions and
  complete wall/node coverage as missing global axioms; the 178-point sample
  is not such coverage.

The exact countermodels are therefore consistent with every canonical input
and close the logical gap between their actual scope and the proposed
transport shortcut.

## 6. Decision and next discriminator

Do not use mutation connectivity or reducible deletion to copy one
diagonal-eight certificate across the catalog.  Exact relabeling,
reorientation, or projective symmetries remain valid transports when they
provide an explicit signed cell-poset isomorphism.

If catalog reduction is revisited, define a **quiet-edge graph** whose edges
are admitted only after the full labeled stratified-pair contract above is
certified.  The next bounded discriminator is one exact candidate edge from
parent 860:

1. certify a proper mutation collar with only one parent bracket zero;
2. prove zero label births/deaths throughout the collar;
3. match every wall and node with signed incidence;
4. match true-infinity subcomplexes exactly; and
5. replay one complete eight-family rank certificate on both sides.

Any failed item rejects that edge.  Even one passing edge proves only that
edge; catalog reduction is the connected-component count of the certified
quiet-edge graph, not of the ordinary mutation graph.

## Replay

```console
PYTHONDONTWRITEBYTECODE=1 python ops/team/diag8-transport/verify_transport_obstruction.py
```

Expected terminal lines include:

```text
PASS canaries mutation_birth, mutation_death, infinity_change, label_collision
NO-GO mutation connectivity and reducible deletion do not supply that isomorphism
SCOPE no all-parent coverage and no 9DVL ledger change
```
