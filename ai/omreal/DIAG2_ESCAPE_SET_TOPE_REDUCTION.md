# Diagonal 2: escape sets from complete topes

> **Promotion update.**  The pointwise intersection needed on any
> hypothetical compact component is now proved at its forced nonstructural
> support drop in `DIAG2_EXCHANGE_SATURATED_SUPPORT_DROP.md`.  The
> complete-tope masks below
> remain exact computational evidence and repair the two selected-witness
> counterexamples, but a global mask atlas is no longer needed.  Diagonal two
> is proved integrally.

## The reduction

Fix a uniform rank-four parent chart `T`, an extension signature `rho` which
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

## Antipodal sign-reversal lemma

Write `-rho` for the global sign reversal of the 56 extension signs.  This is
the extension obtained by reorienting the ninth element.  At every fixed
parent chart `T`,

\[
                         E_T(-\rho)=E_T(\rho).             \tag{2}
\]

Indeed, for every transported row,

\[
 \alpha_{-\rho}(I;e,f)
 =-\operatorname{sort}(I-e+f)(-\rho(I))(-\rho(I-e+f))
 =\alpha_\rho(I;e,f).
\]

Thus `rho` and `-rho` retain exactly the same unsigned rows for each oriented
shear.  The complete topes of the central derived arrangement occur in
antipodal pairs.  A complete tope agrees with `-rho` on all retained rows if
and only if its antipode agrees with `rho` there.  The complete-tope escape
characterization therefore gives (2), direction by direction.

Validity and chart goodness also occur in antipodal pairs: the uniform
single-element-extension axioms are preserved by reorienting the new element,
and `rho` is a complete derived tope exactly when `-rho` is.  Consequently a
finite pairwise-intersection audit may compute one representative of every
pair `{rho,-rho}`.  It must additionally check that every representative mask
is nonempty, because the two distinct antipodal signatures have the same
mask; pairwise intersection among distinct representatives then implies it
for the full bad family.

This is a universal exact reduction, not a common-shear theorem.  It halves
the masks that must be evaluated at any chart but says nothing by itself
about whether two nonantipodal masks intersect.  The independent regression
`verify_diag2_escape_antipodal_symmetry.py` reconstructs the parent-16 tope
table, checks antipodal closure, and pins the equality on five structurally
different bad signatures and their reversals.

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

## Component closure: no further direction gluing is needed

The proper-ray statement in `DIAG2_MOVING_WITNESS_SHEAR.md` has a stronger
consequence than the earlier version of this note recorded.

> **One-point component escape criterion.**  Let `C` be a connected component
> of `B_rho intersection B_eta`.  If there is one `T in C` with
>
> ```text
> E_T(rho) intersection E_T(eta) != empty,
> ```
>
> then `C` is noncompact.

Choose a common oriented shear and one compatible witness for each signature.
The moving-witness lemma transports both witnesses on the same half-ray until
the first parent wall, or to a parallel-column boundary at infinity.  Every
finite initial segment is connected, contains `T`, and lies in the
simultaneous-bad locus, hence the whole half-ray lies in `C`.  Its limit is
outside the uniform parent cell.  If `C` were compact, its image in the
Hausdorff projective-configuration compactification would be closed and would
contain that boundary limit, a contradiction.

Therefore the exchange-saturated escape-set intersection theorem proves that
every simultaneous-bad component is noncompact and closes diagonal two.  It
does **not** require a continuous choice of direction, a global vector field,
or a separate gluing argument between pointwise directions.  The decorated
wall-cycle program is retained only as a historical alternative route.

## Historical remaining target, now closed

The local diagonal-two target at this checkpoint was a finite set-system
assertion:

> At every realizable uniform parent chart, do the escape sets of every
> relevant proper incomparable bad-signature pair intersect?

A disjoint exact pair would have refuted the elementary-shear strategy even
after all witness exchanges.  The exchange-saturated theorem proves the
needed intersection at every nonstructural support drop, while the
persistent-circuit clopen alternative forces every hypothetical compact
component to contain such a drop.  By the one-point component escape
criterion above, this finishes diagonal two directly.

The most promising handles at that checkpoint were the covector-elimination
axioms behind the complete-tope restrictions and the unusually strong lower
bounds 52 and 53.  Pure cardinality was already insufficient at parent 16,
so a global-mask proof would also have needed overlap structure.

## Exact verification

Run the CI-sized audit with:

```console
python ai/omreal/verify_diag2_escape_set_topes.py
```

Run the focused sign-reversal regression with:

```console
python ai/omreal/verify_diag2_escape_antipodal_symmetry.py
```

Replay all 19 selected parent-2599 charts with:

```console
python ai/omreal/verify_diag2_escape_set_topes.py --stress
```

The separate exhaustive source-bank audit checks all 178 stored exact
parent-2599 charts and the quantitative minimum pair overlap:

```console
python ai/omreal/verify_diag2_escape_set_atlas178.py
```

See `DIAG2_ESCAPE_SET_ATLAS178.md` for its exact scope and digest.

The verifier independently enumerates all abstract extensions and all exact
arrangement topes, computes every escape mask, proves pairwise intersection
with packed integer incidence sets, and pins semantic digests of the complete
parent-16 and all 19 selected-chart tables.
