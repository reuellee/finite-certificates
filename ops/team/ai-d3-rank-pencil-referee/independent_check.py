#!/usr/bin/env python3
"""Independent exact Stage D acceptance; stdlib only; no producer imports.

Raw normals are reconstructed by four determinant evaluations per triple.
Rank closures are tested by all four 3x3 coordinate minors, not by Cramer
interpolation. Inputs are immutable Git blobs, not current worktree files.
"""
import ast
from collections import Counter
from copy import deepcopy
from functools import reduce
from hashlib import sha256
from io import BytesIO
from itertools import combinations
from math import comb, gcd, prod
from pathlib import Path
import json
import struct
import subprocess
import time
import zipfile

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
BASE = 'fdd143c8be96636b7b11af0ac7e2ea8d60b65eca'
SECOND = '52ad4e14c63831243f0a57b193e99ebbf32891e5'
OLD = '4927d5bcc24d91cf173551b248721b247107073a'
TARGET = [14988895318912, 3405195891438080, 40418075143643136]
PINNED = {
 BASE+':ops/team/ai-d3-shared-pencil-constructor/OBSTRUCTION.json': '77bd316237f6fd7060e964aec1852daa10dfaa065a7d0c4194b0a59929a32afa',
 BASE+':ops/team/ai-d3-shared-pencil-falsifier/upper_chart_0_flow.json': '83485ff8bb0a1f8cacffdacbf829cbee5898721b008f8bd54ec2a661ca35e6ab',
 OLD+':ai/omreal/data/seeat_parent2599_upper178.npz': '3b90799d26b7783e92c2ac697eaaf8b76d26a787f53205873b997657e114180a',
 OLD+':ai/omgamma/data/cat_4_8.txt': '47b2d2b782d298539c85cb170bb10911abe9c82795b4f344e77e3ae64236c7b5',
 SECOND+':ops/team/ai-d3-rank-pencil-falsifier/certificate.json': '38a469d4f5c84f7d5e4fa2f09382d786d560d4847f96f76578e488bffdfadeea',
}


def need(value, why):
    if not value:
        raise AssertionError(why)


def digest(data):
    return sha256(data).hexdigest()


def compact(data):
    return json.dumps(data, separators=(',', ':')).encode()


def git_blob(key):
    return subprocess.check_output(['git', 'show', key], cwd=ROOT)


def load_inputs():
    blobs = {}
    records = []
    for key, expected in PINNED.items():
        data = git_blob(key)
        need(digest(data) == expected, 'source hash: '+key)
        blobs[key] = data
        records.append({'git_source': key, 'sha256': expected, 'bytes': len(data),
                        'git_blob': subprocess.check_output(['git', 'rev-parse', key], cwd=ROOT, text=True).strip()})
    return blobs, records


def subsets(size):
    result = [None] * comb(8, size)
    for item in combinations(range(8), size):
        index = sum(comb(label, j+1) for j, label in enumerate(item))
        need(result[index] is None, 'duplicate combinadic index')
        result[index] = item
    need(all(v is not None for v in result), 'missing combinadic index')
    return result


TRIPLES = subsets(3)
BASES = subsets(4)
COORD2 = tuple(combinations(range(4), 2))
COORD3 = tuple(combinations(range(4), 3))


def det(a):
    """Recursive Laplace expansion, with direct 2x2 base case."""
    n = len(a)
    need(n > 0 and all(len(row) == n for row in a), 'square determinant')
    if n == 1:
        return a[0][0]
    if n == 2:
        return a[0][0]*a[1][1] - a[0][1]*a[1][0]
    return sum((-1)**j * a[0][j] * det([row[:j]+row[j+1:] for row in a[1:]]) for j in range(n))


def dot(a, b):
    return sum(x*y for x, y in zip(a, b))


def sign(sigma, row):
    return 2*((sigma >> row) & 1)-1


def raw_normals(parent):
    rows = []
    for triple in TRIPLES:
        row = [det([[parent[r][c] for c in triple]+[int(r == j)] for r in range(4)]) for j in range(4)]
        need(any(row), 'zero raw normal')
        need(all(dot(row, [parent[r][c] for r in range(4)]) == 0 for c in triple), 'normal incidence')
        rows.append(row)
    return rows


