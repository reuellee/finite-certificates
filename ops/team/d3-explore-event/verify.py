#!/usr/bin/env python3
"""Exact, stdlib-only replay of the original 56-row event and local transition.

The numerical discovery file is never read. --freeze explicitly writes the
candidate certificate; default execution compares exact frozen semantic fields.
"""
import argparse
import ast
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations
import json
from math import comb
from pathlib import Path
import struct
from time import perf_counter, process_time
import zipfile

ROOT = Path(__file__).resolve().parents[3]
OWN = Path(__file__).resolve().parent
TRIPLES = sorted(combinations(range(8), 3), key=lambda s: s[::-1])
BASES = sorted(combinations(range(8), 4), key=lambda s: s[::-1])
ACTIVE = [19, 21, 37, 38]
EXPECTED_ROOT = Q(37864449186859942661765893, 7029591949415530407677535)
EXPECTED_SIGS = [14988895318912, 3405195891438080, 40418075143643136]


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def trim(p):
    p = list(p)
    while len(p) > 1 and p[-1] == 0:
        p.pop()
    return p


def add(p, q):
    r = [Q(0)] * max(len(p), len(q))
    for i, x in enumerate(p):
        r[i] += x
    for i, x in enumerate(q):
        r[i] += x
    return trim(r)


def scale(p, x):
    return trim([x*v for v in p])


def mul(p, q):
    r = [Q(0)]*(len(p)+len(q)-1)
    for i, x in enumerate(p):
        for j, y in enumerate(q):
            r[i+j] += x*y
    return trim(r)


def det(a):
    if not a:
        return [Q(1)]
    z = [Q(0)]
    for j, x in enumerate(a[0]):
        minor = [r[:j]+r[j+1:] for r in a[1:]]
        z = add(z, scale(mul(x, det(minor)), (-1)**j))
    return z


def ev(p, t):
    z = Q(0)
    for x in reversed(p):
        z = z*t+x
    return z


def dot(a, b):
    out = [Q(0)]
    for x, y in zip(a, b):
        out = add(out, mul(x, y))
    return out


def bernstein(p, lo, hi):
    """Exact coefficients in the degree-n Bernstein basis on [lo,hi]."""
    n = len(p)-1
    powers = [sum(p[j]*comb(j, k)*lo**(j-k)*(hi-lo)**k
                  for j in range(k, n+1)) for k in range(n+1)]
    return [sum(powers[j]*Q(comb(k, j), comb(n, j))
                for j in range(k+1)) for k in range(n+1)]


def positive_on(p, lo, hi, message):
    b = bernstein(p, lo, hi)
    require(all(x > 0 for x in b), message)
    return b


def sign(x):
    return (x > 0)-(x < 0)


