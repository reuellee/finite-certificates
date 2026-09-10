"""Targeted algebraic discovery using the inherited uniform critical parent."""
import sympy as s
from itertools import combinations
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
Y=s.Matrix([[1,0,0,0,1,1,1,1],[0,1,0,0,1,-1,4,7],[0,0,1,0,1,2,-5,-4],[0,0,0,1,1,3,2,5]])
def normal(Y,I):
 A=Y[:,[int(j)-1 for j in I]]
 return s.Matrix([[(-1)**(3+j)*A[[k for k in range(4) if k!=j],:].det() for j in range(4)]])
def gradmap(Y,K):
 N=s.Matrix.vstack(*(normal(Y,I) for I in K));q=N.nullspace()[0];lam=N.T.nullspace()[0];B=s.zeros(8,4)
 for coeff,I in zip(lam,K):
  J=[int(v)-1 for v in I]
  for a,j in enumerate(J):
   for k in range(4):
    cols=[Y[:,v] for v in J];cols[a]=s.eye(4)[:,k];B[j,k]+=coeff*s.Matrix.hstack(*cols,q).det()
 assert Y*B==s.zeros(4,4) and B*q==s.zeros(8,1)
 return N,q,lam,B
if __name__=='__main__':
 K0=('123','145','246','356');KP=('125','126','356','378')
 for K in [K0,KP,('123','145','246','378')]:
  N,q,lam,B=gradmap(Y,K);print(K,'q',list(q),'B rank',B.rank(),'ker',[list(v) for v in B.nullspace()])
 ordinary=[('123','124','345','567'),('123','124','345','678'),('123','124','356','457'),('123','124','356','478'),('123','124','356','578'),('123','145','246','356'),('123','145','246','357'),('123','145','246','378'),('123','145','267','468')]
 for K in ordinary:
  N=s.Matrix.vstack(*(normal(Y,I) for I in K))
  if N.det()==0:print('Canonicalzero',K,N.nullspace())
