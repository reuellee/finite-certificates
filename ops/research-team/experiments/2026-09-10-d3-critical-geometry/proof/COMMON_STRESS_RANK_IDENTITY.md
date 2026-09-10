# Exact remaining row-space alternatives at collinear rank11

Use the common-line matrix of `COLLINEAR_RANK_ESCAPE.md`. Put

    U=row(B_P), V=row(B_Q), W=row(B_R),
    r_P=dim U, r_Q=dim V, r_R=dim W,
    H=U intersect V intersect W.

Then, at every transverse specialization,

    rank M=r_P+r_Q+r_R-dim H.

Indeed the row space of M is the image of the linear map

    U direct-sum V direct-sum W -> R8 direct-sum R8,
    (u,v,w) -> (v+w,u-w).

Its kernel consists exactly of (w,-w,w) for w in H. Rank-nullity proves the
formula without assuming that any block has four independent rows.

Each r_S is at most4. At any actual rank11 point only the following alternatives
are possible:

| Block ranks, up to order | Common-stress dimension |
|---|---:|
| 4,4,4 | 1 |
| 3,4,4 | 0 |

If the sum of the block ranks were at most10, the stacked rank could not be11.
If the sum is11 or12, the displayed common-stress dimensions follow immediately.

The second alternative is relevant to the low global families36/38. For an
ordinary37/38 occurrence the first two selected triples share a parent root
pair a,b and its concurrence lies on their actual projective line. If this
concurrence also lies on the common line L and no parent lies on L, projection
from L sends Y_a,Y_b to the same nonzero transverse direction. The sparse
rows for abc and abd are therefore supported only on a,b and are proportional
(or zero). Hence that block has rank at most3.

In particular, a rank11 common-line configuration with one low-family factor
has the (3,4,4) pattern and no nonzero common stress. Any proposed argument
that criticality supplies a second common stress must first establish the
(4,4,4) hypothesis; it cannot silently cover the one-low case. Two low-family
factors force stacked rank at most10, consistent with the inherited stronger
two-parent-line theorem.

This is an exact structural rank identity. It neither asserts the existence
of critical rank11 parents nor proves escape for that remaining locus.
