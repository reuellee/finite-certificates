#!/usr/bin/env python3
"""Bounded local countercheck: literal stored collar, constant root shear.

This checks only [1358], not a full candidate homotopy or theorem.
"""
from pathlib import Path
import hashlib,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'ai/omreal'))
import verify_diag3_row2599_p01_comparison_prism as p
import verify_diag3_row2599_common_proper_escape as c
import verify_diag3_row2599_p12_p20_comparison_prisms as pairs
assert hashlib.sha256(p.SOURCE.read_bytes()).hexdigest()==p.SOURCE_SHA256
with np.load(p.SOURCE,allow_pickle=False) as z: raw=z['chart_matrix'][0]
zeros=[]
for i,m in enumerate(p.build_collar(raw)):
    M=[[dict(x) for x in row] for row in m]
    for r in range(4):
        M[r][0]=c.mp_add(M[r][0],c.mp_scale(M[r][1],-c.ROOT_ENDPOINTS[1]))
    poly=pairs.determinant(M,(1,3,5,8))
    zeros.append(not poly)
    print(f'stage={i} wall_1358_identically_zero={not poly} terms={len(poly)}')
assert zeros==[True,True,False,False,False]
print('PASS scoped negative test; gauge-aware shear remains untested; ledger 2/9')
