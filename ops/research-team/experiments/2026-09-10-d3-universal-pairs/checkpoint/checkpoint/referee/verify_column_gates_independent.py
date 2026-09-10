"""Independent determinant/interpolation checks of both final column gates.

No producer code is imported. Polynomial identities are checked on exact
unisolvent sets after proving degree bounds from multilinear determinants;
these are complete identities, not numerical or random spot checks.
"""
from pathlib import Path
from fractions import Fraction as F
from itertools import combinations
import json,hashlib
from verify_tangent_independent import determinant,derive_normal

ROOT=Path(__file__).resolve().parents[1]
P=((1,2,3),(1,4,5),(2,4,6),(3,7,8))
Q=((5,6,7),(1,5,8),(2,6,8),(3,4,7))
assert sum(8 in t for t in P)==1 and sum(8 in t for t in Q)==2
FIXED=tuple(map(F,('7','-8','-4','-17/4','2','-3')))
NODES=((0,0),(1,0),(-1,0),(0,1),(0,-1),(1,1))

def parent(fixed,g,h,i):
    a,b,c,d,e,f=fixed
    return [[F(1),0,0,0,1,1,1,1],[0,1,0,0,1,a,d,g],
            [0,0,1,0,1,b,e,h],[0,0,0,1,1,c,f,i]]
def wall(y,support):return determinant([derive_normal(y,tuple(i-1 for i in t)) for t in support])
def bracket(y,cols):return determinant([[y[r][j-1] for j in cols] for r in range(4)])
def get_g(fixed):
    # First factor is affine because precisely one selected triple contains8.
    c=wall(parent(fixed,0,0,0),P)
    a=wall(parent(fixed,1,0,0),P)-c
    b=wall(parent(fixed,0,1,0),P)-c
    d=wall(parent(fixed,0,0,1),P)-c
    assert a!=0 and b==0
    assert (-c/a,-d/a)==(F(-8),F(-5,4))
    return lambda i:-c/a-d/a*i

def audit_full(cert):
    g=get_g(FIXED)
    # After the proved affine substitution, the second determinant has total
    # degree at most2 in(h,i). Six unisolvent evaluations prove its factorization.
    for h,i in NODES:
        y=parent(FIXED,g(F(i)),F(h),F(i))
        assert wall(y,Q)==F(3,16)*(h-10*i-32)*(67*h-115*i+1196)
    for h,i in ((0,0),(1,0),(0,1)):
        assert bracket(parent(FIXED,g(F(i)),F(h),F(i)),(2,6,7,8))==h-10*i-32
    # The other factor is forbidden everywhere in the uniform parent domain.
    h=lambda i:(115*i-1196)/F(67)
    lower=[];upper=[]
    records=cert['all_parent_brackets'];assert len(records)==70
    for cols,entry in zip(combinations(range(1,9),4),records):
        zero=bracket(parent(FIXED,g(F(0)),h(F(0)),F(0)),cols)
        one=bracket(parent(FIXED,g(F(1)),h(F(1)),F(1)),cols)
        # Parent determinant is affine in the sole moving column.
        slope=one-zero;anchor=zero-8*slope;assert anchor
        sign=1 if anchor>0 else -1;slope*=sign;intercept=sign*zero
        assert entry=={'bracket':''.join(map(str,cols)),'anchor_sign':sign,
                       'signed_slope':str(slope),'signed_intercept':str(intercept)}
        if slope>0:lower.append((-intercept/slope,entry['bracket']))
        elif slope<0:upper.append((-intercept/slope,entry['bracket']))
        else:assert intercept>0
    lo=max(x for x,_ in lower);hi=min(x for x,_ in upper)
    assert (lo,hi)==tuple(map(F,cert['interval']))==(F(-12),F(-36,5))
    ends={'lower':[s for v,s in lower if v==lo],'upper':[s for v,s in upper if v==hi]}
    assert ends==cert['endwalls']=={'lower':['3468'],'upper':['3458']}
    assert lo<F(-8)<hi
    assert cert['fiber_Hc1']=='Z' and cert['global_pair_Hc1']=='NOT_COMPUTED'
    return {'status':'PASS','full_fiber_interval':[str(lo),str(hi)],'endwalls':ends,
            'first_wall_uniquely_solves_g':True,'second_factorization_complete':True,
            'excluded_branch_is_parent_bracket':True,'fiber_Hc1':'Z','global_Hc1':'NOT_COMPUTED'}

def audit_conic(cert):
    fixed=tuple(map(F,cert['fixed_parent_coordinates']));assert fixed==tuple(map(F,('7','-8','-399/100','-17/4','2','-3')))
    g=get_g(fixed)
    f=lambda h,i:wall(parent(fixed,g(F(i)),F(h),F(i)),Q)*F(160000,3)
    c00=f(0,0);c20=(f(1,0)+f(-1,0))/2-c00;c10=(f(1,0)-f(-1,0))/2
    c02=(f(0,1)+f(0,-1))/2-c00;c01=(f(0,1)-f(0,-1))/2
    c11=f(1,1)-c00-c20-c10-c02-c01
    coeff={(2,0):c20,(1,1):c11,(1,0):c10,(0,2):c02,(0,1):c01,(0,0):c00}
    assert {str(k):str(v) for k,v in coeff.items()}==cert['conic_coefficients']
    mat=[[c20,c11/2,c10/2],[c11/2,c02,c01/2],[c10/2,c01/2,c00]]
    assert mat==[[F(x) for x in row] for row in cert['homogeneous_conic_matrix']]
    d=determinant(mat);assert d==F(cert['determinant'])!=0
    gp,hp,ip=map(F,cert['uniform_rational_column8']);assert gp==g(ip)
    y=parent(fixed,gp,hp,ip)
    assert wall(y,P)==wall(y,Q)==0
    values=[bracket(y,cols) for cols in combinations(range(1,9),4)]
    assert all(values) and [1 if x>0 else -1 for x in values]==cert['parent_signs']
    return {'status':'PASS','all_parent_brackets_nonzero':70,'conic_matrix_determinant':str(d),
            'route_refuted':'global affine-line fiber presentation for this fixed column8 projection',
            'global_pair_Hc1':'NOT_COMPUTED'}

def main():
    paths=[ROOT/'pair/HARD_COLUMN_FIBER_CERTIFICATE.json',ROOT/'pair/SMOOTH_CONIC_GATE_CERTIFICATE.json']
    full,conic=[json.loads(p.read_text()) for p in paths]
    a=audit_full(full);b=audit_conic(conic);rejected=[]
    changes=[('interval',full,audit_full),('slope',full,audit_full),('conic_coefficient',conic,audit_conic),('conic_point',conic,audit_conic)]
    for name,source,fn in changes:
        bad=json.loads(json.dumps(source))
        if name=='interval':bad['interval'][0]='-11'
        elif name=='slope':bad['all_parent_brackets'][4]['signed_slope']='1'
        elif name=='conic_coefficient':bad['conic_coefficients']['(2, 0)']='0'
        else:bad['uniform_rational_column8'][0]='0'
        try:fn(bad)
        except AssertionError:rejected.append(name)
        else:raise AssertionError('corrupted '+name+' accepted')
    print(json.dumps({'status':'PASS','full_interval_gate':a,'nondegenerate_conic_gate':b,
      'certificate_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
      'hostile_rejections':rejected,'original_obligations_closed':0,'pairwall_residue_unchanged':574},indent=2))

if __name__=='__main__':main()
