#!/usr/bin/env python3
from verify_three_boundary_signatures import *
J=json.loads((P/'ACTUAL_UNIQUE_HARD_THREE_BOUNDARY_SIGNATURES.json').read_text());K=json.loads((P/'BOUNDARY_CURVES.json').read_text());Y=matrix(J['center']['Y']);A0=normals(Y)
for s,c in zip(J['signatures'],K['curves']):
 assert s['index']==c['index'];eps=F(s['epsilon']);H=matrix(s['feasible_parent']);V=[[(H[r][k]-Y[r][k])/eps for k in range(8)]for r in range(4)];assert all(V[r][k]==0 for r in [0,2,3]for k in range(8))
 AA=normals([[Y[r][k]+V[r][k]for k in range(8)]for r in range(4)]);DA=[[x-y for x,y in zip(row,base)]for row,base in zip(AA,A0)]
 C=matrix(c['point_coefficients_ascending']);assert len(C)==4 and all(len(row)==4 for row in C)
 def p(t):return [sum(q*t**k for k,q in enumerate(row))for row in C]
 # Every derived normal is affine because only one matrix row varies.
 # Both identities have degree <=4, so five evaluations are exact proofs.
 for t in map(F,range(5)):
  AT=[[x+t*y for x,y in zip(base,change)]for base,change in zip(A0,DA)];N=[AT[k]for k in s['support_indices']];assert det(N)==t
  assert all(dot(N[j],p(t))==t*w*s['signs'][k]for j,(w,k)in enumerate(zip([1,2,3,5],s['support_indices'])))
 weak=list(map(F,s['weak_primal']));lam=next(x/y for x,y in zip(p(F(0)),weak)if y);assert lam>0 and p(F(0))==[lam*x for x in weak]
 assert p(eps)==list(map(F,s['feasible_point']))
 for k in range(56):
  co=[F(0)]*5
  for r in range(4):
   for d in range(4):co[d]+=s['signs'][k]*A0[k][r]*C[r][d];co[d+1]+=s['signs'][k]*DA[k][r]*C[r][d]
  assert next(x for x in co if x)>0
 # Each signed polynomial is positive for all sufficiently small t>0;
 # finitely many inequalities admit one common such interval.
out={'status':'PASS','actual_boundary_points':3,'curve_coordinates_degree_at_most':3,'exact_polynomial_identity_checks':30,'signed_polynomials_with_positive_leading_coefficient':168,'conclusion':'Each signature is feasible arbitrarily close to the center inside the same connected parent component.'};(P/'BOUNDARY_CURVES_REPLAY.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,sort_keys=True))
