#!/usr/bin/env python3
"""Re-express the sweep's `bfp` certificates in this directory's GORDAN
schema, so `fpcheck.py` can check them too.

`ai/omreal/checkcert.py` reads the sweep's schema; `fpcheck.py` reads the
one `gordan.py` emits.  They are the same object written two ways --
`gordan.gordan_record_bfp` is the map in the other direction -- so the
conversion is mechanical and adds no information:

    {"L": [1,3], "abcd": [2,4,6,8], "big": 2, "small": 0, "w": 10}
      ->
    {"rel": {"kind": "gp3", "L": [1,3], "abcd": [2,4,6,8]},
     "big": 2, "small": 0, "w": 10}

The point is that it lets the sweep's 203,780 non-realizability
certificates be put through a SECOND checker, one that additionally
re-verifies every named relation as a polynomial identity on random integer
matrices before looking at its arithmetic.  Nothing about the certificate's
content is trusted or recomputed here; only the field names change.

    python bfp2gordan.py IN.jsonl OUT.jsonl
"""

import json
import sys


def convert(rec):
    terms = []
    for t in rec['bfp']:
        terms.append({'rel': {'kind': 'gp3', 'L': list(t['L']),
                              'abcd': list(t['abcd'])},
                      'big': int(t['big']), 'small': int(t['small']),
                      'w': int(t['w'])})
    return {'n': rec['n'], 'r': rec['r'], 'chi': rec['chi'],
            'verdict': 'NON_REALIZABLE', 'method': 'GORDAN', 'level': 'L0',
            'terms': terms}


def main():
    src, dst = sys.argv[1], sys.argv[2]
    n = 0
    with open(src) as fh, open(dst, 'w') as out:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            if rec.get('verdict') != 'NON_REALIZABLE' or 'bfp' not in rec:
                continue
            out.write(json.dumps(convert(rec)) + '\n')
            n += 1
    print('converted %d certificates -> %s' % (n, dst))


if __name__ == '__main__':
    main()
