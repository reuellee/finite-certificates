#!/usr/bin/env python3
"""Standard-library verifier for ``data/core_shared_literal.json.gz``.

The generator is not imported.  This script rebuilds colex brackets and every
three-term GP relation.  For each pair it checks either an exact positive
dependence valid for both chirotopes or an exact strict integer solution for
all rows common to the pair.  Thus the reported fixed-labelling count rests on
finite certificates, not on LP status codes.
"""

import copy
import gzip
import hashlib
import json
import os
import sys
from itertools import combinations


HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, '..', '..'))
DEFAULT_ARTIFACT = os.path.join(HERE, 'data', 'core_shared_literal.json.gz')


def colex(n, r):
    return sorted(combinations(range(1, n + 1), r),
                  key=lambda x: tuple(reversed(x)))


def signed_sort(values):
    a = list(values)
    inversions = sum(a[i] > a[j] for i in range(len(a))
                     for j in range(i + 1, len(a)))
    return tuple(sorted(a)), -1 if inversions & 1 else 1


def build_relations(n=9, r=4):
    bases = colex(n, r)
    index = {b: i for i, b in enumerate(bases)}
    relations = []
    for L in combinations(range(1, n + 1), r - 2):
        rest = [x for x in range(1, n + 1) if x not in L]
        for Q in combinations(rest, 4):
            a, b, c, d = Q
            triplet = []
            for x, y, z, u, explicit in (
                    (a, b, c, d, 1), (a, c, b, d, -1),
                    (a, d, b, c, 1)):
                left, sl = signed_sort(L + (x, y))
                right, sr = signed_sort(L + (z, u))
                triplet.append((index[left], index[right], explicit * sl * sr))
            relations.append((L, Q, tuple(triplet)))
    return bases, relations


BASES, RELATIONS = build_relations()
RELATION_INDEX = {(L, Q): i for i, (L, Q, _) in enumerate(RELATIONS)}


def parse_chi(text):
    if not isinstance(text, str) or len(text) != len(BASES) or set(text) - set('+-'):
        raise ValueError('malformed chirotope')
    return [1 if x == '+' else -1 for x in text]


def big_signature(text):
    chi = parse_chi(text)
    answer = []
    for _, _, triplet in RELATIONS:
        signs = [sign * chi[p] * chi[q] for p, q, sign in triplet]
        if signs[0] == signs[1] == signs[2]:
            raise ValueError('GP violation')
        if signs[0] == signs[1]:
            answer.append(2)
        elif signs[0] == signs[2]:
            answer.append(1)
        else:
            answer.append(0)
    return answer


def verify_bfp(text, terms):
    chi = parse_chi(text)
    if not isinstance(terms, list) or not terms:
        return False
    total = [0] * len(BASES)
    seen = set()
    for term in terms:
        try:
            L = tuple(sorted(int(x) for x in term['L']))
            Q = tuple(int(x) for x in term['abcd'])
            big, small, weight = (int(term['big']), int(term['small']),
                                  int(term['w']))
            ri = RELATION_INDEX[(L, Q)]
        except (KeyError, TypeError, ValueError):
            return False
        if (not 0 <= big < 3 or not 0 <= small < 3 or big == small or weight <= 0 or
                (L, Q, big, small) in seen):
            return False
        seen.add((L, Q, big, small))
        triplet = RELATIONS[ri][2]
        signs = [sign * chi[p] * chi[q] for p, q, sign in triplet]
        other = [k for k in range(3) if k != big]
        if not (signs[other[0]] == signs[other[1]] != signs[big]):
            return False
        total[triplet[big][0]] += weight
        total[triplet[big][1]] += weight
        total[triplet[small][0]] -= weight
        total[triplet[small][1]] -= weight
    return not any(total)


