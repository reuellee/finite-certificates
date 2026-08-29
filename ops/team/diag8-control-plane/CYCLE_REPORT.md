# Diagonal-eight strategy-reset cycle

Date: 2026-08-29 UTC

Canonical base: `5393b03fda623dc6b4552130d13467fae71d31bc`

Canonical tree: `06cc3363a021b8adc59e66865f44bf8eafa66029`

## Outcome

This cycle does not prove or disprove diagonal eight.  It replaces the prior
graph-routing loop with a proof-bearing codimension-two gate and obtains two
exact geometric fillings on the parent-860 training network.  The honest
9DVL ledger remains `2/9`, with `diag8_h1` open.

## Accepted exact results

1. The full 26,264-signature network universe has 13 support classes: one
   universal class contains 25,960 signatures, and 304 signatures form 12
   proper classes.  The proper-class inclusion poset has width exactly six.
   There are nine size-six antichains, all with empty common network support,
   and no size-eight antichain.  This is a local quotient theorem only;
   missing chambers can refine its equality and inclusion classes.
2. The rational `a/d` triangle `0-4-11-0` lies in parent 860 and in the
   common feasibility locus of five proper incomparable signatures.  Exact
   replay checks 210 parent controls, 840 signed feasibility controls, and
   350 affine mixed coefficients, so the triangle fills the graph cycle.
3. On the rational `a/g` pentagon `1-2-3-18-17-1`, 26,738 of 26,740 residual
   factors are exact sign-definite.  The remaining factors 16573 and 22629
   meet transversely once while all 70 parent brackets remain strict.  Their
   node dual cell fills the mask-3 cycle for all 26,038 boundary-common stored
   labels.
4. A complete labelled graph is insufficient for diagonal-eight `H_1`.
   Exact filled/unfilled and relative-infinity fixtures with identical
   one-skeleta give different first homology.  Any future certificate must
   supply complete signed `C0/C1/C2` incidence, complete labels, genuine
   infinity, global dominance/properness witnesses, and exact ranks or a
   proof-carrying Morse substitute.
5. Ordinary mutation connectivity and reducible deletion are insufficient
   transport mechanisms: they do not preserve the complete label universe
   and incidence needed by the relative certificate.

## Surviving discriminator

The parent-860 mask-6 graph contains the cycle

```text
4-11-12-14-13-23-4
```

with one attached leaf and 26,038 common stored labels.  It spans the
`a,d,f,g` coordinates.  The next bounded cycle should stop at the first of:

- an exact parent-safe spanning two-chain with every residual wall/node
  subdivision and relative boundary attached;
- an exact parent-boundary crossing that invalidates the proposed disk; or
- an exact non-boundary cocycle in a coverage-certified relative complex.

No graph cycle, sampled mask, mutation path, or deletion equivalence may be
promoted without the complete two-skeleton and infinity gates.

## Replays

```console
PYTHONDONTWRITEBYTECODE=1 python \
  ops/team/diag8-dual-prover/verify_diag8_parent860_graph_h1.py
PYTHONDONTWRITEBYTECODE=1 python \
  ops/team/diag8-falsifier/verify_diag8_falsifier.py
PYTHONDONTWRITEBYTECODE=1 python \
  ops/team/diag8-certificate/verify_diag8_relative_h1_certificate.py
PYTHONDONTWRITEBYTECODE=1 python \
  ops/team/diag8-transport/verify_transport_obstruction.py
```

The independent referee gates are in `ops/team/diag8-referee/GATE_TABLE.yaml`.
