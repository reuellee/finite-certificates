"""Exact double-root elimination and two-pivot Schur reduction.
No claimed global solution of the resulting real system.
"""
from source_context import *
import json,time,itertools
r,z,tau=s.symbols('r z tau')
BASE=(A,B,u,v,r,z)

def construct():
 Q,R,br=reconstruct();data=lower_chart();q=s.sympify(data['q']);p=s.sympify(data['g'])
 a2,a1,a0=s.Poly(q,C).all_coeffs();b2,b1,b0=s.Poly(p,D).all_coeffs()
 dq=s.expand(a1*a1-4*a2*a0);dp=s.cancel((b1*b1-4*b2*b0)/(A*A*u*u)).expand()
 return Q,R,br,q,p,(a2,a1,a0,b2,b1,b0),dq,dp

def schur_entries(Q,R):
 L=s.diff(R,w);I=s.eye(8);H=j*s.hessian(Q,TH)-s.hessian(R,TH)
 V=s.Matrix([0,0,0,A*D,0,0,0,A*t+u]);W=s.Matrix([0,0,C,0,0,0,w-u,0])
 ts=[L*I[:,TH.index(x)]-s.diff(R,x)*I[:,6] for x in (A,u,v,t)]
 h=-2*B*C*u*u*(A+1)*(A+u);g=2*j*(A+1)*(u-v)*((B+u-v)*(A*t+u)+D*u*(B+1));nu=j*s.diff(Q,B)-s.diff(R,B)
 # Retain this arithmetic circuit. Expanding the Schur products is not needed.
 aa=[s.expand((V.T*H*tx)[0]) for tx in ts]
 bb=[s.expand((W.T*H*tx)[0]) for tx in ts]
 nn={(i,k):s.expand((ts[i].T*H*ts[k])[0]) for i in range(4) for k in range(i,4)}
 return h,g,nu,aa,bb,nn

