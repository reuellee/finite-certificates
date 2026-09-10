#!/usr/bin/env python3
"""Construct exact original proper antichain lifting the previous transverse model."""
from pathlib import Path
import itertools, json, hashlib
import sympy as S
P=Path(__file__).resolve().parent
C=P.parent/'checkpoint'
c=json.loads((C/'previous_checkpoint/falsifier/certificate.json').read_text())
Q=S.Rational;t=S.symbols('t');Y=S.Matrix(c['parent']).applyfunc(Q)
triples=sorted(itertools.combinations(range(8),3),key=lambda x:x[::-1]);bases=list(itertools.combinations(range(8),4))
Z=c['center_zero_support'];sigint=c['signature_integer'];sg=[1 if sigint>>i&1 else -1 for i in range(56)]
rel=[[-1,-1,-1,-1,-1],[-1,-1,-1,-1,1],[1,1,1,1,-1]]
sigs=[]
for s in rel:
 r=sg.copy()
 for i,si in zip(Z,s):r[i]*=si
 sigs.append(r)
def normals(M):
 return S.Matrix([[S.expand((-1)**(r+3)*M[[k for k in range(4) if k!=r],list(tr)].det())for r in range(4)]for tr in triples])
A=S.diag(*sg)*normals(Y);K=S.Matrix([[8,Q(19,2)],[Q(32,25),Q(19,25)],[Q(2,5),Q(19,40)],[1,0],[0,1]])
assert A[Z,:3].T*K==S.zeros(3,2)
# A rank-five derivative permits every prescribed infinitesimal active offset.
cols=[];slots=list(itertools.product(range(3),range(8)))
for r,col in slots:
 J=S.zeros(4,8);J[r,col]=1
 # Determinants are affine in one varying matrix entry, so this is exact derivative.
 D=S.diag(*sg)*(normals(Y+J)-normals(Y))
 cols.append(S.Matrix([D[i,3]for i in Z]))
L=S.Matrix.hstack(*cols);assert L.rank()==5
pivots=L.rref()[1];assert len(pivots)==5
Hs=[S.Matrix([-1,-1,-1,-Q(8,25),-Q(1853,200)]),S.Matrix([-1,-1,-1,-Q(8,25),Q(4147,200)]),S.Matrix([1,1,1,Q(8,25),-Q(4147,200)])]
Us=[S.Matrix([-10,-20]),S.Matrix([-10,10]),S.Matrix([10,-10])]
Hs.append(-Hs[0]);Us.append(-Us[0])
eps=Q(1,10**8)
def certpositive(poly):
 p=S.Poly(S.expand(poly),t);k=min(m[0] for m,c0 in p.terms()if c0)
 co=p.nth(k)
 assert co>0,(poly,k,co)
 tail=sum(abs(p.nth(i))*eps**(i-k) for i in range(k+1,p.degree()+1))
 assert tail<co,(poly,tail,co)
 return {'vanishing_order':k,'leading_coefficient':str(co),'tail_bound':str(tail)}
def ser(x):
 if isinstance(x,S.MatrixBase):return [[str(v) for v in row]for row in x.tolist()]
 if isinstance(x,S.Basic):return str(x)
 if isinstance(x,dict):return {str(k):ser(v)for k,v in x.items()}
 if isinstance(x,(list,tuple)):return [ser(v)for v in x]
 return x
records=[]
outer=next(i for i in range(56)if i not in Z and A[i,3]>0)
for own,(h,u)in enumerate(zip(Hs,Us)):
 assert K.T*h==u
 vals=L[:,pivots].inv()*h;J=S.zeros(4,8)
 for n,v in zip(pivots,vals):J[slots[n][0],slots[n][1]]=v
 YY=Y+t*J;NN=normals(YY)
 bcert=[certpositive(S.sign(Y[:,list(b)].det())*YY[:,list(b)].det())for b in bases]
 good=[certpositive(sigs[own][i]*NN[i,3])for i in range(56)]if own<3 else []
 bad=[]
 for other in range(3):
  if other==own:continue
  sj=rel[other]
  # Strict relative-sign kernel and strictly negative offset evaluation.
  qs=[S.Matrix(q)for q in itertools.product(range(-12,13),repeat=2)if any(q)]
  q=next(q for q in sorted(qs,key=lambda q:sum(abs(v)for v in q))if all(s*x>0 for s,x in zip(sj,K*q))and(q.T*u)[0]<0)
  lam=S.diag(*sj)*K*q
  F=S.diag(*(sigs[other][i]for i in Z+[outer]))*NN[Z+[outer],:]
  F0=F.subs(t,0)
  # Fix two positive active weights; solve the remaining three and outer weight.
  chosen=next(tuple(cs)+(5,)for cs in itertools.combinations(range(5),3)if F0[list(cs)+( [5] ),:].det()!=0)
  fixed=[i for i in range(5)if i not in chosen]
  E=F[list(chosen),:].T;rhs=-sum((F[i,:].T*lam[i]for i in fixed),S.zeros(4,1))
  det=S.expand(E.det());epssign=S.sign(det.subs(t,0));den=epssign*det
  raw=epssign*E.adjugate()*rhs
  w=[None]*6
  for i,v in zip(chosen,raw):w[i]=S.expand(v)
  for i in fixed:w[i]=S.expand(den*lam[i])
  weights=S.Matrix(w)
  assert (F.T*weights).applyfunc(S.expand)==S.zeros(4,1)
  wcert=[certpositive(v)for v in weights]
  assert all(v.subs(t,eps)>0 for v in weights)
  bad.append({'other_signature':other,'q':q,'center_kernel':lam,'offset_evaluation':(q.T*u)[0],'normal_indices':Z+[outer],'weight_polynomials':weights,'positivity':wcert,'rank_four_minor_rows':chosen,'rank_four_minor_signed':den,'rank_four_minor_positivity':certpositive(den)})
 rec={'chart_kind':'one_hot_good' if own<3 else 'strictly_all_bad_no_weak_ray','own_signature':own if own<3 else None,'offset':h,'transverse_coordinate':u,'direction':J,'parent_sign_certificates':bcert,'good_margin_certificates':good,'bad':bad}
 records.append(rec)
 print('certified chart',own,flush=True)
out={'status':'EXACT_ACTUAL_PROPER_THREE_SIGNATURE_ANTICHAIN','scope':'Original admissibility proved; transverse Hc1 does not become original global Hc1','base_parent':Y,'parent_same_component_interval':'0<=t<=1/100000000','signatures':[sum(1<<i for i,s in enumerate(row)if s>0)for row in sigs],'relative_signs':rel,'active_indices':Z,'derivative_pivots':[slots[i]for i in pivots],'derivative_rank':5,'outer_index':outer,'records':records,'source_sha256':hashlib.sha256((C/'previous_checkpoint/falsifier/certificate.json').read_bytes()).hexdigest(),'original_obligations_closed':0}
tmp=P/'ACTUAL_ANTICHAIN.tmp';tmp.write_text(json.dumps(ser(out),indent=2)+'\n');tmp.replace(P/'ACTUAL_ANTICHAIN.json')
print('PASS',out['signatures'])
