# Diagonal three: exact first-new-event master-closure atlas

## Result

The row-2599 master-closure compiler has crossed its first genuinely new
residual event.  In the exact two-dimensional parent plane of the original
transverse node, normalize the two pinned branch values by

```text
z0 = q0 / 10^12,    z1 = q1 / 10^12.
```

On the square `|z0|,|z1| <= 64`, exact replay of all 84,840 labelled
residual restrictions finds precisely three residual branches:

1. the pinned branch `q0=0` with 65 labelled occurrences;
2. the pinned branch `q1=0` with 65 labelled occurrences; and
3. one new affine factor, carried by derived-row fourset `(2,8,22,49)`.

The new occurrence corresponds to the four source triples

```text
(0,2,3), (1,3,4), (1,2,6), (4,5,7).
```

After primitive normalization its exact equation is

```text
-2441327503069497643632051255408343070157302308369623
+59793431655840338468670905373092307097000000000000*z0
-4625538281148206669263848248874756608000000000000*z1 = 0.
```

The line meets `q1=0` transversely inside the declared domain and does not
meet `q0=0` there.  Thus the atlas contains two ordinary transverse
two-wall nodes and no higher specialization.

This is an exact local theorem in one parent plane.  The honest 9DVL score
remains **2/9**: the certificate does not cover the full nine-dimensional
row-2599 parent cell and does not address the separate triple compactness
obligation.

## Why this is the first new event

Every residual polynomial is translated to the old rational node.  If it
vanishes there, the verifier divides by exactly one of the two pinned linear
branches and audits the quotient.  It then changes coordinates exactly from
the centered matrix entries to `(z0,z1)`.

For every nonconstant event factor other than `(2,8,22,49)`, exact monomial
dominance proves

```text
|constant term| > sum |nonconstant coefficient| * 64^degree.
```

The smallest remaining relative margin is positive and occurs at fourset
`(26,31,42,48)`.  The same strict test holds for all 70 parent brackets; the
smallest parent margin occurs at basis `(0,1,5,7)`.  Consequently no other
residual branch or parent boundary enters the entire square.

The unique new factor is affine.  Its exact first contact with expanding
centered `L_infinity` squares is therefore

```text
z0 =  813775834356499214544017085136114356719100769456541
      / 21472989978996181712644917873989021235000000000000,

z1 = -z0.
```

This proves both that the event occurs and that no event occurs earlier.

## The 64-box closure atlas

The declared box levels in each normalized branch coordinate are

```text
-64, -48, -32, -16, -8, 8, 16, 32, 64.
```

The exact box census is

| box class | count |
|---|---:|
| no wall | 42 |
| one wall | 20 |
| transverse two wall | 2 |
| unclassified or higher specialization | 0 |

Adding the pinned axes and clipping the new affine line produces a global
regular-CW refinement with

| dimension | cells |
|---:|---:|
| 0 | 110 |
| 1 | 199 |
| 2 | 90 |
| total | 399 |

There are 171 atomic box-boundary sign words.  Of these, 133 are shared by
two boxes and agree with opposite orientations.  The verifier checks that
every box closure is a subcomplex, the union covers all 399 cells, and every
two-cell interior belongs to exactly one box.  It also reconstructs the
integral cellular boundary and proves `d^2=0`.

The outer square and every internal box seam are ordinary cells.  The true
parent-infinity subcomplex is empty.

## Exact labels and middle-rank replay

Six exact rational chamber witnesses independently enumerate 26,112 topes
each.  The complete 97,224-signature universe reduces to eight feasible
chamber profiles with counts

```text
0: 70966, 3: 72, 13: 72, 23: 2,
40: 2, 50: 72, 60: 72, 63: 25966.
```

The barycentric two-skeleton has 399 vertices, 1,118 edges and 720
triangles.  Color symmetry reduces the `8^3=512` ordered profile triples to
120 profile multisets without changing ordered multiplicities.  Every exact
balanced extraction has zero middle residue over `F_2`.  Its semantic rank
digest is

```text
48140daf03371353de766d719e3812219b4612fce87bdeb8b2efc67ed50e7d06
```

Because the matrices are integral and satisfy `MN=0`, mod-two middle
exactness implies rational middle exactness by the standard rank inequality.

## Trust separation

The deterministic producer is

```console
python ai/omreal/build_diag3_pair_master_closure_first_event.py
```

and writes
`data/DIAG3_PAIR_MASTER_CLOSURE_FIRST_EVENT.json`.

The hostile verifier is

```console
python ai/omreal/verify_diag3_pair_master_closure_first_event.py
```

It recomputes the residual and parent polynomials, the unique first event,
all exact chamber labels, the CW closure, all boundary words and all middle
ranks.  It rejects thirteen corruptions, including sampled coverage, a wrong
event factor, lost dominance, a missing or misclassified box, a corrupt
boundary word, incomplete closure/signature accounting, false parent
infinity, nonzero `d^2`, dishonest middle rank or stop accounting, and a
corrupt active-factor digest.

## Consequence and next target

This run answers the bounded scaling question positively: the compiler can
cross a new residual branch, add a second transverse node, glue all affected
boxes and preserve middle exactness without projection growth.

Repeating larger subdivisions in this same plane is now subordinated.  The
next proof-bearing test must change the source geometry: construct a bounded
parent-source transition object from chart zero to a genuinely distinct
row-2599 parent germ, with exact overlap or a preserved first failure.  A
sampled 178-chart assignment is not coverage.  No theorem promotion is
permitted until the full parent master closure and the independent triple
compactness obligation are both closed.
