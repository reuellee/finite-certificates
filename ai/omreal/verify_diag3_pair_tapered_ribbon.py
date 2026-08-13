#!/usr/bin/env python3
"""Exact cellular replay of the scoped diagonal-three tapered ribbon."""

from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path

import numpy as np
from scipy.sparse import bmat, coo_matrix, csr_matrix, hstack

HERE = Path(__file__).resolve().parent
DATA = HERE / "data/DIAG3_pair_tapered_ribbon.json"
EXPECTED_DATA_SHA256 = "7e32badfcdf200fa3bb284db1502c8435bc7732bc973e4e55aa894c81372763f"

RAYS=((0,'negative'),(0,'positive'),(1,'negative'),(1,'positive'))
QUAD={
 ((0,'negative'),1):'c0', ((1,'positive'),1):'c0',
 ((0,'positive'),1):'c1', ((1,'positive'),0):'c1',
 ((0,'positive'),0):'c2', ((1,'negative'),0):'c2',
 ((0,'negative'),0):'c3', ((1,'negative'),1):'c3',
}

def bor(rows):
 rows=tuple(rows)
 return tuple(any(x[i] for x in rows) for i in range(3))

def load():
 raw=DATA.read_bytes()
 if hashlib.sha256(raw).hexdigest()!=EXPECTED_DATA_SHA256:
  raise AssertionError('tapered-ribbon data digest changed')
 packed=json.loads(raw)
 if packed.get('schema')!='diag3-pair-ribbon-compact-v1':
  raise AssertionError('bad tapered-ribbon schema')
 side={}
 for key in RAYS:
  row=packed['rays'][f'{key[0]}_{key[1]}']
  side[key]=(row['orientation'],tuple(map(tuple,row['root_factors'])),
             tuple(map(tuple,row['wall'])),
             tuple(tuple(map(tuple,x)) for x in row['side_rows']))
 multi={}
 for key in RAYS:
  rows=[]
  for row in packed['multi'][f'{key[0]}_{key[1]}']:
   got=tuple((tuple(x[0]),tuple(map(tuple,x[1]))) for x in row['orders'])
   rows.append((row['root_index'],tuple(row['factors']),got))
  multi[key]=tuple(rows)
 return side,multi

def rank2(A):
 A=A.tocsr();piv={};rank=0
 for i in range(A.shape[0]):
  row=0
  for j,v in zip(A.indices[A.indptr[i]:A.indptr[i+1]],A.data[A.indptr[i]:A.indptr[i+1]]):
   if int(v)&1:row^=1<<int(j)
  while row:
   c=row.bit_length()-1
   if c in piv:row^=piv[c]
   else:piv[c]=row;rank+=1;break
 return rank

def make_sparse(rows,cols,entries):
 if not entries:return csr_matrix((rows,cols),dtype=np.int64)
 rr,cc,vv=zip(*entries)
 return coo_matrix((vv,(rr,cc)),shape=(rows,cols),dtype=np.int64).tocsr()

