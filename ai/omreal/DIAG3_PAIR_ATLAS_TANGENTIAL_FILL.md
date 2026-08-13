# Diagonal three: exact tangential filler for the tapered pair ribbon

## Outcome

The unique middle class in the exact tapered normal-slice ribbon has a
genuine proper ambient filler.  This is a theorem about one exact row-2599
pair end, not a global pair atlas and not a proof of diagonal three.

For the three signatures in `DIAG3_PAIR_RECEIVER_END_CANARY.md`, write
`E02=(B0 intersection B2) minus B1`.  The normal-slice calculation had

```text
H_c^1(E02; Z) = Z,
```

with its primitive cocycle supported on 242 signed edges.  Reconstructing
exact positive Gordan circuits on the complete negative `q0` end and all 242
support edges gives only 50 witness-support pairs.  Five oriented elementary
shears transport the block-0 and block-2 witnesses on every pair:

```text
(3 -> 2, -)  (6 -> 2, +)  (6 -> 4, -)
(6 -> 7, -)  (8 -> 3, +).
```

Use `d=(8 -> 3,+)`.  It is transverse to the stored two-dimensional normal
plane, with exact determinant `-63617`.

A pointwise first-exit argument is not sufficient to assemble these rays.
The first terminal can jump, making their union nonclosed and introducing a
nonrelative vertical frontier.  The exact countermodel is retained in
`verify_diag3_tangential_first_exit_no_go.py`.

The additional checker `verify_diag3_pair_tangential_frontier.py` performs
the missing complete two-parameter audit.  It proves that the actual parent
residence domain is a quadrilateral; block 1 is feasible throughout its open
interior; the complete left side is triple-relative; and the other two
terminal sides are the genuine parent walls `3578` and `1268`.  Consequently
the quadrilateral is a proper relative product strip, and the signed product
matrix below is a cellular model of the actual attachment rather than an
illustrative replacement.

The combined verifier is
`verify_diag3_pair_atlas_tangential_fill.py`.

## 1. Exact support and bottom-end coverage

The four-ray machinery restricts all 26,740 primitive residual factors to
the two node branches and isolates every algebraic root.  Along the complete
negative `q0` interval it gives 2,614 open factor segments.  Every segment
has exact status

```text
(block 0, block 1, block 2) = (bad, feasible, bad).
```

At each segment the verifier constructs integer positive Gordan circuits for
blocks 0 and 2.  Factor completeness makes their cofactor signs constant on
the open segment; at a factor endpoint their normalized weights specialize
to nonnegative zero-weight faces.  A separate exact check of 7,811 signed
labeled occurrences excludes a block-1 circuit supported only at a factor
root.

The endpoints are exact:

```text
inner endpoint: node, status BBB, hence triple-relative
outer endpoint: first parent bracket 3578, status BFB in the limit.
```

Thus the bottom attaching edge is a complete relative end, not an artificial
bounded-box edge.  The support/root semantic digest is

```text
ea98122717e86efcfb875bea0662fafef7d3eb1e58119fe840afbf9d4389d900
```

## 2. Why pointwise exits needed another audit

For each bottom point separately, the moving-witness identity transports
blocks 0 and 2 along `d` until a parent boundary.  This does not by itself
prove that the union is proper.

The exact generic no-go uses

```text
base s in [-1,1], shear u in [0,2],
first exit L(0)=1 and L(s)=2 for s != 0.
```

Every individual selected fiber has an allowed terminal.  Nevertheless
`(1/n,3/2)` belongs to the selected union and converges to a nonselected,
nonrelative point `(0,3/2)`.  Closing the union makes the central fiber
`[0,2]` relative to `{1,2}`, whose relative `H_1` is `Q`.  Hardt triviality
on open base strata does not make this jump frontier relative.

This countermodel does not occur in the row-2599 strip because the complete
active frontier can be calculated exactly, as follows.

## 3. Complete bivariate frontier

Let `s` parameterize the negative `q0` branch, normalized so that `s=0` is
the node and `s=1` is the first parent wall `3578`.  Let `u>=0` be the
`8 -> 3,+` shear parameter.  Only column 8 varies, affinely in `(s,u)`, so:

* 35 parent brackets are constant and 35 are affine;
* 140 derived-normal coordinates are constant and 84 are affine; and
* every primitive residual restriction has degree at most three.

The exact parent sign inequalities reduce to

```text
0 <= s <= 1,     0 <= u <= U(s),
```

where `U(s)>0` is affine.  Its graph is the parent wall `1268`.  All other
parent-bracket inequalities are strictly satisfied on the quadrilateral,
except for the indicated facet incidences.  The four sides are therefore:

| side | geometric role |
|---|---|
| `u=0` | bottom attaching `q0` end |
| `s=0` | triple-relative side |
| `s=1` | parent wall `3578` |
| `u=U(s)` | parent wall `1268` |

The checker restricts the full 26,740-factor certificate, strips the stored
parent-bracket units exactly, and obtains:

| bivariate degree | factors |
|---:|---:|
| identically zero | 1 |
| 0 | 1,470 |
| 1 | 10,959 |
| 2 | 14,286 |
| 3 | 24 |