def verify_strict(bigi, bigj, u):
    if not isinstance(u, list) or len(u) != len(BASES):
        return False
    try:
        u = [int(x) for x in u]
    except (TypeError, ValueError):
        return False
    for ri, (left, right) in enumerate(zip(bigi, bigj)):
        if left != right:
            continue
        triplet = RELATIONS[ri][2]
        for small in range(3):
            if small == left:
                continue
            value = (u[triplet[left][0]] + u[triplet[left][1]] -
                     u[triplet[small][0]] - u[triplet[small][1]])
            if value <= 0:
                return False
    return True


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, 'rb') as fh:
        for block in iter(lambda: fh.read(1 << 20), b''):
            digest.update(block)
    return digest.hexdigest()


def check(path):
    with gzip.open(path, 'rt') as fh:
        artifact = json.load(fh)
    if artifact.get('schema') != 1:
        raise ValueError('unsupported schema')
    source_path = os.path.normpath(os.path.join(REPO, artifact['input']['path']))
    if os.path.commonpath((REPO, source_path)) != REPO:
        raise ValueError('input path escapes repository')
    if sha256_file(source_path) != artifact['input']['sha256']:
        raise ValueError('input hash mismatch')
    records = [json.loads(line) for line in open(source_path) if line.strip()]
    if len(records) != artifact['input']['records']:
        raise ValueError('input record count mismatch')
    bigs = [big_signature(record['chi']) for record in records]

    expected = set(combinations(range(len(records)), 2))
    seen = set()
    positive = 0
    first_strict = None
    first_positive = None
    for result in artifact['results']:
        i, j = int(result['i']), int(result['j'])
        if (i, j) not in expected or (i, j) in seen:
            raise ValueError('missing, duplicate, or unordered pair')
        seen.add((i, j))
        shared = sum(a == b for a, b in zip(bigs[i], bigs[j]))
        if (result['shared_relations'] != shared or
                result['shared_rows'] != 2 * shared):
            raise ValueError('shared-row count mismatch at %d,%d' % (i, j))
        if result['kind'] == 'COMMON_BFP':
            if not (verify_bfp(records[i]['chi'], result['bfp']) and
                    verify_bfp(records[j]['chi'], result['bfp'])):
                raise ValueError('bad common BFP at %d,%d' % (i, j))
            positive += 1
            first_positive = first_positive or (i, j, result)
        elif result['kind'] == 'STRICT_WITNESS':
            if not verify_strict(bigs[i], bigs[j], result['u']):
                raise ValueError('bad strict witness at %d,%d' % (i, j))
            first_strict = first_strict or (i, j, result)
        else:
            raise ValueError('unknown result kind')
    if seen != expected:
        raise ValueError('pair coverage is incomplete')
    summary = artifact['summary']
    if (summary['pairs'] != len(expected) or summary['common_bfp'] != positive or
            summary['strict_witness'] != len(expected) - positive):
        raise ValueError('summary mismatch')

    # Deliberate corruptions: the all-zero vector cannot satisfy a nonempty
    # strict system, and changing one positive-circuit weight breaks its sum.
    i, j, strict = first_strict
    if verify_strict(bigs[i], bigs[j], [0] * len(BASES)):
        raise ValueError('zero-witness canary was accepted')
    if first_positive is not None:
        i, j, common = first_positive
        bad = copy.deepcopy(common['bfp'])
        bad[0]['w'] += 1
        if (verify_bfp(records[i]['chi'], bad) or
                verify_bfp(records[j]['chi'], bad)):
            raise ValueError('bad-weight canary was accepted')

    print('%d/%d fixed-labelling pairs have a common BFP' %
          (positive, len(expected)))
    print('%d strict integer witnesses and %d common positive circuits accepted' %
          (len(expected) - positive, positive))
    print('two deliberate corruptions rejected')
    print('SHARED-CORE PILOT CERTIFICATES ACCEPTED')


if __name__ == '__main__':
    try:
        check(sys.argv[1] if len(sys.argv) > 1 else DEFAULT_ARTIFACT)
    except Exception as exc:
        print('SHARED-CORE PILOT REJECTED: %s' % exc)
        sys.exit(1)
