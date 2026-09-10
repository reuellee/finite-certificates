import sys,json,random,itertools
from pathlib import Path
from fractions import Fraction as Q
import numpy as np
from scipy.optimize import linprog
P=Path(__file__).resolve().parent
sys.path.insert(0,str(P.parent/'inputs/code'));import parent_certificates as pc
triples=pc.TRIPLES;bases=pc.BASES

def rref(A):
 a=[list(map(Q,r))for r in A];h=0;piv=[]
 for j in range(len(a[0])):
  i=next((i for i in range(h,len(a))if a[i][j]),None)
  if i is None:continue
  a[h],a[i]=a[i],a[h];v=a[h][j];a[h]=[x/v for x in a[h]]
  for k in range(len(a)):
   if k!=h:
    v=a[k][j];a[k]=[x-v*y for x,y in zip(a[k],a[h])]
  piv.append(j);h+=1
  if h==len(a):break
 return a,piv

def solve(A,b):
 n=len(A[0]);a,p=rref([list(r)+[v]for r,v in zip(A,b)])
 if n in p:return None
 x=[Q(0)]*n
 for j,row in zip(p,a):x[j]=row[-1]
 return x

def null(A):
 a,p=rref(A);n=len(A[0]);out=[]
 for j in range(n):
  if j in p:continue
  x=[Q(0)]*n;x[j]=1
  for k,row in zip(p,a):x[k]=-row[j]
  out.append(x)
 return out

def dot(a,b):return sum(x*y for x,y in zip(a,b))
def normals(Y):return [[(-1)**(r+3)*pc.det([[Y[k][c]for c in t]for k in range(4)if k!=r])for r in range(4)]for t in triples]
def brackets(Y):return [pc.det([[Y[r][c]for c in b]for r in range(4)])for b in bases]
def transpose(A):return list(map(list,zip(*A)))
def minnorm(A,b):
 # Find independent rows; solve full consistent equality by minimum norm right inverse.
 _,ids=rref(transpose(A));AA=[A[i]for i in ids];bb=[b[i]for i in ids]
 G=[[dot(x,y)for y in AA]for x in AA];lam=solve(G,bb);w=[dot(col,lam)for col in transpose(AA)]
 return w if [dot(r,w)for r in A]==b else None

def main():
 pts=[(x,y)for y in range(3)for x in range(3)if(x,y)!=(2,2)];rng=random.Random(1410)
 for count in range(100):
  Y=[[1]*8,[x for x,y in pts],[y for x,y in pts],[rng.randrange(-20,21)for _ in pts]];br=brackets(Y)
  if all(br):break
 lift_trials=count+1
 N=normals(Y);zero=[i for i in range(56)if N[i][3]==0];K=null(transpose([N[i]for i in zero]))
 print('Y',Y,'zeros',zero,'kernel',K,flush=True)
 for co in itertools.product(range(-4,5),repeat=len(K)):
  v=[sum(a*k[j]for a,k in zip(co,K))for j in range(len(zero))]
  if all(v):break
 signs=[pc.sign(N[i][3])if i not in zero else pc.sign(v[zero.index(i)])for i in range(56)]
 A=[[s*x for x in n]for s,n in zip(signs,N)];AZ=transpose([A[i]for i in zero]);best=None
 for mask in range(1,1<<len(zero)):
  J=[j for j in range(len(zero))if mask>>j&1];E=[[r[j]for j in J]for r in AZ]+[[Q(1)]*len(J)];b=[Q(0)]*4+[Q(1)];w=minnorm(E,b)
  if w is None or any(x<0 for x in w):continue
  ww=[Q(0)]*len(zero)
  for j,x in zip(J,w):ww[j]=x
  val=dot(ww,ww)
  if best is None or val<best[0]:best=(val,ww)
 print('signs',signs,'minimum',best,flush=True)
 D=[]
 for r,c in itertools.product(range(3),range(8)):
  YY=[row[:]for row in Y];YY[r][c]+=1;NN=normals(YY);D.append([signs[i]*NN[i][3]for i in zero])
 DD=transpose(D);print('derivative rank',pc.rank(DD),flush=True)
 E=AZ+[[Q(1)]*len(zero)];bb=[Q(0)]*4+[Q(1)]
 for count,bvals in enumerate(itertools.product(range(-2,3),repeat=len(zero))):
  if dot(best[1],bvals)<=0:continue
  rr=linprog(np.array(bvals,dtype=float),A_eq=np.array(E,dtype=float),b_eq=np.array(bb,dtype=float),bounds=(0,None),method='highs')
  if not rr.success or rr.fun>=-1e-8:continue
  sol=solve(DD,bvals)
  if sol is None:continue
  H=[[Q(0)]*8 for _ in range(4)]
  for x,(r,c)in zip(sol,itertools.product(range(3),range(8))):H[r][c]=x
  print('FOUND b',bvals,'dotmin',dot(best[1],bvals),'LP',rr.x,'H',H,flush=True)
  data={'parent':[[str(x)for x in row]for row in Y],'signs':signs,'parent_signs':[pc.sign(x)for x in br],'zero_indices':zero,'minimum_weights':[str(x)for x in best[1]],'minimum_norm2':str(best[0]),'direction':[[str(x)for x in row]for row in H],'zero_derivative':list(bvals),'positive_kernel_weights':[str(abs(x))for x in v],'candidate_checks':count+1,'lift_trials':lift_trials}
  (P/'candidate.json').write_text(json.dumps(data,indent=2)+'\n');break
 else:raise Exception('none')
if __name__=='__main__':main()
