"""Exact kind48 axis and higher-order height-motion canary."""
from pathlib import Path
from itertools import combinations
import hashlib,json
import sympy as s
ROOT=Path(__file__).resolve().parents[1]
Y=s.Matrix([[1,0,0,0,1,1,1,1],[0,1,0,0,1,-1,4,7],[0,0,1,0,1,2,-5,-4],[0,0,0,1,1,3,2,5]])
K=('123','145','246','356');L=('124','135','236','456')
def normal(V,I):
 A=V[:,[int(j)-1 for j in I]]
 return s.Matrix([[(-1)**(3+j)*A[[k for k in range(4) if k!=j],:].det() for j in range(4)]])
def normals(V,K):return s.Matrix.vstack(*(normal(V,I) for I in K))
def det(V,K):return normals(V,K).det(method='domain-ge')
N=normals(Y,K);M=normals(Y,L);qa=N.nullspace()[0];qb=M.nullspace()[0];lam=N.T.nullspace()[0]
assert N.rank()==M.rank()==3 and s.Matrix.hstack(qa,qb).rank()==2
B=s.zeros(8,4)
for coeff,I in zip(lam,K):
 J=[int(v)-1 for v in I]
 for a,j in enumerate(J):
  for k in range(4):
   cols=[Y[:,v] for v in J];cols[a]=s.eye(4)[:,k];B[j,k]+=coeff*s.Matrix.hstack(*cols,qa).det()
assert B.rank()==2 and B*qa==B*qb==s.zeros(8,1)
p=qa+qb;assert B*p==s.zeros(8,1) and all(s.Matrix.hstack(p,q).rank()==2 for q in (qa,qb))
u,v=s.symbols('u v');YY=Y.copy();YY[:,4]=Y[:,4]+u*p;YY[:,5]=Y[:,5]+v*p
F=s.expand(det(YY,K));expected=-(17*u*u*v+6*u*u-7*u*v*v+12*u*v-6*v*v)/6
assert s.expand(F-expected)==0 and F.subs(v,0)==-u*u
assert s.diff(F,u).subs({u:0,v:0})==s.diff(F,v).subs({u:0,v:0})==0
assert s.diff(F,u,2).subs({u:0,v:0})==-2
# Every bracket is affine in u on v=0, so endpoint signs prove uniformity
# throughout the stated closed interval, not merely at finitely many points.
interval=s.Rational(1,100);brackets={}
for I in combinations(range(1,9),4):
 f=s.expand(YY[:,[j-1 for j in I]].det()).subs(v,0)
 assert s.Poly(f,u).degree()<=1
 f0=f.subs(u,0);assert f0 and all(f.subs(u,t)*f0>0 for t in (-interval,interval))
 brackets[''.join(map(str,I))]=str(f)
# Exact ordinary-occurrence identity in a generic normalized parent frame.
a,b,c,d,e,f,g,h,i=s.symbols('a b c d e f g h i')
V=s.Matrix([[1,0,0,0,1,1,1,1],[0,1,0,0,1,a,d,g],[0,0,1,0,1,b,e,h],[0,0,0,1,1,c,f,i]])
assert s.expand(det(V,K)+det(V,L))==0
assert s.expand(det(V,K)-(a+b*c-b-c))==0
# Hostile changes must fail the exact higher-order claim.
assert s.expand(F-(-u*u))!=0 and s.diff(F,u,2).subs({u:0,v:0})!=0
out={'status':'PASS_KIND48_CHARACTERISTIC_AXIS_IS_NOT_FULL_HEIGHT_FLAT','scope':'One exact axis-direction test; global kernel characterization is separately proved in CHARACTERISTIC_KERNELS.md. The direction need not be another factor concurrence.','parent_matrix':[[str(x) for x in row] for row in Y.tolist()],'ordinary_occurrences':[K,L],'ordinary_concurrences':[list(map(str,q)) for q in (qa,qb)],'full_gradient_map_rank':2,'full_gradient_map':[[str(x) for x in row] for row in B.tolist()],'chosen_axis_direction':list(map(str,p)),'shifted_parent_labels':[5,6],'exact_restriction':str(F),'v0_restriction':str(F.subs(v,0)),'second_u_derivative_at_origin':'-2','full_uniform_interval_v0':['-1/100','1/100'],'parent_brackets_on_v0':brackets,'ordinary_polynomial_identity':'det(123,145,246,356)=-det(124,135,236,456)=a+bc-b-c','script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
(ROOT/'noncollinear/KIND48_AXIS_CANARY.json').write_text(json.dumps(out,indent=2)+'\n')
print(out['status']);print('restriction:',F);print('uniform for v=0, |u|<=1/100; wall restriction=-u^2')