The identically zero factor is the defining `q0` factor `1657`; it is not a
block-1 wall.  There are 24,515 distinct restrictions.

The fixed-unit wall-side theorem makes the positive circuit color of every
labeled residual occurrence constant throughout the parent cell.  The
checker transports the ordinary and localization fixed-unit certificates
through all label permutations, verifies exact coverage of all 84,840
labeled occurrences, and evaluates every coefficient at two exact interior
points.  Testing the complete table leaves 1,707 factors and 5,551 positive
occurrences which can change block-1 feasibility.  Their degrees are:

| census | count |
|---|---:|
| degree 0 factors | 84 |
| degree 1 factors | 823 |
| degree 2 factors | 787 |
| degree 3 factors | 13 |

There are 1,579 distinct active restrictions.  The exact active-factor-list
and normalized positive-occurrence digests are

```text
bf392d7227d6fc2d90542d6c59d92b51731458f222d54281c29617ab9e527af4
13b8b8589a0bd8fad48fe6900e2aa944ba8c6310d83b8109ab184e8a1c96b7f5
```

Substitute

```text
u = v U(s),     0 <= s,v <= 1.
```

The checker converts every restriction to the tensor Bernstein basis on the
unit square.  Of the 1,707 active restrictions, 1,700 have coefficients of
one strict sign.  Exactly seven have a zero coefficient:

* factor `12874` becomes exactly `s`, hence vanishes precisely on `s=0`;
* factors `14658`, `14798`, `16735`, `16850`, `17313`, and `17314` each
  have one zero Bernstein coefficient, at `(s,v)=(1,1)`.

Every other coefficient of those six factors has one strict sign.  Since
all tensor Bernstein basis functions are nonnegative and at least one of
the strict terms is positive away from that corner, the six factors vanish
only at the intersection of parent walls `3578` and `1268`, not on an open
side or in the interior.  Hence there is no active block-1 wall in the open
quadrilateral.

Exact Gordan classification gives `BFB` on the bottom and `BBB` on the left
side.  At the node, `8 -> 3,+` also transports the block-1 circuit, so the
whole left side remains triple-bad.  The all-strata wall theorem excludes an
isolated bad point not carried by this active-factor list.  Therefore block 1
is feasible precisely in the open `s>0` part of this quadrilateral, while
blocks 0 and 2 remain bad by the already verified moving witnesses.

The corrected frontier semantic digest is

```text
f9788b5785e68c62e77d8c355554730e0ab39581c4325c58c65e3f2b7373345e
```

## 4. Integral signed incidence

The two affine parameter directions are exactly linearly independent in
the ambient matrix space.  Independently, the shear direction is transverse
to the full stored normal plane with determinant `-63617`.  Therefore the
affine parameter map is injective.  Its restriction from the compact parent
quadrilateral into the ambient Hausdorff matrix space is a homeomorphism
onto a closed image.  Composing with

```text
(s,v) -> (s, v U(s))
```

identifies this actual compactified strip with a square whose left, top, and
right sides are relative and whose bottom is the attaching edge.  Subdivide
the bottom at the 2,614 exact factor segments.  This gives one vertical edge
above each of 2,613 interior base vertices and one strip face above each base
edge—the product-strip cells used by the matrix checker.

For the normal-slice `E02` complex,

```text
C0 = Z^2613,   C1 = Z^7342,   C2 = Z^4728.
```

Let `Q` select the 2,614 oriented `q0` edges.  After adding the vertical
edges and strip faces, the combined cochain matrices have shapes

```text
N: Z^2613 -> Z^9955,
M: Z^9955 -> Z^7342.
```

The vertical part of `N` is `-I_2613`, so it is a unit Smith block.  Clear
the original-edge entries with these pivots.  On the quotient by `im N`, the
remaining matrix is

```text
bar M = [ d_E02^1 ; Q ],
```

a square `7342 by 7342` signed integer matrix.  Exact leaf expansion removes
all 7,342 rows and columns using only `+1` or `-1` pivots.  Thus

```text
SNF(N)     = diag(1^2613),
SNF(bar M) = diag(1^7342),
```

and the middle complex is split exact over every coefficient ring.  Direct
rank replay gives

```text
rank N = 2613,   rank M = 7342,   H^1 = 0.
```

The old primitive cocycle meets the selected `q0` end only in its first edge,
with coefficient `+1`.  This is the unit incidence missing from the normal
ribbon.

## 5. Scope

The tapered-ribbon class is genuinely filled in the ambient row-2599
two-parameter family.  It is no longer a counterexample or a merely formal
matrix canary.

This does not enumerate all exclusive-pair components, all signature pairs,
or all parent cells.  A global pair proof still needs a finite
coverage-certified end complex, every zero-weight and parent-infinity face,
and a full signed `N,M` rank certificate.  No diagonal or status score is
promoted here.

## Replay

```console
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/verify_diag3_pair_tangential_frontier.py

PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/verify_diag3_pair_atlas_tangential_fill.py

PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/verify_diag3_tangential_first_exit_no_go.py
```
