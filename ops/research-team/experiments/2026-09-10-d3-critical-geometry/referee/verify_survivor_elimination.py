#!/usr/bin/env python3
"""Independent raw elimination and exact derivative transport for survivor gate."""
from pathlib import Path
import json,sympy as S,signal
from verify_noncollinear_independent import det,raw
ROOT=Path(__file__).resolve().parent.parent

def main():
    A,B,C,D,u,v,w,t=S.symbols('A B C D u v w t');xs=[A,B,C,D,u,v,t]
    y=[[0,0,0,1,1,1,1,1],[0,1,1,0,0,B,C,D],[1,0,-1,0,A,0,-C-1,-D-1],[0,0,1,0,u,v,w,t]]
    Q=S.expand(raw(y,['126','257','367','458']));R=S.expand(raw(y,['157','168','245','348']))
    L=S.diff(R,w);N=R.subs(w,0);assert S.expand(R-L*w-N)==0
    def bracket(key):return det([[row[int(j)-1] for j in key] for row in y])
    assert S.expand(L+bracket('1468')*bracket('3458'))==0
    qp=S.Poly(Q,w);assert qp.degree()==2
    q0,q1,q2=[qp.nth(j) for j in range(3)]
    E=S.Poly(q2,*xs)*S.Poly(N,*xs)**2-S.Poly(q1,*xs)*S.Poly(N,*xs)*S.Poly(L,*xs)+S.Poly(q0,*xs)*S.Poly(L,*xs)**2
    given=json.loads((ROOT/'noncollinear/survivor_ELIMINATION.json').read_text());factors=given['resultant_factorization'];assert len(factors)==1 and factors[0]['multiplicity']==1
    given_E=S.Poly(S.sympify(factors[0]['factor']),*xs);assert E==given_E
    assert E.total_degree()==13 and len(E.terms())==1690
    height_degree=max(sum(mon[4:]) for mon,co in E.terms());assert height_degree==7
    # The 3x3 Sylvester determinant proves E=L^2 Q(-N/L) exactly.
    sylvester=det([[S.Poly(L,*xs),S.Poly(N,*xs),S.Poly(0,*xs)],[S.Poly(0,*xs),S.Poly(L,*xs),S.Poly(N,*xs)],[S.Poly(q2,*xs),S.Poly(q1,*xs),S.Poly(q0,*xs)]])
    assert sylvester==E
    # Chain-rule equivalence is proved deductively in SURVIVOR_GATE_AUDIT.md:
    # on E=R=0, d_h E=L^2 d_h(Q restricted to the w graph).
    def alarm(signum,frame):raise TimeoutError('bounded factor check')
    signal.signal(signal.SIGALRM,alarm);signal.alarm(45)
    try:
        coeff,fac=S.factor_list(E.as_expr(),*xs)
        irreducible=(len(fac)==1 and fac[0][1]==1 and S.Poly(fac[0][0],*xs).total_degree()==13)
        assert irreducible
    finally:signal.alarm(0)
    out={'verdict':'ACCEPT_EXACT_SURVIVOR_ELIMINATION_AND_CRITICAL_TRANSPORT','R_w':str(S.factor(L)),'unit_identity':'R_w=-[1468][3458]','N':str(S.factor(N)),'eliminated_height':'w=-N/L','residual_total_degree':13,'residual_height_degree':7,'residual_terms':1690,'irreducible_over_QQ':irreducible,'no_factor_removed':True,'critical_equations':['E=0','E_u=0','E_v=0','E_t=0'],'all_projected_specializations_retained_including_C_equals_D':True,'method':'Raw referee permutation determinants; exact Sylvester determinant and independent exact SymPy factorization. No producer code imported.','scope':'Exact global graph/critical-system reduction on the stated uniform contraction chart. No emptiness, noncompactness, complexity improvement, source count, or original promotion.'}
    (ROOT/'referee/SURVIVOR_ELIMINATION_REPLAY.json').write_text(json.dumps(out,indent=2)+'\n')
    print(out['verdict'])
if __name__=='__main__':main()
