from pathlib import Path
from itertools import combinations
import hashlib,json
import sympy as s
ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'falsifier/NONZERO_NONCOLLINEAR_REPLAY.json'
dat=json.loads(source.read_text());P,Q,R=[dat['supports_1based'][j] for j in ('P','Q','R')]
def normal(Y,I):
 A=Y[:,[int(j)-1 for j in I]]
 return s.Matrix([[(-1)**(3+j)*A[[m for m in range(4) if m!=j],:].det() for j in range(4)]])
def det(Y,K):return s.expand(s.Matrix.vstack(*(normal(Y,I) for I in K)).det(method='domain-ge'))
def br(Y,I):return s.expand(Y[:,[int(j)-1 for j in I]].det())
a,b,c,d,e,f,g,h,i=s.symbols('a b c d e f g h i')
Y=s.Matrix([[1,0,0,0,1,1,1,1],[0,1,0,0,1,a,d,g],[0,0,1,0,1,b,e,h],[0,0,0,1,1,c,f,i]])
FP,FQ,FR=[det(Y,K) for K in (P,Q,R)]
D=b*d-b*f*(b-1)-a*h;E=b*g-b*i*(b-1)-a*h
assert s.expand(FQ-f*E+i*D)==0
assert s.expand(b*(FR-FQ)-c*h*(D-E)-b*h*(f-i)*FP)==0
for F,I,sgn in [(b,'1246',-1),(c,'1236',1),(h,'1248',-1),(f-i,'2378',-1)]:assert F==sgn*br(Y,I)
A=b+c-b*c;sub={a:A,d:f*(b-1)+A*h/b,g:i*(b-1)+A*h/b}
assert all(s.cancel(F.subs(sub,simultaneous=True))==0 for F in (FP,FQ,FR))
u,v,w,t,x,y,z,k=s.symbols('u v w t x y z k')
V=s.Matrix([[1,0,0,0,u,v,w,t],[0,1,0,0,2*u-1,2*v-3,2*w+x,2*t+z],[0,0,1,0,2*u-1,2*v,2*w+y,2*t+k],[0,0,0,1,1,3,2,5]])
assert det(V,P)==0
F=det(V,Q);G=det(V,R);H=t*(x-2)-w*(z-5)
assert s.expand(G-(2*u-1)*F-3*(k+2*t)*(2*u-1)*H)==0
C=3*(2*t-5*w)*(k+2*t)
assert s.expand(F-v*s.diff(F,v)-C)==0
for f0,I,sgn in [(2*u-1,'1245',-1),(k+2*t,'1248',-1),(v,'2346',-1),(2*t-5*w,'2378',-1)]:assert s.expand(f0-sgn*br(V,I))==0
coeff=s.Poly(G-(2*u-1)*F,u,v,w,t).coeffs()
assert all(s.expand(q.subs({x:2,z:5}))==0 for q in coeff)
assert s.groebner(coeff,x,z,k).polys==s.groebner([x-2,z-5],x,z,k).polys
point={u:1,v:1,w:1,t:1,x:2,y:-7,z:5,k:-6}
actual=s.Matrix([[s.Rational(q) for q in row] for row in dat['parent']]);assert V.subs(point)==actual
assert all(br(actual,I)!=0 for I in combinations('12345678',4))
assert s.Matrix([[s.diff(q,j).subs(point) for j in (u,v,w,t)] for q in (F,G)]).rank()==1
assert s.expand(F.subs({x:2,y:-7,z:5,k:-6})-6*(2*t-5*w)*(t+2*v-3))==0
# Hostile coefficient change does not satisfy the graph or redundancy identities.
assert s.expand(FQ-f*E+i*(D+1))!=0
assert s.expand((G+u)-(2*u-1)*F).subs({x:2,z:5})!=0
out={'status':'PASS_GLOBAL_SHARED_PLANE_TRIPLE_ESCAPE_AND_CRITICAL_CLASSIFICATION','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'ordinary_supports':{'P':P,'Q':Q,'R':R},'global_raw_polynomials':list(map(str,(FP,FQ,FR))),'graph_equations':{'a':str(A),'d':str(sub[d]),'g':str(sub[g])},'graph_free_variables':['b','c','e','f','h','i'],'complete_contraction_Q':str(F),'complete_contraction_R':str(G),'redundancy_base_equations':['x-2','z-5'],'reduced_second_equation':str(H),'Q_constant_in_v':str(s.expand(C)),'critical_base_exact':'x=2 and z=5','original_obligations_closed':0,'new_net_triple_orbit_count':0,'novelty_note':'This source triple already fits inherited sequential-affine and light-label mechanisms. The contribution is its explicit global escape and entire critical-piece classification.','script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
(ROOT/'noncollinear/escape_GLOBAL_REPLAY.json').write_text(json.dumps(out,indent=2)+'\n')
print(out['status'])
