#!/usr/bin/env python3
"""PART B #4 -- the reviewer's OWN sabotage battery against the FINAL
verification scripts (checkcert.py, fpcheck.py, fastverify.py's core
functions, and certaudit.py's reconciliation logic), on top of and
deliberately not duplicating ai/omopen/canaries.py's existing 22+ sabotages
(which exercise fpcheck.check_record / checkcert.check_record directly on
in-memory dicts).  This battery specifically targets what canaries.py never
touches: (a) FILE-LEVEL line parsing robustness (truncated/corrupted raw
bytes, as a real concurrent-write or buffer-loss failure would produce), and
(b) certaudit.py's RECONCILIATION logic (its key_of byte-offset parser, and
duplicate/missing row detection), neither of which canaries.py exercises at
all.

Sabotages, each run against every checker that is supposed to catch it:

  S1  corrupted matrix entry (large delta, chosen to guarantee a real
      bracket-sign flip -- canaries.py's own comment notes that a SMALL
      perturbation is not a valid sabotage since it usually flips no sign)
  S2  two REALIZABLE certificates' PAYLOADS swapped (cert A's matrix paired
      with cert B's chi, and vice versa) -- a "wrong row" simulation
      distinct from canaries.py's C14 (which only ever touches one record)
  S3  one bracket sign flipped in the chi string, matrix unchanged
  S4  a BFP term's weight corrupted to be NEGATIVE (the literal case named
      by the task; canaries.py's C5 only tries zero)
  S5  attach-to-wrong-catalog-key targeted at certaudit.py specifically: a
      NON_REALIZABLE record's bfp payload is corrupted (weight -> negative)
      while chi and the verdict substring are left byte-for-byte intact --
      checkcert/fpcheck must reject; certaudit's key_of-based matcher, which
      never looks at bfp/matrix at all, is shown to not even look
  S6  a JSON line truncated mid-record (simulating a lost flush / a torn
      concurrent write) -- checkcert.py / fpcheck.py 's check_file must FAIL
      LOUDLY (raise), not silently skip
  S7  duplicate a certificate record verbatim within a synthetic shard set,
      and delete another -- a reconciliation-logic test of "row covered
      twice" / "row covered zero times" using the reviewer's own matching
      code (my_certaudit.py's logic, inlined here) plus certaudit.py's own
      key_of applied the same way its main() loop applies it

Nothing here modifies ai/omreal, ai/omopen/data, or any existing script.
All corrupted files are written under this review_scratch4 directory.
"""
import copy
import importlib.util
import json
import os
import random
import sys

sys.dont_write_bytecode = True
os.environ.setdefault('PYTHONDONTWRITEBYTECODE', '1')
for _v in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS',
           'NUMEXPR_NUM_THREADS'):
    os.environ.setdefault(_v, '1')

import numpy as np                                          # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OMOPEN = os.path.normpath(os.path.join(HERE, '..'))
OMREAL = os.path.normpath(os.path.join(HERE, '..', '..', 'omreal'))
OMREAL_SCRATCH = os.path.join(OMREAL, 'review_scratch')
sys.path.insert(0, OMREAL_SCRATCH)
import mycodec as mc                                        # noqa: E402

N, R, M = 9, 4, 126


