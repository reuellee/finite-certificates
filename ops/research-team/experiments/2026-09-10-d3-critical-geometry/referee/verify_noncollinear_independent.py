#!/usr/bin/env python3
"""Independent rational determinant replay of the noncollinear critical point."""
from pathlib import Path
from fractions import Fraction as F
from itertools import combinations,permutations
from functools import reduce
from math import gcd
import hashlib,json
ROOT=Path(__file__).resolve().parent.parent
Y=[[1,0,0,0,1,1,1,1],[0,1,0,0,1,-1,4,7],
   [0,0,1,0,1,2,-5,-4],[0,0,0,1,1,3,2,5]]
SUP=[['123','145','246','356'],['125','126','356','378'],
     ['123','145','257','348']]

def det(a):
    n=len(a);v=0
    for p in permutations(range(n)):
        term=(-1)**sum(p[i]>p[j] for i in range(n) for j in range(i+1,n))
        for i,j in enumerate(p):term*=a[i][j]
        v+=term
    return v

def rank(rows):
    a=[[F(x) for x in row] for row in rows];r=0
    for j in range(len(a[0])):
        k=next((k for k in range(r,len(a)) if a[k][j]),None)
        if k is None:continue
        a[r],a[k]=a[k],a[r];z=a[r][j];a[r]=[x/z for x in a[r]]
        for k in range(len(a)):
            if k!=r:
                z=a[k][j];a[k]=[x-z*y for x,y in zip(a[k],a[r])]
        r+=1
        if r==len(a):break
    return r

def normal(y,edge):
    js=[int(x)-1 for x in edge]
    return [(-1)**(k+3)*det([[y[i][j] for j in js] for i in range(4) if i!=k])
            for k in range(4)]

def kernel(rows):
    v=[(-1)**k*det([[row[j] for j in range(4) if j!=k] for row in rows])
       for k in range(4)]
    g=reduce(gcd,map(abs,v));assert g;v=[x//g for x in v]
    if next(x for x in v if x)<0:v=[-x for x in v]
    return v

def raw(y,sup):return det([normal(y,e) for e in sup])

def main():
    def relabel(sup,permutation):
        return sorted(''.join(str(j) for j in sorted(permutation[int(v)-1] for v in e)) for e in sup)
    assert relabel(['123','124','345','567'],[1,2,5,6,3,7,8,4])==sorted(SUP[1])
    assert relabel(['123','145','246','357'],[1,2,3,5,4,7,8,6])==sorted(SUP[2])
    br={''.join(str(j+1) for j in ids):det([[row[j] for j in ids] for row in Y])
        for ids in combinations(range(8),4)}
    assert len(br)==70 and all(br.values())
    points=[];normals=[]
    for sup in SUP:
        n=[normal(Y,e) for e in sup];assert det(n)==0 and rank(n)==3
        ks=[kernel([n[j] for j in ids]) for ids in combinations(range(4),3)]
        assert all(k==ks[0] for k in ks);points.append(ks[0]);normals.append(n)
    assert points==[[1,2,2,0],[1,2,0,0],[1,7,7,0]] and rank(points)==3
    p=points[0];ds=[]
    for sup in SUP[1:]:
        assert max(sum(str(j+1) in e for e in sup) for j in range(8))<=2
        d=[]
        for j in range(8):
            plus=[row[:] for row in Y];minus=[row[:] for row in Y]
            for k in range(4):plus[k][j]+=p[k];minus[k][j]-=p[k]
            d.append(F(raw(plus,sup)-raw(minus,sup),2))
        ds.append(d)
    assert not any(ds[0]) and any(ds[1]) and rank(ds)==1
    predicted=[F(0),F(-45,14),F(55,14),F(-25,14),F(-5,7),F(0),F(5,14),F(5,14)]
    scale=ds[1][1]/predicted[1];assert scale and ds[1]==[scale*x for x in predicted]
    core=[normal(Y,e) for e in ['123','356','378']]
    assert rank(core)==2 and all(sum(x*y for x,y in zip(row,p))==0 for row in core)
    central=[row[2] for row in Y]
    assert all(sum(x*y for x,y in zip(row,central))==0 for row in core)
    wrong=points[2][:];wrong[0]+=1
    assert any(sum(x*y for x,y in zip(row,wrong)) for row in normals[2])
    altered=[row[:] for row in Y];altered[1][7]+=1;assert raw(altered,SUP[2])!=0
    out={'verdict':'ACCEPT_ACTUAL_NONCOLLINEAR_VERTICAL_CRITICAL_POINT',
         'method':'Independent stdlib rational determinants and exact quadratic finite differences; no producer imports.',
         'parent_matrix':Y,'parent_brackets':br,'supports':SUP,'ordinary_normals':normals,
         'projective_concurrences':points,'concurrence_rank':3,
         'distinct_global_kinds':[48,36,49],
         'direct_height_derivatives':[[str(v) for v in row] for row in ds],
         'gradient_rank':1,'R_gradient_scale_relative_to_claim':str(scale),
         'localization_core':['123','356','378'],'localization_core_rank':2,
         'anchor_on_localization_axis':True,'hostile_controls_rejected':2,
         'scope':'Refutes criticality-implies-collinearity for these fixed ordinary occurrences. Point lies in the new closed localization-axis piece. No original theorem or compactness counterexample.',
         'producer_witness_sha256':hashlib.sha256((ROOT/'noncollinear/NONCOLLINEAR_CRITICAL_WITNESS.json').read_bytes()).hexdigest()}
    (ROOT/'referee/NONCOLLINEAR_INDEPENDENT_REPLAY.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k] for k in ['verdict','concurrence_rank','gradient_rank','anchor_on_localization_axis']},sort_keys=True))

if __name__=='__main__':main()
