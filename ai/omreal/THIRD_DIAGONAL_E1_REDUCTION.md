# Third diagonal: exact `E_1` reduction and current obstruction ledger

## Status

The third diagonal is **not proved**.  For three extension signatures
`S={sigma,tau,upsilon}`, parent contractibility and Alexander--Lefschetz
duality reduce it to

\[
 \widetilde H_6(F_S;\mathbb Q)=0
 \quad\Longleftrightarrow\quad
 H_c^2(B_S;\mathbb Q)=0.
\]

The cofinal five-support circuit cover gives a compact-support spectral
sequence whose three total-degree-two groups are

\[
 \begin{aligned}
 E_1^{0,2}&=\bigoplus_\alpha H_c^2(C_\alpha),\\
 E_1^{1,1}&=\bigoplus_{\alpha<\beta}
       H_c^1(C_\alpha\cap C_\beta),\\
 E_1^{2,0}&=\bigoplus_{\alpha<\beta<\gamma}
       H_c^0(C_\alpha\cap C_\beta\cap C_\gamma).
 \end{aligned}
 \tag{1}
\]

Current pruning does not kill (1) term by term.  This note records a new exact
reduction of the generic single-piece column, a genuine beta-one survivor,
and exact obstructions showing what a proof still has to do.

## 1. Necessary conditions for a single `H_c^2` summand

Let `Q` be a five-set of parent triples and let

\[
 D_f(Q)=\{e\ne f:\ e\in I\in Q\Rightarrow f\in I\},
 \qquad
 \delta(Q)=\min(3,\max_f|D_f(Q)|).
\]

The omission and common-apex lemmas imply

\[
 H_c^2(C_{\rho,Q})\ne0
 \quad\Longrightarrow\quad
 Q\text{ covers all eight labels and }\delta(Q)\le2.
 \tag{2}
\]

Indeed, an omitted label supplies a three-cell deletion fiber, while
`delta(Q)>=3` supplies a three-dimensional common-apex shear fiber.  Either
case makes compact-support cohomology vanish below degree three.

On a generic derived-wall stratum, every four-subset of `Q` is
nonstructural.  For five triples this is equivalent to

* every label having degree at most three, and
* every label-pair having codegree at most two.

The five circuit cofactors are then nonzero.  Each is either a fixed
parent-bracket unit or one of the thirteen residual derived-wall atoms.  An
all-unit circuit cannot align with a realizable extension signature, because
that positive dependence would persist at every parent chart, including a
chart realizing the signature.

## 2. Exact generic census

An exhaustive exact calculation gives the following filtration.

| stage | labeled supports |
|---|---:|
| generic five-supports | 2,021,992 |
| covering all eight labels | 1,099,560 |
| killed by `delta>=3` | 339,360 |
| all-unit supports left after that pruning | 0 |
| retained generic supports | **760,200** |
| retained `S_8` orbits | **45** |

The complete retained stratification is

| `delta` | weight-gauge `beta` | residual cofactors | labeled supports |
|---:|---:|---:|---:|
| 1 | 0 | 3 | 20,160 |
| 1 | 0 | 4 | 5,040 |
| 1 | 0 | 5 | 40,320 |
| 2 | 0 | 1 | 58,800 |
| 2 | 0 | 2 | 260,400 |
| 2 | 0 | 3 | 272,160 |
| 2 | 0 | 4 | 15,120 |
| 2 | 0 | 5 | 85,680 |
| 2 | 1 | 4 | 2,520 |

Thus 44 survivor orbits have `beta=0`; one has `beta=1`.  Here

\[
 \beta(Q)=4-\operatorname{rank}_{\mathbb Q}D_Q,
 \qquad
 (D_Q)_{I}=\mathbf 1_I-\mathbf 1_{I_0}.
 \tag{3}
\]

The C++ verifier computes the rank in (3) modulo `65,521`.  This is exact:
each centered incidence row has squared norm at most six, so Hadamard bounds
every square minor of order at most four by
`(sqrt(6))^4=36<65,521`.  A nonzero rational minor therefore cannot disappear
modulo that prime, and a nonzero modular minor comes from a nonzero integer
minor.

The orbit extraction applies all 40,320 label permutations.  A separate
Python/SymPy/NumPy audit reconstructs the 52 derived-wall orbits symbolically,
uses a different triple order and genericity implementation, computes ranks
over `QQ`, and reproduces every count above.  Its audit is in
[`THIRD_DIAGONAL_SUPPORT_FILTER_AUDIT.md`](THIRD_DIAGONAL_SUPPORT_FILTER_AUDIT.md).

The unique beta-one orbit may be represented by

```text
156/456/137/347/128.
```

An independently produced lexicographic representative is
`123/125/346/378/456`.

This is only a generic relative-interior census.  Residual-wall degenerations,
zero-weight faces, and positive three- and four-circuits remain boundary data
in the cofinal closed pieces.

## 3. The beta-one type is genuine

The unique beta-one support orbit is not an empty combinatorial artifact.  At
the exact row-2599 pattern-zero chart, extension signature 1 has the
support-minimal positive circuit

```text
Q = 145/356/147/258/278
```

with primitive positive weights

\[
 (7764057116159343,
  14304162776098912,
  2440292901497385,
  11357704845786888,
  2732299507505832).
\]

Its centered incidence matrix has rank three.  A primitive balanced exponent
vector is

\[
 (-1,0,1,1,-1),
\]

so its one invariant weight modulus is

\[
 \frac{\lambda_{147}\lambda_{258}}
      {\lambda_{145}\lambda_{278}}.
 \tag{4}
\]

