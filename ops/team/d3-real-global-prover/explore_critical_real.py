"""Bounded numerical discovery of full height-b critical points; no certificates."""
from pathlib import Path
import json,hashlib,time,resource
resource.setrlimit(resource.RLIMIT_AS,(4*1024**3,4*1024**3))
import numpy as np
import sympy as s
from scipy.optimize import root
from itertools import combinations

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
src=ROOT/'ai/omreal/data/DIAG3_triple_fullspace_critical_h1.json'
raw=src.read_bytes()
pin='c9244a47ded5736e7afe724a9914e75631a22b78653442e88c14f5c397919eb8'
assert hashlib.sha256(raw).hexdigest()==pin
rec=json.loads(raw)
X=s.symbols(' '.join(rec['variables']))
q=[s.Add(*(v*s.prod(x**k for x,k in zip(X,m)) for v,m in r['terms'])) for r in rec['equations'][:3]]
lam,mu=s.symbols('lam mu')
J=s.Matrix(q).jacobian(X)
system=s.Matrix(q+[lam*J[0,k]+mu*J[1,k]+J[2,k] for k in range(9) if k!=1])
var=X+(lam,mu)
evaluate=s.lambdify([var],system,'numpy',cse=True)
deriv=s.lambdify([var],system.jacobian(var),'numpy',cse=True)
parent=s.eye(4).row_join(s.ones(4,1)).row_join(s.Matrix([[1,1,1],[X[0],X[3],X[6]],[X[1],X[4],X[7]],[X[2],X[5],X[8]]]))
brackets=[s.expand(parent[:,idx].det()) for idx in combinations(range(8),4)]
walls=s.lambdify([X],brackets,'numpy',cse=True)
qeval=s.lambdify([X],q,'numpy',cse=True)
jac=s.lambdify([X],J,'numpy',cse=True)
seed=np.array([-19/28,-23/7,-27/14,-5,-4,-3,-1,2,4],float)
rng=np.random.default_rng(9052026)
results=[]
start=time.monotonic()
for trial in range(120):
    if time.monotonic()-start>145:break
    initial=seed+rng.normal(size=9)*([0.15,0.7,1.8,3.0][trial%4])
    j=jac(initial)
    coeff=np.linalg.solve(j[:2,[0,3]].T,-j[2,[0,3]])
    z=np.r_[initial,coeff]
    sol=root(lambda z:evaluate(z).reshape(11),z,jac=lambda z:deriv(z),method='hybr',options={'maxfev':1000,'xtol':1e-10})
    residual=float(np.max(np.abs(evaluate(sol.x))))
    point=sol.x[:9]
    wallvalues=np.array(walls(point))
    margin=float(np.min(np.abs(wallvalues)))
    row={'trial':trial,'initial_point_11_variables':z.tolist(),'success':bool(sol.success),'residual':residual,'minimum_parent_bracket_absolute':margin,'nfev':int(sol.nfev)}
    if residual<1e-6 and margin>1e-5:
        row['candidate']=sol.x.tolist()
        row['parent_signs']=np.sign(wallvalues).astype(int).tolist()
        print('CANDIDATE',json.dumps(row),flush=True)
    results.append(row)
initials=np.array([r['initial_point_11_variables'][:9] for r in results])
out={'kind':'numerical_discovery_only','source_sha256':pin,'system':'q1=q2=q3=0; lam*dq1+mu*dq2+dq3=0 in all columns except b',
     'seed':9052026,'initial_point_rule':'seed source point plus independent standard normal samples times cyclic scales 0.15,0.7,1.8,3.0; multipliers initialized using columns a,d',
     'seed_source_point':seed.tolist(),'realized_initial_coordinate_minima':initials.min(axis=0).tolist(),'realized_initial_coordinate_maxima':initials.max(axis=0).tolist(),
     'root_method':'scipy.optimize.root hybr, analytic Jacobian','root_options':{'maxfev':1000,'xtol':1e-10},
     'candidate_thresholds':{'maximum_absolute_equation_residual_strictly_below':1e-6,'minimum_absolute_parent_bracket_strictly_above':1e-5},
     'trials':len(results),'elapsed_seconds':time.monotonic()-start,'records':results,'consequence':'No missed-point, emptiness, source-orbit, or topological conclusion follows from any numerical outcome.'}
(HERE/'CRITICAL_NUMERICAL_DISCOVERY.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k!='records'},indent=2),flush=True)
print('valid_candidates',sum('candidate' in r for r in results),flush=True)
