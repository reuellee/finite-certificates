#!/usr/bin/env python3
"""Independent exact replay of an auxiliary, generic same-factor theorem.

No repository producer is imported. Standard-library determinants anchor the
line model to one actual uniform parent. The global six-kind reduction remains
the explicitly pinned existing theorem; this does not replay that census.
"""

from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations, product
from pathlib import Path
import json


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
EDGES = tuple(combinations(range(6), 2))


def determinant(matrix):
    rows = [list(row) for row in matrix]
    if not rows:
        return Q(1)
    return sum((-1) ** j * x * determinant(
        [r[:j] + r[j + 1:] for r in rows[1:]])
        for j, x in enumerate(rows[0]))


def rank(matrix):
    rows = [[Q(x) for x in row] for row in matrix]
    r = 0
    for j in range(len(rows[0])):
        p = next((i for i in range(r, len(rows)) if rows[i][j]), None)
        if p is None:
            continue
        rows[r], rows[p] = rows[p], rows[r]
        v = rows[r][j]
        rows[r] = [x / v for x in rows[r]]
        for i in range(len(rows)):
            if i != r:
                v = rows[i][j]
                rows[i] = [x - v * y for x, y in zip(rows[i], rows[r])]
        r += 1
        if r == len(rows):
            break
    return r


def positive_relation(vectors, signing):
    """Four rank-three vectors in R^3 or R^4, all circuit entries nonzero."""
    if rank(vectors) != 3:
        raise AssertionError("circuit is not rank three")
    for coords in combinations(range(len(vectors[0])), 3):
        c = [(-1) ** j * determinant([
            [vectors[i][k] for k in coords]
            for i in range(4) if i != j]) for j in range(4)]
        if not any(c):
            continue
        if not all(c):
            raise AssertionError("generic circuit support has shrunk")
        for k in range(len(vectors[0])):
            assert sum(c[j] * vectors[j][k] for j in range(4)) == 0
        c = [x * (1 if signing >> j & 1 else -1) for j, x in enumerate(c)]
        return all(x > 0 for x in c) or all(x < 0 for x in c)
    raise AssertionError("no nonzero circuit minor")


def pattern(gap, signing):
    """Derived from exact coefficients for p+q+(signed outer sum)=0."""
    w = Q(2 * gap - 1, 2)
    out = 0
    for k, (i, j) in enumerate(EDGES):
        required_i = w > j
        required_j = i > w
        if bool(signing >> i & 1) == required_i and bool(signing >> j & 1) == required_j:
            out |= 1 << k
    return out


def triangle_boundary(tri):
    a, b, c = tri
    return {(b, c): 1, (a, c): -1, (a, b): 1}


def oriented_triangle(tri):
    inversion = sum(tri[i] > tri[j] for i in range(3) for j in range(i + 1, 3))
    return tuple(sorted(tri)), (-1) ** inversion


def chain_boundary(chain):
    out = {}
    for tri, coefficient in chain.items():
        for edge, c in triangle_boundary(tri).items():
            out[edge] = out.get(edge, 0) + c * coefficient
    return {e: c for e, c in out.items() if c}


def matching_fillers(mask):
    active = tuple(k for k in range(15) if mask >> k & 1)
    output = []
    for tri in combinations(active, 3):
        if len(set().union(*(set(EDGES[k]) for k in tri))) != 6:
            continue
        h = next((k for k in active if k not in tri), None)
        if h is None:
            raise AssertionError("matching triangle has no active fourth edge")
        a, b, c = tri
        chain = {}
        for face in ((a, b, h), (b, c, h), (c, a, h)):
            assert len(set().union(*(set(EDGES[k]) for k in face))) <= 5
            key, coefficient = oriented_triangle(face)
            chain[key] = chain.get(key, 0) + coefficient
        assert chain_boundary(chain) == triangle_boundary(tri)
        output.append((tri, h, chain))
    return output


def check_closure(single, double):
    if double != {a & b for a in single for b in single}:
        raise AssertionError("pair-pattern family changed")
    if any((a & b) not in double for a in double for b in single):
        raise AssertionError("intersection family is not closed")


def actual_parent_anchor():
    values = []
    for index in range(9):
        payload = f"diag2-canonical-edge-v1:38:1:{index}".encode("ascii")
        value = int.from_bytes(sha256(payload).digest()[:4], "big") % 67 - 33
        values.append(Q(value + 7 if value in (-1, 0, 1) else value))
    _, b, c, d, e, f, g, h, i = values
    slope = e * i - f * h
    assert slope
    constant = -b*d*i + b*f*g - b*f + b*i + c*d*h - c*e*g + c*e - c*h - e*i + f*h
    values[0] = -constant / slope
    a = values[0]
    columns = ((1,0,0,0), (0,1,0,0), (0,0,1,0), (0,0,0,1),
               (1,1,1,1), (1,a,b,c), (1,d,e,f), (1,g,h,i))
    brackets = [determinant([columns[j] for j in basis])
                for basis in combinations(range(8), 4)]
    assert len(brackets) == 70 and all(brackets)
    triples = tuple(sorted(combinations(range(8), 3), key=lambda x: x[::-1]))
    normals = []
    for tri in triples:
        normals.append(tuple((-1) ** k * determinant([
            [columns[j][l] for l in range(4) if l != k] for j in tri])
            for k in range(4)))
    core = (9, 55)
    line_order = (0, 4, 10, 35, 1, 20)
    assert tuple(triples[j] for j in core) == ((2,3,4), (5,6,7))
    assert all(set((0,1)).issubset(triples[j]) for j in line_order)
    assert rank([normals[j] for j in line_order]) == 2
    assert rank([normals[j] for j in core + line_order]) == 3
    direct = set()
    for word in range(256):
        mask = 0
        for k, (u, v) in enumerate(EDGES):
            positions = (0, 1, 2 + u, 2 + v)
            signed = sum(((word >> p) & 1) << z for z, p in enumerate(positions))
            rows = [normals[j] for j in (core[0], core[1], line_order[u], line_order[v])]
            if positive_relation(rows, signed):
                mask |= 1 << k
        direct.add(mask)
    expected = {pattern(1, word) for word in range(64)}
    assert direct == expected and len(direct) == 58
    return {"coordinates": list(map(str, values)), "parent_brackets_nonzero": 70,
            "outer_rank": 2, "all_eight_rank": 3, "direct_signings": 256,
            "active_patterns": 58, "gap": 1}


