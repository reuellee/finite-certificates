exec(open(__file__.replace('scaling.py','explore.py')).read().split('T=s.symbols')[0])
m,c,l=s.symbols('m c l')
new=s.expand(psi.subs({C:B*c,L:B*l,beta:m/B},simultaneous=True))
print('degrees B',s.degree(new,B),'factors',s.factor(new),flush=True)
