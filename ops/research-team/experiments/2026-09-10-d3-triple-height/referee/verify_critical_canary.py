#!/usr/bin/env python3
"""Independent integer replay; no imports from producer checkers."""
from fractions import Fraction
from itertools import combinations, permutations
from math import gcd
from functools import reduce
from pathlib import Path
import hashlib,json

ROOT=Path(__file__).resolve().parent.parent
Y=[[1,0,0,0,1,1,1,1],[0,1,0,0,1,-1,4,7],
   [0,0,1,0,1,2,-5,-4],[0,0,0,1,1,3,2,5]]
SUPPORTS={'P48':['123','145','246','356'],
          'Q39_ordinary':['125','126','356','378'],
          'R50':['123','145','246','378']}

def det(a):
    n=len(a)
    if n==0:return 1
    s=0
    for p in permutations(range(n)):
        inv=sum(p[i]>p[j] for i in range(n) for j in range(i+1,n))
        term=(-1)**inv
        for i,j in enumerate(p):term*=a[i][j]
        s+=term
    return s

def cols(a,js):return [[row[j] for j in js] for row in a]

def normal(a,edge):
    z=cols(a,[int(j)-1 for j in edge])
    return [(-1)**(k+3)*det([row for i,row in enumerate(z) if i!=k])
            for k in range(4)]

def kernel3(rows):
    v=[(-1)**j*det([[r[k] for k in range(4) if k!=j] for r in rows])
       for j in range(4)]
    g=reduce(gcd,map(abs,v));assert g
    v=[x//g for x in v]
    if next(x for x in v if x)!=abs(next(x for x in v if x)):v=[-x for x in v]
    return v

def occurrence(a,s):return det([normal(a,e) for e in s])

def poly(terms):
    out={}
    for c,word in terms:
        e=tuple(word.count(v) for v in 'abcdefghi');out[e]=out.get(e,0)+c
    return {e:c for e,c in out.items() if c}

def mul(a,b):
    out={}
    for e,c in a.items():
        for f,d in b.items():
            g=tuple(x+y for x,y in zip(e,f));out[g]=out.get(g,0)+c*d
    return {e:c for e,c in out.items() if c}

def main():
    brackets={''.join(str(j+1) for j in js):det(cols(Y,js))
              for js in combinations(range(8),4)}
    assert all(brackets.values())
    rec={}
    for name,support in SUPPORTS.items():
        rows=[normal(Y,e) for e in support];assert det(rows)==0
        kernels=[kernel3([rows[i] for i in ids]) for ids in combinations(range(4),3)]
        assert all(k==kernels[0] for k in kernels)
        rec[name]={'support':support,'normals':rows,'concurrence':kernels[0],
                   'all_three_row_subsets_rank3':True}
    p=rec['P48']['concurrence']
    assert p==rec['R50']['concurrence']
    assert p!=rec['Q39_ordinary']['concurrence']
    for name in ['Q39_ordinary','R50']:
        support=SUPPORTS[name]
        assert max(sum(str(j+1) in e for e in support) for j in range(8))<=2
        deriv=[]
        for j in range(8):
            plus=[row[:] for row in Y];minus=[row[:] for row in Y]
            for i in range(4):plus[i][j]+=p[i];minus[i][j]-=p[i]
            v=Fraction(occurrence(plus,support)-occurrence(minus,support),2)
            assert v==0;deriv.append(str(v))
        rec[name]['exact_vertical_derivatives']=deriv
    q39=poly([(1,'af'),(-1,'ai'),(-1,'cdi'),(1,'cfg'),(-1,'cf'),
              (1,'ci'),(1,'di'),(-1,'fg')])
    q48=poly([(1,'a'),(1,'bc'),(-1,'b'),(-1,'c')])
    q50=poly([(1,'bf'),(-1,'bi'),(1,'di'),(-1,'fg')])
    residual=dict(q39)
    for part in [mul(poly([(1,'f'),(-1,'i')]),q48),
                 mul(poly([(1,''),(-1,'c')]),q50)]:
        for e,c in part.items():residual[e]=residual.get(e,0)-c
    assert not any(residual.values())
    result={'verdict':'ACCEPT_INHERITED_COLLISION_CANARY_AND_GLOBAL_SYZYGY',
            'method':'Independent determinant finite differences, exact because each '
                     'occurrence has parent degree at most two; sparse integer polynomial identity.',
            'parent_matrix':Y,'parent_brackets':brackets,'records':rec,
            'syzygy':'q39=(f-i)q48+(1-c)q50','new_triple_count':0,
            'producer_proof_sha256':hashlib.sha256((ROOT/'proof/VERTICAL_CRITICAL_REDUCTION.md').read_bytes()).hexdigest()}
    (ROOT/'referee/CRITICAL_CANARY_REPLAY.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'verdict':result['verdict'],'parent_brackets':70,'vertical_derivatives':16},sort_keys=True))

if __name__=='__main__':main()
