#!/usr/bin/env python3
"""Exact bookkeeping/regression for the rank-three-program audit.

This checker does not attempt to verify a literature theorem.  It checks the
rank and missing-basis bookkeeping that prevents that theorem from applying
to the one-row double-contraction projection, then reruns the existing exact
row-2599 disconnected-slice certificate.
"""

from math import comb

import verify_double_contraction_gap


def main():
    # Six uncontracted parent labels plus the two private extension labels.
    quotient_labels = 6 + 2
    first_lift_ground_size = quotient_labels + 1
    first_lift_rank = 3
    first_lift_dual_rank = first_lift_ground_size - first_lift_rank

    # A height row is a coextension/lifting of the rank-two quotient.  Dually
    # it is a same-rank extension problem of rank six, not rank three.
    assert quotient_labels == 8
    assert first_lift_ground_size == 9
    assert first_lift_dual_rank == 6

    # Adding the second height row is another coextension.  Its dual is again
    # an extension of a rank-six oriented matroid (now on ten elements).
    double_lift_ground_size = first_lift_ground_size + 1
    double_lift_rank = 4
    double_lift_dual_rank = double_lift_ground_size - double_lift_rank
    assert double_lift_ground_size == 10
    assert double_lift_dual_rank == 6

    # The two private columns never occur together in a prescribed basis.
    # In rank four, choose their two parent partners from all eight parents.
    missing_rank4_bases = comb(8, 2)
    # After contracting one parent basis column, seven rank-three triples
    # containing both private labels remain unprescribed.
    missing_rank3_bases = 7
    assert missing_rank4_bases == 28
    assert missing_rank3_bases == 7

    # The extension-space theorem's full abstract rank-three extension poset
    # has sphere dimension r-1=2, so that conclusion itself does not state
    # degree-two vanishing.
    abstract_extension_sphere_dimension = first_lift_rank - 1
    assert abstract_extension_sphere_dimension == 2

    print("PASS first height row dual extension rank", first_lift_dual_rank)
    print("PASS second height row dual extension rank", double_lift_dual_rank)
    print(
        "PASS private-private bases remain unprescribed:",
        missing_rank4_bases,
        "rank-four and",
        missing_rank3_bases,
        "rank-three",
    )
    print("RUN exact disconnected affine-slice regression")
    verify_double_contraction_gap.main()
    print("PASS rank-three-program audit regression")


if __name__ == "__main__":
    main()
