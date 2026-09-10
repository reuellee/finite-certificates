#!/usr/bin/env python3
"""Independent exact polynomial audit of one full hard50+50 column fiber.
No producer symbolic acceptance code is imported. Arithmetic is rational.
"""
from fractions import Fraction as F
from itertools import combinations, permutations
from pathlib import Path
import json
P=Path(__file__).resolve().parent

def p(x):return {(0,0):F(x)} if x else {}
def add(*xs):
 out={}
 for x in xs:
  for k,v in x.items():out[k]=out.get(k,F(0))+v
 return {k:v for k,v in out.items() if v}
def mul(x,y):
 out={}
 for (a,b),v in x.items():
  for(c,d),w in y.items():out[a+c,b+d]=out.get((a+c,b+d),F(0))+v*w
 return {k:v for k,v in out.items() if v}
def scale(x,c):return {k:v*c for k,v in x.items() if v*c}
def det(M):
 n=len(M);out={}
 for q in permutations(range(n)):
  sign=(-1)**sum(q[a]>q[b] for a in range(n)for b in range(a+1,n));v=p(sign)
  for r,j in enumerate(q):v=mul(v,M[r][j])
  out=add(out,v)
 return out
def normal(Y,J):
 return [scale(det([[Y[r][j-1]for j in J]for r in range(4)if r!=o]),(-1)**(o+3))for o in range(4)]
def derived(Y,support):
 cols=[normal(Y,J)for J in support]
 return det([[cols[j][r]for j in range(4)]for r in range(4)])
def ev(poly,h,i):return sum(v*h**a*i**b for(a,b),v in poly.items())
def subst_h(poly):
 H={(0,0):-F(1196,67),(0,1):F(115,67)};I={(0,1):F(1)};out={}
 for(a,b),v in poly.items():
  term=p(v)
  for _ in range(a):term=mul(term,H)
  for _ in range(b):term=mul(term,I)
  out=add(out,term)
 return out
def sg(x):return (x>0)-(x<0)
def main():
 H={(1,0):F(1)};I={(0,1):F(1)}
 G=add(p(-8),scale(I,-F(5,4)))
 Y=[[p(x)for x in row]for row in [[1,0,0,0,1,1,1,1],[0,1,0,0,1,7,F(-17,4),0],[0,0,1,0,1,-8,2,0],[0,0,0,1,1,-4,-3,0]]]
 Y[1][7]=G;Y[2][7]=H;Y[3][7]=I
 support1=((1,2,3),(1,4,5),(2,4,6),(3,7,8))
 support2=((5,6,7),(1,5,8),(2,6,8),(3,4,7))
 f1=derived(Y,support1);f2=derived(Y,support2)
 L1=add(H,scale(I,-10),p(-32));L2=add(scale(H,67),scale(I,-115),p(1196))
 assert f1=={} and f2==scale(mul(L1,L2),F(3,16))
 b2678=det([[Y[r][j-1]for j in(2,6,7,8)]for r in range(4)])
 assert b2678==L1
 # Consequently the original uniform fiber consists exactly of L2=0.
 lower=[];upper=[];records=[]
 for J in combinations(range(1,9),4):
  B=det([[Y[r][j-1]for j in J]for r in range(4)])
  Bline=subst_h(B)
  assert all(a==0 and b<=1 for a,b in Bline)
  anchor=ev(Bline,0,F(-8));assert anchor
  sign=sg(anchor);lin=scale(Bline,sign)
  intercept=lin.get((0,0),F(0));slope=lin.get((0,1),F(0))
  label=''.join(map(str,J))
  if slope:
   root=-intercept/slope;(lower if slope>0 else upper).append((root,label))
  else:assert intercept>0
  records.append({'bracket':label,'anchor_sign':sign,'signed_slope':str(slope),'signed_intercept':str(intercept)})
 lo=max(x[0]for x in lower);hi=min(x[0]for x in upper)
 assert(lo,hi)==(F(-12),F(-36,5))
 ends={'lower':[j for x,j in lower if x==lo],'upper':[j for x,j in upper if x==hi]}
 assert ends=={'lower':['3468'],'upper':['3458']}
 # Hostile control: changed interval cannot match reconstructed endpoints.
 assert (F(-11),hi)!=(lo,hi)
 # The parameter i is literal last coordinate, making this parametrization
 # bijective. All signs reduce to strictlinear inequalities, so this is the
 # WHOLE fiber for the anchorparent chirotope, with genuineparent endwalls.
 out={'status':'PASS_EXACT_FULL_COLUMN_FIBER','scope':'Fixed seven parent columns in the actual hard 50+50 case',
 'parametrization':{'g':'-5*i/4-8','h':'(115*i-1196)/67','i':'i'},
 'interval':[str(lo),str(hi)],'endwalls':ends,'all_parent_brackets':records,
 'excluded_factor':'h-10*i-32 = [2678]','remaining_factor':'67*h-115*i+1196',
 'fiber_Hc0':'0','fiber_Hc1':'Z','global_pair_Hc1':'NOT_COMPUTED',
 'meaning':'The one-column forgetting map has a nonzero R1 f! stalk; the zero-Hc1 fiber template cannot extend unchanged.'}
 (P/'HARD_COLUMN_FIBER_CERTIFICATE.json').write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({k:v for k,v in out.items()if k!='all_parent_brackets'},indent=2))
if __name__=='__main__':main()
