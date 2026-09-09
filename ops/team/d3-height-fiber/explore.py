"""Bounded symbolic discovery; this script does not certify a theorem."""
from pathlib import Path
import json
import hashlib
import sympy as s

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / 'ai/omreal/data/DIAG3_triple_fullspace_critical_h1.json'
assert hashlib.sha256(SRC.read_bytes()).hexdigest() == 'c9244a47ded5736e7afe724a9914e75631a22b78653442e88c14f5c397919eb8'
data = json.loads(SRC.read_text())
xs = s.symbols('a b c d e f g h i')
a,b,c,d,e,f,g,h,i = xs
qs = [s.Add(*(s.Integer(co)*s.prod(x**p for x,p in zip(xs,mo)) for co,mo in rec['terms'])) for rec in data['equations'][:3]]
print('residuals', [s.factor(q) for q in qs], flush=True)
dsol = s.solve(qs[0], d)[0]
print('d =', dsol, flush=True)
rs = [s.factor(s.together(q.subs(d,dsol))) for q in qs[1:]]
print('after d term counts',[len(s.Poly(s.fraction(r)[0],*xs).terms()) for r in rs],flush=True)
anum = s.fraction(rs[0])[0]
asol = s.factor(s.solve(anum,a)[0])
print('a denominator =',s.fraction(asol)[1],flush=True)
ff = s.factor(s.together(rs[1].subs(a,asol)))
num,den = s.fraction(ff)
print('remaining numerator terms:',len(s.Poly(num,*xs).terms()),flush=True)
print('denominator:',den,flush=True)
print('factor count',len(s.factor_list(num)[1]),flush=True)
for v in [b,c,e,f,g,h,i]:
    print('degree',v,s.degree(num,v),flush=True)
out={'variables':[str(x) for x in xs],'residuals':[str(q) for q in qs],'d':str(dsol),'a':str(asol),'numerator':str(num),'denominator':str(den)}
Path(__file__).with_name('discovery.json').write_text(json.dumps(out,indent=2)+'\n')
