"""Independent exact reconstruction from explicit parent/support inputs only."""
from pathlib import Path
from fractions import Fraction as F
from itertools import combinations,permutations
import json,hashlib
P=Path(__file__).resolve().parent
Y=[[F(x)for x in row]for row in [[1,0,0,0,1,1,1,1],[0,1,0,0,1,-1,4,7],[0,0,1,0,1,2,-5,-4],[0,0,0,1,1,3,2,5]]]
Ks={'P':['123','145','246','356'],'Q':['125','126','356','378'],'R':['123','145','257','348']}
K={name:[tuple(int(c)-1 for c in t)for t in ts]for name,ts in Ks.items()}
def det(A):
 n=len(A);out=F(0)
 for p in permutations(range(n)):
  sign=-1 if sum(p[i]>p[j]for i in range(n)for j in range(i+1,n))%2 else 1
  v=F(sign)
  for i in range(n):v*=A[i][p[i]]
  out+=v
 return out
def tr(A):return list(map(list,zip(*A)))
def cols(A,J):return [[r[j]for j in J]for r in A]
def rr(A):
 A=[r[:]for r in A];m=len(A);n=len(A[0]);k=0;piv=[]
 for j in range(n):
  i=next((i for i in range(k,m)if A[i][j]),None)
  if i is None:continue
  A[k],A[i]=A[i],A[k];d=A[k][j];A[k]=[v/d for v in A[k]]
  for i in range(m):
   if i!=k and A[i][j]:
    d=A[i][j];A[i]=[a-d*b for a,b in zip(A[i],A[k])]
  piv.append(j);k+=1
  if k==m:break
 return A,piv
def rank(A):return len(rr(A)[1])
def null(A):
 R,piv=rr(A);n=len(A[0]);out=[]
 for j in range(n):
  if j in piv:continue
  v=[F(0)]*n;v[j]=F(1)
  for i,k in enumerate(piv):v[k]=-R[i][j]
  out.append(v)
 return out
def normal(V,J):return [F((-1)**(r+3))*det([[V[k][j]for j in J]for k in range(4)if k!=r])for r in range(4)]
N={name:[normal(Y,J)for J in K[name]]for name in K};points={};circuits={}
for name,A in N.items():
 assert det(A)==0 and rank(A)==3
 assert all(rank([A[i]for i in rows])==3 for rows in combinations(range(4),3))
 points[name]=null(A)[0];circuits[name]=null(tr(A))[0];assert all(circuits[name])
p=points['P'];assert p==[F(1,2),F(1),F(1),F(0)]
assert all(rank(tr([points[a],points[b]]))==2 for a,b in combinations(K,2))
assert rank(tr(list(points.values())))==3
brackets={''.join(str(j+1)for j in J):det(cols(Y,J))for J in combinations(range(8),4)};assert all(brackets.values())
gammas={};derivatives={}
for name in ['Q','R']:
 q=points[name];lam=circuits[name];gamma=[F(0)]*8;deriv=[F(0)]*8
 for j in range(8):
  for i,J in enumerate(K[name]):
   if j not in J:continue
   T=cols(Y,J);slot=J.index(j)
   for k in range(4):T[k][slot]=p[k]
   gamma[j]+=lam[i]*det([row+[q[k]]for k,row in enumerate(T)])
   dn=[F((-1)**(k+3))*det([T[l]for l in range(4)if l!=k])for k in range(4)]
   MM=[row[:]for row in N[name]];MM[i]=dn;deriv[j]+=det(MM)
 gammas[name]=gamma;derivatives[name]=deriv
 for g in [gamma,deriv]:assert all(sum(a*b for a,b in zip(g,row))==0 for row in Y)
 if any(gamma):
  k=next(k for k,c in enumerate(gamma)if c);scale=deriv[k]/gamma[k];assert scale!=0 and deriv==[scale*c for c in gamma]
 else:assert not any(deriv)
assert rank(list(gammas.values()))==rank(list(derivatives.values()))==1
assert not any(gammas['Q']) and any(gammas['R'])
# The accepted anchor frame is labels1,2,4; label3 fixes scale. At this parent,
# contraction is (v2-2v1,v3-2v1,v4); after shear, height is v3. Thus free normalized
# parent heights are exactly labels5,6,7,8, and their variations replace Y_j by p.
vertical={n:v[4:]for n,v in derivatives.items()};assert rank(list(vertical.values()))==1
# Verify canonical49 and ordinary37 relabelings, independently of source labels.
relabels={'Q':([1,2,5,6,3,7,8,4],['123','124','345','567']),'R':([1,2,3,5,4,7,8,6],['123','145','246','357'])}
for name,(pm,prototype)in relabels.items():
 result=sorted(''.join(map(str,sorted(pm[int(c)-1]for c in t)))for t in prototype)
 assert result==sorted(Ks[name])
def enc(v):
 if isinstance(v,F):return str(v)
 if isinstance(v,list):return [enc(x)for x in v]
 if isinstance(v,dict):return {k:enc(x)for k,x in v.items()}
 return v
out=enc({'verdict':'PASS actual uniform collision-free noncollinear vertical-critical point','scope':'Refutes dependent height gradients imply collinear selected ordinary concurrences. No compact component or global triple-escape counterexample is claimed.','parent':Y,'supports_1based':Ks,'global_factor_kinds':{'P':48,'Q':36,'R':49},'parent_brackets_1based':brackets,'ordinary_normal_matrices':N,'ordinary_concurrences':points,'ordinary_circuit_dependences':circuits,'concurrence_span_rank':3,'all_pairwise_concurrences_distinct':True,'circuit_gradients_8heights':gammas,'direct_normal_determinant_derivatives_8heights':derivatives,'normalized_free_height_labels':[5,6,7,8],'direct_derivatives_4heights':vertical,'vertical_gradient_rank':1,'new_original_obligations':0,'new_triple_source_count':0})
(P/'NONCOLLINEAR_INDEPENDENT_REPLAY.json').write_text(json.dumps(out,indent=2)+'\n')
print('PASS70 parent units; three ordinary wall circuits; distinct concurrences spanning rank3; direct vertical determinant rank1')
print('gammaQ',gammas['Q']);print('gammaR',gammas['R']);print('directD',derivatives)
