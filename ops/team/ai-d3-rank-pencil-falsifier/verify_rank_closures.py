"""Independent exact checker: no producer, enumeration, LP, or solver imports.

NumPy only decodes the immutable NPZ. All proof decisions use Python integers.
Closure membership is checked by all four 3-by-3 minors, independently of the
producer's two-coordinate span interpolation. No old acceptance code is used.
"""
from collections import Counter
from itertools import combinations, permutations
from math import gcd, prod
from pathlib import Path
import ctypes
import hashlib
import json
import sys
import time

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
LABELS = tuple(range(1, 9))
TRIPLES = tuple(sorted(combinations(LABELS, 3), key=lambda item: item[::-1]))
BASES = tuple(sorted(combinations(LABELS, 4), key=lambda item: item[::-1]))
TRIPLE_IDS = {item: i for i, item in enumerate(TRIPLES)}
SIGS = [14988895318912, 3405195891438080, 40418075143643136]
PERMS = {n: [(p, (-1) ** sum(p[i] > p[j] for i in range(n) for j in range(i + 1, n)))
             for p in permutations(range(n))] for n in (2, 3, 4)}
FROZEN_HASHES = {
    'ai/omgamma/data/cat_4_8.txt': '47b2d2b782d298539c85cb170bb10911abe9c82795b4f344e77e3ae64236c7b5',
    'ai/omreal/data/seeat_parent2599_upper178.npz': '3b90799d26b7783e92c2ac697eaaf8b76d26a787f53205873b997657e114180a',
    'ops/team/ai-d3-shared-pencil-falsifier/upper_chart_0_flow.json': '83485ff8bb0a1f8cacffdacbf829cbee5898721b008f8bd54ec2a661ca35e6ab',
    'ops/team/ai-d3-shared-pencil-falsifier/admissibility_flow.json': 'acf71128ca666697bec36436b35ed8bff991a50b8da26b2413cd610631d7ef10',
}


def det(matrix):
    n = len(matrix)
    assert n in PERMS and all(len(row) == n for row in matrix)
    return sum(s * prod(matrix[r][p[r]] for r in range(n)) for p, s in PERMS[n])


