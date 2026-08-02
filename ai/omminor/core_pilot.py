#!/usr/bin/env python3
"""Exact pilot for reusable BFP cores at UOM(4,9).

This is a *measurement producer*, not a verifier and not a realizability
solver.  It reads already-certified biquadratic-final-polynomial records,
extracts the partial GP signature needed by each certificate, and measures
whether that signature occurs in other chirotopes, modulo relabelling.

The central matching test is exact and combinatorial.  A BFP term names a
three-term GP relation and its odd (BIG) matching of four elements.  Under an
element permutation the relation and the matching are merely transported.
Reorientation is irrelevant because it multiplies all three terms of a GP
relation by one common sign.

The relabelling search is shared across every target by representing the set
of still-compatible targets as one Python integer bitset.  It is exhaustive
over S_n, but backtracks as soon as a completed GP condition leaves no target.

Default corpus (all checked in):

* 64 deterministically sampled classes from the tracked 1,758-class
  minor-minimal prefix, with freshly regenerated exact BFP certificates; and
* 206 exact realizable controls, on which a match is a fatal soundness bug.

The population is depth-prefix biased and the sample is small.  The output is
therefore a preregistered raw-core pilot, not a cell-wide theorem.

Usage:

    python ai/omminor/core_pilot.py
    python ai/omminor/core_pilot.py --out /tmp/core_pilot.json
    python ai/omminor/core_pilot.py --nonreal FILE.jsonl [FILE.jsonl ...]
"""

import argparse
import gzip
import hashlib
import json
import os
import sys
import time
from itertools import combinations


HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, '..', '..'))
DEFAULT_NONREAL = [
    os.path.join(HERE, 'data', 'core_minimal_sample.jsonl'),
]
DEFAULT_REAL = [
    os.path.join(REPO, 'ai', 'omopen', 'data',
                 'validation_realizable.jsonl'),
    os.path.join(REPO, 'ai', 'omopen', 'data', 'certs_realizable.jsonl'),
]
DEFAULT_OUT = os.path.join(HERE, 'data', 'core_minimal_pilot.json.gz')


def colex(n, r):
    return sorted(combinations(range(1, n + 1), r),
                  key=lambda x: tuple(reversed(x)))


def sort_sign(values):
    a = list(values)
    sign = 1
    for i in range(1, len(a)):
        j = i
        while j and a[j - 1] > a[j]:
            a[j - 1], a[j] = a[j], a[j - 1]
            sign = -sign
            j -= 1
    return tuple(a), sign


def relation_terms(L, Q, bidx):
    """Normalized GP terms for sorted L and Q=(a<b<c<d)."""
    a, b, c, d = Q
    ans = []
    for x, y, z, u, explicit in (
            (a, b, c, d, 1),
            (a, c, b, d, -1),
            (a, d, b, c, 1)):
        p, sp = sort_sign(tuple(L) + (x, y))
        q, sq = sort_sign(tuple(L) + (z, u))
        ans.append((bidx[p], bidx[q], explicit * sp * sq))
    return tuple(ans)


def relation_big(chi, trip):
    signs = [sg * chi[p] * chi[q] for p, q, sg in trip]
    if signs[0] == signs[1] == signs[2]:
        raise ValueError('sign string violates a GP relation')
    if signs[0] == signs[1]:
        return 2
    if signs[0] == signs[2]:
        return 1
    return 0


def relation_code(L, Q):
    lm = sum(1 << (x - 1) for x in L)
    qm = sum(1 << (x - 1) for x in Q)
    return (lm << 9) | qm


def parse_chi(text, n=9, r=4):
    bases = colex(n, r)
    if len(text) != len(bases):
        raise ValueError('chi length %d, expected %d' % (len(text), len(bases)))
    try:
        return tuple(1 if c == '+' else -1 if c == '-' else 0 for c in text)
    except TypeError:
        raise ValueError('chi is not text')


def full_big_signature(text, n=9, r=4):
    chi = parse_chi(text, n, r)
    if 0 in chi:
        raise ValueError('chi contains a character other than + or -')
    bases = colex(n, r)
    bidx = {b: i for i, b in enumerate(bases)}
    out = {}
    for L in combinations(range(1, n + 1), r - 2):
        rest = [x for x in range(1, n + 1) if x not in L]
        for Q in combinations(rest, 4):
            out[relation_code(L, Q)] = relation_big(
                chi, relation_terms(L, Q, bidx))
    return out


