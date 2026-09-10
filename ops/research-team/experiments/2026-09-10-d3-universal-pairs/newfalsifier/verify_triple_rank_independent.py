#!/usr/bin/env python3
"""Independent Fraction/permutation replay; no producer imports or matrix input."""
from pathlib import Path
from fractions import Fraction as F
from itertools import permutations,combinations
import json,hashlib
P=Path(__file__).resolve().parent;root=P.parent
source=root/'checkpoint/triple/UNIQUE_HARD_THREE_BOUNDARY_POINTS.json'
d=json.loads(source.read_text());Y=[[F(x)for x in r]for r in d['center']['Y']]
PS=[(1,2,3),(1,4,5),(2,4,6),(3,5,7)];QS=[(1,2,7),(1,5,8),(2,3,4),(3,5,7)];RS=[(2,3,6),(2,4,8),(4,5,6),(5,7,8)]
points=[[F(x)for x in p]for p in [(1,7,7,0),(0,24,5,-4),(9,14,18,54)]]
def det(M):
 n=len(M);v=F(0)
 for p in permutations(range(n)):
  z=F((-1)**sum(p[i]>p[j]for i in range(n)for j in range(i+1,n)))
  for i,j in enumerate(p):z*=M[i][j]
  v+=z
 return v
def rank(M):
 A=[row[:]for row in M];r=0;piv=[]
 for c in range(len(A[0])):
  k=next((k for k in range(r,len(A))if A[k][c]),None)
  if k is None:continue
  A[r],A[k]=A[k],A[r];z=A[r][c];A[r]=[x/z for x in A[r]]
  for k in range(len(A)):
   if k!=r:
    z=A[k][c];A[k]=[x-z*y for x,y in zip(A[k],A[r])]
  piv.append(c);r+=1
  if r==len(A):break
 return r,piv
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def normals(K):
 return [[det([[Y[r][j-1]for j in I]+[F(r==a)]for r in range(4)])for a in range(4)]for I in K]
assert all(det([[Y[r][j]for j in J]for r in range(4)])for J in combinations(range(8),4))
for K,x in zip([PS,QS,RS],points):
 N=normals(K);assert rank(N)[0]==3 and all(dot(n,x)==0 for n in N)
# Independently apply the literal coordinate functions z1=y2-7y1,z2=y3-7y1,z3=y4,h=y1.
A=[[Y[1][j]-7*Y[0][j]for j in range(8)],[Y[2][j]-7*Y[0][j]for j in range(8)],Y[3][:]]
proj=lambda x:[x[1]-7*x[0],x[2]-7*x[0],x[3]]
zq,zr=map(proj,points[1:]);actual=Y[0][:]+[points[1][0],points[2][0]]
rows=[]
for block,(K,z)in enumerate([(QS,zq),(RS,zr)]):
 for I in K:
  row=[]
  for j in range(10):
   H=[F(k==j)for k in range(10)]
   M=[[A[r][k-1]for k in I]+[z[r]]for r in range(3)]
   M.append([H[k-1]for k in I]+[H[8+block]])
   row.append(det(M))
  rows.append(row)
assert rank(rows)[0]==6
assert all(dot(row,actual)==0 for row in rows)
shears=[A[k]+[zq[k],zr[k]]for k in range(3)]
assert all(dot(row,s)==0 for row in rows for s in shears)
assert rank(shears+[actual])[0]==4
assert rank([row[4:]for row in rows])[0]==6
# Record an independently found exact nonzero minor.
minor=None
for rr in combinations(range(8),6):
 M=[rows[r][4:]for r in rr];dd=det(M)
 if dd:minor={'rows_zero_based':rr,'columns_zero_based':list(range(4,10)),'determinant':str(dd)};break
assert minor
producer=json.loads((root/'alternative/TRIPLE_RANK6_GATE.json').read_text())
reported=[[F(x)for x in row]for row in producer['incidence_matrix']]
row_signs=[]
for a,b in zip(rows,reported):
 assert a==b or a==[-x for x in b]
 row_signs.append(1 if a==b else-1)
