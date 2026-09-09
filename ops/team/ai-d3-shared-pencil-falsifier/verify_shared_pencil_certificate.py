"""Search-independent integer verification of the fixed-cohort certificates.

No tope enumeration, LP/simplex, circuit search, or producer import occurs.
NumPy is used only to bind the copied matrices to the frozen NPZ inputs.
"""
from itertools import combinations
from math import gcd
from pathlib import Path
import hashlib
import json
import time

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
TRIPLES = tuple(sorted(combinations(range(1, 9), 3), key=lambda x: x[::-1]))
BASES = tuple(sorted(combinations(range(1, 9), 4), key=lambda x: x[::-1]))
TRIPLE_INDEX = {item: i for i, item in enumerate(TRIPLES)}


def determinant(matrix):
    """Bareiss integer determinant, independently implemented from the search."""
    a = [list(map(int, row)) for row in matrix]
    n = len(a)
    if n == 0:
        return 1
    parity, previous = 1, 1
    for k in range(n - 1):
        pivot_row = next((i for i in range(k, n) if a[i][k]), None)
        if pivot_row is None:
            return 0
        if pivot_row != k:
            a[k], a[pivot_row] = a[pivot_row], a[k]
            parity = -parity
        pivot = a[k][k]
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                numerator = pivot * a[i][j] - a[i][k] * a[k][j]
                assert numerator % previous == 0
                a[i][j] = numerator // previous
            a[i][k] = 0
        previous = pivot
    return parity * a[-1][-1]


