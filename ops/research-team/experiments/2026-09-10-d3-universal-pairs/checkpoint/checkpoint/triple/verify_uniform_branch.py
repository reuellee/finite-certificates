"""Exact replay; no discovery module imported. Requires SymPy."""
import hashlib,itertools,json,sympy as s
from pathlib import Path
P=Path(__file__).resolve().parent
SOURCE=P.parent/'inputs/DIAG3_triple_fullspace_critical_h1.json'
def verify(certificate):
 x=s.symbols('a:i');a,b,c,d,e,f,g,h,i=x
 source=json.loads(SOURCE.read_text()); qs=[s.Poly.from_dict({tuple(m):v for v,m in row['terms']},x).as_expr() for row in source['equations'][:3]]
 env=dict(zip(map(str,x),x)); p=s.Poly(s.sympify(certificate['h_polynomial'],locals=env),h,domain=s.QQ)
 assert p.degree()==4 and p.is_irreducible
 lo,hi=map(s.Rational,certificate['h_interval']);assert lo<hi and p.count_roots(lo,hi)==1
 coords=[s.sympify(z,locals=env) for z in certificate['coordinates']];assert len(coords)==9
 def rem(expr):
  nn,dd=s.cancel(expr).as_numer_denom(); nn=s.Poly(nn,h,domain=s.QQ);dd=s.Poly(dd,h,domain=s.QQ)
  assert s.gcd(p,dd).degree()==0
  return (nn*s.invert(dd,p)).rem(p).as_expr()
 def at(expr):return rem(expr.subs(dict(zip(x,coords)),simultaneous=True))
 assert all(at(q)==0 for q in qs)
 # Global named coordinate graph slopes, identities not sampled values.
 assert s.expand(s.diff(qs[0],b)-(f-i))==0
 assert s.expand(s.diff(qs[2],c)+g*(d-e)*(h-1))==0
 mat=s.Matrix([[1,0,0,0,1,1,1,1],[0,1,0,0,1,a,d,g],[0,0,1,0,1,b,e,h],[0,0,0,1,1,c,f,i]])
 bracket_remainders=[]
 for inds in itertools.combinations(range(8),4):
  rr=at(mat[:,inds].det()); assert rr!=0
  bracket_remainders.append(rr)
 jac=s.Matrix(qs).jacobian(x)
 assert at(jac[:,[0,1,2]].det())==0 # projection to d,e,f,g,h,i is branched.
 minor_a_hi=at(jac[:,[0,7,8]].det()); assert minor_a_hi!=0 # smooth, and b is not critical.
 # Rebuild one-variable-family quadratic after the two exact graph eliminations.
 base={d:-5,e:-4,f:-3,g:-1,i:4,b:s.Rational(-23,7)}
 subq=[s.expand(q.subs(base)) for q in qs]
 cgraph=s.cancel(-subq[2].subs(c,0)/s.diff(subq[2],c))
 numerator=s.cancel(subq[1].subs(c,cgraph)).as_numer_denom()[0]
 pa=s.Poly(numerator,a); assert pa.degree()==2
 assert rem(pa.nth(2))!=0
 assert rem(numerator.subs(a,coords[0]))==0 and rem(s.diff(numerator,a).subs(a,coords[0]))==0
 discr=s.factor(pa.nth(1)**2-4*pa.nth(2)*pa.nth(0))
 assert rem(discr)==0 and rem(s.diff(discr,h))!=0
 return {'status':'PASS','source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'original_factor_ids':[z['factor']for z in source['equations'][:3]],'canonical_row':source['canonical_row'],'exact_real_roots_in_interval':1,'uniform_parent_brackets':70,'projection_abc_minor_zero':True,'full_rank_minor_columns':['a','h','i'],'height_b_critical':False,'double_root_nonzero_quadratic_coefficient':True,'simple_discriminant_h_root':True,'scope':'One exact uniform fold, not a compact component or a universal escape proof.'}
if __name__=='__main__':
 cert=json.loads((P/'UNIFORM_BRANCH.json').read_text()); result=verify(cert)
 # Check that corrupted root and coordinate data cannot be accepted.
 import copy
 mutations=[]
 for kind in ['polynomial','coordinate','interval']:
  bad=copy.deepcopy(cert)
  if kind=='polynomial':bad['h_polynomial']='h**4+1'
  if kind=='coordinate':bad['coordinates'][0]='0'
  if kind=='interval':bad['h_interval']=['-10','-9']
  try: verify(bad)
  except (AssertionError,s.PolynomialError,ValueError,ZeroDivisionError):mutations.append(kind)
  else:raise AssertionError('corruption accepted: '+kind)
 result['rejected_corruptions']=mutations
 (P/'EXACT_BRANCH_REPLAY.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
