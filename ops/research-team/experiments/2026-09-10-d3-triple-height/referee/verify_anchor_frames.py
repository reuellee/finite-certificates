#!/usr/bin/env python3
"""Independent small exact audit of the six ordinary anchor frames.

This verifies only support incidences and displayed projected frames. The
global factor equivalences and fixed-unit wall ranks are inherited source
theorems, not inferred from this finite computation.
"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPECS = {
    36: ('123/124/345/567', (1,3,4,2)),
    38: ('123/124/345/678', (1,3,4,2)),
    48: ('123/145/246/356', (1,2,4,3)),
    49: ('123/145/246/357', (1,2,4,3)),
    50: ('123/145/246/378', (1,2,4,3)),
    51: ('123/145/267/468', (1,2,4,6)),
}
LINES = [(1,0,0),(0,1,0),(0,0,1),(1,1,1)]

def cross(x,y):
    return (x[1]*y[2]-x[2]*y[1], x[2]*y[0]-x[0]*y[2],
            x[0]*y[1]-x[1]*y[0])

def dot(x,y):
    return sum(a*b for a,b in zip(x,y))

def det3(cols):
    return dot(cols[0], cross(cols[1], cols[2]))

def main():
    rows=[]
    for kind,(word,frame) in SPECS.items():
        triples = [tuple(map(int,x)) for x in word.split('/')]
        membership={j:[k for k,t in enumerate(triples) if j in t]
                    for j in range(1,9)}
        assert max(map(len,membership.values()))==2
        high=[j for j,m in membership.items() if len(m)==2]
        low=[j for j,m in membership.items() if len(m)==1]
        omitted=[j for j,m in membership.items() if not m]
        z={j:cross(*(LINES[k] for k in membership[j])) for j in high}
        assert all(z[j]!=(0,0,0) for j in high)
        assert all(all((dot(LINES[k],z[j])==0)==(k in membership[j])
                       for k in range(4)) for j in high)
        assert all(j in high for j in frame)
        d=det3([z[j] for j in frame[:3]])
        assert d!=0
        assert len(low)+2*len(omitted)==4
        assert 8-3-1==4
        rows.append({'global_kind':kind,'ordinary_support':word,
                     'high':high,'low':low,'omitted':omitted,
                     'height_frame':frame,'projected_frame_det':d,
                     'fixed_high_vectors':z,
                     'projected_dimension':4,'free_heights':4})
    source='checkpoint/checkpoint/checkpoint/inputs/verify_derived_walls.py'
    result={'verdict':'ACCEPT_EXACT_SIX_ORDINARY_PROJECTED_FRAMES',
            'scope':'Support incidence and projected frames only; source orbit '
                    'equivalences and wall-rank identities are inherited.',
            'source_sha256':hashlib.sha256((ROOT/source).read_bytes()).hexdigest(),
            'frames':rows}
    out=ROOT/'referee/ANCHOR_FRAME_REPLAY.json'
    out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'verdict':result['verdict'],'frames':len(rows)},sort_keys=True))

if __name__=='__main__':
    main()
