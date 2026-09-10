import sympy as s,json,time
from pathlib import Path
P=Path(__file__).resolve().parent
r=json.loads((P.parent/'falsifier/HARD_PAIR_EQUATIONS.json').read_text())
a,b,c,d,e,f,g,h,i=s.symbols('a b c d e f g h i');v=(a,b,c,d,e,f,g,h,i)
q1=s.sympify(r['f']);q2=s.sympify(r['g'])
gsol=s.solve(q1,g)[0]
start=time.time();rest=s.factor(q2.subs(g,gsol));print('factor=',rest,flush=True)
num,den=s.fraction(rest);fac=s.factor_list(num)
print('factors=',[(s.total_degree(z),s.Poly(z,h,i).total_degree(),str(z)) for z,k in fac[1]],flush=True)
(P/'GENERAL_COLUMN8_FACTORIZATION.json').write_text(json.dumps({'q1_gsolve':str(gsol),'q2_after':str(rest),'denominator':str(den),'numerator_factors':[{'polynomial':str(z),'power':k,'column8_degree':s.Poly(z,h,i).total_degree()}for z,k in fac[1]],'seconds':time.time()-start},indent=2)+'\n')
