#!/usr/bin/env python3
"""Exact actual-source witness-face collapse and filtered convex filler.

Standard library only. No producer acceptance imports. Writes only with --write.
Finite scope: chart 0 at the pinned event and its two rational adjacent points.
"""
import argparse
import ast
from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import struct
import zipfile

ROOT = Path(__file__).resolve().parents[3]
OWN = Path(__file__).resolve().parent
TRIPLES = sorted(combinations(range(1, 9), 3), key=lambda x: x[::-1])
BASES = list(combinations(range(1, 9), 4))
SIGS = [14988895318912, 3405195891438080, 40418075143643136]
SUPPORTS = [(0, 19, 21, 37, 38), (0, 9, 27, 30, 35), (0, 11, 17, 24, 40)]
EVENT = Q(37864449186859942661765893, 7029591949415530407677535)
EPS = Q(1, 1000000)


def require(ok, message):
    if not ok:
        raise AssertionError(message)


def det(rows):
    a = [list(map(Q, row)) for row in rows]
    ans = Q(1)
    for c in range(len(a)):
        p = next((r for r in range(c, len(a)) if a[r][c]), None)
        if p is None:
            return Q(0)
        if p != c:
            a[p], a[c] = a[c], a[p]
            ans = -ans
        pivot = a[c][c]
        ans *= pivot
        for r in range(c + 1, len(a)):
            q = a[r][c] / pivot
            for j in range(c + 1, len(a)):
                a[r][j] -= q * a[c][j]
    return ans


def rref(rows):
    a = [list(map(Q, row)) for row in rows]
    pivots = []
    for c in range(len(a[0])):
        r = len(pivots)
        p = next((i for i in range(r, len(a)) if a[i][c]), None)
        if p is None:
            continue
        a[r], a[p] = a[p], a[r]
        q = a[r][c]
        a[r] = [x / q for x in a[r]]
        for i in range(len(a)):
            if i != r:
                q = a[i][c]
                a[i] = [x - q * y for x, y in zip(a[i], a[r])]
        pivots.append(c)
        if len(pivots) == len(a):
            break
    return a, pivots


def normals(y):
    return [[(-1)**(r + 3) * det([[y[k][i - 1] for i in tri]
                for k in range(4) if k != r]) for r in range(4)]
            for tri in TRIPLES]


def signed(n, sig, support):
    return [[(1 if sig >> i & 1 else -1) * x for x in n[i]]
            for i in support]


def normalized_circuit(n, sig, support):
    a = signed(n, sig, support)
    c = [(-1)**j * det(a[:j] + a[j + 1:]) for j in range(5)]
    require(sum(c) != 0, 'normalization denominator')
    w = [x / sum(c) for x in c]
    require(all(sum(w[i] * a[i][j] for i in range(5)) == 0
                for j in range(4)), 'exact circuit kernel')
    return w


def brackets(y):
    return [det([[y[r][i - 1] for i in b] for r in range(4)]) for b in BASES]


def signs(values):
    return [1 if x > 0 else -1 if x < 0 else 0 for x in values]


def load_parent():
    with zipfile.ZipFile(ROOT / 'ai/omreal/data/seeat_parent2599_upper178.npz') as z:
        data = z.read('chart_matrix.npy')
    require(data[:6] == b'\x93NUMPY', 'NPY magic')
    off = 10 if data[6] == 1 else 12
    size = struct.unpack('<H' if off == 10 else '<I', data[8:off])[0]
    header = ast.literal_eval(data[off:off + size].decode())
    require(header['descr'] == '<i8' and not header['fortran_order']
            and header['shape'] == (178, 4, 8), 'source array contract')
    first = struct.unpack('<32q', data[off + size:off + size + 256])
    return [list(first[8*r:8*r + 8]) for r in range(4)]


def matmul(a, b):
    return [[sum(x * y for x, y in zip(row, col)) for col in zip(*b)] for row in a]


