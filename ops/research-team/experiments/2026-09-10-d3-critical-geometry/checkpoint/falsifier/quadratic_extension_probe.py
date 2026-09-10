from pathlib import Path
from itertools import combinations
import json,sympy as S
P=Path(__file__).resolve().parent;l=S.Symbol('lam');xs=S.symbols('x y z w');t=S.Symbol('t')
D=json.loads((P/'QUAD_INERTIA.json').read_text())['records'];As={r['trial']:S.Matrix([[S.Rational(c)for c in row]for row in r['homogeneous_matrix']])for r in D};Ds={r['trial']:r for r in D}
Y=S.Matrix([[0,0,0,1,1,1,1,1],[0,1,1,0,0,3,4,5],[1,0,-1,0,2,0,-5,-6],[0,0,t,0,*xs]])
bases=list(combinations(range(8),4));brackets=[S.Poly(Y[:,J].det(),*(xs+(t,)))for J in bases];brows=[S.Matrix([[bb.coeff_monomial(x)for x in xs+(t,)]])for bb in brackets]
class Field:
 def __init__(self,f):self.f=S.Poly(f,l,domain=S.QQ)
 def red(self,a):return S.rem(S.Poly(S.cancel(a),l,domain=S.QQ),self.f).as_expr()
 def inv(self,a):return S.invert(S.Poly(a,l,domain=S.QQ),self.f).as_expr()
 def mat(self,A):return A.applyfunc(self.red)
 def rr(self,A):
  A=self.mat(A);pivs=[];row=0
  for col in range(A.cols):
   k=next((i for i in range(row,A.rows)if A[i,col]!=0),None)
   if k is None:continue
   A.row_swap(k,row);iv=self.inv(A[row,col])
   for j in range(A.cols):A[row,j]=self.red(A[row,j]*iv)
   for i in range(A.rows):
    if i==row or A[i,col]==0:continue
    a=A[i,col]
    for j in range(A.cols):A[i,j]=self.red(A[i,j]-a*A[row,j])
   pivs.append(col);row+=1
   if row==A.rows:break
  return A,pivs
 def null(self,A):
  rr,p=self.rr(A);out=[]
  for j in range(A.cols):
   if j in p:continue
   v=S.zeros(A.cols,1);v[j]=1
   for i,k in enumerate(p):v[k]=-rr[i,j]
   out.append(v)
  return out
 def rank(self,A):return len(self.rr(A)[1])
rows=json.loads((P/'EXCEPTIONAL_PENCIL_PROBE.json').read_text())['unresolved_nonlinear_parameter_factors'];out=[]
for row in rows:
 i,j=row['trials'];A,B=As[i],As[j]
 for f,m in S.factor_list(S.sympify(row['polynomial']),l)[1]:
  F=Field(f);ns=F.null(A+l*B);N=S.Matrix.hstack(*ns);H=F.mat(N.T*B*N);z=[J for J,b in zip(bases,brows)if F.mat(b*N)==S.zeros(1,len(ns))]
  rec={'trials':[i,j],'irreducible_factor':str(f),'multiplicity':m,'real_root_isolating_intervals':[[[str(a),str(b)],mult]for(a,b),mult in S.Poly(f,l).intervals(eps=S.Rational(1,100000))],'kernel_dimension':len(ns),'kernel_basis':[[str(v)for v in n]for n in ns],'restricted_B_matrix':[[str(v)for v in H.row(k)]for k in range(H.rows)],'restricted_B_rank':F.rank(H),'whole_kernel_parent_zero_brackets_0based':z}
  if not rec['real_root_isolating_intervals']:rec['status']='no real pencil parameter'
  elif z:rec['status']='whole kernel on parent boundary'
  elif F.rank(H)==1:
   # A rank-one quadratic over any real embedding vanishes exactly on its radical.
   R=F.mat(N*S.Matrix.hstack(*F.null(H)));z=[J for J,b in zip(bases,brows)if F.mat(b*R)==S.zeros(1,R.cols)]
   rec['common_zero_radical_basis']=[[str(v)for v in R.col(k)]for k in range(R.cols)];rec['radical_parent_zero_brackets_0based']=z
   if all(R[-1,k]==0 for k in range(R.cols)):rec['status']='common-zero radical at infinity'
   elif z:rec['status']='common-zero radical on parent boundary'
   else:rec['status']='UNRESOLVED radical may be uniform'
  elif F.rank(H)==0:
   rec['status']='common-zero kernel candidate'
   for trial in range(1,30):
    v=F.mat(N*S.Matrix([S.Integer(trial)**k for k in range(N.cols)]))
    if v[-1]==0:continue
    v=F.mat(v*F.inv(v[-1]));bad=[J for J,b in zip(bases,brows)if F.mat(b*v)[0]==0]
    if bad:continue
    YY=F.mat(Y.subs(dict(zip(xs+(t,),v))));points=[]
    for K in [((0,1,2),(0,3,4),(1,3,5),(2,6,7)),Ds[i]['support_0based'],Ds[j]['support_0based']]:
     NN=F.mat(S.Matrix([[(-1)**(r+3)*YY[[k for k in range(4)if k!=r],list(J)].det(method='domain-ge')for r in range(4)]for J in K]));nn=F.null(NN);assert len(nn)==1;points.append(nn[0])
    rec['status']='actual uniform critical point';rec['point']=[str(vv)for vv in v[:4]];rec['concurrences']=[[str(vv)for vv in p]for p in points];rec['concurrence_span_rank']=F.rank(S.Matrix.hstack(*points));break
  else:rec['status']='UNRESOLVED higher-rank restriction'
  out.append(rec)
result={'scope':'Exact quotient-field expansion of all24 nonlinear exception factors, with real-root isolation; equations and parent units are reduced modulo each irreducible parameter polynomial','records':out}
(P/'QUADRATIC_EXTENSION_PROBE.json').write_text(json.dumps(result,indent=2)+'\n')
from collections import Counter
print('factors',len(out),'statuses',dict(Counter(r['status']for r in out)))
for r in out:
 if r['status'].startswith('UNRESOLVED')or r['status']=='actual uniform critical point':print(r)
