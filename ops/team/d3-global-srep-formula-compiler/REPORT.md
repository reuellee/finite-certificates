# Q0 formula/compiler producer report

## Verdict

`NULL_NO_EXECUTABLE_REPLACEMENT_BACKEND`.

This is one producer handoff, not an independent acceptance review.  The
package contains useful exact formula and canary machinery, but it does not
pass Q0, open Q1, earn theorem credit, or justify cloud use.

## What was produced

[`FORMULAS.json`](FORMULAS.json) gives canonical sparse
integer-polynomial ASTs for three formula-first canaries.

- `M3_UNFILLED` is the boundary of the standard closed two-simplex relative
  to its vertex `(0,0)`.
- `M3_FILLED` is the full standard closed two-simplex relative to the same
  vertex.
- `M2` is the exact tangential first-exit formula from the frozen obstruction
  dossier, including the pointwise terminal set.

[`build_qualification.py`](build_qualification.py) implements an exact,
deliberately narrow compiler for Boolean combinations of the three standard
simplex barycentric atoms.  It enumerates every simplex face, evaluates the
formula at an exact rational relative-interior point, and uses the sublanguage
restriction to prove sign invariance on that relative interior.  It then
derives the relative signed boundary matrices and rational ranks.  The trace
in [`TRACE.json`](TRACE.json) gives:

| canary | formula-derived result | scope |
| --- | ---: | --- |
| M3 unfilled | `rank d1=2`, `rank d2=0`, `dim H1=1` | exact affine-simplex surrogate |
| M3 filled | `rank d1=2`, `rank d2=1`, `dim H1=0` | exact affine-simplex surrogate |
| common one-skeleton | identical | exact affine-simplex surrogate |
| M2 selected plus terminals | nonclosed at `(0,3/2)` | exact rejection; no complex emitted |

The M2 certificate is a whole semialgebraic curve, not a numerical sample:
`(s,u)=(t,3/2)` is selected for every `0<t<=1`, while its limit `(0,3/2)`
is neither selected nor terminal.  The compiler therefore fails before
topology rather than treating an artificial boundary as relative infinity.

The M3 complexes are **not** presented as outputs of Basu--Karisani.  They
are machine-labelled `CANARY_ONLY_NONQUALIFYING_SURROGATE`.  The exact
formula-to-complex derivation is useful for testing boundary/rank contracts,
but it is not a general semialgebraic replacement algorithm and has no
ordered-infinitesimal or real-univariate-representation lane.

## Single-bad control

The producer runs the existing pinned checker in a fresh subprocess and
records its full stdout and source digests.  It reproduces
`H_c^q(B_rho;R)=0` for `q=0,1,2` with the existing pair/triple caveat.  This is
labelled `BOUND_REPLAY_OF_EXISTING_PROVED_CONTROL_NOT_A_NEW_DERIVATION`.

## Global formula attempt

[`GLOBAL_SCHEMA.json`](GLOBAL_SCHEMA.json) expands, in canonical sparse
integer-polynomial form:

- all `70` maximal minors of the standard nine-variable normalized `4 x 8`
  matrix;
- all `56 x 4 = 224` coefficient polynomials of the derived extension
  normals; and
- the exact normalized Gordan-witness formula recipe.

The expanded raw algebra has maximum parent-bracket degree `3`, maximum
derived-normal coefficient degree `3`, `64` distinct normalized bracket
polynomials including constants, and `109` distinct normal-coefficient
polynomials including zero.  Multiplication by a Gordan weight raises the raw
formula degree bound to `4`.

The finite discrete inputs give these exact prefilter counts:

| quantity | exact value |
| --- | ---: |
| realizable unlabelled parent types | 2,604 |
| labelled frames per type | 40,320 |
| raw parent/frame presentations | 104,993,280 |
| valid abstract extensions summed over parent types | 174,937,600 |
| valid extension range per type | 54,520 to 97,224 |
| ordered distinct triples before properness/incomparability, by type | 807,780,496,606,300,008 |
| the same raw-frame-expanded prefilter | 32,569,709,623,166,016,322,560 |

These last two values are deliberately **not** the required denominator.
The first missing required input is an all-parent decision of which
feasibility regions `F_sigma` are proper and which pairs are incomparable on
the full normalized realization space.  The available extension count table
enumerates abstract valid sign extensions, not that semialgebraic inclusion
poset.  Consequently the denominator of ordered proper pairwise-incomparable
triples, and therefore Basu--Karisani's global tuple parameter `N`, remains
unknown.

A second independent input is also missing: no exact quantifier-free
`P`-closed formula has been generated for every compactified parent
realization space `Xbar_M` and genuine infinity subset `I_M`.  A uniform
first-order closure predicate can be written, but the replacement theorem
requires the quantifier-free closed output; blindly weakening strict parent
signs is forbidden and unsound.

For the chosen three-block normalized-witness template, the free-variable
count would be exactly

```text
k = 10 + 3*56 = 178.
```

Before compact-closure quantifier elimination, there are `255` polynomial
occurrences and raw degree at most `4`.  These are not exact theorem inputs
`s,d`: quantifier elimination can change both.  Thus the honest parameter
record is `(N,s,d,k)=(NULL,NULL,NULL,178-template)`.  The theorem's symbolic
bound `(N*s*d)^(178^(O(2)))` cannot be converted into an output-size, memory,
or elapsed-time forecast, both because three inputs are null and because the
published asymptotic exponent hides constants.  Fit inside the fixed cycle
ceiling is not demonstrated.

## Backend inventory

[`BACKEND_INVENTORY.json`](BACKEND_INVENTORY.json) records the search.  The
two pinned papers describe algorithms but do not provide a software or code
link.  Exact GitHub repository/code API searches for the paper title,
authors, and algorithm name returned zero matches; the PyPI names
`simplicial-replacement` and `semialgebraic-homology` do not exist.  No public
turnkey implementation was identified.  This is a bounded search result,
not proof that unpublished or private code does not exist.

Wolfram, Singular, SymPy, and the compiler here provide exact algebraic
primitives or special-case topology.  None implements the paper's
contractible-cover, ordered-infinitesimal, replacement, and diagram trace.
The optional cloud worker cannot repair a missing executable and was not
used.

Primary algorithm sources:

- [Efficient simplicial replacement of semi-algebraic sets](https://arxiv.org/abs/2009.13365v3)
- [Computing the homology functor on semi-algebraic maps and diagrams](https://arxiv.org/abs/2207.10497v1)

## Replay

```console
python -B ops/team/d3-global-srep-formula-compiler/build_qualification.py
python -B ops/team/d3-global-srep-formula-compiler/test_formula_compiler.py
```

Observed result: build completed with the fail-closed NULL verdict; all
`8/8` producer tests passed.  The tests include hostile rejection of a
polynomial outside the declared affine-simplex sublanguage, rejection of a
noncanonical polynomial AST, exact M2 sequence/limit replay, global raw
algebra dimensions, and explicit assertions that Q0/Q1/theorem/cloud flags
remain false.

## Nonconsequences

- no general simplicial-replacement implementation;
- no complete global formula tuple or exact `N,s,d`;
- no Q0 acceptance or Q1 activation;
- no global diagram, comparison, or pair-kernel result;
- no diagonal, obligation, or ledger decrease.
