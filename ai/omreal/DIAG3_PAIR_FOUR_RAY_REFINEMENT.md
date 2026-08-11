# Diagonal three: exact four-ray pair refinement

## Outcome

The four primitive factor rays through the exact row-2599 transverse node
have now been continued to their first parent-bracket walls and subdivided by
**every** localized primitive residual factor.  The result is a complete,
compactified one-dimensional factor-star canary for the three signings in
`DIAG3_PAIR_RECEIVER_END_CANARY.md`.

The exact answer is a scoped obstruction:

\[
 N:\mathbb Z^{4917}\longrightarrow\mathbb Z^{4920},
 \qquad M:\mathbb Z^{4920}\longrightarrow 0,
\]

has

\[
 \operatorname{SNF}(N)=\operatorname{diag}(1^{4917}),
 \qquad \operatorname{coker}N\cong\mathbb Z^3.       \tag{1}
\]

Thus the factor star fails the split-exactness test (25) by three primitive
free classes, one for each exclusive-pair ray.  This is **not** a global
diagonal-three counterexample.  The factor star has no adjacent ambient
two-cells and no seven tangential directions along the codimension-two node;
either can supply the missing rows of `M` in the true parent-space complex.

The executable certificate is
`verify_diag3_pair_four_ray_refinement.py`.

## 1. Complete exact factor subdivision

Use the exact branch parameter from
`verify_diag3_pair_receiver_end_canary.py`, with the node at parameter zero
and the first parent-bracket wall at the outer endpoint.  One labeled
occurrence is selected for each of the `26,740` localized primitive factors.
The selector avoids the endpoint bracket unit.  Its derived-normal
determinant is restricted exactly to the branch, the node and endpoint roots
are divided out, and all remaining roots are isolated by rational Sturm
boxes.

Distinct boxes are compared by exact polynomial gcd.  This is necessary:
`39` parameters carry two or three distinct primitive factors.  Every root
of every individual factor is simple.

| factor ray | parent end | factor-root incidences | algebraic parameters | simultaneous multiplicities |
|---|---:|---:|---:|---:|
| `q0=0, q1>0` | `3578` | 2,641 | 2,613 | `2590 x 1, 18 x 2, 5 x 3` |
| `q0=0, q1<0` | `1358` | 129 | 128 | `127 x 1, 1 x 2` |
| `q1=0, q0<0` | `3478` | 1,773 | 1,756 | `1741 x 1, 13 x 2, 2 x 3` |
| `q1=0, q0>0` | `1268` | 49 | 49 | `49 x 1` |
| **total** | | **4,592** | **4,546** | **39 multi-factor groups** |

On each branch the defining factor is the only factor whose restriction is
identically zero.  The other node factor is the only factor vanishing at the
center, with multiplicity one.  No primitive residual factor vanishes at any
of the four parent endpoints after the recorded bracket unit is removed.

This distinguishes three different phenomena exactly:

* the persistent defining factor of the ray;
* a genuine interior primitive-factor crossing, possibly simultaneous; and
* the tagged parent-bracket end in the relative-infinity subcomplex.

## 2. Statuses and wall-only bad points

Every open segment is sampled rationally.  Feasibility is certified by an
exact integer strict witness; infeasibility is certified by an exact positive
Gordan circuit.  Because the factor list is complete and no parent bracket
vanishes in an open interval, the derived oriented matroid is constant on
that interval.

Writing `B` for bad and `F` for feasible in block order `(0,1,2)`, the full
table collapses to

| factor ray | exact segment status |
|---|---|
| `q0=0, q1>0` | `B F B` on all 2,614 segments |
| `q0=0, q1<0` | `B B B` on all 129 segments |
| `q1=0, q0<0` | `B B B` on 241 segments, then `B B F` on 1,516 segments |
| `q1=0, q0>0` | `F B B` on all 50 segments |

There is exactly one interior status change.  It occurs at primitive factor
`13063`, whose sole labeled occurrence is

```text
19/21/37/38 = 456/137/238/148.
```

It is a unit-free type-50 occurrence.  In the pinned algebraic root box its
unsigned relation signs are

```text
(-,-,+,-),
```

which is positive only for block 2.  Moving outward on `q1=0,q0<0`, block 2
changes from bad to feasible while blocks 0 and 1 remain bad.

Segment statuses alone do not determine the bad subcomplex: a signature can
in principle be feasible on both open sides and acquire a positive circuit
only at the wall.  The checker therefore evaluates every relevant labeled
occurrence circuit at its algebraic parameter.  Ordinary four-circuits use
their exact cofactor signs.  Localization types use their unique
common-apex three-circuit and the bracket-unit localization identity.

