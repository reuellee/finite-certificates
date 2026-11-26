"""Independent arithmetic replay, no LP solver or producer imports."""
from pathlib import Path
from itertools import combinations, permutations
from fractions import Fraction
from math import gcd,lcm
import hashlib,json,numpy as np,sympy as sp
P=Path(__file__).resolve().parent
src=P.parents[1]/'ai/omreal/data/seeat_parent2599_upper178.npz'
assert hashlib.sha256(src.read_bytes()).hexdigest()=='3b90799d26b7783e92c2ac697eaaf8b76d26a787f53205873b997657e114180a'
X=np.load(src,allow_pickle=False)['chart_matrix'];assert X.shape==(178,4,8)
def norm(Y):
 A=sp.Matrix(Y.tolist());M=A[:,:4].inv()*A;M=sp.diag(*[1/abs(M[i,4]) for i in range(4)])*M
 cols=[]
 for j in range(8):
  d=lcm(*[int(x.q) for x in M[:,j]]);v=[int(d*x) for x in M[:,j]];g=gcd(*v);cols.append(tuple(x//g for x in v))
 return cols
Z=[norm(Y) for Y in X];B=sorted(combinations(range(8),4),key=lambda x:x[::-1]);T=sorted(combinations(range(8),3),key=lambda x:x[::-1]);
def det(cols):
 n=len(cols);return sum((-1)**sum(p[i]>p[j] for i in range(n) for j in range(i+1,n))*__import__('math').prod(cols[i][p[i]] for i in range(n)) for p in permutations(range(n)))
def normals(C):
 ans=[]
 for q in T:
  v=[(-1)**(k+3)*det([[C[j][i] for i in range(4) if i!=k] for j in q]) for k in range(4)];g=gcd(*v);assert g;ans.append([x//g for x in v])
 return ans
N=[normals(C) for C in Z];signs=[1 if det([Z[0][i] for i in q])>0 else -1 for q in B]
assert all(all(s*det([C[i] for i in q])>0 for q,s in zip(B,signs)) for C in Z)
def safe(a,b):
 A,C=Z[a],Z[b];A=[tuple(x*abs(C[j][0]) for x in col) if j>=5 else col for j,col in enumerate(A)];C=[tuple(x*abs(Z[a][j][0]) for x in col) if j>=5 else col for j,col in enumerate(C)]
 for q,s in zip(B,signs):
  mov=[j for j in q if j>=5]
  for k in range(len(mov)+1):
   if sum(s*det([C[j] if j in I else A[j] for j in q]) for I in combinations(mov,k))<=0:return False
 return True
def check(v,sig,r):
 A=[[x*(1 if sig>>j&1 else -1) for x in row] for j,row in enumerate(N[v])]
 if set(r)=={'good'}:
  p=r['good'];assert len(p)==4 and all(isinstance(x,int) for x in p);assert min(sum(a*b for a,b in zip(row,p)) for row in A)>0;return True
 assert set(r)=={'bad'};I,w=r['bad'];assert 1<=len(I)==len(w)<=5 and len(set(I))==len(I) and all(0<=i<56 for i in I) and all(isinstance(x,int) and x>0 for x in w)
 assert all(sum(A[i][j]*x for i,x in zip(I,w))==0 for j in range(4));return False
L=json.loads((P/'deeper_gate.json').read_text());R=json.loads((P/'label_gate.json').read_text());expected={'12_37':([12,37],[0]),'37_176':([37,176],[2,5,8])}
for key,(ends,hits) in expected.items():
 a,b=ends;D=L[key];ss=D['signatures'];assert len(ss)==len(set(ss))==9;assert ss==R[key]['signatures'];assert set(D['vertex_certificates'])==set(map(str,range(178)))
 good={v:[check(v,s,r) for s,r in zip(ss,D['vertex_certificates'][str(v)],strict=True)] for v in range(178)};assert [v for v in good if all(good[v])]==ends
 routes=R[key]['paths'];assert len(routes)==len(set(map(tuple,routes)))==142
 edges={tuple(sorted((i,j))) for p in routes for i,j in zip(p,p[1:])};assert all(safe(i,j) for i,j in edges)
 assert all(p[0]==a and p[-1]==b and len(p)==4 for p in routes)
 assert [i for i in range(9) if all(any(not good[v][i] for v in p) for p in routes)]==hits
 assert not safe(a,b)
 print(key,'PASS',178*9,'integer primal/Gordan certs;',len(routes),'routes;',len(edges),'Bernstein edges; universal bank-hit labels',hits)
print('PASS exact arithmetic replay; no global D9 claim')
