#!/usr/bin/env python3
"""Sabotage canaries: certificates that MUST be rejected.

    python canaries.py            (or: python attack.py canaries)

A checker that accepts everything proves nothing.  This file builds honest
certificates of every kind ai/omopen emits, then corrupts each one in a way
a plausible bug would produce, and demands that the checker say no -- with a
diagnosis that names the corruption, not a generic parse error.

Both checkers are exercised:

  * `fpcheck.py`  -- this directory's independent checker, on GORDAN,
    NO_FINAL_POLYNOMIAL, FP and REALIZABLE records;
  * `ai/omreal/checkcert.py` -- the project's older independent checker, on
    the level-0 Gordan certificates re-expressed in its `bfp` schema and on
    the realization certificates.  Getting past two checkers that share no
    code is the point.

Every canary is written to `data/canaries.jsonl` with its expected
diagnosis, so the run is reproducible and the failures are auditable.
"""

import copy
import json
import os
import sys

sys.dont_write_bytecode = True
for _v in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS',
           'NUMEXPR_NUM_THREADS'):
    os.environ.setdefault(_v, '1')

import numpy as np                                          # noqa: E402

import catalog                                              # noqa: E402
import fpcheck                                              # noqa: E402
import gordan                                               # noqa: E402
import weaponA                                              # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, 'data')
N, R = 9, 4

sys.path.insert(0, catalog.OMREAL)
import checkcert as omcheck                                 # noqa: E402


