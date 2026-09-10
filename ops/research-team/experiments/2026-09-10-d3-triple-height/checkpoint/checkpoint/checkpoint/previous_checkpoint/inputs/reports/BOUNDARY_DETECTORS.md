# Canonical double-boundary annihilators; nondegeneracy unproved

Classification: **auxiliary deductive construction; NULL for the original
pair obligation**. This is a canonical candidate detector, not a proved
detector theorem. No original obligation decreases.

## Scope and standing input

Let X be any normalized realization cell of any realizable uniform rank-four
oriented matroid on eight labeled elements. Let rho_0,rho_1,rho_2 be any
admissible pairwise incomparable proper extension signatures. The bad loci
B_i are the actual closed semialgebraic Gordan bad loci in X. All cohomology
below is compactly supported, with rational coefficients. Define

    A_ij = B_i intersect B_j,  T = B_0 intersect B_1 intersect B_2,
    V_ij = Hc1(A_ij),         H = Hc1(T),
    r_ij : V_ij -> H,
    D(x01,x02,x12) = r01 x01 - r02 x02 + r12 x12.

The only vanishing needed for the construction and equivalence below is the
already proved Hc2(B_i)=0. In particular, **Hc0(T)=0 is not assumed**. The
argument also works over any coefficient ring for which these compact-support
localization and finite closed-cover Mayer--Vietoris sequences are defined.
Rational coefficients are used when discussing arbitrary linear left inverses.

For each i, let j<k be the other two indices and put

    W_i = A_ij union A_ik  (closed in B_i),
    C_i = B_i minus (B_j union B_k)  (open in B_i).

C_i is the stratum on which block i alone is bad. It is distinct from every
exclusive-pair stratum E_ij=A_ij minus T in the existing balanced-end theorem.

## Explicit canonical maps

The closed cover W_i=A_ij union A_ik gives the connecting map

    mu_i : Hc1(T) -> Hc2(W_i),

with convention that the preceding map is (r_ij,-r_ik). The closed/open
decomposition B_i=W_i disjoint union C_i gives

    delta_i : Hc2(W_i) -> Hc3(C_i).

Define the canonical annihilator and its opposite-pair restriction by

    tau_i = delta_i mu_i : H -> Hc3(C_i),
    kappa_i = tau_i r_jk : V_jk -> Hc3(C_i).               (1)

All maps use actual original spaces and original extension labels. They
require no selected witness, synthetic signing, circuit-root choice, or
individual escape. They exist whether or not D is injective.

Here is a cellular formula that fixes what these maps mean. Choose a common
finite semialgebraic compactification and triangulation subordinate to all
displayed sets, and take cochains relative to true parent infinity. For a
compact-support one-cocycle z on T, lift it to cochains (a,b) on A_ij,A_ik
with a|T-b|T=z. The pair (da,db) agrees on T, hence glues to a two-cocycle
w on W_i. Extend w as a two-cochain w_tilde on B_i. Its coboundary vanishes
on W_i, so it is a compact-support three-cocycle on C_i. Then

    tau_i[z] = [d w_tilde].                                (2)

Cellular restrictions are degreewise surjective on these relative complexes.
Changing either lift changes (2) by a coboundary. Formula (2) is a formula
for the canonical maps; it does not supply the still-unconstructed actual
global cellular matrices or their oriented incidence entries.

## Exact kernel and equivalence

Mayer--Vietoris exactness gives

    ker mu_i = im r_ij + im r_ik.

Localization exactness and Hc2(B_i)=0 make delta_i injective. Therefore

    ker tau_i = im r_ij + im r_ik.                         (3)

Thus tau_i automatically annihilates both unwanted incident pair images.
There is no unspecified annihilation condition hidden in this construction.

**Proposition.** D is injective if and only if all three kappa_i are
injective.

If D is injective and kappa_i x=0, (3) writes r_jk x as a sum of elements
from the other two pair images. With the signs (1,-1,1), this is a relation
in ker D whose jk-coordinate equals x up to sign. Hence x=0.

Conversely, apply tau_0,tau_1,tau_2 to D(x)=0. The two incident summands
vanish by (3), leaving respectively

    kappa_0 x12=0,  -kappa_1 x02=0,  kappa_2 x01=0.

If all three kappa_i are injective, all coordinates of x vanish. This
proves both directions, including pair classes killed by their individual
restriction r_ij. No assumption that r_ij is injective was inserted.

Over Q, if nondegeneracy were proved, choose linear maps s_i satisfying
s_i kappa_i=1 on V_jk. Then

    L01=s_2 tau_2,   L02=-s_1 tau_1,   L12=s_0 tau_0

