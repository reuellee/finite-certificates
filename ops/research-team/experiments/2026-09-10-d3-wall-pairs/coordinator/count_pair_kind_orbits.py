#!/usr/bin/env python3
"""Burnside accounting for the inherited six factor actions.

This is orbit bookkeeping, not a computation of cohomology. The identification
of these combinatorial actions with the residual factors requires the pinned
occurrence identities and independent source audit.
"""
from collections import Counter
from itertools import combinations, permutations
from math import factorial
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
KINDS = (36, 38, 48, 49, 50, 51)
SIZES = (840, 280, 420, 10080, 10080, 5040)

def mask(s):
    return sum(1 << (int(c)-1) for c in s)

# A tuple of colored, unordered collections of vertex subsets.
SEEDS = {
  36: ((mask('3'),), (mask('8'),), tuple(map(mask, ('12','45','67')))),
  38: ((mask('12'),), tuple(map(mask, ('345','678')))),
  48: ((mask('78'),), tuple(map(mask, ('16','25','34')))),
  49: (tuple(map(mask, ('123','145','246','357'))),),
  50: (tuple(map(mask, ('123','145','246','378'))),),
  51: (tuple(map(mask, ('123','145','267','468'))),),
}

def permute_bits(value, perm):
    return sum(1 << perm[i] for i in range(8) if (value >> i) & 1)

def action(obj, perm):
    return tuple(tuple(sorted(permute_bits(v, perm) for v in part)) for part in obj)

def partitions(n, least=1):
    if n == 0:
        yield ()
    for i in range(least, n+1):
        for rest in partitions(n-i, i):
            yield (i,) + rest

def class_data(part):
    p = list(range(8)); pos = 0
    for length in part:
        for j in range(length):
            p[pos+j] = pos + (j+1) % length
        pos += length
    z = 1
    for length, count in Counter(part).items():
        z *= length**count * factorial(count)
    return tuple(p), factorial(8)//z

def main():
    group = tuple(permutations(range(8)))
    objects = {k: {action(SEEDS[k], p) for p in group} for k in KINDS}
    assert tuple(len(objects[k]) for k in KINDS) == SIZES
    classes=[]
    totals={(k,l):0 for i,k in enumerate(KINDS) for l in KINDS[i:]}
    for part in partitions(8):
        p, size = class_data(part)
        square = tuple(p[p[i]] for i in range(8))
        fixed={k: sum(action(o,p)==o for o in objects[k]) for k in KINDS}
        fixed_square={k: sum(action(o,square)==o for o in objects[k]) for k in KINDS}
        for k,l in totals:
            if k==l:
                value = (fixed[k]*(fixed[k]-1) + fixed_square[k]-fixed[k])//2
            else:
                value = fixed[k]*fixed[l]
            totals[k,l] += size*value
        classes.append({'partition':part,'class_size':size,'fixed':fixed,'fixed_square':fixed_square})
    assert len(classes)==22 and sum(c['class_size'] for c in classes)==40320
    assert all(v%40320==0 for v in totals.values())
    counts={kl:v//40320 for kl,v in totals.items()}
    assert sum(counts.values())==9476
    covered=lambda k,l: bool({k,l}&{36,38,48}) or (k,l)==(49,49)
    rows=[{'kinds':[k,l],'unordered_pair_orbits':n,'template_covered':covered(k,l)} for (k,l),n in counts.items()]
    report={'scope':'factor-pair orbit accounting; no parent-component census or cohomology computation',
      'source_commit':'59fec66666518257c585194b81061f60d91f439d',
      'factor_sizes':dict(zip(KINDS,SIZES)), 'classes':classes,'pair_kind_counts':rows,
      'total':sum(counts.values()),
      'template_covered':sum(r['unordered_pair_orbits'] for r in rows if r['template_covered']),
      'template_remaining':sum(r['unordered_pair_orbits'] for r in rows if not r['template_covered']),
      'factor_action_identification':'REQUIRES_INDEPENDENT_SOURCE_AUDIT',
      'original_ledger':'2/9'}
    (HERE/'PAIR_KIND_ORBIT_COUNTS.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='classes'},indent=2))

if __name__=='__main__':
    main()
