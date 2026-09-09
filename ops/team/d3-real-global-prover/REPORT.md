# Full-source moving-base track: useful null

Starting revision: `cefc495b27247c4a76f88bce04978422161f7ce9`.
Source: `ai/omreal/data/DIAG3_triple_fullspace_critical_h1.json`, SHA-256
`c9244a47ded5736e7afe724a9914e75631a22b78653442e88c14f5c397919eb8`.
Named presentation: `(5563,16134,19284)`; canonical row:
`(5563,4373,23221)`.

**The positive endpoint was not met.** No componentwise noncompactness theorem,
source-orbit reduction, or diagonal-three obligation is closed. The exact
ledger remains `2/9`, with 1,162,302 unresolved source records. These records
are not a count of connected components. Pair-map injectivity is a separate
obligation and was not computed in this track.

## Quantified target and chart

For every uniform normalized parent sign cell, the intended target was that
every connected component of the original nine-coordinate real locus
`q1=q2=q3=0` is noncompact. This target includes the entire parent domain and
all source singularities. A positive generic chart, one path, or one fiber is
insufficient. Transfer to actual triple-bad components and the exhaustive
source family would be additional obligations even after proving this source.

The existing parent-unit graph solves

```
d = (b(i-f)+fg)/i,
i*q2 after this substitution = A*a+B,
i*q3 after this substitution = C*a+D,
A = i(f-1)(h-1)(bf-ce),
a = -B/A,
N = A*D-C*B.
```

Thus the source on the full uniform domain is exactly the graph over `N=0`
in coordinates `(b,c,e,f,g,h,i)`. Its denominator `i*A` is a product of
parent-bracket units. The chart does not invert a three-row Jacobian minor,
so source rank-drop points are retained. All 70 parent inequalities are still
required after the substitutions; no chart divisor is silently declared an
extra admissible interior point. The new verifier reconstructs the 389-term
numerator from the pinned original equations and verifies the graph pivot
factorization; no historical producer output is needed for that reconstruction.

## Exact small obstruction to a maximum-principle shortcut

One potential full-base mechanism was to make `N` harmonic under a constant
positive-definite metric, possibly after an invertible affine change of all
seven base coordinates. This is a necessary condition for that particular
harmonic-polynomial shortcut and is testable by finite linear algebra.

For a constant symmetric real matrix `G`, the identity in question is

```
sum_j G_jj N_jj + 2 sum_(j<k) G_jk N_jk = 0
```

as a polynomial identity on all seven-dimensional affine space. The screen
exhausts **all 28 constant symmetric coefficients**, not just diagonal
weights or integer coefficients. The union of monomial supports of these
28 second derivatives has 1,191 elements. Its coefficient matrix has full
column rank 28 over the rationals, hence also over the reals.

The compact exact certificate stores 28 distinct original monomials and their
28-by-28 coefficient matrix, whose determinant is

```
-7421703487488 != 0.
```

Consequently `G=0` is the only constant symmetric solution. In particular
there is no positive-definite solution. An invertible affine coordinate
change of `N` would pull an ordinary Laplacian back to an operator of this
form with a positive-definite constant matrix, so it cannot make `N`
harmonic either. Multiplication by a nonconstant function, nonlinear
coordinates, variable-coefficient operators, identities only on the source,
or an unrelated moving-base escape argument are outside the searched space.

This obstruction is auxiliary and carries zero theorem credit. It neither
constructs a compact full-source component nor proves that one exists. It is
an exact failure of one structural mechanism, not evidence against 9DVL.

## Bounded full-critical numerical diagnostic

A small floating-point diagnostic solved the complete original height-`b`
multiplier system in eleven variables `(a,...,i,lam,mu)`:

```
q1=q2=q3=0,
lam*(q1)_v + mu*(q2)_v + (q3)_v = 0 for every v other than b.
```