def npy_integers(data):
    """Minimal audited NPY integer decoder; rejects objects/order ambiguity."""
    need(data[:6] == b'\x93NUMPY', 'NPY magic')
    version = tuple(data[6:8])
    need(version in ((1, 0), (2, 0), (3, 0)), 'NPY version')
    width = 2 if version == (1, 0) else 4
    length = int.from_bytes(data[8:8+width], 'little')
    offset = 8+width+length
    header = ast.literal_eval(data[8+width:offset].decode())
    need(header['fortran_order'] is False, 'NPY C-order required')
    desc = header['descr']
    need(desc in ('<i8', '<i4', '|i1', '<u8', '<u4', '|u1'), 'NPY exact integer dtype')
    size = int(desc[2:])
    shape = tuple(header['shape'])
    count = prod(shape)
    need(len(data)-offset == size*count, 'NPY exact payload length')
    values = [int.from_bytes(data[offset+i*size:offset+(i+1)*size], 'little', signed=desc[1] == 'i') for i in range(count)]
    return shape, values


def binding(parent, source, catalog):
    with zipfile.ZipFile(BytesIO(source)) as archive:
        shape, values = npy_integers(archive.read('chart_matrix.npy'))
        need(shape == (178, 4, 8), 'upper178 array shape')
        need(parent == [values[8*r:8*(r+1)] for r in range(4)], 'literal upper chart zero binding')
        shape, index = npy_integers(archive.read('parent_index.npy'))
        need(index == [2599], 'NPZ parent index')
    brackets = [det([[parent[r][c] for c in t] for r in range(4)]) for t in BASES]
    need(all(brackets), 'uniform parent: 70 brackets')
    signs = ''.join('+' if b > 0 else '-' for b in brackets)
    lines = [line.strip() for line in catalog.decode().splitlines() if line.strip()]
    need(signs == lines[2599], 'catalog labeled chirotope')
    need(brackets[0] > 0, 'positive basis orientation')
    return {'parent_index': 2599, 'chart_index': 0, 'catalog_chirotope': signs,
            'brackets': len(brackets), 'minimum_absolute_bracket': min(map(abs, brackets))}


def positive_circuit(rows, sigma, witness):
    indices = witness.get('row_indices', witness.get('support'))
    weights = witness['weights']
    need(len(indices) == len(set(indices)) == len(weights) == 5, 'circuit support length')
    need(all(type(i) is int and 0 <= i < 56 for i in indices), 'circuit index range')
    need(all(type(w) is int and w > 0 for w in weights), 'strictly positive circuit weights')
    signed_rows = [[sign(sigma, i)*x for x in rows[i]] for i in indices]
    need(all(sum(w*r[j] for w, r in zip(weights, signed_rows)) == 0 for j in range(4)), 'circuit residual')
    cofactors = [(-1)**k * det([row for j, row in enumerate(signed_rows) if j != k]) for k in range(5)]
    need(all(cofactors), 'rank-four deletion minor')
    need(all(x*cofactors[0] > 0 for x in cofactors), 'coherent cofactor signs')
    need(all(weights[k]*cofactors[0] == weights[0]*cofactors[k] for k in range(5)), 'cofactor ray')
    need(all(sum(c*r[j] for c, r in zip(cofactors, signed_rows)) == 0 for j in range(4)), 'cofactor identity')
    return {'support': indices, 'rank': 4, 'cofactor_sign': 1 if cofactors[0] > 0 else -1,
            'minimum_absolute_deletion_minor': min(map(abs, cofactors))}


def pair_data(rows, label, pair):
    star = [i for i, triple in enumerate(TRIPLES) if label in triple]
    need(len(star) == 21 and len(pair) == 2 and pair[0] < pair[1] and set(pair) <= set(star), 'valid distinct star pair')
    a, b = (rows[i] for i in pair)
    minors2 = [det([[row[j] for j in cols] for row in (a, b)]) for cols in COORD2]
    need(any(minors2), 'pair rank two')
    rank2_index = next(i for i, m in enumerate(minors2) if m)
    closure, excluded = [], []
    for i in star:
        minors3 = [det([[row[j] for j in cols] for row in (a, b, rows[i])]) for cols in COORD3]
        if all(m == 0 for m in minors3):
            closure.append(i)
        else:
            witness_index = next(k for k, m in enumerate(minors3) if m)
            excluded.append([i, list(COORD3[witness_index]), minors3[witness_index]])
    need(set(pair) <= set(closure), 'pair contained in closure')
    return closure, [list(COORD2[rank2_index]), minors2[rank2_index]], excluded


