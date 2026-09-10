import sympy as s,pickle,time,json
from pathlib import Path
P=Path(__file__).parent; z=pickle.load(open(P/'derived.pkl','rb')); x=z['x'];a,b,c,d,e,f,g,h,i=x;q=z['q']
dgraph=(b*(i-f)+f*g)/i
r=[s.cancel(y.subs(d,dgraph)).as_numer_denom()[0] for y in q[1:]]
C0=r[1].subs(c,0);C1=s.diff(r[1],c)
p=s.Poly(r[0],c); N=s.Poly(s.expand(p.nth(0)*C1**2-p.nth(1)*C0*C1+p.nth(2)*C0**2),a,b,e,f,g,h,i)
co,nprim=N.primitive(); print('N primitive',len(nprim.terms()),'degree',nprim.total_degree(),flush=True)
# Strip elementary coordinate/parent factors detected by polynomial division.
vars=(a,b,e,f,g,h,i)
for fac in [i,g,h-1,i-f,b*(i-f)+f*g-e*i]:
 count=0
 while True:
  quo,rem=s.div(nprim,s.Poly(fac,*vars))
  if not rem.is_zero:break
  nprim=quo;count+=1
 if count:print('stripped',fac,count,flush=True)
N=nprim.as_expr();pa=s.Poly(N,a); A,B,C=[pa.nth(k) for k in [2,1,0]];print('abc termcounts',[len(s.Poly(k,b,e,f,g,h,i).terms()) for k in [A,B,C]],flush=True)
Disc=s.Poly(s.expand(B*B-4*A*C),b,e,f,g,h,i)
units=[i,g,h-1,i-f,b*(i-f)+f*g-e*i]
stripped=[]
for fac in units:
 count=0
 while True:
  quo,rem=s.div(Disc,s.Poly(fac,b,e,f,g,h,i))
  if not rem.is_zero:break
  Disc=quo;count+=1
 if count:stripped.append((str(fac),count))
print('R terms',len(Disc.terms()),'degree',Disc.total_degree(),'removed',stripped,flush=True)
R=Disc.as_expr(); facs=s.factor_list(R);print('irreducible factor stats',[(len(s.Poly(k,b,e,f,g,h,i).terms()),s.Poly(k,b,e,f,g,h,i).total_degree(),v)for k,v in facs[1]],flush=True)
data={'x':x,'q':q,'dgraph':dgraph,'r':r,'C0':C0,'C1':C1,'P':N,'ABC':[A,B,C],'Delta_primitive':R,'units_stripped':stripped}
pickle.dump(data,open(P/'height_discriminant.pkl','wb'))
def terms(v,vs):return [[int(co),list(mon)]for mon,co in s.Poly(v,*vs).terms()]
out={'variables':list(map(str,(a,b,e,f,g,h,i))),'height':'b','d_graph':str(dgraph),'c_graph':str(s.cancel(-C0/C1)),'quadratic':terms(N,(a,b,e,f,g,h,i)),'discriminant_variables':list(map(str,(b,e,f,g,h,i))),'discriminant_primitive':terms(R,(b,e,f,g,h,i)),'units_stripped':stripped}
(P/'HEIGHT_DISCRIMINANT_SYSTEM.json').write_text(json.dumps(out,indent=2)+'\n')
