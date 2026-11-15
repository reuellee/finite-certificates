from fractions import Fraction as F
from itertools import permutations
from hashlib import sha256
import sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[4]/'ai/omreal'))
import verify_diag3_row2599_p01_comparison_prism as p
assert sha256(p.SOURCE.read_bytes()).hexdigest()==p.SOURCE_SHA256
with np.load(p.SOURCE,allow_pickle=False) as z: raw=z['chart_matrix'][0]
M=p.build_collar(raw)[1]
A=[[sum(F(v)*F(0)**k[0] for k,v in e.items()) for e in row] for row in M]
def det(cols, mat):
 cols=[x-1 for x in cols];total=F(0)
 for perm in permutations(range(4)):
  inv=sum(perm[i]>perm[j] for i in range(4) for j in range(i+1,4));term=F((-1)**inv)
  for i in range(4):term*=F(mat[i][cols[perm[i]]])
  total+=term
 return total
d=det((2,3,5,8),A); n=det((1,3,5,8),A)
for r in range(4):A[r][0]=d*A[r][0]-F(1,4)*n*A[r][1]
base=det((1,3,6,7),raw.tolist()); val=det((1,3,6,7),A)*(1 if base>0 else -1)
print('independent permutation determinant d_positive',d>0,'parent 1367 negative',val<0,'value',val)
assert d>0 and val<0
