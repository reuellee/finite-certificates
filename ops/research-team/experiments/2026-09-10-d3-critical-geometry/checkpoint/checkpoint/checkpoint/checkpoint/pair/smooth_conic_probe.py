import sympy as s,json,itertools
from pathlib import Path
P=Path(__file__).resolve().parent
record=json.loads((P.parent/'falsifier/HARD_PAIR_EQUATIONS.json').read_text())
a,b,c,d,e,f,g,h,i=s.symbols('a b c d e f g h i');t=s.symbols('t')
q1=s.sympify(record['f']);q2=s.sympify(record['g'])
fix={a:s.Rational(7),b:-8,c:s.Rational(-399,100),d:s.Rational(-17,4),e:2,f:-3}
gsol=s.solve(q1,g)[0].subs(fix);q=s.factor(q2.subs(fix).subs(g,gsol));N=s.fraction(q)[0]
poly=s.Poly(N,h,i);C=s.Matrix([[poly.coeff_monomial(h*h),poly.coeff_monomial(h*i)/2,poly.coeff_monomial(h)/2],[poly.coeff_monomial(h*i)/2,poly.coeff_monomial(i*i),poly.coeff_monomial(i)/2],[poly.coeff_monomial(h)/2,poly.coeff_monomial(i)/2,poly.coeff_monomial(1)]])
assert C.det()!=0
hsub=2+t*(i+3);R=s.factor(N.subs(h,hsub));I=s.solve(s.cancel(R/(i+3)),i)[0];H=s.factor(hsub.subs(i,I));G=s.factor(gsol.subs(i,I));t0=s.Rational(450,67)
Y=s.Matrix([[1,0,0,0,1,1,1,1],[0,1,0,0,1,a,d,g],[0,0,1,0,1,b,e,h],[0,0,0,1,1,c,f,i]]).subs(fix)
YY=Y.subs({g:G,h:H,i:I});anchor=[G.subs(t,t0),H.subs(t,t0),I.subs(t,t0)]
roots=set();bs=[]
for J in itertools.combinations(range(8),4):
 B=s.factor(YY[:,J].det());sg=s.sign(B.subs(t,t0));assert sg
 bs.append((B,sg))
 n,dn=s.fraction(B)
 for z in(n,dn):
  if s.degree(z,t)>0:
   for r in s.solve(z,t):
    if r.is_real:roots.add(r)
roots=sorted(roots,key=lambda z:float(z.evalf(20)))
allowed=[]
for k in range(len(roots)+1):
 low=roots[k-1]if k else -s.oo;high=roots[k]if k<len(roots)else s.oo
 if low is -s.oo:test=high-1
 elif high is s.oo:test=low+1
 else:test=(low+high)/2
 vals=[s.sign(B.subs(t,test))==sg for B,sg in bs]
 if all(vals):allowed.append((str(low),str(high)))
print('conic=',q,'det=',C.det(),'anchor=',anchor,'intervals=',allowed,flush=True)
out={'status':'SMOOTH_CONIC_FIXED_BASE_DISCRIMINATOR','fixed_base':{str(k):str(v)for k,v in fix.items()},'conic':str(q),'conic_matrix':[[str(x)for x in C.row(r)]for r in range(3)],'conic_matrix_det':str(C.det()),'rational_uniform_column8':[str(x)for x in anchor],'parent_break_count':len(roots),'admissible_parameter_intervals':allowed,'sampling_warning':'Rootorderuseshighprecisiondiscoveryordering;notanacceptedglobalfibercomponentcertificate','conclusion':'Nondegenerateconicrulesoutuniformparent-unit-times-linearrepresentationforthisforget8projection.'}
(P/'SMOOTH_CONIC_PROBE.json').write_text(json.dumps(out,indent=2)+'\n')
