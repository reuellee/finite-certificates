#!/usr/bin/env python3
"""Harvest the UNIFORM-SAMPLE corpus from ai/omreal's pilot certificate files.

    python harvest_pilot.py

The main sweep walks the mutation tree in DEPTH order, so any prefix of it
is a biased sample of the 9 276 595 classes -- shallow classes first.  The
pilot runs in ai/omreal drew classes UNIFORMLY at random from the whole
catalog (`pilot.py --sample49`, labels recorded in the matching stats JSON),
so they give an unbiased estimate of catalogue-wide quantities, at the price
of a much smaller sample.

This script collects those rows, deduplicates by canonical key (the samples
were drawn with different seeds and can overlap), and writes them in the
same schema as `harvest.py` so `minorsweep.py` can consume them unchanged.

The files used and their sampling designs are recorded in the state file.
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import minorlib as ml                                       # noqa: E402

OUT = os.path.join(HERE, 'data')

# (certificate file, stats file that records the sampling design)
FILES = [
    ('certs_4_9_s2000.jsonl', 'stats_4_9_s2000.json'),
    ('certs_4_9_cal.jsonl', 'stats_4_9_cal.json'),
    ('certs_4_9_cal2.jsonl', 'stats_4_9_cal2.json'),
    ('certs_49_u_0.jsonl', 'stats_49_u_0.json'),
    ('certs_49_u_1.jsonl', 'stats_49_u_1.json'),
    ('certs_49_u_2.jsonl', None),
    ('certs_49_u_3.jsonl', None),
    ('certs_49_u_4.jsonl', None),
    ('certs_49_u_5.jsonl', None),
]


def main():
    os.makedirs(OUT, exist_ok=True)
    seen = {}
    full = {}
    counts = {}
    labels = {}
    order = []
    for cf, sf in FILES:
        p = os.path.join(ml.OMREAL, cf)
        if not os.path.exists(p):
            print('  missing %s -- skipped' % cf)
            continue
        if sf:
            try:
                labels[cf] = json.load(open(os.path.join(ml.OMREAL, sf)))['label']
            except Exception:
                labels[cf] = None
        n = 0
        for line in open(p):
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            n += 1
            counts[rec['verdict']] = counts.get(rec['verdict'], 0) + 1
            chi = rec['chi']
            if chi in seen:
                if seen[chi] != rec['verdict'] and 'RESIDUE' not in (
                        seen[chi], rec['verdict']):
                    raise SystemExit('conflicting verdicts for %s' % chi)
                # a class settled in one run and left RESIDUE in another
                # keeps the settled verdict AND the settling certificate
                if seen[chi] == 'RESIDUE':
                    seen[chi] = rec['verdict']
                    rec.setdefault('n', 9)
                    rec.setdefault('r', 4)
                    full[chi] = rec
                continue
            seen[chi] = rec['verdict']
            order.append(chi)
            rec.setdefault('n', 9)
            rec.setdefault('r', 4)
            full[chi] = rec
        print('  %-24s %5d rows  %s' % (cf, n, labels.get(cf, '')))
    outp = os.path.join(OUT, 'harvest_uniform.jsonl')
    with open(outp, 'w') as fh:
        for chi in order:
            # the record is copied VERBATIM (upgraded if a later run settled
            # the class), so the harvest file is itself a certificate file
            # that checkcert.py can read.
            rec = dict(full[chi])
            rec['verdict'] = seen[chi]
            rec['src'] = 'pilot-uniform'
            fh.write(json.dumps(rec) + '\n')
    vc = {}
    for chi in order:
        vc[seen[chi]] = vc.get(seen[chi], 0) + 1
    st = {'files': [f for f, _ in FILES], 'labels': labels,
          'raw_counts': counts, 'distinct': len(order), 'counts': vc,
          'total_lines': len(order), 'sweep_log_tail': []}
    json.dump(st, open(os.path.join(OUT, 'harvest_uniform.state.json'), 'w'),
              indent=1)
    print('%d distinct classes -> %s' % (len(order), outp))
    print('verdicts: %s' % vc)


if __name__ == '__main__':
    main()
