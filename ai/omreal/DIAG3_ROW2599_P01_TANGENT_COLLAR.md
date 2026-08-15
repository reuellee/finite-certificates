# Diagonal three: the row-2599 `p01` tangent collar

## Result

The exceptional `p01` pair edge in the row-2599 flow-triangle canary has an
exact relative bad-locus collar to the previously certified common `[2467]`
endpoint.  This repairs the missing *pair-wall collar* without reviving the
false direct wall slide.

The result is local.  It does **not** construct a comparison prism, the mixed
three-cell `J`, a global pair-frontier cover, or diagonal three.

## Why the direct collar failed

The earlier two-parameter attempt holds the `d01` root at its `[1234]`
first-wall value while moving labelled column 7 in the common-ray direction.
Block 0 becomes good at the exact witness wall

```text
83503134767238851186305349765512866 /
43552580189648394406194000441042241
```

before the first additional parent corner `[1367]`.  The exact good covector
in the predecessor audit proves that changing the circuit support cannot fix
that planar route.

## The nonradial repair

At the witness wall, perturb the first coordinate of labelled column 6 while
continuing the common-column parameter.  The four exact segments are:

| segment | identically zero parent wall | endpoint wall |
|---|---|---|
| source to witness | `[1234]` | block-0 coefficient `134` becomes zero |
| off-plane tangent | `[1234]` | `[1367]` |
| root adjustment | `[1367]` | `[2467]` |
| rational graph | `[2467]` | common apex |

For the off-plane segment, the common parameter advances by `9/160`.  The
column-6 perturbation at its endpoint is

```text
3358010538087089065822291885427450701681795 /
3308387436982263269937203185897076819775106.
```

This is derived by imposing `[1367]=0`, not supplied as an unchecked witness.
The signed derivative of the vanishing block-0 coefficient is strictly
positive, so the segment enters the bad side of the Gordan wall.

On `[1367]`, the exact root parameter reaching `[2467]` is

```text
234256547531343777781047691330195444590421787902374123738445539062790489112404622131159 /
13372644039892933623810456407340392486129320262099558845715262274062239731375045118995681.
```

For the final leg, interpolate the common and off-plane parameters and solve
`[2467]=0` for the root.  The root is a rational function.  Its denominator
has three strictly positive exact Bernstein coefficients, so multiplying
labelled column 2 by that denominator is a positive projective gauge.  The
cleared polynomial path stays on `[2467]` and ends at the existing common
apex, up to that certified positive column scaling.

## What is certified

For every segment, the verifier reconstructs and checks:

- all 70 prescribed parent-bracket signs over the whole interval;
- at least one identically zero genuine parent bracket;
- nonnegative Gordan cofactor circuits for blocks 0 and 1;
- the exact cofactor kernel identities;
- literal seams between the first three path pieces;
- exact positive projective-gauge transport, including the Gordan sections,
  at the final two seams; and
- the off-plane derivative which avoids the former witness-wall obstruction.

Consequently the three pair edges `p01`, `p12`, and `p20` now each have a
certified relative wall collar in this single row-2599 canary.  These are still
only one-dimensional base collars.  A complete comparison incidence needs a
bad-locus prism between each swept face `K(pij)` and its relative collar, with
all lateral faces identified.  The signed sum of those prisms and the three
singleton comparisons must then realize

\[
  \partial J
  =-K(p_{01})-K(p_{12})-K(p_{20})
    +K(h_0)-K(h_1)-K(h_2).
\]

No such `J` is claimed here.

## Replay

```bash
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/verify_diag3_row2599_p01_tangent_collar.py
```

The pinned semantic digest is

```text
e3df18c1a98ccca9e022832e3656c7e2ae3a9c7c822a153c7fc40e9519e08016
```

An independently coded dense-univariate replay does not import the sparse
verifier or its polynomial representation:

```bash
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/review_scratch/DIAG3_HOSTILE_VERIFY_ROW2599_P01_TANGENT_COLLAR.py
```

Its semantic digest is
`82dda129bef8f52ce4c41fbc8b31e9a316419953bb89a9eaaf8983f9ab1379f8`.
