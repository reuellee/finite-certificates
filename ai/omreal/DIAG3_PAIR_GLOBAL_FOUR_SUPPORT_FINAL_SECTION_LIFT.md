# Final algebraic-section lift

This checkpoint completes the exact base lift on every algebraic `t` section
for the first two four-support parent domains.  It resolves the 28 fibers that
were deliberately left open by the regular-event arguments:

```text
14 root-count changes
 7 exceptional same-count transitions
 7 complex unchanged stacks
28 completed final sections
```

Together with the earlier 1,022 transversal, 363 constant-stack, 240
simultaneous multi-crossing, and 40 regular-residual fibers, all **1,693**
algebraic `t` sections are now lifted at the base level.

The global 9DVL ledger remains **2/9**.  The result does not yet lift the 22
original walls in `v`, glue the two square-pyramid supports to their completed
faces, attach extension-signature labels, replay the relative middle rank, or
discharge the independent triple obligation.

## Ordered number-field Sturm lemma

Let `q(t)` be an irreducible rational polynomial and let `(a,b)` isolate one
real root `alpha`.  The interval selects an ordering on

```text
K = Q[t] / (q).
```

For any nonzero element of `K`, rational interval evaluation determines its
sign after finitely many exact bisections of `(a,b)`: irreducibility prevents a
lower-degree representative from vanishing at `alpha`.  Euclidean division
therefore constructs Sturm sequences in `K[u]`, and sign variations at
rational `u` endpoints count the distinct roots of a squarefree polynomial in
the chosen real embedding.

For each final section, the verifier specializes all 114 base factors to
`K[u]`, removes repeated and `u=0,1` boundary factors exactly, and counts all
interior roots.  A proposed section point carries a rational isolating
interval and the complete set of base factors that vanish there.  Every owner
has exactly one root in that interval.  When several factors own a point,
their exact gcd in `K[u]` also has exactly one root there.  Disjoint interval
order plus equality between each factor's total Sturm count and its number of
claimed point intervals proves both completeness and absence of duplicated
section points.

This argument covers births and deaths, multiple resultants, discriminants,
degree drops, vertical factors, and boundary crossings uniformly.  It does
not infer a section stack only from its neighboring generic stacks.

## Exact census

The selected section fields have degrees:

```text
degree 1:  6 sections
degree 2: 11 sections
degree 3:  9 sections
degree 4:  2 sections
```

The completed lift contains:

```text
1,862 distinct section u-root points
1,890 open u strips
3,752 exact section base cells

    1 vertical-zero factor incidence
   33 bounded-boundary zero incidences
```

The complete four-support base CAD now consists of 265,962 open-sector cells
and 261,571 algebraic-section cells, for 527,533 base cells before `v` lifting.

## Producer and independent replay

The producer uses SymPy to propose the real-root ordering and exact common
divisors.  It stores only rational intervals, factor owners, pinned source
hashes, and scoped counts.

The verifier imports neither SymPy nor the producer.  Using only the Python
standard library, it:

1. proves each degree-at-most-four section polynomial irreducible over `Q`
   using an exact finite-field witness;
2. rechecks that the pinned rational interval selects exactly one real root;
3. implements exact arithmetic and inversion in `Q[t]/(q)`;
4. reconstructs all 114 specialized base factors for every section;
5. computes squarefree parts, boundary quotients, gcds, and Sturm sequences;
6. proves every point interval and common-owner group;
7. proves complete per-factor root ownership and all cell counts; and
8. rejects 12 hostile claim and certificate mutations.

Run:

```bash
python ai/omreal/verify_diag3_pair_global_four_support_final_section_lift.py
```

## Remaining pair frontier

There are no unresolved algebraic `t` sections in this bounded base problem.
The next proof-bearing target is to lift the one base-only, 20 linear, and one
quadratic original wall in `v` over the complete sector-and-section base CAD,
then emit face-compatible closure data for both square-pyramid supports.