PAIR_INDEX = (
    ((0, 1), (2, 3)),
    ((0, 2), (1, 3)),
    ((0, 3), (1, 2)),
)


def condition_from_term(term):
    L = tuple(sorted(int(x) for x in term['L']))
    Q = tuple(sorted(int(x) for x in term['abcd']))
    big = int(term['big'])
    if len(L) != 2 or len(set(L)) != 2 or len(Q) != 4 or len(set(Q)) != 4:
        raise ValueError('malformed (4,9) GP term')
    if set(L) & set(Q) or not 0 <= big < 3:
        raise ValueError('malformed (4,9) GP term')
    pairs = tuple(tuple(Q[i] for i in pair) for pair in PAIR_INDEX[big])
    return (L, Q, big, pairs)


def extract_core(rec):
    if (int(rec.get('n', -1)), int(rec.get('r', -1))) != (9, 4):
        return None
    if rec.get('verdict') != 'NON_REALIZABLE' or not rec.get('bfp'):
        return None
    conditions = {}
    for term in rec['bfp']:
        c = condition_from_term(term)
        key = (c[0], c[1])
        old = conditions.get(key)
        if old is not None and old[2] != c[2]:
            raise ValueError('one relation has two BIG terms')
        conditions[key] = c
    return tuple(sorted(conditions.values(), key=lambda c: (c[0], c[1], c[2])))


def load_records(paths, want, require_bfp=False):
    seen = set()
    rows = []
    for path in paths:
        with open(path) as fh:
            for line_no, line in enumerate(fh, 1):
                if not line.strip():
                    continue
                rec = json.loads(line)
                if (int(rec.get('n', -1)), int(rec.get('r', -1))) != (9, 4):
                    continue
                if rec.get('verdict') != want:
                    continue
                if require_bfp and not rec.get('bfp'):
                    continue
                chi = rec.get('chi')
                parse_chi(chi)
                if chi in seen:
                    continue
                seen.add(chi)
                rows.append({
                    'rec': rec,
                    'chi': chi,
                    'source': os.path.relpath(path, REPO),
                    'line': line_no,
                    'id': hashlib.sha256(chi.encode()).hexdigest()[:16],
                })
    return rows


def pairing_index(values):
    """Index of pairs (v0,v1)|(v2,v3) after sorting their four labels."""
    pairs = {frozenset(values[:2]), frozenset(values[2:])}
    q = sorted(values)
    for k, spec in enumerate(PAIR_INDEX):
        trial = {frozenset((q[a], q[b])) for a, b in spec}
        if trial == pairs:
            return k
    raise AssertionError('not a perfect matching')


def transformed_condition(c, mapping):
    L, Q, _, pairs = c
    ml = tuple(sorted(mapping[x] for x in L))
    mq = tuple(sorted(mapping[x] for x in Q))
    vals = tuple(mapping[x] for pair in pairs for x in pair)
    return relation_code(ml, mq), pairing_index(vals)


def condition_schedule(core):
    """Choose a source-element order that exposes many conditions early."""
    by_support = {}
    for c in core:
        support = frozenset(c[0] + c[1])
        by_support.setdefault(support, []).append(c)
    first = max(by_support, key=lambda s: (len(by_support[s]), tuple(sorted(s))))
    order = list(sorted(first))
    remaining = set(range(1, 10)) - set(first)
    while remaining:
        assigned = set(order)
        nxt = max(remaining, key=lambda x: (
            sum(set(c[0] + c[1]) <= assigned | {x} for c in core), -x))
        order.append(nxt)
        remaining.remove(nxt)
    pos = {x: i for i, x in enumerate(order)}
    at_depth = [[] for _ in order]
    for c in core:
        at_depth[max(pos[x] for x in c[0] + c[1])].append(c)
    for bucket in at_depth:
        bucket.sort(key=lambda c: (c[0], c[1], c[2]))
    return tuple(order), at_depth


