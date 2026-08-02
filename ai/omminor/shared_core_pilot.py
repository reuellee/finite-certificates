#!/usr/bin/env python3
"""Search exact BFP cores shared by pairs in one fixed labelling.

Comparing the BFP emitted for class A with class B can miss an alternative
certificate supported by GP conditions common to both classes.  This pilot
tests that stronger question for every pair in ``core_minimal_sample.jsonl``.

For a pair, keep exactly the GP relations having the same BIG term in both
chirotopes.  Gordan's alternative gives one of two exact certificates:

* a positive dependence among the common rows (one BFP valid for both); or
* an integer vector u with v.u > 0 for every common row (proof that no BFP
  supported only on their common, literally labelled conditions exists).

LP is search only.  Positive dependences are reconstructed over Q and emitted
as positive integers.  Strict witnesses are rounded and then checked using an
integer matrix-vector product.  The independent verifier rebuilds everything.

This does *not* search the 9! relative relabellings of each pair.
"""

import argparse
import gzip
import hashlib
import json
import math
import os
import sys
import time
from itertools import combinations

import numpy as np
from scipy.optimize import linprog


HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, '..', '..'))
OMREAL = os.path.join(REPO, 'ai', 'omreal')
sys.path.insert(0, OMREAL)

import bfp  # noqa: E402


DEFAULT_INPUT = os.path.join(HERE, 'data', 'core_minimal_sample.jsonl')
DEFAULT_OUTPUT = os.path.join(HERE, 'data', 'core_shared_literal.json.gz')


def file_hash(path):
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        for block in iter(lambda: fh.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def exact_gordan(V, meta, gp):
    m = len(V)
    matrix = np.vstack((V.T.astype(np.float64), np.ones((1, m))))
    rhs = np.zeros(gp.M + 1)
    rhs[-1] = 1.0
    result = linprog(np.zeros(m), A_eq=matrix, b_eq=rhs,
                     bounds=(0, None), method='highs')
    if not result.success:
        return None
    support = [int(i) for i in np.argsort(-result.x) if result.x[int(i)] > 1e-9]
    for trim in range(min(5, len(support))):
        candidate = support[:len(support) - trim] if trim else support
        weights = bfp._exact_nonneg_kernel(V, candidate)
        if weights is None:
            continue
        terms = []
        for row, weight in zip(candidate, weights):
            relation, big, small = meta[row]
            L, Q, _ = gp.rel[relation]
            terms.append({'L': list(L), 'abcd': list(Q), 'big': int(big),
                          'small': int(small), 'w': int(weight)})
        return terms
    raise RuntimeError('float Gordan hit did not reconstruct exactly')


def exact_strict_witness(V):
    result = linprog(np.zeros(V.shape[1]), A_ub=-V.astype(np.float64),
                     b_ub=-np.ones(len(V)), bounds=(None, None), method='highs')
    if not result.success:
        return None
    for exponent in range(0, 41):
        scale = 1 << exponent
        values = np.rint(result.x * scale).astype(np.int64)
        values -= values[0]  # every GP row has coordinate sum zero
        margins = V.astype(np.int64) @ values
        if len(margins) and int(margins.min()) > 0:
            g = 0
            for value in values:
                g = math.gcd(g, abs(int(value)))
            if g > 1:
                values //= g
            if int((V.astype(np.int64) @ values).min()) <= 0:
                raise AssertionError('normalisation broke a strict witness')
            return [int(x) for x in values]
    raise RuntimeError('float strict witness did not reconstruct exactly')


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--input', default=DEFAULT_INPUT)
    ap.add_argument('--output', default=DEFAULT_OUTPUT)
    args = ap.parse_args(argv)

    records = [json.loads(line) for line in open(args.input) if line.strip()]
    if len(records) < 2:
        raise SystemExit('need at least two BFP records')
    gp = bfp.GPSystem(9, 4)
    systems = []
    bigs = []
    for record in records:
        chi = np.array([1 if x == '+' else -1 for x in record['chi']],
                       dtype=np.int8)
        V, meta = gp.inequalities(chi)
        big = np.full(len(gp.rel), -1, dtype=np.int8)
        for relation, odd, _ in meta:
            big[relation] = odd
        systems.append((V, meta))
        bigs.append(big)

    results = []
    hits = 0
    t0 = time.time()
    pairs = list(combinations(range(len(records)), 2))
    for number, (i, j) in enumerate(pairs, 1):
        V0, meta0 = systems[i]
        keep = np.fromiter((bigs[j][relation] == odd
                            for relation, odd, _ in meta0),
                           dtype=bool, count=len(meta0))
        V = V0[keep]
        meta = [item for item, yes in zip(meta0, keep) if yes]
        terms = exact_gordan(V, meta, gp)
        if terms is not None:
            hits += 1
            result = {'i': i, 'j': j, 'kind': 'COMMON_BFP', 'bfp': terms}
        else:
            witness = exact_strict_witness(V)
            if witness is None:
                raise RuntimeError('Gordan dichotomy unresolved at pair %d,%d' % (i, j))
            result = {'i': i, 'j': j, 'kind': 'STRICT_WITNESS', 'u': witness}
        result['shared_relations'] = int(keep.sum() // 2)
        result['shared_rows'] = int(keep.sum())
        results.append(result)
        if number % 250 == 0 or number == len(pairs):
            print('%d/%d pairs; %d common BFPs; %.1f s' %
                  (number, len(pairs), hits, time.time() - t0), flush=True)

    artifact = {
        'schema': 1,
        'scope': ('all pairs in the deterministic 64-class minor-minimal '
                  'sample, fixed canonical labelling only'),
        'input': {'path': os.path.relpath(args.input, REPO),
                  'sha256': file_hash(args.input), 'records': len(records)},
        'summary': {'pairs': len(pairs), 'common_bfp': hits,
                    'strict_witness': len(pairs) - hits},
        'results': results,
    }
    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    with open(args.output, 'wb') as raw:
        with gzip.GzipFile(filename='', mode='wb', fileobj=raw, mtime=0) as zipped:
            zipped.write((json.dumps(artifact, sort_keys=True,
                                     separators=(',', ':')) + '\n').encode())
    print('wrote %s (%d bytes, %.1f s)' %
          (args.output, os.path.getsize(args.output), time.time() - t0))
    return 0


if __name__ == '__main__':
    sys.exit(main())
