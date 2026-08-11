# Third diagonal: standard-Cremona frontier no-go

## Outcome

The standard `P3` Cremona transformation does not provide the proposed
exceptional-fiber escape for the six hard diagonal-three factor triples.
In the normalized parent coordinates it is simply

\[
 C:(\mathbb R^*)^9\longrightarrow(\mathbb R^*)^9,
 \qquad (x_1,\ldots,x_9)\longmapsto(x_1^{-1},\ldots,x_9^{-1}).       \tag{1}
\]

It is an involutive biregular map of the coordinate torus, with

\[
 \det DC=-\prod_{j=1}^9x_j^{-2}.                                  \tag{2}
\]

Every source uniform parent cell lies in this torus.  Therefore (1) has a
singleton fiber at every source point, including points sent to a
target-nonuniform bracket divisor.  Those internal divisors are frontiers
for an attempted *target uniform-cell* argument, but they are not exceptional
divisors of the Cremona coordinate map and do not themselves create a motion
to source parent infinity.

The exact bounded canary audit also finds no common square-affine block or
triangular sequential unit graph in any standard-Cremona marking.  This note
closes no factor triple and leaves the unresolved count `1,819,789` unchanged.

## 1. Exact target-bracket classification

Let the Cremona center be the four coordinate columns `1234`, and let `B` be
a target four-bracket.  Pull its normalized polynomial back by (1), multiply
by the componentwise least denominator monomial, and primitive-normalize.
The stabilizer `S4 x S4` has one orbit for each value
`k=|B intersection 1234|`.  The complete 70-bracket classification is

| `k` | brackets | stripped pullback |
|---:|---:|---|
| 4 | 1 | coordinate-torus unit |
| 3 | 16 | coordinate-torus unit |
| 2 | 36 | a source parent bracket |
| 1 | 16 | novel six-term divisor |
| 0 | 1 | novel 24-term divisor |

Thus only the last two orbits can be internal target-nonuniform frontiers of
a source uniform locus.  None of their 17 polynomials has any of the 62
nonconstant source parent brackets or any of the `26,740` primitive residual
factors as an exact divisor.  The verifier performs `243,954` degree-filtered
exact multivariate divisions.  Here *novel* is a localized-factor statement;
the computational check is not being advertised as a general-purpose
absolute factorization algorithm.

The exact sparse digests are

```text
all 70 pulled target brackets
6d0aa74b3025c80eff8dc8bc6eacdcb3e2e70f197b8a4972ddfa50e4a0b4b791

the 17 novel pulled target brackets
3e7e5e874b16067e168e33442f2520085b2d8907a9cf4295e39014e6caaed026
```

The two novel orbits genuinely meet the source uniform torus.  For the
representatives `1567` and `5678`, respectively, exact source-coordinate
witnesses are

```text
(-8/13,-6,4,-4,3,2,-7,8,5)
(200/71,5,3,4,-7,6,-4,9,-9).
```

The pulled target bracket vanishes at the displayed point while every one of
the 70 source brackets is nonzero.  The minimum absolute source-bracket
values are `8/13` and `13/71`.  These witnesses rule out silently identifying
the novel target frontier with source parent boundary.

## 2. Why there is no exceptional fiber

Clearing a denominator monomial from a polynomial `p` gives

\[
             p^C(x)=x^m p(x^{-1}).                              \tag{3}
\]

The denominator monomial is a unit on `(R*)^9`, and applying (3) twice
returns the primitive associate of `p`.  The checker replays this identity
for all `26,740` residual factors.  Their transformed sparse database has
digest

```text
d32e5db4412a43906dac4ec26b3c6aba94ead8086a5a4370ecc46c3f7f9f6255
```

Equations (1) and (2) then give more than a generic-fiber statement: the
restriction from a source parent cell `X` to the open set `C(X)` is a
homeomorphism.  If a hard-canary intersection meets one of the 17 novel
frontiers, its Cremona fiber at that point still contains exactly that one
point.  Consequently the proposed positive-dimensional exceptional fiber
does not exist.  Proving noncompactness along such a frontier would require a
new theorem about the factor equations *inside the frontier*; it cannot be
deduced from the Cremona map.

## 3. Bounded hard-canary screens

The six pinned triples are

```text
(2277,390,22507)     (5563,16134,19284)
(12985,16183,7196)   (20355,5442,5949)
(9667,16486,26315)   (9758,24338,15810)
```

Their simultaneous `S8` images give `241,920` distinct rows, with digest

```text
fd688604376a65eddc8adac7dd1f1ad8bbc82444e3499e2ee7bf551f91d5da38
```

This exhausts all relabelings of the six canaries relative to the fixed
standard center, equivalently all standard-Cremona markings obtained by
relabeling.  The reciprocal factor equations have `14,601` nonzero
three-coordinate affinity masks and `243,705` total bits, but no canary row
has a common bit.

The slower exact derivative screen has feature accounting

```text
3,175  distinct (zero-mask, unit-mask) classes
7,260  factors with a parent-unit derivative
12,879 parent-unit derivative bits
41,400 zero-derivative bits
```

and digest

```text
dcffbf90c0fd9fdd926d2a28906b6d297ce1df223cfd65b42b45a4a8a349f08d
```

No canary row has a three-stage triangular unit graph.  These are bounded
no-go screens, not an exhaustive search over longer Coble/Weyl words.

## 4. Replay and scope

Run the compact exact classification, involution, divisor, source-witness,
and square-affine replay with

```bash
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/verify_diag3_triple_cremona_frontier_no_go.py
```

Add the slower exact triangular-unit screen with

```bash
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/verify_diag3_triple_cremona_frontier_no_go.py --full
```

The conclusion is deliberately narrow:

\[
 \boxed{\text{standard Cremona has no exceptional fiber on the source
 torus and does not close the hard canaries by the tested affine families}.}
\]

No componentwise-noncompactness claim, signature transport, chirotope
transport, or diagonal-three score change is made.
