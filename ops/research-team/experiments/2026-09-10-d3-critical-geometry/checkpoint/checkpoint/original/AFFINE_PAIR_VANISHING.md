# Affine parent-column elimination for a pair of residual walls

## Theorem

Let X be any normalized realization-space component of a uniform rank-four
parent on eight labels. Suppose two labeled residual-wall occurrences have
defining determinants D_P and D_Q, each a four-by-four determinant of derived
triple normals. Assume a parent label e occurs in exactly one triple of P and
exactly one triple of Q. Then

    H_c^q(X intersect Z(D_P) intersect Z(D_Q);Q)=0,
    q=0,1.                                          (1)

On a parent cell each defining determinant is a primitive residual factor
times a nonvanishing product of parent-bracket units. Thus (1) is the required
vanishing for the corresponding full pair of primitive factor walls. No
choice of positive Gordan support is being made.

## 1. The global affine model

Use a labeled projective frame among the seven labels other than e. Their
deletion realization space is an open semialgebraic subset U of R^6. The
remaining parent column lies in one fixed affine chart; its parent-sign
residence space over u in U is an open convex polyhedron C_u in R^3, possibly
empty. All inequalities are strict affine-linear in this column x.

Only one row of each determinant D_P,D_Q depends on x. The derived normal of
a triple containing x is linear in x. Multilinearity of the four-by-four
determinant therefore gives two affine-linear equations

    A(u) x = b(u),           A(u) a two-by-three matrix.       (2)

Their coefficients vary semialgebraically and continuously on U in the fixed
frame. There is no division by a possibly vanishing coefficient in (2).

For every fixed u the whole solution set in C_u is convex. Hence it is
connected whenever nonempty. On mapping to the originally specified parent
normalization, this connected fiber lies in one parent component. Restricting
to X selects whole fibers; it never cuts one fiber into disconnected pieces.

## 2. Retain coefficient rank drop as a closed stratum

Let Z be the pair-wall space in (1), with projection f:Z->U, and let

    U2={u:rank A(u)=2},       Z2=f^(-1)(U2),
    Zle1=Z minus Z2.

U2 is open, and Zle1 is closed in Z. Over the coefficient-rank-at-most-one
stratum, any consistent affine solution space has dimension at least two.
Intersecting it with C_u gives an empty set or an open convex two- or
three-manifold. Its compact-support cohomology vanishes in degrees zero and
one. Proper-support base change and the compact-support Leray spectral
sequence consequently give

    H_c^0(Zle1;Q)=H_c^1(Zle1;Q)=0.                         (3)

This includes identically zero equations, inconsistent constant equations,
dependent rows, and every coefficient-rank specialization.

## 3. The rank-two part

On U2 the affine solution spaces form an affine-line bundle. The two ordered
rows of A orient its line direction by their cross product in the fixed
oriented three-space. Let V=f(Z2). Nonemptiness of a strict residence interval
persists under a small change of u: solve (2) continuously using a local
nonzero two-by-two minor, and retain the strict inequalities. Thus V is open
in U2, hence open in R^6. This remains true after restriction to the chosen
parent component X, which is open in the full normalized parent space.

Each fiber over V is one nonempty open convex interval in its oriented affine
line. The total space Z2 is relatively open in the affine-line bundle over V.
Integration along the oriented interval fibers identifies

    R f_! Q = Q_V[-1].                                  (4)

One may equivalently retain the orientation local system; the conclusion
below is unchanged. Connectedness of the full fiber is essential here. A
family with two components that merge at infinity would not justify (4).

An open subset of R^6 has no compact connected component. A compactly
supported locally constant section must therefore vanish on each component,
so H_c^0(V;Q)=0. Equation (4) yields

    H_c^0(Z2;Q)=H_c^1(Z2;Q)=0.                           (5)

Finally the closed/open localization sequence for Zle1 subset Z combines
(3) and (5) to give (1).

The argument uses compact-support direct images, so all unbounded line ends
and all finite parent-wall ends are retained. It does not assume the
projection is proper, nor does it infer compact-support cohomology from an
ordinary homotopy equivalence.

## 4. Application to the authenticated 574-case residue

Every individual type-50 or type-51 quartet uses all eight labels, each once
or twice. In the inherited residue, a label of union degree two therefore
occurs exactly once in each quartet. The theorem applies directly, even
though the previous two-pencil test failed on that label pattern.

The deterministic support audit in verify_affine_pair_coverage.py reads the
authenticated predecessor residue and checks every actual quartet, rather
than trusting the recorded degree vector. It partitions the 574 records as
follows:

| Pair kinds | Newly covered | Remaining |
| --- | ---: | ---: |
| 50,50 | 238 | 19 |
| 50,51 | 233 | 16 |
| 51,51 | 58 | 10 |
| Total | 529 | 45 |

All 45 remaining records have union degree three at every parent label. The
populated conic example from the predecessor is one such record and correctly
fails the theorem's exactly-once-in-each-quartet hypothesis.

Combining this application with the inherited 8,902 covered pair orbits gives
9,431 of 9,476. This is a stronger sufficient pair-wall endpoint, not a count
of original D3 obligations. It does not settle original injectivity, the
45 balanced cases, or the independent triple-bad compactness obligation.

## Provenance and audit

The affine-model idea and its conditional geometric argument were already
discussed in the preceding hard-pair work. The new result here is the complete
global application, with coefficient rank drop retained, to the 529 actual
residual records that satisfy its hypothesis. It is not presented as a new
general theorem in the literature.

Base: 401602fe9f8bcfad74116b46bb5574f63b6a3040.
Input: checkpoint/checkpoint/coordinator/HARD_PAIR_RESIDUE.json.
Initial status: proof and exact source partition submitted for independent
review. No original theorem ledger change is authorized by this file.
