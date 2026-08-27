# Diagonal three: first proof-producing master-closure canary

## Result

The full-support master-closure compiler now has its first generated exact
geometric certificate.  It converts the coverage-certified transverse-node
disk in row 2599 into a labelled 17-cell regular-CW closure object and
independently replays the complete path

```text
parent matrix and residual polynomials
  -> covered semialgebraic partition
  -> regular closure poset
  -> complete bad-signature labels
  -> integral cellular incidence
  -> mod-two middle-rank replay.
```

The honest 9DVL score remains **2/9**.  This is complete on one exact
two-dimensional disk inside the full support `(15,15,15)`.  It is not a
coverage claim for the nine-dimensional parent cell.

## Exact geometric source

The source is
`data/DIAG9_GRAPH_row2599_node_roadmap.npz`, SHA-256

```text
ddec96b052b305d279b543be2af27e12f380f0dedc79ea434616c64b40cd8cea
```

On its exact rational square the independent verifier reconstructs all
`84,840` labelled residual determinant restrictions.  Exactly two coprime
affine branches occur, each carrying `65` labelled occurrences.  Each branch
has `32` constant and `33` affine nonvanishing quotients.  Every other
residual determinant and all `70` parent brackets have exact dominance
margins greater than one, and the two branch gradients have nonzero exact
Jacobian.

Consequently the two branches are the complete discriminant on the square:
they meet transversely in one rational node, cut the square into four open
chambers, and have four wall rays ending at four distinct points of the
artificial square boundary.  No parent wall or compactification face occurs
inside this local object.

## Generated closure object

The producer emits:

| dimension | cells | roles |
|---:|---:|---|
| 0 | 5 | one residual node and four scope-boundary wall endpoints |
| 1 | 8 | four residual wall rays and four scope-boundary arcs |
| 2 | 4 | the four open chambers |

Every chamber closure is an intersection of the exact square with two affine
halfspaces and is therefore a convex regular ball.  Every wall ray is a
closed segment.  The four outer arcs form a closed subcomplex, recorded as
`scope_boundary_subcomplex`.

The true `parent_infinity_subcomplex` is empty.  This distinction is
load-bearing: the square boundary is only the edge of the computed scope,
and the parent-bracket replay proves that it cannot be relabelled as parent
infinity.

The producer stores every strict closure-comparable pair and every strict
three-cell chain.  It also emits canonical integral boundary matrices using
spokes oriented away from the node and the outer cycle oriented cyclically.
The verifier regenerates every incidence and checks `d^2=0` over `Z`.

## Complete signature accounting

Exact Grassmann--Pluecker backtracking reconstructs all `97,224` extensions
of parent 2599.  Exact tope enumeration on the four chambers gives the
complete feasibility-profile census

| chamber mask | signatures |
|---:|---:|
| `0000` | `70,968` |
| `0011` | `72` |
| `0110` | `72` |
| `1001` | `72` |
| `1100` | `72` |
| `1111` | `25,968` |

The certificate stores a semantic digest of the complete
signature-to-profile map.  For each profile it records the derived closed bad
subcomplex; the verifier reconstructs these cell sets from incident chamber
labels and rejects any failure of closure.

## Pair-complex replay

The artificial outer boundary is retained as ordinary cells.  For all
`6^3=216` ordered triples of membership profiles, the verifier constructs the
three closed bad subcomplexes, their triple and exclusive-pair strata, and the
canonical signed integral `N,M` matrices.  Every row satisfies `MN=0` and
has zero middle cohomology over `F_2`.

The exact histogram `(dim C1, rank N, rank M, dim H1)` is

```text
(0,0,0,0): 16     (2,2,0,0): 12     (3,2,1,0): 24
(5,3,2,0): 36     (7,5,2,0): 36     (8,4,4,0): 3
(8,5,3,0): 24     (10,6,4,0): 52    (13,7,6,0): 12
(16,8,8,0): 1
```

This is a local exactness theorem, not the global diagonal-three pair
injectivity theorem.

## Trust separation

The deterministic producer

```console
python ai/omreal/build_diag3_pair_master_closure_node_canary.py
```

only translates the pinned node roadmap into the master-closure format.  The
verifier

```console
python ai/omreal/verify_diag3_pair_master_closure_node_canary.py
```

does not trust producer booleans.  It independently recomputes coverage,
parent residence, branch factorization, regularity, closure, signature
profiles, boundary matrices and all 216 ranks.  Seven hostile mutations are
rejected, including sampled coverage, false parent infinity, incomplete
closure, incomplete signature accounting, a corrupt active-factor digest,
an unsigned branch change and nonzero `d^2`.

The generated certificate is
`data/DIAG3_PAIR_MASTER_CLOSURE_NODE_CANARY.json`.

## Lean kernel replay

The finite semantic layer also has a Lean 4 replay in
[`../../formal/lean/NineDVLFormal/NodeCanary.lean`](../../formal/lean/NineDVLFormal/NodeCanary.lean).
It reconstructs the closed bad subcomplexes and balanced pair complexes from
the 17 simplicial cells, checks integral `d1*d2=0`, and proves all 216 ordered
profile triples have zero middle residue over `F_2`.  Separate theorems reject
four fail-closed mutations: false global coverage, invented parent infinity,
incomplete signature accounting and corrupt integral incidence.

The proofs use kernel reduction (`decide`), not `native_decide`; their printed
axiom audit contains only Lean's `propext`.  A deterministic generated module
carries the JSON payload into Lean, while an independent Python bridge verifier
checks the exact certificate byte digest and semantic fields and rejects six
bridge mutations.  The formal replay deliberately does not duplicate the
semialgebraic branch reconstruction performed above, so its scope is still
local and the 9DVL ledger remains **2/9**.

```console
python ai/omreal/build_diag3_pair_master_closure_node_lean.py --check
python ai/omreal/verify_diag3_pair_master_closure_node_lean.py
cd formal/lean && lake build
```

## Next bounded target

The next compiler stage is a **multi-box two-dimensional full-support
roadmap**, not the full nine-dimensional decomposition.  It should cover a
declared rational rectangle containing several residual events and glue
no-wall, one-wall, transverse two-wall and higher-specialization boxes by
exact boundary sign words.  Success requires the same generated closure
object and independent rank replay.  Projection growth or an unclassified
box at the declared ceiling is a bounded no-go and must preserve its exact
frontier rather than trigger automatic enlargement.
