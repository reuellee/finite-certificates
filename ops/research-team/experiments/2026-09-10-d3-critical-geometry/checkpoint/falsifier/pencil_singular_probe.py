from pathlib import Path
from itertools import combinations
import json,sympy as S,time
P=Path(__file__).resolve().parent; data=json.loads((P/'QUAD_INERTIA.json').read_text())['records'];lam=S.Symbol('lam');xs=S.symbols('x y z w');xs5=xs+(S.Integer(1),)
As=[S.Matrix([[S.Rational(c)for c in row]for row in r['homogeneous_matrix']])for r in data]
Y=S.Matrix([[0,0,0,1,1,1,1,1],[0,1,1,0,0,3,4,5],[1,0,-1,0,2,0,-5,-6],[0,0,1,0,*xs]])
bases=list(combinations(range(8),4));brackets=[S.expand(Y[:,J].det())for J in bases]
records=[];candidates=[];start=time.time()
for n,(i,j) in enumerate(combinations(range(len(As)),2)):
 A,B=As[i],As[j];p=S.Poly((A+lam*B).det(method='domain-ge'),lam);rec={'trials':[data[i]['trial'],data[j]['trial']],'det_pencil':str(S.factor(p.as_expr()))}
 if p.is_zero:
  rec['status']='identically singular pencil';records.append(rec);continue
 roots=S.ground_roots(p.as_expr(),lam);pts=[]
 for l,mult in roots.items():
  if mult<2:continue
  M=A+l*B;null=M.nullspace()
  if len(null)!=1:
   pts.append({'lambda':str(l),'multiplicity':mult,'nullity':len(null),'status':'higher nullity not expanded'});continue
  v=null[0]
  if v[-1]==0:
   pts.append({'lambda':str(l),'multiplicity':mult,'status':'infinite kernel point'});continue
  v=v/v[-1]
  q=[S.factor((v.T*H*v)[0])for H in(A,B)]
  if q!=[0,0]:pts.append({'lambda':str(l),'multiplicity':mult,'status':'not common zero'});continue
  vals=[bb.subs(dict(zip(xs,v[:4])))for bb in brackets];zero=[J for J,val in zip(bases,vals)if val==0]
  hit={'lambda':str(l),'multiplicity':mult,'point':[str(c)for c in v[:4]],'parent_zero_brackets_0based':zero,'actual_uniform':not zero}
  if not zero:candidates.append({'trials':rec['trials'],**hit})
  pts.append(hit)
 rec['repeated_rational_root_checks']=pts;records.append(rec)
print('pairs',len(records),'identically_singular',sum(r.get('status')=='identically singular pencil'for r in records),'uniform_candidates',candidates,'seconds',time.time()-start)
(P/'PENCIL_SINGULAR_PROBE.json').write_text(json.dumps({'scope':'Exact same-data pencil determinant and repeated rational-root kernel probe; higher nullity and irrational roots not exhausted','records':records,'actual_uniform_candidates':candidates},indent=2)+'\n')
