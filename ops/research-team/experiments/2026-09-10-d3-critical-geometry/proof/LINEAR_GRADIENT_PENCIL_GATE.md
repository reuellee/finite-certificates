# A linear-kernel pencil is necessary for collinear criticality

Let C_Q,C_R:R4 to R8 be the full one-parent directional-gradient maps for
two ordinary wall determinants at an actual uniform common zero. The j-th
component C_Q(v)_j differentiates Q after replacing Y_j by Y_j+t v; define
C_R similarly. For the unique ordinary concurrences q,r,

    C_Q(q)=0,  C_R(r)=0.

For global49,50,51 the separately proved characteristic-kernel result says
these kernels are precisely the lines spanned by q,r. This rank statement is
an input from the independent noncollinear track, not proved here.

Suppose an anchor concurrence p is distinct from q,r and lies on their line.
Write p=a q+b r with both a,b nonzero. Then

    gamma_Q(p)=b C_Q(r),  gamma_R(p)=a C_R(q).

Thus the two vertical gradients are dependent exactly when C_Q(r) and C_R(q)
are dependent. Under the point-kernel input both of these vectors are nonzero.
If C_R(q)=c C_Q(r), where c is nonzero, then the rectangular pencil has the
explicit linear polynomial kernel

    (C_Q-t C_R)(q+c t r)=0  for every t.

Conversely this identity implies C_R(q)=c C_Q(r) and hence the dependence
of the vertical gradients for every third point p on their common line.
It is independent of the chosen nonzero scalings of the wall equations,
concurrences and parent-column representatives.

In particular, every four-by-four minor of C_Q-t C_R vanishes identically
as a polynomial in t at a collinear critical parent. This is stronger than
the existence of a single additional parameter value at which the pencil is
singular. The required kernel is linear in t and joins the two known
concurrence kernels. Merely knowing that a pencil is singular everywhere
does not, without further argument, supply this degree-one kernel.

This provides a pair-only necessary-and-sufficient test for a third collinear
point to be vertically critical, assuming the point-kernel statement. It
does not prove that actual wall pairs never satisfy the test. It does not
put the common image vector into row(B_P), and therefore does not silently
assume a second common stress. A structural exclusion or an exact witness
for such linear-kernel pencils is the next discriminating object for the
remaining all49/50/51, all-block-ranks4 collinear branch.

The independently replayed regular rank11 canary already fails this gate:
there p=e3, q=e4 and r=e3+e4, so C_Q(r)=gamma_Q(p) and
C_R(q)=-gamma_R(p). The nonzero two-by-two gradient minor recorded in
`COLLINEAR_RANK11_REPLAY.json` therefore also certifies their independence.
No additional sample or universal exclusion is inferred.
