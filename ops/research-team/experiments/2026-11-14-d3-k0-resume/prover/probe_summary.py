import json,hashlib
from pathlib import Path
import sympy as s
HERE=Path(__file__).resolve().parent
src=Path('/workspace/scratch/1959cf51fea0/input/LIFTED_SYSTEM.json')
j=json.loads(src.read_text());vs=s.symbols(j['variables']);A,B,C,x,beta,L,lam=vs
ps=[s.Poly.from_dict({tuple(e):s.Rational(c) for e,c in row},vs).as_expr() for row in j['equations']]
psi,E=ps[:2];d=s.diff(E,x);n=s.diff(psi,x)
res=[]
for i in (4,6,7):
 R=s.Poly(s.expand(d*ps[i].coeff(lam,0)+n*ps[i].coeff(lam,1)),*vs[:-1])
 content,prim=R.primitive()
 assert s.expand(content*prim.as_expr()-d*ps[i].subs(lam,n/d))==0
 fac=s.factor_list(prim.as_expr())
 res.append({'input_equation_index':i,'terms':len(R.terms()),'degree':R.total_degree(),'content':str(content),'factor_profiles':[{'multiplicity':power,'terms':len(s.Poly(f,*vs[:-1]).terms()),'degree':s.Poly(f,*vs[:-1]).total_degree()} for f,power in fac[1]]})
T=s.symbols('T');m,c,l=s.symbols('m c l')
f=s.cancel(C**2*psi.subs(L,T/C)).expand()
g=s.cancel(psi.subs({C:B*c,L:B*l,beta:m/B},simultaneous=True)/B).expand()
out={'source_input_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'classification':'inconclusive exact structural probes','lambda_elimination_profiles':res,'CL_product_probe':{'C_T_degrees':s.Poly(f,C,T).degree_list(),'terms':len(s.Poly(f,A,B,C,x,beta,T).terms())},'B_scaling_probe':{'B_degree':s.degree(g,B),'terms':len(s.Poly(g,A,B,c,x,m,l).terms())},'whole_source_closures':0,'ledger':'2/9'}
(HERE/'PROBE_SUMMARY.json').write_text(json.dumps(out,indent=2,default=int)+'\n');print(json.dumps(out,indent=2,default=int))
