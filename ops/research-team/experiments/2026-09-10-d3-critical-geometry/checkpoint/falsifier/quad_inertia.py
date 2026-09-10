from pathlib import Path
import json
import sympy as S
P=Path(__file__).resolve().parent
xs=S.symbols('x y z w');t=S.Symbol('t');allv=xs+(t,)
def inertia(A):
 A=S.Matrix(A);pos=neg=zero=0
 while A.rows:
  n=A.rows
  i=next((i for i in range(n) if A[i,i]),None)
  if i is not None:
   order=[i]+[j for j in range(n)if j!=i];A=A[order,order];pivot=A[0,0]
   if pivot>0:pos+=1
   else:neg+=1
   A=A[1:,1:]-A[1:,0]*A[0,1:]/pivot
  else:
   pair=next(((i,j)for i in range(n)for j in range(i+1,n)if A[i,j]),None)
   if pair is None:zero+=n;break
   i,j=pair;order=[i,j]+[k for k in range(n)if k not in pair];A=A[order,order]
   B=A[:2,:2];pos+=1;neg+=1;A=A[2:,2:]-A[2:,:2]*B.inv()*A[:2,2:]
 return [pos,neg,zero]
data=json.loads((P/'HEIGHT_OVAL_PROBE.json').read_text());out=[]
for rec in data['records']:
 for form in rec.get('residual_factors',[]):
  Q=S.Poly(S.sympify(form),*xs)
  if Q.total_degree()!=2:continue
  Hpoly=S.Add(*(coef*S.prod(v**e for v,e in zip(xs,mon))*t**(2-sum(mon))for mon,coef in Q.terms()))
  H=S.hessian(Hpoly,allv)/2;sp=H[:4,:4]
  out.append({'trial':rec['trial'],'kind':rec['kind'],'support_0based':rec['support'],'polynomial':form,'homogeneous_matrix':[[str(v)for v in H.row(i)]for i in range(5)],'homogeneous_inertia':inertia(H),'spatial_inertia':inertia(sp)})
result={'scope':'Exact rational congruence inertias of the same 22 residual quadratic restrictions; no new projected parent or occurrence samples','inertia_convention':['positive','negative','zero'],'records':out}
(P/'QUAD_INERTIA.json').write_text(json.dumps(result,indent=2)+'\n')
for r in out:print(r['trial'],r['homogeneous_inertia'],r['spatial_inertia'])
