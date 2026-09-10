from pathlib import Path
import itertools,json,hashlib
import sympy as S
P=Path(__file__).resolve().parent
u,v=S.symbols('u v');Q=S.Rational
fixed=[S.eye(4)[:,i]for i in range(4)]+[S.ones(4,1),S.Matrix([1,7,-8,-4])]
Pi=S.Matrix([[32,4,0,5]]);q=S.Matrix([1,2,3,3])
def n(pts):
 Y=S.Matrix.hstack(*pts)
 return S.Matrix([[(-1)**(r+3)*Y[[k for k in range(4)if k!=r],:].det()for r in range(4)]])
He=n([fixed[2],fixed[5],q]);Hj=n([fixed[3],fixed[5],q])
ss=S.Matrix.vstack(Pi,He,Hj).nullspace();assert len(ss)==1;s=ss[0]
r=(Pi*q)[0]*fixed[4]-(Pi*fixed[4])[0]*q
E=next(x for x in S.Matrix.vstack(Pi,He).nullspace()if S.Matrix.hstack(x,s).rank()==2)
for tau in map(S.Integer,range(1,20)):
 e=E+tau*s;j=(Hj*r)[0]*e-(Hj*e)[0]*r
 if e[0]==0 or j[0]==0:continue
 e=e/e[0];j=j/j[0];Y=S.Matrix.hstack(*fixed,e,j)
 vals=[Y[:,J].det()for J in itertools.combinations(range(8),4)]
 if all(vals):break
else:raise AssertionError('No uniform anchor')
He=n([fixed[2],fixed[5],e]);Hj=n([fixed[3],fixed[5],j])
assert (He*fixed[0])[0]!=0 and(Hj*fixed[0])[0]!=0
He/=abs((He*fixed[0])[0]);Hj/=abs((Hj*fixed[0])[0])
# Strictly positive column rescalings to signed unit evaluations.
e/=abs((Hj*e)[0]);j/=abs((He*j)[0])
assert abs((Hj*e)[0])==1 and abs((He*j)[0])==1
M=S.Matrix.hstack(*fixed,e+u*s,j+v*s)
parent_polys=[S.expand(M[:,J].det())for J in itertools.combinations(range(8),4)]
assert all(S.Poly(b,u,v).total_degree()<=1 for b in parent_polys)
assert all(b.subs({u:0,v:0})!=0 for b in parent_polys)
NP=n([M[:,0],M[:,1],M[:,2]]).col_join(n([M[:,0],M[:,3],M[:,4]])).col_join(n([M[:,1],M[:,3],M[:,5]])).col_join(n([M[:,2],M[:,6],M[:,7]]))
assert S.expand(NP.det())==0
R_e=n([M[:,2],M[:,5],M[:,6]]);R_j=n([M[:,3],M[:,5],M[:,7]])
rhoe=(R_e*fixed[0])[0]/(He*fixed[0])[0];rhoj=(R_j*fixed[0])[0]/(Hj*fixed[0])[0]
assert (R_e-rhoe*He).applyfunc(S.expand)==S.zeros(1,4)
assert (R_j-rhoj*Hj).applyfunc(S.expand)==S.zeros(1,4)
shared=n([M[:,4],M[:,6],M[:,7]]);Lambda=n([fixed[0],fixed[1],fixed[4]])
D=S.expand(Lambda.col_join(He).col_join(Hj).col_join(shared).det())
assert S.Poly(D,u,v).total_degree()==1 and D.subs({u:0,v:0})==0
raw=S.expand(Lambda.col_join(R_e).col_join(R_j).col_join(shared).det())
assert S.expand(raw-rhoe*rhoj*D)==0
# Full parent-sign chamber cuts the exact normalized affine solution line.
sol=S.solve(D,v)[0];polys=[S.expand(S.sign(b.subs({u:0,v:0}))*b.subs(v,sol))for b in parent_polys]
assert all(S.degree(b,u)<=1 and b.subs(u,0)>0 for b in polys)
lo=[];hi=[]
for J,b in zip(itertools.combinations(range(1,9),4),polys):
 slope=b.coeff(u);intercept=b.subs(u,0)
 if slope>0:lo.append((-intercept/slope,J))
 elif slope<0:hi.append((-intercept/slope,J))
lower=max(x[0]for x in lo)if lo else -S.oo;upper=min(x[0]for x in hi)if hi else S.oo
assert lower<0<upper
out={'status':'PASS_EXACT_SOURCE61_JOINT_AFFINE_PERSPECTIVITY_FIBER','scope':'One actual uniform regular fiber; global theorem requires independent deductive proof','source_index':61,'P':[[1,2,3],[1,4,5],[2,4,6],[3,7,8]],'Q':[[1,2,5],[3,6,7],[4,6,8],[5,7,8]],'fixed_parent_columns':[[str(x)for x in z]for z in fixed],'Pi':list(map(str,Pi)),'He':list(map(str,He)),'Hj':list(map(str,Hj)),'S':list(map(str,s)),'moving_e':list(map(str,e+u*s)),'moving_j':list(map(str,j+v*s)),'positive_normalization_values':{'Hj_e':str((Hj*e)[0]),'He_j':str((He*j)[0])},'quotient_Q_equation':str(D),'raw_Q_unit_factors':[str(rhoe),str(rhoj)],'jointly_affine_parent_brackets':70,'Q_line_v':str(sol),'full_parent_residence_interval_u':[str(lower),str(upper)],'lower_endwalls':[J for x,J in lo if x==lower],'upper_endwalls':[J for x,J in hi if x==upper],'all_signed_line_brackets':list(map(str,polys))}
(P/'AFFINE_PERSPECTIVITY_TEST.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:out[k]for k in ['status','quotient_Q_equation','full_parent_residence_interval_u','lower_endwalls','upper_endwalls']},indent=2))
