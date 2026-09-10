# Excision of closed parent-unit-proportional height pieces

## Theorem

Use an accepted ordinary-concurrence contraction chart for P on a uniform
parent component. It has projected base A open in R4 and full open convex
four-height residences C_A. Let Q,R be ordinary occurrences. Fix polynomial
parent-unit products U(A,h),V(A,h), nonzero everywhere on the parent
residence. The products can include constants and can be obtained by clearing
rational parent-unit denominators.

Let B be the projected-base locus on which the full polynomial identity

    U(A,h)R(A,h)=V(A,h)Q(A,h)

holds in all four height variables. Then B is closed relative to A: it is
the common zero locus of the finitely many continuous coefficient functions.
The identity on the full nonempty open residence is equivalent to this
coefficient identity. In applications the weights or normalization of U,V
must make the displayed identity well defined on the chosen chart.

The subset Z_B of the full P/Q/R triple locus lying over B is closed and
has H_c^0(Z_B;Q)=0. Therefore such a piece can be excised when proving triple
noncompactness. A finite closed union of such pieces has the same vanishing.

## Proof

Because U,V are parent units, the full triple locus over B is precisely the
P/Q pair locus over B. Retain the unique ordinary concurrence q of Q.
The subset q=p is closed and imposes projected-parent conditions only;
its nonempty fibers are the entire four-dimensional cells C_A. They have
no compactly supported cohomology in degree zero.

On q!=p, retain its projected direction z in RP2 and one extension height w.
For fixed(A,z), the four Q incidences are affine in the four parent heights
and w. There are at most four equations in five variables, so every full
nonempty fiber is a positive-dimensional open convex subset of an affine
space. Rank drops only increase this dimension. Its H_c^0 is zero.
Compact-support base change and Leray, or the closed fixed-base fiber
argument, give H_c^0 for this entire open piece equal to zero. No openness
or smoothness of B is required. Closed/open localization with q=p proves
the theorem. The accepted ordinary-concurrence model supplies all original
parent signs, coefficient rank drops and projective-height transitions.

For a finite union, restriction of H_c^0 to the finitely many closed pieces
is injective. Hence their individual vanishing implies vanishing of the
union. The statement applies on every finite clopen normalization sector.

## Componentwise common factors require more

A shared polynomial factor by itself does not justify this argument. Its
zero set might retain only a proper subset of a full affine concurrence
fiber, and intersections of factor branches must not be discarded.

A sufficient extension is a closed selected branch for which every retained
concurrence-height fiber is either empty or the entire P/Q fiber, including
the q=p stratum. Then the same proof applies. This full-fiber saturation
condition must be proved from the actual equations; a gcd or generic branch
calculation does not supply it automatically.

## Actual application

For the new both-nonzero-gradient witness, take

    U=[1234], V=-[1245].

The full coefficient identity U R=V Q holds on the explicit closed projected
locus described in `escape_critical_classification.md`. Thus the exact
counterexample lies in a globally defined removable height piece. This
application includes its whole critical stratum in that support triple,
not merely the single numerical configuration.