def parent_data(parent, expected_signs):
    assert len(parent) == 4 and all(len(row) == 8 for row in parent)
    assert all(type(value) is int for row in parent for value in row)
    determinants = [determinant([[parent[r][label - 1] for label in basis]
                                  for r in range(4)]) for basis in BASES]
    assert all(determinants), 'Nonuniform parent.'
    signs = ''.join('+' if value > 0 else '-' for value in determinants)
    assert signs == expected_signs, 'Parent chirotope is not catalog row 2599.'
    rows = []
    for triple in TRIPLES:
        normal = [(-1) ** (r + 3) * determinant(
            [[parent[q][label - 1] for label in triple] for q in range(4) if q != r])
                  for r in range(4)]
        divisor = gcd(*(abs(value) for value in normal))
        assert divisor > 0
        rows.append(tuple(value // divisor for value in normal))
    return rows, determinants


def sign(signature, row):
    assert type(signature) is int and 0 <= signature < (1 << 56)
    return 1 if signature & (1 << row) else -1


def verify_primal(rows, signature, point, selected=None):
    assert len(point) == 4 and all(type(value) is int for value in point)
    selected = range(56) if selected is None else selected
    margins = [sign(signature, i) * sum(a * b for a, b in zip(rows[i], point)) for i in selected]
    assert margins and min(margins) > 0, 'Invalid strict primal separator.'
    return min(margins)


def verify_dual(rows, signature, witness, selected=None):
    assert witness is not None
    support, weights = witness['support'], witness['weights']
    assert len(support) == len(weights) and support
    assert len(set(support)) == len(support)
    assert all(type(i) is int and 0 <= i < 56 for i in support)
    assert all(type(w) is int and w > 0 for w in weights)
    if selected is not None:
        assert set(support) <= set(selected), 'Dual uses a deleted row.'
    assert all(sum(w * sign(signature, i) * rows[i][r] for i, w in zip(support, weights)) == 0
               for r in range(4)), 'Gordan equation does not vanish exactly.'
    return len(support)


def verify_gp(parent_signs, signature):
    parent_lookup = {basis: 1 if value == '+' else -1 for basis, value in zip(BASES, parent_signs)}
    def chi(sequence):
        parity = (-1) ** sum(sequence[i] > sequence[j]
                             for i in range(4) for j in range(i + 1, 4))
        basis = tuple(sorted(sequence))
        return parity * (sign(signature, TRIPLE_INDEX[basis[:3]]) if basis[-1] == 9
                         else parent_lookup[basis])
    checked = 0
    for lam in combinations(range(1, 10), 2):
        rest = [i for i in range(1, 10) if i not in lam]
        for a, b, c, d in combinations(rest, 4):
            terms = (chi(lam + (a, b)) * chi(lam + (c, d)),
                     -chi(lam + (a, c)) * chi(lam + (b, d)),
                     chi(lam + (a, d)) * chi(lam + (b, c)))
            assert len(set(terms)) == 2, 'Extension signature violates a GP relation.'
            checked += 1
    assert checked == 1260
    return checked


def restricted_rows(label, pair):
    assert 1 <= label <= 8 and len(pair) == 2 and pair[0] < pair[1]
    assert all(label in TRIPLES[i] for i in pair)
    selected = [i for i, triple in enumerate(TRIPLES) if label not in triple or i in pair]
    assert len(selected) == 37
    return selected


def verify_case(case, original_parent, expected_signs):
    assert case['parent'] == original_parent.tolist(), 'Copied parent differs from frozen NPZ case.'
    rows, determinants = parent_data(case['parent'], expected_signs)
    assert case['parent_signs'] == [1 if x > 0 else -1 for x in determinants]
    gp_counts = [verify_gp(expected_signs, signature) for signature in case['signatures']]
    full_dual_sizes = []
    for signature, dual in zip(case['signatures'], case['full_dual_witnesses']):
        full_dual_sizes.append(verify_dual(rows, signature, dual) if dual else None)
    result = {'id': case['id'], 'status': case['status'], 'parent_brackets_checked': 70,
              'gp_relations_per_signature': gp_counts, 'full_dual_support_sizes': full_dual_sizes}
    if case['status'] == 'INELIGIBLE':
        good = []
        for i, (signature, dual, point) in enumerate(zip(case['signatures'],
                    case['full_dual_witnesses'], case['full_primal_witnesses'])):
            if dual is None:
                verify_primal(rows, signature, point)
                good.append(i)
            else:
                assert point is None
        assert good
        result['feasible_signature_indices'] = good
        return result
    assert all(case['full_dual_witnesses'])
    if case['status'] == 'POSITIVE_INSTANCE':
        certificate = case['positive_certificate']
        selected = restricted_rows(certificate['label'], certificate['incident_pair'])
        for signature, dual in zip(case['signatures'], certificate['duals']):
            verify_dual(rows, signature, dual, selected)
        result['label'] = certificate['label']
        result['incident_triples'] = [TRIPLES[i] for i in certificate['incident_pair']]
        result['scope'] = 'One directly verified success; search-reported exhaustive success count is not assumed.'
        return result
    assert case['status'] == 'NEGATIVE_POINTWISE_INSTANCE'
    certificate = case['negative_certificate']
    pool = certificate['witness_pool']
    required = {(e, i, j) for e in range(1, 9)
                for i, j in combinations([k for k, triple in enumerate(TRIPLES) if e in triple], 2)}
    assert len(required) == 1680
    seen = set()
    usage = [0, 0, 0]
    minima = []
    for label, i, j, witness_index in certificate['coverage_rows']:
        key = (label, i, j)
        assert key in required and key not in seen
        assert type(witness_index) is int and 0 <= witness_index < len(pool)
        witness = pool[witness_index]
        block = witness['signature_index']
        assert type(block) is int and 0 <= block < 3
        selected = restricted_rows(label, (i, j))
        minima.append(verify_primal(rows, case['signatures'][block], witness['point'], selected))
        seen.add(key)
        usage[block] += 1
    assert seen == required
    result.update({'all_restrictions_excluded': len(seen), 'strict_inequalities_checked': 1680 * 37,
                   'witness_pool_size': len(pool), 'signature_usage': usage,
                   'minimum_integer_margin': min(minima),
                   'scope': 'Exhaustive pointwise negative proved by strict integer separators, independent of enumeration.'})
    return result


def verify_shatter_admissibility(source, signatures, expected_signs):
    expected = [int(source['signature'][i]) for i in (0, 4, 3)]
    assert signatures == expected
    results = []
    for block, bit in enumerate((0, 4, 3)):
        pattern = 1 << bit
        parent = source['pattern_chart'][pattern].tolist()
        rows, _ = parent_data(parent, expected_signs)
        point = list(map(int, source['feasible_point'][pattern, bit]))
        verify_primal(rows, signatures[block], point)
        others = []
        # Stored weights multiply raw normals, so multiply each weight by the
        # positive row gcd before testing against primitive normals.
        raw = []
        for triple in TRIPLES:
            raw.append([(-1) ** (r + 3) * determinant(
                [[parent[q][label - 1] for label in triple] for q in range(4) if q != r])
                        for r in range(4)])
        for other_block, other_bit in enumerate((0, 4, 3)):
            if other_block == block:
                continue
            weights = [int(value) * gcd(*(abs(v) for v in normal))
                       for value, normal in zip(source['gordan_weight'][pattern, other_bit], raw)]
            dual = {'support': [i for i, w in enumerate(weights) if w],
                    'weights': [w for w in weights if w]}
            verify_dual(rows, signatures[other_block], dual)
            others.append(other_block)
        results.append({'feasible_signature_index': block, 'bad_other_indices': others,
                        'shatter_pattern': pattern, 'parent_brackets_checked': 70})
    return results


def verify_flow_admissibility(data, upper, signatures, expected_signs):
    assert len(data['records']) == 3
    checked = []
    for block, record in enumerate(data['records']):
        assert record['signature'] == signatures[block]
        index = record['upper_point_index']
        chart = record['upper_chart_index']
        assert int(upper['assignment'][index]) == chart
        assert record['parent'] == upper['chart_matrix'][chart].tolist()
        assert record['point'] == list(map(int, upper['point'][index]))
        rows, _ = parent_data(record['parent'], expected_signs)
        verify_primal(rows, signatures[block], record['point'])
        assert len(record['other_systems']) == 3
        bad = []
        for other, system in enumerate(record['other_systems']):
            assert system['signature'] == signatures[other]
            if other == block:
                assert system['dual'] is None
                verify_primal(rows, signatures[other], system['primal'])
            else:
                verify_dual(rows, signatures[other], system['dual'])
                bad.append(other)
        checked.append({'feasible_signature_index': block, 'bad_other_indices': bad,
                        'upper_chart': chart, 'stored_point_index': index,
                        'parent_brackets_checked': 70})
    return checked


def main():
    started = time.perf_counter()
    catalog_path = ROOT / 'ai/omgamma/data/cat_4_8.txt'
    catalog = [line.strip() for line in catalog_path.read_text().splitlines() if line.strip()]
    expected_signs = catalog[2599]
    assert len(expected_signs) == 70
    shatter_path = ROOT / 'ai/omreal/data/seeat_parent2599_shatter8.npz'
    upper_path = ROOT / 'ai/omreal/data/seeat_parent2599_upper178.npz'
    with np.load(shatter_path, allow_pickle=False) as shatter, np.load(upper_path, allow_pickle=False) as upper:
        assert int(shatter['parent_index']) == int(upper['parent_index']) == 2599
        cases = [json.loads((HERE / (name + '.json')).read_text()) for name in
                 ('shatter_pattern_0', 'upper_chart_7', 'upper_chart_0_flow')]
        expected_parents = [shatter['pattern_chart'][0], upper['chart_matrix'][7], upper['chart_matrix'][0]]
        assert cases[0]['signatures'] == cases[1]['signatures'] == [int(shatter['signature'][i]) for i in (0, 4, 3)]
        assert cases[2]['signatures'] == [14988895318912, 3405195891438080, 40418075143643136]
        results = [verify_case(case, parent, expected_signs) for case, parent in zip(cases, expected_parents)]
        first_admissibility = verify_shatter_admissibility(shatter, cases[0]['signatures'], expected_signs)
        flow_admissibility = verify_flow_admissibility(
            json.loads((HERE / 'admissibility_flow.json').read_text()), upper,
            cases[2]['signatures'], expected_signs)
    print(json.dumps({'status': 'PASS', 'arithmetic': 'Exact Python integers; NumPy only reads NPZ files',
                      'search_imported': False, 'tope_enumeration_used': False,
                      'parent_catalog_index_zero_based': 2599,
                      'parent_chirotope': expected_signs, 'cases': results,
                      'shatter_properness_incomparability': first_admissibility,
                      'flow_properness_incomparability': flow_admissibility,
                      'source_sha256': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                                        for p in (catalog_path, shatter_path, upper_path)},
                      'elapsed_seconds': time.perf_counter() - started}, indent=2))


if __name__ == '__main__':
    main()
