"""Bounded genus/degeneration discovery from the existing exact graph."""
from pathlib import Path
import json
import sympy as s

HERE=Path(__file__).resolve().parent
xs=s.symbols('b c e f g h i')
b,c,e,f,g,h,i=xs
old=json.loads(HERE.with_name('d3-height-fiber').joinpath('discovery.json').read_bytes())
N=s.Poly(s.sympify(old['numerator']),*xs)
coeffs=[]
for k in range(3):
    terms={tuple(m[j] if j!=2 else 0 for j in range(7)):co for m,co in N.terms() if m[2]==k}
    coeffs.append(s.Poly.from_dict(terms,xs))
D=coeffs[1]**2-4*coeffs[0]*coeffs[2]
print('N bidegree',N.degree(c),N.degree(e),'D c degree',D.degree(c),'terms',len(D.terms()),flush=True)
sample={b:-s.Rational(23,7),f:-3,g:-1,h:2,i:4}
ns=s.Poly(N.as_expr().subs(sample),c,e)
ds=s.Poly(D.as_expr().subs(sample),c)
print('sample N',s.factor(ns.as_expr()),flush=True)
print('sample D',s.factor(ds.as_expr()),flush=True)
print('gcd',s.gcd(ds,ds.diff()),flush=True)
out={'variables':list(map(str,xs)), 'N':[[int(co),list(m)] for m,co in N.terms()], 'discriminant':[[int(co),list(m)] for m,co in D.terms()], 'sample':{str(k):str(v) for k,v in sample.items()}, 'sample_N':str(ns.as_expr()),'sample_D':str(ds.as_expr()),'sample_gcd':str(s.gcd(ds,ds.diff()).as_expr())}
(HERE/'quartic_discovery.json').write_text(json.dumps(out,indent=2)+'\n')
