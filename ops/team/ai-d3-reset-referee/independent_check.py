#!/usr/bin/env python3
"""Independent finite certificate for frozen generic countermodel 96d2cafd.

No producer code is imported or executed. Algebra uses exact rational
interpolation with explicit degree bounds, rather than a sparse polynomial
implementation. Topological acyclicity uses an integral chain contraction
of cubical compact-relative models, rather than rational matrix ranks.
The global topology and the degree-bound justification are in REVIEW.md.
"""

from fractions import Fraction as F
from hashlib import sha256
from itertools import combinations, product
from pathlib import Path
import json
import subprocess
import time

CANDIDATE = "96d2cafda5c3588d0754780d18b92c694a843b54"
PINS = {
    "ops/team/ai-d3-reset-coordinator/FULL_DIMENSIONAL_COUNTERMODEL.md":
        "29080bd9199295747216dc7f6b619822dfa05d009d2b56accd76b61c35a3d963",
    "ops/team/ai-d3-reset-coordinator/check_full_dimensional_countermodel.py":
        "0cd93fcbf892ebf6969b9983c5055ecca03bb0d1ff15a413a8bcd0c2b7a6927c",
    "ops/research-team/cycles/2026-09-04-d3-block-gordan-compact-relative-source-gate1/THEOREM_CANDIDATE.md":
        "fa26329cb30866a6c127f2b789a1a818f61c3d951aac57ae1ba2b558cd42c56a",
    "ai/omreal/BLOCK_GORDAN_AUDIT.md":
        "5fae5f8cfb301fdec171d79fcd6974899f78341996a73f5e0f5ed13f2ec7bc0a",
    "ai/omreal/ATLAS_HELLY.md":
        "9a1c2791c9b991679587d0a9ba6307191e025069b766b55855bfa0d1357071f0",
    "ops/research-team/cycles/2026-09-05-ai-only-d3-structural-reset/CYCLE.md":
        "e3ce6f7110b13a46e0831fe8c2344ad865ada17d9fa70d03383fd654bd287dea",
    "ops/research-team/cycles/2026-09-05-ai-only-d3-structural-reset/WORK_ORDERS.yaml":
        "2ec4b8edc27946a84adef1f122261cb41db066e6481c3cdee2864e9725534a0a",
}


def demand(condition, message):
    if not condition:
        raise AssertionError(message)


def source_pins():
    root = Path(__file__).resolve().parents[3]
    records = {}
    for path, expected in PINS.items():
        contents = subprocess.check_output(
            ["git", "show", CANDIDATE + ":" + path], cwd=root)
        actual = sha256(contents).hexdigest()
        demand(actual == expected, "frozen Git source hash changed: " + path)
        local = (root / path).read_bytes()
        demand(local.replace(b"\r\n", b"\n") == contents.replace(b"\r\n", b"\n"),
               "worktree source differs from frozen source: " + path)
        records[path] = {
            "git_blob_sha256": actual,
            "worktree_bytes_sha256": sha256(local).hexdigest(),
            "git_blob_id": subprocess.check_output(
                ["git", "rev-parse", CANDIDATE + ":" + path], cwd=root,
                text=True).strip(),
        }
    return records


def determinant_by_elimination(rows):
    a = [[F(v) for v in row] for row in rows]
    det = F(1)
    for c in range(len(a)):
        pivot = next((r for r in range(c, len(a)) if a[r][c]), None)
        if pivot is None:
            return F(0)
        if pivot != c:
            a[c], a[pivot] = a[pivot], a[c]
            det = -det
        value = a[c][c]
        det *= value
        for r in range(c + 1, len(a)):
            multiple = a[r][c] / value
            for j in range(c, len(a)):
                a[r][j] -= multiple * a[c][j]
    return det


def unsigned_columns(g):
    columns = [[F(0)] * 56 for _ in range(4)]
    for j in range(3):
        columns[j][2*j:2*j+2] = [F(1), F(-1)]
    columns[3] = [F(v) for v in g for _ in range(2)] + [F(1)] * 50
    return columns


def signed_columns(g, active, corrupt=False):
    columns = unsigned_columns(g)
    negative = {2*j + 1 for j in range(3) if j != active}
    if corrupt:
        negative.add(2*active + 1)
    return [[-a if r in negative else a for r, a in enumerate(col)]
            for col in columns]


