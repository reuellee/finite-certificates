"""Symbolic discovery of the actual hard50+50 conic specialization."""
import sympy as s
from itertools import combinations
from pathlib import Path
import json

HERE=Path(__file__).resolve().parent
c,h,i,t=s.symbols('c h i t')
Y=s.Matrix([[1,0,0,0,1,1,1,1],
 [0,1,0,0,1,7,s.Rational(-17,4),-s.Rational(5,4)*i-8],
 [0,0,1,0,1,-8,2,h],
 [0,0,0,1,1,c,-3,i]])
def normal(I):
 C=Y[:,[j-1 for j in I]]
 return s.Matrix([(-1)**(r+3)*C.minor_submatrix(r,3).det() for r in []]) if False else s.Matrix([(-1)**(r+3)*C.extract([q for q in range(4) if q!=r],[0,1,2]).det() for r in range(4)])
P=((1,2,3),(1,4,5),(2,4,6),(3,7,8))
Q=((5,6,7),(1,5,8),(2,6,8),(3,4,7))
assert s.factor(s.Matrix.hstack(*(normal(I) for I in P)).det())==0
f=s.factor(s.Matrix.hstack(*(normal(I) for I in Q)).det())
print('Q',f,flush=True)
assert f.subs({h:2,i:-3})==0
quotient=s.factor(f.subs(h,2+t*(i+3))/(i+3))
parameter_i=s.factor(s.solve(quotient,i)[0]);parameter_h=s.factor(2+t*(parameter_i+3))
print('i',parameter_i,'h',parameter_h,flush=True)
brackets=[]
for J in combinations(range(8),4):
 B=s.factor(Y[:,list(J)].det());Bt=s.factor(B.subs({h:parameter_h,i:parameter_i}))
 num,den=s.fraction(Bt)
 if s.degree(num,t)>1:
  discr=s.factor(s.discriminant(num,t))
 else:discr=None
 brackets.append({'labels':''.join(str(j+1) for j in J),'original':str(B),'param':str(Bt),'numerator':str(num),'denominator':str(den),'discriminant':str(discr) if discr is not None else None})
out={'family_Q':str(f),'i':str(parameter_i),'h':str(parameter_h),'brackets':brackets}
(HERE/'CONIC_SPECIALIZATION_DISCOVERY.json').write_text(json.dumps(out,indent=2)+'\n')
print('quadratic_discriminants',json.dumps([{'labels':b['labels'],'discriminant':b['discriminant']} for b in brackets if b['discriminant'] is not None],indent=2),flush=True)
