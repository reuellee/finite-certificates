#!/usr/bin/env python3
"""Frozen exact rational replay; stdlib only, no discovery/producer imports."""
import ast
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations
import json
from math import gcd
from pathlib import Path
import struct
from time import perf_counter
import zipfile
ROOT=Path(__file__).resolve().parents[3]
OWN=Path(__file__).resolve().parent
TRIPLES=sorted(combinations(range(1,9),3),key=lambda b:b[::-1])
BASES=sorted(combinations(range(1,9),4),key=lambda b:b[::-1])
SIGS=[14988895318912,3405195891438080,40418075143643136]
SUPPORTS=[(0,19,21,37,38),(0,9,27,30,35),(0,11,17,24,40)]
ROOT_PARAMETER=Q(37864449186859942661765893,7029591949415530407677535)
EPSILON=Q(1,1000000)
PINS=json.loads((OWN/'SOURCE_MANIFEST.json').read_text())['source_sha256']
def require(condition,message):
 if not condition:raise AssertionError(message)
def det(matrix):
 a=[list(map(Q,row)) for row in matrix];ans=Q(1)
 for c in range(len(a)):
  p=next((r for r in range(c,len(a)) if a[r][c]),None)
  if p is None:return Q(0)
  if p!=c:a[c],a[p]=a[p],a[c];ans=-ans
  pivot=a[c][c];ans*=pivot
  for r in range(c+1,len(a)):
   ratio=a[r][c]/pivot
   for j in range(c+1,len(a)):a[r][j]-=ratio*a[c][j]
 return ans
def rank(matrix):
 a=[list(map(Q,row)) for row in matrix];r=0
 for c in range(len(a[0])):
  p=next((j for j in range(r,len(a)) if a[j][c]),None)
  if p is None:continue
  a[r],a[p]=a[p],a[r];pivot=a[r][c]
  a[r]=[v/pivot for v in a[r]]
  for j in range(len(a)):
   if j!=r:
    ratio=a[j][c];a[j]=[x-ratio*y for x,y in zip(a[j],a[r])]
  r+=1
  if r==len(a):break
 return r
def brackets(y):return [det([[y[r][j-1] for j in b] for r in range(4)]) for b in BASES]
def normals(y,primitive=False):
 out=[]
 for t in TRIPLES:
  v=[(-1)**(r+3)*det([[y[k][j-1] for j in t] for k in range(4) if k!=r]) for r in range(4)]
  if primitive:
   require(all(x.denominator==1 for x in v),'integer primitive gauge')
   scale=gcd(*(int(x) for x in v));v=[x/scale for x in v]
  out.append(v)
 return out
def signed(n,sig,sp):return [[(1 if sig>>i&1 else -1)*x for x in n[i]] for i in sp]
def cofactors(n,sig,sp):
 a=signed(n,sig,sp)
 return [(-1)**j*det(a[:j]+a[j+1:]) for j in range(5)]
def validate_dual(n,sig,sp,weights,strict=True):
 require(len(sp)==len(weights) and len(set(sp))==len(sp),'dual support')
 require(all(w>0 if strict else w>=0 for w in weights) and any(weights),'dual positivity')
 a=signed(n,sig,sp)
 require(all(sum(w*row[j] for w,row in zip(weights,a))==0 for j in range(4)),'Gordan equality')
def normalize(c):
 require(sum(c)!=0,'normalization nonzero');return [v/sum(c) for v in c]
