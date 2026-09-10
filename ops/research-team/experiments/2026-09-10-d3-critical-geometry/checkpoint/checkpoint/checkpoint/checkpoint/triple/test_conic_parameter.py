import pickle,sympy as s,json
from pathlib import Path
P=Path(__file__).parent;z=pickle.load(open(P/'derived.pkl','rb')); a,b,c,d,e,f,g,h,i=x=z['x'];q=z['q'];t=s.symbols('t')
cg=(b*f-t)/e
ag=s.cancel(-q[1].subs(a,0)/s.diff(q[1],a))
line=s.cancel(q[2].subs(a,ag));line=s.cancel(line.subs(c,cg));line=s.cancel(line.subs(d,(b*(i-f)+f*g)/i));F=s.Poly(line.as_numer_denom()[0],t,b,e,f,g,h,i); co,F=F.primitive()
print('conic parametrized graph numerator terms',len(F.terms()),'degree',F.total_degree(),flush=True)
print('coordinate degrees',{str(v):F.degree(v)for v in F.gens},flush=True)
for v in F.gens:
 if F.degree(v)==1:print('affine slope',v,s.factor(s.diff(F.as_expr(),v)),flush=True)
print('denominator',s.factor(line.as_numer_denom()[1]),flush=True)
(P/'CONIC_PARAMETER_GATE.json').write_text(json.dumps({'status':'exact_symbolic_gate','parameter':'t=bf-ce, a parent bracket unit','term_count':len(F.terms()),'total_degree':F.total_degree(),'coordinate_degrees':{str(v):F.degree(v)for v in F.gens},'affine_variables':[str(v)for v in F.gens if F.degree(v)==1],'scope':'Named hardcanary rational conic chart only; no global escape follows if no affine variable exists.'},indent=2)+'\n')
