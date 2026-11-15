import json,sympy as s
from pathlib import Path
src=Path('/workspace/scratch/1959cf51fea0/input/LIFTED_SYSTEM.json');j=json.loads(src.read_text());A,B,C,x,beta,L,lam=vs=s.symbols(j['variables']);eq=[s.Poly.from_dict({tuple(e):s.Rational(c) for e,c in row},vs).as_expr() for row in j['equations']];psi,E=eq[:2]
T=s.symbols('T')
f=s.cancel(C**2*psi.subs(L,T/C)).expand()
print('psi C L degrees',s.Poly(psi,C,L).degree_list(),'new C T degs',s.Poly(f,C,T).degree_list(),flush=True)
print('new poly coefficients',[(ex,s.factor(co)) for ex,co in s.Poly(f,C,T).terms()],flush=True)
