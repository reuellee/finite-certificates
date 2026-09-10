from pathlib import Path
from itertools import combinations,permutations
from math import gcd
from functools import reduce
from collections import Counter,defaultdict
import json,random,time
P=Path(__file__).resolve().parent;Y=[[1,0,0,0,1,1,1,1],[0,1,0,0,1,-1,4,7],[0,0,1,0,1,2,-5,-4],[0,0,0,1,1,3,2,5]];anchor=(1,2,2,0)
perms={n:[(p,(-1)**sum(p[i]>p[j]for i in range(n)for j in range(i+1,n)))for p in permutations(range(n))]for n in [3,4]}
def det(A):
 return sum(sign*reduce(lambda a,b:a*b,(A[i][p[i]]for i in range(len(A))),1)for p,sign in perms[len(A)])
def normal(J):return tuple((-1)**(r+3)*det([[Y[k][j]for j in J]for k in range(4)if k!=r])for r in range(4))
def prim(v):
 g=reduce(gcd,(abs(x)for x in v));
 if not g:return None
 sg=1 if next(x for x in v if x)>0 else -1
 return tuple(sg*x//g for x in v)
def kernel3(A):return prim([(-1)**r*det([[row[k]for k in range(4)if k!=r]for row in A])for r in range(4)])
trs=list(combinations(range(8),3));norm=[normal(J)for J in trs];parentpoints={prim([Y[k][j]for k in range(4)])for j in range(8)};start=time.time();unique=set()
for ids in combinations(range(56),3):
 q=kernel3([norm[j]for j in ids])
 if q and q not in parentpoints and q!=prim(anchor):unique.add(q)
clusters=[]
for q in unique:
 ids=[i for i,n in enumerate(norm)if sum(a*b for a,b in zip(n,q))==0]
 if len(ids)>=4:clusters.append((q,ids))
def classify(I):
 ts=[set(trs[j])for j in I];counts=Counter(k for J in ts for k in J)
 if max(counts.values())>2 or any(len(a&b)>1 for a,b in combinations(ts,2)):return None
 used=len(counts)
 if used==6:return 48
 if used==7:return 49
 if used==8:
  deg=sorted(sum(bool(ts[i]&ts[j])for j in range(4)if i!=j)for i in range(4))
  return 50 if deg==[1,2,2,3]else 51 if deg==[2,2,2,2]else None
 return None
cands=[]
for q,ids in clusters:
 for I in combinations(ids,4):
  kind=classify(I)
  if kind:cands.append((kind,q,I))
cands.sort();rng=random.Random(61577);rng.shuffle(cands)
# Round-robin kinds avoids spending the budget on one prolific family.
bykind={k:[r for r in cands if r[0]==k]for k in [48,49,50,51]};selected=[]
for idx in range(64):
 k=[48,49,50,51][idx%4]
 if not bykind[k]:k=max(bykind,key=lambda kk:len(bykind[kk]))
 if not bykind[k]:break
 selected.append(bykind[k].pop())
def circuit(A):
 for omitcol in range(4):
  l=[(-1)**i*det([[A[j][k]for k in range(4)if k!=omitcol]for j in range(4)if j!=i])for i in range(4)]
  if any(l):return prim(l)
 raise AssertionError('rank below3')
def gamma(I,q):
 A=[norm[i]for i in I];assert det(A)==0
 assert all(kernel3([A[i]for i in J])is not None for J in combinations(range(4),3))
 l=circuit(A);assert all(l);g=[0]*8
 for lam,ii in zip(l,I):
  J=trs[ii]
  for j in J:
   T=[[Y[k][v]for v in J]for k in range(4)];slot=J.index(j)
   for k in range(4):T[k][slot]=anchor[k]
   g[j]+=lam*det([row+[q[k]]for k,row in enumerate(T)])
 return prim(g),g
records=[];groups=defaultdict(list);hits=[]
for kind,q,I in selected:
 direction,g=gamma(I,q);r={'kind':kind,'support_1based':[''.join(str(j+1)for j in trs[i])for i in I],'concurrence':q,'gamma':g,'gamma_direction':direction};records.append(r)
 if direction:
  for other in groups[direction]:
   if kernel3([anchor,q,other['concurrence']])is not None:
    # Different kinds are already distinct global primitive-factor orbits.
    if kind!=other['kind']:hits.append({'first':other,'second':r,'distinct_factor_reason':'different global factor kinds'})
  groups[direction].append(r)
 if hits:break
out={'scope':'Bounded64 ordinary-wall checks at one authenticated nongeneric parent; repaired nonzero-gradient criticality discriminator only','parent':Y,'anchor_support_1based':['123','145','246','356'],'anchor_concurrence':anchor,'unique_nonparent_concurrence_points_from_triples':len(unique),'clusters_with_at_least4_planes':len(clusters),'high_family_candidate_occurrences':len(cands),'candidate_counts_by_kind':dict(Counter(k for k,q,I in cands)),'selected_occurrences_checked':len(records),'records':records,'different_kind_noncollinear_matches':hits,'seconds':time.time()-start}
(P/'NONZERO_GAMMA_SEARCH.json').write_text(json.dumps(out,indent=2)+'\n');print('clusters',len(clusters),'candidates',Counter(k for k,q,I in cands),'checks',len(records),'nonzero',sum(r['gamma_direction']is not None for r in records),'directions',len(groups),'hits',hits,'seconds',time.time()-start)
