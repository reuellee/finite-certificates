# Diagonal three: first exact pair residual-wall adjacency collar

## Result

`verify_diag3_pair_residual_wall_adjacency.py` supplies the first literal
residual-wall adjacency block requested by the global pair-atlas schema.  It
is a two-square exact collar, not another point germ.

The wall is canonical type 49, primitive factor 2267.  This is the smallest
primitive factor ID among the thirteen canonical two-sided wall witnesses.
Its exact center and endpoints are

```text
(a,b,c,d,e,f,g,h,i) = (20,15,-11,-111,-28,9,-33,22,8),
d_left  = -3553/32,
d_right = -3551/32.
```

The selected source colors are

```text
A = 31021161137927844,
B = 31302644972992037,
R = 31021169996281381.
```

`A,B` are bad on both sides.  `R` is feasible on the left and bad on the
wall/right, so the left square is the exclusive-pair color `E_AB` and the
wall plus right square is triple-relative `T`.

## 1. Exact isolated collar

Use elementary root 73, namely `(6 -> 2,+)`.  In the normalized chart this
is exactly `a -> a+u`.  Together with the transverse pivot coordinate, the
closed rectangle is

```text
a -> a+u,       d -> d+t,
-1/32 <= t <= 1/32,       0 <= u <= 1/128.
```

Every one of the 26,740 global primitive factors is restricted exactly to a
bivariate rational polynomial.  Pulling the rectangle back to `[0,1]^2`
and converting to the tensor Bernstein basis proves:

* factor 2267 is exactly `t`;
* each of the other 26,739 factors has strictly one-signed Bernstein
  coefficients; and
* all 70 parent brackets have strictly one-signed Bernstein coefficients.

Hence `t=0` is the only residual wall in the closed collar.  There is no
simultaneous factor crossing, no hidden parent face, and the two open halves
are genuine sign chambers.  The restricted-factor bidegree census is

| bidegree `(deg_t,deg_u)` | factors |
|---:|---:|
| `(0,0)` | 640 |
| `(0,1)` | 3,585 |
| `(0,2)` | 375 |
| `(1,0)` | 3,585 |
| `(1,1)` | 11,355 |
| `(1,2)` | 2,595 |
| `(2,0)` | 375 |
| `(2,1)` | 2,595 |
| `(2,2)` | 1,635 |

Among the nonselected factors, 13,346 certificates are positive and 13,393
are negative.  The 70 parent signs split 34 positive and 36 negative.  The
larger trial height `1/64` is deliberately not asserted: this same direct
Bernstein test is inconclusive there for factor 15226.  This is a certificate
width statement, not evidence that factor 15226 actually crosses.

The first positive parent-bracket terminal of root 73 is `203/8` on bracket
`1368` at the left endpoint, wall center, and right endpoint.  The proved
collar stops much earlier at `u=1/128`; no claim is made about the residual
frontier all the way to that parent terminal.

## 2. Fixed-unit and zero-weight transport

The unique selected labeled occurrence is occurrence 633,

```text
P = (0,7,14,28).
```

Its type-49 fixed-unit relation has coefficient supports

```text
(7,14,28,1), (0,14,28,1), (0,7,28,1), (0,7,14,1)
```

and signs `(-,+,+,-)` throughout the parent cell.  All three selected
signatures make this four-circuit positive.  Its primitive positive weights
on the two ends of the wall edge are

```text
u=0:     (112,8,8,1),
u=1/128: (1792,128,1,16).
```

The verifier replays the following exact endpoint five-circuits:

| color | side | auxiliary | primitive positive weights |
|---|---|---:|---|
| `A` | left | 1 | `(53775,1,3840,3841,15)` |
| `A` | right | 33 | `(24651040,1762656,1758465,6880,1)` |
| `B` | left | 48 | `(125475,8953,8900,35,1)` |
| `B` | right | 1 | `(53745,1,3840,3839,15)` |
| `R` | right | 1 | `(53745,1,3840,3839,15)` |

At `t=0`, each listed five-support cofactor vector specializes to the
four-circuit weights above with auxiliary coefficient exactly zero.  This is
checked for every selected color, every auxiliary `{1,33,48}`, and both ends
of the wall edge.  A direct integer vector

