"""Exact finite-field-free discovery gate for possible Gale quartet identities.
Matching finitely many parents is a discovery filter only, never an identity proof.
"""
from itertools import combinations,permutations
from collections import Counter
from pathlib import Path
import random,json
ROOT=Path(__file__).resolve().parents[1]
PERMS={n:[(p,(-1)**sum(p[i]>p[j] for i in range(n) for j in range(i+1,n))) for p in permutations(range(n))] for n in (3,4)}
def det(A):
 return sum(s*__import__('math').prod(A[i][p[i]] for i in range(len(A))) for p,s in PERMS[len(A)])
def normal(Y,I):
 A=[[Y[r][i-1] for i in I] for r in range(4)]
 return [(-1)**r*det([A[s] for s in range(4) if s!=r]) for r in range(4)]
def makeY(rng):
 while 1:
  B=[[rng.randrange(-9,10) for i in range(4)] for j in range(4)]
  Y=[[int(i==j) for j in range(4)]+B[i] for i in range(4)]
  if all(det([[Y[i][j] for j in J] for i in range(4)]) for J in combinations(range(8),4)):return Y,[[-B[j][i] for j in range(4)]+[int(i==j) for j in range(4)] for i in range(4)]
def degree(P):return tuple(sum(j in I for I in P) for j in range(1,9))
def main():
 rng=random.Random(20260910);parents=[makeY(rng) for i in range(3)]
 ts=list(combinations(range(1,9),3));ns=[{t:normal(Y,t) for t in ts} for Y,G in parents];gs=[{t:normal(G,t) for t in ts} for Y,G in parents]
 reps={50:((1,2,3),(1,4,5),(2,4,6),(3,7,8)),51:((1,2,3),(1,4,5),(2,6,7),(4,6,8))}
 out={}
 for typ,P in reps.items():
  d=tuple(3-v for v in degree(P));target=[det([N[t] for t in P]) for N in gs];matches=[];count=0
  for R in combinations(ts,4):
   if degree(R)!=d:continue
   count+=1;v=[det([N[t] for t in R]) for N in ns]
   if all(v[k]*target[0]==v[0]*target[k] for k in range(1,3)) and v[0]:matches.append({'quartet':R,'ratio_numerator':v[0],'ratio_denominator':target[0]})
  out[typ]={'input':P,'dual_degree':d,'candidate_count':count,'matches':matches,'target_values':target}
 print(json.dumps(out,indent=2));(ROOT/'alternative/GALE_PRESENTATION_DISCOVERY.json').write_text(json.dumps({'status':'discovery_only_three_exact_parents','parents':[Y for Y,G in parents],'families':out},indent=2)+'\n')
if __name__=='__main__':main()
