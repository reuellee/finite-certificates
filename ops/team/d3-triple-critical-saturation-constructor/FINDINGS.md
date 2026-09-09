# D3 triple critical saturation: constructor findings

## Outcome

The constructor produced a deterministic **Q0 candidate handoff** for the
height-`b` critical system of presentation `(5563,16134,19284)`, mapped to
canonical row `(5563,4373,23221)`.  It did not accept Q0 and did not run Q1.
The theorem ledger remains `2/9` and the triple-source residual remains
`1,162,302`.

The exact contract is `SATURATION_CONTRACT.json`.  It is rebuilt by
`build_saturation_contract.py`, checked on the constructor surface by
`verify_saturation_contract.py`, and has a guarded conditional executor in
`run_q1_saturation.py`.

## Exact source and wall census

The source ideal is the pinned 59-record critical artifact:

- 3 residual-factor equations;
- 56 formal height-`b` minors, of which 52 are nonzero and 4 are explicit
  zero records;
- 55 nonzero generators, 14,741 sparse terms, and maximum degree 8.

The normalized parent has 70 bracket coordinates, but eight are nonzero
constant units.  They define no wall and must not receive inverse variables.
The ordered saturation ledger therefore contains exactly 62 distinct
nonconstant parent brackets.  Their degree census is 36 linear, 24 quadratic,
and 2 cubic; they contain 201 sparse terms in total and have total degree 90.

A simultaneous preflight encoding would have 71 variables, 121 formal / 117
nonzero equations, 15,004 sparse terms, and maximum degree 8.  It is recorded
only as a size census.  The execution contract itself is sequential and never
uses an anonymous expanded product.

## Component-decoration rule

At stage `k`, the input ideal is `J_k` and the named parent-wall polynomial is
`H_k`.  The next ideal is

```text
J_(k+1) = J_k : H_k^infinity.
```

The contract also preserves the wall branch

```text
A_k = J_k + <H_k>
```

and the exact set identity

```text
V(J_k) = V(J_(k+1)) union V(A_k).
```

For every primary component omitted at this stage, the future exact job must
emit an exponent `n >= 1` and an exact reduction certificate `H_k^n in Q`.
That witness proves `V(Q) subset V(H_k)`, attaching the component to the named
parent wall.  The constructor packages this obligation but does not claim that
the unknown component list has already been computed.

No residual factor, critical minor, derivative, rank witness, chart divisor,
or homogenizing variable appears in the saturator ledger.  Consequently every
source singular point with all 62 parent walls nonzero remains in the
localized ideal.  Chart/rank/extra-factor/infinity strata are retained rather
than silently discarded.

## Exact canaries

The two known coordinate four-spaces receive separate discriminating wall
checks:

- `P1=<a,b,c,d,f>` is removed by the named wall `1346=a`; the other
  four-space has `a` free.
- `P2=<b,c,d,e,f>` is removed by the named wall `1247=e`; the other
  four-space has `e` free.

In each case the selected wall polynomial belongs to the coordinate ideal, so
the relation `1-uH=0` reduces to `1=0` on that four-space.  The contract also
replays all 23 parent-wall memberships of each four-space.

Three explicit hostile boundary canaries reject relabeling an artificial box
face, an unsupported chart seam, or a source rank-loss minor as projective
infinity.  The constructor replay additionally rejects 27/27 structural
mutations, including a 70-wall transplant from the older D9 workflow,
singular-locus loss, premature Q1 activation, and theorem/residual promotion.

## Available exact executor and resource frontier

The local WSL `lee-dev` distribution contains Singular 4.4.1 under
`/home/lee/.local/share/9dvl-exact-cas/v1`; its installed `elim.lib` provides
`sat_with_exp`.  The guarded runner uses that procedure one named wall at a
time and records the saturation exponent, dumped standard-basis state, timing,
peak RSS, and the last exact completed stage.

The host has about 15.84 GiB physical RAM and WSL currently exposes about
7.68 GiB, so the nominal 32 GiB cycle ceiling is not actually available.  The
job is preregistered at 180 seconds and 7 GiB per stage, 210 total wall minutes,
and 9 GiB scratch.  This arithmetic envelope is inside both the cycle limits
and the observed WSL RAM, but confidence is low: the available measurements
(4.802 s / 213.7 MiB for the exact D3 source replay and 0.789 s / 35.4 MiB for
the older inverse-circuit check) cover construction only, not a saturation
solve.  Any exceeded stage returns a preserved timeout frontier.

The Singular smoke test uses only the toy ideal `<x^2,xy>` and confirms that
`sat_with_exp` is callable.  It is not evidence about the research ideal.

## Gate status

Q0 remains a constructor candidate pending genuinely independent replay.  In
particular, the independent verifier must decide whether the per-stage
component-witness schema and low-confidence local forecast satisfy the Q0
standard.  `run_q1_saturation.py --execute` refuses to run unless an
independent acceptance artifact is bound to both the byte and semantic hashes
of the exact contract.

Even completion of all 62 saturations would not by itself close Q1.  The
remaining ideal would still need an exact dimension result, complete real-root
classification, component attachments, parent-chamber residence, true
infinity continuation, and complete `S8` transfer.

## Replay

```console
python ops/team/d3-triple-critical-saturation-constructor/build_saturation_contract.py
python ops/team/d3-triple-critical-saturation-constructor/verify_saturation_contract.py
python ops/team/d3-triple-critical-saturation-constructor/run_q1_saturation.py --dry-run
python ops/team/d3-triple-critical-saturation-constructor/run_q1_saturation.py --smoke-test
```
