from pathlib import Path
from itertools import combinations,permutations
import hashlib,json
import sympy as s
ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'checkpoint/triple/UNIQUE_HARD_THREE_BOUNDARY_POINTS.json'
d=json.loads(source.read_text());Y=s.Matrix([[s.Rational(v) for v in row] for row in d['center']['Y']])
P=((1,2,3),(1,4,5),(2,4,6),(3,5,7));Q=((1,2,7),(1,5,8),(2,3,4),(3,5,7));R=((2,3,6),(2,4,8),(4,5,6),(5,7,8))
p=s.Matrix([1,7,7,0]);q=s.Matrix([0,24,5,-4]);r=s.Matrix([9,14,18,54])
assert all(Y[:,list(I)].det()!=0 for I in combinations(range(8),4))
assert s.Matrix.hstack(p,q,r).rank()==3
T=s.Matrix([[-7,1,0,0],[-7,0,1,0],[0,0,0,1],[1,0,0,0]])
assert T*p==s.Matrix([0,0,0,1])
V=T*Y;Z=V[:3,:];zq=(T*q)[:3,0];zr=(T*r)[:3,0]
def normal(V,I):
 A=V[:,[i-1 for i in I]]
 return s.Matrix([[(-1)**i*A[[j for j in range(4) if j!=i],:].det() for i in range(4)]])
for K,x in ((P,p),(Q,q),(R,r)):
 N=s.Matrix.vstack(*(normal(Y,I) for I in K));assert N.rank()==3 and N*x==s.zeros(4,1)
rows=[]
for block,(K,z) in enumerate(((Q,zq),(R,zr))):
 for I in K:
  inds=[i-1 for i in I];M=s.Matrix.hstack(z,*[Z[:,i] for i in inds]);row=[s.Integer(0)]*10
  for c,j in enumerate([8+block]+inds):row[j]=(-1)**(3+c)*M[:,[k for k in range(4) if k!=c]].det()
  rows.append(row)
A=s.Matrix(rows);actual=s.Matrix(list(V[3,:])+[(T*q)[3],(T*r)[3]])
assert A*actual==s.zeros(8,1)
shears=[s.Matrix(list(Z[k,:])+[zq[k],zr[k]]) for k in range(3)]
for sh in shears:assert A*sh==s.zeros(8,1)
assert s.Matrix.hstack(*shears,actual).rank()==4
An=A[:,4:];b=A[:,:4]*actual[:4,0];assert An.rank()==6 and An*actual[4:,0]+b==s.zeros(8,1)
u=s.symbols('u0:4');YY=T.inv()*s.Matrix.vstack(Z,s.Matrix([[1,0,0,0,*u]]))
parent_brackets={''.join(map(str,I)):s.expand(YY[:,[i-1 for i in I]].det()) for I in combinations(range(1,9),4)}
unit_matches={}
for tag,target in [('Q_extra',4*u[0]+u[2]),('R_extra',u[1])]:
 matches=[]
 for label,f in parent_brackets.items():
  rat=s.cancel(f/target)
  if rat and not rat.free_symbols:matches.append({'bracket':label,'scalar':str(rat)})
 assert matches
 unit_matches[tag]=matches
polys=[]
for K in (Q,R):
 M=s.Matrix.vstack(*(normal(YY,I) for I in K));f=s.factor(M.det(method='domain-ge'));polys.append(f)
out={'status':'PASS_POPULATED_RANK6_TRIPLE_HEIGHT_OBSTRUCTION','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'supports':{'P':P,'Q':Q,'R':R},'source_note':'Use top-level points and explicitly listed supports; center.supports is legacy metadata.','contraction_matrix':[[str(x) for x in row] for row in T.tolist()],'parent_quotient':[[str(x) for x in row] for row in Z.tolist()],'projected_Q':list(map(str,zq)),'projected_R':list(map(str,zr)),'unknown_order':['h1','h2','h3','h4','h5','h6','h7','h8','wQ','wR'],'incidence_matrix':[[str(x) for x in row] for row in A.tolist()],'incidence_rank':A.rank(),'gauge_kernel_basis':[[str(x) for x in v] for v in [*shears,actual]],'gauge_fixed_columns':[1,2,3,4],'gauge_fixed_values':list(map(str,actual[:4,0])),'normalized_unknown_order':['h5','h6','h7','h8','wQ','wR'],'normalized_coefficient_rank':An.rank(),'normalized_actual_solution':list(map(str,actual[4:,0])),'fixed_quotient_factor_polynomials':list(map(str,polys)),'extra_parent_unit_matches':unit_matches,'all_parent_brackets_jointly_affine':all(s.Poly(f,*u).total_degree()<=1 for f in parent_brackets.values())}
assert out['all_parent_brackets_jointly_affine']
# Nonzero maximal minor and exact kernel identify the full gauge-only fiber.
pr=list(A.T.rref()[1]);pc=list(A.rref()[1]);out['rank6_minor']={'rows':pr,'columns':pc,'determinant':str(A.extract(pr,pc).det())}
assert A.extract(pr,pc).det()!=0
# A false fifth direction and a perturbed actual height must fail.
perturbed=actual.copy();perturbed[4]+=1;assert A*perturbed!=s.zeros(8,1)
F=s.cancel(polys[0]/(s.Rational(7,9)*(4*u[0]+u[2])))
G=s.cancel(polys[1]/(s.Rational(8,3)*u[1]))
assert s.Poly(F,u[0]).degree()==1 and u[1] not in F.free_symbols
assert s.Poly(G,u[1]).degree()==1
assert F.subs(dict.fromkeys(u,1))==0 and G.subs(dict.fromkeys(u,1))==0
out['triangular_residual_equations']=[str(s.expand(F)),str(s.expand(G))]
(ROOT/'alternative/TRIPLE_RANK6_GATE.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:out[k] for k in ['status','incidence_rank','normalized_coefficient_rank','fixed_quotient_factor_polynomials']},indent=2))
