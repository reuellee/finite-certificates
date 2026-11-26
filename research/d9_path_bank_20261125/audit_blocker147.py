#!/usr/bin/env python3
"""Independently check one common signature is lost by all 147 paths.
Prerequisite: separately replay exact parent-safety certificates for stored routes and both coordinate paths.
"""
import argparse, hashlib, json
from pathlib import Path
from itertools import combinations
from math import gcd,lcm
import numpy as np
p=argparse.ArgumentParser()
for name in ('source','old-path','new-path','two-path','three-path','four-path','routes','label-gate','candidate','proof'): p.add_argument('--'+name,required=True,type=Path)
p.add_argument('--tamper',choices=['stored','old','new','two','three','four','endpoint','routes'])
a=p.parse_args()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(a.source)=='3b90799d26b7783e92c2ac697eaaf8b76d26a787f53205873b997657e114180a'
assert sha(a.old_path)=='8db38e00d9bf8701558c27cd4ede3e024db8953ea3ef9873bf0b4fc65ad6bcda'
assert sha(a.new_path)=='ac86b2ac7d1af5f92e34fa7e71309a8a7e70521c7080b4a9f62f72e03fe8e549'
assert sha(a.two_path)=='05a4c2c8991d4a10d86ae7353d09f6d495c0ab0a52b3467a3deb7634b6dbca60'
assert sha(a.three_path)=='52f0b08bb831656417417301e61972b196eddd8b9134b8a4206b1b547a1aea9f'
assert sha(a.four_path)=='c4a76f25ae2b181805fd9a9012fe1ea1c3344f9fde856ff11da8791f3b18eec5'
assert sha(a.routes)=='2da699d3925ed12f1e70b45baa7da591e2a266c6d5ddc4fd76e5b2f7ec854c51'
C=json.loads(a.proof.read_text());candidate=json.loads(a.candidate.read_text());routes=json.loads(a.routes.read_text())['12_37'];gated=json.loads(a.label_gate.read_text())['12_37']['paths']
assert C['signature']==candidate['signature']==1228857710465867
if a.tamper=='stored': C['stored_bad'][next(iter(C['stored_bad']))]['weights'][0]+=1
if a.tamper=='old': C['snapshot_bad']['weights'][0]+=1
if a.tamper=='new': C['new_path_bad']['weights'][0]+=1
if a.tamper=='two': C['two_path_bad']['weights'][0]+=1
if a.tamper=='three': C['three_path_bad']['weights'][0]+=1
if a.tamper=='four': C['four_path_bad']['weights'][0]+=1
if a.tamper=='endpoint': C['endpoint_rays']['12']=[0,0,0,0]
if a.tamper=='routes': candidate['routes'].pop()
assert len(routes)==len(gated)==len(candidate['routes'])==142
assert len(set(map(tuple,routes)))==142 and set(map(tuple,routes))==set(map(tuple,gated))==set(map(tuple,candidate['routes']))
assert all(len(r)==4 and r[0]==12 and r[-1]==37 and r[1]!=r[2] and all(v not in (12,37) for v in r[1:3]) for r in routes)
S=np.load(a.source,allow_pickle=False)['chart_matrix'];old=np.load(a.old_path,allow_pickle=False);new=np.load(a.new_path,allow_pickle=False);two=np.load(a.two_path,allow_pickle=False);three=np.load(a.three_path,allow_pickle=False);four=np.load(a.four_path,allow_pickle=False)
assert tuple(map(int,old['endpoint']))==(12,37) and tuple(map(int,new['endpoint']))==tuple(map(int,two['endpoint']))==tuple(map(int,three['endpoint']))==tuple(map(int,four['endpoint']))==(12,37)
triples=sorted(combinations(range(8),3),key=lambda q:q[::-1]); sig=C['signature']
def det3(a,b,c):return a[0]*(b[1]*c[2]-b[2]*c[1])-a[1]*(b[0]*c[2]-b[2]*c[0])+a[2]*(b[0]*c[1]-b[1]*c[0])
def normals(Y):
 cols=[[int(Y[r,c]) for r in range(4)] for c in range(8)];out=[]
 for bit,q in enumerate(triples):
  row=[(-1)**(k+3)*det3(*[[cols[j][i] for i in range(4) if i!=k] for j in q]) for k in range(4)]
  out.append([x*(1 if sig>>bit&1 else -1) for x in row])
 return out
def check_ray(Y,ray):
 assert len(ray)==4 and all(type(x) is int for x in ray)
 assert all(sum(x*y for x,y in zip(row,ray))>0 for row in normals(Y))
def check_infeasible(Y,cert):
 rows=normals(Y); I=cert['indices'];w=cert['weights'];assert 1<=len(I)==len(w)==len(set(I))<=5
 assert all(type(i) is int and 0<=i<56 for i in I) and all(type(x) is int and x>0 for x in w)
 div=[gcd(*rows[i]) for i in I];assert all(div);L=lcm(*div); weights=[x*(L//g) for x,g in zip(w,div)]
 assert all(sum(rows[i][j]*t for i,t in zip(I,weights))==0 for j in range(4))
for idx in (12,37):check_ray(S[idx],C['endpoint_rays'][str(idx)])
stored=C['stored_bad'];assert len(stored)==15
for k,c in stored.items(): assert k.isdecimal() and 0<=int(k)<178;check_infeasible(S[int(k)],c)
assert all(any(str(v) in stored for v in r[1:3]) for r in routes)
def check_snapshot(path,cert):
 side=cert['side'];step=cert['step'];assert side in ('a','b') and type(step) is int and step>0
 Y=S[12 if side=='a' else 37].astype(object); found=False
 for n,(col,vec) in enumerate(zip(path['update_col_'+side],path['update_vec_'+side]),1):
  col=int(col)
  if col<8:Y[:,col]=[int(q) for q in vec]
  if n==step:found=True;break
 assert found;check_infeasible(Y,cert)
assert (C['snapshot_bad']['side'],C['snapshot_bad']['step'])==('a',2000)
assert (C['new_path_bad']['side'],C['new_path_bad']['step'])==('a',170)
assert (C['two_path_bad']['side'],C['two_path_bad']['step'])==('a',200)
assert (C['three_path_bad']['side'],C['three_path_bad']['step'])==('b',1600)
assert (C['four_path_bad']['side'],C['four_path_bad']['step'])==('a',600)
check_snapshot(old,C['snapshot_bad']);check_snapshot(new,C['new_path_bad']);check_snapshot(two,C['two_path_bad']);check_snapshot(three,C['three_path_bad']);check_snapshot(four,C['four_path_bad'])
print('PASS endpoint rays and 15 stored-chart exact Gordan certificates hitting all 142 source-matched routes')
print('PASS old-path loss',C['snapshot_bad']['side'],C['snapshot_bad']['step'],'new-path loss',C['new_path_bad']['side'],C['new_path_bad']['step'],'two-path loss',C['two_path_bad']['side'],C['two_path_bad']['step'],'three-path loss',C['three_path_bad']['side'],C['three_path_bad']['step'],'and four-path loss',C['four_path_bad']['side'],C['four_path_bad']['step'])
print('SCOPE: packing upper bound 1 for these 147 paths; path safety depends on separately replayed path and bank verifiers')
