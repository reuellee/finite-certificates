#!/usr/bin/env python3
"""Regenerate an exact BFP sample from the tracked minor-minimal list.

The large certificate shards used by ``MINOR_THEORY.md`` are intentionally
gitignored, but ``data/minimal_ext.txt`` retains the canonical chirotope of
each of 1,758 independently established minor-minimal classes.  That is
enough to regenerate BFP certificates for a deterministic pilot sample.

Selection is by the smallest SHA-256 values of ``tag || NUL || chi``.  It is
therefore independent of list order and reproducible.  Floating-point LP is
used only to locate a support; ``bfp.py`` reconstructs positive integer
weights, and the output is accepted only if the independent standard-library
``checkcert.py`` verifies every record.
"""

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time

import numpy as np


HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, '..', '..'))
OMREAL = os.path.join(REPO, 'ai', 'omreal')
sys.path.insert(0, OMREAL)

import bfp  # noqa: E402


DEFAULT_INPUT = os.path.join(HERE, 'data', 'minimal_ext.txt')
DEFAULT_OUTPUT = os.path.join(HERE, 'data', 'core_minimal_sample.jsonl')
TAG = 'uom49-minor-minimal-core-pilot-v1'


def choose(lines, size, tag):
    ranked = []
    for chi in lines:
        digest = hashlib.sha256((tag + '\0' + chi).encode()).digest()
        ranked.append((digest, chi))
    return [chi for _, chi in sorted(ranked)[:size]]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--input', default=DEFAULT_INPUT)
    ap.add_argument('--output', default=DEFAULT_OUTPUT)
    ap.add_argument('--size', type=int, default=64)
    ap.add_argument('--tag', default=TAG)
    args = ap.parse_args(argv)

    lines = [line.strip() for line in open(args.input) if line.strip()]
    if len(lines) != len(set(lines)):
        raise SystemExit('minimal list contains duplicate chirotopes')
    if not 0 < args.size <= len(lines):
        raise SystemExit('sample size must be in 1..%d' % len(lines))
    if any(len(x) != 126 or set(x) - set('+-') for x in lines):
        raise SystemExit('minimal list contains a malformed (4,9) chirotope')
    sample = choose(lines, args.size, args.tag)
    gp = bfp.GPSystem(9, 4)
    records = []
    t0 = time.time()
    for i, text in enumerate(sample):
        chi = np.array([1 if c == '+' else -1 for c in text], dtype=np.int8)
        cert, info = bfp.find_bfp(chi, gp)
        if cert is None:
            raise SystemExit('BFP regeneration failed at sample %d: %r' % (i, info))
        terms = []
        for relation, big, small, weight in cert['terms']:
            L, Q, _ = gp.rel[relation]
            terms.append({'L': list(L), 'abcd': list(Q), 'big': int(big),
                          'small': int(small), 'w': int(weight)})
        records.append({'n': 9, 'r': 4, 'chi': text,
                        'verdict': 'NON_REALIZABLE', 'bfp': terms,
                        'sample': {'population': 'minimal_ext.txt',
                                   'population_size': len(lines),
                                   'selection': 'lowest_sha256',
                                   'tag': args.tag}})
        print('%3d/%d  support %d' % (i + 1, len(sample), len(terms)), flush=True)

    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    with open(args.output, 'w') as fh:
        for record in records:
            fh.write(json.dumps(record, sort_keys=True) + '\n')

    checker = os.path.join(OMREAL, 'checkcert.py')
    proc = subprocess.run([sys.executable, checker, args.output], text=True,
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                          env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'))
    print(proc.stdout, end='')
    if proc.returncode:
        raise SystemExit('independent checker rejected the regenerated sample')
    digest = hashlib.sha256(open(args.output, 'rb').read()).hexdigest()
    print('wrote %s (%d records, sha256 %s, %.1f s)' %
          (args.output, len(records), digest, time.time() - t0))
    return 0


if __name__ == '__main__':
    sys.exit(main())
