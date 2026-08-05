# Diagonal 2: escape sets from complete topes

## The reduction

Fix a generic rank-four parent chart `T`, an extension signature `rho` which
is bad at `T`, and an oriented elementary column shear

\[
                         d=(e,f,a),\qquad e\ne f,\quad a\in\{-1,+1\}.
\]

Write `n_I(T)` for the 56 derived three-normal rows and sign them by `rho`.
Under the moving-witness transport from `e` toward `f`, only the 15 triples
`I` containing `e` and not `f` acquire a replacement term.  Its coefficient
sign is

\[
 \alpha_\rho(I;e,f)
   =-\operatorname{sort}(I-e+f)\,\rho(I)\rho(I-e+f).
\]

Delete a transported row when `alpha_rho(I;e,f) != a`; retain all other
rows.  Denote the retained signed system by `A_(rho,d)`.

> **Complete-tope escape characterization.**
>
> The oriented shear `d` belongs to the moving-witness escape set
> `E_T(rho)` if and only if no complete tope of the 56-row derived
> arrangement agrees with `rho` on every row retained in `A_(rho,d)`.

This removes minimal-circuit enumeration from escape-set computation.  One
exact arrangement tope table determines the 112-bit escape mask of every
abstract extension signature at that chart by restriction hashing.

## Proof

By the moving-witness transport identity, `d` is compatible with a positive
Gordan witness exactly when the retained signed rows have a nonzero
nonnegative dependence.  The strict Gordan alternative says that this holds
exactly when there is no vector `x` satisfying

\[
                   \rho(I)\,n_I(T)\cdot x>0
        \quad\text{for every retained row }I.             \tag{1}
\]

If a complete arrangement tope agrees with `rho` on the retained rows, its
chamber witness satisfies (1).  Conversely, if (1) has a solution, all its
retained inequalities have positive margin.  Perturb it away from the
finitely many omitted hyperplanes without changing those strict signs.  The
perturbed point lies in a complete chamber whose tope agrees with `rho` on
every retained row.  This proves the equivalence.

Nonminimal positive dependences cause no gap: their positive-kernel face
contains a support-minimal circuit, and deleting rows cannot destroy the
compatibility of that subsupport.  Thus this tope formulation computes the
same set `E_T(rho)` defined by minimal witnesses in
`DIAG2_WITNESS_EXCHANGE_AUDIT.md`.

## Exact exhaustive audits

The exact recursive arrangement enumerator supplies an integer witness for
every tope and proves coverage by hyperplane restriction.  Every chart below
has `26,112` complete derived-arrangement topes.

### Catalog parent 16

At the stored integer base chart, all `66,636` abstract uniform extensions
are enumerated directly from Grassmann--Pluecker signs.  Exactly `40,524` are
bad at the chart.  The tope restriction calculation proves:

- every pair of their 112-bit escape sets intersects;
- the minimum escape-set size is 52, attained by exactly two signatures;
- the two minimum sets are identical, so the tempting cardinality shortcut
  `|E_T(rho)|>56` is false; and
- for the exact arbitrary-witness falsifier, the two escape sets have sizes
  89 and 99, intersection size 76, and union size 112, exactly reproducing
  the independent 646,880 minimal-circuit-pair census.

The two minimum signatures are

```text
50531390688592880
21526203349335055
```

### Parent-2599 hard charts

At each of atlas charts `0`, `12`, `37`, and `176`, all `97,224` abstract
extensions are tested.  Exactly `71,112` are bad, every pair of escape sets
intersects, and the minimum size is 53.  The counts attaining that minimum
are respectively `6`, `6`, `12`, and `20`.

The semantic SHA-256 digests of the sorted `(signature, 112-bit escape mask)`
tables are:

| chart | digest |
|---|---|
| parent 16 | `c63e476f934e14908cf6d5848c3c9d97e35537d86b9955eee94bb4ae09e36130` |
| row 2599 / 0 | `f55d5868df8b5e70310e2bad71b3151dc7f8f40d9b1c10d275a2372fa5390177` |
| row 2599 / 12 | `254b3409044804cee48c2b132f542ebe894eca93b6b4dbe534c1f8c107832b9c` |
| row 2599 / 37 | `d16911b0ab2b4faa4771cb0d41d3aa3055823086e2799b96164f3caf6c025401` |
| row 2599 / 176 | `3429f7472c67cdb9cec40c91757cd618e60c9a184ea8187757545f90100e45c3` |

The optional stress run adds 15 charts chosen to be far apart in the pinned
residual-factor sign atlas.  All 19 tested parent-2599 charts have pairwise
intersecting escape sets and minimum size 53.  This is deliberately described
as exact chart evidence, not a universal theorem: the stored charts are not a
certified atlas of all parent chambers.

## What remains

The local diagonal-two target is now a finite set-system assertion:

> At every realizable generic parent chart, do the escape sets of every
> relevant proper incomparable bad-signature pair intersect?

A disjoint exact pair would refute the elementary-shear strategy even after
all witness exchanges.  A universal intersection theorem would make every
simultaneous-bad point locally escape along some parent shear, but one global
step would remain: assemble those pointwise directions to exclude a compact
component of `B_rho intersection B_eta`.  No diagonal is promoted here.

The most promising theoretical handles are the covector-elimination axioms
behind the complete-tope restrictions and the unusually strong lower bounds
52 and 53.  Pure cardinality is insufficient at parent 16, so any proof must
also use overlap structure.

## Exact verification

Run the CI-sized audit with:

```console
python ai/omreal/verify_diag2_escape_set_topes.py
```

Replay all 19 selected parent-2599 charts with:

```console
python ai/omreal/verify_diag2_escape_set_topes.py --stress
```

The verifier independently enumerates all abstract extensions and all exact
arrangement topes, computes every escape mask, proves pairwise intersection
with packed integer incidence sets, and pins semantic digests of the complete
parent-16 and all 19 selected-chart tables.
