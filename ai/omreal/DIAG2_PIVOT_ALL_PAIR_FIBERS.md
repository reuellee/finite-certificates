# Complete labeled residual-pair noncompactness by affine fibers

## Result

Every connected component of the common zero set of two distinct labeled
residual factors in a normalized uniform `UOM(4,8)` parent cell is
noncompact.  Equivalently, the exact relative-label census is now complete:

\[
                         \boxed{9,476/9,476}.
\]

The earlier exhaustive audit settled `9,354` of the `9,476` unordered pair
orbits by bracket-product Jacobian minors, common translations, or common
weighted tori.  It left 122 orbits in the six type pairs

| unordered anchor types | residue before this theorem |
|---|---:|
| `(49,49)` | 7 |
| `(49,50)` | 6 |
| `(49,51)` | 12 |
| `(50,50)` | 32 |
| `(50,51)` | 38 |
| `(51,51)` | 27 |
| **total** | **122** |

All 122 admit an iterated affine-fiber presentation.  This includes the
seven type-`(49,49)` cases whose stronger localized smoothness and
fiber-linearity theorem was proved separately.  The present argument needs
neither Jacobian saturation nor smoothness.

This is a complete local pair-wall theorem, not diagonal two.  A compact
simultaneous-bad component can in principle be assembled from several
noncompact factor walls and pair walls through bounded sign chambers,
witness transfers, and a closed component-decorated transition cycle.  No
9DVL score is promoted.

## 1. Iterated affine-fiber lemma

Let `U` be an open subset of `R^(m+1)` with coordinates `(x,w)`, where
`w in R^m`, and let

\[
                         r(x,w)=C(w)x+D(w).                 \tag{1}
\]

Every connected component of `Z={r=0} subset U` is noncompact when `m>0`.

Indeed, suppose a component `K` were compact.  If `K` contains `(x,w)` with
`C(w)=0`, equation (1) also gives `D(w)=0`.  The whole nonempty open vertical
fiber

\[
                       \{(y,w)\in U:y\in\mathbb R\}
\]

then lies in `Z`, and its interval component through `(x,w)` lies in `K`.
That interval is a connected component of the fixed vertical fiber, hence is
closed in that fiber; the fixed fiber is closed in `Z`.  It is noncompact
(it is either unbounded or approaches the boundary of `U`), so it cannot be
a closed subset of compact `K`.

Otherwise `C` is nowhere zero on `K`.  Compactness would make `|C|` bounded
away from zero there.  Near `K`, projection to `w` identifies `Z` with

\[
                 x=-D(w)/C(w)
\]

over an open subset of `R^m`.  Semialgebraic connected components are open
in `Z`; because the solution is unique, projection maps `K` homeomorphically
to a nonempty open subset of `R^m`.  But the continuous image of compact `K`
would also be compact, an impossibility in positive-dimensional Euclidean
space.  This proves the lemma.

The proof also supplies the proper escape required by compact-support
arguments.  In the first case it is the vertical interval.  In the second,
a semialgebraic curve approaches the frontier or infinity in the open
projection component.

## 2. Graphing the first residual factor

Put the first factor into a canonical projective frame.  For the only three
factor families present in the residue, the canonical equations are affine
in the displayed pivot:

| anchor type | pivot | nowhere-zero slope, up to sign |
|---:|:---:|---|
| 49 | `d` | `1` |
| 50 | `d` | `[1238]` |
| 51 | `f` | `[1456][2468]` |

Every slope is a unit on a uniform parent cell.  Solving the first equation
therefore identifies its wall with an open graph domain `U subset R^8`.
Restrict the second primitive factor to that graph and multiply by the
necessary power of the slope.  This clears denominators without changing
the zero set on the cell.

For every one of the 122 residue orbits, an exact stabilizer-equivalent
presentation makes the resulting restricted polynomial affine in at least
one of the eight graph coordinates.  The lemma with `m=7` then rules out a
compact component of the pair zero set.  A coordinate absent from the
restricted polynomial is allowed: it is the special case `C=0`, giving an
immediate vertical escape.

For 121 orbits the first factor in the stored canonical pair is a sufficient
anchor.  The unique exception is

```text
(50, 20046)
```

and becomes affine after reversing the pair and anchoring its type-51
factor.  The exact presentation census is:

| graph anchor | pair orbits |
|---:|---:|
| 49 | 25 |
| 50 | 69 |
| 51 | 28 |
| **total** | **122** |

The number of affine or absent graph coordinates in the selected
presentations is distributed as follows:

| coordinates | pair orbits |
|---:|---:|
| 1 | 11 |
| 2 | 28 |
| 3 | 14 |
| 4 | 54 |
| 5 | 12 |
| 6 | 3 |

## 3. Exact verification

Run

```console
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/verify_diag2_pivot_all_pair_fibers.py
```

The verifier independently reconstructs:

1. all `84,840` labeled occurrences and `26,740` localized factors;
2. the `S_8` factor action, canonical anchors, and their stabilizers;
3. the stored classification of all `9,476` unordered pair orbits;
4. the exact 122-orbit residue and its pinned digest;
5. every graph substitution over the integer polynomial ring;
6. the nonzero bracket-unit slope for each anchor family;
7. denominator clearing and every selected coordinate degree; and
8. the unique reversed anchor and the complete semantic digest.

The compact classification artifact is
`data/DIAG2_PIVOT_pair_classification.npz`, with SHA-256

```text
a12680b52ace15096437e5cbcfcbdb6d888c9d61a2bccf8a2d336fa5be6b7025
```

and the pinned semantic digest of all 122 selected restricted polynomials is

```text
af0fa699771292f5cca65510f32cf5c007034f4c9fdac5c3c3a49f0dfcd65846
```

The graph split retains the common normalization of `A*x+B`; it does not
primitive-normalize `A` and `B` independently.  The latter operation flips
only `B` for a type-51 anchor and would substitute the wrong graph.  The
digest above pins the corrected, equation-preserving substitution.

The exhaustive all-frame generator remains the independent source of the
classification artifact:

```console
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY.py \
  --all-frames \
  --analysis-output /tmp/diag2_pair_classification.npz
```

Its generated arrays, orbit order, mode counts, and residue digest must agree
with the committed compact artifact before the affine-fiber checker accepts
it.

## 4. Consequence and remaining obstruction

The completed exact classification is

| certificate family | pair orbits |
|---|---:|
| bracket-product minor in the primary canonical presentation | 7,217 |
| bracket-product minor after another canonical presentation | 1,091 |
| bracket-product minor after full stabilizer-frame exhaustion | 918 |
| common affine-translation escape | 124 |
| common weighted-torus escape | 4 |
| iterated affine-fiber graph | 122 |
| **certified noncompact** | **9,476** |
| **residue** | **0** |

Thus a diagonal-two counterexample cannot be an isolated compact component
of one residual factor-pair zero set.  The primary remaining target is the
universal common-shear intersection theorem of
`DIAG2_ESCAPE_SET_ATLAS178.md`; one shared shear at a point supplies a proper
ray in its entire simultaneous-bad component.  Ruling out realizable closed
cycles in the component-decorated transition complex remains an alternative
route if the elementary-shear theorem fails.
