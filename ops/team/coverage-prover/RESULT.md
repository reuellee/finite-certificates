# Coverage-prover result: exact skeleton-information no-go

## Outcome

**Inconclusive for the actual residual factors, with a proved exact obstruction
to the proposed inference.**  The optimal 40-of-105 cover cannot be promoted
from factor incidence to ambient component coverage using source-skeleton data
alone, even if all 40 edges receive complete ordered root roadmaps and labels.

The replay constructs an exact countermodel inside the actual strict row-2599
parent cell.  Let `F_137` be accepted primitive residual factor 137.  It is
affine, crosses six retained edges, and is strictly positive on a rational
nine-box of half-width `1/4096` centered at unused stored chart 9.  Exact
evaluation at all 512 box vertices proves all 70 target-signed parent brackets
strictly positive on that box; multiaffinity makes the vertex check a proof on
the whole box.

Put

```text
q(x) = sum_j (x_j-c_j)^2 - (1/8192)^2,
H(x) = F_137(x) q(x).
```

Exact rational point-to-segment minimization proves `q>0` on every retained
edge.  Therefore `H` and `F_137` have the same signs, zeros, root order, and
root multiplicities on the entire 40-edge skeleton.  Off the skeleton,
`Z(H)` has the additional connected compact component `Z(q)=S^8`.  The sphere
lies inside the certified parent-safe box, where `F_137>0`, so it is disjoint
from `Z(F_137)` and from genuine parent infinity.

This does **not** replace any accepted primitive residual polynomial: `H` is
a semantic countermodel, not an actual residual factor.  It therefore does
not disprove actual component coverage.  It proves the narrower and decisive
nonconsequence that no amount of one-dimensional skeleton compilation can
supply the missing ambient-coverage theorem.

## Recommendation: relative polar-anchor ladder

Do not make compiling the remaining 38 edges the next critical path.  Use a
source-specific off-skeleton certificate with three fail-fast tiers:

1. **Global pivot screen.**  For each of the 10,844 crossed primitive factors,
   search the nine coordinates for an exact Bernstein certificate that a
   partial derivative has fixed sign on a coverage-certified parent atlas.
   Record the coefficient-degeneracy frontier.  This cheaply identifies walls
   that are global graphs on parent fibers.
2. **Boundary escape screen.**  For graph cases, certify that every connected
   projected feasibility component reaches a genuine parent divisor, or meets
   one of the retained factor events.  Artificial box boundaries never count
   as infinity.
3. **Relative polar roadmap for the residue.**  Choose a fixed generic rational
   Morse direction.  A compact missed component must contain an interior
   Lagrange critical point.  Isolate the zero-dimensional polar candidates and
   continue the incident polar arcs exactly until they meet the retained
   skeleton or a tagged parent wall.  Recurse on genuine boundary strata.

This ladder is stronger than a full-skeleton build and potentially much
smaller than a nine-dimensional sign CAD.  Its first discriminating output
should be a census, by primitive factor and pivot, of fixed-sign derivative
certificates versus polar-roadmap residue.  A zero or small residue validates
the architecture; a large residue redirects effort before another expensive
compiler tranche.

## Replay

From pinned revision `ec362dba8a912bc4749c004641aee2da0a88dc05`:

```console
PYTHONDONTWRITEBYTECODE=1 python \
  ops/team/coverage-prover/verify_diag3_pair_skeleton_incidence_no_go.py
```

The verifier reconstructs all exact source data, 35,840 parent-box vertex
checks, the factor-safe box, all 40 rational closest-point calculations, and
the six exact factor crossings.  It rejects re-sealed scope mutations that
claim an actual residual counterexample, actual or global coverage, pair
closure, or promotion to `3/9`.

## Honest scope

- Actual component coverage: **open**.
- Pair obligation `diag3_pair_hc1`: **open**.
- Triple obligation: untouched.
- Honest 9DVL ledger: **2/9**.
- Proposed ledger change: none; preserve this result as a decision-log no-go
  against treating finite-skeleton completion as a coverage proof.
