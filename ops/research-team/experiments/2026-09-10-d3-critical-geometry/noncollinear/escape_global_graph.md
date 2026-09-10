# Global escape for the both-nonzero-gradient witness triple

For every uniform rank4 parent on8 and every normalized parent component X,
the full zero locus of the ordinary occurrences

    P=123/145/246/356,
    Q=123/146/248/378,
    R=126/145/248/378

has no compact component. This concerns the entire support triple, not only
the inherited critical point. It is an explicit instance of the inherited
sequential-affine mechanism, so no new net triple-orbit count is claimed.

Normalize the first five parent points to the standard projective frame,
and the remaining columns to (1,a,b,c),(1,d,e,f),(1,g,h,i). On each original
component the necessary signs are fixed. Constant parent reorientations can
be recorded separately to obtain this chart; they are homeomorphisms and
multiply each determinant by a nonzero factor. No sign sheets are identified.
All parent-component residences are open strict-inequality subsets of R9.

Direct determinant expansion gives

    P=a+bc-b-c,
    Q=-afh+ahi-bdi+bfg,
    R=-bdi+bfg-bfh+bhi+cdh-cgh.

Define

    D=bd-bf(b-1)-ah,
    E=bg-bi(b-1)-ah.

The exact polynomial identities are

    Q=fE-iD,
    b(R-Q)=ch(D-E)+bh(f-i)P.

The factors b=-[1246], c=[1236], h=-[1248], and f-i=-[2378]
are nonzero parent units. On P=Q=R=0 the second identity gives D=E;
the first then gives (f-i)D=0, so D=E=0. Conversely P=D=E=0 gives
Q=R=0. No coefficient-zero stratum is omitted.

Thus the triple locus is exactly the rational graph

    a=b+c-bc,
    d=f(b-1)+(a/b)h,
    g=i(b-1)+(a/b)h

in the six free variables (b,c,e,f,h,i). Its intersection with X corresponds
to an open subset of R6: the graph has no pole on the parent residence and
all original conditions are strict inequalities. Every connected component
is noncompact, because a nonempty open Euclidean set cannot be compact.
The inverse map simply forgets a,d,g, so this is a homeomorphic graph
identification rather than a nonproper homotopy comparison.

There is also a direct support-level escape. Parent7 occurs only in the
single distinct normal triple378 across all three occurrences. Retaining
that plane and moving parent7 within it preserves every selected normal
plane. A parent-unit affine gauge gives a full open convex two-dimensional
residence, excluding compact components. This is an inherited light-label
mechanism, consistent with the algebraic proof and its zero novelty count.

The independent falsifier reconstruction is
`falsifier/GLOBAL_GRAPH_INDEPENDENT.json`. The graph identities and unit
matches are reconstructed by `escape_verify.py` as well. No original
diagonal is promoted by this source-triple explanation.