def compute():
    pins = json.loads((OWN / 'SOURCE_MANIFEST.json').read_text())['source_sha256']
    for path, digest in pins.items():
        require(sha256((ROOT / path).read_bytes()).hexdigest() == digest,
                'source pin ' + path)
    parent = load_parent()
    event_source = json.loads((ROOT / 'ops/team/d3-satinj-falsifier/DISCOVERED_EVENT.json').read_text())
    require(parent == event_source['parent'] and event_source['signatures'] == SIGS,
            'actual source identity')
    require(Q(event_source['root']) == EVENT, 'event identity')
    base_signs = signs(brackets(parent))
    require(0 not in base_signs, 'uniform source parent')
    records = []
    event_vertices = []
    for name, t in [('left', EVENT - EPS), ('event', EVENT), ('right', EVENT + EPS)]:
        y = [row[:] for row in parent]
        y[1][1] += t
        require(signs(brackets(y)) == base_signs, 'true parent remains uniform')
        n = normals(y)
        circuits = []
        for b, (sig, support) in enumerate(zip(SIGS, SUPPORTS)):
            pair = [normalized_circuit(n, sig, sp)
                    for sp in [support, (2,) + support[1:]]]
            circuits.append(pair)
            if b > 0:
                require(all(w > 0 for p in pair for w in p), 'surviving block circuit')
        union = sorted({0, 2, *SUPPORTS[0][1:]})
        a = signed(n, SIGS[0], union)
        eq = [list(col) for col in zip(*a)] + [[1] * 6]
        reduced, pivots = rref(eq)
        require(len(pivots) == 5, 'six-coordinate affine line')
        if name == 'left':
            require(all(w > 0 for p in circuits[0] for w in p), 'left edge endpoints')
            face = 'closed edge: two distinct circuit vertices'
        elif name == 'right':
            require(all(signs(p) == [-1, 1, 1, 1, 1] for p in circuits[0]),
                    'right endpoint obstruction')
            # The two normalized solutions are distinct and span the affine
            # line. Nonnegative coordinates 0 and 2 force both affine
            # coefficients <= 0, impossible when their sum is 1.
            face = 'empty: affine endpoint coefficients forced nonpositive'
        else:
            event_parent = y
            require(all(signs(p) == [0, 1, 1, 1, 1] for p in circuits[0]),
                    'event endpoint collapse')
            require(circuits[0][0][1:] == circuits[0][1][1:], 'same event vertex')
            free = next(i for i in range(6) if i not in pivots)
            direction = [Q(i == free) for i in range(6)]
            for row, pivot in zip(reduced, pivots):
                direction[pivot] = -row[free]
            require(direction[union.index(0)] * direction[union.index(2)] < 0,
                    'event nonnegative line intersects at one point')
            face = 'singleton: opposite signs in the two zero coordinates'
            for b, support in enumerate(SUPPORTS):
                vertex = [Q(0)] * 168
                for i, w in zip(support, circuits[b][0]):
                    vertex[56*b + i] = w
                event_vertices.append(vertex)
        records.append({'point': name, 'parameter': str(t),
                        'block_0_endpoint_signs': [signs(p) for p in circuits[0]],
                        'six_coordinate_face': face,
                        'blocks_1_and_2_two_circuits_positive': True,
                        'all_70_parent_signs_preserved': True,
                        'augmented_rank': len(pivots)})

    # Genuine joined witnesses on disjoint labeled block coordinates.
    require(len(rref(event_vertices)[1]) == 3, 'affinely independent actual vertices')
    masses = [[sum(v[56*b:56*(b+1)]) for b in range(3)] for v in event_vertices]
    require(masses == [[1, 0, 0], [0, 1, 0], [0, 0, 1]], 'block-mass simplex')
    midpoint = [sum(xs) / 3 for xs in zip(*event_vertices)]
    require(all(x >= 0 for x in midpoint), 'convex filler positivity')
    require([sum(midpoint[56*b:56*(b+1)]) for b in range(3)] == [Q(1, 3)]*3,
            'filler has three positive block masses')
    # Columns e01,e02,e12 and oriented triangle 012.
    d1 = [[-1, -1, 0], [1, 0, -1], [0, 1, 1]]
    d2 = [[1], [-1], [1]]
    require(matmul(d1, d2) == [[0], [0], [0]], 'coherent receiver loop closes')
    require(len(rref(d1)[1]) == 2 and len(rref(d2)[1]) == 1, 'exact simplex ranks')
    hostile = {}
    try:
        require(matmul(d1, [[1], [1], [1]]) == [[0], [0], [0]], 'wrong oriented filler')
    except AssertionError:
        hostile['wrong_boundary_orientation_rejected'] = True
    try:
        require(sum(sum(midpoint[56*b:56*(b+1)]) > 0 for b in range(3)) <= 2,
                'pretend pair-only filler')
    except AssertionError:
        hostile['triple_interior_as_pair_face_rejected'] = True
    try:
        require(any(v == 0 for v in brackets(event_parent)), 'pretend true parent infinity')
    except AssertionError:
        hostile['support_event_as_parent_infinity_rejected'] = True
    require(len(hostile) == 3, 'hostile controls')
    return {'status': 'FINITE_EXACT_FILTERED_COHERENT_FILLER',
            'original_target': 'NULL', 'theorem_credit': 0,
            'opening_revision': 'c27a36d6e3f47a2b4c7bb017774cbe5df30abdc2',
            'classification': 'INFORMATIONAL', 'source_sha256': pins,
            'signatures': SIGS, 'initial_test': records,
            'follow_through': {'model': 'three actual event witnesses and their convex simplex',
                'vertices': [{'block': b, 'support': list(SUPPORTS[b]),
                              'normalized_weights': [str(v[56*b+i]) for i in SUPPORTS[b]]}
                             for b, v in enumerate(event_vertices)],
                'boundary_1': d1, 'boundary_2': d2,
                'pair_face_boundary_H1_Z_rank': 1, 'full_triangle_H1_Z_rank': 0,
                'interior_active_blocks': 3, 'true_parent_infinity': False,
                'new_geometric_mechanism': False,
                'inherited_mechanism': 'convex joined witness carrier'},
            'hostile_controls': hostile,
            'nonconsequences': ['No full 56-row block-0 goodness test.',
                'No obstruction to all possible mixed carriers.',
                'No global pair Hc1 or triple Hc0 calculation.',
                'No filtration-preserving contraction or global parent-boundary attachment.',
                'No coverage denominator, theorem promotion, or ledger mutation.']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = compute()
    if args.write:
        (OWN / 'RESULT.json').write_text(json.dumps(result, indent=2) + '\n')
    else:
        require(result == json.loads((OWN / 'RESULT.json').read_text()), 'frozen result replay')
    print(json.dumps({'status': result['status'], 'original_target': result['original_target'],
                      'theorem_credit': 0, 'pair_face_H1_rank': 1,
                      'filler_active_blocks': 3, 'hostile_controls': 3}))