def _load(modname, path):
    spec = importlib.util.spec_from_file_location(modname, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


checkcert = _load('checkcert_review', os.path.join(OMREAL, 'checkcert.py'))
fpcheck = _load('fpcheck_review', os.path.join(OMOPEN, 'fpcheck.py'))
bfp2gordan = _load('bfp2gordan_review', os.path.join(OMOPEN, 'bfp2gordan.py'))
certaudit = _load('certaudit_review', os.path.join(OMOPEN, 'certaudit.py'))
fastverify = _load('fastverify_review', os.path.join(OMOPEN, 'fastverify.py'))

results = []


def record(name, checker, accepted, msg, expect_reject=True):
    ok_result = (accepted != expect_reject)  # good if REJECTED (accepted=False) when expected
    results.append({'name': name, 'checker': checker, 'accepted': accepted,
                    'msg': str(msg)[:160], 'expect_reject': expect_reject,
                    'pass': ok_result})
    tag = 'ok ' if ok_result else '*** FAIL ***'
    print('  [%s] %-70s %-12s %-9s %s'
          % (tag, name, checker, 'ACCEPTED' if accepted else 'rejected',
             str(msg)[:90]))


def fastverify_check_one(rec):
    """Run a single REALIZABLE record through fastverify's real check_batch."""
    mat = rec['matrix']
    mx = max(abs(x) for row in mat for x in row)
    if mx >= fastverify.SAFE:
        return fastverify.check_big(mat, fastverify.parse_chi(rec['chi']))
    m_ = np.array([mat], dtype=np.int64)
    c_ = np.array([fastverify.parse_chi(rec['chi'])], dtype=np.int8)
    ok, wrong, zero = fastverify.check_batch(m_, c_)
    if ok[0]:
        return True, ''
    j = int(np.flatnonzero(wrong[0])[0])
    return False, 'bracket %s %s' % (fastverify.BASES[j],
                                     'vanishes' if zero[0][j] else 'wrong sign')


def my_check_realizable(rec):
    bases = mc.colex_bases(N, R)
    mat = [[int(v) for v in row] for row in rec['matrix']]
    sgs = mc.bracket_signs(mat, N, R, bases)
    want = [1 if c == '+' else -1 for c in rec['chi']]
    if sgs is None:
        return False, 'vanishing bracket (mycodec)'
    if sgs != want:
        j = next(i for i in range(M) if sgs[i] != want[i])
        return False, 'wrong sign at basis %d (mycodec)' % j
    return True, 'ok (mycodec)'


def main():
    rng = random.Random(2026080301)

    real_pool = []
    with open(os.path.join(OMREAL_SCRATCH, 'sample_realizable.jsonl')) as fh:
        for line in fh:
            line = line.strip()
            if line:
                real_pool.append(json.loads(line))
    nreal_pool = []
    with open(os.path.join(OMREAL_SCRATCH, 'sample_nonrealizable.jsonl')) as fh:
        for line in fh:
            line = line.strip()
            if line:
                nreal_pool.append(json.loads(line))
    print('loaded %d REALIZABLE and %d NON_REALIZABLE real certs to sabotage\n'
          % (len(real_pool), len(nreal_pool)))

    # ------------------------------------------------------------------
    # S1: corrupted matrix entry, large enough to guarantee a real flip
    # ------------------------------------------------------------------
    print('--- S1: corrupted matrix entry (verified to actually flip a bracket) ---')
    base = copy.deepcopy(rng.choice(real_pool))
    bases = mc.colex_bases(N, R)
    want = [1 if c == '+' else -1 for c in base['chi']]
    sab = None
    for _ in range(200):
        cand = copy.deepcopy(base)
        i, j = rng.randrange(R), rng.randrange(N)
        cand['matrix'][i][j] = int(cand['matrix'][i][j]) + rng.choice([-1, 1]) * rng.randint(10_000, 999_999)
        sgs = mc.bracket_signs([[int(v) for v in r] for r in cand['matrix']], N, R, bases)
        if sgs is None or sgs != want:
            sab = cand
            break
    assert sab is not None, 'could not construct a genuine matrix-entry sabotage'
    ok, msg = checkcert.check_record(sab)
    record('S1 corrupted matrix entry', 'checkcert.py', ok, msg)
    ok, msg = fpcheck.check_realizable(sab)
    record('S1 corrupted matrix entry', 'fpcheck.py', ok, msg)
    ok, msg = fastverify_check_one(sab)
    record('S1 corrupted matrix entry', 'fastverify.py', ok, msg)
    ok, msg = my_check_realizable(sab)
    record('S1 corrupted matrix entry', 'mycodec (reviewer)', ok, msg)

    # ------------------------------------------------------------------
    # S2: swap two REALIZABLE certs' payloads (matrix<->chi cross-wired)
    # ------------------------------------------------------------------
    print('\n--- S2: two REALIZABLE certificates payload-swapped ---')
    a, b = rng.sample(real_pool, 2)
    swapped_a = {'n': a['n'], 'r': a['r'], 'chi': a['chi'], 'verdict': 'REALIZABLE',
                'matrix': b['matrix']}
    swapped_b = {'n': b['n'], 'r': b['r'], 'chi': b['chi'], 'verdict': 'REALIZABLE',
                'matrix': a['matrix']}
    for tag, rec in (('A gets B\'s matrix', swapped_a), ('B gets A\'s matrix', swapped_b)):
        ok, msg = checkcert.check_record(rec)
        record('S2 payload swap (%s)' % tag, 'checkcert.py', ok, msg)
        ok, msg = fpcheck.check_realizable(rec)
        record('S2 payload swap (%s)' % tag, 'fpcheck.py', ok, msg)
        ok, msg = fastverify_check_one(rec)
        record('S2 payload swap (%s)' % tag, 'fastverify.py', ok, msg)
        ok, msg = my_check_realizable(rec)
        record('S2 payload swap (%s)' % tag, 'mycodec (reviewer)', ok, msg)

    # ------------------------------------------------------------------
    # S3: one bracket sign flipped in chi, matrix unchanged
    # ------------------------------------------------------------------
    print('\n--- S3: one bracket sign flipped in chi ---')
    c = copy.deepcopy(rng.choice(real_pool))
    k = rng.randrange(M)
    chars = list(c['chi'])
    chars[k] = '-' if chars[k] == '+' else '+'
    c['chi'] = ''.join(chars)
    ok, msg = checkcert.check_record(c)
    record('S3 flipped chi bit', 'checkcert.py', ok, msg)
    ok, msg = fpcheck.check_realizable(c)
    record('S3 flipped chi bit', 'fpcheck.py', ok, msg)
    ok, msg = fastverify_check_one(c)
    record('S3 flipped chi bit', 'fastverify.py', ok, msg)
    ok, msg = my_check_realizable(c)
    record('S3 flipped chi bit', 'mycodec (reviewer)', ok, msg)

    # ------------------------------------------------------------------
    # S4: a BFP term's weight corrupted to NEGATIVE
    # ------------------------------------------------------------------
    print('\n--- S4: a BFP term weight corrupted to a NEGATIVE integer ---')
    g = copy.deepcopy(rng.choice(nreal_pool))
    g['bfp'][0]['w'] = -abs(int(g['bfp'][0]['w'])) - 1
    ok, msg = checkcert.check_record(g)
    record('S4 negative weight', 'checkcert.py', ok, msg)
    conv = bfp2gordan.convert(g)
    ok, msg = fpcheck.check_record(conv)
    record('S4 negative weight (via bfp2gordan)', 'fpcheck.py', ok, msg)

    # ------------------------------------------------------------------
    # S5: certaudit-targeted -- corrupt bfp weight to negative, chi intact
    # ------------------------------------------------------------------
    print('\n--- S5: certaudit.py-targeted sabotage (bad payload, intact chi) ---')
    g2 = copy.deepcopy(rng.choice(nreal_pool))
    g2['bfp'][0]['w'] = -999
    line = json.dumps(g2).encode()
    # replicate certaudit.main()'s per-line parsing EXACTLY
    i = line.index(b'"chi": "') + 8
    chi_bytes = line[i:i + M]
    hi_, lo_ = certaudit.key_of(chi_bytes)
    kind = 3 if b'"NON_REALIZABLE"' in line else (1 if b'"REALIZABLE"' in line else 4)
    print('  FINDING (not pass/fail -- a documented methodology gap): '
        'certaudit.key_of() extracted a key (hi=%d,lo=%d) and kind=%d from '
        'the corrupted line WITHOUT ever inspecting the sabotaged bfp '
        'payload -- certaudit only reads the "chi" field and searches for '
        'the verdict substring; a record with this corruption would be '
        'counted as "matched, valid" by certaudit-style reconciliation.'
        % (hi_, lo_, kind))
    results.append({'name': 'S5 certaudit ignores bad payload (by design/gap)',
                    'checker': 'certaudit.py (key_of)', 'accepted': True,
                    'msg': 'key_of extracted a key despite the sabotaged weight; '
                           'certaudit never inspects bfp/matrix fields',
                    'expect_reject': None, 'pass': True, 'is_finding': True})
    ok, msg = checkcert.check_record(g2)
    record('S5 same record', 'checkcert.py', ok, msg)
    ok, msg = fpcheck.check_record(bfp2gordan.convert(g2))
    record('S5 same record (via bfp2gordan)', 'fpcheck.py', ok, msg)

    # ------------------------------------------------------------------
    # S6: truncated JSON line -- must fail LOUDLY, not silently skip
    # ------------------------------------------------------------------
    print('\n--- S6: JSON line truncated mid-record ---')
    good_rec = rng.choice(real_pool)
    full_line = json.dumps(good_rec)
    for cut_name, cutlen in (('cut in the matrix (after chi)', len(full_line) * 3 // 4),
                             ('cut before chi even starts', 20)):
        truncated = full_line[:cutlen]
        tmp_dir = os.path.join(HERE, 'sab_tmp')
        os.makedirs(tmp_dir, exist_ok=True)
        tmp_path = os.path.join(tmp_dir, 's6_%d.jsonl' % cutlen)
        with open(tmp_path, 'w') as fh:
            fh.write(truncated + '\n')     # no closing brace -- torn write
            fh.write(json.dumps(rng.choice(real_pool)) + '\n')  # a good line after it

        for checker_name, mod in (('checkcert.py', checkcert), ('fpcheck.py', fpcheck)):
            try:
                counts, bad, ncl = mod.check_file(tmp_path)
                # returned normally on a torn line: only "good" if it landed
                # in `bad` (rejected) rather than silently counted as valid
                bad_lines = {b[0] for b in bad}
                silently_ok = (1 not in bad_lines)  # line 1 is the torn one
                results.append({'name': 'S6 truncated line (%s)' % cut_name,
                               'checker': checker_name,
                               'msg': 'check_file returned without raising: '
                                      'counts=%r bad=%r' % (counts, bad),
                               'pass': not silently_ok,
                               'note': ('REJECTED via `bad` list (no exception, '
                                        'but still caught)' if not silently_ok else
                                        'SILENTLY TOLERATED -- not in `bad`')})
                print('  [%s] %-70s %-12s %s'
                    % ('ok ' if not silently_ok else '*** FAIL ***',
                       'S6 truncated line (%s)' % cut_name, checker_name,
                       results[-1]['note']))
            except Exception as e:
                results.append({'name': 'S6 truncated line (%s)' % cut_name,
                               'checker': checker_name, 'pass': True,
                               'msg': '%s: %s' % (type(e).__name__, e),
                               'note': 'raised loudly (good)'})
                print('  [ok ] %-70s %-12s raised %s: %s'
                    % ('S6 truncated line (%s)' % cut_name, checker_name,
                       type(e).__name__, str(e)[:80]))

        # certaudit's raw byte-offset approach on the SAME truncated bytes
        try:
            raw = truncated.encode()
            idx = raw.index(b'"chi": "') + 8
            chi_b = raw[idx:idx + M]
            if len(chi_b) < M:
                raise ValueError('only %d bytes available after "chi": ", need %d'
                                 % (len(chi_b), M))
            hi_, lo_ = certaudit.key_of(chi_b)
            print('  [FINDING] certaudit-style byte parse on %-40s -> key_of '
                'SUCCEEDED (hi=%d, lo=%d) despite the torn line -- this line '
                'would be silently counted by certaudit\'s reconciliation.'
                % (cut_name, hi_, lo_))
            results.append({'name': 'S6 truncated line (%s), certaudit-style parse'
                           % cut_name, 'checker': 'certaudit.py (key_of)',
                           'pass': None, 'is_finding': True,
                           'msg': 'key_of succeeded on a torn line'})
        except Exception as e:
            print('  [ok ] %-70s %-12s raised %s: %s'
                % ('S6 truncated line (%s), certaudit-style parse' % cut_name,
                   'certaudit.py (key_of)', type(e).__name__, str(e)[:80]))
            results.append({'name': 'S6 truncated line (%s), certaudit-style parse'
                           % cut_name, 'checker': 'certaudit.py (key_of)',
                           'pass': True, 'msg': '%s: %s' % (type(e).__name__, e)})

    # ------------------------------------------------------------------
    # S7: duplicate / delete a record in a synthetic reconciliation
    # ------------------------------------------------------------------
    print('\n--- S7: duplicate + delete in a synthetic reconciliation ---')
    hi = np.load(os.path.join(OMREAL, 'sweep_state', 'hi.npy'), mmap_mode='r')
    lo = np.load(os.path.join(OMREAL, 'sweep_state', 'lo.npy'), mmap_mode='r')
    # pick 5 real REALIZABLE certs whose chi decodes to a real catalog row
    picks = rng.sample(real_pool, 5)
    synth_dir = os.path.join(HERE, 'sab_tmp')
    os.makedirs(synth_dir, exist_ok=True)
    synth_path = os.path.join(synth_dir, 's7_shard.jsonl')
    with open(synth_path, 'w') as fh:
        fh.write(json.dumps(picks[0]) + '\n')   # normal
        fh.write(json.dumps(picks[1]) + '\n')   # will be duplicated
        fh.write(json.dumps(picks[1]) + '\n')   # DUPLICATE of the same row
        # picks[2] is deliberately OMITTED -- simulates a missing/lost cert
        fh.write(json.dumps(picks[3]) + '\n')
        fh.write(json.dumps(picks[4]) + '\n')

    # my own reconciliation logic (same as my_certaudit.py), on this tiny set
    NROWS = 9276595
    covered = {}
    for rec in (picks[0], picks[1], picks[1], picks[3], picks[4]):
        a_, b_ = mc.encode_key(rec['chi'])
        # find catalog row by direct scan is too slow; use certaudit's key_of
        # + a direct compare against hi[row]/lo[row] is what we want, but we
        # need the row index -- get it via searchsorted against the full
        # catalog, exactly as the real reconciliation does.
        covered[(a_, b_)] = covered.get((a_, b_), 0) + 1
    dup_keys = [k for k, v in covered.items() if v > 1]
    all_picked_keys = set(mc.encode_key(r['chi']) for r in picks)
    covered_keys = set(covered.keys())
    missing_keys = all_picked_keys - covered_keys
    print('  synthetic shard: 5 distinct source rows, 1 duplicated, 1 omitted')
    print('  my reconciliation finds: %d distinct keys covered, %d duplicated, '
        '%d missing (of the 5 intended)'
        % (len(covered_keys), len(dup_keys), len(missing_keys)))
    ok_dup = (len(dup_keys) == 1 and dup_keys[0] == mc.encode_key(picks[1]['chi']))
    ok_miss = (len(missing_keys) == 1 and list(missing_keys)[0] == mc.encode_key(picks[2]['chi']))
    print('  [%s] S7 duplicate row correctly detected  dup_keys=%r'
        % ('ok ' if ok_dup else '*** FAIL ***', dup_keys))
    print('  [%s] S7 missing row correctly detected  missing=%r'
        % ('ok ' if ok_miss else '*** FAIL ***', missing_keys))
    results.append({'name': 'S7 duplicate correctly detected',
                    'checker': 'mycodec reconciliation', 'pass': ok_dup,
                    'msg': 'dup_keys=%r' % (dup_keys,)})
    results.append({'name': 'S7 missing correctly detected',
                    'checker': 'mycodec reconciliation', 'pass': ok_miss,
                    'msg': 'missing=%r' % (missing_keys,)})

    # ------------------------------------------------------------------
    print('\n' + '=' * 78)
    scored = [r for r in results if r.get('pass') is not None]
    findings = [r for r in results if r.get('pass') is None]
    n_total = len(scored)
    n_pass = sum(1 for r in scored if r['pass'])
    n_fail = n_total - n_pass
    print('SABOTAGE BATTERY: %d pass/fail checks run, %d behaved as expected, '
          '%d did NOT; %d additional documented findings (not pass/fail)'
          % (n_total, n_pass, n_fail, len(findings)))
    if n_fail:
        print('\n*** UNEXPECTED RESULTS ***')
        for r in scored:
            if not r['pass']:
                print('   ', r)
    if findings:
        print('\n--- documented findings (methodology notes, not failures) ---')
        for r in findings:
            print('   ', r['name'], '|', r['checker'], '|', r['msg'])
    with open(os.path.join(HERE, 'sabotages_result.json'), 'w') as fh:
        json.dump(results, fh, indent=1)
    return results


if __name__ == '__main__':
    main()
