#!/usr/bin/env python3
"""Raw permutation determinants independently verify the specific global graph."""
from pathlib import Path
import json,hashlib
import sympy as S
from verify_noncollinear_independent import det,normal,raw
ROOT=Path(__file__).resolve().parent.parent

def main():
    a,b,c,d,e,f,g,h,i=S.symbols('a b c d e f g h i')
    y=[[1,0,0,0,1,1,1,1],[0,1,0,0,1,a,d,g],[0,0,1,0,1,b,e,h],[0,0,0,1,1,c,f,i]]
    supports=[['123','145','246','356'],['123','146','248','378'],['126','145','248','378']]
    P,Q,R=[S.expand(raw(y,s)) for s in supports]
    D=b*d-b*f*(b-1)-a*h;G=b*g-b*i*(b-1)-a*h
    assert S.expand(P-(a+b*c-b-c))==0
    assert S.expand(Q-f*G+i*D)==0
    assert S.expand(b*(R-Q)-c*h*(D-G)-b*h*(f-i)*P)==0
    units={'1246':-b,'1236':c,'1248':-h,'2378':i-f}
    for key,value in units.items():
        assert S.expand(det([[row[int(j)-1] for j in key] for row in y])-value)==0
    solution={a:b+c-b*c,d:f*(b-1)+(b+c-b*c)*h/b,g:i*(b-1)+(b+c-b*c)*h/b}
    assert all(S.cancel(v.subs(solution,simultaneous=True))==0 for v in [P,Q,R,D,G])
    # On the parent-unit locus the first identity and D=G force D=G=0.
    coefficient=S.Matrix([[-i,f],[c*h,-c*h]])
    assert S.expand(coefficient.det()-c*h*(i-f))==0
    # A wrong identity or graph coefficient must be rejected.
    assert S.expand(Q-f*G+i*D+1)!=0
    wrong=dict(solution);wrong[d]+=1
    assert S.cancel(D.subs(wrong,simultaneous=True))!=0
    out={'verdict':'ACCEPT_SPECIFIC_GLOBAL_RATIONAL_GRAPH','supports':supports,'raw_determinants':list(map(str,[P,Q,R])),'auxiliary_equations':list(map(str,[D,G])),'units':{k:str(v) for k,v in units.items()},'graph':{str(k):str(v) for k,v in solution.items()},'free_coordinates':['b','c','e','f','h','i'],'coefficient_determinant':str(S.factor(coefficient.det())),'hostile_controls_rejected':2,'method':'Referee-owned permutation determinants; SymPy only simplifies independently reconstructed expressions. No producer imports.','scope':'Specific support triple and its relabelings; global uniform sign residences form open subsets of R6. No new numerical orbit credit.'}
    (ROOT/'referee/GLOBAL_GRAPH_REPLAY.json').write_text(json.dumps(out,indent=2)+'\n')
    print(out['verdict'])
if __name__=='__main__':main()
