#!/usr/bin/env python3
"""Exact arithmetic for the registered one-parameter label-8 follow-through."""
from pathlib import Path
from fractions import Fraction as Q
from itertools import combinations,permutations
import json
ROOT=Path(__file__).resolve().parents[3];OWN=Path(__file__).resolve().parent
TRIPLES=sorted(combinations(range(8),3),key=lambda b:b[::-1]);BASES=sorted(combinations(range(8),4),key=lambda b:b[::-1])
SOURCE='ops/team/ai-d3-shared-pencil-falsifier/upper_chart_0_flow.json'
src=json.loads((ROOT/SOURCE).read_text());P=src['parent'];SIGS=src['signatures']
def trim(p):
 p=list(map(Q,p))
 while len(p)>1 and not p[-1]:p.pop()
 return p

def add(a,b):return trim([(a[i] if i<len(a) else 0)+(b[i] if i<len(b) else 0) for i in range(max(len(a),len(b)))])
def neg(a):return [-x for x in a]
def sub(a,b):return add(a,neg(b))
def mul(a,b):
 c=[Q(0)]*(len(a)+len(b)-1)
 for i,x in enumerate(a):
  for j,y in enumerate(b):c[i+j]+=x*y
 return trim(c)
def scale(a,x):return trim([x*y for y in a])
def val(p,x):
 z=Q(0)
 for c in p[::-1]:z=z*x+c
 return z

def det(a):
 ans=[Q(0)];n=len(a)
 for perm in permutations(range(n)):
  term=[Q((-1)**sum(perm[i]>perm[j] for i in range(n) for j in range(i+1,n)))]
  for i,j in enumerate(perm):term=mul(term,a[i][j])
  ans=add(ans,term)
 return ans

def normals(axis=0):
 a=[[[Q(x),Q(int(i==axis and j==7))] for j,x in enumerate(r)] for i,r in enumerate(P)]
 return [[scale(det([[a[k][j] for j in t] for k in range(4) if k!=r]),(-1)**(r+3)) for r in range(4)] for t in TRIPLES]

def signed(ns,sig,sp):return [[scale(p,1 if sig>>i&1 else -1) for p in ns[i]] for i in sp]
def cofactors(a):return [scale(det(a[:j]+a[j+1:]),(-1)**j) for j in range(5)]

def dump(p):return [str(x) for x in p]
if __name__=='__main__':
 import numpy as np
 ns=normals();data=json.loads((OWN/'DISCOVERY.json').read_text());rs=data['coordinate_chords'][0]['records'];seen=[set() for _ in SIGS]
 for rec in rs:
  if rec['state']=='BBB':
   for i,sp in enumerate(rec['dual_supports']):
    if len(sp)==5:seen[i].add(tuple(sp))
 for i in range(3):
  print('BLOCK',i)
  for sp in sorted(seen[i]):
   cs=cofactors(signed(ns,SIGS[i],sp));print('support',sp,'labels',[TRIPLES[j] for j in sp])
   for p in cs:
    roots=np.polynomial.polynomial.polyroots([float(x) for x in p]);print('poly',dump(p),'roots',roots.tolist())
 for i,sp in [(0,[19,21,37,38]),(1,[9,11,27,30])]:
  d=det(signed(ns,SIGS[i],sp));print('GOOD_BASIS',i,sp,dump(d),'roots',np.polynomial.polynomial.polyroots([float(x) for x in d]).tolist())
