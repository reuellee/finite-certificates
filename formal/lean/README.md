# Lean formal replay

This Lake project is a small-kernel formalization checkpoint for the 9DVL
certificate library.  Its first target is the exact row-2599
[`DIAG3_PAIR_MASTER_CLOSURE_NODE_CANARY`](../../ai/omreal/DIAG3_PAIR_MASTER_CLOSURE_NODE_CANARY.md).

From this directory, run:

```console
lake build
```

The build checks three concrete theorems:

- `nodeCertificateAccepted`: the finite 17-cell certificate satisfies its
  scope, closure, integral-incidence, profile-accounting and balanced-pair
  checks;
- `all216ProfileTriplesExact`: every ordered triple of the six exact
  feasibility profiles has `MN=0` and zero middle residue over `F_2`;
- `hostileMutationsRejected`: global-scope promotion, invented parent
  infinity, incomplete signature accounting and corrupt integral incidence
  are rejected.

All three proofs use kernel reduction via `decide`, not `native_decide` or an
external solver.  The module prints each theorem's axiom dependencies during
the build; with Lean 4.33.1 they contain only `propext`.

## JSON data bridge

The proof consumes
[`GeneratedNodeData.lean`](NineDVLFormal/GeneratedNodeData.lean), rendered
deterministically from the exact JSON certificate:

```console
python ../../ai/omreal/build_diag3_pair_master_closure_node_lean.py --check
python ../../ai/omreal/verify_diag3_pair_master_closure_node_lean.py
```

The first command checks byte-for-byte regeneration.  The second verifier does
not import the generator: it independently matches the JSON byte digest,
scope, cell simplices, profile census and integral matrices, and rejects six
hostile bridge mutations.

## Scope

This formalizes the finite semantic layer of one exact two-dimensional local
disk.  The existing exact Python verifier remains responsible for rebuilding
the semialgebraic branch partition from source polynomials.  Neither checker
claims global coverage of the nine-dimensional parent cell.  The honest 9DVL
ledger therefore remains **2/9**.