The coefficient of `dq3` can be normalized to one at every actual parent
critical point because the first two derivative rows in columns `(a,d)`
have the nonzero minor `-i(f-1)(h-1)(bf-ce)`. This includes intrinsic source
singularities. Outside the parent domain that normalization has no such
coverage guarantee, which is immaterial to the stated target. The diagnostic
did not include saturation inverse variables; candidate parent admissibility
was checked afterward using all 70 bracket values. Thus it also converges
readily toward discarded boundary solutions.

There were 120 deterministic starts, generator seed `9052026`, around
`(-19/28,-23/7,-27/14,-5,-4,-3,-1,2,4)`, with independent standard normal
perturbations and cyclic scales `0.15,0.7,1.8,3.0`. The Gaussian proposal
law has no finite support bound; the realized initial points and coordinate
envelope are recorded explicitly. Multipliers were initialized using the
two pivot columns. SciPy's `hybr` root method used the analytic Jacobian,
`xtol=1e-10`, and `maxfev=1000` per start.

The fixed heuristic candidate screen required equation residual below
`1e-6` and all absolute parent-bracket values above `1e-5`. No output passed.
There were 32 solver-success flags and 70 outputs below the residual
threshold; the largest minimum bracket value among those 70 was about
`5.377e-6`. These thresholds are diagnostics, not exact nonuniformity or
nonexistence tests. No floating-point point is asserted to lie on a parent
wall. The result gives **no emptiness, completeness, source-reduction, or
topological credit** and adds no missing quantifier to the older modular
diagnostics. It is retained only as a reproducible negative search log.

The discovery dependencies were temporary local SymPy 1.14.0, NumPy 2.5.2,
SciPy 1.18.1, and python-flint 0.9.0. Each symbolic/numeric process was limited
to 180 seconds and 4 GiB virtual address space. The numerical search's own
stop limits were 120 starts or 145 seconds, whichever came first. No bounds
were enlarged; no new saturation, Macaulay matrix, orbit census, or
resultant cascade was launched.

## Closing frontier

The first unresolved implication is still that the **entire** original
height-`b` critical locus is absent after restricting to all genuine parent
units, or that some different full-source argument excludes compact
components despite critical points. Numerical absence does not establish
that implication. The new exact harmonic obstruction eliminates one finite
family of alternative mechanisms; it does not supply the required identity.

The independent oval track reports a candidate whole compact fixed-base
oval inside a uniform parent cell. That candidate's certification is owned
and reviewed in that track. Even if accepted, it concerns a fiber with five
coordinates fixed and does not settle compactness of the six-dimensional
moving-base source. This track relies on no extrapolation from the historical
one-slice escape theorem.

Opening and closing proof-distance vectors are unchanged:
`(2/9,1,{triple Hc0,pair Hc1},7,UNKNOWN,UNKNOWN)`.
Classification: **INFORMATIONAL** for the exact auxiliary rank result;
**STALLED** for theorem convergence. Endpoint: **NULL**. Decision: freeze the
track, without same-route continuation or increased elimination bounds.

A discriminating successor would need a genuinely new, quantified
moving-base escape mechanism or an independently replayable parent-unit
critical identity; repeating the numerical search does not supply either.
No successor is claimed to be ready for automatic execution.

## Replay

```
python -B ops/team/d3-real-global-prover/verify_harmonic_obstruction.py
```

The standard-library verifier imports no producer, CAS, or repository
arithmetic. It reconstructs the original numerator and coefficient rows,
uses a separate fraction-free determinant algorithm, and rejects a
corrupted row, duplicate-row singular matrix, and altered source bytes.
This is an independently implemented arithmetic replay, not an independent
AI acceptance verdict. Such acceptance belongs to the referee.

Optional numerical discovery, with the dependencies available on
`PYTHONPATH`:

```
OPENBLAS_NUM_THREADS=1 timeout 180 python -B ops/team/d3-real-global-prover/explore_critical_real.py
```

The exact harmonic producer is `explore_harmonic.py`; it imports historical
chart arithmetic for discovery and is not the acceptance entrypoint.
