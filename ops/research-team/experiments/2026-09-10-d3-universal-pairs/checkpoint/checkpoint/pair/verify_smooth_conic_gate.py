#!/usr/bin/env python3
"""Exact populated nonsingular conic gate; no numerical topology inference."""
from fractions import Fraction as F
from itertools import combinations
from pathlib import Path
import json
from verify_hard_column_fiber import p,add,mul,scale,det,derived,ev
P=Path(__file__).resolve().parent

def det_number(M):
 a,b,c=M[0];d,e,f=M[1];g,h,i=M[2]
 return a*(e*i-f*h)-b*(d*i-f*g)+c*(d*h-e*g)

def main():
 H={(1,0):F(1)};I={(0,1):F(1)};G=add(p(-8),scale(I,-F(5,4)))
 Y=[[p(x)for x in row]for row in [[1,0,0,0,1,1,1,1],[0,1,0,0,1,7,F(-17,4),0],[0,0,1,0,1,-8,2,0],[0,0,0,1,1,F(-399,100),-3,0]]]
 Y[1][7]=G;Y[2][7]=H;Y[3][7]=I
 f1=derived(Y,((1,2,3),(1,4,5),(2,4,6),(3,7,8)))
 f2=derived(Y,((5,6,7),(1,5,8),(2,6,8),(3,4,7)))
 conic={(2,0):F(696072),(1,1):F(-7855535),(1,0):F(-9451068),
        (0,2):F(11465000),(0,1):F(-83098930),(0,0):F(-383497152)}
 assert f1=={} and f2==scale(conic,F(3,160000))
 C=[[F(696072),F(-7855535,2),F(-9451068,2)],
    [F(-7855535,2),F(11465000),F(-83098930,2)],
    [F(-9451068,2),F(-83098930,2),F(-383497152)]]
 determinant=det_number(C)
 assert determinant==F(-144211276259416406250) and determinant!=0
 h0=F(-6168314428,177693661);i0=F(-1504387688,177693661)
 assert ev(conic,h0,i0)==0
 signs=[]
 for J in combinations(range(8),4):
  B=det([[Y[r][j]for j in J]for r in range(4)])
  value=ev(B,h0,i0);assert value!=0
  signs.append((value>0)-(value<0))
 # A nonsingular projective conic is irreducible over the algebraic closure,
 # so it cannot equal a parent-unit times an affine line on a nonempty open
 # parent chamber. The rational uniform point certifies populated geometry.
 out={'status':'PASS_EXACT_NONDEGENERATE_CONIC_DISCRIMINATOR',
 'fixed_parent_coordinates':['7','-8','-399/100','-17/4','2','-3'],
 'column8_g':'-5*i/4-8','conic_coefficients':{str(k):str(v)for k,v in conic.items()},
 'homogeneous_conic_matrix':[[str(v)for v in row]for row in C],
 'determinant':str(determinant),'uniform_rational_column8':['458935322/177693661',str(h0),str(i0)],
 'all70_parent_brackets_nonzero':True,'parent_signs':signs,
 'route_refuted':'Uniform parent-unit times affine-linear second equation for this fixed forget-column8 projection',
 'not_refuted':['Other projections','A connected-conic fiber theorem','The factor-pair Hc1 target','Original D and D3'],
 'full_fiber_component_topology':'NOT_CERTIFIED_HERE'}
 (P/'SMOOTH_CONIC_GATE_CERTIFICATE.json').write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({k:v for k,v in out.items()if k!='parent_signs'},indent=2))
if __name__=='__main__':main()