def build():
 side,multis=load();multimap={key:{x[0]:x for x in rows} for key,rows in multis.items()}
 vertices=[('node',)];vid={('node',):0}
 edges=[];ed0=[];faces=[];fid={};face_status=[];face_boundary=defaultdict(dict)
 def vertex(name):
  if name not in vid:vid[name]=len(vertices);vertices.append(name)
  return vid[name]
 def face(name,status):
  if name in fid:
   if face_status[fid[name]]!=status:raise AssertionError(('face status mismatch',name,face_status[fid[name]],status))
   return fid[name]
  fid[name]=len(faces);faces.append(name);face_status.append(status);return fid[name]
 def fkey(key,zi,slot):return ('core',QUAD[(key,zi)]) if slot==0 else ('arm',key,zi,slot)
 def edge(name,boundary):
  i=len(edges);edges.append(name);ed0.append(dict(boundary));return i
 def incidence(fi,ei,value):
  old=face_boundary[fi].get(ei,0);face_boundary[fi][ei]=old+value

 for key in RAYS:
  orient,roots,wall,side_rows=side[key]
  # Make the ordered sector/status sequence independently on both q sides.
  sequences=[];orders=[]
  for zi in (0,1):
   seq=[side_rows[0][zi]];order=[]
   for gi,root in enumerate(roots):
    factors=root
    if len(factors)==1:
     local_order=factors;local_seq=(side_rows[gi][zi],side_rows[gi+1][zi])
    else:
     _idx,_fs,got=multimap[key][gi]
     local_order,local_seq=got[zi]
    if seq[-1]!=local_seq[0]:raise AssertionError(('sector left mismatch',key,gi,zi))
    order.extend(local_order);seq.extend(local_seq[1:])
   if len(seq)!=sum(map(len,roots))+1:raise AssertionError('wrong face sequence')
   sequences.append(tuple(seq));orders.append(tuple(order))
   for slot,status in enumerate(seq):face(fkey(key,zi,slot),status)

  # Root vertices and defining-wall segments.
  root_vertices=[vertex(('root',key,gi)) for gi in range(len(roots))]
  cumulative=[0]
  for r in roots:cumulative.append(cumulative[-1]+len(r))
  for seg in range(len(roots)+1):
   source=vid[('node',)] if seg==0 else root_vertices[seg-1]
   target=None if seg==len(roots) else root_vertices[seg]
   b={source:-1}
   if target is not None:b[target]=b.get(target,0)+1
   ei=edge(('q',key,seg),b)
   for zi,local_sign in ((0,-1),(1,1)):
    fi=fid[fkey(key,zi,cumulative[seg])]
    incidence(fi,ei,orient*local_sign)

  # Every factor curve is split at q into lower and upper half-edges.
  for zi in (0,1):
   position=0
   for gi,root in enumerate(roots):
    factors=root
    local_order=(factors if len(factors)==1 else multimap[key][gi][2][zi][0])
    v=root_vertices[gi]
    for factor in local_order:
     boundary={v:(1 if zi==0 else -1)} # lower boundary->v; upper v->boundary
     ei=edge(('p',key,zi,gi,factor),boundary)
     before=fid[fkey(key,zi,position)];after=fid[fkey(key,zi,position+1)]
     incidence(before,ei,orient);incidence(after,ei,-orient)
     position+=1

 V=len(vertices);E=len(edges);F=len(faces)
 d0_entries=[(ei,v,c) for ei,b in enumerate(ed0) for v,c in b.items() if c]
 d1_entries=[(f,e,c) for f,b in face_boundary.items() for e,c in b.items() if c]
 d0=make_sparse(E,V,d0_entries);d1=make_sparse(F,E,d1_entries)
 if (d1@d0).nnz:raise AssertionError('ribbon differential does not square')
 # Lower-cell labels are closures: a bad label on an incident open cell persists.
 edge_faces=[[] for _ in edges]
 for f,b in face_boundary.items():
  for e,c in b.items():
   if c:edge_faces[e].append(f)
 if any(len(x)!=2 for x in edge_faces):raise AssertionError(Counter(map(len,edge_faces)))
 edge_status=[bor(face_status[f] for f in fs) for fs in edge_faces]
 vertex_edges=[[] for _ in vertices]
 for e,b in enumerate(ed0):
  for v,c in b.items():
   if c:vertex_edges[v].append(e)
 vertex_status=[bor(edge_status[e] for e in es) for es in vertex_edges]
 # Check all defining-ray labels against the independent exact wall ledger.
 for e,name in enumerate(edges):
  if name[0]=='q':
   _,key,seg=name
   if edge_status[e]!=side[key][2][seg]:raise AssertionError(('q status mismatch',name,edge_status[e],side[key][2][seg]))
 if vertex_status[0]!=(True,True,True):raise AssertionError('node status')
 if (V,E,F)!=(4547,13734,9188):raise AssertionError('base cell census changed')
 print('BASE',V,E,F,'Euler',V-E+F,'status counts',Counter(face_status),Counter(edge_status),Counter(vertex_status))
 return (vertices,edges,faces),(vertex_status,edge_status,face_status),(d0,d1)

