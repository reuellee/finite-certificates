# Stage 1: sigma-complete max-margin search for (3,5)

## Decision

No valid 44-vertex instance was found.

The largest final normalized margin was

```text
2.0816681711721685e-17
```

for sigma class 16568 and split `k=3`. This is numerical zero, not a
positive margin: it is eleven orders of magnitude below the requested
`1e-6` decision threshold. A fresh HiGHS solve reproduces the value and its
dual multipliers sum to `0.9999999999999996`. No saved candidate exceeded
`1e-6`, including the smaller positive-weight-floor sensitivity runs.

Accordingly, `instance_44.json` is deliberately absent. This is a negative
numerical result, not a proof that a (3,5)-zonoboxtope with 44 vertices does
not exist. The sigma enumeration is exhaustive; the nonconvex optimization
over directions is not.

## Incidence and exhaustive sigma enumeration

I used a deterministic chamber builder independent of the randomized sampling
inside `facet_lp.build`. It tests each of the 32 sign vectors by the
homogeneous feasibility LP

```text
diag(epsilon) U x >= 1.
```

The reference direction set is generic and has 22 chambers. The chamber
degree multiset is

```text
10 chambers of degree 3
10 chambers of degree 4
 2 chambers of degree 5
```

and every one of the 20 facet sides is incident to four chambers.

I tested 40 additional seeded random generic direction sets. All had 22
chambers and were isomorphic to the reference structure. The test was exact
colored graph isomorphism, with separate node colors for sides, chamber
degrees, and the ten degree-two nodes encoding antipodal side pairing. Thus
the test preserved more than the plain chamber-side incidence graph. This is
strong empirical confirmation of the expected unique structure, but the 40
random trials are not themselves a proof of oriented-matroid uniqueness.

The exhaustive result is:

```text
33,140 valid labeled sigmas
16,570 classes modulo global sign flip
```

Two independent methods agree exactly, including sorted assignment order:

1. a vectorized scan of all `2^20` assignments;
2. a constraint-pruned DFS with side zero fixed to remove the global flip.

The representative Hamming-weight histogram, for weights 0 through 20, is:

```text
[0,0,0,0,0,0,4,121,1341,4628,6220,3452,754,49,1,0,0,0,0,0,0]
```

The complete incidence, assignments, counts, random direction sets, and
isomorphism maps are in `sigma_enum.json`.

## Margin normalization

The margin as stated in the task is still homogeneous in
`x=(T,alpha,beta)`: normalizing each constraint row does not stop the common
scaling `x -> c x`. Without a parameter gauge, every strictly feasible sigma
has unbounded maximum margin.

I therefore used

```text
sum(alpha) + sum(beta) = 1
```

with all five weights bounded below by `1e-5`. Each constraint row was divided
by its current Euclidean norm. Fixed-`U` LPs bounded each coordinate of `T` by
50 only to make the numerical problem explicitly bounded; the largest
absolute `T` coordinate in the reference screening optima was below 0.463, so
this bound was inactive by a factor over 100. The joint smooth optimization
did not bound `T`.

Because the best result touched a weight lower bound, I re-solved 3,120 saved
direction/sign candidates at weight floors `1e-7` and `1e-9`. All 6,240 LPs
succeeded; the best margin remained `2.0816681711721685e-17`, with zero
results above `1e-6`. This is a sensitivity check at saved directions, not a
new global direction optimization at the smaller floors.

## Numerical coverage

Seeds are consecutive and recorded in the JSON logs:

```text
incidence/enumeration  20260730
all-class joint search 19440566
deep smooth restarts   19440567
outer true-LP search   19440568
broad LP screens       19440569
```

The completed work was:

- 33,140 globally solved reference-`U` max-margin LPs: all 16,570 sigma
  classes for both `k=2` and `k=3`. There were no LP failures and no positive
  result.
- One joint local direction/parameter run for every class and split, 320 Adam
  steps each, followed by 33,140 true fixed-`U` LP polishes.
- Two additional broad canonical random direction sets, exhaustively screened
  by LP for every class and both splits: 66,280 more LPs, no failures and no
  positive result.
- Two top-20 campaigns, one before and one after the broad screens changed the
  numerical zero tie. Each campaign used 12 smooth joint restarts per class
  and split at 1,400 steps. Total: 960 deep smooth restarts; every final LP
  polish succeeded.
- Two top-20 true-inner-LP campaigns. Each used the reference start, the
  polished start, and ten canonical random starts per class and split. COBYLA
  optimized ten spherical direction coordinates while every objective
  evaluation globally solved the inner max-margin LP. Total: 960 outer
  restarts and 100,950 inner LP evaluations. All 960 COBYLA runs terminated
  successfully and there were no inner LP failures.

The all-class joint checkpoint initially retained one invalid perturbed
initializer in each split: those two starts had crossed a triple-determinant
wall before recording any barrier-eligible iterate. The first apparent
positive result (`0.00399`) came from one of these invalid checkpoints.
Independent reconstruction caught it immediately: its sigma was not NAE for
the changed incidence, only 16 chambers were bicolored by the cone test, and
the hull had 38 rather than 44 vertices. It was rejected and no instance file
was kept. The polish was rerun with an explicit reference-chirotope check, and
the rerunnable code now resets any such initializer before optimization. The
corrected polish rejected exactly one checkpoint per split and found no
positive result.

