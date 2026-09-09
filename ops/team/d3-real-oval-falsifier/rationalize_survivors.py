"""Replay finite-sample rationalization of frozen heuristic survivors.

This only selects discovery candidates. It cannot accept whole-oval signs.
"""
from pathlib import Path
from fractions import Fraction
import json
import numpy as np
import search_ovals as s

HERE=Path(__file__).resolve().parent


def main():
    _,_,A,B,N,walls=s.model()
    raw=json.loads((HERE/'local1.json').read_text())['survivors']
    results=[]
    for bound in (2,3,4,5,6,8,10,12,16,20):
        for old in raw:
            rational=[Fraction(float(x)).limit_denominator(bound) for x in old['base']]
            base=np.array(list(map(float,rational)))
            if len(set(rational))<5:continue
            b,f,g,h,i=base
            if i==0 or f==1 or h==1:continue
            n=s.specialize_numeric(N,base)
            for interval in s.compact_intervals(n):
                points,_=s.oval_points(base,n,s.specialize_numeric(A,base),s.specialize_numeric(B,base),interval,513)
                values=[s.evaluate(p,points) for p in walls.values()]
                if any(np.min(v)<=0<=np.max(v) for v in values):continue
                result={'base':list(map(str,rational)),
                        'interval':[float(t) for t in interval[:2]],
                        'margin':float(min(np.min(np.abs(v)) for v in values)),
                        'maxden':bound}
                if result['base'] not in [r['base'] for r in results]:results.append(result)
    results.sort(key=lambda x:(x['maxden'],-x['margin']))
    (HERE/'rational_survivors.json').write_text(json.dumps(results,indent=2)+'\n')


if __name__=='__main__':main()
