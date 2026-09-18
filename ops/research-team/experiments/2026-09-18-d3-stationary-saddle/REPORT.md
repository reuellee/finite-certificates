# 9DVL: fully admissible stationary saddle and the required pivot

18 September 2026. **Original ledger: 2/9. Whole survivor OPEN. No source orbit closed.**

## Main result

The proposed fully parent-localized stationary-emptiness target is false.
This cycle certifies an isolated real solution of the genuine B-stationary
system for source (5563,4373,23221), with all 70 original brackets nonzero.
It is not another point on a forbidden boundary.

The same exact certificate proves that this point is a saddle of B on the
local triple intersection. It is not a maximum and is not a compact-component
counterexample to 9DVL. The relevant consequence is that no parent-unit-product
identity excluding every stationary point can exist for this source.

## Execution and decision

The predecessor Drive archive was downloaded and matched its recorded 9,470,555
bytes and SHA-256 2ba051521941e61573b50ae24cc120d50e2003604858178c6a161d19c69a02c5.
Its ZIP integrity, all 50 payload hashes, exact source verifier and separate
Fraction witness checker passed. GitHub still pointed to
f7c73f00c2990f20baffa93977c146b55909ebd3 on
research/d3-critical-geometry-20260910 when this cycle started.

The planned structured algebra produced an exactly checked parent-unit
provenance identity for W(Q), a separated-quadratic coordinate representation,
and source-wide curvature identities. Alongside it, a deterministic 192-start
numerical discovery screen found a candidate separated from every parent
boundary. Numerical failure or success was not treated as proof.

The candidate was refined and then certified with rational interval arithmetic.
The decisive validation was a contraction mapping of a rational nine-dimensional
box into its interior, with contraction bound below 4.429e-7 and radius 1e-12.
Every one of the 70 bracket intervals excludes zero. The smallest absolute
bracket lower bound exceeds 0.00510054. This proves an actual real algebraic
stationary point, not an approximately vanishing polynomial system.

After acceptance, the stationary-emptiness search was stopped. No longer
Groebner run or larger-machine request is justified for that false target.
A native msolve download was attempted once but failed on DNS resolution;
no msolve computation or performance result is claimed.

## What is now proved

At the certified point, approximately B=-0.12946643015334363121, two explicit
tangent directions have constrained B curvatures in the intervals

    (0.0557412698, 0.0557412701)
    (-0.0096646542, -0.0096646531).

Thus B increases and decreases along local curves: the point is a genuine
saddle, not a local extremum. All coordinates, rational interval data and
verification code are retained in the archive.

More generally, at every genuine stationary point let

    H = j Hess(Q)-Hess(R),
    V = AD partial_D+(At+u) partial_t,
    W = C partial_C+(w-u) partial_w.

The following source-wide identities hold on the stationary locus:

    V^T H V = h = -2 B C u^2(A+1)(A+u),
    W^T H W = g = 2j(A+1)(u-v)[(B+u-v)(At+u)+Du(B+1)],
    V^T H W = 0.

Every factor in h is an authenticated parent unit, so h never vanishes.
The certificate includes explicit polynomial combinations of the original
generators proving all three identities. This gives an inexpensive, exact
exclusion of all stationary points with h*g<0 from the maximum target.

## Corrected next target

The proper next objective is to rule out possible maxima or prove component
escape, not to rule out every stationary point. Put nu=j Q_B-R_B. The written
proof derives the necessary conditions

    stationary equations + all original parent conditions,
    nu*h >= 0,
    K positive semidefinite,

where K is a polynomial five-by-five Schur matrix explicitly defined from the
fixed-B tangent Hessian. The inexpensive first filter is h*g>=0. The argument
retains nu=0 and g=0, and explains the singular case instead of assuming generic
smoothness. B=D and C=D are not removed.

No emptiness, exhaustive stationary census, full maximum classification,
or complete source-component escape proof is claimed. The new maximum target
can itself be nonempty without refuting 9DVL. It remains a sufficient route,
not a mandatory proof format. The older height-semidefinite target S is a
different set and remains OPEN.

## Verification and limitations

Exact replays authenticate the parent matrix, wall equations, brackets, parent
units, interval box, saddle signs, separated quadratics and curvature identities.
Separate Python Fraction determinant arithmetic agrees at the rational center
for both walls and all 16 first derivatives. Three corrupted certificates,
a wrong curvature sign, and interval-arithmetic edge cases are rejected.

A clean-directory and extracted-archive replay are required before publication.
Those replays are implementation checks, not independent mathematical peer
review. Their results and the publication receipt are stored separately.
The inherited residue remains 1,162,302 source records; it is not a component
count. Both original D3 obligations, including injectivity, remain open.
Original ledger stays 2/9 and the new source-orbit credit is zero.

## Recovery and publication

The recovery snapshot contains the unchanged predecessor archive, new proofs,
exact witness data, source reconstruction, checkers and discovery logs. It is
not a full Git-history bundle. New files are intended for the existing research
branch and Projects/research-backups only. Main, PRs, history and sharing settings
are not changed. The separate publication receipt, not this report alone,
records which remote writes and readbacks actually succeeded.