```text
(41230745460380018,
 618622239402628941,
 618461184826892161,
 7313520)
```

realizes `R` in the left endpoint arrangement.  The isolated oriented
matroid chambers then transport this feasible color over the open left
half.  On the wall and right, the displayed positive circuits make `R` bad.

The optional complete-tope replay gives the independent selection census:

```text
common-bad signatures:               44962
wall-active common-bad signatures:     814
minimum robust overlap:                 20
minimum witness pair:                  (B,A)
left-only exchanged topes:                2
smallest exchanged receiver:              R
```

The pinned pair has exactly the 20 common robust roots

```text
14,15,16,17,73,76,77,80,82,88,
93,98,101,103,104,105,106,108,109,110.
```

Root 73 is the smallest one whose selected wall circuit remains compatible
for all three colors.

## 3. Signed incidence and `MN=0`

Subdivide the collar at `t=0`.  With vertices

```text
BL,BW,BR,TL,TW,TR
```

and edges

```text
bL,bR,tL,tR,vL,vW,vR,
```

orient each square by `(t,u)`.  Its signed boundaries are

```text
boundary(qL) = bL - tL - vL + vW,
boundary(qR) = bR - tR - vW + vR.
```

The absolute matrices have integral and mod-two ranks `(5,2)`.  Quotienting
by the triple-relative right square and its wall edge leaves

```text
C0 = (BL,TL),
C1 = (bL,tL,vL),
C2 = (qL),

boundary_1 = [-1  0 -1]
             [ 0 -1  1],

boundary_2 = [ 1]
             [-1]
             [-1].
```

Thus `boundary_1 boundary_2=0`.  In the schema's cochain convention,
`N=boundary_1^T` and `M=boundary_2^T`, so signed integral `MN=0`.  The
integral and mod-two rank pairs are both `(2,1)`, whose sum is
`dim C1=3`.  The visible `-I_2` minor in `boundary_1` and the unit entry in
`boundary_2` are unit Smith pivots, so this local relative block is split
exact over the integers.

## 4. Exact source accounting

Literal column relabeling transports the matrix path, root, colors, and
incidence block, so it produces exact geometric collars rather than merely
renaming factor polynomials.  The S8 replay gives

| accounting item | count |
|---|---:|
| distinct full labeled source records | 40,320 |
| distinct receiver signatures in that orbit | 40,320 |
| type-49 labeled wall occurrences | 10,080 |
| distinct primitive factor identities | 10,080 |
| identities also in the schema's 10,844 sampled two-sided list | 3,720 |
| relabeled parent cells equal to row 2599 | 0 |
| canonical row-2599 receiver assignments covered | 0 |

The `3,720` intersection is only factor-identity accounting.  It is **not**
3,720 certified row-2599 adjacencies: none of the transported parent sign
cells is row 2599.  Likewise the free 40,320-element receiver orbit covers
zero of the 97,224 canonical row-2599 receiver assignments as geometric
source records.

## Scope and remaining blocker

This closes one honest residual-wall adjacency block, including its entire
receiver-colored two-parameter collar and all zero-weight faces.  It does
not connect any two of the 178 stored row-2599 germs.  Consequently it does
not reduce the row-2599 chart-adjacency deficit, certify the global chamber
graph, or imply pair `H_c^1` vanishing.

The next genuinely global step must construct a path in the row-2599 parent
cell, isolate its complete residual crossing sequence, and attach collars of
the same form to the actual 97,224 receiver assignment cover.

## Replay

Core exact collar and source accounting:

```console
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/verify_diag3_pair_residual_wall_adjacency.py
```

Complete-tope pair/root reselection:

```console
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/verify_diag3_pair_residual_wall_adjacency.py --full-selection
```

Pinned semantic digests:

```text
core:  b46be52d472acba6aecc168d26de8faef37e2e68bb4ca1457ce0c9a21307a6c2
full:  13f27e194bed826cb184cab678df017066f7193b0442be251e9d1c68e454b6a6
```
