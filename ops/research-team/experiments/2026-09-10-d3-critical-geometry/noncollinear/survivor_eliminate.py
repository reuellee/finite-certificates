from pathlib import Path
from itertools import combinations
import sympy as s,json
ROOT=Path(__file__).resolve().parents[1];obj=json.loads((ROOT/'noncollinear/survivor_CONTRACTION_CHART.json').read_text());A,B,C,D,u,v,w,t=s.symbols('A B C D u v w t');allvs=(A,B,C,D,u,v,w,t)
Q=s.sympify(obj['raw_factors']['Q']);R=s.sympify(obj['raw_factors']['R']);br={k:s.sympify(f) for k,f in obj['parent_brackets'].items()}
L=s.factor(s.diff(R,w));N=s.factor(R.subs(w,0));assert s.expand(R-L*w-N)==0
assert s.expand(L+br['1468']*br['3458'])==0
E=s.factor(s.resultant(R,Q,w));print('L',L,flush=True);print('N',N,flush=True);print('resultant factors',[(str(f) if len(s.Poly(f,*allvs).terms())<20 else ('terms'+str(len(s.Poly(f,*allvs).terms()))),m) for f,m in s.factor_list(E)[1]],flush=True)
factors=[]
for f,m in s.factor_list(E)[1]:
 matches=[I for I,b in br.items() if s.cancel(f/b) in (1,-1)]
 print('factor',s.Poly(f,*allvs).total_degree(),len(s.Poly(f,*allvs).terms()),'height',s.Poly(f,u,v,t).total_degree(),'matches',matches,flush=True)
 factors.append({'factor':str(f),'multiplicity':m,'parent_matches':matches,'height_degree':s.Poly(f,u,v,t).total_degree(),'terms':len(s.Poly(f,*allvs).terms())})
print('done',flush=True)
out={'status':'PARENT_UNIT_AFFINE_ELIMINATION','R_w':str(L),'R_at_w_zero':str(N),'R_w_parent_identity':'R_w = -[1468][3458]','w_graph':str(-N/L),'resultant_factorization':factors,'scope':'R globally solved for w in each parent residence; remaining Q equation and its critical locus unresolved.'}
(ROOT/'noncollinear/survivor_ELIMINATION.json').write_text(json.dumps(out,indent=2)+'\n')
