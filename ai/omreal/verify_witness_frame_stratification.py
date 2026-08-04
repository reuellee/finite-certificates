#!/usr/bin/env python3
"""Exact regression test for the independent-witness-frame strategy.

The saved row-2599 affine family has two proper incomparable signatures for
which the second is feasible at the ends and Gordan-infeasible on the whole
middle interval.  This checker adds two fixed extension columns.  It verifies
that all four signatures are proper and pairwise incomparable and that their
endpoint witnesses are independent frames of one positive orientation.
Thus the full-rank witness stratum has a disconnected affine projection
slice.  Full witness rank therefore does not repair projected height-line
convexity.  This is not a 9DVL counterexample.
"""

import numpy as np

import verify_double_contraction_gap as gap
import verify_seeat_residence_nonconvex as residence
import verify_seeat_upper_bound as upper


EXTRA_COLUMNS = ((339, -435, -214, 201), (-319, 147, 82, 194))
EXTRA_SIGNATURES = (71899532269460528, 13946487285424257)

# Ordered pair (a,b) -> (chart, strict witness for a, positive circuit for b).
SEPARATORS = {
    (0, 1): (1, (520355, 767936, -729137, 25814),
             ((13, 71600012), (17, 244289969), (43, 219639604),
              (44, 497292651), (51, 167852091))),
    (0, 2): (1, (520355, 767936, -729137, 25814),
             ((40, 566660), (41, 1085324), (47, 1292876), (53, 277857))),
    (0, 3): (1, (520355, 767936, -729137, 25814),
             ((0, 91885920), (33, 53349282), (41, 327758326),
              (43, 183579245), (52, 139580523))),
    (1, 0): (31, (39690, -956949, 444343, 506125),
             ((1, 64062537), (29, 28010290), (30, 196347516),
              (34, 39419440), (41, 79556169))),
    (1, 2): (32, (-631980, 445056, 146208, 510808),
             ((6, 1201072392), (13, 619776688), (25, 582638589),
              (47, 5492291246), (53, 947488906))),
    (1, 3): (17, (1502203, -1180503, 4545685, -3563471),
             ((0, 35237334), (7, 189835101), (18, 25773892),
              (33, 36589366), (41, 107915583))),
    (2, 0): (2, (-2, -4, -5, 7),
             ((3, 874666767957611180274818340),
              (28, 67071104927867665927849659),
              (30, 1184874324249437382541012830),
              (41, 644990303885873720494092306),
              (44, 670469703326831926505401667))),
    (2, 1): (2, (-2, -4, -5, 7),
             ((4, 2077761508723495173), (13, 1400516973102763068),
              (30, 500789070551888770), (36, 1261743052322000656))),
    (2, 3): (2, (-2, -4, -5, 7),
             ((2, 32333629263878103), (3, 484253284286314805),
              (14, 874208746110302380), (44, 1041053674024143724))),
    (3, 0): (44, (9027, 6120, -9538, -8067),
             ((3, 8014850993093180), (14, 9535383827206828),
              (28, 8664032686321265), (31, 11452905989829998),
              (41, 11267253675251195))),
    (3, 1): (3, (9, -6, -2, 3),
             ((3, 280418752037621635599354632),
              (16, 21921502986943619631060565),
              (27, 33420749118584629324851680),
              (32, 110738570166670627644842028),
              (36, 68833125970613725158586616))),
    (3, 2): (3, (9, -6, -2, 3),
             ((40, 187807724236693458), (41, 8974002480569479),
              (47, 174547404257235460), (53, 20051613016533220))),
}


def main():
    gap.main()
    certificate = np.load(residence.CERTIFICATE, allow_pickle=False)
    fixed = certificate["fixed"]
    right, left = certificate["right"], certificate["left"]
    contraction_column = left - right
    endpoint_parents = (
        residence.insert(fixed, 0, 2 * right),
        residence.insert(fixed, 0, 2 * left),
    )
    midpoint_parent = residence.insert(fixed, 0, left + right)
    signatures = (
        residence.extension_signature(endpoint_parents[0], contraction_column),
        int(certificate["signature"].item()),
        *EXTRA_SIGNATURES,
    )
    if len(set(signatures)) != 4:
        raise AssertionError("the four signatures are not distinct")

    for column, expected in zip(EXTRA_COLUMNS, EXTRA_SIGNATURES, strict=True):
        got = tuple(
            residence.extension_signature(parent, column)
            for parent in (*endpoint_parents, midpoint_parent)
        )
        if got != (expected,) * 3:
            raise AssertionError("an extra signature changes on the line")

    sigma2_points = (certificate["right_point"], certificate["left_point"])
    determinants = []
    for parent, sigma2_point in zip(endpoint_parents, sigma2_points, strict=True):
        _, rows = residence.signed_rows(parent, signatures[1])
        if not residence.strict_witness(rows, sigma2_point):
            raise AssertionError("invalid endpoint witness")
        frame = np.column_stack(
            (contraction_column, sigma2_point, *EXTRA_COLUMNS)
        )
        determinants.append(residence.determinant(frame.tolist()))
    if not all(value > 0 for value in determinants):
        raise AssertionError("the endpoint frames do not have one orientation")

    cert178 = np.load(
        upper.HERE / "data" / "seeat_parent2599_upper178.npz",
        allow_pickle=False,
    )
    charts = cert178["chart_matrix"]
    catalog = [
        line.strip()
        for line in residence.gate.CATALOG_48.open(encoding="utf-8")
        if line.strip()
    ]
    expected_parent = catalog[residence.gate.PARENT_INDEX]
    ordered_pairs = {
        (a, b) for a in range(4) for b in range(4) if a != b
    }
    if set(SEPARATORS) != ordered_pairs:
        raise AssertionError("ordered-pair separators are incomplete")
    for (feasible, excluded), (chart_index, point, circuit) in SEPARATORS.items():
        matrix = charts[chart_index]
        parent, feasible_rows = residence.signed_rows(matrix, signatures[feasible])
        _, excluded_rows = residence.signed_rows(matrix, signatures[excluded])
        if parent != expected_parent:
            raise AssertionError("a separator has the wrong parent")
        if not residence.strict_witness(feasible_rows, point):
            raise AssertionError("invalid ordered-pair feasible witness")
        if not residence.gordan_witness(
            excluded_rows, residence.sparse_weights(circuit)
        ):
            raise AssertionError("invalid ordered-pair Gordan circuit")

    print("PASS two fixed extra signatures remain feasible on the affine line")
    print("PASS the four endpoint witnesses form one positively oriented frame")
    print("PASS all four regions are proper and pairwise incomparable")
    print("THEOREM: the full-rank witness stratum has a disconnected affine projection slice")
    print("NOTE: full rank does not restore linewise convexity; diagonal four stays open")


if __name__ == "__main__":
    main()
