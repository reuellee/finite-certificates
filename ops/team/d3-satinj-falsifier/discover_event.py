from itertools import combinations
from fractions import Fraction as F
import json
from pathlib import Path
P=[[-94,-25,256,256,42,-3,-78,-101],[-163,54,35,-164,-96,256,256,-21],[256,256,-27,-25,197,160,-83,54],[71,122,19,-204,-256,-61,-93,-256]]
SIGS=[14988895318912,3405195891438080,40418075143643136]
SP=[(0,19,21,37,38),(0,9,27,30,35),(0,11,17,24,40)]
T=sorted(combinations(range(8),3),key=lambda x:x[::-1]); B=sorted(combinations(range(8),4),key=lambda x:x[::-1])
def trim(p):
 while len(p)>1 and not p[-1]:p.pop()
 return p
def add(p,q):
 r=[0]*max(len(p),len(q))
 for i,v in enumerate(p):r[i]+=v
 for i,v in enumerate(q):r[i]+=v
 return trim(r)
def mul(p,q):
 r=[0]*(len(p)+len(q)-1)
 for i,x in enumerate(p):
  for j,y in enumerate(q):r[i+j]+=x*y
 return trim(r)
def scale(p,c):return trim([x*c for x in p])
def det(A):
 if not A:return [1]
 z=[0]
 for j,x in enumerate(A[0]):z=add(z,scale(mul(x,det([r[:j]+r[j+1:] for r in A[1:]])),(-1)**j))
 return z
def ev(p,t):return sum(x*t**i for i,x in enumerate(p))
def div(p,q):
 p=list(map(F,p));q=list(map(F,q));out=[F(0)]*max(1,len(p)-len(q)+1)
 while len(p)>=len(q) and p!=[0]:
  d=len(p)-len(q);c=p[-1]/q[-1];out[d]=c
  for i,x in enumerate(q):p[i+d]-=c*x
  trim(p)
 return trim(out),p
def circuit(N,sig,sp):
 A=[[scale(v,1 if sig>>i&1 else -1) for v in N[i]] for i in sp]
 return [scale(det([r for k,r in enumerate(A) if k!=j]),(-1)**j) for j in range(5)]
for label in range(8):
 for coord in range(4):
  Y=[[[v] for v in row] for row in P];Y[coord][label].append(1)
  br=[det([[Y[r][i] for i in b] for r in range(4)]) for b in B]
  N=[[scale(det([[Y[r][i] for r in range(4) if r!=j] for i in t]),(-1)**(j+5)) for j in range(4)] for t in T]
  C=[circuit(N,sig,sp) for sig,sp in zip(SIGS,SP)]
  for block in range(3):
   for k,poly in enumerate(C[block]):
    reduced=poly
    for h in br:
     if len(h)>1:
      while True:
       q,r=div(reduced,h)
       if r!=[0]:break
       reduced=q
    if len(reduced)!=2:continue
    root=-F(reduced[0],reduced[1])
    if not all(ev(h,root)*h[0]>0 for h in br):continue
    vals=[[ev(c,root) for c in blockc] for blockc in C]
    if any(not ((all(x>=0 for x in v) or all(x<=0 for x in v)) and any(v)) for v in vals):continue
    if sum(x==0 for x in vals[block])!=1:continue
    data={'label':label+1,'coord':coord,'root':str(root),'block':block,'zero_weight':k,'cofactor_polynomials':C,'parent_bracket_polynomials':br,'reduced_polynomial':list(map(str,reduced)),'parent':P,'signatures':SIGS,'supports':SP}
    Path(__file__).with_name('DISCOVERED_EVENT.json').write_text(json.dumps(data,indent=2)+'\n')
    print('FOUND',label+1,coord,root,block,k,'otherzero',[sum(x==0 for x in v) for v in vals]);raise SystemExit
print('NO EVENT')
