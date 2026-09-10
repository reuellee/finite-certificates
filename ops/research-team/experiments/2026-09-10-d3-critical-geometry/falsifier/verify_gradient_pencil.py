from pathlib import Path
from fractions import Fraction as F
from itertools import permutations
import json
P=Path(__file__).resolve().parent;src=json.loads((P/'NONZERO_NONCOLLINEAR_REPLAY.json').read_text());Y=[[F(c)for c in row]for row in src['parent']];Ks={k:[tuple(int(c)-1 for c in t)for t in ts]for k,ts in src['supports_1based'].items()}
def det(A):
 n=len(A);out=F(0)
 for p in permutations(range(n)):
  v=F((-1)**sum(p[i]>p[j]for i in range(n)for j in range(i+1,n)))
  for i in range(n):v*=A[i][p[i]]
  out+=v
 return out
def rr(A):
 A=[r[:]for r in A];row=0;piv=[]
 for j in range(len(A[0])):
  k=next((k for k in range(row,len(A))if A[k][j]),None)
  if k is None:continue
  A[row],A[k]=A[k],A[row];d=A[row][j];A[row]=[x/d for x in A[row]]
  for k in range(len(A)):
   if k!=row and A[k][j]:
    d=A[k][j];A[k]=[x-d*y for x,y in zip(A[k],A[row])]
  piv.append(j);row+=1
  if row==len(A):break
 return A,piv
def rank(A):return len(rr(A)[1])
def null(A):
 R,p=rr(A);out=[]
 for j in range(len(A[0])):
  if j in p:continue
  v=[F(0)]*len(A[0]);v[j]=F(1)
  for i,k in enumerate(p):v[k]=-R[i][j]
  out.append(v)
 return out
def mv(A,v):return [sum(x*y for x,y in zip(row,v))for row in A]
def norm(T):return [F((-1)**r)*det([row for j,row in enumerate(T)if j!=r])for r in range(4)]
# All normal signs are the negatives of the preceding point verifier; four row
# sign flips preserve its raw determinant and every raw determinant derivative.
C={}
for name in ['Q','R']:
 triples=[[[Y[k][j]for j in J]for k in range(4)]for J in Ks[name]];N=[norm(T)for T in triples];assert det(N)==0;A=[[F(0)for k in range(4)]for j in range(8)]
 for j in range(8):
  for k in range(4):
   for ii,J in enumerate(Ks[name]):
    if j not in J:continue
    T=[row[:]for row in triples[ii]];slot=J.index(j)
    for row in range(4):T[row][slot]=F(row==k)
    NN=[row[:]for row in N];NN[ii]=norm(T);A[j][k]+=det(NN)
 C[name]=A
A,B=C['Q'],C['R'];p=list(map(F,[1,2,2,0]));q=list(map(F,[1,2,-4,0]));r=list(map(F,[1,-4,-4,-6]));assert rank(A)==rank(B)==3;assert not any(mv(A,q))and not any(mv(B,r))
ar=mv(A,r);bq=mv(B,q);assert any(ar)and any(bq);k=next(k for k,v in enumerate(ar)if v);c=bq[k]/ar[k];proportional=bq==[c*x for x in ar]
L=[row+[F(0)]*4 for row in A]+[[-b for b in br]+arow for br,arow in zip(B,A)]+[[F(0)]*4+row for row in B];ns=null(L)
if proportional:
 assert c!=0;v0=q;v1=[c*x for x in r];assert not any(mv(A,v0))and not any(mv(B,v1));assert mv(A,v1)==mv(B,v0);assert ns
else:assert not ns
crit=[[a-b for a,b in zip(aa,bb)]for aa,bb in zip(A,B)];assert not any(mv(crit,p))
out={'scope':'Exact full directional-gradient pencil for one already-covered actual Q49/R50 pair; no residual-triple membership or global cohomology conclusion','map_convention':'C_S(v)_j differentiates the raw ordinary four-normal determinant underY_j->Y_j+t v; eight output rows and four ambient input columns','full_maps':{n:[[str(x)for x in row]for row in M]for n,M in C.items()},'map_ranks':{'Q':rank(A),'R':rank(B)},'q':[str(x)for x in q],'r':[str(x)for x in r],'C_Q_r':[str(x)for x in ar],'C_R_q':[str(x)for x in bq],'cross_images_proportional':proportional,'c_in_C_Rq_equals_c_C_Qr':str(c)if proportional else None,'degree1_kernel_exists':bool(ns),'degree1_kernel_constant_q':[str(x)for x in q]if proportional else None,'degree1_kernel_linear_c_r':[str(c*x)for x in r]if proportional else None,'coefficient_system_rank':rank(L),'coefficient_system_nullspace':[[str(x)for x in v]for v in ns],'rank_CQ_minus_CR_at_witness_critical_parameter1':rank(crit),'common_p_in_kernel_at_parameter1':[str(x)for x in p],'already_covered_reason':'Parent7 occurs only in the distinct selected plane378; inherited light-label coverage applies. Specific global rational graph also proved.','original_status':'2/9'}
(P/'GRADIENT_PENCIL_REPLAY.json').write_text(json.dumps(out,indent=2)+'\n');print('gate',proportional,'c',c,'degree1kernel',bool(ns),'rank_at1',rank(crit),'cross_images',ar,bq)
