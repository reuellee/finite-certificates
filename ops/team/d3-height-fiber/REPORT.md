# D3 remains open after a full-source critical-system test

**The requested 3/9 milestone was not achieved. The verified ledger remains
2/9.** This investigation identified the actual two-part completion condition,
checked the preceding route failures against older positive results, derived
a smaller exact full-source critical system, and executed bounded compiled
algebra calculations. None closed a D3 invariant or one residual source orbit.

Base: `8cab91141240236a203f812f490901b3a67573d2`, tree
`1fd457ed04e1a9b8565705febde4fb9f99fae61a`.
Working branch: `research/d3-height-fiber-20260905`.
The user's instruction authorized new local research. No human expert was
consulted and no research was pushed to GitHub.

## What would actually establish 3/9

For every realizable uniform rank-four parent on eight labels, every parent
realization component, and every proper pairwise-incomparable signature
triple, write `Aij = Bi intersect Bj` and `T = B0 intersect B1 intersect B2`.
The existing lower vanishings reduce D3 to BOTH

1. `Hc^0(T;Q)=0`: every triple-bad component is noncompact in the true parent
   space; and
2. injectivity of `(x01,x02,x12) -> r01(x01)-r02(x02)+r12(x12)` from the direct
   sum of the three pair `Hc^1` groups into `Hc^1(T;Q)`.

See the [prospectus](../../../ai/omreal/9DVL_THEOREM_PROSPECTUS.md) and
[balanced end map](../../../ai/omreal/DIAG3_PAIR_DIFFERENTIAL_ENDS.md).
Proving each individual restriction injective does not eliminate cancellation
between their images. Proving component escape does not compute those images.
The finite source-existence result from the preceding task supplies neither
vanishing by itself.

The fixed-plane counterexample in the preceding task is the same parent-2599
chart-zero configuration that already has an exact proper moving-plane path
in [the common-escape certificate](../../../ai/omreal/DIAG3_ROW2599_COMMON_PROPER_ESCAPE.md).
Its fixed-plane rigidity is therefore not evidence of a compact component.
No further escape sampling at that point was performed here.

