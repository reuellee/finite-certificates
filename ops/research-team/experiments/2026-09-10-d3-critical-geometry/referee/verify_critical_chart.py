#!/usr/bin/env python3
"""Independent exact whole-chart classification for the covered witness triple."""
from pathlib import Path
import hashlib,json,sympy as S
from verify_noncollinear_independent import det,raw
ROOT=Path(__file__).resolve().parent.parent

def main():
    u,v,w,t,x,y,z,k=S.symbols('u v w t x y z k')
    Y=[[1,0,0,0,u,v,w,t],[0,1,0,0,2*u-1,2*v-3,2*w+x,2*t+z],[0,0,1,0,2*u-1,2*v,2*w+y,2*t+k],[0,0,0,1,1,3,2,5]]
    supports=[['123','145','246','356'],['123','146','248','378'],['126','145','248','378']]
    P,F,R=[S.expand(raw(Y,s)) for s in supports]
    assert P==0
    H=t*(x-2)-w*(z-5)
    assert S.expand(R-(2*u-1)*F-3*(k+2*t)*(2*u-1)*H)==0
    C=3*(2*t-5*w)*(k+2*t);L=S.diff(F,v)
    assert S.expand(F-v*L-C)==0 and S.diff(L,v)==0
    units={'1245':-(2*u-1),'1248':-(k+2*t),'2346':-v,'2378':-(2*t-5*w)}
    for key,expected in units.items():
        assert S.expand(det([[row[int(j)-1] for j in key] for row in Y])-expected)==0
    assert [S.diff(H,a) for a in [u,v,w,t]]==[0,0,5-z,x-2]
    assert S.expand(F.subs({x:2,z:5,k:-6})-6*(2*t-5*w)*(t+2*v-3))==0
    # Full coefficient equality holds exactly for x=2,z=5: integral-domain
    # cancellation leaves H, whose two independent coefficients are explicit.
    coeff=S.Poly(H,u,v,w,t).coeffs();assert set(coeff)=={5-z,x-2}
    out={'verdict':'ACCEPT_FULL_WITNESS_CHART_CRITICAL_CLASSIFICATION','supports':supports,'raw_P':str(P),'raw_Q':str(F),'raw_R':str(R),'H':str(H),'C':str(C),'F_v':str(L),'units':{a:str(b) for a,b in units.items()},'critical_projected_base':['x=2','z=5'],'argument':'On F=0, F_v=-C/v is a parent unit. Outside x=2,z=5, dH is nonzero with zero v coordinate, so rank(dF,dH)=2; on that base it is1.','method':'Independent permutation determinants and symbolic simplification; no producer imports.','scope':'Full accepted P48 chart for this already-covered support triple and transported sign sectors. No general classification or new source count.'}
    (ROOT/'referee/CRITICAL_CHART_REPLAY.json').write_text(json.dumps(out,indent=2)+'\n')
    print(out['verdict'])
if __name__=='__main__':main()
