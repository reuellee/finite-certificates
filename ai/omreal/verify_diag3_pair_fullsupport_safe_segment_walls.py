#!/usr/bin/env python3
"""Exact interior-crossing certificate for row-2599 full-support walls.

A fixed set of 105 straight segments joins stored exact row-2599 interior
realizations. Every segment is proved to stay in the strict parent cell by
exact rational Bernstein subdivision of all seventy signed parent brackets.
Floating point is then used only to propose residual-wall crossings; every
accepted crossing is rechecked by exact rational endpoint evaluation. A
floating-point miss can therefore only leave a factor open, never create a
false nonemptiness certificate.
"""
from __future__ import annotations
from fractions import Fraction
from math import comb
import hashlib,json
from pathlib import Path
import sys
import numpy as np
from scipy.sparse import csr_matrix
HERE=Path(__file__).resolve().parent; sys.path.insert(0,str(HERE))
import DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY as labeled
import verify_diag2_canonical_robust_edges as evaluator
import verify_diag3_pair_global_parent_face_gate as gate
CATALOG=HERE/'certs_4_8.jsonl'
EDGES=((0,2),(0,8),(0,10),(0,11),(0,19),(0,21),(0,23),(0,25),(0,26),(0,27),(0,35),(0,38),(0,46),(0,52),(0,55),(0,56),(0,60),(0,66),(0,67),(0,68),(0,72),(0,74),(0,76),(0,79),(0,80),(0,85),(0,86),(0,89),(0,96),(0,98),(0,102),(0,104),(0,105),(0,106),(0,107),(0,108),(0,109),(0,111),(0,112),(0,113),(0,121),(0,122),(0,127),(0,129),(0,131),(0,132),(0,134),(0,137),(0,140),(0,145),(0,147),(0,150),(0,151),(0,155),(0,160),(0,162),(0,165),(1,10),(1,13),(1,15),(1,31),(1,32),(1,37),(1,39),(1,44),(1,48),(1,53),(1,59),(1,69),(1,73),(1,75),(1,77),(1,81),(1,82),(1,84),(1,90),(1,94),(1,114),(1,116),(1,117),(1,119),(1,126),(1,173),(2,3),(2,6),(2,7),(2,12),(2,14),(2,20),(2,24),(2,28),(2,29),(2,50),(2,63),(2,91),(2,92),(3,30),(4,10),(4,17),(4,22),(4,163),(5,65),(7,33),(10,61),(13,161))
EXPECTED_CROSSED=10844; EXPECTED_OPEN=6980
EXPECTED_OPEN_SHA256='72de0ff0ba439e00a54e8fdb16a1505d4d7a8fbfaf7f42c00030f1c1a7149930'
MAX_DEPTH=8

def mul_linear(poly,a,b):
 out=[Fraction(0)]*(len(poly)+1)
 for k,c in enumerate(poly):out[k]+=c*a;out[k+1]+=c*b
 return out
def segment_power(poly,x0,x1):
 out=[Fraction(0)]*(max(sum(m) for m in poly)+1); dx=tuple(b-a for a,b in zip(x0,x1))
 for m,c in poly.items():
  term=[Fraction(c)]
  for i,e in enumerate(m):
   for _ in range(e):term=mul_linear(term,x0[i],dx[i])
  for k,v in enumerate(term):out[k]+=v
 while len(out)>1 and out[-1]==0:out.pop()
 return out
def restrict_power(c,lo,hi):
 s=hi-lo; out=[Fraction(0)]*len(c)
 for k,v in enumerate(c):
  for j in range(k+1):out[j]+=v*comb(k,j)*lo**(k-j)*s**j
 while len(out)>1 and out[-1]==0:out.pop()
 return out
def bernstein(c):
 d=len(c)-1
 if d==0:return tuple(c)
 return tuple(sum(c[k]*Fraction(comb(j,k),comb(d,k)) for k in range(j+1)) for j in range(d+1))
def positive_unit(c):
 stack=[(Fraction(0),Fraction(1),0)]
 while stack:
  lo,hi,depth=stack.pop(); b=bernstein(restrict_power(c,lo,hi))
  if all(v>0 for v in b):continue
  if any(v<0 for v in b) or depth>=MAX_DEPTH:return False
  mid=(lo+hi)/2; stack.extend(((lo,mid,depth+1),(mid,hi,depth+1)))
 return True
def factor_value_table(xs):
 with np.load(gate.FACTOR_CENSUS,allow_pickle=False) as source:
  offsets=np.asarray(source["factor_offset"],dtype=np.int64)
  exponents=np.asarray(source["factor_exponent"],dtype=np.uint8)
  coefficients=np.asarray(source["factor_coefficient"],dtype=np.float64)
 unique,inverse=np.unique(exponents,axis=0,return_inverse=True)
 mono=np.ones((len(unique),len(xs)),dtype=np.float64)
 for variable in range(9):
  power=unique[:,variable]
  if np.any(power): mono*=xs[:,variable][None,:]**power[:,None]
 rows=np.repeat(np.arange(len(offsets)-1),np.diff(offsets))
 matrix=csr_matrix((coefficients,(rows,inverse)),shape=(len(offsets)-1,len(unique)))
 return np.asarray(matrix@mono)

def main():
 records=[json.loads(line) for line in CATALOG.read_text().splitlines() if line]
 parents,_=gate.parent_polynomials(records[2599])
 with np.load(gate.POINT_BANK,allow_pickle=False) as source:mats=np.asarray(source['chart_matrix'],dtype=np.int64)
 points=tuple(gate.normalized_values(m.tolist()) for m in mats); xs=np.asarray([[float(v) for v in p] for p in points])
 if len(points)!=178 or len(EDGES)!=105 or len(set(EDGES))!=105:raise AssertionError('seed census changed')
 for ei,(i,j) in enumerate(EDGES):
  for _label,target,poly,_terms in parents:
   if not positive_unit([target*c for c in segment_power(poly,points[i],points[j])]):raise AssertionError(f'parent-safe edge {ei} failed')
 cands=gate.parse_candidates();_,_,polys=labeled.factor_polynomials(); all_values=factor_value_table(xs); crossed=0; open_ids=[]
 for fid in cands:
  poly=polys[fid]; vals=all_values[fid]; witness=None
  for i,j in EDGES:
   if vals[i]*vals[j]<0:
    left=evaluator.evaluate(poly,points[i]); right=evaluator.evaluate(poly,points[j])
    if left*right<0:witness=(i,j);break
  if witness is None:open_ids.append(fid)
  else:crossed+=1
 digest=hashlib.sha256(','.join(map(str,open_ids)).encode('ascii')).hexdigest()
 if crossed!=EXPECTED_CROSSED or len(open_ids)!=EXPECTED_OPEN or digest!=EXPECTED_OPEN_SHA256:raise AssertionError((crossed,len(open_ids),digest))
 print('PASS',len(EDGES),'exact parent-safe interior segments')
 print('PASS',crossed,'candidate residual walls have exact interior crossings')
 print('OPEN',len(open_ids),'candidate factors retained without emptiness/nonemptiness claim')
 print('OPEN_SHA256',digest)
 print('SCOPE exact nonemptiness certificate only; diagonal three remains open')
if __name__=='__main__':main()
