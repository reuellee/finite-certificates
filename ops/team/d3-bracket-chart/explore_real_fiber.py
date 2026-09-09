"""Exact exploratory parent-boundary audit on the selected genus-one fiber."""
from pathlib import Path
from itertools import combinations
import json
import sympy as s

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
xs=s.symbols('a b c d e f g h i')
a,b,c,d,e,f,g,h,i=xs
data=json.loads((ROOT/'ai/omreal/data/DIAG3_triple_fullspace_critical_h1.json').read_bytes())
qs=[sum(s.Integer(co)*s.prod(x**n for x,n in zip(xs,mo)) for co,mo in rec['terms']) for rec in data['equations'][:3]]
base={b:-s.Rational(23,7),d:-5,f:-3,g:-1,h:2,i:4}
asolve=s.solve(qs[1].subs(base),a)[0]
N=s.factor(s.fraction(s.cancel(qs[2].subs(base).subs(a,asolve)))[0])
F=s.Poly(N,c,e).primitive()[1].as_expr()
D=s.Poly(s.discriminant(F,e),c).primitive()[1]
print('a graph',asolve,flush=True)
print('fiber',F,flush=True)
print('D intervals',D.intervals(eps=s.Rational(1,10000)),flush=True)
Y=s.Matrix([[1,0,0,0,1,1,1,1],[0,1,0,0,1,a,d,g],[0,0,1,0,1,b,e,h],[0,0,0,1,1,c,f,i]])
events=[]
for I in combinations(range(8),4):
    wall=Y[:,I].det().subs(base)
    numerator,denominator=map(s.factor,s.fraction(s.cancel(wall.subs(a,asolve))))
    R=s.Poly(s.resultant(F,numerator,e),c)
    if R.is_zero:
        print('IDENTICAL',I,numerator,flush=True)
        intervals=[]
    else:
        R=R.primitive()[1]
        intervals=R.intervals(eps=s.Rational(1,10000))
    events.append({'bracket':''.join(str(k+1) for k in I),'numerator':str(numerator),'denominator':str(denominator),'resultant':str(R.as_expr()),'c_intervals':str(intervals)})
    if intervals: print(events[-1]['bracket'],events[-1]['resultant'],intervals,flush=True)
out={'a':str(asolve),'F':str(F),'D':str(D.as_expr()),'D_intervals':str(D.intervals(eps=s.Rational(1,10000))),'parent_events':events}
(HERE/'real_fiber_discovery.json').write_text(json.dumps(out,indent=2)+'\n')
