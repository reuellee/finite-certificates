#!/usr/bin/env python3
"""Independent exact checker for ``data/core_minimal_pilot.json.gz``.

This verifier imports no project module and does not trust the producer's GP
tables, matching code, counts, or source-file summaries.  It rebuilds colex
bases and all three-term relations, verifies every source Gordan vector with
integer arithmetic, transports every emitted coverage pointer, and verifies
the transported Gordan vector against the target chirotope.

The pointer list is a *positive coverage certificate*.  This checker proves
that every declared match is sound; it deliberately does not reproduce the
producer's exhaustive search for additional matches.  Missing pointers could
only make the measured compression look worse, not create a false pruning
rule or a false coverage claim for a listed target.
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
DEFAULT_REPORT = os.path.join(HERE, 'data', 'core_minimal_pilot.json.gz')


def bases_colex(n, r):
    return sorted(combinations(range(1, n + 1), r),
                  key=lambda b: tuple(reversed(b)))


def ordered(values):
    a = list(values)
    parity = 1
    for i in range(len(a)):
        for j in range(i + 1, len(a)):
            if a[i] > a[j]:
                parity = -parity
    return tuple(sorted(a)), parity


def chi_values(text, expected):
    if not isinstance(text, str) or len(text) != expected:
        raise ValueError('bad chirotope length')
    ans = []
    for ch in text:
        if ch not in '+-':
            raise ValueError('bad chirotope character')
        ans.append(1 if ch == '+' else -1)
    return ans


def gp_triplet(L, Q, index):
    a, b, c, d = Q
    raw = ((a, b, c, d, 1), (a, c, b, d, -1),
           (a, d, b, c, 1))
    result = []
    for x, y, z, u, sign in raw:
        left, sl = ordered(tuple(L) + (x, y))
        right, sr = ordered(tuple(L) + (z, u))
        result.append((index[left], index[right], sign * sl * sr))
    return result


def odd_term(chi, triplet):
    signs = [s * chi[i] * chi[j] for i, j, s in triplet]
    if signs[0] == signs[1] == signs[2]:
        raise ValueError('GP violation')
    for k in range(3):
        other = [x for x in range(3) if x != k]
        if signs[other[0]] == signs[other[1]] != signs[k]:
            return k
    raise AssertionError('no odd GP term')


def verify_bfp(chi_text, terms, n=9, r=4):
    bases = bases_colex(n, r)
    index = {b: i for i, b in enumerate(bases)}
    chi = chi_values(chi_text, len(bases))
    if not isinstance(terms, list) or not terms:
        return False, 'empty certificate'
    total = [0] * len(bases)
    seen = set()
    for term in terms:
        try:
            L = tuple(sorted(int(x) for x in term['L']))
            Q = tuple(int(x) for x in term['abcd'])
            big = int(term['big'])
            small = int(term['small'])
            weight = int(term['w'])
        except (KeyError, TypeError, ValueError):
            return False, 'malformed term'
        if (len(L) != r - 2 or len(set(L)) != r - 2 or
                len(Q) != 4 or tuple(sorted(Q)) != Q or len(set(Q)) != 4 or
                set(L) & set(Q) or any(x < 1 or x > n for x in L + Q)):
            return False, 'malformed relation'
        if not (0 <= big < 3 and 0 <= small < 3 and big != small and weight > 0):
            return False, 'bad BIG/SMALL/weight'
        key = (L, Q, big, small)
        if key in seen:
            return False, 'duplicate inequality'
        seen.add(key)
        triplet = gp_triplet(L, Q, index)
        try:
            actual = odd_term(chi, triplet)
        except ValueError as exc:
            return False, str(exc)
        if actual != big:
            return False, 'claimed BIG is not odd'
        total[triplet[big][0]] += weight
        total[triplet[big][1]] += weight
        total[triplet[small][0]] -= weight
        total[triplet[small][1]] -= weight
    if any(total):
        return False, 'weighted rows do not cancel'
    return True, 'exact Gordan vector'


PAIRINGS = (
    ((0, 1), (2, 3)),
    ((0, 2), (1, 3)),
    ((0, 3), (1, 2)),
)


def transported_index(Q, which, permutation):
    pair_set = {frozenset((permutation[Q[a] - 1], permutation[Q[b] - 1]))
                for a, b in PAIRINGS[which]}
    mapped_q = tuple(sorted(permutation[x - 1] for x in Q))
    for k, spec in enumerate(PAIRINGS):
        candidate = {frozenset((mapped_q[a], mapped_q[b])) for a, b in spec}
        if candidate == pair_set:
            return k
    raise AssertionError('transport did not preserve a perfect matching')


def transport_terms(terms, permutation):
    if sorted(permutation) != list(range(1, 10)):
        raise ValueError('not a permutation of 1..9')
    result = []
    for term in terms:
        L = tuple(sorted(int(x) for x in term['L']))
        Q = tuple(int(x) for x in term['abcd'])
        result.append({
            'L': sorted(permutation[x - 1] for x in L),
            'abcd': sorted(permutation[x - 1] for x in Q),
            'big': transported_index(Q, int(term['big']), permutation),
            'small': transported_index(Q, int(term['small']), permutation),
            'w': int(term['w']),
        })
    return result


def core_conditions(terms):
    result = {}
    for term in terms:
        L = tuple(sorted(int(x) for x in term['L']))
        Q = tuple(int(x) for x in term['abcd'])
        big = int(term['big'])
        key = (L, Q)
        if key in result and result[key] != big:
            raise ValueError('inconsistent BIG condition')
        result[key] = big
    return [{'L': list(k[0]), 'abcd': list(k[1]), 'big': result[k]}
            for k in sorted(result)]


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, 'rb') as fh:
        while True:
            block = fh.read(1048576)
            if not block:
                break
            digest.update(block)
    return digest.hexdigest()


def source_records(report):
    declared = {entry['path']: entry for entry in report['sources']}
    loaded = {}
    for relative, meta in declared.items():
        path = os.path.normpath(os.path.join(REPO, relative))
        if os.path.commonpath((REPO, path)) != REPO:
            raise ValueError('source path escapes repository')
        if sha256_file(path) != meta['sha256'] or os.path.getsize(path) != meta['bytes']:
            raise ValueError('source hash or size mismatch: ' + relative)
        with open(path) as fh:
            loaded[relative] = [json.loads(line) for line in fh if line.strip()]
    return loaded


def greedy(sets, universe):
    left = set(universe)
    result = []
    while left:
        best = max(range(len(sets)), key=lambda i: len(sets[i] & left))
        gain = sets[best] & left
        if not gain:
            break
        result.append({'core': best, 'new': len(gain)})
        left -= gain
    return result, sorted(left)


def exact_small_cover(sets, universe, max_k):
    universe = set(universe)
    answer = []
    for k in range(1, max_k + 1):
        best_n, best_choice = -1, None
        for choice in combinations(range(len(sets)), k):
            covered = set().union(*(sets[i] for i in choice)) & universe
            if len(covered) > best_n:
                best_n, best_choice = len(covered), choice
        answer.append({'k': k, 'covered': best_n,
                       'cores': list(best_choice or ())})
    return answer


def split_indices(rows):
    train, test = [], []
    for i, row in enumerate(rows):
        value = int(hashlib.sha256(('split:' + row['chi']).encode()).hexdigest(), 16)
        (train if value & 1 else test).append(i)
    return train, test


def check_pointer(core, target_chi, permutation):
    try:
        transported = transport_terms(core['bfp'], permutation)
    except (KeyError, TypeError, ValueError) as exc:
        return False, str(exc)
    return verify_bfp(target_chi, transported)


def run_canaries(report, combined):
    failures = []

    def reject(name, ok):
        if ok:
            failures.append(name)

    core = report['cores'][0]
    source_chi = report['nonreal'][core['source']]['chi']

    bad = copy.deepcopy(core['bfp'])
    bad[0]['w'] += 1
    reject('altered weight', verify_bfp(source_chi, bad)[0])

    bad = copy.deepcopy(core['bfp'])
    bad[0]['big'] = bad[0]['small']
    reject('changed BIG', verify_bfp(source_chi, bad)[0])

    bad = copy.deepcopy(core['bfp'])
    del bad[0]
    reject('dropped row', verify_bfp(source_chi, bad)[0])

    pointer = next(p for p in report['coverage_pointers'] if p['core'] == 0)
    target_chi = combined[pointer['target']]['chi']
    caught = False
    for a in range(8):
        for b in range(a + 1, 9):
            perm = list(pointer['permutation'])
            perm[a], perm[b] = perm[b], perm[a]
            if not check_pointer(core, target_chi, perm)[0]:
                caught = True
                break
        if caught:
            break
    if not caught:
        failures.append('corrupted permutation')

    real_index = len(report['nonreal'])
    reject('pointer transplanted to realizable control',
           check_pointer(core, combined[real_index]['chi'],
                         pointer['permutation'])[0])
    return failures


def check(path):
    opener = gzip.open if path.endswith('.gz') else open
    with opener(path, 'rt') as fh:
        report = json.load(fh)
    if report.get('schema') != 1 or (report.get('n'), report.get('r')) != (9, 4):
        raise ValueError('unsupported report schema or cell')
    loaded = source_records(report)
    nonreal = report['nonreal']
    real = report['realizable']
    combined = nonreal + real
    if len({x['chi'] for x in combined}) != len(combined):
        raise ValueError('duplicate target chirotope')

    for row, verdict in [(x, 'NON_REALIZABLE') for x in nonreal] + \
                        [(x, 'REALIZABLE') for x in real]:
        records = loaded.get(row['source'])
        if records is None or not 1 <= int(row['line']) <= len(records):
            raise ValueError('bad source pointer')
        source = records[int(row['line']) - 1]
        if source.get('chi') != row['chi'] or source.get('verdict') != verdict:
            raise ValueError('target does not match source record')

    for i, core in enumerate(report['cores']):
        src = nonreal[int(core['source'])]
        source = loaded[src['source']][int(src['line']) - 1]
        if source.get('bfp') != core.get('bfp'):
            raise ValueError('core %d BFP differs from source' % i)
        ok, why = verify_bfp(src['chi'], core['bfp'])
        if not ok:
            raise ValueError('core %d invalid: %s' % (i, why))
        if core_conditions(core['bfp']) != core['conditions']:
            raise ValueError('core %d conditions are not its BFP support' % i)

    pairs = set()
    sets = [set() for _ in report['cores']]
    for pointer in report['coverage_pointers']:
        i, j = int(pointer['core']), int(pointer['target'])
        if not (0 <= i < len(report['cores']) and 0 <= j < len(combined)):
            raise ValueError('coverage pointer out of range')
        if (i, j) in pairs:
            raise ValueError('duplicate coverage pointer')
        pairs.add((i, j))
        ok, why = check_pointer(report['cores'][i], combined[j]['chi'],
                                pointer['permutation'])
        if not ok:
            raise ValueError('bad pointer core %d -> target %d: %s' % (i, j, why))
        if j >= len(nonreal):
            raise ValueError('BFP core points to a realizable control')
        sets[i].add(j)

    for i, core in enumerate(report['cores']):
        if sorted(sets[i]) != core['relabelled_targets']:
            raise ValueError('core %d target list differs from pointers' % i)
        if i not in sets[i]:
            raise ValueError('core %d does not cover its source' % i)

        literal = []
        identity = list(range(1, 10))
        for j, target in enumerate(combined):
            if check_pointer(core, target['chi'], identity)[0]:
                literal.append(j)
        if literal != core['literal_targets']:
            raise ValueError('core %d literal target list is incomplete' % i)

    chosen, missing = greedy(sets, range(len(nonreal)))
    if chosen != report['greedy_cover'] or missing != report['greedy_uncovered']:
        raise ValueError('greedy cover summary mismatch')
    gate_k = int(0.05 * len(nonreal))
    small = exact_small_cover(sets, range(len(nonreal)), gate_k)
    if small != report['exact_small_cover']:
        raise ValueError('exact small-cover result mismatch')
    need90 = (9 * len(nonreal) + 9) // 10
    cumulative = 0
    greedy90 = None
    for step, item in enumerate(chosen, 1):
        cumulative += item['new']
        if cumulative >= need90:
            greedy90 = step
            break

    train, test = split_indices(nonreal)
    train_coverage = set().union(*(sets[i] for i in train)) if train else set()
    test_covered = sorted(set(test) & train_coverage)
    if report['heldout'] != {'train': train, 'test': test,
                             'test_covered': test_covered}:
        raise ValueError('held-out split or coverage mismatch')
    cross = sorted(j for j in range(len(nonreal))
                   if any(j in sets[i] for i in range(len(sets)) if i != j))
    if cross != report['cross_covered']:
        raise ValueError('cross-coverage list mismatch')

    counts = report['counts']
    condition_sizes = sorted(len(core['conditions']) for core in report['cores'])
    if (counts['nonreal_bfp'] != len(nonreal) or
            counts['realizable_controls'] != len(real) or
            counts['greedy_cover_size'] != len(chosen) or
            counts['greedy_cores_for_90pct'] != greedy90 or
            counts['five_percent_core_budget'] != gate_k or
            counts['exact_best_coverage_at_budget'] != small[-1]['covered'] or
            counts['core_conditions_min'] != condition_sizes[0] or
            counts['core_conditions_median'] != condition_sizes[len(condition_sizes) // 2] or
            counts['core_conditions_max'] != condition_sizes[-1] or
            counts['literal_cross_covered'] != sum(
                any(j in report['cores'][i]['literal_targets']
                    for i in range(len(sets)) if i != j)
                for j in range(len(nonreal))) or
            counts['relabelled_cross_covered'] != len(cross) or
            counts['heldout_train'] != len(train) or
            counts['heldout_test'] != len(test) or
            counts['heldout_test_covered'] != len(test_covered) or
            counts['realizable_false_matches'] != 0):
        raise ValueError('count summary mismatch')
    expected_decision = 'PASS' if small[-1]['covered'] >= need90 else 'FAIL'
    if report['go_no_go']['decision'] != expected_decision:
        raise ValueError('go/no-go decision mismatch')

    canary_failures = run_canaries(report, combined)
    if canary_failures:
        raise ValueError('canaries failed: ' + ', '.join(canary_failures))
    print('core pilot: %d exact BFP cores, %d exact coverage pointers' %
          (len(report['cores']), len(report['coverage_pointers'])))
    print('realizable controls: %d, false matches: 0' % len(real))
    print('greedy certified cover: %d cores cover %d/%d pilot non-realizable rows' %
          (len(chosen), len(nonreal) - len(missing), len(nonreal)))
    print('five deliberate corruptions rejected')
    print('CORE PILOT CERTIFICATES ACCEPTED')


if __name__ == '__main__':
    try:
        check(sys.argv[1] if len(sys.argv) > 1 else DEFAULT_REPORT)
    except Exception as exc:
        print('CORE PILOT REJECTED: %s' % exc)
        sys.exit(1)
