from pathlib import Path
import sympy as S,itertools,json
P=Path(__file__).resolve().parent
t=S.symbols('t');Q=S.Rational
fixed=[S.eye(4)[:,i]for i in range(4)]+[S.ones(4,1),S.Matrix([1,7,-8,-4])]
Pi=S.Matrix([[32,4,0,5]])
def plane(*pts):return S.Matrix.hstack(*pts).T.nullspace()[0].T
def meet_line_plane(x,y,H):return S.expand((H*y)[0])*x-S.expand((H*x)[0])*y
records=[]
for q in [S.Matrix([1,2,3,3]),S.Matrix([2,-1,1,1]),S.Matrix([1,3,-1,-1]),S.Matrix([3,1,2,2]),S.Matrix([1,-2,4,4])]:
 He=plane(fixed[2],fixed[5],q);Hj=plane(fixed[3],fixed[5],q)
 if S.Matrix.vstack(Pi,He).rank()!=2 or S.Matrix.vstack(Pi,Hj).rank()!=2:continue
 ss=S.Matrix.vstack(Pi,He,Hj).nullspace()
 if len(ss)!=1:continue
 s=ss[0];r=meet_line_plane(fixed[4],q,Pi)
 if (He*r)[0]==0 or(Hj*r)[0]==0:continue
 ee=S.Matrix.vstack(Pi,He).nullspace();e0=next(v for v in ee if S.Matrix.hstack(v,s).rank()==2)
 e=e0+t*s
 # j is intersection of line(r,e) with Hj, with coefficient Hj(r) constant.
 j=S.expand((Hj*r)[0])*e-S.expand((Hj*e)[0])*r
 assert S.expand((Hj*j)[0])==0
 assert all(S.degree(x,t)<=1 for x in e.col_join(j))
 YY=S.Matrix.hstack(*fixed,e,j);bs=[];cuts=set()
 for J in itertools.combinations(range(8),4):
  raw=S.factor(YY[:,J].det());assert S.degree(raw,t)<=1
  b=raw
  if 6 in J:b/=e[0]
  if 7 in J:b/=j[0]
  b=S.cancel(b);bs.append(b)
  for pol in S.fraction(b):
   if pol==0:break
   cuts.update(S.solve(pol,t))
 if any(b==0 for b in bs):continue
 rr=sorted(cuts);segments=[];seen={}
 for lo,hi in zip([-S.oo]+rr,rr+[S.oo]):
  x=hi-1 if lo==-S.oo else lo+1 if hi==S.oo else(lo+hi)/2
  sg=tuple(int(S.sign(b.subs(t,x)))for b in bs);assert all(sg)
  seen.setdefault(sg,[]).append([str(lo),str(hi),str(x)]);segments.append({'interval':[str(lo),str(hi)],'signs':sg})
 dup=[v for v in seen.values()if len(v)>1]
 print('q',list(q),'segments',len(segments),'duplicate_chambers',len(dup),flush=True)
 records.append({'q':list(map(str,q)),'Pi':list(map(str,Pi)),'e':list(map(str,e)),'j':list(map(str,j)),'r':list(map(str,r)),'s':list(map(str,s)),'components_duplicate_chambers':dup,'all_parent_bracket_functions':list(map(str,bs))})
(P/'PERSPECTIVITY_TEST.json').write_text(json.dumps(records,indent=2)+'\n')
