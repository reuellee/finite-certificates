"""Bounded discovery in parent-bracket coordinates; no theorem flags."""
from pathlib import Path
import json
import hashlib
import time
import sympy as s

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
source = ROOT / 'ai/omreal/data/DIAG3_triple_fullspace_critical_h1.json'
assert hashlib.sha256(source.read_bytes()).hexdigest() == 'c9244a47ded5736e7afe724a9914e75631a22b78653442e88c14f5c397919eb8'
xs = s.symbols('a b c d e f g h i')
a,b,c,d,e,f,g,h,i = xs
u,v = s.symbols('u v')
data = json.loads(source.read_bytes())
qs = [sum(s.Integer(co)*s.prod(x**n for x,n in zip(xs,mo)) for co,mo in rec['terms']) for rec in data['equations'][:3]]
sub = {d:(b*(i-f)+f*g)/i, e:(b*f-u)/c, a:(v+b*g)/h}
out = {'variables':[str(x) for x in (b,c,f,g,h,i,u,v)], 'substitution':{str(k):str(x) for k,x in sub.items()}, 'equations':[]}
start = time.monotonic()
reduced = []
for q in qs[1:]:
    p,den = s.fraction(s.cancel(q.subs(sub)))
    p = s.Poly(p,b,c,f,g,h,i,u,v).as_expr()
    reduced.append(p)
    rec = {'terms':len(s.Poly(p).terms()), 'numerator':str(p), 'denominator':str(den), 'degrees':[int(s.degree(p,x)) for x in (b,c,f,g,h,i,u,v)]}
    out['equations'].append(rec)
    print('bracket equation', rec['terms'], rec['degrees'], 'den',den,flush=True)
K = s.factor(s.resultant(*reduced,v))
print('resultant factors',[(len(s.Poly(p).terms()),n) for p,n in s.factor_list(K)[1]],flush=True)
out['resultant_v'] = str(K)
primitive = max(s.factor_list(K)[1], key=lambda pn:len(s.Poly(pn[0]).terms()))[0]
print('primitive u degree',s.degree(primitive,u),flush=True)
coeffs = s.Poly(primitive,u).all_coeffs()
disc = s.expand(coeffs[1]**2-4*coeffs[0]*coeffs[2])
vars7 = (b,c,f,g,h,i,u)
out['discriminant_u'] = {'terms':[[int(co),list(mo)] for mo,co in s.Poly(disc,*vars7).terms()], 'variables':list(map(str,vars7))}
print('discriminant terms',len(out['discriminant_u']['terms']),flush=True)
out['seconds'] = time.monotonic()-start
HERE.joinpath('bracket_discovery.json').write_text(json.dumps(out,indent=2)+'\n')