The final `margins.json` has all 16,570 classes and both split results per
class. Five raw combined margins are slightly greater than zero, but the
largest is only `2.08e-17`; these are solver-scale roundoff. There are zero
classes above `1e-6`.

## Where the obstruction binds

At the best numerical solution:

```text
T = (0,0,0) to solver precision
one alpha weight is at the positivity floor
active sides = [2,3,4,5,10,11,12,13,16,17]
```

These are both antipodal sides of the five facet classes

```text
(0,2), (0,3), (1,3), (1,4), (2,4).
```

As a graph on the five generators, those pairs form the 5-cycle

```text
0 - 2 - 4 - 1 - 3 - 0.
```

Every one of the 22 chambers is incident to at least one of these ten active
sides. The best LP dual has nonzero side multipliers on sides 2, 4, 10, and
17, with multipliers approximately

```text
0.4706938325, 0.4842697641, 0.0304597583, 0.0145766451.
```

Their sum is one. This is useful near-optimal dual information, not a
direction-independent impossibility certificate.

The same 5-cycle pattern dominates the independent deep restarts. Among deep
runs whose polished margin was greater than `-1e-8`:

```text
k=2: 224 / 226 runs had exactly this active-side pattern
k=3: 238 / 252 runs had exactly this active-side pattern
```

Literal “always active” labels are weakened by symmetry and by numerical
ties. Across the top 100 final classes, no single side was active in every
`k=2` solution; sides 5 and 16 were active in every `k=3` solution. The
cycle-level pattern is substantially more stable than any one side label.
Full side/chamber frequencies and the dual record are in
`obstruction_analysis.json`.

## Honest limitations

- Sigma enumeration and the LP optimum at any fixed `U` are complete (within
  floating LP tolerances and the explicit gauge/bounds). Optimization over
  the continuous direction space is nonconvex and is not globally complete.
- The all-class joint stage has one local direction start per class and split.
  Broad random starts and much deeper treatment were concentrated on the
  leaders. A class that is poor near the sampled directions could conceivably
  become positive in a distant region.
- Searches were constrained to the reference chirotope cell. Random
  configurations were mapped into it by signed permutation; the incidence
  tests support the expected uniqueness. This implementation does not provide
  a formal proof that this covers every relevant labeled/A-B realization.
- All geometry and optimization here use floating point. No exact
  nonexistence certificate was produced.
- The `1e-5` weight floor is a numerical stand-in for strict positivity.
  Smaller-floor re-solves were negative, but did not globally re-optimize
  directions.
- There were no LP, deep-polish, or COBYLA failures. The only invalid states
  were the two crossed-wall all-class initializers described above; both were
  detected, rejected, logged, and fixed in the code.

## Files and reproduction

Principal deliverables:

- `sigma_enum.json`: exhaustive enumeration and incidence verification.
- `margins.json`: complete per-class final margin table and the best LP/dual.
- `obstruction_analysis.json`: blocker frequencies, 5-cycle analysis, and
  dual support.
- `validation_report.json`: fresh enumeration and artifact consistency checks.
- `floor_sensitivity.json`: smaller positivity-floor results.
- `incidence_enum.py`, `margin_search.py`, `broad_lp_screen.py`,
  `outer_lp_search.py`, `floor_sensitivity.py`, `analyze_results.py`,
  `verify_candidate.py`, and `validate_artifacts.py`: seeded rerunnable code.
- JSON logs and NPZ checkpoints preserve all seeds, traces, directions, and
  pre-/post-broad leader campaigns.

Using the requested interpreter from the repository root:

```powershell
$PY = 'E:/Projects/sae-identifiability/.venv/Scripts/python.exe'
& $PY ai/maxout/stage1_gpt/incidence_enum.py --out ai/maxout/stage1_gpt/sigma_enum.json --incidence-trials 40
& $PY ai/maxout/stage1_gpt/margin_search.py --phase fixed
& $PY ai/maxout/stage1_gpt/margin_search.py --phase joint --joint-steps 320 --batch-size 512
& $PY ai/maxout/stage1_gpt/margin_search.py --phase polish
& $PY ai/maxout/stage1_gpt/broad_lp_screen.py --trials 2
& $PY ai/maxout/stage1_gpt/margin_search.py --phase deep --top-n 20 --deep-restarts 12 --deep-steps 1400
& $PY ai/maxout/stage1_gpt/outer_lp_search.py --top-n 20 --random-restarts 10 --maxiter 600
& $PY ai/maxout/stage1_gpt/floor_sensitivity.py
& $PY ai/maxout/stage1_gpt/margin_search.py --phase assemble
& $PY ai/maxout/stage1_gpt/analyze_results.py
& $PY ai/maxout/stage1_gpt/validate_artifacts.py
& $PY ai/maxout/stage1_gpt/verify_candidate.py
```

The last command writes `instance_44.json` only if the assembled best margin
exceeds `1e-6` and the deterministic incidence, cone-LP chamber count, and
unjoggled/deduplicated float hull count all verify 44.