def strict(rows, sigma, point, retained):
    need(len(point) == 4 and all(type(v) is int for v in point), 'integer separator')
    margins = [sign(sigma, i)*dot(rows[i], point) for i in retained]
    need(margins and min(margins) > 0, 'expanded separator is not strict')
    return margins


def coverage_check(records, rows, pool, expected):
    seen, count, minima, uses = set(), 0, [], Counter()
    for record in records:
        label, pair = record['label']-1, tuple(record['pair'])
        key = (label, pair)
        need(key in expected and key not in seen, 'invalid or duplicate indexed closure')
        seen.add(key)
        closure = expected[key][0]
        need(record['closure'] == closure, 'incorrect expanded closure')
        retained = [i for i, triple in enumerate(TRIPLES) if label not in triple]+closure
        wi = record['witness']
        need(type(wi) is int and 0 <= wi < len(pool), 'separator pool reference')
        entry = pool[wi]
        need(type(entry['signature_index']) is int and 0 <= entry['signature_index'] < 3, 'signature index')
        margins = strict(rows, TARGET[entry['signature_index']], entry['point'], retained)
        if 'minimum_margin' in record:
            need(record['minimum_margin'] == min(margins), 'incorrect recorded minimum margin')
        count += len(margins)
        minima.append(min(margins))
        uses[entry['signature_index']] += 1
    need(seen == set(expected), 'missing indexed closure')
    return {'indexed_pairs': len(seen), 'strict_inequalities': count,
            'minimum_integer_margin': min(minima), 'signature_usage': dict(uses)}


def memory_snapshot():
    import ctypes
    from ctypes import wintypes
    class Counters(ctypes.Structure):
        _fields_ = [('cb', wintypes.DWORD), ('PageFaultCount', wintypes.DWORD)]+[(name, ctypes.c_size_t) for name in ('PeakWorkingSetSize', 'WorkingSetSize', 'QuotaPeakPagedPoolUsage', 'QuotaPagedPoolUsage', 'QuotaPeakNonPagedPoolUsage', 'QuotaNonPagedPoolUsage', 'PagefileUsage', 'PeakPagefileUsage')]
    if not hasattr(ctypes, 'WinDLL'):
        return {'instrumented': False}
    data = Counters(); data.cb = ctypes.sizeof(data)
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    psapi = ctypes.WinDLL('psapi', use_last_error=True)
    kernel.GetCurrentProcess.restype = wintypes.HANDLE
    psapi.GetProcessMemoryInfo.argtypes = [wintypes.HANDLE, ctypes.POINTER(Counters), wintypes.DWORD]
    need(psapi.GetProcessMemoryInfo(kernel.GetCurrentProcess(), ctypes.byref(data), data.cb), 'process memory instrumentation')
    return {'instrumented': True, 'peak_working_set_bytes': data.PeakWorkingSetSize, 'peak_pagefile_bytes': data.PeakPagefileUsage}


