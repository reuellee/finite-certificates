#!/usr/bin/env python3
"""PART A #3 -- full adversarial parse-validity scan of every certificate
shard the sweep wrote (ai/omreal/sweep_state/certs/*.jsonl), plus reservoir
sampling for Part B's independent re-verification.

This is the direct empirical test of the concurrent-append / buffering
concerns identified by reading sweep49.py's do_chunk: Z[i] write, then a
BUFFERED fh.write() of the JSON record, then st[i]=how, with fh.flush() +
fsync() only once per WHOLE CHUNK (default 8000 rows), and with more chunks
per wave than worker processes (so the same wid shard file can in principle
be opened by two different OS processes at once).  Either failure mode
(buffer loss at a kill, or cross-process interleaving) would show up here
as: a malformed / unparseable JSON line, OR a byte count that does not
divide cleanly into whole records.

For each shard file:
  - every line is stripped and, if non-blank, run through json.loads.
    NOT wrapped defensively beyond catching the exception to report it --
    every failure is recorded, not silently absorbed.
  - verdict tallies (REALIZABLE / NON_REALIZABLE / RESIDUE / other)
  - reservoir sample of REALIZABLE records (for Part B fresh re-verification)
  - reservoir sample of NON_REALIZABLE records
  - all RESIDUE 'row' values collected in full (there should be exactly 659)
  - duplicate-chi detection WITHIN a shard (same chi string appearing twice)

Read-only on ai/omreal throughout.  Writes only to this review_scratch dir.
"""
import glob
import json
import os
import random
import sys
import time
from multiprocessing import Pool

sys.dont_write_bytecode = True
os.environ.setdefault('PYTHONDONTWRITEBYTECODE', '1')

HERE = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.normpath(os.path.join(HERE, '..', 'sweep_state'))
CERTS = os.path.join(STATE, 'certs')
OUT = os.path.join(HERE, 'shard_scan_result.json')

REAL_RESERVOIR = 2500
NONREAL_RESERVOIR = 600


def scan_one(path):
    seed = abs(hash(os.path.basename(path))) % (2**31)
    rng = random.Random(seed)
    counts = {'REALIZABLE': 0, 'NON_REALIZABLE': 0, 'RESIDUE': 0, 'OTHER': 0}
    n_lines = 0
    n_blank = 0
    n_bad = 0
    bad_examples = []
    residue_rows = []
    real_reservoir = []
    nreal_reservoir = []
    n_real_seen = 0
    n_nreal_seen = 0
    chi_seen_this_shard = {}
    dup_chi = []
    total_bytes = os.path.getsize(path)
    t0 = time.time()
    with open(path, 'rb') as fh:
        for ln, raw in enumerate(fh, 1):
            n_lines += 1
            line = raw.strip()
            if not line:
                n_blank += 1
                continue
            try:
                rec = json.loads(line)
            except Exception as e:
                n_bad += 1
                if len(bad_examples) < 25:
                    bad_examples.append({'line': ln, 'error': str(e),
                                          'raw_prefix': raw[:200].decode('utf8', 'replace'),
                                          'raw_len': len(raw)})
                continue
            v = rec.get('verdict')
            if v == 'REALIZABLE':
                counts['REALIZABLE'] += 1
                n_real_seen += 1
                ch = rec.get('chi')
                if ch is not None:
                    if ch in chi_seen_this_shard:
                        if len(dup_chi) < 20:
                            dup_chi.append({'chi_prefix': ch[:24], 'lines':
                                            [chi_seen_this_shard[ch], ln]})
                    else:
                        chi_seen_this_shard[ch] = ln
                # reservoir sampling
                if len(real_reservoir) < REAL_RESERVOIR:
                    real_reservoir.append(rec)
                else:
                    j = rng.randint(0, n_real_seen - 1)
                    if j < REAL_RESERVOIR:
                        real_reservoir[j] = rec
            elif v == 'NON_REALIZABLE':
                counts['NON_REALIZABLE'] += 1
                n_nreal_seen += 1
                ch = rec.get('chi')
                if ch is not None:
                    if ch in chi_seen_this_shard:
                        if len(dup_chi) < 20:
                            dup_chi.append({'chi_prefix': ch[:24], 'lines':
                                            [chi_seen_this_shard[ch], ln]})
                    else:
                        chi_seen_this_shard[ch] = ln
                if len(nreal_reservoir) < NONREAL_RESERVOIR:
                    nreal_reservoir.append(rec)
                else:
                    j = rng.randint(0, n_nreal_seen - 1)
                    if j < NONREAL_RESERVOIR:
                        nreal_reservoir[j] = rec
            elif v == 'RESIDUE':
                counts['RESIDUE'] += 1
                if 'row' in rec:
                    residue_rows.append(int(rec['row']))
            else:
                counts['OTHER'] += 1
    dt = time.time() - t0
    return {
        'path': os.path.basename(path), 'bytes': total_bytes,
        'lines': n_lines, 'blank': n_blank, 'bad': n_bad,
        'bad_examples': bad_examples, 'counts': counts,
        'residue_rows': residue_rows,
        'dup_chi_within_shard': dup_chi,
        'seconds': round(dt, 1),
        'real_reservoir': real_reservoir,
        'real_seen': n_real_seen,
        'nreal_reservoir': nreal_reservoir,
        'nreal_seen': n_nreal_seen,
    }


