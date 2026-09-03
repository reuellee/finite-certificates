# Independent D3 saturation Q0 verification

Verdict: **PASS — `Q0_NULL_INDEPENDENTLY_CONFIRMED`** for frozen evidence
commit `2df3285c19b0c65127bd0acd79df2cc57f0d7752` and tree
`67bc7fa65db3d45f42edf724d7c7f69cef8edbfc`.

This is an independent machine replay, not human review.  The verifier reads
seven inputs directly from frozen Git, imports no constructor or falsifier
code, and accepts no reported gate status on trust.  After checking the frozen
canonical wall source byte-for-byte, it independently reconstructs the 62
ordered parent-wall polynomials.

The replay confirms the useful exact part of the handoff:

- 59 formal source equations, 55 nonzero equations, 14,741 sparse terms, and
  maximum degree 8;
- a deterministic 62-stage parent-wall-only saturation order with no
  anonymous product saturation;
- exact stagewise set identities and named wall branches;
- both coordinate-four-space attachment canaries; and
- all three artificial-boundary rejection canaries.

It also independently confirms the fail-closed result.  No stage contains a
materialized component list with exact reduction certificates.  The numeric
forecast allocates 12,600 of the 14,400 cycle seconds to saturation, leaving
1,800 seconds while five endpoint obligations remain unforecasted: exact
dimension/emptiness, real-root isolation, chamber classification,
true-parent-infinity continuation, and complete `S8` transfer.  The forecast
is explicitly low-confidence and uncalibrated on saturation, and the runner
does not enforce the 10-GiB scratch ceiling.  Its own successful terminal
marker says further Q1 work remains.

Therefore the preregistered theorem-level decrease is not certified reachable
inside the fixed ceiling.  The mandatory midpoint action is
`FREEZE_Q0_NULL_AND_STOP`; Q1 stays denied.  All 22 hostile gate mutations,
including fabricated Q0 acceptance, Q1 activation, row removal, theorem
credit, and same-route continuation, are rejected.

This result does not disprove component-decorated saturation, prove a compact
component, remove an orbit, or change the theorem ledger.

Replay from the repository root:

```console
python -B ops/team/d3-triple-critical-saturation-independent-verifier/verify_q0.py
```

