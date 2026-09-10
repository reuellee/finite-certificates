from pathlib import Path
from itertools import combinations,permutations
import random,json,time
import sympy as S
P=Path(__file__).resolve().parent;xs=S.symbols('x y z w');x,y,z,w=xs
rng=random.Random(934251)
proj=(2,3,4,5)
a,b,c,d=map(S.Integer,proj)
Y=S.Matrix([[0,0,0,1,1,1,1,1],[0,1,1,0,0,b,c,d],[1,0,-1,0,a,0,-1-c,-1-d],[0,0,1,0,x,y,z,w]])
trs=list(combinations(range(8),3));bas=list(combinations(range(8),4))
def normal(J):return [S.expand((-1)**(r+3)*Y[[k for k in range(4)if k!=r],list(J)].det())for r in range(4)]
N={J:normal(J)for J in trs}
bpol=[S.Poly(Y[:,J].det(),*xs)for J in bas]
assert all(p.total_degree()<=1 and p.as_expr()!=0 for p in bpol)
uniform_height=(-87,-32,-78,96)
uniform_values=[p.as_expr().subs(dict(zip(xs,uniform_height)))for p in bpol]
assert all(v!=0 for v in uniform_values)
anchor=((0,1,2),(0,3,4),(1,3,5),(2,6,7))
anchor_normals=S.Matrix([N[J]for J in anchor])
assert anchor_normals.det()==0
anchor_at=anchor_normals.subs(dict(zip(xs,uniform_height)))
assert anchor_at.rank()==3
assert all(anchor_at[list(rows),:].rank()==3 for rows in combinations(range(4),3))
def canon(p):
 p=S.Poly(p,*xs)
 if p.is_zero:return ()
 return tuple((m,str(c/p.LC()))for m,c in p.terms())
units={canon(p.as_expr())for p in bpol}
proto=[((0,1,2),(0,3,4),(1,3,5),(2,6,7)),((0,1,2),(0,3,4),(1,5,6),(3,5,7))]
seen=set();records=[];linear=[];quad=[];start=time.time()
for trial in range(120):
 while True:
  pm=list(range(8));rng.shuffle(pm);typ=rng.randrange(2)
  K=tuple(sorted(tuple(sorted(pm[i]for i in t))for t in proto[typ]))
  if K not in seen:seen.add(K);break
 M=S.Matrix([N[J]for J in K]);D=S.Poly(M.det(method='domain-ge'),*xs)
 if D.is_zero:
  records.append({'trial':trial,'kind':50+typ,'support':K,'residual_degrees':'identically_zero'});continue
 factors=S.factor_list(D.as_expr())[1];remain=[]
 for fac,mul in factors:
  if canon(fac)not in units:
   degree=S.Poly(fac,*xs).total_degree();remain.append((fac,degree))
   if degree==1:linear.append((trial,fac,K))
   if degree==2:quad.append((trial,fac,K))
 rec={'trial':trial,'kind':50+typ,'support':K,'residual_degrees':[dd for f,dd in remain],'residual_factors':[str(f)for f,dd in remain]};records.append(rec)
 if(trial+1)%20==0:print('trial',trial+1,'linear',len(linear),'quad',len(quad),'seconds',round(time.time()-start,1),flush=True)
checks=[]
for li,L,LK in linear:
 k=next(k for k,q in enumerate(xs)if S.diff(L,q)!=0);var=xs[k];others=[q for q in xs if q!=var];sol=S.solve(L,var)[0]
 for qi,Q,QK in quad:
  if len(checks)>=120:break
  qq=S.Poly(S.expand(Q.subs(var,sol)),*others)
  H=S.hessian(qq.as_expr(),others)/2
  minors=[H[:j,:j].det()for j in range(1,4)]
  sg=1 if all(m>0 for m in minors)else -1 if all((-1)**j*m>0 for j,m in enumerate(minors,1)) else 0
  if not sg:
   checks.append({'linear_trial':li,'quad_trial':qi,'definite':False});continue
  H=sg*H;qq=sg*qq.as_expr();grad=S.Matrix([S.diff(qq,q).subs(dict.fromkeys(others,0))for q in others]);center=-H.inv()*grad/2
  centerdict=dict(zip(others,center));radius2=-S.expand(qq.subs(centerdict));cuts=[]
  if radius2>0:
   for J,B in zip(bas,bpol):
    p=S.expand(B.as_expr().subs(var,sol));value=S.expand(p.subs(centerdict));v=S.Matrix([S.diff(p,q)for q in others]);margin=S.factor(value**2-radius2*(v.T*H.inv()*v)[0])
    if margin<=0:cuts.append(J)
  rec={'linear_trial':li,'quad_trial':qi,'definite':True,'radius_squared':str(radius2),'cut_parent_brackets':cuts,'isolated_or_compact_oval':bool(radius2>=0 and not cuts),'linear':str(L),'quadratic_restriction':str(qq)}
  checks.append(rec);print('DEFINITE',rec,flush=True)
 if len(checks)>=120:break
out={'scope':'Bounded actual determinant restriction probe; no universal claim','projected_parent_parameters':proj,'height_matrix':[[str(v)for v in Y.row(i)]for i in range(4)],'anchor_support_1based':['123','145','246','378'],'exact_uniform_height':uniform_height,'uniform_parent_brackets_1based':{''.join(str(j+1)for j in J):str(v)for J,v in zip(bas,uniform_values)},'anchor_rank_at_uniform_height':3,'all_three_anchor_normals_independent_at_uniform_height':True,'occurrence_instantiations':len(records),'linear_residuals':len(linear),'quadratic_residuals':len(quad),'records':records,'ellipsoid_tests':checks,'original_obligations_closed':0}
(P/'HEIGHT_OVAL_PROBE.json').write_text(json.dumps(out,indent=2)+'\n');print('DONE',len(linear),len(quad),len(checks),flush=True)
