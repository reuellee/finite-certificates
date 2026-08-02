#!/usr/bin/env python3
"""The final residue's per-class outcome table and summary numbers.

    python finaltable.py                 # markdown table + summary
    python finaltable.py --tsv           # also write data/final_outcomes.tsv

Reads `data/results.jsonl` (append-only; the best record per row wins:
terminal beats non-terminal, larger budget beats smaller), the exact-gate
records `data/exactgate_*.jsonl`, and the witness file
`data/certs_no_bfp.jsonl`.
"""

import argparse
import glob
import json
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, 'data')
TERMINAL = ('REALIZABLE', 'NON_REALIZABLE')


def _read(path):
    out = []
    if os.path.exists(path):
        with open(path) as fh:
            for line in fh:
                line = line.strip()
                if line:
                    out.append(json.loads(line))
    return out


def best_results():
    best = {}
    for rec in _read(os.path.join(DATA, 'results.jsonl')):
        r = int(rec['row'])
        old = best.get(r)
        if old is None or (old['verdict'] not in TERMINAL and
                           (rec['verdict'] in TERMINAL or
                            rec.get('budget', 0) >= old.get('budget', 0))):
            best[r] = rec
    return best


def exact_records():
    out = {}
    for p in sorted(glob.glob(os.path.join(DATA, 'exactgate_*.jsonl'))):
        if 'realizable' in p or 'infeasible' in p:
            continue
        for rec in _read(p):
            r = int(rec['row'])
            old = out.get(r)
            if old is None or rec['verdict'] == 'REALIZABLE' or \
                    rec.get('exact_lp', 0) > old.get('exact_lp', 0):
                out[r] = rec
    return out


def witnesses():
    out = {}
    for rec in _read(os.path.join(DATA, 'certs_no_bfp.jsonl')):
        out.setdefault(rec['chi'], set()).add(tuple(rec.get('families', ())))
    return out


L0 = ('gp3',)
L1 = ('gp3', 'pl4', 'pl5')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--tsv', action='store_true')
    ap.add_argument('--md', default=None)
    a = ap.parse_args()

    res = best_results()
    ex = exact_records()
    wit = witnesses()
    rows = sorted(res)

    lines = []
    lines.append('| row | depth | verdict | how | s | max&#124;entry&#124; | '
                 'no-FP witness (L0 / L1) | exact gate |')
    lines.append('|---|---|---|---|---|---|---|---|')
    tsv = ['row\tdepth\tverdict\tmethod\tseconds\tmax_entry\twitness_L0\t'
           'witness_L1\texact_lp\texact_infeasible\tdeletions_covered\t'
           'fp_levels_tried']
    tally, src = {}, {}
    for r in rows:
        d = res[r]
        v = d['verdict']
        e = ex.get(r)
        if e is not None and e['verdict'] == 'REALIZABLE':
            v = 'REALIZABLE'
        tally[v] = tally.get(v, 0) + 1
        how = (d.get('method') or '-').replace('weaponA:', '')
        if e is not None and e['verdict'] == 'REALIZABLE':
            how = 'exact:' + str(e.get('found'))
        if v == 'REALIZABLE':
            src[how] = src.get(how, 0) + 1
        note = d.get('note') or ''
        ent = note.split('<= ')[-1] if '<=' in note else '-'
        have = wit.get(d['chi'], set())
        w0 = 'yes' if L0 in have else 'NO'
        w1 = 'yes' if L1 in have else 'NO'
        if e is None:
            g = '-'
            elp = ei = dc = ''
        else:
            g = '%d LP, %d inf, %d/9 p' % (e['exact_lp'],
                                           e['exact_infeasible'],
                                           len(e['deletions_covered']))
            elp, ei = e['exact_lp'], e['exact_infeasible']
            dc = len(e['deletions_covered'])
        fps = ','.join(sorted(k for k in d.get('stages', {})
                              if k.startswith('fp')))
        lines.append('| %d | %d | %s | %s | %.1f | %s | %s / %s | %s |'
                     % (r, d['depth'], v, how, d['seconds'], ent, w0, w1, g))
        tsv.append('%d\t%d\t%s\t%s\t%.2f\t%s\t%s\t%s\t%s\t%s\t%s\t%s'
                   % (r, d['depth'], v, how, d['seconds'], ent, w0, w1,
                      elp, ei, dc, fps))

    md = '\n'.join(lines)
    if a.md:
        with open(a.md, 'w') as fh:
            fh.write(md + '\n')
        print('wrote %s' % a.md)
    else:
        print(md)
    if a.tsv:
        p = os.path.join(DATA, 'final_outcomes.tsv')
        with open(p, 'w') as fh:
            fh.write('\n'.join(tsv) + '\n')
        print('wrote %s (%d rows)' % (p, len(rows)))

    print()
    print('rows            : %d' % len(rows))
    print('summary         : %s' % tally)
    print('realized by     : %s' % src)
    ts = sorted(res[r]['seconds'] for r in rows)
    print('seconds         : min %.1f median %.1f max %.1f total %.0f'
          % (ts[0], ts[len(ts) // 2], ts[-1], sum(ts)))
    lp = [(res[r]['stages'].get('weaponA', {}) or {}).get('lp_infeasible', 0)
          for r in rows]
    print('float completion LPs refuted: max %d on one class, %d total'
          % (max(lp), sum(lp)))
    nw0 = sum(1 for r in rows if L0 in wit.get(res[r]['chi'], set()))
    nw1 = sum(1 for r in rows if L1 in wit.get(res[r]['chi'], set()))
    print('certified NO biquadratic final polynomial (L0): %d / %d'
          % (nw0, len(rows)))
    print('certified no Gordan vector at L1              : %d / %d'
          % (nw1, len(rows)))
    if ex:
        tot = sum(e['exact_lp'] for e in ex.values())
        inf = sum(e['exact_infeasible'] for e in ex.values())
        print('exact gate       : %d classes, %d exact LPs, %d INFEASIBLE '
              'certificates, %d rejects'
              % (len(ex), tot, inf, sum(e.get('rejects', 0)
                                        for e in ex.values())))
        full = sum(1 for e in ex.values()
                   if len(e['deletions_covered']) == 9)
        print('                   all nine deletions covered exactly: %d/%d'
              % (full, len(ex)))
    ent = [int(res[r]['note'].split('<= ')[-1]) for r in rows
           if '<=' in (res[r].get('note') or '')]
    if ent:
        print('largest matrix entry emitted: %d (%d classes exceed 16384)'
              % (max(ent), sum(1 for v in ent if v > 16384)))


if __name__ == '__main__':
    main()
