import sympy as s,itertools,json
from pathlib import Path
root=Path('d3_direct_proof_20260910/triple')
J=json.loads((root/'THREE_BOUNDARY_POINTS.json').read_text()); Y=s.Matrix([[s.Rational(x) for x in r] for r in J['Y']]); triples=list(itertools.combinations(range(8),3)); bases=list(itertools.combinations(range(8),4))
def normal(A,I):
 Q=A[:,I];return s.Matrix([(-1)**(r+3)*Q.extract([j for j in range(4) if j!=r],range(3)).det() for r in range(4)]).T
A=s.Matrix.vstack(*(normal(Y,I) for I in triples));si=[[triples.index(tuple(int(k)-1 for k in t)) for t in S.split('/')] for S in J['supports']]
b,c,e,f,h,i=[Y[r,j] for r,j in [(2,5),(3,5),(2,6),(3,6),(2,7),(3,7)]]
u,v,w=s.symbols('u v w');d=f+b-b*f+v;a=(u+b*d-b-c*d+c+e-f)/(e-f);g=(w-a*b*f+a*c*e-a*c*h+a*f*h+b*b*f-b*c*e-b*f*h+c*e*h)/(c*(e-b));YY=Y.copy();YY[1,5]=a;YY[1,6]=d;YY[1,7]=g
out={'schema':'actual_three_distinct_weak_primal_points_v1','center':J,'parameterized_matrix':[[str(t) for t in r] for r in YY.tolist()],'parameter_coordinates':['u','v','w'],'signatures':[]}
for j in range(3):
 N=A[si[j],:];lam=N.T.nullspace()[0];sig=s.Matrix([s.sign(x) for x in lam]); pp=s.Matrix([s.Rational(x) for x in J['points'][j]])
 zeros=[k for k in range(56) if (A*pp)[k]==0]; print('block',j,'support',si[j],'zero',zeros,'rel',list(lam),flush=True)
 for exp in range(2,13):
  eps=s.Rational(1,10**exp); vals={z:eps if k==j else 0 for k,z in enumerate([u,v,w])}; Yj=YY.subs(vals);Aj=s.Matrix.vstack(*(normal(Yj,I) for I in triples)); p=Aj[si[j],:].inv()*(eps*s.diag(1,2,3,5)*sig); values=Aj*p
  if not all(x!=0 for x in values):continue
  parent=[Yj[:,B].det() for B in bases];center=[Y[:,B].det() for B in bases]
  if not all(x*y>0 for x,y in zip(parent,center)):continue
  sigma=[int(s.sign(x)) for x in values];center_values=A*pp
  orient=next(sigma[k]*s.sign(center_values[k]) for k in range(56) if center_values[k])
  if not all(sigma[k]*orient*center_values[k]>=0 for k in range(56)):continue
  print('FOUND',j,'eps',eps,'sig',sum((x==1)<<k for k,x in enumerate(sigma)),'point',list(p),'weak_orient',orient,flush=True)
  assert all(sigma[k]==sig[z] for z,k in enumerate(si[j]))
  out['signatures'].append({'index':j,'bits':sum((x==1)<<k for k,x in enumerate(sigma)),'signs':sigma,'support_indices':si[j],'support_relation':[str(x) for x in lam],'positive_weights':[str(abs(x)) for x in lam],'weak_primal':[str(orient*x) for x in pp],'all_zero_indices':zeros,'epsilon':str(eps),'feasible_parent':[[str(x) for x in r] for r in Yj.tolist()],'feasible_point':[str(x) for x in p]})
  break
 else:raise RuntimeError(j)
for j in range(3):
 Yj=s.Matrix([[s.Rational(x) for x in r] for r in out['signatures'][j]['feasible_parent']]);Aj=s.Matrix.vstack(*(normal(Yj,I) for I in triples))
 for k in range(3):
  if j==k:continue
  sg=out['signatures'][k];M=Aj[sg['support_indices'],:];ker=M.T.nullspace()[0];signs=[sg['signs'][z] for z in sg['support_indices']];z=[signs[t]*ker[t] for t in range(4)];assert all(t>0 for t in z) or all(t<0 for t in z)
out['triple_order']='lexicographic combinations of labels 0..7'
out['bit_sign_convention']='1 is positive; 0 is negative'
out['center']={k:out['center'][k]for k in ['Y','parent_brackets']}
colex=sorted(triples,key=lambda x:tuple(reversed(x)))
for z in out['signatures']:
 z['signature_bits_lex']=z.pop('bits');z['signature_bits_colex']=sum((z['signs'][triples.index(t)]==1)<<k for k,t in enumerate(colex))
(root/'ACTUAL_THREE_BOUNDARY_SIGNATURES.json').write_text(json.dumps(out,indent=2)+'\n')