def run(a=None):
    os.makedirs(DATA, exist_ok=True)
    sup0 = gordan.Support(N, R, 'L0', verify=True, trials=40)
    sup1 = gordan.Support(N, R, 'L1', verify=True, trials=40)
    print('identity tables verified exactly on %d random integer '
          'configurations each' % sup0.verified)

    rng = np.random.default_rng(99)
    nr = catalog.rows_with_status(catalog.NONREAL)
    wk = catalog.rows_with_status(catalog.WALK)
    row_nr = int(rng.choice(nr))
    row_wk = int(rng.choice(wk))
    row_wk2 = int(rng.choice(wk))
    chi_nr = catalog.chi_of_rows([row_nr])[0]
    chi_wk = catalog.chi_of_rows([row_wk])[0]
    chi_wk2 = catalog.chi_of_rows([row_wk2])[0]
    s_nr, s_wk, s_wk2 = (catalog.chi_string(c)
                         for c in (chi_nr, chi_wk, chi_wk2))

    cert0, _ = gordan.find_gordan(chi_nr, sup0)
    cert1, _ = gordan.find_gordan(chi_nr, sup1)
    assert cert0 is not None and cert1 is not None
    G0 = gordan.gordan_record(N, R, s_nr, cert0, sup0)
    G1 = gordan.gordan_record(N, R, s_nr, cert1, sup1)
    B0 = gordan.gordan_record_bfp(N, R, s_nr, cert0, sup0)
    u, _ = gordan.find_witness(chi_wk, sup1)
    assert u is not None
    W = gordan.witness_record(N, R, s_wk, u, sup1)

    S = weaponA.Searcher()
    Z, _ = S.attack(chi_wk, budget=30.0, row=row_wk, arrays=catalog.arrays())
    assert Z is not None
    RZ = weaponA.realizable_record(N, R, s_wk, Z)

    cases = []

    def add(name, rec, checker, expect_sub):
        cases.append({'canary': name, 'checker': checker,
                      'expect': expect_sub, 'record': rec})

    # ---- positive controls (must be ACCEPTED) --------------------------
    add('control: honest L0 Gordan vector', G0, 'fpcheck', None)
    add('control: honest L1 Gordan vector', G1, 'fpcheck', None)
    add('control: honest no-BFP witness', W, 'fpcheck', None)
    add('control: honest realization', RZ, 'fpcheck', None)
    add('control: honest L0 Gordan, omreal schema', B0, 'checkcert', None)
    add('control: honest realization, omreal schema', RZ, 'checkcert', None)

    # ---- sabotages ----------------------------------------------------
    c = copy.deepcopy(G0)
    c['terms'][0]['w'] += 1
    add('C1  one weight increased by 1', c, 'fpcheck', 'does not cancel')

    c = copy.deepcopy(G0)
    c['terms'][1]['big'], c['terms'][1]['small'] = \
        c['terms'][1]['small'], c['terms'][1]['big']
    add('C2  big and small swapped on one term', c, 'fpcheck',
        'not the dominating term')

    c = copy.deepcopy(G0)
    del c['terms'][3]
    add('C3  one inequality dropped', c, 'fpcheck', 'does not cancel')

    c = copy.deepcopy(G0)
    c['chi'] = s_wk
    add('C4  attached to a realizable class', c, 'fpcheck', None)

    c = copy.deepcopy(G0)
    c['terms'][0]['w'] = 0
    add('C5  a zero weight', c, 'fpcheck', 'not positive')

    c = copy.deepcopy(G1)
    c['terms'][0]['rel'] = {'kind': 'pl', 'A': [1, 2, 3],
                            'B': [1, 2, 3, 4, 5]}
    add('C6  a degenerate relation spec (A inside B: only two terms)', c,
        'fpcheck', 'fewer than three')

    c = copy.deepcopy(G1)
    c['terms'][0]['rel'] = {'kind': 'pl', 'A': [1, 2, 3], 'B': [4, 4, 5, 6, 7]}
    add('C7  a relation spec with a repeated element', c, 'fpcheck',
        'repeated element')

    c = copy.deepcopy(G0)
    c['terms'].append(copy.deepcopy(c['terms'][0]))
    add('C8  a duplicated inequality', c, 'fpcheck', 'duplicate')

    c = copy.deepcopy(W)
    c['u'][17] = -c['u'][17] - 1
    add('C9  no-BFP witness with one coordinate corrupted', c, 'fpcheck',
        'u fails inequality')

    c = copy.deepcopy(W)
    c['chi'] = s_nr
    add('C10 no-BFP witness attached to a class that HAS a BFP', c,
        'fpcheck', 'u fails inequality')

    c = copy.deepcopy(W)
    c['families'] = ['pl4', 'pl5']
    add('C11 witness that silently drops the three-term relations', c,
        'fpcheck', 'do not include gp3')

    c = copy.deepcopy(W)
    c['u'] = [1] * 126
    add('C12 the trivial witness u = 1', c, 'fpcheck', 'u fails inequality')

    # NOTE.  "one matrix entry off by one" is NOT a valid canary and was
    # removed after it was (correctly) accepted: a realization certificate is
    # SELF-VALIDATING -- any integer matrix whose 126 brackets match the sign
    # string certifies the class, and nudging a well-centred entry by 1 flips
    # no bracket, so the perturbed matrix realizes the same class and the
    # checker is right to accept it.  The sabotages that bite are the ones a
    # bug would actually produce: a relabelling applied to the columns but not
    # to the chirotope, and a reorientation applied to one and not the other.
    c = copy.deepcopy(RZ)
    for i in range(R):
        c['matrix'][i][2], c['matrix'][i][6] = \
            c['matrix'][i][6], c['matrix'][i][2]
    add('C13a two columns swapped (relabelling applied to only one side)', c,
        'fpcheck', 'wrong sign')

    c = copy.deepcopy(RZ)
    for i in range(R):
        c['matrix'][i][4] = -int(c['matrix'][i][4])
    add('C13b one column negated (reorientation applied to only one side)', c,
        'fpcheck', 'wrong sign')

    c = copy.deepcopy(RZ)
    c['chi'] = s_wk2
    add('C14 realization attached to a different realizable class', c,
        'fpcheck', 'wrong sign')

    c = copy.deepcopy(B0)
    c['bfp'][0]['w'] += 1
    add('C15 omreal-schema Gordan vector, one weight increased', c,
        'checkcert', 'does not cancel')

    c = copy.deepcopy(B0)
    c['bfp'][2]['big'], c['bfp'][2]['small'] = \
        c['bfp'][2]['small'], c['bfp'][2]['big']
    add('C16 omreal-schema, big and small swapped', c, 'checkcert',
        'not the odd one out')

    c = copy.deepcopy(B0)
    c['chi'] = s_wk
    add('C17 omreal-schema Gordan vector on a realizable class', c,
        'checkcert', None)

    c = copy.deepcopy(RZ)
    c['matrix'][0][0] = 0
    c['matrix'][1][0] = 0
    c['matrix'][2][0] = 0
    c['matrix'][3][0] = 0
    add('C18 realization with a zero column, omreal schema', c, 'checkcert',
        'vanishes')

    # ---- the general final polynomial, exercised through its own control --
    import fpoly
    rigged, fcert, finfo = fpoly.positive_control(chi_wk, sup1)
    if fcert is not None:
        s_rig = catalog.chi_string(rigged)
        FP = fpoly.fp_record(N, R, s_rig, fcert, 2, sup1)
        add('control: honest degree-2 final polynomial (rigged instance)',
            FP, 'fpcheck', None)
        c = copy.deepcopy(FP)
        c['gens'][0]['c'] = [int(c['gens'][0]['c'][0]) * 3, 1]
        add('C19 final polynomial with one coefficient tripled', c,
            'fpcheck', 'both signs')
        c = copy.deepcopy(FP)
        c['chi'] = s_wk
        add('C20 final polynomial attached to a realizable class', c,
            'fpcheck', 'both signs')
        c = copy.deepcopy(FP)
        c['gens'] = c['gens'][:max(1, len(c['gens']) // 2)]
        add('C21 final polynomial with half its generators dropped', c,
            'fpcheck', 'both signs')
    else:
        print('WARNING: the final-polynomial positive control did not fire; '
              'its canaries were skipped')

    # ---- run ----------------------------------------------------------
    path = os.path.join(DATA, 'canaries.jsonl')
    with open(path, 'w') as fh:
        for k in cases:
            fh.write(json.dumps(k) + '\n')

    nfail = 0
    print('\n%-4s %-62s %-9s %s' % ('', 'canary', 'checker', 'result'))
    for k in cases:
        rec = k['record']
        if k['checker'] == 'fpcheck':
            ok, msg = fpcheck.check_record(rec, trials=12)
        else:
            ok, msg = omcheck.check_record(rec)
        control = k['canary'].startswith('control')
        want_ok = control
        good = (ok == want_ok)
        if good and not control and k['expect']:
            good = k['expect'].lower() in msg.lower()
        if not good:
            nfail += 1
        print('  %-4s %-60s %-9s %s: %s'
              % ('ok' if good else 'FAIL', k['canary'][:60], k['checker'],
                 'ACCEPTED' if ok else 'REJECTED', msg[:78]))
    ncan = sum(1 for k in cases if not k['canary'].startswith('control'))
    print('\n%d controls accepted, %d sabotages rejected with the expected '
          'diagnosis, %d failures' % (len(cases) - ncan, ncan - nfail, nfail))
    print('written: %s' % path)
    return nfail


if __name__ == '__main__':
    sys.exit(1 if run() else 0)
