#!/usr/bin/env python3
"""Reconstruct all data using only Python integer/Fraction arithmetic."""
from fractions import Fraction as F
from itertools import combinations
from pathlib import Path
import json,hashlib
P=Path(__file__).resolve().parent

def matrix(rows):return [[F(x) for x in row] for row in rows]
def det(A):
 A=[row[:] for row in A];n=len(A);out=F(1)
 for c in range(n):
  pivot=next((r for r in range(c,n) if A[r][c]),None)
  if pivot is None:return F(0)
  if pivot!=c:A[pivot],A[c]=A[c],A[pivot];out=-out
  q=A[c][c];out*=q
  for r in range(c+1,n):
   u=A[r][c]/q
   for k in range(c+1,n):A[r][k]-=u*A[c][k]
 return out

def rank(A):
 A=[row[:] for row in A];r=0
 for c in range(len(A[0])):
  p=next((j for j in range(r,len(A)) if A[j][c]),None)
  if p is None:continue
  A[r],A[p]=A[p],A[r];q=A[r][c];A[r]=[x/q for x in A[r]]
  for j in range(r+1,len(A)):
   q=A[j][c];A[j]=[x-q*y for x,y in zip(A[j],A[r])]
  r+=1
  if r==len(A):break
 return r
T=list(combinations(range(8),3));B=list(combinations(range(8),4))
def normals(Y):return [[(-1)**(r+3)*det([[Y[k][j] for j in I] for k in range(4) if k!=r]) for r in range(4)] for I in T]
def brackets(Y):return [det([[Y[r][j] for j in I] for r in range(4)]) for I in B]
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def positive_relation(N,signs):
 assert rank(N)==3
 for colset in combinations(range(4),3):
  rel=[(-1)**r*det([[N[j][c] for c in colset] for j in range(4) if j!=r]) for r in range(4)]
  if not any(rel):continue
  assert all(dot(rel,[N[j][c] for j in range(4)])==0 for c in range(4))
  signed=[a*b for a,b in zip(rel,signs)]
  assert all(x>0 for x in signed) or all(x<0 for x in signed)
  return
 raise AssertionError('no rank-three relation')

def verify(J, expected_degrees=None):
 Y=matrix(J['center']['Y']);A=normals(Y);bb=brackets(Y);assert len(bb)==70 and all(bb)
 assert bb==list(map(F,J['center']['parent_brackets']))
 S=J['signatures'];assert len(S)==3;points=[];U=set()
 for idx,s in enumerate(S):
  assert s['index']==idx
  sigma=s['signs'];assert J['triple_order']=='lexicographic combinations of labels 0..7'
  colex=sorted(T,key=lambda x:tuple(reversed(x)))
  assert sum((sigma[T.index(t)]==1)<<k for k,t in enumerate(colex))==s['signature_bits_colex']
  assert len(sigma)==56 and set(sigma)=={-1,1}
  assert sum((x==1)<<k for k,x in enumerate(sigma))==s['signature_bits_lex']
  support=s['support_indices'];assert len(set(support))==4;U.update(support)
  N=[A[k] for k in support];rel=list(map(F,s['positive_weights']))
  assert all(w>0 for w in rel)
  assert all(sum(rel[j]*sigma[k]*A[k][c] for j,k in enumerate(support))==0 for c in range(4))
  positive_relation(N,[sigma[k] for k in support])
  p=list(map(F,s['weak_primal']));points.append(p);assert any(p)
  vv=[sigma[k]*dot(A[k],p) for k in range(56)]
  assert all(x>=0 for x in vv) and any(x>0 for x in vv)
  assert [k for k in range(56) if vv[k]==0]==s['all_zero_indices']
  # Positive relation forces every weak-primal vector into ker N;
  # rank N=3 makes that a line, and a strict signed value fixes its ray.
  assert rank(N)==3 and all(dot(row,p)==0 for row in N)
  Q=matrix(s['feasible_parent']);C=normals(Q);qb=brackets(Q)
  assert all(Q[r][k]==Y[r][k] for r in [0,2,3] for k in range(8))
  assert all(x*y>0 for x,y in zip(bb,qb))
  q=list(map(F,s['feasible_point']));assert all(sigma[k]*dot(C[k],q)>0 for k in range(56))
  for j,t in enumerate(S):
   if j==idx:continue
   positive_relation([C[k] for k in t['support_indices']],[t['signs'][k] for k in t['support_indices']])
 assert rank(points)==3
 degrees=[sum(e in T[k] for k in U) for e in range(8)]
 assert expected_degrees is None or degrees==expected_degrees
 return {'status':'PASS','parent_brackets_per_matrix':70,'signed_normals_per_signature':56,'actual_signatures':3,'positive_center_circuits':3,'weak_primal_ray_rank':3,'exclusive_feasibility_anchors':3,'cross_badness_checks':6,'support_union_degrees':degrees,'scope':'No automatic common weak-primal direction for original proper incomparable triples; no compact component or D3 counterexample.'}

if __name__=='__main__':
 path=P/'ACTUAL_THREE_BOUNDARY_SIGNATURES.json';J=json.loads(path.read_text());out=verify(J)
 # Concrete hostile checks alter the original claims, not cosmetic metadata.
 from copy import deepcopy
 mutants=[]
 q=deepcopy(J);q['signatures'][0]['signs'][0]*=-1;mutants.append(q)
 q=deepcopy(J);q['signatures'][0]['weak_primal'][0]='0';mutants.append(q)
 q=deepcopy(J);q['signatures'][0]['feasible_parent'][1][5]='13/3';mutants.append(q)
 rejected=0
 for q in mutants:
  try:verify(q)
  except (AssertionError,ZeroDivisionError):rejected+=1
 assert rejected==len(mutants)
 out['hostile_mutations_rejected']=rejected;out['input_sha256']=hashlib.sha256(path.read_bytes()).hexdigest()
 (P/'THREE_BOUNDARY_REPLAY.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,sort_keys=True))
