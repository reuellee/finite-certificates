"""Exact identities for exclusion of the full g=0 maximum branch.
The accompanying proof contains the logical case analysis. No numerical acceptance.
"""
from source_context import *
import json,time
r,z=s.symbols('r z')

def run():
 start=time.monotonic();Q,R,br=reconstruct();src=source_path()
 require(hashlib.sha256(src.read_bytes()).hexdigest()==SOURCE_SHA,'source SHA-256')
 raw=json.loads(src.read_text())
 for name,f in [('Q',Q),('R',R)]:zero(f-s.sympify(raw['raw_factors'][name]),'raw '+name)
 for name,f in br.items():zero(f-s.sympify(raw['parent_brackets'][name]),'bracket '+name)
 change={t:(D*r-u)/A,w:C*z+u}
 lower=lower_chart();q=s.sympify(lower['q']);p=s.sympify(lower['g'])
 zero(Q.subs(change,simultaneous=True)-D*q,'Q chart');zero(R.subs(change,simultaneous=True)-C*p/A**2,'R chart')
 require(D not in q.free_symbols and C not in p.free_symbols,'separation')
 a2,a1,a0=s.Poly(q,C).all_coeffs();b2,b1,b0=s.Poly(p,D).all_coeffs()
 K=r*(B+u-v)+u*(B+1)
 zero(a0-(A+1)*(u-v)*K,'q constant coefficient')
 zero(b0-B*u**2*(A+1)*(A+u),'p constant coefficient')
 zero(a2-(z-1)*(z*(A*(r+v)-B*(r+u))+r*(u-v)),'q leading coefficient')
 zero(q-C*s.diff(q,C)-(a0-C**2*a2),'double-root coefficient identity')
 # Factors used in every division and zero-product inference are authenticated.
 expected={'A':A,'B':B,'C':C,'D':D,'u':u,'B+1':B+1,'C+1':C+1,
           'A+1':A+1,'A+u':A+u,'u-v':u-v,'A+u-v':A+u-v}
 factors=set()
 for f in br.values():
  for pp,nn in s.factor_list(f,*TH)[1]:factors.add(str(s.Poly(pp,*TH).monic().as_expr()))
 require(len(factors)==61,'all 61 parent factors')
 for name,f in expected.items():require(str(s.Poly(f,*TH).monic().as_expr()) in factors,'parent unit '+name)
 zero(br['2458'].subs(change,simultaneous=True)+D*(r+u),'unit r+u')
 zero(br['1357'].subs(change,simultaneous=True)+C*(z-1),'unit z-1')
 zero(br['2357'].subs(change,simultaneous=True)-(A+C-C*z+1),'bracket H0')
 zero(s.diff(p,z)-A**2*s.diff(R,w).subs(change,simultaneous=True),'p_z is unit')
 B0=-(r*(u-v)+u)/(r+u)
 S=s.expand((z*(A*(r+v)-B*(r+u))+r*(u-v)).subs(B,B0)).cancel().expand()
 b=s.cancel(a1.subs(B,B0)).expand();d=A*r+A*v+r*u-r*v+u
 J=r*(A+u-v+1)+A*v+u
 zero(S-(d*z+r*(u-v)),'S representation')
 zero(d*b-s.diff(b,z)*S+r*(u-v)*(A+u-v)*J,'division-free resultant consequence')
 zero(S-(z*J+r*(u-v-z)),'z=u-v inference identity')
 delta=A+u-v+1
 zero((A*v+u).subs(A,v-u-1)+(u-v)*(v-1),'delta=0 branch consequence')
 r0=-(A*v+u)/delta
 zero((r+u).subs(r,r0)-(A+u)*(u-v)/delta,'r+u on flat family')
 Bflat=(A*u*v-A*u-A*v**2-u)/((A+u)*(u-v))
 zero(B0.subs(r,r0)-Bflat,'B flat family')
 flat={B:Bflat,r:r0,z:u-v}
 for name,f in [('a2',a2),('a1',a1),('a0',a0)]:zero(f.subs(flat,simultaneous=True),'flat-family '+name)
 def mixed(a,b):return s.expand(s.diff(q,a)*s.diff(q,C,b)-s.diff(q,b)*s.diff(q,C,a))
 ar=-u*(A+1)*(C+1)**2*(u-v)**2*(v-1)*(u-v-1)**2/(A+u)
 ar_actual=s.factor(mixed(A,r).subs(flat,simultaneous=True))
 zero(ar_actual-ar,'A,r mixed certificate')
 one={v:1,r:-1,z:u-1,B:1/(1-u)}
 zero(mixed(u,z).subs(one,simultaneous=True)-(-A+C*u-2*C-1)**2,'v=1 mixed certificate')
 zero(br['2357'].subs(change,simultaneous=True).subs(one,simultaneous=True)-(A+2*C-C*u+1),'v=1 nonzero mixed bracket')
 # Deliberately wrong signs/coefficients must not be accepted.
 failures={}
 for label,f in [('wrong A,r sign',ar_actual+ar),
                 ('wrong v=1 coefficient',mixed(u,z).subs(one,simultaneous=True)-2*(-A+C*u-2*C-1)**2)]:
  try:zero(f,label)
  except AssertionError:failures[label]='REJECTED'
  else:raise AssertionError('negative control accepted')
 # A 2x2 zero-diagonal block with nonzero off-diagonal has negative determinant.
 off,diag=s.symbols('off diag');zero(s.Matrix([[0,off],[off,diag]]).det()+off**2,'indefinite 2x2 identity')
 out={'status':'PASS','source_sha256':SOURCE_SHA,'parent_brackets':70,'parent_factors':61,
      'result':'g=0 stationary points cannot be B maxima or minima on any parent residence',
      'scope':'all g=0 cases in the authenticated chart; singular nu=0 included',
      'flat_family':'derived from a2=a1=a0=0 using authenticated units; no generic-case deletion',
      'case_partition':['v!=1: mixed A,r nonzero','v=1: mixed u,z equals nonzero parent-bracket square'],
      'negative_controls':failures,'original_ledger':'2/9','new_source_orbits_closed':0,
      'whole_survivor':'OPEN','independent_mathematical_referee':False,'seconds':time.monotonic()-start}
 (HERE/'ZERO_CURVATURE_REPLAY.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
 return out
if __name__=='__main__':run()
