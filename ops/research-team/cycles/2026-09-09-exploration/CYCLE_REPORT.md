# 9DVL exploration: an actual boundary and a certified escape

**The theorem ledger remains 2/9.** The exploratory round produced two exact
geometric results: a full feasibility transition at the previously known
support event, and an escaping actual triple-bad component whose horizontal
slice is compact. Independent review accepted all four results within their stated scopes.

Canonical base: `21a97db6aa66912fd37556d81711c0588c454a7d`, tree
`4b7b850cd3e0e1ebb2aa0bf4e7c5c3f25a360bf7`. Opening revision:
`c27a36d6e3f47a2b4c7bb017774cbe5df30abdc2`.

## What the experiments found

| Experiment | Accepted outcome | Scope |
|---|---|---|
| Full feasibility across the support event | Exact primal/dual interval certificates distinguish triple badness from the exclusive pair; the full boundary witness fiber is a singleton | One parameter interval and an explicit open parent-matrix neighborhood |
| Actual topology and counterexample search | A complete compact triple-bad horizontal interval has a certified transverse escape to genuine parent boundary | One specified ambient component for the admitted row-2599 triple |
| Flexible witness choices | A coherent triangle exists, but its loop cannot fill within the pair-face layer | Exact source instance of an inherited fiberwise mechanism; no new global construction |
| Alternative-diagonal test | Only two of 512 endpoint-coordinate hybrids and two of eight endpoint-column hybrids preserve the parent signs | Refutes that fixed-frame endpoint-replacement shortcut; an inherited longer path still connects the endpoints |

### The support event changes actual feasibility

Keep the original proper incomparable signatures
`14988895318912`, `3405195891438080`, and `40418075143643136`.
At the old row-2599 event parameter

\[
t_* = \frac{37864449186859942661765893}{7029591949415530407677535},
\]

the exact certificate treats **all 56 inequalities** in each block. Throughout
`[t*−10⁻⁶,t*]` all three blocks are bad. Throughout `(t*,t*+10⁻⁶]`, block 0
is strictly feasible while blocks 1 and 2 remain bad. All 70 parent signs
remain strict. Numerical discovery had also returned an apparent dual on the
good side within solver tolerance; exact reconstruction rejects it.

An explicit adjugate primal vector gives a local defining polynomial Delta.
In a specified open neighborhood of the event in parent-matrix coordinates,

\[
B_0=\{\Delta\leq0\},\qquad B_1=B_2=U,\qquad
E_{12}=\{\Delta>0\}.
\]

The boundary is smooth. Its full normalized block-0 witness fiber consists
of one point: a supporting primal forces every dual onto four rank-three
active rows. This is actual local geometry, rather than merely a change of
selected circuit. No normalized-gauge comparison or global frontier map is
claimed by this germ.

### A compact-looking slice has an exact escape

A different experiment moves the first two coordinates of parent label 8,
with parameters `(u,v)`. The first five projective-frame labels stay fixed.
Along the complete strict parent chord `v=0`, the actual triple-bad locus is
exactly a compact interval `[alpha,beta]`, with
`alpha ≈ −11.89452588236` and `beta ≈ 0.283132286962`. Exact full-block
primal certificates exclude triple badness on both complementary intervals;
dual certificates retain the zero-weight endpoints.

Every point of this interval connects within triple badness to `(0,0)`.
From there the exact vertical path

\[
u=0,\qquad 0\leq v<\frac{2037283091}{10548542}
\]

stays triple-bad and approaches the parent wall `[3578]=0`. The balanced
bracket ratio

\[
\frac{[3578][1234]}{[1238][3457]}
\]

is invariant under projective transformations and individual column
rescalings. It tends to zero while its denominator remains nonzero. Hence
the path leaves every compact subset of the normalized uniform parent
space. **The ambient component containing the horizontal interval is
noncompact.** Other components of this triple and other parents are not
covered.

The initial 3,313-point two-dimensional sample was only discovery evidence.
Its apparent regions supply no proof of connectivity or coverage between
sampled points. Acceptance rests on the exact two-chord certificates.

## Strategy decision

The broad discovery round answered questions that the previous
attachment-design gate left open. Its two useful geometric results do not
remove the central global burden. Simply accumulating additional examples
of escapes or collars would leave that burden unchanged.

