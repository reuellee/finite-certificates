from verify_three_boundary_signatures import *
from math import gcd,lcm
from functools import reduce
J=json.loads((P/'ACTUAL_THREE_BOUNDARY_SIGNATURES.json').read_text());Y=matrix(J['center']['Y']);AA=normals(Y)
def primitive(v):
 L=lcm(*(x.denominator for x in v));w=[int(x*L) for x in v];g=reduce(gcd,w);w=[x//g for x in w]
 if next(x for x in w if x)<0:w=[-x for x in w]
 return tuple(w)
A=[primitive(row) for row in AA]
def d3(a,b,c):return a[0]*(b[1]*c[2]-b[2]*c[1])-a[1]*(b[0]*c[2]-b[2]*c[0])+a[2]*(b[0]*c[1]-b[1]*c[0])
def cross(a,b,c):return tuple((-1)**r*d3([a[k] for k in range(4) if k!=r],[b[k] for k in range(4) if k!=r],[c[k] for k in range(4) if k!=r]) for r in range(4))
groups={}
for I in combinations(range(56),3):
 p=cross(*(A[k] for k in I))
 if not any(p):continue
 g=reduce(gcd,p);p=tuple(x//g for x in p)
 if next(x for x in p if x)<0:p=tuple(-x for x in p)
 groups.setdefault(p,set()).update(I)
cs=[]
for p,G in groups.items():
 if len(G)<4:continue
 for I in combinations(sorted(G),4):
  edges=[set(T[k]) for k in I]
  if set.intersection(*edges):continue
  if any(sum(set(pair)<=E for E in edges)>=3 for pair in combinations(range(8),2)):continue
  if not all(any(cross(*(A[k] for k in Q))) for Q in combinations(I,3)):continue
  cs.append((I,p))
print('points',len(groups),'ordinary residual circuits',len(cs),flush=True)
count=0
for C in combinations(cs,3):
 U=set(k for I,p in C for k in I);degrees=[sum(e in T[k] for k in U) for e in range(8)]
 if min(degrees)<3:continue
 points=[list(p) for I,p in C]
 if rank(points)!=3:continue
 print('FOUND',C,'degrees',degrees,flush=True);out={'schema':'hard_three_distinct_boundary_points_v1','center':J['center'],'supports':[[k for k in I] for I,p in C],'points':points,'degrees':degrees,'circuits_at_center':len(cs)};(P/'HARD_THREE_BOUNDARY_POINTS.json').write_text(json.dumps(out,indent=2)+'\n');break
else:print('NO HARD TRIPLE',flush=True)