assert producer['incidence_rank']==producer['normalized_coefficient_rank']==6
# Wrong unique-solution/extra physical-motion claims are discriminated exactly.
wrong=actual.copy();wrong[4]+=1;assert any(dot(row,wrong)for row in rows)
out={'verdict':'ACCEPT_EXACT_RANK6_MARKED_TRIPLE_HEIGHT_GATE','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'producer_snapshot_sha256':hashlib.sha256((root/'alternative/TRIPLE_RANK6_GATE.json').read_bytes()).hexdigest(),'all70_parent_brackets_nonzero':True,'three_normal_system_ranks':[3,3,3],'incidence_rank':6,'normalized_8x6_rank':6,'kernel_dimension':4,'gauge_kernel_basis_rank':4,'nonzero_normalized_minor':minor,'row_signs_relative_producer':row_signs,'hostile_changed_height_rejected':True,'reconstruction':'Direct determinants evaluated on each of10 unit height assignments using only fractions and permutations; no producer coefficient formulas or rank routines','scope':'Fixes projected parent and both projected Q/R concurrence directions. Only three shears plus globalscale remain; says nothing about motions changing projected data. Predecessor-settled fixture; no new triple/source count or original obligation.'}
# Independently reconstruct the two raw factor identities with sparse rational polynomials.
ZERO=(0,0,0,0)
def pc(x):return {ZERO:F(x)}if x else{}
def add(*polys):
 out={}
 for p0 in polys:
  for m,x in p0.items():out[m]=out.get(m,F(0))+x
 return {m:x for m,x in out.items()if x}
def mul(a,b):
 out={}
 for m,x in a.items():
  for n,y in b.items():
   k=tuple(i+j for i,j in zip(m,n));out[k]=out.get(k,F(0))+x*y
 return {m:x for m,x in out.items()if x}
def scale(p0,x):return {m:y*x for m,y in p0.items()if y*x}
def dp(M):
 n=len(M);out={}
 for perm in permutations(range(n)):
  v=pc((-1)**sum(perm[i]>perm[j]for i in range(n)for j in range(i+1,n)))
  for i,j in enumerate(perm):v=mul(v,M[i][j])
  out=add(out,v)
 return out
us=[{tuple(int(j==k)for j in range(4)):F(1)}for k in range(4)]
hh=[pc(1),pc(0),pc(0),pc(0)]+us
YY=[hh,[add(pc(A[0][j]),scale(hh[j],7))for j in range(8)],[add(pc(A[1][j]),scale(hh[j],7))for j in range(8)],[pc(A[2][j])for j in range(8)]]
def bracket(I):return dp([[YY[r][j-1]for j in I]for r in range(4)])
def raw_wall(K):
 normals=[]
 for I in K:
  normals.append([scale(dp([[YY[r][j-1]for j in I]for r in range(4)if r!=k]),(-1)**(k+3))for k in range(4)])
 return dp(normals)
FF={(1,0,1,0):F(126),(1,0,0,0):F(-164),(0,0,1,1):F(63),(0,0,1,0):F(-77),(0,0,0,1):F(-234),ZERO:F(286)}
GG={(2,0,0,0):F(80),(1,1,0,0):F(205),(1,0,1,0):F(85),(1,0,0,1):F(1301),(0,1,1,0):F(-95),(0,1,0,1):F(-208),(0,0,1,1):F(582),(0,0,0,2):F(-1950)}
unitQ=add(scale(us[0],4),us[2]);unitR=us[1]
assert raw_wall(PS)=={}
assert raw_wall(QS)==scale(mul(unitQ,FF),F(7,9))
assert raw_wall(RS)==scale(mul(unitR,GG),F(8,3))
assert bracket((2,3,5,7))==scale(unitQ,-1)
assert bracket((2,3,4,6))==scale(unitR,-1)
assert all(all(sum(m)<=1 for m in bracket(I))for I in combinations(range(1,9),4))
assert rank(points)[0]==3
out['three_concurrence_points_rank']=3
out['independent_sparse_polynomial_identities']={'P_identically_zero':True,'Q_raw_factor':True,'R_raw_factor':True,'Q_extra_unit_bracket2357':True,'R_extra_unit_bracket2346':True,'all70_parent_brackets_affine':True}
out['triangular_escape_review']='ACCEPT_SCOPED_FIXED_PROJECTED_PARENT_ESCAPE; eliminate h6 first, then h5, retaining zero-coefficient open fibers. No universal triangular statement or new triple coverage.'
(P/'TRIPLE_RANK6_INDEPENDENT_REPLAY.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
