#!/usr/bin/env python3
"""Exact GP-valid no-go for a fixed triangular pair-root order.

At the canonical type-49 residual wall, two actual one-element extension
signatures are positive on the active wall circuit.  Their common compatible
elementary roots all have source label larger than target label.  Hence none
descends for the opposite total order

    1 > 2 > ... > 8.

By simultaneous S8 equivariance, any globally fixed label order can be
relabelled to this order.  Thus a universal pair receiver theorem cannot
choose every common root from one fixed triangular root system.  This says
nothing against a cell-dependent order or a non-triangular carrier atlas.
"""

from __future__ import annotations

import DIAG9_GRAPH_exact_topes as exact_topes
import verify_diag2_canonical_robust_edges as robust
import verify_diag2_escape_set_topes as escape
import verify_diag3_pair_local_root_switch as local


KIND = 49
SUPPORT = (0, 7, 14, 28)
SIGNATURES = (11_880_862_721_603_236, 4_655_783_301_794_266)
EXPECTED_COMMON = (
    (6, 2, -1), (6, 2, 1),
    (6, 4, -1), (6, 4, 1),
    (7, 3, -1), (7, 3, 1),
    (7, 5, -1), (7, 5, 1),
    (8, 1, -1), (8, 1, 1),
    (8, 2, -1), (8, 2, 1),
    (8, 3, -1), (8, 3, 1),
    (8, 4, -1), (8, 4, 1),
    (8, 5, -1), (8, 5, 1),
    (8, 6, -1), (8, 6, 1),
    (8, 7, -1), (8, 7, 1),
)


def main() -> None:
    factor_ids, factor_polynomials = robust.canonical_data()
    witness = robust.construct_witness(KIND, factor_ids, factor_polynomials)
    if local.active_support(KIND) != SUPPORT:
        raise AssertionError("type-49 active support changed")

    normals = exact_topes.derived_rows(
        robust.integer_matrix(witness.center), normalize=False
    )
    _, extensions = local.gate.enumerate_extensions(witness.parent)
    extensions = set(map(int, extensions))
    if not set(SIGNATURES).issubset(extensions):
        raise AssertionError("the pinned signings are no longer GP-valid extensions")
    if not all(
        local.positive_wall_signing(signature, SUPPORT, normals)
        for signature in SIGNATURES
    ):
        raise AssertionError("a pinned signing lost the positive wall circuit")

    predicates = local.RootPredicates.build(SUPPORT)
    common = tuple(
        direction
        for root, direction in enumerate(escape.DIRECTIONS)
        if all(
            local.constraints_hold(
                signature, predicates.compatibility[root]
            )
            for signature in SIGNATURES
        )
    )
    if common != EXPECTED_COMMON:
        raise AssertionError(f"common-root list changed: {common}")

    # For the total order 1 > 2 > ... > 8, a descending root has source
    # numerically smaller than target.  Every common root goes the other way.
    if not all(source > target for source, target, _sign in common):
        raise AssertionError("a common root now descends in the pinned order")

    print("PASS type-49 canonical wall and active support", SUPPORT)
    print("PASS GP-valid positive signings", SIGNATURES)
    print("PASS common roots", len(common), "all ascend for 1>2>...>8")
    print("NO-GO no globally fixed triangular label order is universal")
    print("SCOPE relabeling-equivariant local obstruction; dynamic atlases remain possible")


if __name__ == "__main__":
    main()
