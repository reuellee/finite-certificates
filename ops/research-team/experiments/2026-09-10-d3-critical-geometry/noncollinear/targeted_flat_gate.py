"""One-parent targeted search for a third wall off the known zero-gradient line."""
from itertools import combinations
from math import gcd
from functools import reduce
from collections import defaultdict
import sympy as s
from gradient_map_probe import Y,normal,gradmap
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
def prim(v):
 d=reduce(gcd,map(abs,v));w=tuple(x//d for x in v)
 return tuple(-x for x in w) if next(x for x in w if x)<0 else w
T=[''.join(map(str,I)) for I in combinations(range(1,9),3)]
N=[prim(tuple(map(int,normal(Y,I)))) for I in T]
def d3(a,b,c):return a[0]*(b[1]*c[2]-b[2]*c[1])-a[1]*(b[0]*c[2]-b[2]*c[0])+a[2]*(b[0]*c[1]-b[1]*c[0])
def cross(a,b,c):
 return tuple((-1)**j*d3([a[k] for k in range(4) if k!=j],[b[k] for k in range(4) if k!=j],[c[k] for k in range(4) if k!=j]) for j in range(4))
parents={prim(tuple(map(int,Y[:,j]))) for j in range(8)}
flats=defaultdict(set)
for I in combinations(range(56),3):
 v=cross(*[N[i] for i in I])
 if not any(v):continue
 v=prim(v)
 if v in parents:continue
 flats[v].update(I)
p=gradmap(Y,('123','145','246','356'))[1];q=gradmap(Y,('125','126','356','378'))[1]
out=[]
for v,inds in flats.items():
 if len(inds)<4 or s.Matrix.hstack(p,q,s.Matrix(v)).rank()!=3:continue
 for I in combinations(sorted(inds),4):
  if all(any(cross(*[N[i] for i in J])) for J in combinations(I,3)):
   K=tuple(T[i] for i in I);R,r,lam,B=gradmap(Y,K)
   assert R.det()==0 and s.Matrix.hstack(p,q,r).rank()==3
   out.append({'R':K,'r':list(map(str,r)),'gamma_R':list(map(str,B*p)),'ordinary_normal_indices':I})
   break
print('ordinary noncollinear candidates',len(out));print(json.dumps(out[:5],indent=2))
(ROOT/'noncollinear/TARGETED_FLAT_DISCOVERY.json').write_text(json.dumps({'status':'discovery_candidates_requiring_factor_identity_audit','scope':'one inherited actual parent; no new parent sampling','parent':[[str(x) for x in row] for row in Y.tolist()],'P':['123','145','246','356'],'Q':['125','126','356','378'],'candidates':out},indent=2)+'\n')
