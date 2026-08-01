#!/usr/bin/env python3
"""The gates that must pass BEFORE any OPEN class is touched.

    python validate.py [--n 40] [--budget 60]
    python attack.py validate --n 40

Each gate is stated as a claim that the run either confirms or refutes; a
refutation is fatal and says so.  Results are written to
`data/validation.json` so OPEN_ATTACK.md quotes measurements, not memories.

    A1  WEAPON A reproduces realizations of classes the sweep decided
        REALIZABLE(repair) -- the hard-but-solved population.  Anything
        less than 100% means the attack's negative results are weak.
    A2  WEAPON A on REALIZABLE(walk) classes, as a smoke control.
    B1  Level-0 Gordan search fires on every certified NON_REALIZABLE
        class.  Level 0 is exactly ai/omreal/bfp.py's support, so this is
        an independent reimplementation agreeing with the sweep.
    B2  Level-0 and level-1 Gordan search fire on NO certified REALIZABLE
        class.  SOUNDNESS.  A single hit is fatal: it would mean the
        identity table emits an invalid inequality, and every
        non-realizability verdict in this directory would be void.
    B3  The exact no-final-polynomial witness exists for every certified
        REALIZABLE class and for none of the certified NON_REALIZABLE ones
        -- Gordan's dichotomy, measured rather than assumed.
    B4  Every certificate produced during the gates is accepted by
        `fpcheck.py`, and every level-0 one also by `ai/omreal/checkcert.py`.
"""

import json
import os
import subprocess
import sys
import time

sys.dont_write_bytecode = True
for _v in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS',
           'NUMEXPR_NUM_THREADS'):
    os.environ.setdefault(_v, '1')

import numpy as np                                          # noqa: E402

import catalog                                              # noqa: E402
import gordan                                               # noqa: E402
import weaponA                                              # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, 'data')
N, R = 9, 4


