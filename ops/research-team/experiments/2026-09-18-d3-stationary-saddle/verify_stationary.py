"""Exact real stationary-root and saddle certificate.
An isolated real algebraic solution is defined by a rational box and a
Banach-contraction proof. Numerical approximations are never acceptance tests.
"""
from pathlib import Path
import importlib.util
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('parent_source',HERE.parent/'2026-09-18-d3-parent-localized'/'verify_exact.py')
sv=importlib.util.module_from_spec(spec);spec.loader.exec_module(sv)
reconstruct,TH,j,SOURCE_SHA,zero,require=sv.reconstruct,sv.TH,sv.j,sv.SOURCE_SHA,sv.zero,sv.require
A,B,C,D,u,v,w,t=TH
SOURCE_PATH=sv.source_path()
from interval_exact import Rat,IV,terms,poly_eval
import sympy as s,json,hashlib,time

def verify(cert,negative_controls=True):
    started=time.monotonic();
    require(hashlib.sha256(SOURCE_PATH.read_bytes()).hexdigest()==SOURCE_SHA,'source hash')
    Q,R,br=reconstruct();source=json.loads(SOURCE_PATH.read_text())
    for name,f in [('Q',Q),('R',R)]:zero(f-s.sympify(source['raw_factors'][name]),'raw '+name)
    for name,f in br.items():zero(f-s.sympify(source['parent_brackets'][name]),'parent '+name)
    xs=TH+(j,); F=[Q,R]+[s.expand(j*s.diff(Q,x)-s.diff(R,x)) for x in TH if x!=B]
    require(cert['coordinates']==list(map(str,xs)),'coordinate order')
    center=list(map(Rat,cert['center']));rho=Rat(cert['radius']);require(rho>0,'radius')
    box=[IV(c-rho,c+rho) for c in center];cb=[IV(c) for c in center]
    Y=[[Rat(x) for x in row] for row in cert['preconditioner']]
    require(len(Y)==9 and all(len(row)==9 for row in Y),'matrix shape')
    Fc=[poly_eval(terms(f,xs),cb).lo for f in F]
    jac=[[poly_eval(terms(s.diff(f,x),xs),box) for x in xs] for f in F]
    # Derivative of Newton-preconditioned fixed-point map T(x)=x-YF(x).
    M=[[IV(int(i==k))-sum((Y[i][a]*jac[a][k] for a in range(9)),IV(0)) for k in range(9)] for i in range(9)]
    rowbounds=[sum(x.absmax() for x in row) for row in M]
    contraction=max(rowbounds);require(contraction<1,'strict contraction')
    correction=[abs(sum(Y[i][k]*Fc[k] for k in range(9))) for i in range(9)]
    require(all(correction[i]+rowbounds[i]*rho<rho for i in range(9)),'self map into interior')
    # Exact nonsingularity, so a fixed point of x-YF is a zero of F.
    require(s.Matrix([[s.Rational(x.numerator,x.denominator) for x in row] for row in Y]).det()!=0,'preconditioner invertible')
    brackets={name:poly_eval(terms(f,xs),box) for name,f in br.items()}
    require(all(vv.nonzero() for vv in brackets.values()),'all 70 parent conditions strict')
    L=s.diff(R,w);U=s.diff(Q,B);nu=s.expand(j*U-s.diff(R,B))
    signs={name:poly_eval(terms(expr,xs),box) for name,expr in [('L',L),('U',U),('j',j),('nu',nu)]}
    require(all(vv.nonzero() for vv in signs.values()),'regular wall intersection and multipliers')
    # V,W are tangent to both walls at the stationary root.
    V=s.Matrix([0,0,0,A*D,0,0,0,A*t+u]);W=s.Matrix([0,0,C,0,0,0,w-u,0])
    HQ=s.hessian(Q,TH);HR=s.hessian(R,TH);H=j*HQ-HR
    hV=s.expand((V.T*H*V)[0]);hW=s.expand((W.T*H*W)[0])
    VV=poly_eval(terms(hV,xs),box);WW=poly_eval(terms(hW,xs),box)
    require(VV.hi<0 and WW.lo>0,'opposite tangent quadratic signs')
    # On the regular wall intersection, Hess(B)(X,X)=-X^T(j HQ-HR)X/nu.
    bV=-VV/signs['nu'];bW=-WW/signs['nu']
    require(bV.lo>0 and bW.hi<0,'B saddle with both increase and decrease')
    # A globally valid source identity, not merely evaluation at this witness.
    zero(A*D*s.diff(Q,D)+(A*t+u)*s.diff(Q,t)-A*Q,'VQ identity')
    zero(C*s.diff(R,C)+(w-u)*s.diff(R,w)-R,'WR identity')
    qt_product=A*D*(u-v)*(v-w)*(A*w+C*u+u)*(C+v-w+1)*(A+C+u-w+1)
    zero(s.diff(Q,t)*U-Q*s.diff(Q,t,B)-qt_product,'Qt parent identity')
    Fd=j*s.diff(Q,D)-s.diff(R,D);Ft=j*s.diff(Q,t)-s.diff(R,t)
    unit=2*B*C*u**2*(A+1)*(A+u)
    zero(hV+unit-(2*A*(A*D*Fd+(A*t+u)*Ft-j*A*Q)+2*A**2*R),'global nonzero V curvature identity')
    # New safe representation of W(Q) without an unproved division by j.
    T=C*s.diff(Q,C)+(w-u)*s.diff(Q,w)
    Fc_=j*s.diff(Q,C)-s.diff(R,C);Fw=j*s.diff(Q,w)-s.diff(R,w)
    zero(L*T-(s.diff(Q,w)*(C*Fc_+(w-u)*Fw+R)-T*Fw),'parent unit LT provenance')
    Xi=(B+u-v)*(A*t+u)+D*u*(B+1)
    g=2*j*(A+1)*(u-v)*Xi
    zero(hW-g-(2*C*Fc_+2*(w-u)*Fw+2*R-2*j*Q),'global W curvature')
    cross=s.expand((V.T*H*W)[0])
    zero(cross-(A*C*Fc_+A*(w-u)*Fw+A*R-j*A*Q+A*D*Fd+(A*t+u)*Ft),'global mixed curvature')
    factors=set()
    for f in br.values():
        for factor,power in s.factor_list(f,*TH)[1]:
            factors.add(str(s.Poly(factor,*TH).monic().as_expr()))
    require(len(factors)==61,'61 parent factors')
    for factor in [B,C,u,A+1,A+u]:
        require(str(s.Poly(factor,*TH).monic().as_expr()) in factors,'V curvature parent unit')
    out={'status':'PASS','certificate_type':'rational interval contraction; isolated real algebraic root',
         'source_hash':SOURCE_SHA,'original_ledger':'2/9','new_source_orbits_closed':0,
         'parent_localized_stationary_empty':'FALSE','whole_survivor_noncompactness':'OPEN',
         'contraction_bound':str(contraction),'contraction_bound_float':float(contraction),
         'center_correction_max':str(max(correction)),'center_correction_float':float(max(correction)),
         'radius':str(rho),'parent_brackets_checked':70,'parent_signs':{name:1 if vv.lo>0 else -1 for name,vv in brackets.items()},
         'parent_intervals':{name:vv.as_pair() for name,vv in brackets.items()},
         'pivot_intervals':{name:vv.as_pair() for name,vv in signs.items()},
         'tangent_HV':VV.as_pair(),'tangent_HW':WW.as_pair(),
         'Hessian_B_V':bV.as_pair(),'Hessian_B_W':bW.as_pair(),
         'saddle':True,'global_V_curvature_identity':'PASS','LT_identity':'PASS',
         'independent_mathematical_review':False,'seconds':time.monotonic()-started}
    return out