def exhaustive_matches(core, targets):
    """Return target-index -> source-to-target permutation for every match."""
    signatures = [t['signature'] for t in targets]
    lookup = {}
    for i, sig in enumerate(signatures):
        bit = 1 << i
        for code, big in sig.items():
            lookup[(code, big)] = lookup.get((code, big), 0) | bit
    wanted = (1 << len(targets)) - 1
    found = {}
    order, at_depth = condition_schedule(core)
    mapping = [0] * 10
    nodes = [0]

    def visit(depth, unused, compatible):
        nonlocal wanted
        compatible &= wanted
        if not compatible:
            return
        nodes[0] += 1
        if depth == 9:
            perm = tuple(mapping[x] for x in range(1, 10))
            bits = compatible
            while bits:
                low = bits & -bits
                idx = low.bit_length() - 1
                found[idx] = perm
                bits ^= low
            wanted &= ~compatible
            return
        src = order[depth]
        bits = unused
        while bits and compatible & wanted:
            low = bits & -bits
            target = low.bit_length()  # bit 0 represents label 1
            mapping[src] = target
            ok = compatible & wanted
            for c in at_depth[depth]:
                code, big = transformed_condition(c, mapping)
                ok &= lookup.get((code, big), 0)
                if not ok:
                    break
            if ok:
                visit(depth + 1, unused ^ low, ok)
            mapping[src] = 0
            bits ^= low

    visit(0, (1 << 9) - 1, wanted)
    return found, nodes[0], order


def literal_match(core, signature):
    identity = [0] + list(range(1, 10))
    return all(signature.get(code) == big
               for code, big in (transformed_condition(c, identity)
                                 for c in core))


def greedy_cover(cover_sets, universe):
    uncovered = set(universe)
    chosen = []
    while uncovered:
        best = max(range(len(cover_sets)),
                   key=lambda i: len(cover_sets[i] & uncovered))
        gain = cover_sets[best] & uncovered
        if not gain:
            break
        chosen.append({'core': best, 'new': len(gain)})
        uncovered -= gain
    return chosen, sorted(uncovered)


def exact_best_small_cover(cover_sets, universe, max_k):
    """Maximum covered rows by at most k cores, for the small pilot gate."""
    universe = set(universe)
    answer = []
    for k in range(1, max_k + 1):
        best_n, best_choice = -1, None
        for choice in combinations(range(len(cover_sets)), k):
            covered = set().union(*(cover_sets[i] for i in choice)) & universe
            if len(covered) > best_n:
                best_n, best_choice = len(covered), choice
        answer.append({'k': k, 'covered': best_n,
                       'cores': list(best_choice or ())})
    return answer


