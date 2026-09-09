#!/usr/bin/env python3
"""Bounded actual-parent search. Float screening chooses work; exact arithmetic accepts."""
from pathlib import Path
from itertools import combinations
from fractions import Fraction as Q
from math import gcd,lcm
from functools import reduce
import argparse,hashlib,json,time
import numpy as np

HERE=Path(__file__).resolve().parent
SOURCE=HERE.parent/'source'
TRIPLES=sorted(combinations(range(8),3),key=lambda x:x[::-1])
BASES=sorted(combinations(range(8),4),key=lambda x:x[::-1])
TIDX={x:i for i,x in enumerate(TRIPLES)}

def det(a):
 n=len(a)
 if n==0:return 1
 if n==1:return a[0][0]
 if n==2:return a[0][0]*a[1][1]-a[0][1]*a[1][0]
 return sum((-1)**j*a[0][j]*det([r[:j]+r[j+1:] for r in a[1:]]) for j in range(n))

def normal(y,t):
 return [(-1)**(r+3)*det([[y[k][j] for j in t] for k in range(4) if k!=r]) for r in range(4)]

def normalize(c):
 d=lcm(*(x.denominator if isinstance(x,Q) else 1 for x in c))
 z=[int(x*d) for x in c];g=reduce(gcd,(abs(x) for x in z),0)
 if not g:return z
 z=[x//g for x in z]
 if next(x for x in z if x)!=abs(next(x for x in z if x)):z=[-x for x in z]
 return z

def sign(x):return int(x>0)-int(x<0)

def matchings(xs):
 if not xs:yield ();return
 a=xs[0]
 for i,b in enumerate(xs[1:],1):
  for rest in matchings(xs[1:i]+xs[i+1:]):yield ((a,b),)+rest

def supports():
 records=[]
 for common in range(8):
  for omitted in range(8):
   if omitted==common:continue
   others=tuple(x for x in range(8) if x not in (common,omitted))
   for pairs in matchings(others):
    ts=sorted(tuple(sorted((common,)+pair)) for pair in pairs)
    records.append(dict(common=common,omitted=omitted,triples=ts,indices=[TIDX[t] for t in ts]))
 assert len(records)==840 and len({tuple(r['indices']) for r in records})==840
 return records

def screen(charts,recs,sigs):
 idx=np.array([r['indices'] for r in recs]);pol=np.array([[1 if s>>j&1 else -1 for j in range(56)] for s in sigs])
 result=[];t0=time.perf_counter()
 for ci,yi in enumerate(charts):
  y=yi.astype(float);ns=np.array([normal(y.tolist(),t) for t in TRIPLES])
  ns/=np.linalg.norm(ns,axis=1)[:,None]
  u,sv,_=np.linalg.svd(ns[idx],full_matrices=False)
  for si,sig in enumerate(sigs):
   v=u[:,:,-1]*pol[si,idx]
   aligned=np.all(v>1e-8,axis=1)|np.all(v < -1e-8,axis=1)
   for ri in np.flatnonzero(aligned):
    result.append((float(sv[ri,2]/sv[ri,1]),ci,int(ri),si))
 result.sort();return result,time.perf_counter()-t0

def one_solve(chart,rec,sig):
 y=[[int(x) for x in row] for row in chart];common=rec['common'];ts=rec['triples']
 drop=max(range(4),key=lambda r:abs(y[r][common]));cols=[r for r in range(4) if r!=drop]
 ns=[normal(y,t) for t in ts]
 f0=det([[n[c] for c in cols] for n in ns])
 # Select largest coordinate derivative without solving a root yet.
 candidates=[]
 for k,t in enumerate(ts):
  for label in t:
   if label==common:continue
   for coord in range(4):
    y[coord][label]+=1;n=normal(y,t);y[coord][label]-=1
    rows=ns[:];rows[k]=n
    d=det([[v[c] for c in cols] for v in rows])-f0
    if d:candidates.append((abs(d),coord,label,k,d))
 if not candidates:return dict(status='NO_AFFINE_DIRECTION')
 _,coord,label,k,d=max(candidates)
 delta=-Q(f0,d);y[coord][label]=Q(y[coord][label])+delta
 brackets=[det([[y[r][j] for j in b] for r in range(4)]) for b in BASES]
 ns=[normal(y,t) for t in ts]
 signed=[[x*(1 if sig>>idx&1 else -1) for x in n] for idx,n in zip(rec['indices'],ns)]
 failures=[i for i,(v,s) in enumerate(zip(brackets,TARGET_SIGNS)) if sign(v)!=s]
 rank3minors=[det([[row[c] for c in cc] for row in signed]) for cc in combinations(range(4),3)]
 assert not any(rank3minors),'affine wall failed exact rank <=2'
 weights=None
 for cc in combinations(range(4),2):
  cs=[(-1)**i*det([[row[c] for c in cc] for j,row in enumerate(signed) if j!=i]) for i in range(3)]
  if any(cs):weights=normalize(cs);break
 assert weights and all(sum(weights[i]*signed[i][j] for i in range(3))==0 for j in range(4))
 positive=all(x>0 for x in weights)
 return dict(status='EXACT_POSITIVE_CIRCUIT' if not failures and positive else 'PARENT_SIGN_FAILURE' if failures else 'WEIGHTS_NOT_POSITIVE',parent=[[str(x) for x in row] for row in y],coordinate=[coord,label],delta=str(delta),parent_sign_failures=failures,parent_signs=[sign(x) for x in brackets],rank=2,weights=weights,positive=positive,signed_normals=[[str(x) for x in row] for row in signed],wall_minor_columns=cols)

def main():
 global TARGET_SIGNS
 ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int,default=128);args=ap.parse_args()
 assert 0<args.limit<=128
 start=time.perf_counter();flow=json.loads((SOURCE/'FLOW.json').read_text());TARGET_SIGNS=flow['parent_signs'];sigs=flow['signatures']
 z=np.load(SOURCE/'parent_bank.npz',allow_pickle=False);charts=z['chart_matrix']
 assert charts.shape==(178,4,8) and charts[0].tolist()==flow['parent'] and int(z['parent_index'])==2599
 recs=supports();candidates,elapsed=screen(charts,recs,sigs)
 # One candidate per chart/support. Try best aligned source signature first.
 seen=set();chosen=[]
 for cand in candidates:
  _,ci,ri,si=cand
  if (ci,ri) in seen:continue
  seen.add((ci,ri));chosen.append(cand)
  if len(chosen)==args.limit:break
 attempts=[];witnesses=[]
 for serial,(ratio,ci,ri,si) in enumerate(chosen):
  rec=recs[ri];result=one_solve(charts[ci],rec,sigs[si]);result.update(attempt=serial,chart_index=ci,support_index=ri,signature_index=si,signature=sigs[si],support=rec,screening_singular_ratio=ratio)
  attempts.append(result)
  if result['status']=='EXACT_POSITIVE_CIRCUIT':witnesses.append(result)
 counts={s:sum(r['status']==s for r in attempts) for s in sorted({r['status'] for r in attempts})}
 output=dict(classification='LOCAL_CERTIFICATES_ONLY' if witnesses else 'BOUNDED_NULL',source_sha256={f:hashlib.sha256((SOURCE/f).read_bytes()).hexdigest() for f in ['FLOW.json','parent_bank.npz','verify_derived_wall_sides.py']},source_chart_count=178,star_support_count=840,screened_unsigned_matrices=178*840,screened_signature_tests=178*840*3,numerically_aligned_count=len(candidates),targeted_exact_wall_solves=len(attempts),max_wall_solves=args.limit,selection='increasing sigma_3/sigma_2 among approximate fixed-sign positive left singular vectors; unique chart/support; strongest one-coordinate wall derivative',counts=counts,screening_seconds=elapsed,total_seconds=time.perf_counter()-start,witnesses=witnesses,attempts=attempts,theorem_credit=0,original_injectivity='OPEN',original_ledger='2/9',coverage='NONE: no exhaustion of the continuous parent space')
 (HERE/'SEARCH_RESULT.json').write_text(json.dumps(output,indent=2)+'\n')
 print(json.dumps({k:v for k,v in output.items() if k not in ('attempts','witnesses','source_sha256')},indent=2))

if __name__=='__main__':main()
