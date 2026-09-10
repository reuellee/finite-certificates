import sympy as s,json,itertools
from pathlib import Path
P=Path(__file__).resolve().parent;J=json.loads((P/'ACTUAL_UNIQUE_HARD_THREE_BOUNDARY_SIGNATURES.json').read_text());Y=s.Matrix([[s.Rational(x)for x in r]for r in J['center']['Y']]);T=list(itertools.combinations(range(8),3));t=s.symbols('t');curves=[]
def normal(A,I):
 Q=A[:,I];return s.Matrix([(-1)**(r+3)*Q.extract([j for j in range(4)if j!=r],range(3)).det()for r in range(4)]).T
for z in J['signatures']:
 H=s.Matrix([[s.Rational(x)for x in r]for r in z['feasible_parent']]);eps=s.Rational(z['epsilon']);V=Y+t*(H-Y)/eps;A=s.Matrix.vstack(*(normal(V,I)for I in T));N=A[z['support_indices'],:];rhs=t*s.diag(1,2,3,5)*s.Matrix([z['signs'][k]for k in z['support_indices']]);assert s.expand(N.det())==t
 p=[s.cancel(x)for x in N.inv()*rhs];assert all(s.Poly(x,t).degree()<=3 for x in p);cc=[[str(s.expand(x).coeff(t,k))for k in range(4)]for x in p]
 values=[s.Poly(s.expand(z['signs'][k]*(A*s.Matrix(p))[k]),t)for k in range(56)]
 assert all(next(q.nth(k)for k in range(q.degree()+1)if q.nth(k))>0 for q in values)
 curves.append({'index':z['index'],'point_coefficients_ascending':cc,'signed_value_degrees':[q.degree()for q in values]})
(P/'BOUNDARY_CURVES.json').write_text(json.dumps({'schema':'actual_small_parameter_boundary_curves_v1','parameter':'t','curves':curves},indent=2)+'\n')
