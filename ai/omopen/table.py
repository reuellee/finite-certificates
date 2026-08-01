#!/usr/bin/env python3
"""Emit the per-class results table and the summary numbers for OPEN_ATTACK.md.

    python table.py            # markdown to stdout
"""

import json
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, 'data', 'results.jsonl')


def load():
    out = {}
    with open(RESULTS) as fh:
        for line in fh:
            line = line.strip()
            if line:
                r = json.loads(line)
                out[int(r['row'])] = r          # later record wins
    return out


def witnesses():
    """chi -> the set of family-tuples for which a witness is on file."""
    out = {}
    p = os.path.join(HERE, 'data', 'certs_no_bfp.jsonl')
    if os.path.exists(p):
        with open(p) as fh:
            for line in fh:
                line = line.strip()
                if line:
                    r = json.loads(line)
                    out.setdefault(r['chi'], set()).add(
                        tuple(r.get('families', ())))
    return out


def main():
    res = load()
    wit = witnesses()
    rows = sorted(res)
    print('| row | depth | verdict | how | s | max&#124;entry&#124; | '
          'no-FP witness (L0 / L1) |')
    print('|---|---|---|---|---|---|---|')
    for r in rows:
        d = res[r]
        how = (d.get('method') or '-').replace('weaponA:', '')
        note = d.get('note') or ''
        ent = note.split('<= ')[-1] if '<=' in note else '-'
        have = wit.get(d['chi'], set())
        w = '%s / %s' % ('yes' if ('gp3',) in have else 'NO',
                         'yes' if ('gp3', 'pl4', 'pl5') in have else 'NO')
        print('| %d | %d | %s | %s | %.1f | %s | %s |'
              % (r, d['depth'], d['verdict'], how, d['seconds'], ent, w))
    print()
    tally = {}
    src = {}
    for d in res.values():
        tally[d['verdict']] = tally.get(d['verdict'], 0) + 1
        if d['verdict'] == 'REALIZABLE':
            src[d['method']] = src.get(d['method'], 0) + 1
    print('summary:', tally)
    print('sources:', src)
    ts = sorted(d['seconds'] for d in res.values())
    print('seconds: min %.1f median %.1f max %.1f total %.0f'
          % (ts[0], ts[len(ts) // 2], ts[-1], sum(ts)))
    lp = [(d['stages'].get('weaponA', {}) or {}).get('lp_infeasible', 0)
          for d in res.values()]
    print('completion LPs refuted per class: max %d, total %d'
          % (max(lp), sum(lp)))


if __name__ == '__main__':
    main()
