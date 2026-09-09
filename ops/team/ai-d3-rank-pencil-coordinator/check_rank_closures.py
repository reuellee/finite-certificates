"""Exact rank-closure audit using only frozen pre-Stage-D certificates.

No active Stage-D producer is read or imported. The parent binding and global
signature admissibility are supplied by the separately accepted Stage C audit.
This checker independently reconstructs raw normals, Cramer rank closures,
full badness circuits, and strict expanded-row separations.
"""
from collections import Counter
from hashlib import sha256
from itertools import combinations, permutations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TRIPLES = tuple(sorted(combinations(range(8), 3), key=lambda t: t[::-1]))
SOURCES = {
    "ops/team/ai-d3-shared-pencil-constructor/OBSTRUCTION.json":
        "77bd316237f6fd7060e964aec1852daa10dfaa065a7d0c4194b0a59929a32afa",
    "ops/team/ai-d3-shared-pencil-falsifier/upper_chart_0_flow.json":
        "83485ff8bb0a1f8cacffdacbf829cbee5898721b008f8bd54ec2a661ca35e6ab",
}


def determinant(matrix):
    total = 0
    for order in permutations(range(len(matrix))):
        sign = (-1) ** sum(order[i] > order[j]
                          for i in range(len(order)) for j in range(i + 1, len(order)))
        term = sign
        for row, col in enumerate(order):
            term *= matrix[row][col]
        total += term
    return total


def in_plane(first, second, third):
    """Membership in the span of two independent 4-vectors, without division."""
    for p, q in combinations(range(4), 2):
        denominator = first[p] * second[q] - first[q] * second[p]
        if denominator:
            alpha = third[p] * second[q] - third[q] * second[p]
            beta = first[p] * third[q] - first[q] * third[p]
            return all(denominator * third[j] == alpha * first[j] + beta * second[j]
                       for j in range(4))
    raise AssertionError("Distinct star rows are proportional")


def main():
    inputs = []
    for path, expected in SOURCES.items():
        data = (ROOT / path).read_bytes()
        assert sha256(data).hexdigest() == expected, path
        inputs.append(json.loads(data))
    constructor, old_falsifier = inputs
    parent, signatures = constructor["parent"], constructor["signatures"]
    assert signatures == [14988895318912, 3405195891438080, 40418075143643136]
    brackets = [determinant([[parent[r][c] for c in basis] for r in range(4)])
                for basis in combinations(range(8), 4)]
    assert len(brackets) == 70 and all(brackets)
    rows = [tuple((-1) ** (coordinate + 3) * determinant(
        [[parent[r][c] for c in triple] for r in range(4) if r != coordinate])
        for coordinate in range(4)) for triple in TRIPLES]
    signed = [[tuple((1 if (sigma >> i) & 1 else -1) * v for v in row)
               for i, row in enumerate(rows)] for sigma in signatures]
    cofactor_signs = []
    for block, witness in enumerate(constructor["full_bad_witnesses"]):
        indices, weights = witness["row_indices"], witness["weights"]
        assert len(indices) == len(set(indices)) == len(weights) == 5
        assert all(w > 0 for w in weights)
        assert all(sum(w * signed[block][i][j] for i, w in zip(indices, weights)) == 0
                   for j in range(4))
        cofactors = [(-1) ** k * determinant([signed[block][i] for j, i in enumerate(indices) if j != k])
                     for k in range(5)]
        assert all(c > 0 for c in cofactors) or all(c < 0 for c in cofactors)
        cofactor_signs.append([1 if c > 0 else -1 for c in cofactors])
    pool = old_falsifier["negative_certificate"]["witness_pool"]
    margins = [[sum(x * y for x, y in zip(row, entry["point"]))
                for row in signed[entry["signature_index"]]] for entry in pool]
    masks = [sum((v > 0) << i for i, v in enumerate(values)) for values in margins]
    sizes, used, unique, count, inequalities, minimum = Counter(), set(), set(), 0, 0, None
    closure_tables = []
    for e in range(8):
        star = tuple(i for i, triple in enumerate(TRIPLES) if e in triple)
        nonstar = tuple(i for i, triple in enumerate(TRIPLES) if e not in triple)
        assert (len(star), len(nonstar)) == (21, 35)
        for pair in combinations(star, 2):
            closure = tuple(i for i in star if in_plane(rows[pair[0]], rows[pair[1]], rows[i]))
            assert set(pair) <= set(closure)
            retained = nonstar + closure
            retained_mask = sum(1 << i for i in retained)
            covering = next((j for j, mask in enumerate(masks) if retained_mask & ~mask == 0), None)
            assert covering is not None, (e + 1, pair, closure)
            values = [margins[covering][i] for i in retained]
            assert all(v > 0 for v in values)
            local_min = min(values)
            minimum = local_min if minimum is None else min(minimum, local_min)
            count += 1
            inequalities += len(retained)
            sizes[len(closure)] += 1
            used.add(covering)
            unique.add((e, closure))
            closure_tables.append([e + 1, list(pair), list(closure), covering])
    assert count == 8 * 210 == 1680
    assert in_plane((1, 0, 0, 0), (0, 1, 0, 0), (2, 3, 0, 0))
    assert not in_plane((1, 0, 0, 0), (0, 1, 0, 0), (2, 3, 1, 0))
    output = {
        "status": "PASS_COMPLETE_FIXED_PLANE_RANK_PREDICATE_COUNTERCERTIFICATE",
        "source_hashes": SOURCES,
        "new_predicate_points": 1,
        "indexed_pairs": count,
        "distinct_labeled_rank_closures": len(unique),
        "closure_size_histogram": dict(sizes),
        "expanded_strict_inequalities": inequalities,
        "existing_separator_pool": len(pool),
        "separator_indices_used": sorted(used),
        "minimum_raw_integer_margin": minimum,
        "three_full_badness_circuits_rank_four": True,
        "cofactor_signs": cofactor_signs,
        "closure_table_sha256": sha256(json.dumps(closure_tables, separators=(",", ":")).encode()).hexdigest(),
        "active_stage_d_producer_read_or_imported": False,
        "scope": "Rank at most two of all incident support normals is impossible for every label at this actual point; no claim about moving support planes, multiple columns, compact components, or D3.",
    }
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