def check_scope(scope):
    required = {"generic_supported_factor_only": True, "rank_two_pencil_required": True,
                "arbitrary_signings": True, "global_pair_map_proved": False,
                "source_orbits_removed": 0, "diagonals_proved": 2}
    if scope != required:
        raise AssertionError("the finite computation does not support that scope")


def expect_failure(fn):
    try:
        fn()
    except AssertionError:
        return
    raise AssertionError("hostile control was incorrectly accepted")


def main():
    manifest = json.loads((HERE / "SOURCE_MANIFEST.json").read_text())
    for name, digest in manifest["sources"].items():
        assert sha256((ROOT / name).read_bytes()).hexdigest() == digest, name
    scope = {"generic_supported_factor_only": True, "rank_two_pencil_required": True,
             "arbitrary_signings": True, "global_pair_map_proved": False,
             "source_orbits_removed": 0, "diagonals_proved": 2}
    check_scope(scope)
    total = set()
    tables = []
    all_fillers = []
    for gap in range(7):
        w = Q(2 * gap - 1, 2)
        p, q = (0,0,1), (1,w,-1)
        for signing in range(64):
            direct = 0
            for k, (i,j) in enumerate(EDGES):
                bits = 3 | (((signing >> i) & 1) << 2) | (((signing >> j) & 1) << 3)
                if positive_relation((p,q,(1,i,0),(1,j,0)), bits):
                    direct |= 1 << k
            assert direct == pattern(gap, signing)
        single = {pattern(gap, s) for s in range(64)}
        double = {a & b for a in single for b in single}
        assert len(single) == 58 and len(double) == 180
        check_closure(single, double)
        # All ternary bit words are audited at each endpoint. The proof for
        # arbitrarily many words is the consensus-bit identity in FINDINGS.
        words = [pattern(gap,s) for s in range(64)]
        for a,b,c in product(range(64), repeat=3):
            synthesized = a ^ ((a ^ b) | (a ^ c))
            assert words[a] & words[b] & words[c] == words[a] & words[synthesized]
        fillers = [item for mask in sorted(double) for item in matching_fillers(mask)]
        all_fillers.extend(fillers)
        total.update(double)
        raw = json.dumps(sorted(double), separators=(",", ":")).encode()
        tables.append({"gap": gap, "single": 58, "double": 180,
                       "arbitrary_finite_intersections": 180,
                       "matching_triangles_filled": len(fillers),
                       "double_masks_sha256": sha256(raw).hexdigest()})
    assert len(total) == 487 and len(all_fillers) == 105
    anchor = actual_parent_anchor()
    # Old theorem's 58/180/487/105 counts are exactly retained; this proof
    # changes the number of permitted block signings, not the pattern family.
    expect_failure(lambda: check_closure(single, double - {0}))
    a,b,c = next(tri for tri in combinations(range(15), 3)
                 if len(set(EDGES[tri[0]]) | set(EDGES[tri[1]]) | set(EDGES[tri[2]])) == 6)
    expect_failure(lambda: matching_fillers((1<<a) | (1<<b) | (1<<c)))
    tri, _, chain = all_fillers[0]
    broken = dict(chain)
    face = next(iter(broken))
    broken[face] *= -1
    expect_failure(lambda: assert_same_boundary(broken, tri))
    expect_failure(lambda: check_scope({**scope, "global_pair_map_proved": True}))
    expect_failure(lambda: check_scope({**scope, "generic_supported_factor_only": False}))
    # Two synthetic signings need not be two members of the original family.
    family = (8,25,26)
    patterns = [pattern(0,s) for s in family]
    common = patterns[0] & patterns[1] & patterns[2]
    assert common == 512
    assert all(patterns[i] & patterns[j] != common for i,j in combinations(range(3),2))
    assert pattern(0,8) & pattern(0,27) == common
    result = {"status": "PASS_AUXILIARY_EXACT_REPLAY", "original_pair_target": "INCONCLUSIVE",
              "scope": scope, "tables": tables, "all_gap_distinct_patterns": 487,
              "matching_triangles_filled": 105, "actual_parent_anchor": anchor,
              "synthetic_not_original_canary": {"gap":0,"words":list(family),
                "patterns":patterns,"intersection":common,"synthetic_pair":[8,27]},
              "hostile_controls_rejected":5}
    print(json.dumps(result, indent=2, sort_keys=True))


def assert_same_boundary(chain, tri):
    assert chain_boundary(chain) == triangle_boundary(tri)


if __name__ == "__main__":
    main()
