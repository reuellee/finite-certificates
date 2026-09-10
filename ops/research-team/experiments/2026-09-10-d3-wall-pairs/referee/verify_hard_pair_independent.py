"""Independently reconstruct actual rational 50/50 wall intersection.

Uses only the independent referee's standard-library determinant routines,
not producer code or stored normal matrices as mathematical input.
"""
from pathlib import Path
from fractions import Fraction as F
from itertools import combinations
from collections import Counter
import json,hashlib
from verify_tangent_independent import determinant,derive_normal,rank

ROOT=Path(__file__).resolve().parents[1]

def audit(c):
    a,b,z,d,e,f,g,h,i=map(F,c['point'])
    y=[[F(1),0,0,0,1,1,1,1],[0,1,0,0,1,a,d,g],
       [0,0,1,0,1,b,e,h],[0,0,0,1,1,z,f,i]]
    assert y==[[F(x) for x in r] for r in c['parent']]
    values=[determinant([[y[r][j] for j in cols] for r in range(4)]) for cols in combinations(range(8),4)]
    assert len(values)==70 and all(values)
    assert [1 if x>0 else -1 for x in values]==c['parent_bracket_signs']
    p,q=[tuple(tuple(t) for t in block) for block in c['supports']]
    assert p==((1,2,3),(1,4,5),(2,4,6),(3,7,8))
    swap=dict(zip(range(1,9),(5,6,7,8,1,2,3,4)))
    assert set(q)=={tuple(sorted(swap[k] for k in t)) for t in p}
    degrees=Counter(k for t in set(p)|set(q) for k in t)
    assert tuple(degrees[k] for k in range(1,9))==(3,)*8
    computed=[]
    for support,recorded in zip((p,q),c['normal_matrices']):
        rows=[derive_normal(y,tuple(k-1 for k in t)) for t in support]
        assert rows==[[F(x) for x in r] for r in recorded]
        assert determinant(rows)==0 and rank(rows)==3
        # Each selected support is an ordinary minimal4circuit: every three
        # rows have rank3, ruling out a disguised smaller support.
        assert all(rank([rows[k] for k in three])==3 for three in combinations(range(4),3))
        computed.append(rows)
    return {'uniform_brackets':70,'support_ranks':[3,3],
            'all_three_row_subsets_independent':True,'union_degrees':[3]*8}

def main():
    p=ROOT/'falsifier/HARD_PAIR_POINT.json';c=json.loads(p.read_text());result=audit(c)
    bad=json.loads(json.dumps(c));bad['point'][0]=str(F(bad['point'][0])+1)
    try:audit(bad)
    except AssertionError:pass
    else:raise AssertionError('corrupted point accepted')
    result.update({'status':'PASS','certificate_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
                   'scope':'one actual uniform two-factor point; no compact-support cohomology result',
                   'hostile_rejections':['point'],'original_obligations_closed':0})
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