def reconstruct(parent, expected):
    assert len(parent) == 4 and all(len(row) == 8 for row in parent)
    assert all(type(value) is int for row in parent for value in row)
    brackets = [det([[parent[r][e - 1] for e in basis] for r in range(4)]) for basis in BASES]
    assert all(brackets), 'Parent must be uniform.'
    assert ''.join('+' if value > 0 else '-' for value in brackets) == expected
    normals = []
    for triple in TRIPLES:
        a = [(-1) ** (r + 3) * det([[parent[q][e - 1] for e in triple]
                                  for q in range(4) if q != r]) for r in range(4)]
        divisor = gcd(*map(abs, a))
        assert divisor > 0
        a = [value // divisor for value in a]
        assert all(sum(a[r] * parent[r][e - 1] for r in range(4)) == 0 for e in triple)
        normals.append(a)
    return normals, brackets


def signed_row(rows, signature, i):
    sign = 1 if signature & (1 << i) else -1
    return [sign * value for value in rows[i]]


def primal(rows, signature, point, selected):
    assert len(point) == 4 and all(type(v) is int for v in point)
    margins = [sum(a * b for a, b in zip(signed_row(rows, signature, i), point)) for i in selected]
    assert margins and min(margins) > 0, 'Strict separator failed on retained row.'
    return min(margins)


def dual(rows, signature, item, require_circuit=False):
    support, weights = item['support'], item['weights']
    assert support and len(support) == len(weights) and len(set(support)) == len(support)
    assert all(type(i) is int and 0 <= i < 56 for i in support)
    assert all(type(w) is int and w > 0 for w in weights)
    selected = [signed_row(rows, signature, i) for i in support]
    assert all(sum(w * a[r] for w, a in zip(weights, selected)) == 0 for r in range(4))
    report = {'support': support, 'strictly_positive_integer_weights': weights,
              'kernel_residual': [0, 0, 0, 0]}
    if require_circuit:
        assert len(support) == 5
        cofactors = [(-1) ** k * det(selected[:k] + selected[k + 1:]) for k in range(5)]
        assert all(cofactors), 'Full witness must have rank four with every deletion independent.'
        assert all(v > 0 for v in cofactors) or all(v < 0 for v in cofactors)
        assert all(cofactors[i] * weights[0] == cofactors[0] * weights[i] for i in range(5))
        report.update(rank=4, signed_deletion_minors=cofactors,
                      common_cofactor_sign=1 if cofactors[0] > 0 else -1)
    return report


def gp_count(parent_signs, signature):
    lookup = dict(zip(BASES, (1 if s == '+' else -1 for s in parent_signs)))
    def chi(seq):
        parity = (-1) ** sum(seq[i] > seq[j] for i in range(4) for j in range(i + 1, 4))
        ordered = tuple(sorted(seq))
        value = (1 if signature & (1 << TRIPLE_IDS[ordered[:3]]) else -1) if ordered[-1] == 9 else lookup[ordered]
        return parity * value
    count = 0
    for pair in combinations(range(1, 10), 2):
        remaining = [e for e in range(1, 10) if e not in pair]
        for a, b, c, d in combinations(remaining, 4):
            signs = {chi(pair + (a, b)) * chi(pair + (c, d)),
                     -chi(pair + (a, c)) * chi(pair + (b, d)),
                     chi(pair + (a, d)) * chi(pair + (b, c))}
            assert signs == {-1, 1}
            count += 1
    assert count == 1260
    return count


def memory_usage():
    if sys.platform != 'win32':
        return {'instrumented': False}
    class Counters(ctypes.Structure):
        _fields_ = [('cb', ctypes.c_ulong), ('PageFaultCount', ctypes.c_ulong)] + [
            (name, ctypes.c_size_t) for name in ('PeakWorkingSetSize', 'WorkingSetSize',
                'QuotaPeakPagedPoolUsage', 'QuotaPagedPoolUsage', 'QuotaPeakNonPagedPoolUsage',
                'QuotaNonPagedPoolUsage', 'PagefileUsage', 'PeakPagefileUsage')]
    counters = Counters()
    counters.cb = ctypes.sizeof(counters)
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.GetCurrentProcess.restype = ctypes.c_void_p
    psapi = ctypes.WinDLL('psapi', use_last_error=True)
    psapi.GetProcessMemoryInfo.argtypes = [ctypes.c_void_p, ctypes.POINTER(Counters), ctypes.c_ulong]
    assert psapi.GetProcessMemoryInfo(kernel.GetCurrentProcess(), ctypes.byref(counters), counters.cb)
    assert counters.PeakWorkingSetSize < 16 * 1024 ** 3
    return {'instrumented': True, 'peak_working_set_bytes': counters.PeakWorkingSetSize,
            'peak_pagefile_bytes': counters.PeakPagefileUsage}


def main():
    started = time.perf_counter()
    certificate_path = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / 'certificate.json'
    certificate = json.loads(certificate_path.read_text())
    assert certificate['schema'] == 'rank-closure-negative-v1'
    assert certificate['status'] == 'NEGATIVE_POINTWISE_INSTANCE'
    assert certificate['parent_index'] == 2599 and certificate['chart_index'] == 0
    assert certificate['signatures'] == SIGS
    source_pins = json.loads((HERE / 'SOURCE_PINS.json').read_text())
    assert source_pins['base_revision'] == '390d447eb1dceb3cf78b294a043e303a6430c267'
    for path, expected_hash in source_pins['sha256'].items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == expected_hash, path
    for path, expected_hash in FROZEN_HASHES.items():
        assert source_pins['sha256'][path] == expected_hash
    old = ROOT / 'ops/team/ai-d3-shared-pencil-falsifier'
    original = json.loads((old / 'upper_chart_0_flow.json').read_text())
    assert certificate['witness_pool'] == original['negative_certificate']['witness_pool']
    assert len(certificate['witness_pool']) == 23
    assert certificate['full_dual_witnesses'] == original['full_dual_witnesses']
    catalog = [line.strip() for line in (ROOT / 'ai/omgamma/data/cat_4_8.txt').read_text().splitlines() if line.strip()]
    parent_signs = catalog[2599]
    assert len(parent_signs) == 70
    anchor_records = json.loads((old / 'admissibility_flow.json').read_text())['records']
    assert len(anchor_records) == 3
    anchors = []
    with np.load(ROOT / 'ai/omreal/data/seeat_parent2599_upper178.npz', allow_pickle=False) as source:
        assert int(source['parent_index']) == 2599
        parent = source['chart_matrix'][0].tolist()
        assert certificate['parent'] == parent == original['parent']
        rows, brackets = reconstruct(parent, parent_signs)
        assert certificate['primitive_normals'] == rows
        for block, record in enumerate(anchor_records):
            assert record['signature'] == SIGS[block]
            chart, index = record['upper_chart_index'], record['upper_point_index']
            assert chart == [3, 14, 2][block] and index == [24588, 14261, 2534][block]
            assert int(source['assignment'][index]) == chart
            anchor = source['chart_matrix'][chart].tolist()
            assert record['parent'] == anchor
            assert record['point'] == source['point'][index].tolist()
            anchor_rows, _ = reconstruct(anchor, parent_signs)
            good_margin = primal(anchor_rows, SIGS[block], record['point'], range(56))
            assert len(record['other_systems']) == 3
            bad = []
            for other, item in enumerate(record['other_systems']):
                assert item['signature'] == SIGS[other]
                if other == block:
                    assert item['dual'] is None
                    primal(anchor_rows, SIGS[other], item['primal'], range(56))
                else:
                    dual(anchor_rows, SIGS[other], item['dual'])
                    bad.append(other)
            anchors.append({'chart': chart, 'point_index': index, 'good_signature_index': block,
                            'bad_signature_indices': bad, 'good_minimum_margin': good_margin})
    validity = [gp_count(parent_signs, signature) for signature in SIGS]
    full_circuits = [dual(rows, signature, item, require_circuit=True)
                     for signature, item in zip(SIGS, certificate['full_dual_witnesses'])]
    assert len(full_circuits) == 3
    required = {(e, i, j) for e in LABELS for i, j in combinations(
        [k for k, triple in enumerate(TRIPLES) if e in triple], 2)}
    assert len(required) == 1680
    pool = certificate['witness_pool']
    usage = Counter()
    closure_counts = Counter()
    geometry = Counter()
    unique = set()
    seen = set()
    margins = []
    inequalities = 0
    rank3_outside_count = 0
    pair_minors = []
    exclusion_minors = []
    coords3 = tuple(combinations(range(4), 3))
    for record in certificate['coverage']:
        e = record['label']
        pair = record['pair']
        assert type(e) is int and len(pair) == 2 and all(type(i) is int for i in pair)
        key = (e, *pair)
        assert key in required and key not in seen
        seen.add(key)
        i, j = pair
        star = [k for k, triple in enumerate(TRIPLES) if e in triple]
        nonstar = [k for k, triple in enumerate(TRIPLES) if e not in triple]
        assert len(star) == 21 and len(nonstar) == 35
        minors2 = [det([[rows[k][r] for r in coords] for k in pair])
                   for coords in combinations(range(4), 2)]
        assert any(minors2), 'Two incident normals are proportional.'
        pair_minors.append(next(abs(v) for v in minors2 if v))
        closure = []
        for k in star:
            minors3 = [det([[rows[l][r] for r in coords] for l in (i, j, k)]) for coords in coords3]
            if not any(minors3):
                closure.append(k)
            else:
                rank3_outside_count += 1
                exclusion_minors.append(next(abs(v) for v in minors3 if v))
        assert record['closure'] == closure, 'Closure was not computed exactly or contains omitted rows.'
        assert set(pair) <= set(closure)
        common = set(TRIPLES[i]) & set(TRIPLES[j])
        if len(common) == 2:
            expected_closure = [k for k, triple in enumerate(TRIPLES) if common <= set(triple)]
            assert closure == expected_closure and len(closure) == 6
            geometry['six_rows_through_two_fixed_labels'] += 1
        else:
            assert common == {e} and closure == pair
            geometry['two_rows_sharing_only_moving_label'] += 1
        selected = nonstar + closure
        witness_index = record['witness']
        assert type(witness_index) is int and 0 <= witness_index < len(pool)
        witness = pool[witness_index]
        block = witness['signature_index']
        assert type(block) is int and 0 <= block < 3
        minimum = primal(rows, SIGS[block], witness['point'], selected)
        assert type(record['minimum_margin']) is int and minimum == record['minimum_margin']
        margins.append(minimum)
        inequalities += len(selected)
        usage[block] += 1
        closure_counts[len(closure)] += 1
        unique.add((e, tuple(closure)))
    assert seen == required
    assert closure_counts == {2: 840, 6: 840}
    assert len(unique) == 896 and inequalities == 65520 and rank3_outside_count == 28560
    report = {
        'status': 'PASS', 'scope': 'All rank-at-most-two incident support unions excluded at one frozen point.',
        'parent_index': 2599, 'chart_index': 0, 'signatures': SIGS,
        'parent_chirotope': parent_signs, 'parent_brackets_checked_at_target': 70,
        'minimum_absolute_parent_bracket': min(map(abs, brackets)),
        'primitive_normals_reconstructed': len(rows), 'target_normal_incidence_equations': 168,
        'gp_relations_per_signature': validity,
        'indexed_pairs': len(seen), 'unique_labelled_closures': len(unique),
        'closure_size_distribution': dict(closure_counts), 'geometry': dict(geometry),
        'strict_inequalities_checked': inequalities, 'signature_usage': dict(usage),
        'reused_separator_pool_size': len(pool), 'minimum_integer_margin': min(margins),
        'rank_two_pairs_verified': len(pair_minors), 'rank_three_exclusions_verified': rank3_outside_count,
        'minimum_absolute_selected_pair_minor': min(pair_minors),
        'minimum_absolute_selected_exclusion_minor': min(exclusion_minors),
        'full_positive_rank_four_circuits': full_circuits,
        'same_parent_realized_proper_incomparable_anchors': anchors,
        'new_rank_predicate_points': [[2599, 0]],
        'stability': {'nonzero_pair_minors': 1680, 'nonzero_exclusion_minors': 28560,
                      'strict_separator_inequalities': inequalities,
                      'positive_rank_four_full_circuits': 3,
                      'conclusion': 'A relative open neighborhood is triple-bad and fails the full rank-two-star criterion.'},
        'arithmetic': 'Python arbitrary-precision integers; NumPy only decodes frozen NPZ.',
        'producer_or_old_verifier_imported': False, 'tope_enumeration_or_lp_used': False,
        'certificate_sha256': hashlib.sha256(certificate_path.read_bytes()).hexdigest(),
        'sources_sha256': source_pins['sha256'],
        'elapsed_seconds': time.perf_counter() - started, 'memory': memory_usage(),
    }
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
