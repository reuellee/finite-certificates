# Noncollinear ordinary concurrences do not force height-gradient independence

The proposed implication is false for actual uniform parents and distinct
primitive factors. The following exact witness uses global kinds48,36,49,
so it does not belong to the already-treated subclass having two factors
of global kind36 or38.

Use the inherited normalized parent whose columns6,7,8 are

    (1,-1,2,3), (1,4,-5,2), (1,7,-4,5),

with columns1,...,4 the coordinate frame and column5=(1,1,1,1). All70 parent
four-brackets are nonzero.

Choose these ordinary occurrences:

    P=123/145/246/356,
    Q=125/126/356/378,
    R=123/145/257/348.

Every three normals in each quartet are independent. Their four-normal
matrices have rank3, with unique concurrence points

    p=(1/2,1,1,0), q=(1/2,1,0,0), r=(1/7,1,1,0).

These three points span a three-dimensional vector space, so they are
pairwise distinct and projectively noncollinear. Nevertheless the exact
circuit-gradient formula for height motions along p gives

    gamma_Q=(0,0,0,0,0,0,0,0),
    gamma_R=(0,-45/14,55/14,-25/14,-5/7,0,5/14,5/14).

The two gradients have rank1. The checker also differentiates the actual
four-normal determinants independently, one height variable at a time,
and obtains the same rank. Thus the conclusion does not depend on a
primitive-polynomial normalization or on the circuit formula implementation.

The factors are genuinely distinct. Q is the canonical type37 ordinary
occurrence under permutation(1,2,5,6,3,7,8,4), and R is canonical type49
under permutation(1,2,3,5,4,7,8,6). In the normalized nine coordinates their
primitive polynomials are

    P=a+bc-b-c,
    Q=af-ai-cdi+cfg-cf+ci+di-fg,
    R=e-f+fg-g.

The actual occurrence determinants are P,(b-c)Q,-R respectively; b-c is a
nonzero parent bracket. The checker verifies irreducibility, pairwise
coprimeness, the relabelings and the exact identities.

This is not a counterexample to triple escape. There is a global relation

    Q=(f-i)P+(1-c)Q50,
    Q50=bf-bi+di-fg,

where1-c is a parent unit. Hence P=Q=0 can be replaced by P=Q50=0. Those two
ordinary occurrences share their concurrence, exposing a collision hidden
by the original choice of three defining factors. The falsifier track independently verified an even stronger full-fiber
escape for this witness; the referee independently accepted the critical
point and identified its localization-axis mechanism.

The negative result invalidates a localization of all collision-free
critical points to collinear chosen concurrences. A repaired route must
handle characteristic directions, factor replacements, or the critical
locus itself. `CHARACTERISTIC_KERNELS.md` supplies several precise kernel
lemmas and isolates the remaining higher-order kind48 and nonzero
proportional-gradient cases. Original3/9 is not established.
