#!/usr/bin/env python3
"""Independent algebraic-point/conic audit. Reads source data only; no producer imports."""
from pathlib import Path
from itertools import combinations,permutations
from fractions import Fraction
import sympy as S,json,hashlib,time
P=Path(__file__).resolve().parent;B=P.parent
src=B/'inputs/DIAG3_triple_fullspace_critical_h1.json';raw=json.loads(src.read_text());data=json.loads((B/'triple/UNIFORM_BRANCH.json').read_text())
xs=S.symbols('a b c d e f g h i');env=dict(zip(map(str,xs),xs));a,b,c,d,e,f,g,h,i=xs
qs=[S.Add(*(S.Integer(co)*S.Mul(*(x**pw for x,pw in zip(xs,mon)))for co,mon in rec['terms']))for rec in raw['equations'][:3]]
assert [rec['kind']for rec in raw['equations'][:3]]==['factor']*3
root=S.Poly(S.sympify(data['h_polynomial'],locals=env),h,domain=S.QQ)
assert root.degree()==4 and len(S.factor_list(root)[1])==1 and S.factor_list(root)[1][0][0].degree()==4
lo,hi=map(S.Rational,data['h_interval']);assert lo<hi
# Independent exact Sturm sign-variation count, not producer count_roots.
def variation(seq,z):
 vals=[S.sign(S.Poly(p,h).eval(z))for p in seq];vals=[v for v in vals if v];return sum(x!=y for x,y in zip(vals,vals[1:]))
sturm=S.sturm(root.as_expr(),h);assert root.eval(lo)!=0 and root.eval(hi)!=0
assert variation(sturm,lo)-variation(sturm,hi)==1
coords=[S.sympify(z,locals=env)for z in data['coordinates']];subst=dict(zip(xs,coords))
def field_fraction(expr):
 n,z=S.cancel(expr).as_numer_denom();n=S.Poly(n,h,domain=S.QQ);z=S.Poly(z,h,domain=S.QQ)
 assert S.gcd(z,root).degree()==0
 return n,z
def algebraic_zero(expr):
 n,z=field_fraction(expr);return n.rem(root).is_zero
def specialize(expr):return S.cancel(expr.subs(subst,simultaneous=True))
assert all(algebraic_zero(specialize(q))for q in qs)
Y=S.Matrix([[1,0,0,0,1,1,1,1],[0,1,0,0,1,a,d,g],[0,0,1,0,1,b,e,h],[0,0,0,1,1,c,f,i]])
# Determinants by explicit signed permutations, independent of producer's Matrix.det acceptance.
def det(M):
 out=0;n=len(M)
 for perm in permutations(range(n)):
  sg=(-1)**sum(perm[r]>perm[k]for r in range(n)for k in range(r+1,n));out+=sg*S.prod(M[r][perm[r]]for r in range(n))
 return S.expand(out)
bs={J:det([[Y[r,j]for j in J]for r in range(4)])for J in combinations(range(8),4)}
assert len(data['brackets'])==70
for rec,(J,br) in zip(data['brackets'],bs.items()):
 v=specialize(br);nn,dd=field_fraction(v)
 assert S.gcd(nn,root).degree()==0
 stored=S.sympify(rec['numerator'],locals=env)/S.sympify(rec['denominator'],locals=env)
 assert rec['labels']==[j+1 for j in J] and S.cancel(v-stored)==0
J=[[S.diff(q,x)for x in xs]for q in qs]
mabc=det([[r[k]for k in [0,1,2]]for r in J]);mahi=det([[r[k]for k in [0,7,8]]for r in J])
assert algebraic_zero(specialize(mabc)) and not algebraic_zero(specialize(mahi))
macd=det([[r[k]for k in [0,2,3]]for r in J]);assert algebraic_zero(specialize(macd))
# Conic matrix built directly from coefficient monomials.
co=S.Poly(qs[1],a,c);assert co.total_degree()==2 and co.degree(a)==1
CM=S.Matrix([[co.coeff_monomial(a*a),co.coeff_monomial(a*c)/2,co.coeff_monomial(a)/2],[co.coeff_monomial(a*c)/2,co.coeff_monomial(c*c),co.coeff_monomial(c)/2],[co.coeff_monomial(a)/2,co.coeff_monomial(c)/2,co.coeff_monomial(1)]])
conic_det=S.expand(4*det(CM.tolist()))
unit_product=-b*f*(b-e)*(e-f)*(f-1)**2*(h-1)**2*(d*h-d-e*g+e+g-h)
assert S.expand(conic_det-unit_product)==0
unit_ids={b:((1,2,4,6),-1),f:((1,2,3,7),1),b-e:((2,4,6,7),1),e-f:((1,2,5,7),-1),f-1:((2,3,5,7),1),h-1:((2,4,5,8),-1),d*h-d-e*g+e+g-h:((4,5,7,8),-1)}
for u,(labels,sg)in unit_ids.items():assert S.expand(u-sg*bs[tuple(v-1 for v in labels)])==0
assert S.diff(qs[0],d)==i
assert S.expand(S.diff(qs[2],c)+g*(d-e)*(h-1))==0
assert S.Poly(qs[2],a,c).total_degree()==1
graph_units=[]
for u in [i,g,d-e,h-1]:
 hits=[{'bracket':[x+1 for x in inds],'sign':sg}for inds,br in bs.items()for sg in [-1,1]if S.expand(u-sg*br)==0]
 assert hits;graph_units.append({'factor':str(u),'identity':hits[0]})
# Exact specialized quadratic; independently eliminate c on the chosen rational slice.
base={env[k]:S.Rational(v)for k,v in data['base'].items()};sq=[S.expand(q.subs(base))for q in qs]
assert sq[0]==0
sl=S.Poly(sq[2],a,c);ca=sl.coeff_monomial(a);cc=sl.coeff_monomial(c);c0=sl.coeff_monomial(1)
cn=S.cancel(sq[1].subs(c,-(ca*a+c0)/cc)).as_numer_denom()[0];cn=S.Poly(cn,a,domain=S.QQ[h]);assert cn.degree()==2
A,Bb,C=cn.nth(2),cn.nth(1),cn.nth(0)
assert not algebraic_zero(A)
assert algebraic_zero(cn.as_expr().subs(a,coords[0]))
assert algebraic_zero((2*A*a+Bb).subs(a,coords[0]))
disc=S.expand(Bb**2-4*A*C)
assert algebraic_zero(disc) and not algebraic_zero(S.diff(disc,h))
report={'status':'PASS_INDEPENDENT_EXACT_POINT_AND_CONIC','source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'original_factor_ids':[r['factor']for r in raw['equations'][:3]],'canonical_row':raw['canonical_row'],'irreducible_quartic':True,'exact_sturm_root_count':1,'all70_reconstructed_brackets_nonzero':True,'all70_recorded_bracket_functions_match':True,'all3_original_factor_equations_zero':True,'projection_abc_minor_zero':True,'projection_acd_minor_zero':True,'smoothness_ahi_minor_nonzero':True,'height_b_critical':False,'nonzero_quadratic_A':True,'quadratic_double_root':True,'simple_discriminant_h_zero':True,'conic_determinant_parent_unit_identity':True,'all7_conic_unit_identities':True,'q0_d_unit_graph':True,'q2_c_unit_graph':True,'q2_line_in_a_c':True,'graph_unit_identities':graph_units,'scope':'Exact uniform branch point and universal conic identity for one named triple; no compact component or original counterexample; generic1951/4186term reduction audited separately if recorded.'}
(P/'TRIPLE_INDEPENDENT_REPLAY.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