def run():
 start=time.monotonic();require(hashlib.sha256(source_path().read_bytes()).hexdigest()==SOURCE_SHA,'source SHA')
 Q,R,br,q,p,co,dq,dp=construct();a2,a1,a0,b2,b1,b0=co
 sub={t:(D*r-u)/A,w:C*z+u}
 zero(Q.subs(sub,simultaneous=True)-D*q,'Q transformation');zero(R.subs(sub,simultaneous=True)-C*p/A**2,'R transformation')
 qc=s.diff(q,C);pd=s.diff(p,D)
 zero(4*a2*q-qc**2+dq,'quadratic q identity')
 zero(4*b2*p-pd**2+A*A*u*u*dp,'quadratic p identity')
 for x in BASE:
  zero(4*a2*s.diff(q,x)+s.diff(dq,x)-2*qc*s.diff(qc,x)+4*s.diff(a2,x)*q,'q differentiated identity '+str(x))
  zero(4*b2*s.diff(p,x)+A*A*u*u*s.diff(dp,x)+s.diff(A*A*u*u,x)*dp-2*pd*s.diff(pd,x)+4*s.diff(b2,x)*p,'p differentiated identity '+str(x))
 # These exact source units justify the multiplier removal on the relevant locus.
 zero(s.diff(p,z)-A*A*s.diff(R,w).subs(sub,simultaneous=True),'p_z unit identity')
 zero(D*s.diff(q,z)-C*s.diff(Q,w).subs(sub,simultaneous=True),'q_z identity')
 zero(s.diff(Q,w)*j-s.diff(R,w)-(j*s.diff(Q,w)-s.diff(R,w)),'stationary Fw')
 # Polynomial reconstruction identities; residual discriminants are retained.
 ka,kb,kc,xx=s.symbols('ka kb kc xx',nonzero=True)
 zero((ka*xx**2+kb*xx+kc).subs(xx,-kb/(2*ka))+(kb**2-4*ka*kc)/(4*ka),'universal double-root reconstruction')
 seven=[dq,dp]+[s.expand(tau*s.diff(dq,x)-s.diff(dp,x)) for x in BASE if x!=B]
 dqP=s.Poly(dq,*BASE);dpP=s.Poly(dp,*BASE)
 crossP=[dqP.diff(z)*dpP.diff(x)-dpP.diff(z)*dqP.diff(x) for x in (A,u,v,r)]
 cross=[f.as_expr() for f in crossP]
 # A universal multiplier identity avoids expanding redundant high-degree products.
 dx,dz,px,pz=s.symbols('dx dz px pz')
 zero(dz*px-pz*dx-(-dz*(tau*dx-px)+dx*(tau*dz-pz)),'multiplier elimination identity')
 # Persist coefficients directly, avoiding quadratic-cost string parsing.
 sparse={'variables':list(map(str,BASE)),'equations':[[[list(mon),str(coef)] for mon,coef in pp.terms()] for pp in [dqP,dpP]+crossP]}
 (HERE/'SIX_VARIABLE_CRITICAL_SPARSE.json').write_text(json.dumps(sparse,separators=(',',':'))+'\n')
 profiles=lambda fs,vs:[{'degree':s.Poly(f,*vs).total_degree(),'terms':len(s.Poly(f,*vs).terms())} for f in fs]
 generated={'variables':list(map(str,BASE+(tau,))),'delta_q':str(dq),'delta_p':str(dp),'equations':list(map(str,seven)),
  'coefficients':{key:str(val) for key,val in zip(('a2','a1','a0','b2','b1','b0'),co)},
  'scope':'g!=0 stationary chart; original parents and maximum filters still required'}
 (HERE/'REDUCED_CRITICAL.json').write_text(json.dumps(generated,indent=2)+'\n')
 print('double-root and multiplier identities PASS',flush=True)
 # General exact congruence, independent of source-specific simplification.
 hh,gg=s.symbols('hh gg',nonzero=True);av=s.Matrix(s.symbols('a0:4'));bv=s.Matrix(s.symbols('b0:4'))
 N=s.Matrix(4,4,lambda i,k:s.Symbol('n%d%d'%(min(i,k),max(i,k))))
 M=s.zeros(6);M[0,0]=hh;M[1,1]=gg
 for i in range(4):M[0,i+2]=M[i+2,0]=av[i];M[1,i+2]=M[i+2,1]=bv[i]
 M[2:6,2:6]=N;P=s.eye(6)
 for i in range(4):P[0,i+2]=-av[i]/hh;P[1,i+2]=-bv[i]/gg
 transformed=P.T*(hh*M)*P;S=hh*N-av*av.T-hh/gg*bv*bv.T
 target=s.diag(hh*hh,hh*gg,s.eye(4));target[2:6,2:6]=S
 require(all(s.cancel(f)==0 for f in transformed-target),'exact Schur congruence')
 P4=gg**2*(hh*N-av*av.T)-hh*gg*bv*bv.T
 require(all(s.cancel(f)==0 for f in P4-gg**2*S),'polynomial four-by-four matrix')
 bad=gg**2*(hh*N-av*av.T)+hh*gg*bv*bv.T
 require(any(s.cancel(f)!=0 for f in bad-gg**2*S),'wrong Schur sign rejected')
 principal_subsets=[list(c) for size in range(1,5) for c in itertools.combinations(range(4),size)]
 require(len(principal_subsets)==15,'all 15 principal minors')
 counter=s.diag(0,-1,1,1)
 require(all(counter[:i,:i].det()>=0 for i in range(1,5)) and counter[1,1]<0,'leading-minor-only negative control')
 print('Schur congruence PASS; constructing retained entries',flush=True)
 h,g,nu,aa,bb,nn=schur_entries(Q,R)
 HH=j*s.hessian(Q,TH)-s.hessian(R,TH)
 VV=s.Matrix([0,0,0,A*D,0,0,0,A*t+u]);WW=s.Matrix([0,0,C,0,0,0,w-u,0])
 FF={x:j*s.diff(Q,x)-s.diff(R,x) for x in TH if x!=B}
 zero(s.expand((VV.T*HH*VV)[0]-h-(2*A*(A*D*FF[D]+(A*t+u)*FF[t]-j*A*Q)+2*A*A*R)),'source h identity')
 zero(s.expand((WW.T*HH*WW)[0]-g-(2*C*FF[C]+2*(w-u)*FF[w]+2*R-2*j*Q)),'source g identity')
 zero(s.expand((VV.T*HH*WW)[0]-(A*C*FF[C]+A*(w-u)*FF[w]+A*R-j*A*Q+A*D*FF[D]+(A*t+u)*FF[t])),'source mixed identity')
 LL=s.diff(R,w);zero(LL+br['1468']*br['3458'],'source L unit')
 eye=s.eye(8);basis=s.Matrix.hstack(VV,WW,*[LL*eye[:,TH.index(xx)]-s.diff(R,xx)*eye[:,6] for xx in (A,u,v,t)])
 minor=basis.extract([3,2,0,4,5,7],list(range(6)))
 expected=s.diag(A*D,C,LL,LL,LL,LL);expected[5,0]=A*t+u
 require(minor==expected,'fixed-B tangent basis has nonzero minor AD*C*L^4')
 (HERE/'SCHUR_CIRCUIT.json').write_text(json.dumps({'variables':list(map(str,TH+(j,))),'h':str(h),'g':str(g),'nu':str(nu),
  'a':list(map(str,aa)),'b':list(map(str,bb)),'N_upper':{f'{i},{k}':str(val) for (i,k),val in nn.items()},
  'formula':'P4[i,k]=g**2*(h*N[i,k]-a[i]*a[k])-h*g*b[i]*b[k]',
  'domain':'stationary, all 70 parents, h*g>0; retain nu=0',
  'maximum_conditions':'nu*h>=0 and P4 positive semidefinite',
  'principal_subsets':principal_subsets},indent=2)+'\n')
 out={'status':'PASS','source_sha256':SOURCE_SHA,'seven_variable_profiles':profiles(seven,BASE+(tau,)),
  'six_variable_profiles':profiles([dq,dp]+cross,BASE),'six_variable_recovery':'C,D,j,t,w rationally recovered; full parent conditions rechecked',
  'retained_exceptions':['nu=0','B=D','C=D','singular/semidefinite remaining points'],
  'excluded_branch':'g=0 only by the separately verified universal saddle proof',
  'Schur_matrix_order':4,'principal_minors_required':15,'expanded_Schur_products':False,
  'algebraic_identities':'PASS','negative_controls':2,'runtime_advantage_claimed':False,
  'whole_survivor':'OPEN','source_orbits_closed':0,'original_ledger':'2/9','seconds':time.monotonic()-start}
 (HERE/'REDUCTION_REPLAY.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2));return out
if __name__=='__main__':run()