def npy(z,name):
 b=z.read(name+'.npy');require(b[:6]==b'\x93NUMPY','NPY magic')
 off=10 if b[6]==1 else 12;hsize=struct.unpack('<H' if off==10 else '<I',b[8:off])[0]
 h=ast.literal_eval(b[off:off+hsize].decode());require(not h['fortran_order'],'NPY ordering')
 code={'<i8':'q','<u2':'H'}[h['descr']];width=struct.calcsize(code);raw=b[off+hsize:]
 return h['shape'],struct.unpack('<'+code*(len(raw)//width),raw)
def gp(parent_signs,sig):
 ps=dict(zip(BASES,parent_signs));ti={t:i for i,t in enumerate(TRIPLES)}
 def chi(seq):
  b=tuple(sorted(seq));v=(1 if sig>>ti[b[:3]]&1 else -1) if b[-1]==9 else ps[b]
  return (-1)**sum(seq[i]>seq[j] for i in range(4) for j in range(i+1,4))*v
 count=0
 for lam in combinations(range(1,10),2):
  for a,b,c,d in combinations([i for i in range(1,10) if i not in lam],4):
   vals=[chi(lam+(a,b))*chi(lam+(c,d)),-chi(lam+(a,c))*chi(lam+(b,d)),chi(lam+(a,d))*chi(lam+(b,c))]
   require(len(set(vals))==2,'extension GP');count+=1
 return count
def verify():
 start=perf_counter()
 for path,digest in PINS.items():require(sha256((ROOT/path).read_bytes()).hexdigest()==digest,'source hash '+path)
 source=json.loads((ROOT/'ops/team/ai-d3-shared-pencil-falsifier/upper_chart_0_flow.json').read_text())
 parent=source['parent'];require(source['signatures']==SIGS,'source labels')
 anchors=json.loads((ROOT/'ops/team/ai-d3-shared-pencil-falsifier/admissibility_flow.json').read_text())['records']
 with zipfile.ZipFile(ROOT/'ai/omreal/data/seeat_parent2599_upper178.npz') as z:
  shape,matrices=npy(z,'chart_matrix');ashape,assignment=npy(z,'assignment');pshape,points=npy(z,'point')
 require(shape==(178,4,8),'source bank shape')
 def chart(i):return [list(matrices[32*i+8*r:32*i+8*r+8]) for r in range(4)]
 require(parent==chart(0),'actual source chart 0')
 b0=brackets(parent);sg=[1 if v>0 else -1 for v in b0]
 require(all(b0),'source uniform')
 require(sg==source['parent_signs'],'source chirotope')
 for index,anchor in enumerate(anchors):
  require(anchor['signature']==SIGS[index],'anchor signature')
  ap=anchor['parent'];ai=anchor['upper_point_index'];ci=anchor['upper_chart_index']
  require(ap==chart(ci) and assignment[ai]==ci,'anchor bank binding')
  require(anchor['point']==list(points[4*ai:4*ai+4]),'anchor point binding')
  require([1 if v>0 else -1 if v<0 else 0 for v in brackets(ap)]==sg,'anchor parent signs')
  an=normals(ap,primitive=True)
  require(all(sum(x*y for x,y in zip(row,anchor['point']))>0 for row in signed(an,SIGS[index],range(56))),'anchor primal')
  for j,system in enumerate(anchor['other_systems']):
   require(system['signature']==SIGS[j],'dual anchor labels')
   if index!=j:validate_dual(an,SIGS[j],system['dual']['support'],system['dual']['weights'])
 checks=sum(gp(sg,sig) for sig in SIGS);require(checks==3780,'GP denominator')
 def moved(t):
  y=deepcopy(parent);y[1][1]+=t;return y
 rootparent=moved(ROOT_PARAMETER);rn=normals(rootparent);rb=brackets(rootparent)
 require(all(v*s>0 for v,s in zip(rb,sg)),'event retains every parent sign')
 weights=[normalize(cofactors(rn,sig,sp)) for sig,sp in zip(SIGS,SUPPORTS)]
 for block in range(3):validate_dual(rn,SIGS[block],SUPPORTS[block],weights[block],strict=block!=0)
 require(weights[0][0]==0 and all(v>0 for v in weights[0][1:]),'exact single zero weight')
 eventrows=signed(rn,SIGS[0],SUPPORTS[0]);require(rank(eventrows)==4,'five-support rank')
 require(rank(eventrows[1:])==3,'surviving four-support rank')
 require(rank([row+[Q(1)] for row in eventrows])==5,'augmented support rank')
 # The special cofactor is affine: its four underlying normals exclude label 2
 # except n238, so multilinearity bounds its degree by one, independent of interpolation.
 special=SUPPORTS[0][1:]
 require(sum(2 in TRIPLES[i] for i in special)==1,'linear cofactor incidence')
 c0=cofactors(normals(parent),SIGS[0],SUPPORTS[0])[0]
 c1=cofactors(normals(moved(Q(1))),SIGS[0],SUPPORTS[0])[0]-c0
 require(c0==-1590306865848117591794167506 and c1==295242861875452277122456470,'explicit failure polynomial')
 require(c0+c1*ROOT_PARAMETER==0 and c1!=0,'simple support event')
 side_records=[]
 for name,t in [('left',ROOT_PARAMETER-EPSILON),('right',ROOT_PARAMETER+EPSILON)]:
  y=moved(t);n=normals(y);b=brackets(y)
  require(all(v*s>0 for v,s in zip(b,sg)),'strict adjacent parent endpoint')
  cs=[normalize(cofactors(n,sig,sp)) for sig,sp in zip(SIGS,SUPPORTS)]
  for block in [1,2]:validate_dual(n,SIGS[block],SUPPORTS[block],cs[block])
  side_records.append({'side':name,'parameter':str(t),'selected_weight_signs':[1 if v>0 else -1 if v<0 else 0 for v in cs[0]],'blocks_1_and_2_bad':True,'block_0_bad_via_selected_support':all(v>0 for v in cs[0])})
 require(side_records[0]['selected_weight_signs']==[1]*5,'selected support positive on left')
 require(side_records[1]['selected_weight_signs']==[-1,1,1,1,1],'selected support absent on right')
 # Parent brackets are affine in one moving coordinate. Strict endpoints prove
 # the entire interval is in the same parent chamber, including original t=0.
 controls={}
 bad=list(weights[0]);bad[1]+=1
 try:validate_dual(rn,SIGS[0],SUPPORTS[0],bad,strict=False)
 except AssertionError:controls['corrupted_weight_rejected']=True
 try:validate_dual(rn,SIGS[0]^(1<<SUPPORTS[0][1]),SUPPORTS[0],weights[0],strict=False)
 except AssertionError:controls['supported_signature_flip_rejected']=True
 try:require(c0+c1*(ROOT_PARAMETER+EPSILON)==0,'false event')
 except AssertionError:controls['shifted_event_parameter_rejected']=True
 try:require(any(v==0 for v in rb),'claimed parent infinity')
 except AssertionError:controls['parent_infinity_relabel_rejected']=True
 require(len(controls)==4,'hostile controls complete')
 result={'status':'EXACT_ORIGINAL_SOURCE_SUPPORT_EVENT','original_pair_target':'NULL','theorem_credit':0,'ledger':'2/9','base_revision':'3a7ce7b5d57543d54eace7707659418cea6d69c9','source_sha256':PINS,'moved_parent':[[str(v) for v in row] for row in rootparent],'coordinate_move':{'row_zero_based':1,'column_label':2,'parameter':str(ROOT_PARAMETER)},'signatures':SIGS,'supports':[list(sp) for sp in SUPPORTS],'support_labels':[[''.join(map(str,TRIPLES[i])) for i in sp] for sp in SUPPORTS],'normalized_weights':[[str(v) for v in w] for w in weights],'selected_cofactor_polynomial':[str(c0),str(c1)],'all_parent_brackets_nonzero':True,'parent_brackets':[str(v) for v in rb],'parent_chirotope_unchanged':True,'proper_incomparable_anchor_charts':[a['upper_chart_index'] for a in anchors],'ordered_noninclusions_verified':6,'gp_sign_relations_verified':checks,'five_support_rank':4,'surviving_four_support_rank':3,'augmented_five_support_rank':5,'adjacent_checks':side_records,'hostile_controls':controls,'elapsed_seconds':round(perf_counter()-start,4)}
 frozen=json.loads((OWN/'EXACT_REPLAY.json').read_text())
 semantic=lambda record:{key:value for key,value in record.items() if key!='elapsed_seconds'}
 require(semantic(result)==semantic(frozen),'frozen exact replay semantic fields')
 print(json.dumps({k:result[k] for k in ['status','original_pair_target','theorem_credit','all_parent_brackets_nonzero','five_support_rank','surviving_four_support_rank','elapsed_seconds']}))
if __name__=='__main__':verify()
