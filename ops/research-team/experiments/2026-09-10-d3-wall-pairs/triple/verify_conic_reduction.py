"""Reconstruct the exact conic and discriminant identities from pinned q terms."""
import hashlib,itertools,json,sympy as s
from pathlib import Path
P=Path(__file__).resolve().parent;src=P.parent/'inputs/DIAG3_triple_fullspace_critical_h1.json'
x=s.symbols('a:i');a,b,c,d,e,f,g,h,i=x; qs=json.loads(src.read_text());q=[s.Poly.from_dict({tuple(m):v for v,m in o['terms']},x).as_expr()for o in qs['equations'][:3]]
mat=s.Matrix([[1,0,0,0,1,1,1,1],[0,1,0,0,1,a,d,g],[0,0,1,0,1,b,e,h],[0,0,0,1,1,c,f,i]])
brs=[([v+1 for v in J],s.expand(mat[:,J].det()))for J in itertools.combinations(range(8),4)]
pc=s.Poly(q[1],a,c);L=pc.coeff_monomial(a*c);M=pc.coeff_monomial(a);N=pc.coeff_monomial(c*c);O=pc.coeff_monomial(c);C=pc.coeff_monomial(1)
assert pc.degree(a)==1 and pc.total_degree()==2
fourdet=s.expand(-L*L*C+L*M*O-M*M*N)
units=[b,f,b-e,e-f,f-1,h-1,d*h-d-e*g+e+g-h]
expected=-b*f*(b-e)*(e-f)*(f-1)**2*(h-1)**2*(d*h-d-e*g+e+g-h)
assert s.expand(fourdet-expected)==0
unit_ids=[]
for u in units:
 hits=[{'bracket':J,'sign':sg}for J,v in brs for sg in [1,-1]if s.expand(u-sg*v)==0]
 assert hits;unit_ids.append({'factor':str(u),'identity':hits[0]})
assert s.expand(s.diff(q[2],c)+g*(d-e)*(h-1))==0
assert s.diff(q[0],d)==i
# Exact graph comparison, with both graph denominators parent units.
ds=(b*(i-f)+f*g)/i
r2=s.cancel(q[1].subs(d,ds)).as_numer_denom()[0]
r3=s.cancel(q[2].subs(d,ds)).as_numer_denom()[0]
C0=r3.subs(c,0);C1=s.diff(r3,c);cp=s.Poly(r2,c)
vs=(a,b,e,f,g,h,i)
NF=s.Poly(cp.nth(0),*vs)*s.Poly(C1,*vs)**2-s.Poly(cp.nth(1),*vs)*s.Poly(C0,*vs)*s.Poly(C1,*vs)+s.Poly(cp.nth(2),*vs)*s.Poly(C0,*vs)**2
_,NF=NF.primitive()
cert=json.loads((P/'HEIGHT_DISCRIMINANT_SYSTEM.json').read_text())
stored=s.Poly.from_dict({tuple(m):v for v,m in cert['quadratic']},vs)
assert NF==stored
pa=s.Poly(NF.as_expr(),a);A,B,C=[pa.nth(k)for k in [2,1,0]]
ys=(b,e,f,g,h,i);R=s.Poly.from_dict({tuple(m):v for v,m in cert['discriminant_primitive']},ys)
D=s.Poly(B,*ys)**2-4*s.Poly(A,*ys)*s.Poly(C,*ys)
unit=g*(h-1)*(b*(i-f)+f*g-e*i)
assert D==s.Poly(unit,*ys)**2*R
# Algebraic double-root and derivative identities (formal coefficient ring).
AA,BB,CC,Av,Bv,Cv,zz=s.symbols('AA BB CC Av Bv Cv zz')
assert s.expand(4*AA*(AA*zz**2+BB*zz+CC)-((2*AA*zz+BB)**2-(BB**2-4*AA*CC)))==0
assert s.cancel((2*BB*Bv-4*Av*CC-4*AA*Cv+4*AA*(Av*zz**2+Bv*zz+Cv)).subs({CC:BB**2/(4*AA),zz:-BB/(2*AA)},simultaneous=True))==0
out={'status':'PASS','source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'conic_degree':2,'conic_determinant_unit_factors':unit_ids,'quadratic_terms':len(NF.terms()),'quadratic_total_degree':NF.total_degree(),'discriminant_terms':len(R.terms()),'discriminant_total_degree':R.total_degree(),'critical_variables':list(map(str,ys)),'critical_height':'b','critical_equations':['R','dR/de','dR/df','dR/dg','dR/dh','dR/di'],'critical_term_counts':[len(R.terms())]+[len(R.diff(v).terms())for v in ys[1:]],'identities_verified':['4det(conic)=parent_unit_product','unit d graph','unit c graph','quadratic pullback','discriminant=unit²R','double-root identity','critical derivative identity'],'scope':'Exact all-parent presentation and compactness reduction for canonical triple (5563,4373,23221); its critical system remains undecided.'}
(P/'CONIC_REDUCTION_REPLAY.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
