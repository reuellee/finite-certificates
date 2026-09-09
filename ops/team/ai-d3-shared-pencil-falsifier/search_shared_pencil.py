"""Fixed-cohort discovery. Exact certificate replay is a separate script."""
from fractions import Fraction
from itertools import combinations
from math import gcd, lcm
from pathlib import Path
import json
import sys
import time

sys.dont_write_bytecode = True

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'ai/omreal'))
import DIAG9_GRAPH_exact_topes as topes


def positive_kernel(rows, signature, selected=None, primal_output=None):
    """Exact phase-I simplex, with Bland pivots, for A^t w=0, sum(w)=1."""
    selected = list(range(len(rows))) if selected is None else sorted(selected)
    n = len(selected)
    columns = [tuple((1 if signature >> i & 1 else -1) * v for v in rows[i]) + (1,)
               for i in selected]
    matrix = [[Fraction(columns[j][i]) for j in range(n)] +
              [Fraction(i == j) for j in range(5)] for i in range(5)]
    rhs = [Fraction(0)] * 4 + [Fraction(1)]
    basis = list(range(n, n + 5))
    reduced = [-sum(matrix[i][j] for i in range(5)) for j in range(n)] + [Fraction(0)] * 5
    objective = Fraction(1)
    pivots = 0
    while True:
        entering = next((j for j, value in enumerate(reduced) if value < 0), None)
        if entering is None:
            break
        candidates = [(rhs[i] / matrix[i][entering], basis[i], i)
                      for i in range(5) if matrix[i][entering] > 0]
        assert candidates, 'Phase-I objective cannot be unbounded below.'
        _, _, leaving = min(candidates)
        pivot = matrix[leaving][entering]
        matrix[leaving] = [v / pivot for v in matrix[leaving]]
        rhs[leaving] /= pivot
        for i in range(5):
            if i != leaving:
                multiplier = matrix[i][entering]
                if multiplier:
                    matrix[i] = [a - multiplier * b for a, b in zip(matrix[i], matrix[leaving])]
                    rhs[i] -= multiplier * rhs[leaving]
        coefficient = reduced[entering]
        objective += coefficient * rhs[leaving]
        reduced = [a - coefficient * b for a, b in zip(reduced, matrix[leaving])]
        basis[leaving] = entering
        pivots += 1
        assert pivots < 20000, 'Bland phase-I safety bound reached.'
    if objective:
        if primal_output is not None:
            point = [reduced[n + j] - 1 for j in range(4)]
            denominator = lcm(*(value.denominator for value in point))
            point = [int(value * denominator) for value in point]
            divisor = gcd(*point)
            point = [value // divisor for value in point]
            assert all(sum(column[j] * point[j] for j in range(4)) > 0 for column in columns)
            primal_output.extend(point)
        return None
    weights = [Fraction(0)] * n
    for i, variable in enumerate(basis):
        if variable < n:
            weights[variable] = rhs[i]
    assert sum(weights) == 1 and min(weights) >= 0
    assert all(sum(columns[j][i] * weights[j] for j in range(n)) == 0 for i in range(4))
    denominator = lcm(*(value.denominator for value in weights))
    integers = [int(value * denominator) for value in weights]
    divisor = gcd(*integers)
    return {'support': [selected[j] for j, value in enumerate(integers) if value],
            'weights': [value // divisor for value in integers if value], 'phase_one_pivots': pivots}


def source_cases():
    s = np.load(ROOT / 'ai/omreal/data/seeat_parent2599_shatter8.npz', allow_pickle=False)
    u = np.load(ROOT / 'ai/omreal/data/seeat_parent2599_upper178.npz', allow_pickle=False)
    sigs = [int(s['signature'][i]) for i in (0, 4, 3)]
    return [
        {'id': 'shatter_pattern_0', 'parent': s['pattern_chart'][0].tolist(), 'signatures': sigs},
        {'id': 'upper_chart_7', 'parent': u['chart_matrix'][7].tolist(), 'signatures': sigs},
        {'id': 'upper_chart_0_flow', 'parent': u['chart_matrix'][0].tolist(),
         'signatures': [14988895318912, 3405195891438080, 40418075143643136]},
    ]


def save(data, filename):
    (HERE / filename).write_bytes((json.dumps(data, indent=2) + '\n').encode())


def test_case(case):
    started = time.perf_counter()
    rows = topes.derived_rows(case['parent'])
    case['parent_signs'] = list(topes.parent_signs(case['parent']))
    case['full_dual_witnesses'] = [positive_kernel(rows, s) for s in case['signatures']]
    print(case['id'], 'full dual support sizes',
          [len(w['support']) if w else None for w in case['full_dual_witnesses']], flush=True)
    enumerated = topes.enumerate_topes(rows, dimension=4)
    topes.verify_topes(rows, enumerated)
    case['full_tope_count'] = len(enumerated)
    print(case['id'], 'enumerated and verified', len(enumerated), 'topes', flush=True)
    if any(w is None for w in case['full_dual_witnesses']):
        case['status'] = 'INELIGIBLE'
        case['full_primal_witnesses'] = [list(enumerated[s]) if s in enumerated else None
                                         for s in case['signatures']]
        assert all((w is None) == (s in enumerated)
                   for s, w in zip(case['signatures'], case['full_dual_witnesses']))
        case['elapsed_seconds'] = time.perf_counter() - started
        save(case, case['id'] + '.json')
        return case
    assert all(s not in enumerated for s in case['signatures'])
    full_mask = (1 << 56) - 1
    successes = []
    negative_rows = []
    witness_pool = []
    witness_index = {}
    for e in range(8):
        incident = [i for i, triple in enumerate(topes.TRIPLES) if e in triple]
        incident_mask = sum(1 << i for i in incident)
        nonincident = full_mask ^ incident_mask
        extending = [[(signs, point) for signs, point in enumerated.items()
                      if (signs ^ s) & nonincident == 0] for s in case['signatures']]
        for pair in combinations(incident, 2):
            pair_mask = sum(1 << i for i in pair)
            separator = None
            for block, (s, candidates) in enumerate(zip(case['signatures'], extending)):
                matching = next((p for signs, p in candidates if (signs ^ s) & pair_mask == 0), None)
                if matching is not None:
                    separator = (block, matching)
                    break
            if separator is None:
                successes.append((e + 1, list(pair)))
            else:
                block, point = separator
                key = (block, tuple(point))
                if key not in witness_index:
                    witness_index[key] = len(witness_pool)
                    witness_pool.append({'signature_index': block, 'point': list(point)})
                negative_rows.append([e + 1, pair[0], pair[1], witness_index[key]])
    assert len(successes) + len(negative_rows) == 1680
    case['successful_pair_count'] = len(successes)
    case['excluded_pair_count'] = len(negative_rows)
    case['successful_pairs'] = successes
    if successes:
        if case['id'] == 'shatter_pattern_0':
            wanted = {tuple(int(x) - 1 for x in name) for name in ('134', '127')}
            pair = sorted(i for i, triple in enumerate(topes.TRIPLES) if triple in wanted)
            e = 1
            assert (e, pair) in successes
        else:
            e, pair = successes[0]
        selected = [i for i, triple in enumerate(topes.TRIPLES) if e - 1 not in triple or i in pair]
        duals = [positive_kernel(rows, s, selected) for s in case['signatures']]
        assert all(duals)
        case['status'] = 'POSITIVE_INSTANCE'
        case['positive_certificate'] = {'label': e, 'incident_pair': pair, 'duals': duals}
    else:
        case['status'] = 'NEGATIVE_POINTWISE_INSTANCE'
        case['negative_certificate'] = {'witness_pool': witness_pool, 'coverage_rows': negative_rows}
    case['elapsed_seconds'] = time.perf_counter() - started
    save(case, case['id'] + '.json')
    print(case['id'], case['status'], 'successful', len(successes), 'excluded', len(negative_rows),
          'elapsed', case['elapsed_seconds'], flush=True)
    return case


if __name__ == '__main__':
    for case in source_cases():
        if len(sys.argv) > 1 and case['id'] not in sys.argv[1:]:
            continue
        result = test_case(case)
        if result['status'] == 'NEGATIVE_POINTWISE_INSTANCE':
            print('STOP discovery at first complete local negative; admissibility binding still required.', flush=True)
            break
