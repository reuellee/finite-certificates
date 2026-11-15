#!/usr/bin/env python3
"""Bounded exact-point screen only; NOT a full surface certificate."""
from pathlib import Path
from itertools import combinations
import sys
import numpy as np
import sympy as s
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT/'ai/omreal'))
import verify_diag3_row2599_p01_tangent_collar as k
import verify_diag3_row2599_p01_comparison_prism as p
import verify_diag3_row2599_common_proper_escape as c
b,r,q,w,t=s.symbols('b r q w t',real=True);R=s.Rational
with np.load(p.SOURCE,allow_pickle=False) as z: raw=s.Matrix(z['chart_matrix'][0].tolist())
M=raw.copy();M[:,6]+=R(k.WITNESS_WALL+k.TANGENT_ADVANCE)*R(c.ENDPOINT)*s.Matrix(c.EXPECTED_DIRECTION);M[0,5]+=b;M[:,1]-=r*M[:,7];M[:,0]-=q*M[:,1]
f=M[:,[0,2,5,6]].det();g=M[:,[1,3,5,6]].det()
rr=s.factor(s.solve(g,r)[0]);qq=s.factor(s.solve(f.subs(r,rr),q)[0]);beta=s.factor(s.solve(f.subs(b,w),w)[0]);root0=R(c.ROOT_ENDPOINTS[0]);rrt=root0+t*(rr-root0)
B=s.factor(beta.subs({q:qq,r:rrt},simultaneous=True))
Y=M.subs({q:qq,r:rrt,b:B},simultaneous=True)
for bt in [2,10,25]:
 for tt in [R(0),R(1,4),R(1,2),R(3,4),R(1)]:
  T=Y.subs({b:bt,t:tt}); assert not any(x.has(s.zoo,s.nan) for x in T)
  for I in combinations(range(8),4):
   assert T[:,I].det()*raw[:,I].det()>=0,(bt,tt,I)
print('PASS 15 rational surface points have no reversed parent determinant')
print('NO full parameter-domain or Gordan witness proof')
