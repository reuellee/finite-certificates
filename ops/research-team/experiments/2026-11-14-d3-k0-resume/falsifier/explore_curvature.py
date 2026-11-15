import sympy as s,json,time
j=json.load(open('/workspace/scratch/1959cf51fea0/input/LIFTED_SYSTEM.json'));vs=s.symbols(' '.join(j['variables']));A,B,C,x,beta,L,lam=vs
parse=lambda rows:s.Poly.from_dict({tuple(e):s.Rational(c) for e,c in rows},vs).as_expr()
psi,E=[parse(rows) for rows in j['equations'][:2]]
print('psi degrees C L',s.degree(psi,C),s.degree(psi,L),flush=True)
h=s.expand(s.diff(psi,C,2)*s.diff(psi,L,2)-s.diff(psi,C,L)**2)
print('Hessian CL determinant factor',s.factor(h),flush=True)
# Since E independent of C,L, treat remaining variables as rational parameters.
t=time.time();G=s.groebner([psi,s.diff(psi,C),s.diff(psi,L)],C,L,domain=s.QQ.frac_field(A,B,x,beta))
print('basis',time.time()-t,len(G.polys),flush=True)
for p in G.polys:print(s.factor(p.as_expr()),flush=True)
