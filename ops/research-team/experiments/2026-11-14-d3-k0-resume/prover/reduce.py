exec(open(__file__.replace('reduce.py','explore.py')).read().split('T=s.symbols')[0])
Ex=s.diff(E,x);px=s.diff(psi,x)
print('E',s.factor(E),flush=True)
for i in [4,6,7]:
 a=eq[i].coeff(lam,0);b=eq[i].coeff(lam,1)
 R=s.expand(Ex*a+px*b)
 print(i,'before',len(s.Poly(R,*vs[:-1]).terms()), 'factor',s.factor(R),flush=True)
