#!/usr/bin/env python3
"""Harvest the classes we need from the (4,9) sweep's certificate shards.

    python harvest.py --tag sweep                # first pass
    python harvest.py --tag sweep --extend       # continue from recorded offsets

The sweep in ai/omreal is LIVE and its shards are append-only.  This reader

  * opens the shards read-only in binary and never writes to ai/omreal;
  * consumes only COMPLETE lines (a line must end in b'\\n'), so a record
    half-written at the moment of reading is left for the next pass;
  * records, per shard, the byte offset just past the last complete line and
    the number of lines consumed, so `--extend` resumes exactly there and a
    later re-run EXTENDS the measurement instead of redoing it.

It keeps the full record for the classes whose minors we want to test
(NON_REALIZABLE and RESIDUE) and only a count for the rest -- the REALIZABLE
records carry a 4x9 matrix each and there are a million of them.

A separate `--realizable-sample K` keeps every K-th REALIZABLE record too;
those are the canary corpus (a realizable class must have NO non-realizable
minor, by the deletion lemma).
"""

import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, '..', '..'))
SHARDS = os.path.join(REPO, 'ai', 'omreal', 'sweep_state', 'certs')
OUT = os.path.join(HERE, 'data')

KEEP = ('NON_REALIZABLE', 'RESIDUE')


def shard_paths():
    return sorted(os.path.join(SHARDS, f) for f in os.listdir(SHARDS)
                  if f.endswith('.jsonl'))


def scan(path, start, out_fh, counts, rsample, rmod):
    """Consume complete lines from `start`; return (new offset, lines read)."""
    nlines = 0
    off = start
    base = os.path.basename(path)
    with open(path, 'rb') as fh:
        fh.seek(start)
        buf = b''
        while True:
            chunk = fh.read(1 << 22)
            if not chunk:
                break
            buf += chunk
            cut = buf.rfind(b'\n')
            if cut < 0:
                continue
            body, buf = buf[:cut + 1], buf[cut + 1:]
            off += len(body)
            for line in body.split(b'\n'):
                if not line.strip():
                    continue
                rec = json.loads(line)
                v = rec.get('verdict')
                counts[v] = counts.get(v, 0) + 1
                nlines += 1
                keep = v in KEEP
                if not keep and rsample and v == 'REALIZABLE':
                    rmod[0] += 1
                    keep = rmod[0] % rsample == 0
                if keep:
                    # the record is copied VERBATIM, so the harvest file is
                    # itself a certificate file that checkcert.py can read.
                    rec['src'] = base
                    out_fh.write(json.dumps(rec) + '\n')
    return off, nlines


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--tag', default='sweep')
    ap.add_argument('--extend', action='store_true')
    ap.add_argument('--realizable-sample', type=int, default=0,
                    help='also keep every K-th REALIZABLE record (canary corpus)')
    a = ap.parse_args()

    os.makedirs(OUT, exist_ok=True)
    statep = os.path.join(OUT, 'harvest_%s.state.json' % a.tag)
    outp = os.path.join(OUT, 'harvest_%s.jsonl' % a.tag)

    if a.extend and os.path.exists(statep):
        st = json.load(open(statep))
    else:
        st = {'offsets': {}, 'lines': {}, 'counts': {}, 'kept': 0,
              'realizable_sample': a.realizable_sample, 'rmod': 0}
    if a.realizable_sample and st.get('realizable_sample') != a.realizable_sample:
        raise SystemExit('realizable-sample stride changed; use a new --tag')

    counts = dict(st['counts'])
    rmod = [int(st.get('rmod', 0))]
    t0 = time.time()
    with open(outp, 'a' if a.extend else 'w') as out_fh:
        for p in shard_paths():
            b = os.path.basename(p)
            start = int(st['offsets'].get(b, 0)) if a.extend else 0
            off, nl = scan(p, start, out_fh, counts, a.realizable_sample, rmod)
            st['offsets'][b] = off
            st['lines'][b] = int(st['lines'].get(b, 0)) + nl if a.extend else nl
            print('  %-18s +%d lines, offset %d' % (b, nl, off))
    st['counts'] = counts
    st['rmod'] = rmod[0]
    st['total_lines'] = sum(st['lines'].values())
    st['wall_s'] = time.time() - t0
    st['when'] = time.strftime('%Y-%m-%dT%H:%M:%S')
    # the sweep's own progress line, verbatim, so the prefix is nameable
    logp = os.path.join(REPO, 'ai', 'omreal', 'sweep_run2.log')
    try:
        st['sweep_log_tail'] = [ln.rstrip('\n')
                                for ln in open(logp).read().splitlines()][-1:]
    except OSError:
        st['sweep_log_tail'] = []
    json.dump(st, open(statep, 'w'), indent=1)
    print('total lines consumed: %d' % st['total_lines'])
    print('verdicts: %s' % counts)
    print('kept -> %s' % outp)


if __name__ == '__main__':
    main()
