# The entire critical locus for the shared-plane witness triple

Use the occurrences from `escape_global_graph.md`. A full ordinary P48
contraction chart, on its fixed normalization sign sector, has matrix

    (1,0,0,0,       u,      v,      w,      t)
    (0,1,0,0,    2u-1,   2v-3,   2w+x,   2t+z)
    (0,0,1,0,    2u-1,     2v,   2w+y,   2t+k)
    (0,0,0,1,       1,      3,      2,      5).

The fixed concurrence is p=(1,2,2,0). The projected coordinates are(x,y,z,k)
and the heights are(u,v,w,t). This is the accepted four-line contraction
normal form: the six high-parent projections are fixed, and the two omitted
parents7,8 have free projected coordinates(x,y,2),(z,k,5). Their third
coordinates are fixed using excluded-plane parent units. The height frame
is parents1,...,4. Constant sign choices are retained as in the global
ordinary model; relabeling or fixed parent reorientation transports the
same conclusions without identifying components.

Direct expansion gives P=0 and

    F=Q=-4ktv+6kt+10kvw-15kw+12t^2-10tvx+4tvz-30tw,

    R-(2u-1)F=3(k+2t)(2u-1)H,
    H=t(x-2)-w(z-5).

The extra factors are parent units: 2u-1=-[1245], k+2t=-[1248].
Thus the full triple zero locus in the parent residence is exactly F=H=0.
Moreover [1234]=1, so the identity can be written homogeneously as

    [1234]R+[1245]Q=3(k+2t)(2u-1)H.

The polynomial on the right is identically zero in all heights precisely
on the closed projected-base locus

    B={x=2,z=5}.

There is no additional branch: the nonzero polynomials k+2t and2u-1 do
not make the full coefficient identity vanish unless both coefficients
of H vanish.

The vertical rank can be determined everywhere, including all special
projected parents. Write F=vL+C, where

    C=3(2t-5w)(k+2t).

The quantities v=-[2346], 2t-5w=-[2378], and k+2t=-[1248] are parent
units. On F=0, therefore, F_v=L=-C/v is nonzero. On the triple locus,
the original pair of vertical differentials is related by invertible
parent-unit row operations to(d_h F,d_h H).

Outside B, d_h H=(0,0,-(z-5),x-2) is nonzero and has zero v entry. It is
independent from d_h F. On B, d_h H=0 while d_h F remains nonzero. Hence

    {F=H=0 and vertical rank<2} = {F=0 and x=2,z=5}.

This is an exact classification of the entire vertical critical locus for
this support triple on the full contraction chart, not a sample or a
first-order approximation at the witness. By the closed parent-unit
proportionality theorem in `escape_redundant_height.md`, it has H_c^0=0.

The inherited parent corresponds to(x,y,z,k)=(2,-7,5,-6) and
(u,v,w,t)=(1,1,1,1), so it lies in this critical piece. At that projected
parent the formulas specialize to

    Q=6(2t-5w)(t+2v-3), R=(2u-1)Q.

The original source triple already has the stronger full escape in
`escape_global_graph.md`; no new net source-orbit count is assigned to this
critical-locus classification. The general theory for other support triples
remains open.
