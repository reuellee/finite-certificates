#!/usr/bin/env python3
"""Closes the last gap: does the RESIDUE population (659 records, each
carrying an explicit 'row' field) EXACTLY match the set of rows st.dat
marks OPEN (status 4)?  And does each RESIDUE record's chi, re-encoded by
the reviewer's OWN codec, resolve to the SAME row its 'row' field claims?

Also independently reads st.dat's status histogram directly (TODO/WALK/
REPAIR/NONREAL/OPEN counts), which nothing in this review has done yet --
everything so far came from the certificate shards, not from st.dat itself.
"""
import glob
import json
import os
import sys

sys.dont_write_bytecode = True
os.environ.setdefault('PYTHONDONTWRITEBYTECODE', '1')
for _v in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS',
           'NUMEXPR_NUM_THREADS'):
    os.environ.setdefault(_v, '1')

import numpy as np                                          # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OMREAL_SCRATCH = os.path.normpath(os.path.join(HERE, '..', '..', 'omreal', 'review_scratch'))
sys.path.insert(0, OMREAL_SCRATCH)
import mycodec as mc                                        # noqa: E402

STATE = os.path.normpath(os.path.join(HERE, '..', '..', 'omreal', 'sweep_state'))
CERTS = os.path.join(STATE, 'certs')
NROWS, M = 9276595, 126
TODO, WALK, REPAIR, NONREAL, OPEN = 0, 1, 2, 3, 4
NAMES = {TODO: 'TODO', WALK: 'REALIZABLE(walk)', REPAIR: 'REALIZABLE(repair)',
         NONREAL: 'NON_REALIZABLE', OPEN: 'OPEN'}


def main():
    st = np.asarray(np.memmap(os.path.join(STATE, 'st.dat'), dtype=np.uint8,
                              mode='r', shape=(NROWS,)))
    hi = np.asarray(np.load(os.path.join(STATE, 'hi.npy'), mmap_mode='r'))
    lo = np.asarray(np.load(os.path.join(STATE, 'lo.npy'), mmap_mode='r'))

    print('=== st.dat status histogram, read directly (never done yet in '
        'this review) ===')
    counts = {}
    for k in (TODO, WALK, REPAIR, NONREAL, OPEN):
        c = int((st == k).sum())
        counts[k] = c
        print('   %-20s %9d' % (NAMES[k], c))
    print('   %-20s %9d' % ('SUM', sum(counts.values())))
    print('   matches NROWS=%d: %s' % (NROWS, sum(counts.values()) == NROWS))
    print()
    print('   FINAL_RESIDUE.md SECTION 0 total-st.dat arithmetic claims: '
        'WALK 9,060,883 + REPAIR 11,273 + NONREAL 203,780 + OPEN 659 + TODO 0')
    print('   (NOTE: section 6 separately quotes WALK 9,060,742 -- that is '
        'the CERTIFICATE-MATCHED subset of WALK, i.e. total WALK minus the '
        '141 backfilled rows, a *different* number for a *different* '
        'purpose (9,060,883 - 141 = 9,060,742); the correct comparison for '
        'st.dat\'s own total is the section-0 figure used below.)')
    claim = {WALK: 9060883, REPAIR: 11273, NONREAL: 203780, OPEN: 659, TODO: 0}
    for k in (TODO, WALK, REPAIR, NONREAL, OPEN):
        match = counts[k] == claim[k]
        print('   %-20s independently read %9d vs claimed %9d : %s'
              % (NAMES[k], counts[k], claim[k], 'MATCH' if match else '*** MISMATCH ***'))

    open_rows = set(np.flatnonzero(st == OPEN).tolist())
    print('\n=== st.dat OPEN rows: %d ===' % len(open_rows))

    # gather every RESIDUE record (row field) from the certificate shards
    residue_records = []
    for p in sorted(glob.glob(os.path.join(CERTS, '*.jsonl'))):
        with open(p) as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                rec = json.loads(line)
                if rec.get('verdict') == 'RESIDUE':
                    residue_records.append(rec)
    print('=== RESIDUE certificate records found: %d ===' % len(residue_records))

    residue_rows_claimed = set(int(r['row']) for r in residue_records)
    print('distinct row values among RESIDUE records: %d' % len(residue_rows_claimed))

    # (a) does the SET of claimed rows equal the SET of st.dat OPEN rows?
    only_in_residue = residue_rows_claimed - open_rows
    only_in_open = open_rows - residue_rows_claimed
    print('\n(a) RESIDUE.row set == st.dat OPEN set ?')
    print('    rows claimed RESIDUE but st.dat says something else: %d'
        % len(only_in_residue))
    if only_in_residue:
        sample = sorted(only_in_residue)[:10]
        print('       sample:', sample, [NAMES[int(st[r])] for r in sample])
    print('    rows st.dat marks OPEN but no RESIDUE record claims:  %d'
        % len(only_in_open))
    if only_in_open:
        print('       sample:', sorted(only_in_open)[:10])
    print('    EXACT SET MATCH: %s' % (len(only_in_residue) == 0 and len(only_in_open) == 0))

    # (b) for each RESIDUE record, does mc.encode_key(chi) resolve (via the
    # catalog's hi/lo at the STATED row) to that same row -- i.e. is the
    # record's own chi consistent with catalog[row]?
    print('\n(b) for each RESIDUE record: does its chi match catalog[row] '
        '(hi[row],lo[row]) exactly, via the reviewer\'s OWN codec?')
    mismatches = []
    for rec in residue_records:
        row = int(rec['row'])
        my_chi_at_row = mc.decode_key(int(hi[row]), int(lo[row]), M)
        if my_chi_at_row != rec['chi']:
            mismatches.append(row)
    print('    mismatches: %d / %d' % (len(mismatches), len(residue_records)))
    if mismatches:
        print('       sample:', mismatches[:10])

    # (c) duplicate row field across RESIDUE records?
    all_rows_list = [int(r['row']) for r in residue_records]
    dup = len(all_rows_list) != len(set(all_rows_list))
    print('\n(c) duplicate row values among RESIDUE records: %s (%d records, '
        '%d distinct)' % (dup, len(all_rows_list), len(set(all_rows_list))))

    ok = (len(only_in_residue) == 0 and len(only_in_open) == 0
          and not mismatches and not dup
          and all(counts[k] == claim[k] for k in claim))
    print('\n%s' % ('ALL RESIDUE<->OPEN CHECKS PASS -- the four-population '
                    'partition is a verified bijection, not arithmetic'
                    if ok else '*** MISMATCH FOUND -- SEE ABOVE ***'))

    out = {'status_counts': {NAMES[k]: v for k, v in counts.items()},
           'claimed_counts': {NAMES[k]: v for k, v in claim.items()},
           'residue_records': len(residue_records),
           'open_rows_st_dat': len(open_rows),
           'only_in_residue': sorted(only_in_residue)[:50],
           'only_in_open': sorted(only_in_open)[:50],
           'chi_mismatches': mismatches[:50],
           'duplicate_row_field': dup,
           'ALL_OK': ok}
    with open(os.path.join(HERE, 'verify_residue_open_result.json'), 'w') as fh:
        json.dump(out, fh, indent=1)
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