def algebra_certificate(corrupt=False):
    # Each identity below is polynomial in independent g0,g1,g2,
    # with degree at most three in each variable. Four distinct values
    # per variable are a complete interpolation certificate, not sampling.
    nodes = tuple(map(F, (-2, -1, 0, 1)))
    for g in product(nodes, repeat=3):
        cols = unsigned_columns(g)
        selected = [[col[r] for col in cols] for r in (0, 2, 4, 6)]
        demand(determinant_by_elimination(selected) == 1, "rank-four minor")
        demand(all(any(col[r] for col in cols) for r in range(56)), "nonzero rows")
        for i in range(3):
            signed = signed_columns(g, i, corrupt)
            p = [F(0) if j == i else g[j]**2 + 1 for j in range(3)] + [F(1)]
            margins = [sum(signed[j][r] * p[j] for j in range(4)) for r in range(56)]
            for r, margin in enumerate(margins):
                if r >= 6:
                    expected = F(1)
                elif r // 2 == i:
                    expected = g[i]
                else:
                    v = g[r // 2]
                    expected = (v + F(1 if r % 2 == 0 else -1, 2))**2 + F(3, 4)
                demand(margin == expected, "signed primal/completed-square identity")

            # Independent fiber reconstruction: first three coordinate
            # equations are difference of active weights, sum of each
            # inactive pair. Nonnegativity forces each inactive pair zero.
            for j in range(3):
                target = [F(0)] * 56
                target[2*j:2*j+2] = [F(1), F(-1 if j == i else 1)]
                demand(signed[j] == target, "fiber support equations")

            # Independent normalized section distributes padding mass
            # uniformly, unlike the producer's single-padding-row section.
            # Clear positive denominator 2(1-g_i) before checking.
            numerators = [F(0)] * 56
            numerators[2*i:2*i+2] = [F(1), F(1)]
            numerators[6:] = [F(-g[i], 25)] * 50
            demand(sum(numerators) == 2*(1-g[i]), "fiber mass identity")
            demand(all(sum(col[r]*numerators[r] for r in range(56)) == 0
                       for col in signed), "uniform-padding kernel section")
            if g[i] <= 0:
                demand(2*(1-g[i]) > 0 and min(numerators) >= 0, "section positivity")
    return {"independent_parameter_grid_size": 64, "coordinatewise_degree_bound": 3}


def quadratic_nodes(n):
    # For total degree <=2, values at z, z+e_i, z+2e_i,
    # z+e_i+e_j determine every coefficient. Here z=(1,0,...,0)
    # keeps the homogenizing coordinate strictly positive.
    origin = [F(0)] * n
    origin[0] = F(1)
    yield origin
    for i in range(n):
        for amount in (1, 2):
            point = origin[:]
            point[i] += amount
            yield point
    for i, j in combinations(range(n), 2):
        point = origin[:]
        point[i] += 1
        point[j] += 1
        yield point


def functions_at(x, y, u):
    return [-x, -y, x+y+sum(v*v for v in u)-1]


def geometry_certificate(corrupt=False):
    # Chart identities have degree <=1 in x,y,s,z, where s is an
    # independent placeholder for sum(u_j^2). This covers every actual u.
    for x, y, s, z in product(map(F, (0, 1)), repeat=4):
        inverse_y = (0 if corrupt else 1) - x - s - z
        inverse_x = 1 - y - s - z
        demand(x + inverse_y + s - 1 == -z, "02 chart")
        demand(inverse_x + y + s - 1 == -z, "12 chart")
        demand(1-x-inverse_y-s == z, "02 inverse")
        demand(1-inverse_x-y-s == z, "12 inverse")
    # Scaling identity proves contraction of triple towards the origin.
    for x, y, s, h in product(map(F, (0, 1, 2)), repeat=4):
        demand(h*x+h*y+h*h*s == h*(x+y+s)-h*(1-h)*s,
               "triple contraction")
    anchors = [(1, -1, 2), (-1, 1, 2), (-1, -1, 0)]
    for i, (x, y, u0) in enumerate(anchors):
        bad = [g <= 0 for g in functions_at(F(x), F(y), [F(u0)]+[F(0)]*6)]
        demand(bad == [j == i for j in range(3)], "exclusive-bad anchor")
    demand(min(functions_at(F(-1), F(-1), [F(2)]+[F(0)]*6)) > 0,
           "common feasibility")
    demand(max(functions_at(F(1,4), F(1,4), [F(0)]*7)) < 0,
           "full-dimensional triple")
    count = 0
    for point in quadratic_nodes(10):
        t, X, Y, *U = point
        original = functions_at(X/t, Y/t, [v/t for v in U])
        extension = [-X*t, -Y*t, (X+Y)*t+sum(v*v for v in U)-t*t]
        demand([t*t*g for g in original] == extension, "homogeneous degree-two extension")
        count += 1
    demand(count == 66, "quadratic interpolation dimension")
    return {"compactification_unisolvent_nodes": count, "total_degree_bound": 2}


def add_chains(*chains):
    answer = {}
    for chain in chains:
        for cell, coefficient in chain.items():
            answer[cell] = answer.get(cell, 0) + coefficient
    return {cell: coefficient for cell, coefficient in answer.items() if coefficient}


def apply_operator(chain, operator):
    return add_chains(*({b: coefficient*v for b, v in operator(a).items()}
                        for a, coefficient in chain.items()))


def cubical_contraction(m, k, corrupt=False):
    # Cube [0,1]^(m+k), relative to both endpoint faces in its first m
    # coordinates and upper endpoint faces in its last k coordinates.
    # Surviving cells: E^m followed by L (lower vertex) or E (open edge).
    # Full cubical boundary is upper minus lower, with product signs;
    # upper faces and Euclidean endpoint faces are then quotiented out.
    cells = [tuple("E"*m) + tail for tail in product("LE", repeat=k)]

    def boundary(cell):
        answer = {}
        for j in range(m, m+k):
            if cell[j] == "E":
                lower = cell[:j] + ("L",) + cell[j+1:]
                answer[lower] = -(-1)**cell[:j].count("E")
        return answer

    def contraction(cell):
        if cell[m] == "E":
            return {}
        lifted = cell[:m] + ("E",) + cell[m+1:]
        return {lifted: (-1)**(m+1) * (2 if corrupt else 1)}

    for cell in cells:
        demand(apply_operator(boundary(cell), boundary) == {}, "integral boundary squared")
        lhs = add_chains(apply_operator(contraction(cell), boundary),
                         apply_operator(boundary(cell), contraction))
        demand(lhs == {cell: 1}, "integral d h + h d = identity")
    return {"euclidean_factors": m, "halfline_factors": k,
            "cell_counts_by_degree": {str(d): sum(c.count("E") == d for c in cells)
                                      for d in range(m, m+k+1)},
            "integer_chain_contraction": True}


def labeled_minor_certificate():
    labels = tuple(combinations(range(1, 9), 3))
    selected = [labels[r] for r in (0, 2, 4, 6)]
    demand(selected == [(1,2,3), (1,2,5), (1,2,7), (1,3,4)], "lexicographic labels")
    demand(set.intersection(*(set(t) for t in selected)) == {1}, "common label")
    # Structural elementary row operations: subtract g0,g1,g2 times
    # fourth row from rows 0,2,4; the resulting minor is I_4.
    # For any parent normal n_I(v)=det(y_i,y_j,y_k,v), setting v=y_1
    # repeats a column. These four rows must annihilate nonzero y_1.
    return {"zero_based_rows": [0,2,4,6], "triples": selected,
            "common_label": 1, "determinant": 1,
            "scope": "specified labeled parent origin only"}


def main():
    start = time.perf_counter()
    result = {"format": "independent-generic-countermodel-check-v1",
              "reviewed_candidate": CANDIDATE, "source_hashes": source_pins(),
              "producer_code_executed_or_imported": False}
    result["algebra"] = algebra_certificate()
    result["geometry"] = geometry_certificate()
    result["integral_relative_complexes"] = [cubical_contraction(8,1), cubical_contraction(7,2)]
    result["labeled_minor"] = labeled_minor_certificate()
    hostile = [lambda: algebra_certificate(True), lambda: geometry_certificate(True),
               lambda: cubical_contraction(8,1,True), lambda: cubical_contraction(7,2,True)]
    rejected = 0
    for test in hostile:
        try:
            test()
        except AssertionError:
            rejected += 1
    demand(rejected == len(hostile), "mutated finite certificate escaped")
    result["hostile_mutations_rejected"] = rejected
    result["status"] = "PASS_FINITE_CERTIFICATES"
    result["global_topology_proof"] = "REVIEW.md; not a machine formalization"
    result["elapsed_seconds"] = round(time.perf_counter()-start, 6)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
