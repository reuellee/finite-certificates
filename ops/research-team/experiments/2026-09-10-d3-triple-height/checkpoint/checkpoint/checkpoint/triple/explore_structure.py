import sympy as s,json
from pathlib import Path
D=Path(__file__).parent.parent
J=json.loads((D/'inputs/DIAG3_triple_fullspace_critical_h1.json').read_text()); x=s.symbols('a:i'); a,b,c,d,e,f,g,h,i=x
q=[s.Poly.from_dict({tuple(z):v for v,z in o['terms']},x).as_expr() for o in J['equations'][:3]]
t=i-f; u=d*i-f*g
r=[s.Poly(s.cancel(y.subs(b,u/t)).as_numer_denom()[0],x).as_expr() for y in q[1:]]
A=r[0].subs(a,0); B=s.diff(r[0],a); C=r[1].subs(a,0); Dd=s.diff(r[1],a)
E=s.Poly(s.expand(B*C-Dd*A),x).as_expr()
print('R2 terms',len(s.Poly(r[0],x).terms()),'R3',len(s.Poly(r[1],x).terms()),'E',len(s.Poly(E,x).terms()))
for vs in [(c,e,h),(c,e),(c,h),(e,h),(d,g,i),(d,f,g,i)]:
 p=s.Poly(E,*vs); print('variables',vs,'degree',p.total_degree(),'monomials',p.monoms())
print('Bfactor',s.factor(B))
print('c,e,h terms factored:')
for mon,co in s.Poly(E,c,e,h).terms(): print(mon,s.factor(co))
import pickle
with open(Path(__file__).parent/'derived.pkl','wb') as out: pickle.dump({'x':x,'q':q,'R':r,'E':E},out)