give L D=1 on V01 direct-sum V02 direct-sum V12. The left inverses s_i
are conditional algebraic choices; none has been constructed geometrically.

This is an exact canonical form of the proposed backward detector idea.
Its required nondegeneracy is **equivalent to the original obligation**,
so the construction alone earns no original theorem credit.

## The one-boundary selective-lift attempt

Fix distinct i,j,k. Set U=B_i minus B_j and E=A_ik minus B_j. The set E is
closed in U; its complement is C_i. Single-bad Hc1,Hc2 vanishing gives an
isomorphism

    theta_ij : Hc1(A_ij) -> Hc2(U).

The pair frontier map epsilon:Hc1(T)->Hc2(E) satisfies the naturality square

    epsilon r_ij = q theta_ij,
    q : Hc2(U) -> Hc2(E).                                  (4)

The variance matters: q is restriction from U to its closed subset E. There
is no canonical degree-preserving extension-by-zero map in this direction
from constant-coefficient Hc2(E) back to Hc2(U). Properness of E -> U does
not supply such a cohomological map.

The exact obstruction and ambiguity to lifting epsilon(y) through q are
visible in

    Hc2(C_i) -> Hc2(U) --q--> Hc2(E) --eta--> Hc3(C_i).       (5)

A lift exists precisely if eta epsilon(y)=0, and two lifts differ by an
element of im[Hc2(C_i)->Hc2(U)]. A choice of section on im q, even if
available, does not by itself kill both rival pair images. The double-boundary
construction (1) resolves the annihilation issue, but leaves nondegeneracy.

## What support-plane geometry does and does not supply

On a fixed selected Gordan coordinate face U, a support-plane residence
motion multiplies each selected normal a_u by a positive scalar s_u. Its
witness transport is

    lambda_u -> (lambda_u/s_u) / sum_v(lambda_v/s_v).

This formula is continuous on the closed normalized face and preserves zero
weights while the s_u remain finite and strictly positive. It proves no
continuation when a needed scale degenerates at the true parent boundary.
It also gives no transport for a different block whose rows are not in the
selected plane family. Membership in C_i requires the other two blocks to
remain good. That condition is not part of the selected-face formula.

The tiny exact replay demonstrates the latter logical limit inside a genuine
uniform rank-four eight-column parent geometry. Take y_t=(1,t,t^2,t^3),
t=0,...,7, and replace column 1 by column 1 + column 2. All 70 ordered parent
brackets stay positive. Every normal n12k is unchanged, whereas

    n145(new) = n145(old) + n245(old)

is not proportional to n145(old). The two summands cannot be proportional:
that would put columns 1,2,4,5 in one three-plane, contradicting uniformity.
The exact vectors are recorded in GEOMETRY_REPLAY.json.

**Scope of this discriminator:** it refutes the extrapolation from preservation
of a selected support-plane family to positive rescaling of every derived
normal. The selected family is not asserted to be a positive Gordan witness
for an admissible signature. No feasibility flip, actual detector failure,
counterexample to D3, or exhaustive detector impossibility is claimed. The
falsifier's separate actual triple-bad-stalk analysis is the appropriate
admissible-signature test of a local/sheaf shortcut.

## Finite lemma frontier and null endpoint

The checked formal lemmas are (a) the closed-cover connecting map, (b) the
localization injection from Hc2(B_i)=0, (c) the exact kernel (3), and (d) the
all-three nondegeneracy equivalence. These hold under the full original
quantifiers.

The first missing geometric input is a construction proving that every
nonzero class x in Hc1(A_jk) has a nonzero signed three-dimensional trace
kappa_i(x) in the actual single-exclusive C_i. Its proof must include all
zero-weight specializations and true-infinity attachment. Selected-face
transport does not provide that trace or show it is nonzero. Assuming its
nonvanishing would assume an equivalent part of the original pair theorem.

A sufficient support-plane proof would have to provide a global relative
chain model on C_i, with the two other blocks' good-locus truncations included;
identify (2) with its oriented trace map; and prove no opposite-pair class
has zero trace. None of these new geometric steps has been established.
There is no certified smaller residual or bounded global successor here.

Discovery therefore stops at **NULL**. The strongest surviving discriminator
is the nonzero-trace property for kappa_i on all opposite-pair classes,
equivalently the actual balanced frontier blocks already isolated in the
source. Further signing enumeration or a local witness contraction cannot
answer that property. All seven original obligations remain open, the ledger
remains 2/9, and the pair coverage/residual remain UNKNOWN.