def deterministic_split(rows):
    train, test = [], []
    for i, row in enumerate(rows):
        value = int(hashlib.sha256(('split:' + row['chi']).encode()).hexdigest(), 16)
        (train if value & 1 else test).append(i)
    return train, test


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        for block in iter(lambda: fh.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--nonreal', nargs='+', default=DEFAULT_NONREAL)
    ap.add_argument('--real', nargs='+', default=DEFAULT_REAL)
    ap.add_argument('--out', default=DEFAULT_OUT)
    args = ap.parse_args(argv)

    nonreal = load_records(args.nonreal, 'NON_REALIZABLE', require_bfp=True)
    real = load_records(args.real, 'REALIZABLE')
    if not nonreal:
        raise SystemExit('no (4,9) BFP records found')
    all_targets = nonreal + real
    for row in all_targets:
        row['signature'] = full_big_signature(row['chi'])

    cores = []
    for row in nonreal:
        core = extract_core(row['rec'])
        if core is None:
            raise AssertionError('filtered record has no core')
        cores.append(core)

    print('corpus: %d BFP classes, %d realizable controls' %
          (len(nonreal), len(real)))
    print('core conditions: min %d, median %d, max %d' % (
        min(map(len, cores)), sorted(map(len, cores))[len(cores) // 2],
        max(map(len, cores))))

    literal = []
    relabel = []
    match_permutations = []
    search_nodes = []
    orders = []
    t0 = time.time()
    for i, core in enumerate(cores):
        lit = {j for j, target in enumerate(all_targets)
               if literal_match(core, target['signature'])}
        matches, nodes, order = exhaustive_matches(core, all_targets)
        got = set(matches)
        if not lit <= got:
            raise AssertionError('relabelled matcher lost a literal match')
        if i not in got:
            raise AssertionError('a source core did not match its own class')
        if any(j >= len(nonreal) for j in got):
            raise AssertionError('BFP core matched an exact realizable control')
        literal.append(lit)
        relabel.append(got)
        match_permutations.append(matches)
        search_nodes.append(nodes)
        orders.append(order)
        print('  core %3d/%d: %3d conditions; literal %2d; relabelled %2d; '
              '%d nodes' % (i + 1, len(cores), len(core), len(lit), len(got), nodes))

    nr_universe = set(range(len(nonreal)))
    chosen, missed = greedy_cover(relabel, nr_universe)
    gate_k = int(0.05 * len(nonreal))
    small_cover = exact_best_small_cover(relabel, nr_universe, gate_k)
    need90 = (9 * len(nonreal) + 9) // 10
    running = 0
    greedy90 = None
    for step, item in enumerate(chosen, 1):
        running += item['new']
        if running >= need90:
            greedy90 = step
            break
    train, test = deterministic_split(nonreal)
    train_coverage = set().union(*(relabel[i] for i in train)) if train else set()
    test_covered = sorted(set(test) & train_coverage)
    cross_covered = sorted(j for j in nr_universe
                           if any(j in relabel[i] for i in nr_universe if i != j))

    pointers = []
    for i, matches in enumerate(relabel):
        for j in sorted(matches):
            pointers.append({'core': i, 'target': j,
                             'permutation': list(match_permutations[i][j])})

    sources = []
    for p in args.nonreal + args.real:
        sources.append({'path': os.path.relpath(p, REPO),
                        'sha256': sha256_file(p),
                        'bytes': os.path.getsize(p)})
    report = {
        'schema': 1,
        'scope': ('deterministic sample of the tracked 1,758-class '
                  'minor-minimal prefix; not UOM(4,9) coverage'),
        'n': 9,
        'r': 4,
        'sources': sources,
        'counts': {
            'nonreal_bfp': len(nonreal),
            'realizable_controls': len(real),
            'core_conditions_min': min(map(len, cores)),
            'core_conditions_median': sorted(map(len, cores))[len(cores) // 2],
            'core_conditions_max': max(map(len, cores)),
            'literal_cross_covered': sum(any(j in literal[i] for i in nr_universe
                                             if i != j) for j in nr_universe),
            'relabelled_cross_covered': len(cross_covered),
            'greedy_cover_size': len(chosen),
            'greedy_cores_for_90pct': greedy90,
            'five_percent_core_budget': gate_k,
            'exact_best_coverage_at_budget': (small_cover[-1]['covered']
                                               if small_cover else 0),
            'heldout_train': len(train),
            'heldout_test': len(test),
            'heldout_test_covered': len(test_covered),
            'realizable_false_matches': 0,
            'wall_seconds': round(time.time() - t0, 3),
            'search_nodes_total': sum(search_nodes),
        },
        'go_no_go': {
            'eligible_for': 'reuse of unoptimized emitted BFP cores only',
            'decision': ('PASS' if small_cover and
                         small_cover[-1]['covered'] >= need90 else 'FAIL'),
            'reason': ('The alternative completion-tree node gate was not '
                       'measured. Alternative certificates are not ruled out.'),
            'preregistered_gate': ('at most 5% as many core orbits as pilot '
                                   'non-realizable classes cover 90%, or held-out '
                                   'tree visits at most 10% of baseline'),
        },
        'nonreal': [{'id': x['id'], 'source': x['source'], 'line': x['line'],
                     'chi': x['chi']} for x in nonreal],
        'realizable': [{'id': x['id'], 'source': x['source'], 'line': x['line'],
                        'chi': x['chi']} for x in real],
        'cores': [{
            'source': i,
            'conditions': [{'L': list(c[0]), 'abcd': list(c[1]), 'big': c[2]}
                           for c in core],
            'bfp': nonreal[i]['rec']['bfp'],
            'literal_targets': sorted(literal[i]),
            'relabelled_targets': sorted(relabel[i]),
            'search_order': list(orders[i]),
            'search_nodes': search_nodes[i],
        } for i, core in enumerate(cores)],
        'coverage_pointers': pointers,
        'greedy_cover': chosen,
        'greedy_uncovered': missed,
        'exact_small_cover': small_cover,
        'heldout': {'train': train, 'test': test, 'test_covered': test_covered},
        'cross_covered': cross_covered,
    }
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    opener = gzip.open if args.out.endswith('.gz') else open
    with opener(args.out, 'wt') as fh:
        json.dump(report, fh, indent=1, sort_keys=True)
        fh.write('\n')
    print('wrote %s' % args.out)
    print(json.dumps(report['counts'], indent=1, sort_keys=True))
    return 0


if __name__ == '__main__':
    sys.exit(main())
