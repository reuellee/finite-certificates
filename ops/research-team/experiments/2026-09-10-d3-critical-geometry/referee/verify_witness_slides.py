#!/usr/bin/env python3
from pathlib import Path
from fractions import Fraction as F
from itertools import combinations
import json
from verify_noncollinear_independent import Y,normal,det
ROOT=Path(__file__).resolve().parent.parent

def main():
    cases=[('zero_gradient',[['123','145','246','356'],['125','126','356','378'],['123','145','257','348']],[[1,2,2,0],[1,2,0,0],[1,7,7,0]],5,[F(-1,3),F(8,11)]),('nonzero_gradients',[['123','145','246','356'],['123','146','248','378'],['126','145','248','378']],[[1,2,2,0],[1,2,-4,0],[1,-4,-4,-6]],4,[F(-4,23),F(2,5)])]
    out=[]
    for name,supports,points,moving,expected in cases:
        p=list(map(F,[F(1,2),1,1,0])); shifted=[[F(x) for x in row] for row in Y]
        for i in range(4):shifted[i][moving]+=p[i]
        # Every incidence and every original bracket is affine in this one moved parent.
        for sup,point in zip(supports,points):
            for e in sup:
                for y in [Y,shifted]:assert sum(a*b for a,b in zip(normal(y,e),point))==0
        lower=[];upper=[]
        for ids in combinations(range(8),4):
            key=''.join(str(j+1) for j in ids)
            c=det([[row[j] for j in ids] for row in Y]);assert c
            d=det([[row[j] for j in ids] for row in shifted])-c
            if d:
                root=-F(c,d)
                (lower if c*d>0 else upper).append((root,key))
        lo=max(x for x,k in lower);hi=min(x for x,k in upper);assert [lo,hi]==expected
        out.append({'name':name,'moving_parent':moving+1,'height_direction':list(map(str,p)),'full_open_interval':list(map(str,[lo,hi])),'lower_boundary':[k for x,k in lower if x==lo],'upper_boundary':[k for x,k in upper if x==hi],'all_selected_concurrences_fixed':True})
    result={'verdict':'ACCEPT_BOTH_EXACT_FULL_RESIDENCE_SLIDES','cases':out,'method':'Independent affine bracket inequalities and exact concurrence identities; no producer imports.','scope':'Specific already-covered witnesses only.'}
    (ROOT/'referee/WITNESS_SLIDES_REPLAY.json').write_text(json.dumps(result,indent=2)+'\n')
    print(result['verdict'])
if __name__=='__main__':main()
