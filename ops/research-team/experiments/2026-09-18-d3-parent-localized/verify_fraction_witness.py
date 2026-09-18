"""Independent Fraction determinant arithmetic for the explicit boundary witness.
Central differences are exact: each differentiated coordinate occurs in at most
 two parent columns' normal-row occurrences, hence degree at most two.
This certifies the point, not the universal parameter family or the full target.
"""
from fractions import Fraction as F
from itertools import permutations
import json
from pathlib import Path

def det(rows):
    n=len(rows); ans=F(0)
    for p in permutations(range(n)):
        sign=(-1)**sum(p[i]>p[j] for i in range(n) for j in range(i+1,n))
        term=F(sign)
        for i in range(n): term*=rows[i][p[i]]
        ans+=term
    return ans

def raw(point):
    A,B,C,D,u,v,w,t=map(F,point)
    M=[[0,0,0,1,1,1,1,1],[0,1,1,0,0,B,C,D],
       [1,0,-1,0,A,0,-1-C,-1-D],[0,0,1,0,u,v,w,t]]
    def normal(key):
        cols=[int(c)-1 for c in key]
        return [(-1)**(i+1)*det([[M[r][c] for c in cols] for r in range(4) if r!=i]) for i in range(4)]
    def poly(keys): return det([normal(k) for k in keys])
    return poly(['126','257','367','458']),poly(['157','168','245','348'])

def verify(point,j,y):
    point=list(map(F,point));j,y=F(j),F(y)
    q,r=raw(point)
    if q or r: raise AssertionError('wall equations')
    derivatives=[]
    for i in range(8):
        plus=point[:];minus=point[:];plus[i]+=1;minus[i]-=1
        qp,rp=raw(plus);qm,rm=raw(minus)
        derivatives.append(((qp-qm)/2,(rp-rm)/2))
    for i,(dq,dr) in enumerate(derivatives):
        if i!=1 and j*dq!=dr: raise AssertionError('stationary equation')
    L,U=derivatives[6][1],derivatives[1][0]
    if not L or not U or y*L*U!=1: raise AssertionError('unit equation')
    return {'Q':str(q),'R':str(r),'L':str(L),'U':str(U),'derivatives':[[str(x),str(z)] for x,z in derivatives]}

if __name__=='__main__':
    point=[3,0,-1,-3,3,1,0,-2]
    out={'status':'PASS','implementation':'Python Fraction; permutation determinants; no SymPy',
         'witness':verify(point,1,F(1,1296)),'negative_controls':0,'global_target_proved':False}
    for jj,yy in [(2,F(1,1296)),(1,F(1,1295))]:
        try: verify(point,jj,yy)
        except AssertionError: out['negative_controls']+=1
        else: raise AssertionError('bad witness accepted')
    print(json.dumps(out,indent=2))
    Path(__file__).with_name('FRACTION_REPLAY.json').write_text(json.dumps(out,indent=2)+'\n')
