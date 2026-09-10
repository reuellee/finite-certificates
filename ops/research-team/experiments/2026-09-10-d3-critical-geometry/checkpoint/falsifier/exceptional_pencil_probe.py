from pathlib import Path
from itertools import combinations
import json,sympy as S,time
P=Path(__file__).resolve().parent;lam,u=S.symbols('lam u');xs=S.symbols('x y z w');t=S.Symbol('t');cs=S.symbols('c0:5')
D=json.loads((P/'QUAD_INERTIA.json').read_text())['records'];As={r['trial']:S.Matrix([[S.Rational(c)for c in row]for row in r['homogeneous_matrix']])for r in D}
Y=S.Matrix([[0,0,0,1,1,1,1,1],[0,1,1,0,0,3,4,5],[1,0,-1,0,2,0,-5,-6],[0,0,t,0,*xs]])
bases=list(combinations(range(8),4));brackets=[S.Poly(Y[:,J].det(),*(xs+(t,)))for J in bases]
brows=[S.Matrix([[bb.coeff_monomial(x)for x in xs+(t,)]])for bb in brackets]
def analyze_kernel(M,A,B):
 ns=M.nullspace();N=S.Matrix.hstack(*ns);rec={'nullity':len(ns),'kernel_basis':[[str(v)for v in n]for n in ns]}
 if all(n[-1]==0 for n in ns):rec['status']='whole kernel at infinity';return rec
 zero=[J for J,b in zip(bases,brows)if b*N==S.zeros(1,len(ns))]
 if zero:rec['status']='whole kernel on parent boundary';rec['parent_zero_brackets_0based']=zero;return rec
 H=N.T*B*N;rec['common_zero_restriction_matrix']=[[str(v)for v in H.row(i)]for i in range(H.rows)]
 if len(ns)>2:
  cv=S.Matrix(cs[:len(ns)]);q=S.factor((cv.T*H*cv)[0]);rec['common_zero_polynomial']=str(q)
  fac=S.factor_list(q)[1]
  if fac and all(S.Poly(f,*cs[:len(ns)]).total_degree()==1 for f,m in fac):
   parts=[]
   for f,m in fac:
    rr=S.Matrix([[S.diff(f,c)for c in cs[:len(ns)]]]);R=N*S.Matrix.hstack(*rr.nullspace())
    zeros=[J for J,b in zip(bases,brows)if b*R==S.zeros(1,R.cols)]
    status='component at infinity' if all(R[-1,k]==0 for k in range(R.cols))else 'component on parent boundary' if zeros else 'unresolved component'
    parts.append({'linear_factor':str(f),'basis':[[str(v)for v in R.col(k)]for k in range(R.cols)],'parent_zero_brackets_0based':zeros,'status':status})
   rec['linear_components']=parts
   rec['status']='all higher-kernel components excluded' if all(p['status']!='unresolved component'for p in parts)else 'unresolved higher-dimensional kernel'
  else:rec['status']='unresolved higher-dimensional kernel'
  return rec
 if len(ns)==1:
  cand=[ns[0]] if H[0,0]==0 else []
 else:
  v=u*ns[0]+ns[1];q=S.factor((v.T*B*v)[0]);rec['binary_common_zero_polynomial']=str(q)
  if q==0:
   rec['status']='unresolved identically zero kernel restriction'
   return rec
  roots=S.solve(q,u)
  cand=[v.subs(u,a)for a in roots if a.is_real is not False]
  if (ns[0].T*B*ns[0])[0]==0:cand.append(ns[0])
 points=[]
 for v in cand:
  if v[-1]==0:continue
  v=v/v[-1]
  if any(S.simplify((v.T*C*v)[0])!=0 for C in(A,B)):continue
  z=[J for J,b in zip(bases,brows)if S.simplify((b*v)[0])==0]
  points.append({'point':[str(S.simplify(x))for x in v[:4]],'parent_zero_brackets_0based':z,'actual_uniform':not z})
 rec['points']=points;rec['status']='actual uniform critical point' if any(p['actual_uniform']for p in points)else 'all finite common-zero kernel points excluded'
 return rec
start=time.time();out=[];roots_unresolved=[]
# Every point at infinity in pencil parameter space is in an individual kernel.
for trial,A in As.items():
 r=analyze_kernel(A,A,A);out.append({'kind':'individual quadric kernel','trial':trial,**r})
rows=json.loads((P/'PENCIL_SINGULAR_PROBE.json').read_text())['records']
for row in rows:
 i,j=row['trials'];A,B=As[i],As[j];M=A+lam*B
 if row.get('status')=='identically singular pencil':
  # Generic rank is four. Its exceptional parameter set is the gcd of all25 4-minors.
  g=S.Poly(0,lam)
  for rows4 in combinations(range(5),4):
   for cols4 in combinations(range(5),4):
    m=S.Poly(M[list(rows4),list(cols4)].det(method='domain-ge'),lam)
    if not m.is_zero:g=S.gcd(g,m)
  assert not g.is_zero
  g=g.monic();rt=S.ground_roots(g.as_expr(),lam)
  rem=g
  for l,mult in rt.items():rem=rem.exquo(S.Poly((lam-l)**mult,lam))
  if rem.degree()>0:roots_unresolved.append({'trials':[i,j],'polynomial':str(rem.as_expr())})
  for l in rt:out.append({'kind':'singular-pencil exceptional parameter','trials':[i,j],'lambda':str(l),'exceptional_parameter_gcd':str(S.factor(g.as_expr())),**analyze_kernel(M.subs(lam,l),A,B)})
 else:
  for point in row.get('repeated_rational_root_checks',[]):
   if point.get('nullity',0)>1:
    l=S.Rational(point['lambda']);out.append({'kind':'nonzero-pencil higher-nullity parameter','trials':[i,j],'lambda':str(l),**analyze_kernel(M.subs(lam,l),A,B)})
result={'scope':'Exact expansion of all same-data higher-nullity rational pencil parameters, all individual kernels, and gcd-detected exceptions of38 generically singular pencils','records':out,'unresolved_nonlinear_parameter_factors':roots_unresolved}
(P/'EXCEPTIONAL_PENCIL_PROBE.json').write_text(json.dumps(result,indent=2)+'\n')
from collections import Counter
print('records',len(out),'statuses',dict(Counter(r['status']for r in out)),'unresolved_parameters',roots_unresolved,'seconds',time.time()-start)
for r in out:
 if r['status'] not in ['whole kernel at infinity','whole kernel on parent boundary','all finite common-zero kernel points excluded']:print(r)