def main():
    paths = sorted(glob.glob(os.path.join(CERTS, '*.jsonl')))
    print('scanning %d shard files under %s' % (len(paths), CERTS))
    for p in paths:
        print('   %-16s %10.1f MB' % (os.path.basename(p), os.path.getsize(p) / 1e6))
    t0 = time.time()
    with Pool(4) as pool:
        results = pool.map(scan_one, paths)
    dt = time.time() - t0
    print('scan complete in %.1f s' % dt)

    total = {'lines': 0, 'blank': 0, 'bad': 0}
    counts = {'REALIZABLE': 0, 'NON_REALIZABLE': 0, 'RESIDUE': 0, 'OTHER': 0}
    all_residue_rows = []
    all_bad = []
    all_dup = []
    real_pool = []
    nreal_pool = []
    for r in results:
        total['lines'] += r['lines']
        total['blank'] += r['blank']
        total['bad'] += r['bad']
        for k in counts:
            counts[k] += r['counts'][k]
        all_residue_rows.extend(r['residue_rows'])
        for b in r['bad_examples']:
            b2 = dict(b)
            b2['shard'] = r['path']
            all_bad.append(b2)
        for d in r['dup_chi_within_shard']:
            d2 = dict(d)
            d2['shard'] = r['path']
            all_dup.append(d2)
        real_pool.extend(r['real_reservoir'])
        nreal_pool.extend(r['nreal_reservoir'])
        print('  %-16s lines=%-9d blank=%-4d bad=%-4d REAL=%-9d NONREAL=%-8d '
              'RESIDUE=%-4d OTHER=%-3d  (%.1fs)'
              % (r['path'], r['lines'], r['blank'], r['bad'],
                 r['counts']['REALIZABLE'], r['counts']['NON_REALIZABLE'],
                 r['counts']['RESIDUE'], r['counts']['OTHER'], r['seconds']))

    n_records = counts['REALIZABLE'] + counts['NON_REALIZABLE'] + counts['RESIDUE'] + counts['OTHER']
    print()
    print('TOTAL lines            : %d' % total['lines'])
    print('TOTAL blank             : %d' % total['blank'])
    print('TOTAL PARSE FAILURES    : %d' % total['bad'])
    print('TOTAL parsed records    : %d' % n_records)
    print('  REALIZABLE            : %d' % counts['REALIZABLE'])
    print('  NON_REALIZABLE        : %d' % counts['NON_REALIZABLE'])
    print('  RESIDUE               : %d' % counts['RESIDUE'])
    print('  OTHER (unknown verdict): %d' % counts['OTHER'])
    print('  distinct RESIDUE rows : %d (expect 659, expect all distinct)'
          % len(set(all_residue_rows)))
    print('  RESIDUE row count == records?: %s'
          % (len(all_residue_rows) == counts['RESIDUE']))
    dupset = len(all_residue_rows) != len(set(all_residue_rows))
    print('  RESIDUE rows duplicated within/across shards: %s' % dupset)
    print('  cross-shard sum REAL+NONREAL+RESIDUE+OTHER == total lines - blank - bad: %s'
          % (n_records == total['lines'] - total['blank'] - total['bad']))
    if all_bad:
        print('\n  *** PARSE FAILURES (first 25) ***')
        for b in all_bad[:25]:
            print('   ', b)
    if all_dup:
        print('\n  *** DUPLICATE CHI WITHIN A SHARD (first 20) ***')
        for d in all_dup[:20]:
            print('   ', d)

    # residue row-index clustering: are the 141-missing analog visible here?
    # (that check happens in a separate script against certaudit; here we
    # just persist the raw counts + samples.)
    out = {
        'per_shard': [{k: v for k, v in r.items()
                       if k not in ('real_reservoir', 'nreal_reservoir')}
                      for r in results],
        'total': total, 'counts': counts, 'n_records': n_records,
        'residue_rows': sorted(set(all_residue_rows)),
        'residue_row_count_records': len(all_residue_rows),
        'bad_examples': all_bad,
        'dup_chi': all_dup,
        'seconds': round(dt, 1),
    }
    with open(OUT, 'w') as fh:
        json.dump(out, fh, indent=1)
    print('\nwrote %s' % OUT)

    # persist the reservoir samples for Part B scripts (separate files, not
    # part of the JSON report, since they can be large)
    with open(os.path.join(HERE, 'sample_realizable.jsonl'), 'w') as fh:
        for rec in real_pool:
            fh.write(json.dumps(rec) + '\n')
    with open(os.path.join(HERE, 'sample_nonrealizable.jsonl'), 'w') as fh:
        for rec in nreal_pool:
            fh.write(json.dumps(rec) + '\n')
    print('wrote %d REALIZABLE and %d NON_REALIZABLE sampled records for Part B'
          % (len(real_pool), len(nreal_pool)))


if __name__ == '__main__':
    main()