def sub(A,row_ids,col_ids):return A[row_ids,:][:,col_ids]

def matrices(cells,statuses,diffs):
 vertices,edges,faces=cells
 d0,d1=diffs
 T=[];Es={pair:[] for pair in ((0,1),(0,2),(1,2))}
 for dim,sts in enumerate(statuses):
  T.append([i for i,s in enumerate(sts) if all(s)])
  for pair in Es:
   third=3-pair[0]-pair[1]
   Es[pair].append([i for i,s in enumerate(sts) if s[pair[0]] and s[pair[1]] and not s[third]])
 print('STRATA T',tuple(map(len,T)),'E',{p:tuple(map(len,x)) for p,x in Es.items()})
 dT0=sub(d0,T[1],T[0]);dT1=sub(d1,T[2],T[1])
 de0={p:sub(d0,x[1],x[0]) for p,x in Es.items()};de1={p:sub(d1,x[2],x[1]) for p,x in Es.items()}
 b0={p:sub(d0,Es[p][1],T[0]) for p in Es};b1={p:sub(d1,Es[p][2],T[1]) for p in Es}
 print('COH2 T ranks',rank2(dT0),rank2(dT1),'H',len(T[0])-rank2(dT0),len(T[1])-rank2(dT0)-rank2(dT1),len(T[2])-rank2(dT1))
 for p in Es:
  r0,r1=rank2(de0[p]),rank2(de1[p])
  print('COH2 E',p,'ranks',r0,r1,'H',len(Es[p][0])-r0,len(Es[p][1])-r0-r1,len(Es[p][2])-r1)
 # Pin the unique E02 class: the first q0=0,q1>0 edge and the 241
 # upper factor half-edges on q1=0,q0<0 through factor 13063.
 e02_global=Es[(0,2)][1];e02_position={edge:index for index,edge in enumerate(e02_global)}
 support_global=[
  index for index,name in enumerate(edges)
  if name==('q',(0,'negative'),0)
  or (name[0]=='p' and name[1:3]==((1,'negative'),1)
      and statuses[1][index]==(True,False,True))
 ]
 if len(support_global)!=242:raise AssertionError('E02 survivor support changed')
 support=[e02_position[index] for index in support_global]
 restricted=de1[(0,2)][:,support].tocsr()
 row_sizes=np.diff(restricted.indptr)
 if np.count_nonzero(row_sizes)!=241 or set(row_sizes)!={0,2}:
  raise AssertionError('E02 survivor corridor changed')
 coefficients=[None]*len(support);coefficients[0]=1
 adjacency=[[] for _ in support]
 for row in range(restricted.shape[0]):
  begin,end=restricted.indptr[row:row+2]
  if begin==end:continue
  (left,right)=restricted.indices[begin:end]
  (a,b)=map(int,restricted.data[begin:end])
  adjacency[left].append((right,-a//b));adjacency[right].append((left,-b//a))
 stack=[0]
 while stack:
  left=stack.pop()
  for right,scale in adjacency[left]:
   value=coefficients[left]*scale
   if coefficients[right] is None:coefficients[right]=value;stack.append(right)
   elif coefficients[right]!=value:raise AssertionError('inconsistent survivor signs')
 if any(value not in (-1,1) for value in coefficients):
  raise AssertionError('survivor is not a signed unit chain')
 survivor=coo_matrix((coefficients,(support,[0]*len(support))),shape=(len(e02_global),1),dtype=np.int64).tocsr()
 if (de1[(0,2)]@survivor).nnz:raise AssertionError('survivor is not a cocycle')
 if rank2(hstack((de0[(0,2)],survivor)))!=2614:
  raise AssertionError('survivor became a coboundary')
 if edges[support_global[-1]][-1]!=13063:
  raise AssertionError('survivor no longer ends at factor 13063')
 survivor_digest=hashlib.sha256(repr(tuple((edges[g],c) for g,c in zip(support_global,coefficients))).encode('ascii')).hexdigest()
 if survivor_digest!='c0e0d4146b1f8f59c70440267a62e983231150707498d8713d5a372571397063':
  raise AssertionError(f'E02 survivor digest changed: {survivor_digest}')
 print('PASS E02 signed survivor support=242 terminal_factor=13063',survivor_digest)
 z=lambda r,c:csr_matrix((r,c),dtype=np.int64)
 # Block rows/columns are exactly (22)--(23): T,T,E01,E02,E12.
 p01,p02,p12=(0,1),(0,2),(1,2)
 N=bmat([
  [dT0,z(len(T[1]),len(T[0])),z(len(T[1]),len(Es[p01][0])),z(len(T[1]),len(Es[p02][0])),z(len(T[1]),len(Es[p12][0]))],
  [z(len(T[1]),len(T[0])),dT0,z(len(T[1]),len(Es[p01][0])),z(len(T[1]),len(Es[p02][0])),z(len(T[1]),len(Es[p12][0]))],
  [-b0[p01],z(len(Es[p01][1]),len(T[0])),de0[p01],z(len(Es[p01][1]),len(Es[p02][0])),z(len(Es[p01][1]),len(Es[p12][0]))],
  [-b0[p02],-b0[p02],z(len(Es[p02][1]),len(Es[p01][0])),de0[p02],z(len(Es[p02][1]),len(Es[p12][0]))],
  [z(len(Es[p12][1]),len(T[0])),-b0[p12],z(len(Es[p12][1]),len(Es[p01][0])),z(len(Es[p12][1]),len(Es[p02][0])),de0[p12]],
 ],format='csr')
 M=bmat([
  [dT1,z(len(T[2]),len(T[1])),z(len(T[2]),len(Es[p01][1])),z(len(T[2]),len(Es[p02][1])),z(len(T[2]),len(Es[p12][1]))],
  [z(len(T[2]),len(T[1])),dT1,z(len(T[2]),len(Es[p01][1])),z(len(T[2]),len(Es[p02][1])),z(len(T[2]),len(Es[p12][1]))],
  [b1[p01],z(len(Es[p01][2]),len(T[1])),-de1[p01],z(len(Es[p01][2]),len(Es[p02][1])),z(len(Es[p01][2]),len(Es[p12][1]))],
  [b1[p02],b1[p02],z(len(Es[p02][2]),len(Es[p01][1])),-de1[p02],z(len(Es[p02][2]),len(Es[p12][1]))],
  [z(len(Es[p12][2]),len(T[1])),b1[p12],z(len(Es[p12][2]),len(Es[p01][1])),z(len(Es[p12][2]),len(Es[p02][1])),-de1[p12]],
 ],format='csr')
 P=M@N;P.eliminate_zeros()
 if P.nnz:raise AssertionError(('MN',P.nnz,P.data[:20]))
 print('NM',N.shape,M.shape,'nnz',N.nnz,M.nnz)
 rN=rank2(N);rM=rank2(M)
 if N.shape!=(12098,4917) or M.shape!=(7180,12098):
  raise AssertionError('balanced complex shape changed')
 if (rN,rM)!=(4917,7180):raise AssertionError('balanced complex rank changed')
 if N.shape[0]-rN-rM!=1:raise AssertionError('middle residue changed')
 print('RANK2',rN,rM,'H1',N.shape[0]-rN-rM)
 return N,M,{'T':(T,dT0,dT1),'E':{p:(Es[p],de0[p],de1[p]) for p in Es}}

if __name__=='__main__':
 x=build();matrices(*x)
 print('PASS exact tapered ribbon: one middle class over F2 and Q')
 print('SCOPE two-dimensional normal slice only; no ambient tangential theorem')
