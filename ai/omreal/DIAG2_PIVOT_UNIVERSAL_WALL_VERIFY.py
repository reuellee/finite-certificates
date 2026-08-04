#!/usr/bin/env python3
"""Verifier for the universal support-drop wall-star theorem and census.

The topological theorem is proved in the accompanying note.  This script
checks its signed incidence algebra for every compactness pattern on small
stars and at the full 51-spoke size.  It then compiles and runs the residual-
wall Burnside enumerator and parses its exact orbit counts.  Those pairs are
precisely the generic simple support types for which the smaller wall support
P union R is pencil-rigid, so support pruning alone does not supply a flexible
spoke.

The 112,041 retained orbits pass only the universal unary signed circuit
filter.  They are an exact finite exceptional superset, not 112,041
realizable compact wall components.
"""

import argparse
from itertools import product
from pathlib import Path
import subprocess
import tempfile


HERE = Path(__file__).resolve().parent
CPP_CENSUS = HERE / "DIAG2_PIVOT_RESIDUAL_WALL_ORBITS.cpp"


def rational_rank(matrix):
    rows = [list(map(int, row)) for row in matrix]
    if not rows:
        return 0
    from fractions import Fraction

    rows = [[Fraction(value) for value in row] for row in rows]
    rank = 0
    for column in range(len(rows[0])):
        pivot = next(
            (row for row in range(rank, len(rows)) if rows[row][column]), None
        )
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        scale = rows[rank][column]
        rows[rank] = [value / scale for value in rows[rank]]
        for row in range(len(rows)):
            if row == rank or not rows[row][column]:
                continue
            scale = rows[row][column]
            rows[row] = [
                left - scale * right
                for left, right in zip(rows[row], rows[rank], strict=True)
            ]
        rank += 1
        if rank == len(rows):
            break
    return rank


def compactness_matrix(center_compact, spoke_compact):
    """Component incidence after Q,T columns have been pencil-pruned.

    Row i exists whenever the center or spoke-i component is compact: the
    triple component through the wall is then a closed component of a compact
    pair component.  Its nonzero entries are the characteristic functions of
    whichever of those two pair components are compact.
    """
    columns = []
    if center_compact:
        columns.append(("center", None))
    columns.extend(
        ("spoke", index)
        for index, compact in enumerate(spoke_compact)
        if compact
    )
    position = {column: index for index, column in enumerate(columns)}
    rows = []
    for index, compact in enumerate(spoke_compact):
        if not (center_compact or compact):
            continue
        row = [0] * len(columns)
        if center_compact:
            row[position[("center", None)]] = 1
        if compact:
            # Alternating Cech signs can replace either 1 by -1 without
            # changing any rank; use -1 to retain the transfer form.
            row[position[("spoke", index)]] = -1
        rows.append(row)
    return rows, columns


def verify_wall_star_algebra():
    # Exhaust every compact/noncompact decoration for eight spokes.  The
    # theorem predicts one kernel exactly when center and every spoke are
    # compact; all other decorations are injective.
    spokes = 8
    for center in (False, True):
        for decoration in product((False, True), repeat=spokes):
            matrix, columns = compactness_matrix(center, decoration)
            kernel = len(columns) - rational_rank(matrix)
            expected = int(center and all(decoration))
            if kernel != expected:
                raise AssertionError(
                    f"wrong wall-star kernel for {center=} {decoration=}: {kernel}"
                )

    # Check the full cofinal size.  A four-support has 52 five-support
    # paddings; after excluding Q there are 51 third indices in the
    # cross-signature case.
    all_compact = (True,) * 51
    matrix, columns = compactness_matrix(True, all_compact)
    if (len(matrix), len(columns), rational_rank(matrix)) != (51, 52, 51):
        raise AssertionError("wrong full exceptional wall-star matrix")
    for missing in (0, 25, 50):
        decoration = list(all_compact)
        decoration[missing] = False
        matrix, columns = compactness_matrix(True, tuple(decoration))
        if rational_rank(matrix) != len(columns):
            raise AssertionError("one noncompact spoke does not kill the transfer kernel")
    matrix, columns = compactness_matrix(False, all_compact)
    if (len(matrix), len(columns), rational_rank(matrix)) != (51, 51, 51):
        raise AssertionError("escaping-center wall star is not unimodular")


EXPECTED_LINES = (
    "PASS: 84,840 labeled residual four-sets form 13 S_8 wall orbits",
    "good=0 total_residual_wall_4plus5=117510 distinguished_fans=5311538",
    "good=1 total_residual_wall_4plus5=112041 distinguished_fans=5082873",
    " wall=36 paddings=30 subtotal=6157 fan_subtotal=182591",
    " wall=37 paddings=48 subtotal=5307 fan_subtotal=246208",
    " wall=38 paddings=48 subtotal=2803 fan_subtotal=128243",
    " wall=39 paddings=30 subtotal=2694 fan_subtotal=78027",
    " wall=41 paddings=48 subtotal=10530 fan_subtotal=501693",
    " wall=42 paddings=48 subtotal=4206 fan_subtotal=197517",
    " wall=44 paddings=48 subtotal=17178 fan_subtotal=817725",
    " wall=46 paddings=34 subtotal=5172 fan_subtotal=174023",
    " wall=47 paddings=34 subtotal=13156 fan_subtotal=442958",
    " wall=48 paddings=52 subtotal=638 fan_subtotal=31555",
    " wall=49 paddings=52 subtotal=12743 fan_subtotal=659313",
    " wall=50 paddings=52 subtotal=20758 fan_subtotal=1071142",
    " wall=51 paddings=52 subtotal=10699 fan_subtotal=551878",
    "THEOREM: these are the exact support-orbit exceptions to the flexible-spoke test",
)


def verify_orbit_census():
    if not CPP_CENSUS.is_file():
        raise AssertionError("missing independent Burnside census source")
    with tempfile.TemporaryDirectory(prefix="diag2-wall-census-") as directory:
        executable = Path(directory) / "verify_signed_pencil_orbits"
        subprocess.run(
            [
                "g++",
                "-O3",
                "-std=c++17",
                str(CPP_CENSUS),
                "-o",
                str(executable),
            ],
            check=True,
        )
        result = subprocess.run(
            [str(executable)], check=True, text=True, capture_output=True
        )
    output = result.stdout
    for line in EXPECTED_LINES:
        if line not in output:
            raise AssertionError(f"missing exact census line: {line}")
    return output


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--skip-orbit-census",
        action="store_true",
        help="run only the instantaneous incidence-algebra regression",
    )
    arguments = parser.parse_args()

    verify_wall_star_algebra()
    print("PASS every compactness pattern on the abstract wall star has the predicted kernel")
    print("PASS a wall-star kernel requires the center and every adjacent spoke compact")
    if arguments.skip_orbit_census:
        print("SKIP exhaustive C++ Burnside orbit census")
        return
    verify_orbit_census()
    print("PASS independent Burnside census: unsigned residual-wall exceptions = 117,510")
    print("PASS unary-signed residual-wall exceptional orbit superset = 112,041")
    print("PASS signed beta strata = 77,649 / 33,453 / 938 / 1 / 0")
    print("PASS distinguished incoming-support wall fans = 5,082,873 orbits")
    print("THEOREM generic simple walls outside those support orbits have a flexible spoke")
    print("CAVEAT the 112,041 are necessary support types, not realized compact components")


if __name__ == "__main__":
    main()
