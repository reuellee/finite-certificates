from pathlib import Path
import json,sympy as S,time
P=Path(__file__).resolve().parent;D=json.loads((P/'DEFORMED_QUADRATICS.json').read_text());r={d['trial']:d for d in D['records']};x,y,z,w,s=S.symbols('x y z w s');Q=S.sympify(r[10]['residual_factors'][0]['polynomial']);ys=S.solve(Q,y)[0];F=S.sympify(r[13]['residual_factors'][0]['polynomial']);N=S.fraction(S.factor(S.together(F.subs(y,ys))))[0];records=[]
for sv in [S.Integer(2),S.Rational(-9,8),S.Integer(3),S.Integer(9),S.Integer(-3),S.Rational(3,5),S.Rational(-9,5)]:
 start=time.time();NN=N.subs(s,sv);disc=S.discriminant(NN,z);G=S.groebner([disc,S.diff(disc,x),S.diff(disc,w)],x,w);assert G.reduce(w**6)[1]==0
 records.append({'parameter':str(sv),'restricted_polynomial':str(S.factor(NN)),'z_discriminant':str(disc),'critical_discriminant_groebner_basis':[str(S.factor(p.as_expr()))for p in G.polys],'w6_remainder':'0','excluded_parent_bracket':'[1248]=-w'})
 print('PASS s=',sv,'critical discriminant ideal forces w=0; seconds',round(time.time()-start,2),flush=True)
(P/'CUBIC13_TARGET_NULL.json').write_text(json.dumps({'scope':'Seven exact parameter values only, one quadratic/cubic support pair; no statement at other parameter values','Q_support_1based':['125','136','248','378'],'R_support_1based':['135','237','456','678'],'records':records},indent=2)+'\n')
