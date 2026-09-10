#!/usr/bin/env python3
"""Exact relative-label orbit residue of the two-pencil support criterion.

Types50/51 each have one global occurrence. This enumerates combinatorial
factor orbits, not parent realizations. A failed criterion is not nonvanishing.
"""
from itertools import permutations
from pathlib import Path
import hashlib, json

HERE=Path(__file__).resolve().parent
SEEDS={50:((1,2,3),(1,4,5),(2,4,6),(3,7,8)),
       51:((1,2,3),(1,4,5),(2,6,7),(4,6,8))}

def move(support,p):
    return tuple(sorted(tuple(sorted(p[v-1] for v in t)) for t in support))

def inverse(p):
    return tuple(p.index(i)+1 for i in range(1,9))

def criterion(P,Q):
    union=set(P)|set(Q)
    d=tuple(sum(v in t for t in union) for v in range(1,9))
    return (min(d)<=1 or d.count(2)>=2),d

def main():
    group=tuple(permutations(range(1,9)))
    models={};align={};stab={}
    for k,seed in SEEDS.items():
        models[k]=set();align[k]={};stab[k]=[]
        for p in group:
            o=move(seed,p);models[k].add(o)
            if o not in align[k]:align[k][o]=inverse(p)
            if o==seed:stab[k].append(p)
    assert {k:len(v) for k,v in models.items()}=={50:10080,51:5040}
    counts=[];residue=[]
    for k,l in ((50,50),(50,51),(51,51)):
        anchor=SEEDS[k]
        def canon(o): return min(move(o,p) for p in stab[k])
        reps={canon(o) for o in models[l] if k!=l or o!=anchor}
        if k==l:
            def reverse(o): return canon(move(anchor,align[k][o]))
            reps={min(o,reverse(o)) for o in reps}
        passed=0
        for o in sorted(reps):
            ok,d=criterion(anchor,o)
            if ok: passed+=1
            else: residue.append({'kinds':[k,l],'anchor':anchor,'partner':o,'degree':d})
        counts.append({'kinds':[k,l],'total':len(reps),'two_pencil_covered':passed,'residue':len(reps)-passed})
    assert [r['total'] for r in counts]==[1411,1272,379]
    assert all(sorted(r['degree']) in ([3]*8,[2]+[3]*6+[4]) for r in residue)
    data={'scope':'universal geometric support-certificate applicability; not original pair-map or parent-component coverage',
          'source_commit':'59fec66666518257c585194b81061f60d91f439d',
          'counts':counts,'total':sum(r['total'] for r in counts),
          'two_pencil_covered':sum(r['two_pencil_covered'] for r in counts),
          'remaining':len(residue),'residue':residue,
          'independent_audit':'PENDING','original_D':'OPEN','original_D3':'OPEN','ledger':'2/9'}
    (HERE/'HARD_PAIR_RESIDUE.json').write_text(json.dumps(data,indent=2)+'\n')
    print(json.dumps({k:v for k,v in data.items() if k!='residue'},indent=2))

if __name__=='__main__':main()
