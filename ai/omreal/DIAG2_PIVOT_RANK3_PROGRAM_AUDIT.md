# Rank-three Euclidean programs do not control the one-row double lift

## Verdict

The rank-three Euclidean-program theorem gives **no justified improvement**
to the current bound

\[
                 \widetilde H_q(P_b;\mathbb Z)=0\qquad(q\ge5).
\]

This is a sharp hypothesis mismatch, not a counterexample to the desired
vanishing for `q>=2`.  The one-row projection `P_b` may still have that
vanishing for a different reason.

There are two independent obstructions to applying the theorem:

1. a height row parametrizes a **lifting/coextension**, which dualizes to an
   extension problem of rank six, not a rank-three program; and
2. `P_b` is a semialgebraic coefficient/support locus for a **partial**
   chirotope, not the abstract weak-map extension poset whose contractibility
   characterizes a Euclidean program.

The exact disconnected line slice in `verify_double_contraction_gap.py` is
fully consistent with this verdict and rules out the most literal affine
program-feasible-set identification.

## 1. Exact form of the two lift rows

At a fixed literal double-contraction base, let `D` contain the six remaining
parent labels and the two private extension labels.  Thus `|D|=8`, and write
the fixed rank-two quotient columns as `a_x` for `x in D`.  With contracted
parent columns denoted `e,f`, the remaining columns have the form

\[
                         v_x=(a_x,h_x,k_x).
\]

After contracting `f`, the first row `h` gives the rank-three configuration

\[
 N_h=\{(a_x,h_x):x\in D\}\cup\{e\},\qquad N_h/e=A_b.                \tag{1}
\]

Thus `h` parametrizes realizable **one-element liftings** of the fixed
rank-two quotient `A_b`.  Lifting is dual to extension, and

\[
                  \operatorname{rank}(N_h^*)=9-3=6.                \tag{2}

\]

Fixing `h` and choosing `k` is another coextension: the resulting rank-four
configuration `M_(h,k)` satisfies `M_(h,k)/f=N_h`.  Dually this is a
single-element extension of the rank-six matroid `N_h*`; indeed

\[
              \operatorname{rank}(M_{h,k}^*)=10-4=6.               \tag{3}

\]

Consequently neither stage is an extension program of rank at most three.
Calling the intermediate primal configuration `N_h` rank three does not fix
this variance: the variable `k` is a coextension of `N_h`, and the theorem on
rank-three extension programs is not a theorem on all coextensions of a
rank-three matroid.

## 2. The private-extension bases prevent a fixed full program

The incidence problem prescribes all parent bases and every basis containing
exactly one private extension column.  It prescribes no basis containing both
private columns.  There are

\[
                            \binom82=28                              \tag{4}

\]

such missing rank-four bases.  After contracting `f`, seven missing
rank-three bases remain: the two private labels together with any one of the
other seven labels of `N_h`.

Hence, even at fixed quotient coordinates, the allowed first rows cross
walls at which these unprescribed triple signs change.  They do not realize
one fixed full rank-three oriented matroid.  Completing the partial
chirotope separately on each stratum does not solve this: the existence of a
compatible second row is exactly the extra gluing condition whose topology
defines `P_b`.

The possible coincidence of the two private quotient points makes the
fixed rank-two quotient itself nonuniform on some base strata.  The
rank-three theorem permits nonuniform full matroids under its loop/nonloop
hypotheses, but it still requires a full oriented matroid and a fixed program;
it supplies no theorem for this partial family.

## 3. What the Euclidean theorem actually says

Sturmfels--Ziegler, *Extension Spaces of Oriented Matroids*,
[Corollary 4.5](https://www.mi.fu-berlin.de/math/groups/discgeom/ziegler/Preprintfiles/020PREPRINT.pdf),
proves that every oriented matroid of rank at most three is strongly
Euclidean.  Their relevant objects are:

* a fixed full program `(M!,g,f)`, where `f` is not a coloop and `g` is not a
  loop; and
* the abstract poset `E(M!,g,f)` of single-element extensions `f'` of
  `M! minus f` satisfying the exact contraction equality
  `(M! minus f plus f')/g=M!/g`, ordered by weak maps.

Their Corollary 3.12 says this **abstract poset** is contractible exactly when
the fixed program is Euclidean.  It does not identify the order complex with
the space of real coefficient matrices realizing those extensions, nor with
a projection obtained by existentially quantifying a second lift row.

The distinction is essential even in rank three.  The same paper proves:

* the full abstract extension poset of a rank-three oriented matroid is
  homotopy equivalent to `S^2` (Corollary 4.5 together with Theorem 1.2), not
  contractible; and
* there is a realizable rank-three oriented matroid whose **realizable**
  extension subposet has second Betti number at least three (Theorem 1.1 and
  Proposition 2.2), although every rank-three oriented matroid is strongly
  Euclidean.

Thus abstract Euclideanness cannot, by itself, imply the requested geometric
`H_q(-)=0` for `q>=2`.  One would need an additional theorem identifying the
actual semialgebraic support locus with the relevant order complex and proving
contractible Quillen fibers across all partial-completion strata.  No such
hypothesis is present here.

## 4. Regression against the exact line slice

For a fixed realizable linear program, feasibility in its decision variables
is convex, so its intersection with an affine line is an interval.  The
row-2599 certificate gives a line in one fixed rank-two quotient fiber on
which the projected extra-feasibility locus is feasible at both ends and
infeasible throughout `[1/2,3/2]`.  Therefore `P_b` cannot be the feasible
region of one fixed realizable program under the natural affine height
coordinates.

This regression does not show that the full `P_b` is disconnected: the two
line pieces may connect around the certified interval.  It also does not
preclude a new stratified/topological argument.  It confirms exactly the
scope mismatch above.

The bookkeeping and the existing exact certificate are rerun by

```console
python ai/omreal/DIAG2_PIVOT_RANK3_PROGRAM_AUDIT_VERIFY.py
```

## 5. Proof-safe conclusion

No double-contraction Leray term can be removed solely by citing
rank-three Euclideanness.  The finite cofactor-stratification target in
`DOUBLE_CONTRACTION_FIBERS.md` remains necessary if this route is pursued.
In particular, the terms of bidegrees `(3,4)`, `(4,3)`, and `(5,2)` are not
killed by the program theorem.