def make_certificate():
    Q,R,_=reconstruct();xs=TH+(j,)
    centers=CENTER
    F=s.Matrix([Q,R]+[j*s.diff(Q,x)-s.diff(R,x) for x in TH if x!=B])
    substitutions=dict(zip(xs,map(s.Rational,centers)))
    exact_inverse=F.jacobian(xs).subs(substitutions).inv()
    scale=10**20
    rounded=[[str(s.floor(exact_inverse[i,k]*scale)/scale) for k in range(9)] for i in range(9)]
    return {'coordinates':list(map(str,xs)),'center':centers,'radius':'1/1000000000000','preconditioner':rounded}

CENTER=['-2416852684324638388209564256827327101282454738453219323/5000000000000000000000000000000000000000000000000000000', '-1294664301533436312108299725252840001876124546408215609/10000000000000000000000000000000000000000000000000000000', '-1832041699691747565224470761694620435033037084452150319/5000000000000000000000000000000000000000000000000000000', '1999231507320464781324915399756085877838085494236199907/25000000000000000000000000000000000000000000000000000000', '4896702752002527778615478246700107972530985125015351653/5000000000000000000000000000000000000000000000000000000', '1092930919959943544993247260704678840802854806299312187/1000000000000000000000000000000000000000000000000000000', '2961454516551742892283781489436476584903976013346640739/5000000000000000000000000000000000000000000000000000000', '797253812181674037078558255981435571920052715721646719/500000000000000000000000000000000000000000000000000000', '-1970994519650219580461412840584018209525641544869297129/1000000000000000000000000000000000000000000000000000000']

if __name__=='__main__':
    cert=make_certificate();out=verify(cert)
    (HERE/'GENERATED_STATIONARY_WITNESS.json').write_text(json.dumps(cert,indent=2)+'\n')
    (HERE/'STATIONARY_REPLAY.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k not in ['parent_intervals','contraction_bound','center_correction_max','tangent_HV','tangent_HW','Hessian_B_V','Hessian_B_W','pivot_intervals']},indent=2))
    for key in ['tangent_HV','tangent_HW','Hessian_B_V','Hessian_B_W']:
        print(key,[float(Rat(z)) for z in out[key]])
