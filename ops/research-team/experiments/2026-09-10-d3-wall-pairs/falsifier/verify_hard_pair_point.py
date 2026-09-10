#!/usr/bin/env python3
"""Exact original-geometry point certificate; no producer verifier imports."""
from fractions import Fraction as Q
from itertools import combinations, permutations
from pathlib import Path
import json,hashlib
P=Path(__file__).resolve().parent
vals=list(map(Q,['7','-8','-4','-17/4','2','-3','2','-2116/67','-8']))
a,b,c,d,e,f,g,h,i=vals
Y=[[Q(x)for x in r]for r in [[1,0,0,0,1,1,1,1],[0,1,0,0,1,a,d,g],[0,0,1,0,1,b,e,h],[0,0,0,1,1,c,f,i]]]
U=((1,2,3),(1,4,5),(2,4,6),(3,7,8));V=((5,6,7),(1,5,8),(2,6,8),(3,4,7))
def det(M):
 n=len(M);out=Q(0)
 for p in permutations(range(n)):
  z=(-1)**sum(p[i]>p[j]for i in range(n)for j in range(i+1,n))
  for r in range(n):z*=M[r][p[r]]
  out+=z
 return out
def normal(t):return [(-1)**(r+3)*det([[Y[k][j-1]for j in t]for k in range(4)if k!=r])for r in range(4)]
def rank3(rows):
 return det(rows)==0 and any(det([[rows[r][c]for c in cs]for r in rs])!=0 for rs in combinations(range(4),3)for cs in combinations(range(4),3))
bs=[det([[Y[r][j]for j in J]for r in range(4)])for J in combinations(range(8),4)]
assert all(bs)
N=[list(map(normal,Z))for Z in [U,V]]
assert all(rank3(M)for M in N)
assert tuple(sum(e in T for T in U+V)for e in range(1,9))==(3,)*8
assert len(set(U+V))==8
perm=(5,6,7,8,1,2,3,4)
assert set(V)=={tuple(sorted(perm[x-1]for x in T))for T in U}
# Type50 canonical factor checked directly independently of source polynomial.
assert b*f-b*i+d*i-f*g==0
changed=[row[:]for row in N[0]];changed[0][0]+=1
# A mutation at an actually nonzero cofactor must break the determinant.
canary=False
for r in range(4):
 for c in range(4):
  changed=[row[:]for row in N[1]];changed[r][c]+=1
  if det(changed)!=0:canary=True;break
 if canary:break
assert canary
report={'status':'EXACT_UNIFORM_HARD_50_50_INTERSECTION_POINT_ONLY','scope':'Point on full two actual residual walls; no Hc1 or global topology result','point':list(map(str,vals)),'parent':[[str(x)for x in row]for row in Y],'supports':[U,V],'support_union_degree':[3]*8,'normal_matrices':[[[str(x)for x in row]for row in M]for M in N],'all70_parent_brackets_nonzero':True,'parent_bracket_signs':[int(x>0)-int(x<0)for x in bs],'normal_support_ranks':[3,3],'normal_support_determinants':['0','0'],'point_mutation_rejected':canary}
(P/'HARD_PAIR_POINT.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items()if k not in ['parent','normal_matrices','parent_bracket_signs']},indent=2))
