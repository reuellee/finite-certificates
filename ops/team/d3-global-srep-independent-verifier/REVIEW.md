# Independent Q0 verification

Verdict: **PASS — `Q0_NULL_INDEPENDENTLY_CONFIRMED`** for frozen evidence commit
`e18efbdea3ef00616f4a6cb83967f6bb267b1a5d`.

This is a machine-independent replay in the sense relevant to the cycle: the verifier uses only
the Python standard library, parses the producer and falsifier JSON as untrusted data, imports no
producer/falsifier code, and binds five inputs by SHA-256.

The replay independently:

- derives the producer triangle faces from its integer-polynomial formulas and recomputes relative
  rational homology, obtaining unfilled `H1=1` and filled `H1=0`, with `d^2=0` in both cases;
- rebuilds the falsifier tetrahedral complexes from maximal simplices and obtains unfilled `H1=1`
  and filled `H1=0`, again with `d^2=0`;
- checks exactly that `(1/n,3/2)` lies in the M2 pointwise union for every positive integer `n`,
  converges to `(0,3/2)`, and that this limit is excluded and is not true parent infinity; and
- confirms the producer reports `q0_pass=false`, `q1_eligible=false`, `cloud_used=false`,
  `theorem_credit=NONE`, and null `N`, `s`, and `d`.

All 22 hostile in-memory mutations were rejected, covering false gate promotion, fabricated global
parameters, filled/unfilled conflation, face/relative/incidence/rank drift, a changed M2 limit, and
false-infinity relabelling.

The conclusion is deliberately negative: Q0's canary package is internally sound, but the cycle has
no executable Basu--Karisani replacement backend and no complete global parameters. This review is
not human review, does not activate Q1, and earns no theorem or ledger credit.

Replay:

```text
python -B ops/team/d3-global-srep-independent-verifier/verify_q0.py
```
