# D4-SP falsifier: minimal signed obstruction and actual candidate

Date: 2026-08-29 UTC

Track: `diag4-top-sheaf-falsifier`

Canonical mathematical base:
`d047359e7892106021022b0401554f56eb4e4d8a`

## Outcome

The D4-SP claim remains **inconclusive**.  No exact admissible tuple with a
checked nonzero class in `H_c^3(C_(rho,Q);Q)` was found.  The bounded track
did produce a complete minimal abstract classification and one exact actual-OM
candidate family for the next topology calculation.

The fixed target is the referee-locked D4-SP proposition: for every realizable
uniform rank-four parent on `[8]`, every admissible proper pairwise-
incomparable four-family `S`, every `rho in S`, and every cover-all support
`Q` of one through five triples, the entire closed circuit piece—including
zero-weight faces and structural/residual-wall specializations—has vanishing
`H_c^3`.

This is only the unresolved cover-all part of the single-piece `(p,q)=(0,3)`
column.  It is not diagonal four.

## 1. Complete minimal abstract classification

The exact abstract search class was:

- a connected one-dimensional component diagram;
- no births or deaths;
- at most two generic component-changing events;
- at most two simultaneous component branches; and
- connected fibers outside the event interval.

With zero or one event the component graph is a tree.  With two events, the
only word that starts and ends with one component and can carry a cycle is

```text
1 -> 2 -> 1.
```

Write the signed attachments of the two middle branches at the left and
right events as `(l0,r0,l1,r1) in {+1,-1}^4`.  The exact boundary matrix is

\[
  D=\begin{pmatrix}l_0&l_1\\r_0&r_1\end{pmatrix}.
\]

Exhausting all sixteen matrices gives eight with a one-dimensional kernel
and eight with zero kernel.  Changes of event and branch generators reduce
them to exactly two gauge classes.  The sole invariant is the orientation
holonomy

\[
 h=l_0r_1l_1r_0\in\{+1,-1\};
\]

`ker(D)` is nonzero exactly when `h=+1`.  Flipping any one attachment sign
changes the holonomy and kills the class.

This exactly excludes every zero- or one-event obstruction in the declared
abstract class and reduces the minimal two-event class to one signed bit.  It
does **not** refute D4-SP: neither gauge class was derived from a rank-four
third-compound realization.

## 2. Actual retained-domain positive control

The pinned row-2599 certificate supplies one exact admissible control.  Use
signature indices `0,4,5,6` from
`seeat_parent2599_shatter8.npz`.  Replaying all sixteen selected good/bad
patterns on one parent chirotope proves the four regions are proper and
pairwise incomparable.  At pattern zero, every selected signature has a
strictly positive support-minimal five-circuit whose support covers all eight
labels.

The four exact signature values are:

| index | signature |
| ---: | ---: |
| `0` | `454112161268235` |
| `4` | `71943275699830784` |
| `5` | `3545933521575936` |
| `6` | `13949244655240191` |

This positive control prevents the abstract canary gate from rejecting all
actual retained data.  It supplies no split--remerge event and no cohomology
class.

## 3. Exact support-preserving D4-SP candidate

For `rho` equal to signature index `0`, the pattern-zero circuit support is

```text
Q = 123/134/267/258/468.
```

It is cover-all, positive, and support-minimal.  On the exact pattern-zero
parent chart make the four-parameter motion

\[
 y_5\mapsto y_5+s y_2+t y_8,\qquad
 y_1\mapsto y_1+u y_3,\qquad
 y_7\mapsto y_7+v y_2.
\]

Every one of the five derived support normals is literally unchanged, so the
stored positive Gordan circuit persists throughout the parent-safe parameter
domain.  The domain is cut out exactly by the original signs of all seventy
parent brackets.  Reconstructing their integer polynomials gives:

- `48` nonconstant signed bracket inequalities;
- `16` inequalities with degree at least two; and
- canonical polynomial fingerprint
  `144b1c69ede7f4d7a78caae7f00bf66f162bd54d08f1cd17e44f1ba8c70b86cb`.

This is actual signed rank-four data, not an abstract sheaf model.  But it is
only a support-preserving subset of the closed piece.  Its compact-support
topology is not computed, and even a class on this subset would have to be
shown to survive in the full `C_(rho,Q)` before it could refute D4-SP.

## Complete searched domain and nonconsequences

The abstract enumeration is complete only for the stated two-event,
two-component, no-birth/death class.  It excludes higher event counts,
three-or-more simultaneous components, births/deaths, higher-dimensional
base incidence, and actual third-compound constraints.

The actual calculation covers exactly:

- parent row `2599` at the pinned shatter-certificate charts;
- the four signatures with indices `0,4,5,6`;
- all sixteen selected feasibility patterns for admissibility;
- `rho` at index `0` and the one support
  `123/134/267/258/468`; and
- the displayed four-parameter support-preserving motion and all seventy
  signed parent bracket polynomials.

It does not calculate topology for any whole closed circuit piece, any other
support, parent, signature family, zero-weight specialization, or
structural/residual-wall stratum.  In particular, it does not topologically
search the complete cover-all universe of `1,715,980` supports
(`840/72,380/1,642,760` in sizes `3/4/5`).  The `66` generic cover-all
five-support orbits are not used as a complete obstruction class.

## Failed hypotheses and next discriminator

The exhaustive signed canary confirms that branchwise escape and an unsigned
component graph are insufficient.  Pointwise realizability of a proper
incomparable cover-all tuple is also insufficient: the missing evidence is a
compactly supported class on the entire closed piece.

The next exact discriminator is the displayed row-2599 candidate.  Construct
a compatible semialgebraic compactification and relative cellular cochains
for its four-parameter parent-safe domain, including every boundary sign
stratum, and compute its signed top-component differential.  If a nonzero
class survives there, the subsequent mandatory gate is to prove that it
survives under inclusion into the full closed `C_(rho,Q)`, including weight
faces and all remaining parent directions.  If the exact calculation instead
shows that the candidate domain is acyclic, record the complete event/sheaf
classification before moving to another support.

## Replay

From the repository root:

```console
PYTHONDONTWRITEBYTECODE=1 python \
  ops/team/diag4-top-sheaf-falsifier/verify_diag4_top_sheaf_falsifier.py
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/verify_fourth_single_piece_light_count.py
```

The first replay includes the required `abstract_false_positive`,
`realizable_positive`, `sign_mutation`, and `boundary` canaries.  The second
pins the complete support counts but makes no topological claim.
