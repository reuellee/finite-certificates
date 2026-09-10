from pathlib import Path
from itertools import combinations
import sympy as s,json
ROOT=Path(__file__).resolve().parents[1]
D=json.loads((ROOT/'falsifier/NONZERO_NONCOLLINEAR_REPLAY.json').read_text())
P=D['supports_1based']['P'];Q=D['supports_1based']['Q'];R=D['supports_1based']['R']
a,b,c,d,e,f,g,h,i=s.symbols('a b c d e f g h i');Y=s.Matrix([[1,0,0,0,1,1,1,1],[0,1,0,0,1,a,d,g],[0,0,1,0,1,b,e,h],[0,0,0,1,1,c,f,i]])
def normal(V,I):
 A=V[:,[int(j)-1 for j in I]]
 return s.Matrix([[(-1)**(3+j)*A[[k for k in range(4) if k!=j],:].det() for j in range(4)]])
def det(K):return s.factor(s.Matrix.vstack(*(normal(Y,I) for I in K)).det(method='domain-ge'))
F=det(Q);G=det(R);PP=det(P)
print('P',PP);print('Q',F);print('R',G)
Fa=s.factor(F.subs(a,b+c-b*c));Ga=s.factor(G.subs(a,b+c-b*c));print('QonP',Fa);print('RonP',Ga);print('ratio',s.cancel(Ga/Fa));print('difference',s.factor(G-F))
