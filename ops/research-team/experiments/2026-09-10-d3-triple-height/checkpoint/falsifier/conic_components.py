#!/usr/bin/env python3
from pathlib import Path
import sympy as S,itertools,json
P=Path(__file__).resolve().parent
c,h,i,t=S.symbols('c h i t',real=True)
Y=S.Matrix([[1,0,0,0,1,1,1,1],[0,1,0,0,1,7,-S.Rational(17,4),-5*i/4-8],[0,0,1,0,1,-8,2,h],[0,0,0,1,1,c,-3,i]])
def normal(tr):
 return S.Matrix([[S.expand((-1)**(r+3)*Y[[k for k in range(4)if k!=r],[j-1 for j in tr]].det())for r in range(4)]])
F=S.Matrix.vstack(*(normal(tr)for tr in [(5,6,7),(1,5,8),(2,6,8),(3,4,7)]))
q=S.factor(F.det());print('q=',q,flush=True)
q=S.Poly(q,h,i).primitive()[1].as_expr()
assert S.expand(q.subs({h:2,i:-3}))==0
brackets=[S.expand(Y[:,J].det())for J in itertools.combinations(range(8),4)]
anchor={c:-4,i:-8,h:-S.Rational(2116,67)}
signs=[S.sign(b.subs(anchor))for b in brackets];assert all(signs)
# Lines through the rational excluded point (2,-3): h=2+t(i+3).
line=S.factor(q.subs(h,2+t*(i+3)))
rest=S.cancel(line/(i+3));assert S.degree(rest,i)==1
irat=S.factor(S.solve(rest,i)[0]);hrat=S.factor(2+t*(irat+3));grat=S.factor(-5*irat/4-8)
print('i(t)=',irat,flush=True)
records=[]
for cv in [-S.Rational(401,100),-4+S.Rational(1,10000),-4+S.Rational(1,1000),-4+S.Rational(1,500),-4+S.Rational(1,200),-S.Rational(399,100)]:
 if cv==-4:continue
 qq=S.Poly(q.subs(c,cv),h,i);CC=S.Matrix([[qq.coeff_monomial(h*h),qq.coeff_monomial(h*i)/2,qq.coeff_monomial(h)/2],[qq.coeff_monomial(h*i)/2,qq.coeff_monomial(i*i),qq.coeff_monomial(i)/2],[qq.coeff_monomial(h)/2,qq.coeff_monomial(i)/2,qq.coeff_monomial(1)]]);assert CC.det()!=0
 ip=S.cancel(irat.subs(c,cv));hp=S.cancel(hrat.subs(c,cv));gp=S.cancel(grat.subs(c,cv))
 bs=[S.factor(s*b.subs(c,cv).subs({h:hp,i:ip},simultaneous=True))for b,s in zip(brackets,signs)]
 roots=set()
 for b in bs:
  nu,de=S.fraction(b)
  for p in [nu,de]:
   for r in S.polys.polytools.intervals(p,eps=S.Rational(1,10**14)):
    (lo,hi),mult=r
    if lo==hi:roots.add(lo)
    else:
     exact=[r for r in S.solve(p,t)if r.is_real and lo<r<hi]
     assert len(exact)==1;roots.add(exact[0])
 rr=sorted(roots,key=lambda x:float(x));assert all(bool(l<r)for l,r in zip(rr,rr[1:]));bounds=[-S.oo]+rr+[S.oo];valid=[]
 for l,r in zip(bounds,bounds[1:]):
  if l==-S.oo:x=S.floor(r)-1
  elif r==S.oo:x=S.ceiling(l)+1
  else:
   # dyadic rational strictly within exact algebraic interval
   den=1
   while True:
    x=(S.floor(l*den)+1)/den
    if x<r:break
    den*=2
  vals=[S.sign(b.subs(t,x))for b in bs]
  if all(v==1 for v in vals):valid.append((l,r,x))
 # A finite parameter cut at infinity could divide one RP1 interval: determine whether infinity is admissible.
 infvals=[]
 for b in bs:
  val=S.limit(b,t,S.oo)
  infvals.append(bool(val.is_real and val.is_finite and val>0))
 infinity_valid=all(infvals)
 # Base point itself lies outside original uniform parent space (duplicate columns).
 # A rational parametrization of a nonsingular projective conic is bijective on RP1.
 # Poles correspond to affine points at infinity, excluded by fixed first-coordinate chart.
 count=len(valid)-(1 if infinity_valid and len(valid)>=2 and valid[0][0]==-S.oo and valid[-1][1]==S.oo else 0)
 print('c',cv,'components',count,'infinity',infinity_valid,'intervals',valid,flush=True)
 records.append({'c':str(cv),'conic_matrix_determinant':str(CC.det()),'exact_root_order_checked':True,'i':str(ip),'h':str(hp),'g':str(gp),'components':count,'infinity_valid':infinity_valid,'intervals':[[str(v)for v in x]for x in valid],'all_roots':[str(x)for x in rr],'parent_inequalities':[str(x)for x in bs]})
(P/'CONIC_COMPONENTS.json').write_text(json.dumps({'scope':'Actual hard50+50 full parent8 fiber for fixed anchor chirotope; no global cohomology claim','conic':str(q),'parameterization':{'i':str(irat),'h':str(hrat)},'records':records},indent=2)+'\n')