The exact one-bit chart realizes the same extension signature.  Hence the
signature is realizable, its feasibility region is proper, and this circuit
piece is genuinely nonempty.  This does **not** imply that the full piece has
nonzero `H_c^2`.

## 4. Infinitesimal sparse-form stabilizers: useful no-go

For each of the 45 representatives, take the exact pattern-zero chart `Y` and
its alternating cofactor tensor

\[
 c_Q=\sum_{I\in Q}c_Ie_I,
 \qquad \Lambda^3Y(c_Q)=0.
\]

The exact infinitesimal projective stabilizer is

\[
 \mathfrak g_{c_Q}
 =\{(A,\mu)\in\mathfrak{gl}_8\oplus\mathbb Q:
                 A\cdot c_Q=\mu c_Q\}.
 \tag{5}
\]

Map it to `delta Y=YA` and quotient the 32 matrix coordinates by

\[
 \{LY+Y\operatorname{diag}(d):L\in\mathfrak{gl}_4, d\in\mathbb Q^8\},
\]

a 23-dimensional gauge subspace.  Exact rational ranks give:

* 43 beta-zero representatives induce all nine tangent directions;
* the beta-one representative induces eight tangent directions;
* one beta-zero representative, `246/356/347/157/128`, also induces eight;
* every representative has at least eight nonvertical exact-`c` stabilizer
  directions.  No survivor has only vertical or scalar directions.

For the beta-one support, the looser Lie algebra which merely preserves the
five-coordinate support has dimension 21 and already surjects onto all nine
tangent directions.  Thus raw support preservation is too nonselective; the
exact tensor equation matters.

This is an infinitesimal classification at an exact compatible chart, not an
escape theorem.  The maximal real stabilizer orbit inside a parent chirotope
cell may have several ends, return, or meet lower-support strata in ways not
seen by tangent rank.  In particular, (5) alone does not kill `H_c^2`.

## 5. Exact obstructions to the current tests at all three `E_1` positions

The current deletion/shear lemmas cannot prove termwise vanishing in (1).

### Single pieces

For

```text
123/256/127/357/478
```

at the exact pattern-zero chart, deletion of light label 8 has an exit-facet
nerve which is connected with first Betti number one.  Therefore its residence
fiber has

\[
                         H_c^2(K_b;\mathbb Q)=\mathbb Q.
\]

So a proof cannot replace the global single-piece calculation by universal
degree-two fiber acyclicity.

### Pair intersections

At pattern 14, the proper incomparable signatures 0 and 6 have five-circuits

```text
134/234/156/267/258
125/246/147/358/468.
```

They have common-light label 7, but the exact exit nerve is an edge disjoint
from a point.  Hence the joint residence fiber has

\[
                         H_c^1(K_b;\mathbb Q)=\mathbb Q.
\]

Thus common-light deletion does not give universal pairwise `H_c^1`
vanishing.

### Triple intersections

At the exact pattern-zero chart, the three cofinal pieces

```text
(rho_0, 123/134/267/258/468)
(rho_4, 123/256/127/357/478)
(rho_3, 123/256/356/127/347)
```

meet.  Exact other charts distinguish the three semialgebraic pieces and
realize all three signatures, so this is not duplicate cover indexing.  Their
union degree vector is

\[
                         (3,5,5,4,4,4,5,3).
\]

It is pencil-rigid, has no common-apex shear, and its incident support-plane
normals have rank three at every label.  Therefore the present incidence,
common-apex, and plane-preserving tests leave a genuine nonempty
`E_1^{2,0}` candidate.  No compact component or nonzero `H_c^0` is claimed.

## 6. What remains

The exact generic single-piece calculation has been reduced from more than
two million supports to 45 sparse-form orbit types:

* 44 fixed-weight (`beta=0`) sparse three-vector loci;
* one one-parameter (`beta=1`) sparse three-vector family;
* their residual-wall and zero-weight boundary strata.

A plausible next calculation is an exact constructible-sheaf/CAD analysis of
these 45 types in a normalized nine-variable parent chart, using stabilizer
orbits only as a stratification aid.  It must compute the global supports of
the deletion-fiber `H_c^2` and `H_c^1` sheaves, attach lower-support faces, and
then evaluate the `d_1` and possible higher differentials in (1).  The exact
fiber examples above show why checking each fiber in isolation cannot finish
the argument.

The stabilizer census suggests a more structured version of that CAD.  For
the 43 rank-nine beta-zero types, compute the identity-component
algebraic-group orbit of the exact sparse tensor, pull the 70 parent-bracket inequalities back
to explicit unipotent/Bruhat coordinates, and determine the compact-support
cohomology of each orbit-cell intersection.  For the two rank-eight types,
adjoin one transverse modulus: the weight invariant (4) for the beta-one
type, and one still-to-be-identified geometric modulus for
`246/356/347/157/128`.  A successful version would prove that every relevant
orbit-cell component has a controlled boundary exit and would attach those
exits across zero-weight faces.  The present calculation supplies the exact
finite list and tangent dimensions, but not the needed group integration or
global boundary theorem.

## Reproduction

```bash
g++ -O3 -std=c++17 \
  ai/omreal/verify_third_diagonal_support_filter.cpp \
  -o /tmp/verify_third_diagonal_support_filter
/tmp/verify_third_diagonal_support_filter

python ai/omreal/verify_third_diagonal_support_filter_independent.py
python ai/omreal/verify_third_diagonal_beta1_survivor.py
python ai/omreal/verify_common_light_exits.py
python ai/omreal/verify_third_diagonal_triple_obstruction.py
python ai/omreal/verify_third_diagonal_sparse_stabilizers.py
```

All computations are exact.  The two support-census implementations are
independent.  No command above proves the third diagonal.
