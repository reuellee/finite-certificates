from pathlib import Path
from itertools import combinations
import sympy as s
u,v,w,t,x,y,z,k=s.symbols('u v w t x y z k')
Y=s.Matrix([[1,0,0,0,u,v,w,t],[0,1,0,0,2*u-1,2*v-3,2*w+x,2*t+z],[0,0,1,0,2*u-1,2*v,2*w+y,2*t+k],[0,0,0,1,1,3,2,5]])
P=('123','145','246','356');Q=('123','146','248','378');R=('126','145','248','378')
def n(I):
 A=Y[:,[int(j)-1 for j in I]]
 return s.Matrix([[(-1)**(3+j)*A[[m for m in range(4) if m!=j],:].det() for j in range(4)]])
def d(K):return s.factor(s.Matrix.vstack(*(n(I) for I in K)).det(method='domain-ge'))
F=d(Q);G=d(R);E=s.factor(G-(2*u-1)*F)
print('Q=',F);print('R=',G);print('parent-unit difference=',E)
print('coefficient factors=',[s.factor(c) for c in s.Poly(E,u,v,w,t).coeffs()])