Selected lead: **a small parameterized escape construction that preserves
the labeled bad-set diagram across actual feasibility boundaries**. The next
discriminator is whether the newly explicit boundary and escape mechanisms
can be made compatible as the parent varies. A positive finite instance
would still need an exhaustive global comparison before theorem credit.
This is a bounded future construction target, not an asserted construction
or an automatically running successor cycle.

The coherent-choice route stops at its inherited filtration cost. Retire the
fixed-frame endpoint-only hybrid shortcut for D9. The alternative-diagonal
audit also checked that the historical D8 mask-6 obstruction had already
been filled and retired; it was not repeated. No evidence from this round
justifies replacing D3 with D9 as the main theorem target.

## Verification and scope

The coordinator recovered and checked all three archive volumes, the
137,518,347-byte complete archive, every recovery-manifest file hash, and the
exact base/tree. The predecessor's independent referee replay passed.
Four discovery workers used isolated branches and assigned file surfaces.
A fifth worker independently audited opening sources and candidate claims.
The coordinator alone owns integration and this report.

The final independent verdict is `ACCEPT_SCOPED_AUXILIARY_RESULTS_ONLY`, at
raw referee revision `cb4f11e3ef4819014e13928416e442e3801865a8`.
The referee reconstructed the event using centered Taylor bounds, the chord
certificates using rational Sturm sequences, and the D9 hybrids with a
separate normalization and determinant implementation. It also checked
original-label admission and hostile sign, interval, normalization, and
boundary controls without importing producer acceptance logic.

| Gate | Result |
|---|---|
| Recovery inputs, base/tree and inherited state | PASS |
| Independent source, arithmetic and written scope review | PASS for all four scoped outcomes |
| Integrated candidate bytes vs frozen revisions | PASS, 28 files |
| Hostile controls | PASS |
| Original global obligation closure | 0; no theorem promotion |
| Final-head clean restoration | Recorded in external `CLEAN_RESTORE_REPLAY.json` |

Written mathematical arguments received independent agent review, not
proof-assistant formalization. The complete independent replay is
`python -B ops/team/d3-explore-referee/verify_candidates.py`; it needs Python
and NumPy for NPZ decoding only. Exact arithmetic uses rational numbers. All raw worker
revisions are preserved in `FROZEN_CANDIDATES.json` and the full recovery
bundle. No historical source, theorem definition, or protected verifier was
modified.

## Mandatory solution-convergence verdict

Opening proof-distance vector:
`(2/9,1,{diag3_pair_hc1,diag3_triple_hc0},7,UNKNOWN,UNKNOWN,13,16)`.

Closing proof-distance vector:
`(2/9,1,{diag3_pair_hc1,diag3_triple_hc0},7,UNKNOWN,UNKNOWN,14,17)`.

Mid-cycle convergence check: no global obligation had closed. The user had
explicitly authorized small discovery tests without an upfront global
proof architecture, so each independent test completed its bounded initial
experiment and at most one exact follow-through. Budgets were not enlarged
to avoid a stalled theorem verdict. Subsequent work is frozen-candidate
review and recovery, not more discovery.

Trajectory classification: **STALLED for the theorem endpoint;
INFORMATIONAL for the auxiliary geometry**. The theorem-credit minimum was
not met. Original obligations closed: 0. Ledger delta: 0/9. All seven global
obligations remain open. Triple source accounting stays 77,940,147 settled /
79,102,449 total / 1,162,302 unresolved; these are not component counts.
Pair coverage and the exhaustive global component residual remain UNKNOWN.

Automatic strategy-reset result: PIVOT completed through distinct
experiments; STOP the finished tests and retain the stated new construction
lead. Same-route continuation justified as theorem convergence: **NO**.
The new finite knowledge does not alter the global proof-distance measure.

## Recovery and authority

GitHub remained read-only. No human was contacted and no paid compute or API
was used. All existing recovery refs and raw worker branches are retained.
The external recovery manifest identifies the final revision/tree, bundle
digest, independently reviewed candidates, and clean-restoration replay.
The complete recovery package preserves all raw worker histories and source
data and needs no earlier checkpoint. It accompanies this report with a
recovery mirror under the authorized Projects/research-backups area.
