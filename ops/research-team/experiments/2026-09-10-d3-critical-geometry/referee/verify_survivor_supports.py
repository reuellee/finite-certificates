#!/usr/bin/env python3
"""Independent source polynomial and raw chart reconstruction; no search."""
from pathlib import Path
from itertools import combinations
import hashlib,json,sympy as S
from verify_noncollinear_independent import det,raw
ROOT=Path(__file__).resolve().parent.parent
SRC=ROOT/'checkpoint/checkpoint/checkpoint/checkpoint/inputs/DIAG3_triple_fullspace_critical_h1.json'

def main():
    source=json.loads(SRC.read_text());vs=S.symbols(' '.join(source['variables']));a,b,c,d,e,f,g,h,i=vs
    factors={o['factor']:sum(S.Integer(co)*S.prod(v**ex for v,ex in zip(vs,mon)) for co,mon in o['terms']) for o in source['equations'] if o['kind']=='factor'}
    y=[[1,0,0,0,1,1,1,1],[0,1,0,0,1,a,d,g],[0,0,1,0,1,b,e,h],[0,0,0,1,1,c,f,i]]
    supports={5563:['123','145','246','378'],16134:['126','257','367','458'],19284:['157','168','245','348']}
    ratios={}
    for ident,sup in supports.items():
        F=S.expand(raw(y,sup));ratio=S.cancel(F/factors[ident]);assert ratio in [-1,1];ratios[str(ident)]=str(ratio)
    assert ratios['16134']=='-1' and ratios['19284']=='1'
    A,B,C,D,u,v,w,t=S.symbols('A B C D u v w t')
    chart=[[0,0,0,1,1,1,1,1],[0,1,1,0,0,B,C,D],[1,0,-1,0,A,0,-C-1,-D-1],[0,0,1,0,u,v,w,t]]
    polynomials={name:S.expand(raw(chart,supports[ident])) for name,ident in [('P',5563),('Q',16134),('R',19284)]}
    assert polynomials['P']==0
    producer=json.loads((ROOT/'noncollinear/survivor_CONTRACTION_CHART.json').read_text())
    for name,F in polynomials.items():assert S.expand(F-S.sympify(producer['raw_factors'][name]))==0
    heights=[u,v,w,t];degrees={name:S.Poly(F,*heights).total_degree() for name,F in polynomials.items() if name!='P'};assert degrees=={'Q':3,'R':3}
    for ids in combinations(range(8),4):
        key=''.join(str(j+1) for j in ids);br=S.expand(det([[row[j] for j in ids] for row in chart]))
        assert S.Poly(br,*heights).total_degree()<=1
        assert S.expand(br-S.sympify(producer['parent_brackets'][key]))==0
    jac=[[S.diff(polynomials[name],h) for h in heights] for name in ['Q','R']]
    for j,k in combinations(range(4),2):
        m=S.expand(jac[0][j]*jac[1][k]-jac[0][k]*jac[1][j]);assert S.expand(m-S.sympify(producer['critical_minors'][str(j)+str(k)]))==0
    out={'verdict':'ACCEPT_SURVIVOR_ORDINARY_IDENTITIES_AND_CONTRACTION_ALGEBRA','source_sha256':hashlib.sha256(SRC.read_bytes()).hexdigest(),'canonical_row':source['canonical_row'],'named_presentation':source['named_presentation'],'ordinary_supports':supports,'raw_to_source_ratios':ratios,'height_degrees':degrees,'parent_brackets_independently_rebuilt':70,'vertical_minors_independently_rebuilt':6,'method':'Referee-owned raw permutation determinants against authenticated coefficient lists; no recovery/producer code imported.','scope':'Exact source/support transport and chart algebra only. No actual uniform critical point, survivor closure, count increment, or original promotion.'}
    (ROOT/'referee/SURVIVOR_SUPPORTS_REPLAY.json').write_text(json.dumps(out,indent=2)+'\n')
    print(out['verdict'])
if __name__=='__main__':main()
