#!/usr/bin/env python3
"""Aggregate sharded pilot runs and extrapolate to the full (4,9) catalogue.

    python aggregate.py certs_49_u_*.jsonl            # rates + Wilson CIs
    python aggregate.py --stats stats_49_u_*.json     # stage timings too
"""

import glob
import json
import math
import sys

TOTAL_49 = 9276595


def wilson(k, n, z=1.96):
    """Wilson score interval -- honest at small counts, unlike k/n +- 2 sd."""
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def main():
    args = sys.argv[1:]
    statmode = '--stats' in args
    args = [a for a in args if not a.startswith('-')]
    paths = []
    for a in args:
        paths.extend(glob.glob(a))
    if statmode:
        S = {}
        dur = {'C': [], 'D': []}
        for p in paths:
            d = json.load(open(p))
            for k, v in d.items():
                if isinstance(v, (int, float)) and k != 'n' and k != 'r':
                    S[k] = S.get(k, 0) + v
            for t in 'CD':
                dur[t].extend(d.get('dur_' + t) or [])
        tot = S.get('total', 0)
        print('shards %d   classes %d   wall %.0f s' % (len(paths), tot, S.get('wall', 0)))
        for st in 'ABCD':
            nh, nm = S.get('n_%s_hit' % st, 0), S.get('n_%s_miss' % st, 0)
            th, tm = S.get('t_%s_hit' % st, 0.0), S.get('t_%s_miss' % st, 0.0)
            if nh + nm == 0:
                continue
            print('  stage %s  entered %6d  hit %6d @ %8.1f ms   miss %6d @ %9.1f ms'
                  '   cost %8.1f s (%5.1f%% of class-time)'
                  % (st, nh + nm, nh, 1000 * th / max(nh, 1), nm,
                     1000 * tm / max(nm, 1), th + tm, 0.0))
        for t in 'CD':
            d = sorted(dur[t])
            if d:
                q = lambda f: d[min(len(d) - 1, int(f * len(d)))]
                print('  stage %s seconds  n=%d median %.2f p90 %.2f p99 %.2f MAX %.2f'
                      % (t, len(d), q(.5), q(.9), q(.99), d[-1]))
        return

    cnt = {'REALIZABLE': 0, 'NON_REALIZABLE': 0, 'RESIDUE': 0}
    seen = set()
    for p in paths:
        for line in open(p):
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            if rec['chi'] in seen:
                continue
            seen.add(rec['chi'])
            cnt[rec['verdict']] = cnt.get(rec['verdict'], 0) + 1
    n = sum(cnt.values())
    print('sample size %d (distinct classes)' % n)
    print('%-16s %8s %9s   %-22s %s'
          % ('verdict', 'count', 'rate', '95% Wilson interval',
             'implied count out of %d' % TOTAL_49))
    for k in ('REALIZABLE', 'NON_REALIZABLE', 'RESIDUE'):
        v = cnt[k]
        lo, hi = wilson(v, n)
        print('%-16s %8d %8.3f%%   [%7.3f%%, %7.3f%%]    %9d   [%9d, %9d]'
              % (k, v, 100.0 * v / n, 100 * lo, 100 * hi,
                 round(TOTAL_49 * v / n), round(TOTAL_49 * lo),
                 round(TOTAL_49 * hi)))


if __name__ == '__main__':
    main()
