import sympy as s,pickle,json,time
from pathlib import Path
P=Path(__file__).parent
z=pickle.load(open(P/'derived.pkl','rb'));x=z['x'];a,b,c,d,e,f,g,h,i=x;q=z['q'];t=i-f;u=d*i-f*g
v0=q[2].subs(c,0);v1=s.diff(q[2],c)
print('v1',s.factor(v1),flush=True)
# q2 as quadratic c, with coefficients degree<=1 a; numerator exact elimination.
pc=s.Poly(q[1],c); num=s.expand(pc.nth(0)*v1**2-pc.nth(1)*v0*v1+pc.nth(2)*v0**2)
print('num terms',len(s.Poly(num,x).terms()),flush=True)
num=s.cancel(num.subs(b,u/t)).as_numer_denom()[0]
fac=s.factor_list(num);print('factor counts',[(s.Poly(y,x).total_degree(),len(s.Poly(y,x).terms()),e)for y,e in fac[1]],flush=True)
for y,k in fac[1]:
 if a in y.free_symbols:
  p=s.Poly(y,a);print('a degree',p.degree(),flush=True);print('a2',s.factor(p.nth(2)),flush=True)
  dd=s.factor(p.nth(1)**2-4*p.nth(2)*p.nth(0));print('discriminant',dd,flush=True)
  pickle.dump({'Eca':y,'disc':dd,'q':q,'x':x},open(P/'double_cover.pkl','wb'))
