import sympy as s,pickle,itertools,random,json
from pathlib import Path
P=Path(__file__).parent; z=pickle.load(open(P/'derived.pkl','rb'));x=z['x'];a,b,c,d,e,f,g,h,i=x;q=z['q']; rng=random.Random(9102026)
for trial in range(30):
 vals=[-5,-4,-3,-1,4] if trial==0 else rng.sample([-7,-6,-5,-4,-3,-2,-1,2,3,4,5,6,7],5)
 base=dict(zip([d,e,f,g,i],vals)); base[b]=s.cancel((d*i-f*g)/(i-f)).subs(base)
 qq=[s.expand(y.subs(base)) for y in q]; cs=s.cancel(-qq[2].subs(c,0)/s.diff(qq[2],c)); n=s.cancel(qq[1].subs(c,cs)).as_numer_denom()[0]; pa=s.Poly(n,a)
 if pa.degree()!=2: continue
 disc=s.Poly(pa.nth(1)**2-4*pa.nth(2)*pa.nth(0),h)
 for pp,mult in s.factor_list(disc)[1]:
  if pp.degree()<1:continue
  for interval, mm in s.polys.polytools.intervals(pp,eps=s.Rational(1,10**12)):
   ht=(interval[0]+interval[1])/2
   aa=s.cancel(-pa.nth(1)/(2*pa.nth(2))); cc=s.cancel(cs.subs(a,aa)); coords=[aa,base[b],cc,base[d],base[e],base[f],base[g],h,base[i]]
   if any(s.denom(co).subs(h,ht)==0 for co in coords):continue
   mat=s.Matrix([[1,0,0,0,1,1,1,1],[0,1,0,0,1,coords[0],coords[3],coords[6]],[0,0,1,0,1,coords[1],coords[4],coords[7]],[0,0,0,1,1,coords[2],coords[5],coords[8]]])
   numeric=[float(mat[:,I].det().subs(h,ht)) for I in itertools.combinations(range(8),4)]
   if min(map(abs,numeric))<1e-7:continue
   # Every rational bracket numerator coprime to minimal factor, denominator nonzero.
   brackets=[]; good=True
   for I in itertools.combinations(range(8),4):
    num,den=s.cancel(mat[:,I].det()).as_numer_denom()
    if s.gcd(s.Poly(num,h),pp).degree()>0 or s.gcd(s.Poly(den,h),pp).degree()>0:good=False;break
    brackets.append({'labels':[j+1 for j in I],'numerator':str(num),'denominator':str(den)})
   if not good:continue
   out={'kind':'exact_algebraic_uniform_projection_branch','trial':trial,'base':{str(k):str(v)for k,v in base.items()},'h_polynomial':str(pp.as_expr()),'h_interval':list(map(str,interval)),'coordinates':list(map(str,coords)),'quadratic':str(n),'coordinate_order':list(map(str,x)),'approx_min_abs_bracket':min(map(abs,numeric)),'brackets':brackets,'scope':'One actual common-factor zero point; branch of projection to d,e,f,g,h,i. Not compact component and not height-b critical.'}
   (P/'UNIFORM_BRANCH.json').write_text(json.dumps(out,indent=2)+'\n');print('FOUND trial',trial,'hpoly',pp.as_expr(),'interval',interval,'minbracket',min(map(abs,numeric)),flush=True);raise SystemExit
 print('trial',trial,'no uniform branch',flush=True)
print('NONE')
