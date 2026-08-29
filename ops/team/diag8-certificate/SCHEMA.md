# Diagonal-eight relative `H1` certificate interface

## Outcome

This directory defines and independently replays the smallest abstract input
that can decide `H1(-; F2)` for every admissible eight-signature family in a
finite labelled relative two-complex.  The input is:

1. all zero-, one-, and two-cells;
2. every signed immediate cellular incidence;
3. the complete signature label of every cell;
4. the true-infinity subcomplex;
5. global signature/dominance accounting; and
6. pinned external evidence for the geometric facts which finite algebra
   cannot reconstruct.

It is an interface theorem, not a parent-860 certificate and not a diagonal-
eight proof.  The honest 9DVL score is unchanged.

## Abstract theorem checked

Let `(K,I)` be a finite regular relative CW two-complex, with `I` the genuine
true-infinity subcomplex.  Every cell `c` has a complete feasibility label
`T(c)`.  The verifier requires label monotonicity

```text
d is an immediate face of c  =>  T(c) is a subset of T(d).
```

For a signature family `S`, this makes

```text
K_S = {c : S is a subset of T(c)}
```

a subcomplex.  The verifier forms the relative cellular complex
`C_*(K_S, K_S intersection I; F2)` by deleting the true-infinity basis cells.
It checks `d1*d2=0` and computes

```text
dim H1 = number(C1) - rank_F2(d1) - rank_F2(d2).
```

Signatures with equal ordinary-cell supports are quotiented.  Empty and
universal supports are discarded.  Inclusion of the remaining supports is
the declared dominance poset.  The verifier independently reconstructs this
poset, verifies an exact Dilworth width certificate (a maximum antichain plus
a chain cover), enumerates every size-eight antichain, and replays its
relative rank calculation.

The global accounting block is deliberately redundant with the cell labels.
It pins their semantic digest and supplies explicit present/absent witnesses
for properness and two-sided cell witnesses for every pair in the width
antichain.  This prevents a local or partial label mask from silently becoming
a global admissibility assertion.

If every mod-two `H1` vanishes, rational `H1` also vanishes: reduction modulo
two cannot have larger boundary rank than characteristic zero, so the mod-two
Betti number bounds the rational Betti number from above.  A nonzero mod-two
result alone does **not** prove nonzero rational `H1`.

## External fail-closed obligations

The algebraic checker cannot prove that a finite file faithfully represents a
semialgebraic parent.  Therefore every accepted certificate must bind, by a
verified SHA-256 digest, external evidence discharging exactly these fields:

- `ambient_coverage`;
- `regular_cell_structure`;
- `complete_cellular_incidence`;
- `complete_signature_labels`;
- `genuine_true_infinity_identification`; and
- `relative_model_matches_target_space`.

Missing fields, open status, moved artifacts, digest mismatches, paths outside
the repository, partial-domain accounting, nonclosed infinity, incomplete
label monotonicity, or inconsistent incidence all reject.  Checking the
digest only authenticates the referenced evidence; independent geometric
review remains required.

Artificial box or atlas boundaries are ordinary cells unless the external
geometry proof identifies them with genuine parent infinity.  A producer may
not discharge coverage or incidence while any relevant wall/node factor or
two-cell attachment remains unresolved.

## Why a smaller graph schema is unsound

`contractible_disk` and `unfilled_loop` have literally identical labelled
zero- and one-skeleta, the same eight globally witnessed incomparable proper
signature classes, and no infinity.  Adding the single two-cell changes the
unique admissible family's exact result from

```text
unfilled: dim H1(F2) = 1
filled:   dim H1(F2) = 0.
```

Thus a chamber/wall graph, even with complete labels and dominance data,
cannot decide diagonal eight.  Complete codimension-two incidence is
load-bearing.  The `relative_boundary` fixture supplies the second sharp
test: an ordinary interval whose two endpoints are true infinity has relative
`H1(F2)=1`; erasing the infinity tags changes the answer.

## Replay

```console
PYTHONDONTWRITEBYTECODE=1 python ops/team/diag8-certificate/verify_diag8_relative_h1_certificate.py
```

The replay accepts the contractible disk, detects the unfilled and relative
cycles, verifies width eight with exactly one admissible family in each
fixture, and rejects all deterministic hostile mutations.

## Scope and next adapter

The current parent-860 chamber network cannot instantiate this schema without
complete two-cell attachments, genuine infinity data, and global
signature/dominance evidence.  A geometric producer should next emit one
coverage-certified two-dimensional filling witness and leave every external
obligation open until all relevant factors and attachments are resolved.
