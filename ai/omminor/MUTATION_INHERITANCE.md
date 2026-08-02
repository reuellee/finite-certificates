# Mutation-inherited deletion certificates

This note records an exact, inexpensive pruning rule for a mutation-tree
realizability sweep.  The rule is elementary, but it matters operationally:
after one non-realizable deletion has been identified, some descendant
classes can be certified without another realization attempt, LP, or minor
canonicalization.

It does **not** make every descendant of a non-realizable node
non-realizable.  It certifies a descendant subforest selected by the
mutation bases and the edge relabelings.  The live `(4,9)` sweep should not
be restarted merely to add it.

## 1. The invariant

Let `M` and `M'` be uniform rank-`r` oriented matroids on the same labelled
ground set, and suppose their chirotopes differ only at the basis `B`:

```
chi'(A) = -chi(A)  if A = B,
          chi(A)   otherwise.
```

Thus `B` is a mutation of `M`.  For every `p in B`,

> **Mutation/deletion lemma.** `M \ p = M' \ p` as labelled oriented
> matroids.  Consequently, if `M \ p` is non-realizable, then `M'` is
> non-realizable.

**Proof.** Every basis of either deletion avoids `p`, whereas the only
chirotope value changed by the mutation is indexed by `B`, which contains
`p`.  The deletion chirotopes are therefore identical.  A realization of
`M'` would restrict to a realization of `M' \ p = M \ p`, contradicting
the hypothesis.  QED.

This is the single-element-extension formulation: a mutation wall whose
basis contains the extension element does not change the deletion being
extended.

## 2. Reorientation classes and canonical tree edges

The catalogue stores canonical representatives modulo relabeling,
reorientation, and global sign.  Those operations preserve realizability
and commute with deletion after transporting the element label.  Hence the
lemma survives passage to reorientation classes, but the permutation on a
canonicalized edge must not be discarded.

For a parent representative `chi`, let `P` be a set of labels such that
`chi \ p` is known non-realizable for every `p in P`.  Suppose the tree edge
is represented by

```
g . chi_child = mu_B(chi),
```

where `mu_B` flips basis `B`, and let `sigma` be the permutation part of
`g`.  The child inherits the witness set

```
P_child = sigma^{-1}(P intersect B).
```

In particular, `P_child != empty` is an exact non-realizability
certificate.  The reorientation and global-sign parts of `g` change signs
but not realizability; the inverse permutation appears because deleting
`p` from `g . chi_child` corresponds to deleting `sigma^{-1}(p)` from
`chi_child`.

If an implementation records the edge identity in the opposite direction,
the permutation must of course be inverted accordingly.  Testing only
canonical labels without the saved edge permutation is unsound.

## 3. The descendant-subforest cut

Starting from any node with a known witness set, traverse the already-built
tree using only edge metadata:

```
propagate(node, P):
    for (child, mutation_basis B, edge_group g) in children(node):
        Q = permutation(g)^(-1)(P intersect B)
        if Q is not empty:
            mark child NON_REALIZABLE by inherited deletion
            propagate(child, Q)
```

This decides the maximal descendant subforest supported by that particular
set of inherited witnesses.  It scans edge labels, but performs no
geometric solve.  A production certificate should retain the parent
certificate identifier, the witness element, the mutation basis, and the
edge group.  Following those pointers ends at the independently checked
certificate for the non-realizable deletion.

The set can shrink along a propagated path.  It may also be enlarged if a
separate minor lookup discovers additional bad deletions at a node.  A
failed intersection says only that this proof did not cross the edge; it
says nothing about the child's realizability.

Rank `(4,9)`/`(5,9)` duality does not duplicate the cut.  Duality transports
the same statement, changing a rank-4 deletion witness into the
corresponding rank-5 contraction witness.  It is a useful consistency
check, not an independent source of certified classes.

## 4. Exact regression check

`mutation_inheritance.py` exercises the claim on the checked-in lifted
certificate corpus:

```
PYTHONDONTWRITEBYTECODE=1 python ai/omminor/mutation_inheritance.py
```

For each of the 40 rank-4, 9-element records in
`data/lifted_certs.jsonl`, it:

1. verifies the original Gordan certificate with the independent
   standard-library checker `ai/omreal/checkcert.py`;
2. enumerates every valid one-basis mutation;
3. for every mutation basis containing the recorded deleted element,
   checks directly that the deletion sign string is unchanged; and
4. attaches the *unchanged* Gordan certificate to the mutated chirotope and
   asks the independent checker to verify it again.

On the pinned corpus, all **271 of 271** theorem-covered mutation edges are
accepted.  There are 4--10 such edges per record (mean 6.775).  As a useful
control, among the valid mutation edges not covered by the lemma, the same
certificate happens to remain valid on 35 and is rejected on 298.  Thus
`p in B` is sufficient, not necessary; the script deliberately makes no
claim in the other direction.

## 5. Expected size of the cut

In the frozen prefix measured in `MINOR_THEORY.md`, the certified
non-realizable rows have the following numbers of bad deletions:

| bad deletions `k` | 0 | 1 | 2 | 3 |
|---:|---:|---:|---:|---:|
| rows | 1,279 | 10,021 | 2,703 | 393 |

For an *unbiased uniformly random* 4-subset mutation basis, the probability
of meeting a `k`-element witness set is

```
q_k = 1 - C(9-k, 4) / C(9, 4),
```

namely 44.444%, 72.222%, and 88.095% for `k = 1, 2, 3`.  Weighting those
three values by the table gives **51.476%** among rows that have a witness.

That number is only a calibration baseline.  Tree edges are selected from
mutable bases, not uniform 4-subsets; the tree construction can correlate
edge bases with witnesses; outdegrees matter; and inherited witness sets
usually shrink.  It must not be quoted as “51.5% of the catalogue”.  Since
non-realizable classes are only about 1.8% of the running split, this rule
alone is unlikely to remove hours from an already 57%-complete sweep.  Its
best use is in the next run, or in a lightweight replay over saved tree-edge
metadata.

## 6. What this does not solve

* It gives no verdict when `P intersect B` is empty.
* It does not classify the minor-minimal non-realizable remainder, whose
  members have `P = empty` by definition.
* Reorientation symmetry is already fully accounted for by the edge group;
  it supplies no further closure theorem here.
* Duality supplies the same certificate in another rank, not a second
  certificate.
* The generic rule “a final polynomial survives a mutation outside all of
  its bracket support” is also exact, but typical certificates have dense
  support.  It should be measured on the actual tree before adding
  complexity to the live sweep.

The honest result is therefore a small exact cut with a short proof and an
auditable certificate chain, not a replacement for the exhaustive split.
