import sympy as s,json,itertools
from pathlib import Path
P=Path(__file__).resolve().parent
record=json.loads((P.parent/'falsifier/HARD_PAIR_EQUATIONS.json').read_text())
a,b,c,d,e,f,g,h,i=s.symbols('a b c d e f g h i');vs=(a,b,c,d,e,f,g,h,i)
q1=s.sympify(record['f']);q2=s.sympify(record['g'])
fixed={a:s.Rational(7),b:-8,c:-4,d:s.Rational(-17,4),e:2,f:-3}
gsol=s.solve(q1,g)[0].subs(fixed)
conic=s.factor(q2.subs(fixed).subs(g,gsol));num=s.fraction(conic)[0]
t=s.symbols('t');hs=2+t*(i+3)
param=s.factor(num.subs(h,hs));isol=s.solve(param/(i+3),i)
print('g(i)=',gsol,'conic=',conic,'pencil=',param,'i=',isol,flush=True)
assert len(isol)==1
ip=isol[0];hp=s.factor(hs.subs(i,ip));gp=s.factor(gsol.subs(i,ip))
Y=s.Matrix([[1,0,0,0,1,1,1,1],[0,1,0,0,1,a,d,g],[0,0,1,0,1,b,e,h],[0,0,0,1,1,c,f,i]]).subs(fixed)
base=[s.Rational(x) for x in json.loads((P.parent/'falsifier/HARD_PAIR_POINT.json').read_text())['point']]
t0=s.factor((base[7]-2)/(base[8]+3))
YY=Y.subs({g:gp,h:hp,i:ip})
brackets=[];roots=set()
for J in itertools.combinations(range(8),4):
 B=s.factor(Y[:,J].det());Bt=s.factor(B.subs({g:gp,h:hp,i:ip}));nv,dv=s.fraction(Bt)
 assert not Bt==0
 forpoly=[]
 for poly in(nv,dv):
  if s.degree(poly,t)>0:
   sol=s.solve(poly,t)
   for r in sol:
    if r.is_real:roots.add(r)
 brackets.append({'labels':''.join(str(j+1) for j in J),'function':str(Bt),'anchor_sign':int(s.sign(Bt.subs(t,t0)))})
assert s.factor(q1.subs(fixed).subs({g:gp,h:hp,i:ip}))==0
assert s.factor(q2.subs(fixed).subs({g:gp,h:hp,i:ip}))==0
roots=sorted(roots,key=float)
below=[r for r in roots if r<t0];above=[r for r in roots if r>t0]
lo=max(below) if below else '-infinity';hi=min(above) if above else '+infinity'
print('anchor t=',t0,'residence interval=',lo,hi,'critical roots=',roots,flush=True)
out={'status':'EXACT_ONE_COLUMN_FIBER_COMPONENT','scope':'hard50+50pair,sevenfixedparentcolumns;notglobalpaircohomology',
'fixed_coordinates':{str(k):str(v) for k,v in fixed.items()},'conic_equation':str(conic),
'parameterization':{'g':str(gp),'h':str(hp),'i':str(ip)},'anchor_t':str(t0),
'component_interval':[str(lo),str(hi)],'all_real_parameter_breaks':[str(r)for r in roots],
'brackets':brackets,'component_Hc1':'Z','interpretation':'Afullfibercomponentisopeninterval,soonecolumnforgettinghasnonzeroHc1stalk;currentzeroHc1fibertemplatecannotextend.'}
(P/'HARD_CONIC_FIBER.json').write_text(json.dumps(out,indent=2)+'\n')
