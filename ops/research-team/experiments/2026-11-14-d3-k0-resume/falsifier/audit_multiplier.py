"""Independent algebraic audit of multiplier elimination; NOT an emptiness checker."""
import json,hashlib,sys
from pathlib import Path
import sympy as s
src=Path(sys.argv[1] if len(sys.argv)>1 else '/workspace/scratch/1959cf51fea0/input/LIFTED_SYSTEM.json')
j=json.loads(src.read_text()); vs=s.symbols(' '.join(j['variables'])); A,B,C,x,beta,L,lam=vs
parse=lambda rows, vv=vs:s.Poly.from_dict({tuple(e):s.Rational(c) for e,c in rows},vv).as_expr()
polys=[parse(rows) for rows in j['equations']]
psi,E=polys[:2]; n=s.diff(psi,x);d=s.diff(E,x)
reduced=[psi,E,polys[2],polys[3]]
checks=[]
for idx in [4,6,7]:
 p=s.Poly(polys[idx],lam); assert p.degree()<=1
 reduced.append(s.expand(d*p.nth(0)+n*p.nth(1)))
 assert s.expand(d*polys[idx]-(d*p.nth(0)+n*p.nth(1))-(d*lam-n)*p.nth(1))==0
 checks.append('exact equation identity '+str(idx))
N,D=s.symbols('N D',nonzero=True)
a2=parse(j['a2']); orient=parse(j['orientation'])
assert s.cancel(D**2*orient.subs(lam,N/D)-N*(D*s.diff(psi,B)-N*s.diff(E,B)))==0
checks.append('orientation positive denominator D^2')
assert s.cancel(D**2*(a2*lam).subs(lam,N/D)-a2*N*D)==0
checks.append('strict filter positive denominator D^2')
e=s.symbols('e');Psi=parse(j['Psi'],vs+(e,));Gamma=parse(j['Gamma'],vs+(e,))
xi=[A,C,x,beta,L,e]
HP=s.hessian(Psi,xi);HG=s.hessian(Gamma,xi)
for i in range(6):
 for k in range(6):
  old=lam*B*L**2*HP[i,k]-lam**2*HG[i,k]
  new=N*D*B*L**2*HP[i,k]-N**2*HG[i,k]
  assert s.cancel(D**2*old.subs(lam,N/D)-new)==0
checks.append('all 36 curvature entries under positive D^2 scale')
# An arbitrary symmetric block verifies second Schur numerator scaling exactly.
a,b,c,z=s.symbols('a b c z')
assert s.expand((D**2*a)*(D**2*z)-(D**2*b)*(D**2*c)-D**4*(a*z-b*c))==0
checks.append('Schur numerator positive D^4 scale')
# Hostile scalar examples: d can have either sign; clearing by d is not sign-safe.
assert (1*(-1)/(-2)>0) and not (1*(-1)>0)
assert (-1)*((-2)*0-(-1)*1)<0
checks.append('negative denominator wrong-sign shortcut rejected')
# Exact conic instances prove E_x is not globally positive.
conic=[]
for kval in [3,-3,2,-2]:
 for aval in map(s.Rational,[1,-2,s.Rational(-1,2)]):
  n0=kval*kval-aval*(aval+1);t0=n0-aval*(aval+1)
  if not n0 or not t0:continue
  mp={A:aval,B:1,x:-aval*n0/t0,beta:-aval*(kval-aval-1)**2/n0}
  if s.factor(E.subs(mp))!=0:continue
  der=s.factor(d.subs(mp));conic.append({'A':str(aval),'k':str(kval),'E_x':str(der)})
assert any(s.Rational(v['E_x'])<0 for v in conic) and any(s.Rational(v['E_x'])>0 for v in conic)
checks.append('both E_x signs on exact conic instances; no parent admissibility claimed')
result={'status':'PASS','classification':'exact algebraic equivalence audit, not locus exclusion','source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'checks':checks,'conic_sign_canaries':conic,'reduced_profiles':[{'degree':s.Poly(p,*vs[:-1]).total_degree(),'terms':len(s.Poly(p,*vs[:-1]).terms())} for p in reduced], 'ledger':'2/9','new_source_closures':0}
Path(__file__).with_name('AUDIT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
