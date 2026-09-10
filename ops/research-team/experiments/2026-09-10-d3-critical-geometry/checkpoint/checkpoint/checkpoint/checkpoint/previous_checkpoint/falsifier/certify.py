#!/usr/bin/env python3
"""Exact literal-matrix certificate production/replay for a canonical-selection counterexample."""
import json,itertools,hashlib
from pathlib import Path
import sympy as S
P=Path(__file__).resolve().parent;t=S.Symbol('t');Q=S.Rational
triples=sorted(itertools.combinations(range(8),3),key=lambda x:x[::-1]);bases=sorted(itertools.combinations(range(8),4),key=lambda x:x[::-1])
def normal(Y):return S.Matrix([[S.expand((-1)**(r+3)*Y[[k for k in range(4)if k!=r],list(tr)].det())for r in range(4)]for tr in triples])
def signcert(poly,eps):
 p=S.Poly(S.expand(poly),t);c=p.nth(0)
 return bool(c>0 and sum(abs(p.nth(i))*eps**i for i in range(1,p.degree()+1))<c)
def serial(x):
 if isinstance(x,S.MatrixBase):return [[str(v)for v in r]for r in x.tolist()]
 if isinstance(x,(list,tuple)):return [serial(a)for a in x]
 if isinstance(x,dict):return {k:serial(v)for k,v in x.items()}
 return str(x)if isinstance(x,S.Basic)else x