Direct double/triple contraction also has known generic obstructions in the
repository. The outside literature check did not supply a replacement:
[Basu and Perrucci, arXiv:2204.01595v1](https://arxiv.org/html/2204.01595v1)
studies multi-affine topology, but does not imply this two-part D3 vanishing
for the parent-specific determinant family. No new theorem is imported from
that paper.

## Exact full-source reduction

The source is the complete nine-variable factor variety with presentation
`(5563,16134,19284)`, canonical row `(5563,4373,23221)`. Its pinned input is
`ai/omreal/data/DIAG3_triple_fullspace_critical_h1.json`, SHA-256
`c9244a47ded5736e7afe724a9914e75631a22b78653442e88c14f5c397919eb8`.
Let its three polynomials be `q1,q2,q3`, coordinates `(a,b,c,d,e,f,g,h,i)`, and
`J` their three-by-nine Jacobian. Retain `b` as the proposed height.

Direct differentiation gives

```text
q1 = bf-bi+di-fg,
(q1)_a = 0,                       (q1)_d = i,
(q2)_a = (f-1)(h-1)(bf-ce).
```

Thus the first two rows have the fixed minor

```text
Delta = det J[rows 1,2; columns a,d]
      = -i(f-1)(h-1)(bf-ce).
```

Each factor is a genuine parent bracket up to sign:
`i=[1238]`, `f-1=[2357]`, `h-1=-[2458]`, `bf-ce=[1267]`.
Consequently Delta is nonzero throughout EVERY uniform parent cell.

For `v` in `{c,e,f,g,h,i}`, put `Mv = det J[a,d,v]`. The full 56-minor
height-critical condition is equivalent on every parent cell to the six
equations `Mv=0`, together with `q1=q2=q3=0`.
Their total term count is **1,080**, compared with **14,681** in the original
52 nonzero minors. Four original minors are identically zero.

Here is a polynomial certificate of the equivalence. For every ordered
three-column subset `I` avoiding b, expansion after eliminating the first
two entries of row three gives

```text
Delta det(J_I)
 = sum over j in I of (-1)^(position(j)-1)
   Mj det(J[first two rows; I minus j]),
Ma = Md = 0.
```

The reverse implication is immediate because the selected minors are among
the original ones, up to orientation. Division is only by Delta. In
particular the reduction retains singular source points: it does not divide
by a full-rank three-by-three minor or discard an interior rank-drop stratum.

The separate, standard-library integer-polynomial implementation
[verify_height_chart.py](verify_height_chart.py) reconstructs all 56 input
minors and verifies all 56 displayed polynomial identities. It also checks
the parent-bracket identifications and a rank-drop countermodel showing why
the nonzero-pivot hypothesis cannot be removed. It imports neither the
SymPy producer nor the repository's determinant code.

This is separate arithmetic reconstruction by the coordinator, **not an
independent AI referee verdict or a formally checked topological proof**.

## Two equivalent presentations tested

Keeping b and solving the first equation gives

```text
d = (b(i-f)+fg)/i.
```

The second equation remains affine in a with the same parent-unit slope.
Solving it gives a graph onto a seven-variable hypersurface. The final
numerator has 389 terms and degree vector `(3,2,2,3,2,2,3)` in
`(b,c,e,f,g,h,i)`. Its denominator is
`i^2(f-1)(h-1)(bf-ce)` up to the documented numerator orientation. This is a
global rational change on the actual source, not a fixed base slice. It did
not reveal an affine proper fiber. A quadratic-discriminant factorization
attempt was stopped after about four minutes; no discriminant conclusion is
claimed. The surviving formula is in [discovery.json](discovery.json).

There is also an exact low-degree multiplier presentation. Introduce
`lam,mu,z`, retain the three q equations, and impose

```text
lam (q1)_v + mu (q2)_v + (q3)_v = 0   for every v other than b,
1-z i(f-1)(h-1)(bf-ce) = 0.
```

This is twelve equations in twelve variables. The two pivot columns determine
lam and mu uniquely. The checker proves all eight cleared multiplier
identities, so this system is a graph over the same localized critical locus,
including singular points. Its complete input is under two kilobytes.

If the full critical locus were empty after localization by genuine parent
brackets, every compact component would be excluded: a maximum of b on a
compact component is either a smooth constrained critical point or a
singular point, and both satisfy the retained system. **Emptiness is the
missing step.** No solver result below establishes it.

## Executed algebra and resource limits

Used the official Linux x86 binary of
[msolve 0.10.1](https://msolve.proj.lip6.fr/binaries/index.html), obtained from
the project's `msolve.lip6.fr` download mirror. Binary SHA-256:
`a4c2beb9a7d186394af6bb21e235f76e3bfb3d0e6fdf872c27b517b8a6e87e13`.
Archive SHA-256:
`b2ee3fdd3b84129b48c31a900bcd2a6e47bd39577fa12843798747743f074cfb`.
It runs locally in the existing `lee-dev` WSL distribution; no system package
installation or paid compute was needed.

The [official tutorial](https://msolve.proj.lip6.fr/downloads/msolve-tutorial.pdf)
documents deterministic prime-field linear algebra and a prime-field-only
F4 saturation interface. These runs used prime `1073741827`, exact linear
algebra option `-l 2`, and two threads. They are modular discovery, not rational
certificates. An initial `65521` attempt was rejected by the interface before
computation because the characteristic was too small for its saturation mode.

| Input | Elapsed seconds | Outcome |
| --- | ---: | --- |
| Six-minor system, saturation by the pivot product | 164.411 | Exit 9, no completed basis |
| Same system, adding genuine parent brackets [1468] and [5678] to the saturator | 3.162 | Exit 11; transcript reports a core-dumping crash; no completed basis |
| Twelve-equation multiplier system with explicit inverse | 162.707 | Exit 9, no completed basis |

Each run enforced 300 CPU seconds, 300 wall seconds, 8 GiB virtual address
space, and a per-output-file limit. Exit 9 is recorded without pretending
the wrapper measured its precise cause; the CPU ceiling was in force and the
transcripts end during matrix reduction. A failure, signal, empty output
file, or modular miss is not evidence for either emptiness or nonemptiness.
The run records and inputs are frozen in [evidence](evidence). The readable
copies use LF line endings and omit trailing whitespace; exact original run
bytes are preserved in [RAW_SOLVER_EVIDENCE.zip](RAW_SOLVER_EVIDENCE.zip).

Exact parent-factor stripping was also tested on the selected generators;
it removes three coordinate factors and one linear factor, but yields no
unit equation. It was not followed by a larger search. A rational-input
export exists for reproducibility but **was not run** after the modular
feasibility failures. No characteristic-zero claim rests on these attempts.

## Closing decision and verification

Opening and closing mathematical proof-distance coordinates are unchanged:
`(2/9,1,{pair Hc1,triple Hc0},7,UNKNOWN,UNKNOWN)`.
The complete triple source residual remains **1,162,302**. The accepted
previous-cycle counters remain historical; this coordinator investigation
does not claim a separately reviewed cycle close.

Trajectory: **INFORMATIONAL** for the exact system reduction, with a **NULL**
endpoint for the attempted noncompactness proof. No load-bearing obligation
closed. No source orbit, pair incidence, or global component coverage is added.
The minimum theorem-level decrease in [OPENING.md](OPENING.md) was not met.
The checkpoint is at the first completed solver failures. The same route is
stopped without increasing its limits or launching an orbit census.

The next proof-bearing input must still be a full-domain noncompactness
argument and the independent pair injectivity argument, or a direct proof
of `H_6(F_S;Q)=0` carrying both. The reduced equations provide a smaller exact
entry point; they are not evidence that repeating a larger solve will work.

Validation: the integer replay proves 56 source-minor reconstructions, 56
pivot identities, eight multiplier identities, and the actual parent-unit
identifications. Canonical V11 and the existing research-cycle protocol
checks pass. Canonical ledger bytes were left unchanged. Exact runtime,
input, and output hashes are recorded in the frozen manifest. The current
branch is locally committed; its recovery bundle is recorded separately.
