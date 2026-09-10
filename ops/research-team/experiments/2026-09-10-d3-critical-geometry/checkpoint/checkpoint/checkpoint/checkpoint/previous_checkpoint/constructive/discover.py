from pathlib import Path
from fractions import Fraction as Q
from itertools import combinations
import json, numpy as np
from scipy.optimize import linprog
import importlib.util
R=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('pc',R/'inputs/code/parent_certificates.py');pc=importlib.util.module_from_spec(spec);spec.loader.exec_module(pc)
f=json.loads((R/'inputs/certificates/THREE_ROW_WITNESS.json').read_text())
p=pc.matrix(f['parent']); normals=pc.geometry(f['parent'],f['parent_signs']);sig=f['signature']
a=[[v*(1 if sig>>i&1 else -1) for v in n] for i,n in enumerate(normals)]
ids=[i for i,t in enumerate(pc.TRIPLES) if 0 not in t]
E=np.array([[float(a[i][j]) for i in ids] for j in range(4)]+[[1]*len(ids)])
b=np.array([0,0,0,0,1.])
for seed in range(30):
 res=linprog(np.random.default_rng(seed).random(len(ids)),A_eq=E,b_eq=b,bounds=(0,None),method='highs')
 if not res.success:
  print('infeasible',res.message);break
 nz=[ids[i] for i,v in enumerate(res.x) if v>1e-8]
 print(seed,nz,[float(v) for v in res.x if v>1e-8])
 if len(nz)==5:
  (R/'constructive/reserve_support.json').write_text(json.dumps({'indices':nz,'seed':seed})+'\n');break
