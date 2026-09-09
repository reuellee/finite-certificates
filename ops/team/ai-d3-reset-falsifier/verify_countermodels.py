"""Small exact checks, with no external dependencies and no parent enumeration.

The geometric proofs are in FINDINGS.md. This checks polynomial identities,
the specified intersection dimensions, and a separate relative cubical complex
for the bad-locus union. It does not test the 2,604 actual parent classes.
"""
from fractions import Fraction
from itertools import combinations, permutations, product
import json
from pathlib import Path
import time

HERE = Path(__file__).resolve().parent
ZERO = (0, 0, 0)


def polynomial(constant=0, variable=None):
    answer = {ZERO: constant} if constant else {}
    if variable is not None:
        exponent = tuple(int(i == variable) for i in range(3))
        answer[exponent] = 1
    return answer


def add(a, b):
    answer = a.copy()
    for key, value in b.items():
        answer[key] = answer.get(key, 0) + value
        if answer[key] == 0:
            del answer[key]
    return answer


def multiply(a, b):
    answer = {}
    for x, coefficient_x in a.items():
        for y, coefficient_y in b.items():
            key = tuple(u + v for u, v in zip(x, y))
            answer[key] = answer.get(key, 0) + coefficient_x * coefficient_y
    return {key: value for key, value in answer.items() if value}


def scale(a, coefficient):
    return {key: value * coefficient for key, value in a.items() if value * coefficient}


def dot(a, b):
    answer = {}
    for x, y in zip(a, b):
        answer = add(answer, multiply(x, y))
    return answer


def determinant(matrix):
    answer = {}
    for order in permutations(range(len(matrix))):
        inversions = sum(order[i] > order[j]
                         for i in range(len(order)) for j in range(i + 1, len(order)))
        term = polynomial((-1) ** inversions)
        for i, j in enumerate(order):
            term = multiply(term, matrix[i][j])
        answer = add(answer, term)
    return answer


def rank(matrix):
    if not matrix:
        return 0
    data = [[Fraction(value) for value in row] for row in matrix]
    rows, columns = len(data), len(data[0])
    pivot_row = 0
    for column in range(columns):
        pivot = next((i for i in range(pivot_row, rows) if data[i][column]), None)
        if pivot is None:
            continue
        data[pivot_row], data[pivot] = data[pivot], data[pivot_row]
        leading = data[pivot_row][column]
        data[pivot_row] = [entry / leading for entry in data[pivot_row]]
        for i in range(pivot_row + 1, rows):
            factor = data[i][column]
            if factor:
                data[i] = [x - factor * y for x, y in zip(data[i], data[pivot_row])]
        pivot_row += 1
        if pivot_row == rows:
            break
    return pivot_row


def common_matrix():
    rows = []
    for j in range(3):
        for sign in (1, -1):
            row = [polynomial() for _ in range(4)]
            row[j] = polynomial(sign)
            row[3] = polynomial(variable=j)
            rows.append(row)
    rows.extend([[polynomial(), polynomial(), polynomial(), polynomial(1)]
                 for _ in range(50)])
    return rows


