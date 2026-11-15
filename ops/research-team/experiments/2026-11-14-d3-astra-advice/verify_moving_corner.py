#!/usr/bin/env python3
"""Exact parent and block-1 witness certificate for one moving corner curve.
This is a 1-dimensional boundary path, not an H1 comparison prism or D3 proof.
"""
from pathlib import Path
from hashlib import sha256
from itertools import combinations
import sys
import numpy as np
import sympy as s
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'ai/omreal'))
import verify_diag3_row2599_p01_tangent_collar as k
import verify_diag3_row2599_p01_comparison_prism as p
import verify_diag3_row2599_common_proper_escape as c
import verify_diag3_row2599_p12_p20_comparison_prisms as pairs
import prototype_koszul_circuits as koszul
import verify_diag3_joined_flow_triangle as joined
import verify_diag2_moving_witness_shear as moving
assert sha256(p.SOURCE.read_bytes()).hexdigest()==p.SOURCE_SHA256
b,r,q=s.symbols('b r q',real=True);R=s.Rational
with np.load(p.SOURCE,allow_pickle=False) as z: raw=s.Matrix(z['chart_matrix'][0].tolist())
M=raw.copy(); a=R(k.WITNESS_WALL+k.TANGENT_ADVANCE)
M[:,6]+=a*R(c.ENDPOINT)*s.Matrix(c.EXPECTED_DIRECTION)
M[0,5]+=b
M[:,1]-=r*M[:,7]
M[:,0]-=q*M[:,1]
det=lambda I:s.factor(M[:,[x-1 for x in I]].det())
f=det((1,3,6,7));g=det((2,4,6,7))
rr=s.factor(s.solve(g,r)[0]);qq=s.factor(s.solve(s.factor(f.subs(r,rr)),q)[0])
assert s.factor(f.subs({r:rr,q:qq},simultaneous=True))==0
assert s.factor(g.subs(r,rr))==0
b0=R(k.OFFPLANE_ENDPOINT); target=R(c.ROOT_ENDPOINTS[1])
assert 0<b0<2<25
assert qq.subs(b,b0)==0 and s.cancel(rr.subs(b,b0)-R(k.ROOT_TARGET))==0
num,den=s.fraction(s.factor(s.diff(qq,b)))
assert all(v>0 for v in s.Poly(num,b).all_coeffs())
assert all(v>0 for v in s.Poly(den,b).all_coeffs())
assert qq.subs(b,25)<target<qq.subs(b,26)
targetnum=s.fraction(s.cancel(qq-target))[0]
assert s.degree(targetnum,b)>0

def roots(expr):
    if not expr.has(b):return []
    return [(interval,m) for interval,m in s.polys.polytools.intervals(s.Poly(expr,b),eps=R(1,10000)) if interval[1]>=b0 and interval[0]<=26]
zeros=[]
for I in combinations(range(1,9),4):
    pp=s.factor(det(I).subs({r:rr,q:qq},simultaneous=True))
    if pp==0:zeros.append(I);continue
    num,den=s.fraction(s.cancel(pp));assert not roots(den),I
    original=raw[:,[x-1 for x in I]].det();assert pp.subs(b,2)*original>0,I
    rs=roots(num)
    if I==(1,3,5,8):
        assert len(rs)==1 and s.rem(num,targetnum,b)==0
    else:assert not rs,(I,rs)
assert zeros==[(1,3,6,7),(2,4,6,7)]
assert tuple(pairs.SAFE_SUPPORTS[1])==(2,9,27,30,35)
Y=M.subs({r:rr,q:qq},simultaneous=True);cols=[]
for idx in pairs.SAFE_SUPPORTS[1]:
    U=Y[:,[j-1 for j in koszul.TRIPLES[idx]]]
    cols.append(s.Matrix([(-1)**(i+5)*U[[j for j in range(4) if j!=i],:].det()*moving.signature_sign(joined.SIGNATURES[1],idx) for i in range(4)]))
C=s.Matrix.hstack(*cols)
cof=[s.factor((-1)**i*C[:,[j for j in range(5) if j!=i]].det()) for i in range(5)]
for z in cof:
    num,den=s.fraction(s.cancel(z));assert z.subs(b,2)<0
    assert not roots(num) and not roots(den)
assert all(s.cancel(x)==0 for x in C*s.Matrix(cof))
print('PASS unique endpoint 25<b*<26; correct canonical corner at b0; [1367]=[2467]=0')
print('PASS other parent signs on [b0,b*), with [1358]=0 exactly at b*')
print('PASS five strictly positive block-1 Gordan weights after common sign change')
print('SCOPE: one boundary path; no H1 prism or global claim; ledger 2/9')
