#!/usr/bin/env python3
"""Referee-owned exact replay; only referee determinant helpers are imported."""
from pathlib import Path
from fractions import Fraction as F
from itertools import combinations, product
import hashlib,json
from verify_noncollinear_independent import Y,det,rank,normal,kernel,raw
ROOT=Path(__file__).resolve().parent.parent

def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def relabel(sup,p):return sorted(''.join(map(str,sorted(p[int(v)-1] for v in e))) for e in sup)
def brackets(y):return {''.join(str(j+1) for j in ids):det([[row[j] for j in ids] for row in y]) for ids in combinations(range(8),4)}
def shifted(y,v,motions):
    z=[list(map(F,row)) for row in y]
    for j,t in motions.items():
        for k in range(4):z[k][j]+=t*v[k]
    return z

def main():
    sup=[['123','145','246','356'],['123','146','248','378'],['126','145','248','378']]
    assert relabel(['123','145','246','357'],[2,1,3,4,8,6,7,5])==sorted(sup[1])
    assert relabel(['123','145','246','378'],[2,4,8,1,6,5,3,7])==sorted(sup[2])
    br=brackets(Y);assert len(br)==70 and all(br.values())
    ns=[];points=[]
    for s in sup:
        n=[normal(Y,e) for e in s];assert rank(n)==3 and det(n)==0
        ks=[kernel([n[j] for j in ids]) for ids in combinations(range(4),3)]
        assert all(k==ks[0] for k in ks);points.append(ks[0]);ns.append(n)
    assert points==[[1,2,2,0],[1,2,-4,0],[1,-4,-4,-6]] and rank(points)==3
    p=[F(x,2) for x in points[0]];der=[]
    for s in sup[1:]:
        assert all(sum(str(j+1) in e for e in s)<=2 for j in range(8))
        der.append([(raw(shifted(Y,p,{j:1}),s)-raw(shifted(Y,p,{j:-1}),s))/2 for j in range(8)])
    expected=list(map(F,[27,45,0,99,0,-18,0,-9]));assert der==[expected,expected]
    assert rank(der)==1 and all(any(row[4:]) for row in der)
    # Hostile controls must fail the literal concurrence and critical-wall data.
    wrong=points[1][:];wrong[0]+=1
    assert any(sum(a*b for a,b in zip(n,wrong)) for n in ns[1])
    bad=shifted(Y,p,{5:1});assert raw(bad,sup[1])!=0
    strong={'verdict':'ACCEPT_NONZERO_NONCOLLINEAR_CRITICAL_WITNESS','parent':Y,'supports':sup,'all70_parent_brackets':br,'points':points,'concurrence_rank':3,'direct_gradients':[[str(x) for x in row] for row in der],'normalized_free_height_labels':[5,6,7,8],'normalized_gradient_rank':1,'both_gradients_nonzero':True,'hostile_controls_rejected':2,'producer_json_sha256':sha('falsifier/NONZERO_NONCOLLINEAR_REPLAY.json'),'scope':'Refutes even the nonzero-gradient critical-implies-collinear claim. No compactness counterexample or original theorem.'}
    # Independent kind48 characteristic-axis canary.
    alternate=['124','135','236','456'];nn=[normal(Y,e) for e in alternate]
    assert rank(nn)==3 and det(nn)==0
    qp=[F(1,3),F(1),F(0),F(1)]
    assert all(sum(a*b for a,b in zip(n,qp))==0 for n in nn)
    v=[a+b for a,b in zip(p,qp)]
    assert v==[F(5,6),F(2),F(1),F(1)]
    def formula(u,t):return -(17*u*u*t+6*u*u-7*u*t*t+12*u*t-6*t*t)/6
    # Degree at most two in each variable follows from two occurrences of each moved parent.
    for u,t in product(map(F,[-1,0,1]),repeat=2):
        assert raw(shifted(Y,v,{4:u,5:t}),sup[0])==formula(u,t)
    axis_der=[(raw(shifted(Y,v,{j:1}),sup[0])-raw(shifted(Y,v,{j:-1}),sup[0]))/2 for j in range(8)]
    assert not any(axis_der)
    for u in [F(-1,100),F(1,100)]:
        endpoint=brackets(shifted(Y,v,{4:u}));assert all(br[k]*endpoint[k]>0 for k in br)
        assert raw(shifted(Y,v,{4:u}),sup[0])==-u*u
    assert raw(shifted(Y,v,{4:1}),sup[0])+raw(shifted(Y,v,{4:-1}),sup[0])==-2
    axis={'verdict':'ACCEPT_KIND48_FIRST_ORDER_BUT_NOT_FULL_HEIGHT_FLAT','direction':[str(x) for x in v],'second_derivative_parent5':-2,'parent_sign_interval':['-1/100','1/100'],'identity_method':'Nine rational evaluations and determinant bidegree bound (2,2).','producer_json_sha256':sha('noncollinear/KIND48_AXIS_CANARY.json'),'scope':'Kernel direction diagnostic; direction need not be another factor concurrence.'}
    out={'method':'Independent stdlib Fraction/permutation determinants; no producer imports or acceptance logic.','nonzero_noncollinear':strong,'kind48_axis':axis}
    (ROOT/'referee/NEW_CRITICAL_CANARIES_REPLAY.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'nonzero_noncollinear':strong['verdict'],'kind48_axis':axis['verdict']},sort_keys=True))
if __name__=='__main__':main()
