#!/usr/bin/env python3
"""Independent exact audit of eleven-column three-signature incidence path."""
import argparse, hashlib, itertools
from fractions import Fraction as F
from pathlib import Path
import numpy as np
SIGS=(17331133384703,102950366083904,114322895077375)
T=sorted(itertools.combinations(range(8),3),key=lambda x:x[::-1])
B=sorted(itertools.combinations(range(8),4),key=lambda x:x[::-1])
def det3(a,b,c):return a[0]*(b[1]*c[2]-b[2]*c[1])-a[1]*(b[0]*c[2]-b[2]*c[0])+a[2]*(b[0]*c[1]-b[1]*c[0])
def det4(cols):
 a,b,c,d=cols
 return sum((-1)**(k+3)*d[k]*det3(*[[v[i] for i in range(4) if i!=k] for v in (a,b,c)]) for k in range(4))
def test(v,signs):
 assert len(v)==11 and all(len(x)==4 for x in v)
 for q,s in zip(B,signs):assert det4([v[i] for i in q])*s>0,('parent',q)
 for z,sig in enumerate(SIGS):
  for i,q in enumerate(T):assert det4([v[j] for j in q]+[v[8+z]])*(1 if sig>>i&1 else -1)>0,('signature',z,q)
def cols(a):return [[int(a[r,c]) for r in range(4)] for c in range(a.shape[1])]
def replay(init,cols1,vecs,signs,tamper=False):
 assert len(cols1)==len(vecs);v=[x[:] for x in init];test(v,signs);undo=[]
 for i,(k,w) in enumerate(zip(cols1,vecs)):
  k=int(k);assert 0<=k<11;old=v[k];undo.append((k,old));v[k]=[int(x) for x in w]
  if tamper and i==0:v[k]=[0,0,0,0]
  test(v,signs)
 final=[x[:] for x in v]
 for k,w in reversed(undo):v[k]=w;test(v,signs)
 assert v==init
 return final
def invert(A):
 n=len(A);q=[[F(v) for v in row]+[F(i==j) for j in range(n)] for i,row in enumerate(A)]
 for i in range(n):
  j=next(j for j in range(i,n) if q[j][i]);q[i],q[j]=q[j],q[i];x=q[i][i];q[i]=[v/x for v in q[i]]
  for j in range(n):
   if i!=j:
    x=q[j][i];q[j]=[a-x*b for a,b in zip(q[j],q[i])]
 return [r[n:] for r in q]
def mm(A,B):return [[sum(A[i][k]*B[k][j] for k in range(len(B))) for j in range(len(B[0]))] for i in range(len(A))]
def cmat(v):return [[F(col[i]) for col in v] for i in range(4)]
def rays(a,b):
 assert len(a)==len(b)
 for x,y in zip(a,b):
  j=next(i for i in range(4) if x[i]);assert y[j]/x[j]>0 and all(y[i]*x[j]==x[i]*y[j] for i in range(4))
def gauge(old,canonical):
 I=invert(cmat(old[:4]));q=mm(I,cmat([old[4]]));D=[[F(int(i==j))/abs(q[i][0]) for j in range(4)] for i in range(4)];G=mm(D,I)
 assert det4([[G[i][j] for i in range(4)] for j in range(4)])>0
 W=mm(G,cmat(old));rays([[W[i][j] for i in range(4)] for j in range(len(old))],canonical)
def main():
 a=argparse.ArgumentParser();a.add_argument('--tamper',action='store_true');a.add_argument('--source',required=True,type=Path);a.add_argument('--catalog',required=True,type=Path);a.add_argument('--cert',required=True,type=Path);args=a.parse_args(); SOURCE=args.source; CAT=args.catalog; CERT=args.cert
 assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()=='3b90799d26b7783e92c2ac697eaaf8b76d26a787f53205873b997657e114180a'
 assert hashlib.sha256(CAT.read_bytes()).hexdigest()=='47b2d2b782d298539c85cb170bb10911abe9c82795b4f344e77e3ae64236c7b5'
 z=np.load(CERT,allow_pickle=False);x=np.load(SOURCE,allow_pickle=False)['chart_matrix']
 assert str(z['format'])=='ninth-candidate-12-37-coordinate-path-v1' and int(z['parent_index'])==2599
 assert list(z['endpoint'])==[12,37] and list(z['signature'])==list(SIGS)
 signs=[1 if c=='+' else -1 for c in CAT.read_text().splitlines()[2599].strip()];assert len(signs)==70
 init=[]
 for idx,side in ((12,'a'),(37,'b')):
  v=cols(x[idx])+[[int(w) for w in row] for row in z['initial_p_'+side]];test(v,signs);init.append(v)
 print('PASS exact source endpoints and all 70+168 initial determinants',flush=True)
 A=replay(init[0],z['update_col_a'],z['update_vec_a'],signs,args.tamper); print('A PASS forward/reverse',len(z['update_col_a']),flush=True)
 C=replay(init[1],z['update_col_b'],z['update_vec_b'],signs); print('B PASS forward/reverse',len(z['update_col_b']),flush=True)
 ca,cb,bs=cols(z['canonical_a']),cols(z['canonical_b']),cols(z['bridge_start']);gauge(A,ca);gauge(C,cb);rays(ca,bs)
 E=replay(bs,z['bridge_col'],z['bridge_vec'],signs);rays(E,cb)
 print('bridge PASS forward/reverse',len(z['bridge_col']));print('PASS positive GL and column-rescaling gauge joins; every vertex and all 238 determinants at every vertex, 5,205 updates')
 print('certificate_sha256',hashlib.sha256(CERT.read_bytes()).hexdigest())
if __name__=='__main__':main()
