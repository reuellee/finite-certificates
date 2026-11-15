#!/usr/bin/env python3
"""Exact counterexample to a fixed-collar gauge-aware shear ramp.
Not a counterexample to a moving-corner homotopy or to 9DVL.
"""
from pathlib import Path
from fractions import Fraction as F
from hashlib import sha256
import sys
import numpy as np
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'ai/omreal'))
import verify_diag3_row2599_p01_comparison_prism as p
import verify_diag3_row2599_common_proper_escape as c
import verify_diag3_row2599_p12_p20_comparison_prisms as pairs
import verify_diag2_moving_witness_shear as moving
assert sha256(p.SOURCE.read_bytes()).hexdigest()==p.SOURCE_SHA256
with np.load(p.SOURCE,allow_pickle=False) as z: raw=z['chart_matrix'][0]
base=moving.parent_brackets(raw)
for index,M in enumerate(p.build_collar(raw)):
    d=pairs.determinant(M,(2,3,5,8)); n=pairs.determinant(M,(1,3,5,8))
    assert min(c.mp_bernstein(d))>0
    B=[[dict(x) for x in row] for row in M]; s={(0,1,0):F(1)}
    for r in range(4):
        B[r][0]=c.mp_add(c.mp_multiply(d,M[r][0]),c.mp_scale(c.mp_multiply(c.mp_multiply(s,n),M[r][1]),-1))
    end=p.restrict_matrix(B,1,1)
    assert not pairs.determinant(end,(1,3,5,8))
    if index==1:
        bracket=pairs.determinant(B,(1,3,6,7))
        signed=c.mp_scale(bracket,1 if base[(1,3,6,7)]>0 else -1)
        value=sum(coeff*F(0)**ex[0]*F(1,4)**ex[1] for ex,coeff in signed.items())
        assert value<0
        print('stage=1 t=0 shear_fraction=1/4 signed_[1367] < 0')
        print('signed_[1367]=',value)
print('PASS: positive gauge on all five stages; forced wall verified; fixed-collar ramp fails parent sign')
print('SCOPE: no global obstruction or ledger advancement')