def main():
    start = time.perf_counter()
    blobs, sources = load_inputs()
    keys = list(PINNED)
    principal, old_pool_cert, secondary = (json.loads(blobs[keys[i]]) for i in (0, 1, 4))
    need(principal['signatures'] == old_pool_cert['signatures'] == secondary['signatures'] == TARGET, 'target signatures')
    parent = principal['parent']
    need(parent == old_pool_cert['parent'] == secondary['parent'], 'frozen parent agreement')
    base_binding = binding(parent, blobs[keys[2]], blobs[keys[3]])
    rows = raw_normals(parent)
    primitive = [[x//reduce(gcd, map(abs, row)) for x in row] for row in rows]
    need(primitive == secondary['primitive_normals'], 'secondary primitive normals/order')
    primary_circuits = [positive_circuit(rows, sigma, w) for sigma, w in zip(TARGET, principal['full_bad_witnesses'])]
    need(len(primary_circuits) == len(principal['full_bad_witnesses']) == 3, 'three full raw circuits')
    secondary_circuits = [positive_circuit(primitive, sigma, w) for sigma, w in zip(TARGET, secondary['full_dual_witnesses'])]
    need(len(secondary_circuits) == len(secondary['full_dual_witnesses']) == 3, 'three full primitive circuits')
    pool = old_pool_cert['negative_certificate']['witness_pool']
    need(pool == secondary['witness_pool'] and len(pool) == 23, 'same frozen 23-vector pool')
    expected, selected, rank_records = {}, [], []
    indexed_sizes, unique, strict_hash = Counter(), set(), sha256()
    for label in range(8):
        star = [i for i, triple in enumerate(TRIPLES) if label in triple]
        nonstar = [i for i, triple in enumerate(TRIPLES) if label not in triple]
        need((len(star), len(nonstar)) == (21, 35), 'star/nonstar sizes')
        for pair in combinations(star, 2):
            closure, minor2, excluded = pair_data(rows, label, pair)
            expected[(label, pair)] = (closure, minor2, excluded)
            rank_records.append([label+1, list(pair), minor2, excluded])
            indexed_sizes[len(closure)] += 1
            unique.add((label, tuple(closure)))
            retained = nonstar+closure
            candidates = [(wi, [sign(TARGET[p['signature_index']], i)*dot(rows[i], p['point']) for i in retained]) for wi, p in enumerate(pool)]
            passed = [(wi, margins) for wi, margins in candidates if min(margins) > 0]
            need(passed, 'no existing separator covers expanded closure')
            wi, margins = passed[0]
            selected.append({'label': label+1, 'pair': list(pair), 'closure': closure, 'witness': wi, 'minimum_margin': min(margins)})
            strict_hash.update(compact([label+1, pair, wi, margins]))
    own_coverage = coverage_check(selected, rows, pool, expected)
    secondary_coverage = coverage_check(secondary['coverage'], primitive, pool, expected)
    need(own_coverage['indexed_pairs'] == 1680, 'exhaustive indexed count')
    closure_hash = digest(compact([[r['label'], r['pair'], r['closure'], r['witness']] for r in selected]))
    coordinator_key = BASE+':ops/team/ai-d3-rank-pencil-coordinator/CHECK_OUTPUT.json'
    coordinator_bytes = git_blob(coordinator_key)
    sources.append({'git_source': coordinator_key, 'sha256': digest(coordinator_bytes), 'bytes': len(coordinator_bytes), 'usage': 'compare independently reconstructed output only'})
    coordinator = json.loads(coordinator_bytes)
    need(closure_hash == coordinator['closure_table_sha256'], 'independent coordinator table agreement')
    need(own_coverage['strict_inequalities'] == coordinator['expanded_strict_inequalities'], 'coordinator strict count')
    need(own_coverage['minimum_integer_margin'] == coordinator['minimum_raw_integer_margin'], 'coordinator minimum margin')
    mutations = []
    def rejected(name, action):
        try:
            action()
        except (AssertionError, KeyError, ValueError, IndexError) as error:
            mutations.append({'mutation': name, 'rejection': str(error)})
            return
        raise AssertionError('hostile mutation accepted: '+name)
    changed = deepcopy(selected); changed.pop()
    rejected('missing_indexed_closure', lambda: coverage_check(changed, rows, pool, expected))
    changed = deepcopy(selected); changed[-1] = deepcopy(changed[0])
    rejected('duplicate_indexed_closure', lambda: coverage_check(changed, rows, pool, expected))
    changed = deepcopy(selected); changed[0]['closure'] = changed[0]['pair']
    rejected('omit_added_closure_rows', lambda: coverage_check(changed, rows, pool, expected))
    changed = deepcopy(selected); changed[0]['closure'].append(next(i for i in range(56) if i not in changed[0]['closure']))
    rejected('insert_nonmember_row', lambda: coverage_check(changed, rows, pool, expected))
    changed_pool = deepcopy(pool); changed_pool[selected[0]['witness']]['point'] = [0]*4
    rejected('zero_separator', lambda: coverage_check(selected, rows, changed_pool, expected))
    changed = deepcopy(selected); changed[0]['minimum_margin'] = 0
    rejected('corrupt_stored_margin', lambda: coverage_check(changed, rows, pool, expected))
    rejected('proportional_star_pair', lambda: pair_data([rows[0]]*56, 0, (0, 1)))
    witness = deepcopy(principal['full_bad_witnesses'][0]); witness['weights'][0] = 0
    rejected('zero_full_circuit_weight', lambda: positive_circuit(rows, TARGET[0], witness))
    witness = deepcopy(principal['full_bad_witnesses'][0]); witness['weights'][0] += 1
    rejected('corrupt_full_circuit_weight', lambda: positive_circuit(rows, TARGET[0], witness))
    badrows = deepcopy(rows); badrows[principal['full_bad_witnesses'][0]['row_indices'][0]] = [0]*4
    rejected('corrupt_full_circuit_row', lambda: positive_circuit(badrows, TARGET[0], principal['full_bad_witnesses'][0]))
    rejected('signature_bit_drift_on_support', lambda: positive_circuit(rows, TARGET[0]^(1 << principal['full_bad_witnesses'][0]['row_indices'][0]), principal['full_bad_witnesses'][0]))
    # The old at-most-two test really passes this vector; the added rows kill it.
    label, pair = 0, (0, 2)
    closure = expected[(label, pair)][0]
    nonstar = [i for i, triple in enumerate(TRIPLES) if label not in triple]
    old_entry = pool[0]
    before = strict(rows, TARGET[old_entry['signature_index']], old_entry['point'], nonstar+list(pair))
    rejected('old_two_row_separator_fails_expanded_closure', lambda: strict(rows, TARGET[old_entry['signature_index']], old_entry['point'], nonstar+closure))
    canary_values = [[i, sign(TARGET[old_entry['signature_index']], i)*dot(rows[i], old_entry['point'])] for i in closure if i not in pair]
    exclusions = [x for record in rank_records for x in record[3]]
    result = {
      'status': 'PASS_INDEPENDENT_COMPLETE_FIXED_PLANE_COUNTERCERTIFICATES',
      'principal_commit': BASE, 'secondary_commit': SECOND,
      'arithmetic': 'stdlib exact integers; recursive Laplace determinants; all four 3x3 coordinate minors',
      'producer_acceptance_code_imported_or_executed': False,
      'new_rank_predicate_points': 1, 'binding': base_binding, 'signatures': TARGET,
      'primary_raw_coverage': own_coverage, 'secondary_primitive_coverage': secondary_coverage,
      'distinct_labeled_closures': len(unique),
      'indexed_closure_size_histogram': dict(indexed_sizes),
      'distinct_closure_size_histogram': dict(Counter(len(c) for _, c in unique)),
      'existing_pool_vectors': len(pool), 'pool_indices_used': sorted({r['witness'] for r in selected}),
      'pair_rank_two_witnesses': len(rank_records), 'excluded_row_rank_three_witnesses': len(exclusions),
      'three_by_three_coordinate_minors_evaluated': 1680*21*4,
      'minimum_selected_nonzero_pair_minor_abs': min(abs(r[2][1]) for r in rank_records),
      'minimum_selected_nonzero_exclusion_minor_abs': min(abs(r[2]) for r in exclusions),
      'primary_full_positive_rank_four_circuits': primary_circuits,
      'secondary_full_positive_rank_four_circuits': secondary_circuits,
      'closure_table_sha256': closure_hash,
      'all_selected_strict_evaluations_sha256': strict_hash.hexdigest(),
      'rank_witness_table_sha256': digest(compact(rank_records)),
      'raw_normals_sha256': digest(compact(rows)),
      'added_row_canary': {'label': 1, 'pair': [0, 2], 'pool_index': 0, 'old_retained_minimum': min(before), 'added_rows_and_raw_evaluations': canary_values},
      'hostile_mutations_rejected': mutations,
      'elapsed_seconds': round(time.perf_counter()-start, 6),
      'process_memory': memory_snapshot(),
      'scope': 'Refutes the universal fixed-support-plane one-column rank-at-most-two witness criterion; does not refute all one-column motions, D3, or prove compactness.'
    }
    for name, data in [('EXPANDED_COVERAGE.json', selected), ('RANK_WITNESSES.json', rank_records), ('SOURCE_PINS.json', sources)]:
        (OUT/name).write_text(json.dumps(data, separators=(',', ':'))+'\n', encoding='utf-8', newline='\n')
    result['process_memory'] = memory_snapshot()
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