def npy_i8(z, name):
    raw = z.read(name+'.npy')
    require(raw[:6] == b'\x93NUMPY', 'NPY magic')
    off = 10 if raw[6] == 1 else 12
    n = struct.unpack('<H' if off == 10 else '<I', raw[8:off])[0]
    header = ast.literal_eval(raw[off:off+n].decode())
    require(header['descr'] == '<i8' and not header['fortran_order'], 'NPY integer ordering')
    data = raw[off+n:]
    return header['shape'], struct.unpack('<'+'q'*(len(data)//8), data)


def rank_exact(a):
    a = deepcopy(a)
    r = 0
    for j in range(len(a[0])):
        k = next((k for k in range(r, len(a)) if a[k][j]), None)
        if k is None:
            continue
        a[k], a[r] = a[r], a[k]
        pivot = a[r][j]
        a[r] = [v/pivot for v in a[r]]
        for k in range(len(a)):
            if k != r:
                c = a[k][j]
                a[k] = [x-c*y for x, y in zip(a[k], a[r])]
        r += 1
        if r == len(a):
            break
    return r


def serialized(value):
    if isinstance(value, Q):
        return str(value)
    if isinstance(value, dict):
        return {k: serialized(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [serialized(v) for v in value]
    return value


def verify():
    manifest = json.loads((OWN/'SOURCE_MANIFEST.json').read_text())
    for path, digest in manifest['source_sha256'].items():
        require(sha256((ROOT/path).read_bytes()).hexdigest() == digest, 'source digest '+path)
    source = json.loads((ROOT/'ops/team/ai-d3-shared-pencil-falsifier/upper_chart_0_flow.json').read_text())
    event = json.loads((ROOT/'ops/team/d3-satinj-falsifier/DISCOVERED_EVENT.json').read_text())
    with zipfile.ZipFile(ROOT/'ai/omreal/data/seeat_parent2599_upper178.npz') as z:
        shape, matrices = npy_i8(z, 'chart_matrix')
    require(shape == (178, 4, 8), 'original source chart bank')
    parent = [list(matrices[8*r:8*r+8]) for r in range(4)]
    require(parent == source['parent'] == event['parent'], 'original chart zero binding')
    require(source['signatures'] == event['signatures'] == EXPECTED_SIGS, 'original labels')
    require(event['coord'] == 1 and event['label'] == 2 and event['block'] == 0,
            'event coordinate and block')
    tstar = Q(event['root'])
    require(tstar == EXPECTED_ROOT, 'event parameter')
    lo, hi = tstar-Q(1, 1000000), tstar+Q(1, 1000000)
    y = [[[Q(v)] for v in row] for row in parent]
    y[1][1].append(Q(1))
    brackets = [det([[y[r][i] for i in b] for r in range(4)]) for b in BASES]
    require(brackets == event['parent_bracket_polynomials'], 'recomputed parent polynomials')
    parent_bernstein = []
    for i, (p, s) in enumerate(zip(brackets, source['parent_signs'])):
        require(sign(p[0]) == s and len(p) <= 2, 'source sign and structural affine bracket')
        parent_bernstein.append(positive_on(scale(p, s), lo, hi, 'parent sign over entire interval'))
    normals = [[scale(det([[y[k][j] for j in tri] for k in range(4) if k != r]), (-1)**(r+3))
                for r in range(4)] for tri in TRIPLES]
    signed = [[[scale(v, 1 if sig >> i & 1 else -1) for v in row]
               for i, row in enumerate(normals)] for sig in EXPECTED_SIGS]
    cofactors = []
    dual_bernstein = []
    for b, sp in enumerate(event['supports']):
        rows = [signed[b][i] for i in sp]
        cs = [scale(det(rows[:j]+rows[j+1:]), (-1)**j) for j in range(5)]
        require(cs == event['cofactor_polynomials'][b], 'recomputed original cofactor polynomials')
        for r in range(4):
            require(dot(cs, [row[r] for row in rows]) == [0], 'coefficientwise dual equality')
        checks = []
        for j, c in enumerate(cs):
            if b == 0 and j == 0:
                require(len(c) == 2 and c[1] > 0 and ev(c, tstar) == 0, 'simple event factor')
                require(ev(c, lo) < 0 and ev(c, hi) > 0, 'event factor side signs')
                checks.append(bernstein(scale(c, -1), lo, tstar))
                require(checks[-1][0] > 0 and checks[-1][-1] == 0, 'closed left interval event sign')
            else:
                checks.append(positive_on(scale(c, -1), lo, hi, 'negative cofactor over whole interval'))
        cofactors.append(cs)
        dual_bernstein.append(checks)
    require(event['supports'][0] == [0]+ACTIVE, 'original selected support')
    d = [signed[0][i] for i in ACTIVE]
    delta = det(d)
    require(delta == cofactors[0][0], 'active determinant is actual event cofactor')
    # Cramer's rule gives p=adj(D)1 without division, valid also at det(D)=0.
    p = [det([[[Q(1)] if k == j else v for k, v in enumerate(row)] for row in d])
         for j in range(4)]
    require(all(len(v) <= 2 for v in p), 'affine primal section')
    margins = [dot(row, p) for row in signed[0]]
    margin_bernstein = {}
    for i, m in enumerate(margins):
        if i in ACTIVE:
            require(m == delta, 'coefficientwise Cramer identity on each active row')
        else:
            margin_bernstein[str(i)] = positive_on(m, lo, hi, 'strict nonactive primal margin over interval')
    pstar = [ev(v, tstar) for v in p]
    require(any(pstar), 'nonzero event weak primal')
    require([i for i, m in enumerate(margins) if ev(m, tstar) == 0] == ACTIVE,
            'exactly four zero margins at event')
    event_rank = rank_exact([[ev(v, tstar) for v in row] for row in d])
    require(event_rank == 3, 'event active rank three')
    endpoint_records = []
    for name, t in [('left', lo), ('event', tstar), ('right', hi)]:
        weights = []
        for b, cs in enumerate(cofactors):
            c = [ev(v, t) for v in cs]
            require(sum(c) != 0, 'dual normalization denominator')
            w = [v/sum(c) for v in c]
            if name != 'right' or b != 0:
                require(all(v >= 0 for v in w), 'exact accepted endpoint dual')
            weights.append(w)
        primal_margins = [ev(m, t) for m in margins]
        if name == 'right':
            require(all(m > 0 for m in primal_margins), 'strict full 56-row right primal')
        endpoint_records.append(dict(side=name, parameter=t, full_block_badness=[name != 'right', True, True],
                                     selected_normalized_dual_weights=weights,
                                     affine_primal_point=[ev(v, t) for v in p],
                                     primal_margin_signs=[sign(m) for m in primal_margins]))
    # Deliberate false claims are rejected by the load-bearing exact predicates.
    controls = {}
    tests = {
        'event_as_strict_primal_rejected': lambda: require(all(ev(m, tstar) > 0 for m in margins), 'false event primal'),
        'right_as_selected_dual_rejected': lambda: require(all(v >= 0 for v in endpoint_records[2]['selected_normalized_dual_weights'][0]), 'false right dual'),
        'negated_right_primal_rejected': lambda: require(all(-ev(m, hi) > 0 for m in margins), 'negative primal'),
        'shifted_event_rejected': lambda: require(ev(delta, hi) == 0, 'shifted event'),
        'omitted_active_margin_rejected': lambda: require(len([m for i, m in enumerate(margins) if i != ACTIVE[0]]) == 56, '56-row denominator'),
    }
    for name, test in tests.items():
        try:
            test()
        except AssertionError:
            controls[name] = True
    require(len(controls) == len(tests), 'hostile controls')
    return serialized(dict(
        classification='FINITE_EXACT_LOCAL_TRANSITION_WITH_DEDUCTIVE_GERM',
        canonical_base_revision=manifest['canonical_base_revision'],
        opening_revision=manifest['opening_revision'],
        source_sha256=manifest['source_sha256'],
        signatures=EXPECTED_SIGS, event_parameter=tstar, closed_interval=[lo, hi],
        active_support=ACTIVE, active_labels=[''.join(str(j+1) for j in TRIPLES[i]) for i in ACTIVE],
        event_factor=delta, event_factor_derivative=delta[1], primal_section_coefficients=p,
        nonactive_margin_polynomials={str(i): m for i, m in enumerate(margins) if i not in ACTIVE},
        nonactive_margin_bernstein=margin_bernstein, parent_bracket_bernstein=parent_bernstein,
        original_dual_cofactor_bernstein=dual_bernstein, endpoint_records=endpoint_records,
        event_active_rank=event_rank, normalized_block0_witness_fiber_at_event='singleton',
        full_badness_on_closed_left_interval=[True, True, True],
        full_badness_on_open_right_half_interval=[False, True, True],
        local_germ=dict(neighborhood='U defined by strict polynomial inequalities in FINDINGS.md',
                        block0_bad='Delta <= 0', block0_good='Delta > 0',
                        blocks1_and2_bad_everywhere=True, exclusive_pair_12='Delta > 0',
                        boundary='Delta = 0', boundary_smooth=True),
        exact_56_row_primal_checks=56, other_primal_margins_strict_over_interval=52,
        parent_sign_denominator=70, coefficientwise_dual_equalities=12,
        hostile_controls=controls, original_obligations_closed=0, theorem_credit=0,
        global_attachment=False, ledger='2/9'))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--freeze', action='store_true')
    args = parser.parse_args()
    wall, cpu = perf_counter(), process_time()
    result = verify()
    target = OWN/'CERTIFICATE.json'
    if args.freeze:
        target.write_text(json.dumps(result, indent=2)+'\n')
    else:
        require(json.loads(target.read_text()) == result, 'frozen exact certificate semantic equality')
    print(json.dumps(dict(status='PASS', classification=result['classification'],
                          left=result['full_badness_on_closed_left_interval'],
                          right=result['full_badness_on_open_right_half_interval'],
                          event_full_witness_fiber=result['normalized_block0_witness_fiber_at_event'],
                          local_germ=result['local_germ'], hostile_controls=len(result['hostile_controls']),
                          wall_seconds=perf_counter()-wall, cpu_seconds=process_time()-cpu)))


if __name__ == '__main__':
    main()
