# Type-(49,50) pair closure

## Result

The six type-`(49,50)` cases left by the relative-label pair audit are now
settled. All six are among the exact factor IDs

\[
                8218,\ 8387,\ 12366,\ 12371,\ 20097,\ 20112,
\]

independently reconfirmed unresolved by every certificate family in
`DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY.py` before attempting anything new.

Four saturate exactly as the seven type-`(49,49)` cases do: the localized
critical ideal of the restricted second wall, after eliminating `q_49`'s
pivot, reaches the unit ideal (unbounded search budget `processed<1000,
basis<100`, matching `verify_diag2_pivot_49_pair_saturation.py` exactly), so
the common-zero locus is a smooth 7-manifold and hence noncompact:

| factor | restricted terms | degree | basis size | S-pairs |
|---:|---:|---:|---:|---:|
| 8218 | 183 | 8 | 49 | 66 |
| 8387 | 120 | 7 | 8 | 0 |
| 12366 | 72 | 6 | 9 | 0 |
| 12371 | 82 | 7 | 9 | 0 |

The other two (20097, 20112) exhaust the same bounded search without
reaching the unit ideal. This is residue against *that* method, not a rank
drop: both are affine in a coordinate (`h`; and `e,h` respectively) after the
same elimination, so `DIAG2_AFFINE_FIBER_RESIDUE_CLOSURE.md`'s strictly
weaker sufficient condition closes them anyway (noncompact, without the
stronger smooth-manifold conclusion).

This closes the entire type-`(49,50)` slice: `9,367/9,476` relative-label
pair orbits are now certified noncompact (`9,361` prior + these `6`), leaving
`109` -- which the broader affine-fiber sweep in
`DIAG2_AFFINE_FIBER_RESIDUE_CLOSURE.md` further reduces to `4`, across all
five hard factor-type families at once.

The exact checker is

```console
python ai/omreal/verify_diag2_pivot_49_50_pair_saturation.py
```

## 1. Why `q_49` is still the elimination equation

Every `(49,50)`-type pair orbit representative canonically anchors at type
49: `pair_orbit_representatives` keeps `min(forward, reverse)` under its
`(kind, second)` ordering, and `49 < 50`, so a pair between a type-49 factor
and a type-50 factor always canonicalizes to `kind=49`. The elimination
`d = b+f-bf` from `q_49 = bf+d-b-f = 0` -- the same one
`verify_diag2_pivot_49_pair_saturation.py` uses, unmodified -- is therefore
still exactly the right equation; only the *second* polynomial being
restricted changes, from another type-49 factor to a type-50 one.

## 2. Uniform-locus saturation (four cases)

Identical machinery to the type-`(49,49)` closure: substitute `d`, form the
localized critical ideal `<r,r_a,r_b,r_c,r_e,r_f,r_g,r_h,r_i>` at the 62
restricted nonconstant parent brackets, and run the same bounded
pseudo-reduction / S-polynomial search. All four reach `1`; the largest
(factor 8218) needs 66 S-pairs and a 49-element basis -- larger than any of
the seven type-`(49,49)` cases (which needed at most 19 S-pairs), but well
inside the same resource budget.

## 3. The two residue-against-saturation cases

Factors 20097 and 20112 restrict to degree-7 and degree-8 polynomials with
183 and 191 terms respectively. Neither reaches the unit ideal within
`processed<1000, basis<100`. This does not mean their gradients are
degenerate anywhere on the uniform locus -- it means the specific bounded
Buchberger-style search used throughout this repository did not find a
certificate. Both restricted polynomials are, however, affine (degree
`<=1`) in at least one coordinate (`h` for 20097; `e` and `h` for 20112), and
`DIAG2_AFFINE_FIBER_RESIDUE_CLOSURE.md` proves that alone is sufficient for
noncompactness, via the fixed-minor lemma
(`RESIDUAL_STRATUM_NONCOMPACTNESS.md`) and the fiber-linear escape
(section 3 of `DIAG2_PIVOT_49_PAIR_SATURATION.md`) combined. So all six
close; only four get the stronger smooth-manifold certificate.

## 4. Exact verification

The checker independently reconfirms the six pairs are genuine residue
(re-running the existing all-frame certificate audit scoped to just them),
re-derives the restricted polynomial and its affine-variable set for all six,
attempts the bounded saturation for the four expected to succeed (raising if
any of them now fails, or if any of the two expected-bounded cases were
somehow no longer required to fall back on the affine argument), and pins
the exact term counts, degrees, basis sizes, and S-pair counts for
regression.

```text
PASS: all six (49,50) pairs independently reconfirmed unresolved by prior certificates
PASS: restricted nonconstant parent-bracket units: 62
PASS target=8218: terms=183 degree=8 reached_unit=True basis=49 s-pairs=66 affine_in=('e',)
PASS target=8387: terms=120 degree=7 reached_unit=True basis=8 s-pairs=0 affine_in=('e', 'h')
PASS target=12366: terms=72 degree=6 reached_unit=True basis=9 s-pairs=0 affine_in=('a', 'c', 'i')
PASS target=12371: terms=82 degree=7 reached_unit=True basis=9 s-pairs=0 affine_in=('a', 'c', 'g', 'i')
PASS target=20097: terms=183 degree=7 reached_unit=not-attempted affine_in=('h',)
PASS target=20112: terms=191 degree=8 reached_unit=not-attempted affine_in=('e', 'h')
PASS: 4/6 targets fully saturate to the unit ideal (smooth 7-manifold)
PASS: 6/6 targets close via the affine-fiber argument (noncompact)
THEOREM all six type-(49,50) pair-wall common-zero loci are noncompact
STATUS certified relative-label pair orbits: 9367/9476 (via this + prior certificates); residue: 109
CAVEAT diagonal two still requires global decorated transition-cycle acyclicity
```

## 5. Boundary

This is a local pair-wall theorem, exactly like its type-`(49,49)`
predecessor. It does not promote diagonal two: compact simultaneous-bad sets
could still be assembled through decorated cycles of different wall chambers
and witness transfers, gluing several individually-noncompact pair pieces at
points where two different residual factors vanish at once. See
`DIAG2_AFFINE_FIBER_RESIDUE_CLOSURE.md` section 3 for the precise statement
of what this class of certificate does and does not establish, and
`NINE_DIAGONAL_STATUS.md` for the surrounding proof program.
