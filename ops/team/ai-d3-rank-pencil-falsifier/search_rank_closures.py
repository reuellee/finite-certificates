"""One frozen point only. Discovery does not supply acceptance logic."""
from collections import Counter
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path
import hashlib
import json
import sys
import time

sys.dont_write_bytecode = True
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'ai/omreal'))
import DIAG9_GRAPH_exact_topes as topes

SIGS = [14988895318912, 3405195891438080, 40418075143643136]
OLD = ROOT / 'ops/team/ai-d3-shared-pencil-falsifier'


def closure_of(rows, star, pair):
    a, b = (rows[i] for i in pair)
    p, q = next((p, q) for p, q in combinations(range(4), 2)
                if a[p] * b[q] - a[q] * b[p])
    minor = a[p] * b[q] - a[q] * b[p]
    selected = []
    for k in star:
        v = rows[k]
        alpha = v[p] * b[q] - v[q] * b[p]
        beta = a[p] * v[q] - a[q] * v[p]
        if all(minor * v[r] == alpha * a[r] + beta * b[r] for r in range(4)):
            selected.append(k)
    return selected


def main():
    started = time.perf_counter()
    original = json.loads((OLD / 'upper_chart_0_flow.json').read_text())
    with np.load(ROOT / 'ai/omreal/data/seeat_parent2599_upper178.npz', allow_pickle=False) as source:
        assert int(source['parent_index']) == 2599
        parent = source['chart_matrix'][0].tolist()
    assert parent == original['parent'] and SIGS == original['signatures']
    rows = topes.derived_rows(parent)
    pool = original['negative_certificate']['witness_pool']
    assert len(pool) == 23
    margins = [[(1 if SIGS[w['signature_index']] >> i & 1 else -1) *
                topes.dot(row, w['point']) for i, row in enumerate(rows)] for w in pool]
    coverage = []
    unresolved = []
    counts = Counter()
    for e in range(8):
        star = [i for i, triple in enumerate(topes.TRIPLES) if e in triple]
        nonstar = [i for i, triple in enumerate(topes.TRIPLES) if e not in triple]
        assert len(star) == 21 and len(nonstar) == 35
        for pair in combinations(star, 2):
            closure = closure_of(rows, star, pair)
            selected = nonstar + closure
            counts[len(closure)] += 1
            found = next((k for k, m in enumerate(margins) if min(m[i] for i in selected) > 0), None)
            record = {'label': e + 1, 'pair': list(pair), 'closure': closure}
            if found is None:
                unresolved.append(record)
            else:
                record.update(witness=found, minimum_margin=min(margins[found][i] for i in selected))
                coverage.append(record)
    print(json.dumps({'indexed_pairs': sum(counts.values()), 'closure_size_distribution': dict(counts),
                      'covered_by_old_pool': len(coverage), 'unresolved': len(unresolved),
                      'first_unresolved': unresolved[:1]}, indent=2), flush=True)
    enumerated_count = None
    if unresolved:
        enumerated = topes.enumerate_topes(rows, dimension=4)
        enumerated_count = len(enumerated)
        print('Additional exact tope enumeration at chart zero:', enumerated_count, flush=True)
        for record in unresolved:
            selected = [i for i, triple in enumerate(topes.TRIPLES)
                        if record['label'] - 1 not in triple or i in record['closure']]
            mask = sum(1 << i for i in selected)
            found = None
            for block, signature in enumerate(SIGS):
                point = next((point for pattern, point in enumerated.items()
                              if (pattern ^ signature) & mask == 0), None)
                if point is not None:
                    found = len(pool)
                    pool.append({'signature_index': block, 'point': list(point)})
                    record.update(witness=found, minimum_margin=min(
                        (1 if signature >> i & 1 else -1) * topes.dot(rows[i], point)
                        for i in selected))
                    coverage.append(record)
                    break
            if found is None:
                raise RuntimeError('STOP: first unresolved expanded closure ' + repr(record))
    coverage.sort(key=lambda r: (r['label'], *r['pair']))
    assert len(coverage) == 1680
    certificate = {'schema': 'rank-closure-negative-v1', 'status': 'NEGATIVE_POINTWISE_INSTANCE',
                   'parent_index': 2599, 'chart_index': 0, 'parent': parent, 'signatures': SIGS,
                   'row_order': 'colex triples of labels 1..8; row indices 0..55',
                   'primitive_normals': [list(row) for row in rows],
                   'full_dual_witnesses': original['full_dual_witnesses'],
                   'witness_pool': pool, 'coverage': coverage,
                   'discovery': {'reused_original_pool_size': 23,
                                 'additional_tope_enumeration_count': enumerated_count,
                                 'new_predicate_points': [[2599, 0]],
                                 'elapsed_seconds': time.perf_counter() - started,
                                 'completed_utc': datetime.now(timezone.utc).isoformat()}}
    (HERE / 'certificate.json').write_text(json.dumps(certificate, indent=2) + '\n', newline='\n')
    print('STOP at first complete negative certificate.', flush=True)


if __name__ == '__main__':
    main()