def main():
 c=json.loads((P/'candidate.json').read_text());Y=S.Matrix(c['parent']).applyfunc(Q);H=S.Matrix(c['direction']).applyfunc(Q);sg=c['signs'];Z=c['zero_indices'];eps=Q(1,1000000)
 N=normal(Y);A=S.diag(*sg)*N;E=A[Z,:].T
 assert [i for i in range(56)if A[i,3]==0]==Z
 assert all(A[i,3]>0 for i in range(56)if i not in Z)
 assert E.rank()==3
 rays=E.nullspace();assert len(rays)==2 and all(x>=0 for ray in rays for x in ray)
 r0=rays[0]/sum(rays[0]);r1=rays[1]/sum(rays[1]);q=S.Matrix(c['minimum_weights']);assert q==r0
 assert (q.T*(r1-r0))[0]>0
 assert all(Y[:,list(b)].det()!=0 for b in bases)
 def family(K):
  YY=Y+t*K;AA=S.diag(*sg)*normal(YY)
  assert all(signcert(s*S.expand(YY[:,list(b)].det()),eps)for s,b in zip(c['parent_signs'],bases))
  assert all(signcert(AA[i,3],eps)for i in range(56)if i not in Z)
  return YY,AA
 YY,AA=family(H);F=AA[Z,:];raw=S.Matrix([S.expand((-1)**i*F[[j for j in range(5)if j!=i],:].det())for i in range(5)])
 assert all(x.subs(t,0)==0 for x in raw)
 k=raw.applyfunc(lambda x:S.cancel(x/t))
 if k[0].subs(t,0)<0:k=-k
 assert all(signcert(x,eps)for x in k)
 assert (F.T*k).applyfunc(S.expand)==S.zeros(4,1)
 d=S.Matrix([S.diff(AA[i,3],t).subs(t,0)for i in Z]);assert list(d)==c['zero_derivative'];assert (d.T*q)[0]>0
 # Construct a nearby strict-primal signature realization, solving the five
 # zero signed last-coordinate derivatives to all+1.
 dirs=[]
 for row,col in itertools.product(range(3),range(8)):
  J=S.zeros(4,8);J[row,col]=1;temp=S.diag(*sg)*normal(Y+J);dirs.append(S.Matrix([temp[i,3]for i in Z]))
 deriv=S.Matrix.hstack(*dirs);assert deriv.rank()==5
 sol=deriv.gauss_jordan_solve(S.ones(5,1))[0];symbols=set().union(*(x.free_symbols for x in sol));sol=sol.subs(dict.fromkeys(symbols,0));G=S.zeros(4,8)
 for x,(row,col)in zip(sol,itertools.product(range(3),range(8))):G[row,col]=x
 YG,AG=family(G)
 assert all(signcert(S.cancel(AG[i,3]/t),eps)for i in Z)
 # A second BAD approach forces a disjoint first-order limit halfspace.
 H2=-H+G/89;YY2,AA2=family(H2);F2=AA2[Z,:]
 raw2=S.Matrix([S.expand((-1)**i*F2[[j for j in range(5)if j!=i],:].det())for i in range(5)])
 assert all(x.subs(t,0)==0 for x in raw2)
 k2=raw2.applyfunc(lambda x:S.cancel(x/t))
 if k2[0].subs(t,0)<0:k2=-k2
 assert all(signcert(x,eps)for x in k2)
 assert (F2.T*k2).applyfunc(S.expand)==S.zeros(4,1)
 d2=S.Matrix([S.diff(AA2[i,3],t).subs(t,0)for i in Z])
 assert d2==-d+S.ones(5,1)/89
 assert (d2.T*r0)[0]<0 and (d2.T*r1)[0]>0
 # One explicit GOOD rational parent and primal e4.
 good=Y+eps*G;goodm=S.diag(*sg)*normal(good);assert all(v>0 for v in goodm[:,3])
 # Hostile controls: center minimizer fails first-order feasibility; perturbing
 # a certified circuit coefficient destroys exact equality.
 damaged=k.copy();damaged[0]+=1
 assert any(x!=0 for x in (F.T*damaged).applyfunc(S.expand))
 out={'classification':'EXACT_ACTUAL_PARENT_NO_CONTINUOUS_NORMALIZED_SECTION','coefficient_field':'Q','normalization':'raw cofactor normals; sum weights=1; Euclidean norm on56 coordinates','signature_integer':sum(1<<i for i,s in enumerate(sg)if s>0),'parent':Y,'perturbation':H,'same_parent_interval':'0<=t<=1/1000000','center_zero_support':Z,'center_zero_triples':[triples[i]for i in Z],'center_signed_normals':A[Z,:],'center_ray0':r0,'center_ray1':r1,'center_minimum_norm_squared':(q.T*q)[0],'minimum_optimality_direction_dot':(q.T*(r1-r0))[0],'family_positive_kernel_polynomials':k,'family_normalized_kernel_limit':k.subs(t,0)/sum(k.subs(t,0)),'zero_last_derivative':d,'derivative_dot_center_minimum':(d.T*q)[0],'derivative_dot_second_ray':(d.T*r1)[0],'second_perturbation':H2,'second_positive_kernel_polynomials':k2,'second_kernel_limit':k2.subs(t,0)/sum(k2.subs(t,0)),'second_zero_last_derivative':d2,'disjoint_limit_halfspaces':'Path1 requires d dot w<=0; Path2 requires d dot w>=1/89. Therefore no continuous normalized nonnegative Gordan witness section exists on any relative neighborhood of the center in the full bad locus.','good_direction':G,'good_parent':good,'good_primal':[0,0,0,1],'good_minimum_margin':min(goodm[:,3]),'proof':'Every feasible weight at center is supported onZ and lies onsegment[r0,r1]. Since q=r0 and q·(r1-r0)>0, q uniquely minimizes norm. For t>0 outsideZ signed last coordinates remainpositive. Any convergent normalized feasible sequence has d·w_limit<=0 after last-coordinate equation is divided byt. Since d·q>0, no such sequence approaches q. Exact positive kernel polynomials prove every t in(0,epsilon] isBAD. GOOD nearby parent proves fixed signature realizable and proper in same parent chamber.','coverage':'One new literal uniform rank4 parent chamber and one new fixed realizable signature. No antichain construction, no source fixed3 result, no original cohomology target refutation.','source_sha256':{'candidate.json':hashlib.sha256((P/'candidate.json').read_bytes()).hexdigest(),'THREE_ROW_WITNESS.json':hashlib.sha256((P.parent/'inputs/certificates/THREE_ROW_WITNESS.json').read_bytes()).hexdigest()},'hostile_changed_circuit_weight_rejected':True,'original_obligations_closed':0,'ledger':'2/9'}
 (P/'certificate.json').write_text(json.dumps(serial(out),indent=2)+'\n');print(json.dumps({'verdict':out['classification'],'signature':out['signature_integer'],'ray0':serial(r0),'ray1':serial(r1),'d_dot_min':str((d.T*q)[0]),'k':serial(k),'G':serial(G),'min_good_margin':str(out['good_minimum_margin'])},indent=2))
if __name__=='__main__':main()
