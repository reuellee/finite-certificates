from pathlib import Path
from itertools import combinations
import sympy as s,json
ROOT=Path(__file__).resolve().parents[1]
D=json.loads((ROOT/'falsifier/NONZERO_NONCOLLINEAR_REPLAY.json').read_text())
Y=s.Matrix([[s.Rational(x) for x in row] for row in D['parent']]);P=D['supports_1based']['P'];Q=D['supports_1based']['Q'];R=D['supports_1based']['R']
p=s.Matrix([1,2,2,0]);T=s.Matrix([[-2,1,0,0],[-2,0,1,0],[0,0,0,1],[1,0,0,0]])
V=T*Y;Z=V[:3,:];u,v,w,t=s.symbols('u v w t');YY=T.inv()*s.Matrix.vstack(Z,s.Matrix([[1,0,0,0,u,v,w,t]]))
def normal(V,I):
 A=V[:,[int(j)-1 for j in I]]
 return s.Matrix([[(-1)**(3+j)*A[[k for k in range(4) if k!=j],:].det() for j in range(4)]])
def determinant(V,K):return s.factor(s.Matrix.vstack(*(normal(V,I) for I in K)).det(method='domain-ge'))
F=determinant(YY,Q);G=determinant(YY,R)
print('P',determinant(YY,P));print('Q',F);print('R',G);print('R-Q',s.factor(G-F));print('grobner',s.groebner([F,G],u,v,w,t))
