import json,itertools,sympy as S
from pathlib import Path
P=Path(__file__).resolve().parent;B=P.parent
D=json.loads((B/'previous_checkpoint/falsifier/certificate.json').read_text())
Y=S.Matrix(D['parent']).applyfunc(S.Rational);H=S.Matrix(D['perturbation']).applyfunc(S.Rational);G=S.Matrix(D['good_direction']).applyfunc(S.Rational)
s,t=S.symbols('s t');Y=Y+s*H+t*G
T=sorted(itertools.combinations(range(8),3),key=lambda x:x[::-1]);sgn=[1 if D['signature_integer']>>i&1 else -1 for i in range(56)]
N=S.Matrix([[sgn[i]*(-1)**(r+3)*S.det(Y[[k for k in range(4)if k!=r],list(T[i])])for r in range(4)]for i in D['center_zero_support']])
cs=[]
for i in range(5):
 c=S.factor((-1)**i*N[[k for k in range(5)if k!=i],:].det());cs.append(c);print(i,c,flush=True)
(P/'cofactor_factors.json').write_text(json.dumps([str(x)for x in cs],indent=2)+'\n')
