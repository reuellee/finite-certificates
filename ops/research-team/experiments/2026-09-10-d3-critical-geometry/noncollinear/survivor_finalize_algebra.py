from pathlib import Path
import json,sympy as s
root=Path(__file__).resolve().parent;o=json.loads((root/'survivor_ELIMINATION.json').read_text());vs=s.symbols('A B C D u v w t');A,B,C,D,u,v,w,t=vs
E=s.sympify(o['resultant_factorization'][0]['factor']);ep=s.Poly(E,*vs)
print('degrees',dict(zip(map(str,vs),ep.degree_list())),flush=True)
print('critical derivative termcounts',{str(x):len(ep.diff(x).terms()) for x in (u,v,t)},flush=True)
p=json.loads((root/'survivor_CONTRACTION_CHART.json').read_text());Q=s.sympify(p['raw_factors']['Q']);R=s.sympify(p['raw_factors']['R']);L=s.sympify(o['R_w']);N=s.sympify(o['R_at_w_zero']);coeff=s.Poly(Q,w)
structured=coeff.nth(2)*N**2-coeff.nth(1)*N*L+coeff.nth(0)*L**2
assert s.Poly(s.expand(structured),*vs)==ep
print('structured resultant exact',flush=True)
o['residual_coordinate_degrees']={str(x):int(d) for x,d in zip(vs,ep.degree_list()) if x!=w};o['critical_equations']=['E=0','dE/du=0','dE/dv=0','dE/dt=0'];o['critical_derivative_termcounts']={str(x):len(ep.diff(x).terms()) for x in (u,v,t)};o['Q_w_coefficients']={str(j):str(s.factor(coeff.nth(j))) for j in range(3)};o['resultant_structure_verified']=True;o['Q_t_nonzero_on_uniform_Q_wall']='Geometric ordinary-circuit argument; not asserted to be a global polynomial unit.';o['projected_leaf_coincidence_C_equals_D_retained']=True
(root/'survivor_ELIMINATION.json').write_text(json.dumps(o,indent=2)+'\n')