def run(a=None):
    n = getattr(a, 'n', 40) or 40
    budget = getattr(a, 'budget', 60.0) or 60.0
    os.makedirs(DATA, exist_ok=True)
    out = {'n': n, 'budget': budget, 'when': time.strftime('%Y-%m-%dT%H:%M:%S')}

    t0 = time.time()
    sup0 = gordan.Support(N, R, 'L0', verify=True, trials=60)
    sup1 = gordan.Support(N, R, 'L1', verify=True, trials=60)
    out['identity_test'] = {'L0_identities': len(sup0.idents),
                            'L1_identities': len(sup1.idents),
                            'random_configs': sup0.verified,
                            'failures': 0}
    print('identity tables: L0 %d relations, L1 %d relations, exact on %d '
          'random integer configurations, 0 failures (%.1f s)'
          % (len(sup0.idents), len(sup1.idents), sup0.verified,
             time.time() - t0))

    rng = np.random.default_rng(20260801)
    pools = {'REPAIR': catalog.rows_with_status(catalog.REPAIR),
             'WALK': catalog.rows_with_status(catalog.WALK),
             'NONREAL': catalog.rows_with_status(catalog.NONREAL)}
    pick = {k: rng.choice(v, min(n, len(v)), replace=False)
            for k, v in pools.items()}

    f_real = os.path.join(DATA, 'validation_realizable.jsonl')
    f_gord = os.path.join(DATA, 'validation_gordan.jsonl')
    f_bfps = os.path.join(DATA, 'validation_gordan_bfpschema.jsonl')
    f_wit = os.path.join(DATA, 'validation_witness.jsonl')
    for p in (f_real, f_gord, f_bfps, f_wit):
        open(p, 'w').close()

    S = weaponA.Searcher()
    arrays = catalog.arrays()

    # ---- A1 / A2 ------------------------------------------------------
    for tag in ('REPAIR', 'WALK'):
        rows = pick[tag]
        CH = catalog.chi_of_rows(rows)
        ok, times, srcs = 0, [], {}
        t0 = time.time()
        for r, c in zip(rows, CH):
            Z, log = S.attack(c, budget=budget, row=int(r), arrays=arrays)
            if Z is not None:
                ok += 1
                times.append(log['time'])
                srcs[log['found']] = srcs.get(log['found'], 0) + 1
                with open(f_real, 'a') as fh:
                    fh.write(json.dumps(weaponA.realizable_record(
                        N, R, catalog.chi_string(c), Z)) + '\n')
        key = 'A1_weaponA_' + tag
        out[key] = {'n': len(rows), 'realized': ok, 'sources': srcs,
                    'median_s': float(np.median(times)) if times else None,
                    'max_s': float(max(times)) if times else None,
                    'wall_s': round(time.time() - t0, 1),
                    'PASS': ok == len(rows)}
        print('%-26s %d/%d realized (median %.2f s, max %.2f s) %s'
              % (key, ok, len(rows),
                 float(np.median(times)) if times else -1,
                 float(max(times)) if times else -1,
                 'PASS' if ok == len(rows) else '*** FAIL ***'))

    # ---- B1 -----------------------------------------------------------
    rows = pick['NONREAL']
    CH = catalog.chi_of_rows(rows)
    hit = 0
    t0 = time.time()
    for c in CH:
        cert, _ = gordan.find_gordan(c, sup0)
        if cert is not None:
            hit += 1
            s = catalog.chi_string(c)
            with open(f_gord, 'a') as fh:
                fh.write(json.dumps(gordan.gordan_record(N, R, s, cert,
                                                         sup0)) + '\n')
            b = gordan.gordan_record_bfp(N, R, s, cert, sup0)
            with open(f_bfps, 'a') as fh:
                fh.write(json.dumps(b) + '\n')
    out['B1_gordan_on_nonrealizable'] = {
        'n': len(rows), 'found': hit, 'wall_s': round(time.time() - t0, 1),
        'PASS': hit == len(rows)}
    print('%-26s %d/%d Gordan vectors found %s'
          % ('B1_L0_on_NONREAL', hit, len(rows),
             'PASS' if hit == len(rows) else '*** FAIL ***'))

    # ---- B2 (soundness) and B3 (dichotomy) ----------------------------
    for lvl, sup in (('L0', sup0), ('L1', sup1)):
        false_pos = 0
        wit_real = 0
        rows = np.concatenate([pick['WALK'], pick['REPAIR']])
        CH = catalog.chi_of_rows(rows)
        t0 = time.time()
        for c in CH:
            sysm = sup.system(c)
            if sysm.contradiction is not None:
                false_pos += 1
                continue
            cert, _ = gordan.find_gordan(c, sup, sys=sysm)
            if cert is not None:
                false_pos += 1
            u, _ = gordan.find_witness(c, sup, sys=sysm)
            if u is not None:
                wit_real += 1
                with open(f_wit, 'a') as fh:
                    fh.write(json.dumps(gordan.witness_record(
                        N, R, catalog.chi_string(c), u, sup)) + '\n')
        out['B2_soundness_' + lvl] = {'n': len(rows), 'false_positives':
                                      false_pos, 'PASS': false_pos == 0}
        out['B3_witness_on_realizable_' + lvl] = {
            'n': len(rows), 'found': wit_real, 'wall_s':
            round(time.time() - t0, 1), 'PASS': wit_real == len(rows)}
        print('%-26s %d false positives on %d realizable classes %s'
              % ('B2_soundness_' + lvl, false_pos, len(rows),
                 'PASS' if false_pos == 0 else '*** FATAL ***'))
        print('%-26s %d/%d realizable classes carry an exact witness %s'
              % ('B3_witness_' + lvl, wit_real, len(rows),
                 'PASS' if wit_real == len(rows) else '*** FAIL ***'))
        rows = pick['NONREAL']
        CH = catalog.chi_of_rows(rows)
        wit_bad = 0
        for c in CH:
            u, _ = gordan.find_witness(c, sup)
            if u is not None:
                wit_bad += 1
        out['B3_witness_on_nonrealizable_' + lvl] = {
            'n': len(rows), 'found': wit_bad, 'PASS': wit_bad == 0}
        print('%-26s %d/%d non-realizable classes carry a witness (must be 0) %s'
              % ('B3_nowitness_' + lvl, wit_bad, len(rows),
                 'PASS' if wit_bad == 0 else '*** FATAL ***'))

    # ---- B4: both checkers --------------------------------------------
    def check(cmd, files):
        files = [f for f in files if os.path.getsize(f) > 0]
        if not files:
            return None
        p = subprocess.run([sys.executable] + cmd + files,
                           capture_output=True, text=True,
                           env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'))
        return {'rc': p.returncode, 'tail': p.stdout.strip().splitlines()[-6:]}

    out['B4_fpcheck'] = check([os.path.join(HERE, 'fpcheck.py'),
                               '--trials=12'],
                              [f_real, f_gord, f_wit])
    out['B4_checkcert'] = check([os.path.join(catalog.OMREAL, 'checkcert.py')],
                                [f_real, f_bfps])
    for k in ('B4_fpcheck', 'B4_checkcert'):
        v = out[k]
        print('%-26s rc=%s' % (k, v and v['rc']))
        for ln in (v or {}).get('tail', []):
            print('      %s' % ln)

    out['ALL_PASS'] = all(v.get('PASS', True) for v in out.values()
                          if isinstance(v, dict)) and \
        out['B4_fpcheck']['rc'] == 0 and out['B4_checkcert']['rc'] == 0
    with open(os.path.join(DATA, 'validation.json'), 'w') as fh:
        json.dump(out, fh, indent=1, default=str)
    print('\nVALIDATION %s  ->  data/validation.json'
          % ('PASSED' if out['ALL_PASS'] else 'FAILED'))
    return 0 if out['ALL_PASS'] else 1


if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--n', type=int, default=40)
    ap.add_argument('--budget', type=float, default=60.0)
    sys.exit(run(ap.parse_args()))