| factor ray | signed occurrence circuits tested |
|---|---:|
| `q0=0, q1>0` | 7,811 |
| `q0=0, q1<0` | 0 (all blocks are already bad) |
| `q1=0, q0<0` | 4,591 |
| `q1=0, q0>0` | 49 |
| **total** | **12,451** |

No feasible-on-both-sides signing is bad only at a wall.  At the four parent
endpoints an independent exact Gordan check gives the same status as the
last open segment.  At the node all three blocks are bad.

## 3. Receiver and zero-mass data

Orient the rays outward from the node.  There are exactly three loss germs
and no all-die germ:

| loss germ | dying block / factor / wall circuit | receiver block / persistent circuit |
|---|---|---|
| node to `q0=0,q1>0` | block 1 / `12874` / `2/32/43` | block 0 / `0/18/40` on factor `1657` |
| node to `q1=0,q0>0` | block 0 / `1657` / `0/18/40` | block 1 / `2/32/43` on factor `12874` |
| outward through `13063` | block 2 / `13063` / `19/21/37/38` | block 1 / `2/32/43` on factor `12874` |

Every receiver is bad on the target segment, and its displayed positive
kernel is checked exactly.  Compactness of the normalized kernel simplex
retains its zero-weight specialization at the wall.  At every base cell the
carrier retains **all** nonempty faces of the active block-mass simplex,
including singleton/zero-mass faces.  The exact counts are

```text
relative base cells with two active blocks:   8,357
relative base cells with three active blocks:   740
relative base x mass-face tags:              30,251
parent-infinity mass-face tags:                  16
```

All three loss rows are cross-factor.  Therefore the fixed-parameter
strengthening in `DIAG3_PAIR_FACTOR_ROOT_SWITCH.md` is compatible but does
not orient any of these receiver transfers: it only contracts duplicate root
choices on a single factor.  Numeric `source>target` descent is not used as a
geometric orientation.

## 4. Concrete `N,M` blocks

Let `L` be the four compact intervals joined at the node, with the four
parent-bracket endpoints in `L_infinity`.  Subdivide at all `4,546`
algebraic parameters.  The exact closed bad subcomplexes give

```text
T:    C0=370,  C1=370
E01:  C0=1515, C1=1516
E02:  C0=2613, C1=2614
E12:  C0=49,   C1=50.
```

In the block orders of (21), formulas (22)--(23) therefore give

```text
C0 = 2*T0 + E01^0 + E02^0 + E12^0 = Z^4917
C1 = 2*T1 + E01^1 + E02^1 + E12^1 = Z^4920
C2 = 0.
```

The checker assembles every signed sparse entry of `N`.  It also supplies a
unit minor without relying on a modular rank calculation:

1. each copy of `d_T` is the relative incidence matrix of a tree with one
   infinity vertex and is square unimodular;
2. for each `Eij`, delete its unique attachment-edge row; the remaining
   incidence matrix is square unimodular; and
3. every frontier block `b_ij` is supported on the deleted attachment row,
   so the combined `4917 x 4917` minor is block diagonal.

Leaf elimination checks every pivot is `+1` or `-1`.  Consequently all
nonzero Smith invariants of `N` are units and `rank N=4917`.  The three
deleted attachment rows give a primitive basis of the free cokernel.  Since
the star is one-dimensional, `M` has shape `0 x 4920`; the reduced
`bar M` has shape `0 x 3` and rank zero.  Criterion (25) fails exactly by

\[
                    H^1(C^\bullet)\cong\mathbb Z^3.    \tag{2}
\]

## 5. Exact scope and next missing certificate

The theorem proved here is complete for the compactified factor-star pair
`(L,L_infinity)`.  It closes the formerly unknown one-dimensional root and
end ledger: factor coincidences, multiplicities, segment statuses,
wall-only points, receivers, zero-mass faces, signs, and parent-end tags are
all explicit.

It does **not** justify gluing the long rays onto the two-dimensional node
square as an ambient neighborhood.  Outside the square the adjacent chamber
sectors have not been continued, so there are no certified two-cells whose
boundaries run along the refined rays.  In the full parent cell there are
also seven directions tangent to the codimension-two node stratum.  These
missing cells are precisely where nonzero rows of `M` can fill the three
classes in (2).

The next theorem-grade endpoint is therefore not another ray scan.  It is a
covered two-dimensional (or tangentially Thom-correct) neighborhood that
records, for each of the three exclusive-pair attachment classes, the signed
incidence of ambient two-cells and parent infinity.  Its reduced matrix must
have three unit pivots.  Until that exists, the four-ray result is a strong
canary and an exact obstruction to any proof that uses wall intervals alone.

## Replay

```console
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/verify_diag3_pair_four_ray_refinement.py
```

Pinned semantic digest:

```text
e8ee42d741c80497e1d9f89d7973e702765de405ae2b78420a2439a408bf0bf4
```
