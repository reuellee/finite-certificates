from pathlib import Path
from itertools import combinations
import json,sympy as S,time
P=Path(__file__).resolve().parent; data=json.loads((P/'QUAD_INERTIA.json').read_text())['records'];lam=S.Symbol('lam');cs=S.symbols('c0:5');xs=S.symbols('x y z w');xs5=xs+(S.Integer(1),)
Ds={r['trial']:r for r in data};As={r['trial']:S.Matrix([[S.Rational(c)for c in row]for row in r['homogeneous_matrix']])for r in data}
Yh=S.Matrix([[0,0,0,1,1,1,1,1],[0,1,1,0,0,3,4,5],[1,0,-1,0,2,0,-5,-6],[0,0,1,0,*xs]])
bases=list(combinations(range(8),4));brackets=[S.expand(Yh[:,J].det())for J in bases]
rows=json.loads((P/'PENCIL_SINGULAR_PROBE.json').read_text())['records'];out=[];hit=[];start=time.time()
for row in rows:
 if row.get('status')!='identically singular pencil':continue
 i,j=row['trials'];A,B=As[i],As[j];M=A+lam*B;ns=M.nullspace();v=sum((c*n for c,n in zip(cs,ns)),S.zeros(5,1));v=v.applyfunc(S.factor)
 q=[S.factor((v.T*H*v)[0])for H in(A,B)];assert q==[0,0]
 rec={'trials':[i,j],'generic_nullity':len(ns),'kernel_basis':[[str(e)for e in n]for n in ns]}
 if v[-1]==0:rec['status']='entire generic kernel at infinity'
 else:
  vd=v/v[-1];bv=[S.factor(bb.subs(dict(zip(xs,vd[:4]))))for bb in brackets];zeros=[J for J,b in zip(bases,bv)if b==0];rec['identically_zero_parent_brackets_0based']=zeros
  if zeros:rec['status']='entire generic kernel lies on parent boundary'
  else:
   rec['status']='potential uniform critical family';hit.append(rec)
   for la in [1,2,3,-1,-2]:
    vv=vd.subs({lam:la,**{c:k+1 for k,c in enumerate(cs)}})
    if any(e.has(S.zoo,S.nan)for e in vv):continue
    vals=[S.factor(bb.subs(dict(zip(xs,vv[:4]))))for bb in brackets]
    if any(e==0 for e in vals):continue
    Y=Yh.subs(dict(zip(xs,vv[:4])));points=[]
    for K in [((0,1,2),(0,3,4),(1,3,5),(2,6,7)),Ds[i]['support_0based'],Ds[j]['support_0based']]:
     N=S.Matrix([[(-1)**(r+3)*Y[[k for k in range(4)if k!=r],list(J)].det()for r in range(4)]for J in K]);points.append(N.nullspace()[0])
    rec['exact_uniform_point']=[str(e)for e in vv[:4]];rec['concurrences']=[[str(e)for e in p]for p in points];rec['concurrence_span_rank']=S.Matrix.hstack(*points).rank();break
 out.append(rec)
print('families',len(out),'hits',hit,'seconds',time.time()-start)
(P/'SINGULAR_PENCIL_FAMILY.json').write_text(json.dumps({'scope':'Symbolic generic kernels of the same-data 38 identically singular pencils; no new parent projection sampling','records':out},indent=2)+'\n')
