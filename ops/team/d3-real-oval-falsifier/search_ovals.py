"""Deterministic numerical DISCOVERY of fixed-base compact ovals.

This is not an acceptance checker. In particular finite sign samples neither
prove whole-oval uniformity nor exhaust all real parameter choices.
"""
from pathlib import Path
from itertools import combinations
import argparse
import hashlib
import importlib.util
import json
import time
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = ROOT/'ai/omreal/data/DIAG3_triple_fullspace_critical_h1.json'
PIN = 'c9244a47ded5736e7afe724a9914e75631a22b78653442e88c14f5c397919eb8'


def model():
    # Historical arithmetic is reused ONLY for discovery, never acceptance.
    path = HERE.parent/'d3-bracket-chart/verify_genus_one_fiber.py'
    spec = importlib.util.spec_from_file_location('historical_arithmetic', path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    raw = SOURCE.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == PIN
    data = json.loads(raw)
    assert data['named_presentation'] == [5563,16134,19284]
    q = [{tuple(ex):int(co) for co,ex in rec['terms']} for rec in data['equations'][:3]]
    a,b,c,d,e,f,g,h,i = [m.variable(j) for j in range(9)]
    dnum = m.plus(m.times(b,m.plus(i,m.scale(f,-1))),m.times(f,g))
    reduced = [m.plus(m.times(i,m.coefficient(p,3,0)),m.times(dnum,m.coefficient(p,3,1))) for p in q[1:]]
    B,A = m.coefficient(reduced[0],0,0),m.coefficient(reduced[0],0,1)
    D,C = m.coefficient(reduced[1],0,0),m.coefficient(reduced[1],0,1)
    N = m.plus(m.times(A,D),m.scale(m.times(C,B),-1))
    one=m.constant(1)
    parent = [[m.constant(int(row==col)) for col in range(4)]+[one]+[
        one if row==0 else m.variable(3*col+row-1) for col in range(3)] for row in range(4)]
    walls={''.join(str(j+1) for j in inds):m.det_poly([[row[j] for j in inds] for row in parent]) for inds in combinations(range(8),4)}
    return m,q,A,B,N,walls


def specialize_numeric(p,base):
    """Output coefficients in ascending powers (c,e)."""
    out=np.zeros((3,3))
    for ex,co in p.items():
        for j,x in zip((1,5,6,7,8),base):co*=x**ex[j]
        out[ex[2],ex[4]]+=co
    return out


def evaluate(p,points):
    out=np.zeros(points.shape[1])
    for ex,co in p.items():
        term=np.full(points.shape[1],float(co))
        for j,k in enumerate(ex):
            if k:term*=points[j]**k
        out+=term
    return out


def evaluate_ce(coeff,c,e):
    return np.polynomial.polynomial.polyval2d(c,e,coeff)


def compact_intervals(n):
    c0,c1,c2=(n[:,j] for j in range(3))
    W=np.polynomial.polynomial.polysub(np.polynomial.polynomial.polymul(c1,c1),4*np.polynomial.polynomial.polymul(c0,c2))
    if not np.any(W) or abs(W[-1])<1e-11*np.max(np.abs(W)):return []
    roots=np.roots(W[::-1]/np.max(np.abs(W)))
    if any(abs(z.imag)<1e-7 and abs(z.imag)>1e-10 for z in roots):return []
    reals=sorted(z.real for z in roots if abs(z.imag)<1e-10)
    intervals=[]
    for lo,hi in zip(reals,reals[1:]):
        if hi-lo<1e-6*(1+abs(lo)+abs(hi)):continue
        if np.polynomial.polynomial.polyval((lo+hi)/2,W)<=0:continue
        poles=np.roots(np.trim_zeros(c2[::-1],'f'))
        if any(abs(z.imag)<1e-10 and lo-1e-8<=z.real<=hi+1e-8 for z in poles):continue
        intervals.append((lo,hi,W))
    return intervals


def oval_points(base,n,A,B,interval,samples):
    lo,hi,W=interval
    # Offset endpoints to prevent roundoff-created negative discriminants.
    theta=np.linspace(1e-7,np.pi-1e-7,samples)
    c=(lo+hi)/2+(hi-lo)/2*np.cos(theta)
    C0,C1,C2=[np.polynomial.polynomial.polyval(c,n[:,j]) for j in range(3)]
    disc=np.maximum(0,np.polynomial.polynomial.polyval(c,W))
    es=[(-C1+sign*np.sqrt(disc))/(2*C2) for sign in (1,-1)]
    c=np.tile(c,2);e=np.concatenate(es)
    den=evaluate_ce(A,c,e)
    a=-evaluate_ce(B,c,e)/den
    b,f,g,h,i=base
    d=(b*(i-f)+f*g)/i
    points=np.array([a,np.full_like(c,b),c,np.full_like(c,d),e,np.full_like(c,f),np.full_like(c,g),np.full_like(c,h),np.full_like(c,i)])
    return points,den


def search(args):
    start=time.monotonic()
    m,q,A,B,N,walls=model()
    rng=np.random.default_rng(args.seed)
    counts={'base_attempts':0,'base_unit_rejections':0,'nontrivial_fibers':0,'candidate_ovals':0,'sign_sample_rejections':0,'finite_sample_survivors':0}
    hit_walls={}
    examples=[]
    survivors=[]
    known=np.array([-23/7,-3,-1,2,4])
    for number in range(args.bases):
        counts['base_attempts']+=1
        if number==0:base=known
        elif args.mode=='local':base=known+args.radius*rng.normal(size=5)
        else:base=rng.integers(-args.radius,args.radius+1,size=5).astype(float)/args.denominator
        b,f,g,h,i=base
        if i==0 or f==1 or h==1:counts['base_unit_rejections']+=1;continue
        d=(b*(i-f)+f*g)/i
        constpoint=np.array([0,b,0,d,0,f,g,h,i])
        fixedwalls=[w for w in walls.values() if all(ex[0]==ex[2]==ex[4]==0 for ex in w)]
        if any(evaluate(w,constpoint[:,None])[0]==0 for w in fixedwalls):counts['base_unit_rejections']+=1;continue
        n=specialize_numeric(N,base)
        counts['nontrivial_fibers']+=1
        for interval in compact_intervals(n):
            counts['candidate_ovals']+=1
            pts,den=oval_points(base,n,specialize_numeric(A,base),specialize_numeric(B,base),interval,args.samples)
            varying=[]
            margins=[]
            for label,w in walls.items():
                values=evaluate(w,pts)
                if np.min(values)<=0<=np.max(values):varying.append(label)
                margins.append(float(np.min(np.abs(values))))
            rec={'base':base.tolist(),'interval':[float(t) for t in interval[:2]],'varying_brackets':varying,'min_abs_sample_bracket':min(margins),'max_abs_sample_coordinate':float(np.max(np.abs(pts)))}
            if varying:
                counts['sign_sample_rejections']+=1
                for wall in varying:hit_walls[wall]=hit_walls.get(wall,0)+1
                if len(examples)<10:examples.append(rec)
            else:
                counts['finite_sample_survivors']+=1
                survivors.append(rec)
                print('SURVIVOR',json.dumps(rec),flush=True)
        if number and number%1000==0:print('PROGRESS',number,counts,'seconds',time.monotonic()-start,flush=True)
    output={'status':'HEURISTIC_DISCOVERY_ONLY','source_sha256':PIN,'args':vars(args),'counts':counts,'hit_wall_counts':hit_walls,'examples':examples,'survivors':survivors,'seconds':time.monotonic()-start,'limitations':['Finite samples are not whole-oval acceptance.','No exhaustive full real parameter family coverage.','No implication about full-source compactness or original triple-bad components.']}
    Path(args.output).write_text(json.dumps(output,indent=2)+'\n')
    print(json.dumps(output,indent=2),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--bases',type=int,default=2000)
    parser.add_argument('--samples',type=int,default=65)
    parser.add_argument('--seed',type=int,default=20260905)
    parser.add_argument('--mode',choices=['grid','local'],default='grid')
    parser.add_argument('--radius',type=int,default=8)
    parser.add_argument('--denominator',type=int,default=1)
    parser.add_argument('--output',default=str(HERE/'search.json'))
    search(parser.parse_args())