def verify_polynomial_system():
    rows = common_matrix()
    assert len(rows) == 56
    assert determinant([rows[j] for j in (0, 2, 4, 6)]) == polynomial(1)
    output = []
    for i in range(3):
        signs = [1 if j >= 6 or j % 2 == 0 or j // 2 == i else -1 for j in range(56)]
        signed = [[scale(value, sign) for value in row] for row, sign in zip(rows, signs)]
        witness = [polynomial(1, j) if j != i else polynomial() for j in range(3)]
        witness.append(polynomial(1))
        slacks = [dot(row, witness) for row in signed]
        for j in range(3):
            expected = ([polynomial(variable=i)] * 2 if j == i else
                        [add(polynomial(1), scale(polynomial(variable=j), 2)), polynomial(1)])
            assert slacks[2*j:2*j+2] == expected
        assert slacks[6:] == [polynomial(1)] * 50
        # At g_i=0 the active two rows are exact opposites; their sum is 2*g_i*e4.
        pair_sum = [add(signed[2*i][j], signed[2*i+1][j]) for j in range(4)]
        assert pair_sum == [polynomial()] * 3 + [scale(polynomial(variable=i), 2)]
        # Every other module has two +1 coefficients in its private coordinate.
        # A nonnegative kernel therefore kills both weights in each such module.
        for j in range(3):
            if j != i:
                assert [signed[k][j] for k in range(56)] == [
                    polynomial(1) if k in (2*j, 2*j+1) else polynomial()
                    for k in range(56)]
        output.append(signs)
    return {"common_unsigned_rows": 56, "columns": 4,
            "constant_full_rank_minor": 1, "signature_signs": output,
            "symbolic_strict_witness_identities": "PASS",
            "nonnegative_kernel_elimination_coefficients": "PASS"}


def relative_cells(free_axes):
    """Relative cubical cells: 0 is the point, +/-1 the two open half-edges.

    All cells with a coordinate fixed at an endpoint +/-1 belong to infinity
    and have already been removed. The remaining cells have this finite code.
    """
    cells = set()
    for axes in free_axes:
        for values in product((-1, 0, 1), repeat=len(axes)):
            cell = [0] * 9
            for axis, value in zip(axes, values):
                cell[axis - 1] = value
            cells.add(tuple(cell))
    dimension = max(sum(value != 0 for value in cell) for cell in cells)
    return [sorted(cell for cell in cells if sum(value != 0 for value in cell) == d)
            for d in range(dimension + 1)]


def boundary_of(cell):
    answer = {}
    active = [j for j, value in enumerate(cell) if value]
    for order, coordinate in enumerate(active):
        face = list(cell)
        face[coordinate] = 0
        # Boundary [-1,0] = [0]-[-1]; boundary [0,1] = [1]-[0].
        answer[tuple(face)] = (-1) ** order * (-cell[coordinate])
    return answer


def cubical_cohomology(free_axes):
    cells = relative_cells(free_axes)
    cell_sets = [set(level) for level in cells]
    boundaries = [{cell: boundary_of(cell) for cell in level} for level in cells]
    ranks = [0]
    for d in range(1, len(cells)):
        for cell, boundary in boundaries[d].items():
            assert set(boundary) <= cell_sets[d - 1]
            if d >= 2:
                squared = {}
                for face, coefficient in boundary.items():
                    for subface, coefficient2 in boundaries[d - 1][face].items():
                        squared[subface] = squared.get(subface, 0) + coefficient * coefficient2
                assert all(coefficient == 0 for coefficient in squared.values())
        matrix = [[boundaries[d][cell].get(face, 0) for cell in cells[d]]
                  for face in cells[d - 1]]
        ranks.append(rank(matrix))
    counts = list(map(len, cells))
    betti = [count - ranks[d] - (ranks[d + 1] if d + 1 < len(cells) else 0)
             for d, count in enumerate(counts)]
    return {"cell_counts": counts, "boundary_ranks": ranks, "betti_numbers": betti,
            "boundary_squared_zero": True}


def verify_model(model):
    axes = list(map(set, model["free_axes"]))
    assert [len(item) for item in axes] == model["singleton_dimensions"]
    assert all(3 <= len(item) < 9 for item in axes)
    assert all(axes[i] - axes[j] for i in range(3) for j in range(3) if i != j)
    pair_axes = [axes[i] & axes[j] for i, j in combinations(range(3), 2)]
    assert list(map(len, pair_axes)) == model["pair_dimensions_in_01_02_12_order"]
    assert all(len(item) > 0 for item in pair_axes)
    triple_axes = set.intersection(*axes)
    assert len(triple_axes) == model["triple_dimension"]
    # Check each intersection separately against the relative n-cube calculation.
    intersections = []
    for size in (1, 2, 3):
        for subset in combinations(range(3), size):
            common = set.intersection(*(axes[i] for i in subset))
            calculation = cubical_cohomology([sorted(common)])
            assert calculation["betti_numbers"] == [0] * len(common) + [1]
            intersections.append({"signature_subset": list(subset), "dimension": len(common),
                                  "relative_betti_numbers": calculation["betti_numbers"]})
    pair_rank = sum(len(item) == 1 for item in pair_axes)
    target_rank = int(len(triple_axes) == 1)
    assert target_rank == model["pair_map_target_rank"]
    differential = model["pair_hc1_to_triple_hc1_matrix"]
    if target_rank:
        # Here every inclusion is literally the identity of the same oriented axis.
        assert all(item == triple_axes for item in pair_axes)
        assert differential == [[1, -1, 1]]
    else:
        assert differential == []
    assert pair_rank - rank(differential) == model["pair_kernel_rank"]
    assert int(not triple_axes) == model["triple_hc0_rank"]
    union = cubical_cohomology(model["free_axes"])
    assert union["cell_counts"] == model["relative_cell_counts_by_degree"]
    assert union["boundary_ranks"] == model["relative_boundary_ranks_by_degree"]
    assert union["betti_numbers"] == model["relative_betti_numbers"]
    assert union["betti_numbers"][2] == model["union_hc2_rank"]
    assert model["union_hc2_rank"] == model["pair_kernel_rank"] + model["triple_hc0_rank"]
    return {"id": model["id"], "all_lower_vanishing_checks": "PASS",
            "proper_pairwise_incomparable_feasibility_loci": "PASS",
            "intersections": intersections, "union_independent_cubical_calculation": union,
            "pair_kernel_rank": model["pair_kernel_rank"],
            "triple_hc0_rank": model["triple_hc0_rank"]}


def main():
    started = time.perf_counter()
    data = json.loads((HERE / "COUNTERMODELS.json").read_text(encoding="utf-8"))
    result = {"status": "PASS", "arithmetic": "exact integers and fractions",
              "polynomial_system": verify_polynomial_system(),
              "models": [verify_model(model) for model in data["models"]],
              "scope": "No actual-parent search, signature-admissibility test, or global source triangulation.",
              "integral_scope": "Cellular matrices are integral; ranks are computed over Q. Integral cohomology claims use the written cube and Mayer-Vietoris proof."}
    result["elapsed_seconds"] = round(time.perf_counter() - started, 6)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
