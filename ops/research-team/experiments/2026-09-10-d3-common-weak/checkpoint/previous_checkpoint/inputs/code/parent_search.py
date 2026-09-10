#!/usr/bin/env python3
"""Bounded actual-parent search; approximate proposals, exact certificate acceptance.

Run from any cwd. NumPy/SciPy are required; CuPy and a usable CUDA device are
required only for --backend cuda. No CUDA fallback. Numerical chunks resume only
under the identical code/configuration/source hash. Exact output is regenerated.
"""
import argparse
from collections import Counter, defaultdict
from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations, permutations
import json
from math import gcd, lcm
import os
from pathlib import Path
import platform
import sys
from time import perf_counter

try:
    import resource
except ImportError:  # Native Windows does not expose the POSIX resource module.
    resource = None

import numpy as np
import scipy
from scipy.optimize import linprog

HERE = Path(__file__).resolve().parent
TRIPLES = sorted(combinations(range(8), 3), key=lambda x: x[::-1])
BASES = sorted(combinations(range(8), 4), key=lambda x: x[::-1])
SIGS = [14988895318912, 3405195891438080, 40418075143643136]
PINS = {
    'parent_bank.npz': '3b90799d26b7783e92c2ac697eaaf8b76d26a787f53205873b997657e114180a',
    'FLOW.json': '83485ff8bb0a1f8cacffdacbf829cbee5898721b008f8bd54ec2a661ca35e6ab',
    'DISCOVERED_EVENT.json': 'b3d3e6122d38d46c6f8229a6d400e9fc1b1e461b151d03b26d6a9e803e022d8a',
    'EVENT_CERTIFICATE.json': 'd10682642cb6b7990bf7b7531c8c681f5166127d76f5aef4f32589f5eeece90b',
}


def require(x, message):
    if not x:
        raise ValueError(message)


def dump(path, obj):
    path = Path(path)
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(obj, sort_keys=True, indent=2) + '\n')
    tmp.replace(path)


def digest(obj):
    return sha256(json.dumps(obj, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def load_source(path):
    for name, h in PINS.items():
        require(sha256((path/name).read_bytes()).hexdigest() == h, 'Source SHA256 mismatch: ' + name)
    flow = json.loads((path/'FLOW.json').read_text())
    event = json.loads((path/'DISCOVERED_EVENT.json').read_text())
    event_cert = json.loads((path/'EVENT_CERTIFICATE.json').read_text())
    with np.load(path/'parent_bank.npz', allow_pickle=False) as bank:
        charts = bank['chart_matrix'].copy()
        require(charts.shape == (178, 4, 8) and charts.dtype == np.dtype('int64'), 'Source chart schema')
        require(int(bank['parent_index']) == 2599, 'Source parent index')
    require(charts[0].tolist() == flow['parent'] == event['parent'], 'Source chart0 identity')
    require(flow['signatures'] == event['signatures'] == event_cert['signatures'] == SIGS,
            'Source signature identity')
    require(len(flow['parent_signs']) == 70 and set(flow['parent_signs']) <= {-1, 1}, '70 strict signs')
    require(event['coord'] == 1 and event['label'] == 2, 'Source event coordinate')
    return charts, flow, event, event_cert


def make_candidates(charts, event, count, seed):
    """First3 are inherited controls, next178 source charts, rest reproducible perturbations.

    Each perturbation changes one coordinate of one source chart by a rational
    from a fixed finite list. SHA256(seed,index) supplies indices, not floating RNG.
    The generated finite domain is not a cover of the parent realization space.
    """
    out = []
    root = Q(event['root'])
    for side, delta in [('left', Q(-1, 10**6)), ('event', Q(0)), ('right', Q(1, 10**6))]:
        p = [[Q(int(x)) for x in row] for row in charts[0]]
        p[1][1] += root + delta
        out.append(dict(id=len(out), origin='inherited_event_control', side=side,
                        chart=0, parameter=str(root+delta), parent=p))
    for chart, mat in enumerate(charts):
        out.append(dict(id=len(out), origin='source_chart', chart=chart,
                        parent=[[Q(int(x)) for x in row] for row in mat]))
    offsets = [Q(s*n, d) for n, d in [(1,16), (1,4), (1,1), (4,1), (8,1), (16,1)] for s in [-1,1]]
    for i in range(181, count):
        bits = sha256(f'9DVL-parent-pilot:{seed}:{i}'.encode()).digest()
        chart = int.from_bytes(bits[:4], 'big') % 178
        coord = int.from_bytes(bits[4:8], 'big') % 32
        offset = offsets[int.from_bytes(bits[8:12], 'big') % len(offsets)]
        p = [[Q(int(x)) for x in row] for row in charts[chart]]
        p[coord//8][coord%8] += offset
        out.append(dict(id=i, origin='rational_single_coordinate_perturbation', chart=chart,
                        coordinate=[coord//8,coord%8], offset=str(offset), parent=p))
    return out[:count]


def add_controls(candidates, paths):
    controls=[]
    require(len(paths)<=2, 'At most2 current structural controls')
    for offset,path in enumerate(paths):
        raw=path.read_bytes();d=json.loads(raw)
        require(d['signature'] in SIGS, 'Structural control fixed signature')
        p=[[Q(x) for x in row] for row in d['parent']]
        require(len(p)==4 and all(len(row)==8 for row in p), 'Structural control parent schema')
        sp=d['support']['indices'] if isinstance(d.get('support'),dict) else d['support_indices']
        require(len(sp)==3 and len(set(sp))==3 and all(isinstance(i,int) and 0<=i<56 for i in sp),
                'Structural control support schema')
        i=len(candidates)
        candidates.append({'id':i,'origin':'current_structural_control','chart':d.get('chart_index',32),
                       'parent':p,'control_name':path.name,'control_sha256':sha256(raw).hexdigest(),
                       'control_signature':d['signature'],'control_support':sp})
        controls.append({'name':path.name,'sha256':sha256(raw).hexdigest(),'candidate_id':i})
    return controls


def backend(name):
    if name == 'cpu':
        return np, lambda: None, lambda x: x, {'backend':'numpy_cpu', 'cuda_executed':False}
    try:
        import cupy as cp
        n = cp.cuda.runtime.getDeviceCount()
        require(n > 0, 'No CUDA device exposed')
        cp.zeros(1).sum().item()
    except Exception as exc:
        raise RuntimeError('CUDA requested but unavailable; no CPU fallback: ' + str(exc)) from exc
    props = cp.cuda.runtime.getDeviceProperties(0)
    name_value = props.get('name', 'unknown')
    if isinstance(name_value, bytes):
        name_value = name_value.decode()
    return cp, lambda: cp.cuda.get_current_stream().synchronize(), cp.asnumpy, {
        'backend':'cupy_cuda', 'cupy_version':cp.__version__, 'device_count':n,
        'device_name':name_value, 'cuda_executed':True}


def det_batch(a, xp):
    n = a.shape[-1]
    result = xp.zeros(a.shape[:-2], dtype=xp.float64)
    for p in permutations(range(n)):
        sign = -1 if sum(p[i] > p[j] for i in range(n) for j in range(i+1,n)) % 2 else 1
        term = xp.ones(a.shape[:-2], dtype=xp.float64)
        for i,j in enumerate(p):
            term *= a[...,i,j]
        result += sign*term
    return result


def batch_geometry(parent_array, xp):
    vertices = xp.asarray(parent_array, dtype=xp.float64).transpose(0,2,1)
    brackets = det_batch(vertices[:, xp.asarray(BASES), :], xp)
    triples = vertices[:, xp.asarray(TRIPLES), :]
    normals = xp.stack([(-1)**(r+3) * det_batch(triples[..., [j for j in range(4) if j != r]], xp)
                        for r in range(4)], axis=-1)
    return brackets, normals


def numeric_block(normals, signature, known_support):
    a = normals * np.array([1 if signature >> i & 1 else -1 for i in range(56)])[:,None]
    norm = np.max(np.abs(a), axis=1)
    if np.any(norm == 0) or not np.all(np.isfinite(a)):
        return {'proposal':'UNKNOWN','reason':'zero_or_nonfinite_normal'}
    a = a/norm[:,None]
    # Exact Gordan candidates will be reconstructed later. LP status is not proof.
    sol = linprog([0,0,0,0,-1], A_ub=np.c_[-a,np.ones(56)], b_ub=np.zeros(56),
                  bounds=[(-1,1)]*4+[(-1,1)], method='highs',
                  options={'dual_feasibility_tolerance':1e-9,'primal_feasibility_tolerance':1e-9})
    if not sol.success or not np.all(np.isfinite(sol.x)):
        return {'proposal':'UNKNOWN','reason':'numeric_solver_failure','solver_status':int(sol.status)}
    margin = float(sol.x[4])
    if margin > 1e-8:
        return {'proposal':'GOOD','margin':margin,'point_proposal':sol.x[:4].tolist()}
    # The zero-margin optimum suggests badness; extract a dual support for exact checking.
    weights = -np.asarray(sol.ineqlin.marginals)
    sp = np.flatnonzero(weights > 1e-8).tolist()
    return {'proposal':'BAD_CANDIDATE','margin':margin,'support_proposal':sp,
            'known_support':known_support}


def numerical_chunk(candidates, flow, xp, sync, to_cpu):
    arrays = np.asarray([[[float(x) for x in row] for row in c['parent']] for c in candidates])
    sync(); t0 = perf_counter()
    brackets, normals = batch_geometry(arrays, xp)
    sync(); t1 = perf_counter()
    brackets, normals = to_cpu(brackets), to_cpu(normals)
    sync(); t2 = perf_counter()
    records = []
    sign_ref = np.asarray(flow['parent_signs'])
    supports = [w['support'] for w in flow['full_dual_witnesses']]
    for c,b,n in zip(candidates,brackets,normals):
        valid = bool(np.all(b*sign_ref > 0) and np.all(np.isfinite(b)))
        r = {'id':c['id'],'numerical_parent_sign_match':valid,
             'min_abs_parent_bracket':float(np.min(np.abs(b)))}
        if valid:
            r['blocks'] = [numeric_block(n,sig,sp) for sig,sp in zip(SIGS,supports)]
        else:
            r['blocks'] = []
            r['rejected_parent_indices'] = np.flatnonzero(b*sign_ref <= 0).tolist()
        records.append(r)
    t3 = perf_counter()
    return {'records':records,'timing_seconds':{'geometry_with_upload':t1-t0,
            'download':t2-t1,'numerical_lp_and_parent_screen':t3-t2},
            'array_shapes':{'parents':list(arrays.shape),'brackets':list(brackets.shape),
                            'normals':list(normals.shape)},
            'host_output_array_bytes':int(arrays.nbytes+brackets.nbytes+normals.nbytes)}


def det_exact(a):
    if not a:
        return Q(1)
    if len(a) == 1:
        return a[0][0]
    return sum(((-1)**j)*x*det_exact([r[:j]+r[j+1:] for r in a[1:]]) for j,x in enumerate(a[0]))


def exact_geometry(p):
    b = [det_exact([[p[r][i] for i in basis] for r in range(4)]) for basis in BASES]
    n = [[(-1)**(r+3)*det_exact([[p[k][i] for i in triple] for k in range(4) if k != r])
          for r in range(4)] for triple in TRIPLES]
    return b,n


def null_vector(rows):
    """One-dimensional nullspace of rows^T using Fraction RREF; None otherwise."""
    n = len(rows)
    if n == 0:
        return None
    a = [[Q(rows[j][i]) for j in range(n)] for i in range(4)]
    pivots=[]; r=0
    for c in range(n):
        k = next((k for k in range(r,4) if a[k][c]), None)
        if k is None:
            continue
        a[r],a[k]=a[k],a[r]
        z=a[r][c];a[r]=[x/z for x in a[r]]
        for k in range(4):
            if k != r:
                z=a[k][c];a[k]=[x-z*y for x,y in zip(a[k],a[r])]
        pivots.append(c);r+=1
        if r==4:
            break
    free=[c for c in range(n) if c not in pivots]
    if len(free)!=1:
        return None
    v=[Q(0)]*n;v[free[0]]=Q(1)
    for row,c in enumerate(pivots):
        v[c]=-a[row][free[0]]
    if all(x<=0 for x in v):
        v=[-x for x in v]
    if not all(x>=0 for x in v) or not any(v):
        return None
    return [x/sum(v) for x in v]


def primitive_point(point):
    denominator=lcm(*(x.denominator for x in point))
    v=[int(x*denominator) for x in point]
    common=gcd(*v)
    return [Q(x//common) for x in v] if common else [Q(0)]*4


def verify_block(a, cert):
    """Producer acceptance, separate from the independent reviewer implementation."""
    if cert['status']=='GOOD':
        p=[Q(x) for x in cert['point']]
        require(len(p)==4, 'Primal dimension')
        margins=[sum(x*y for x,y in zip(row,p)) for row in a]
        require(len(margins)==56 and all(x>0 for x in margins), 'All56 strict primal margins')
        return
    if cert['status']=='BAD':
        sp=cert['support'];w=[Q(x) for x in cert['weights']]
        require(len(sp)==len(w)>0 and len(set(sp))==len(sp) and all(0<=i<56 for i in sp), 'Dual support')
        require(all(x>=0 for x in w) and any(x>0 for x in w), 'Nonnegative nonzero dual')
        require(all(sum(wj*a[i][c] for i,wj in zip(sp,w))==0 for c in range(4)), 'Exact Gordan identity')
        return
    require(cert['status']=='UNKNOWN', 'Explicit unknown status')


def certify_candidate(candidate, numeric, flow, event, event_cert):
    b,n=exact_geometry(candidate['parent'])
    signs=[(x>0)-(x<0) for x in b]
    result={k:v for k,v in candidate.items() if k!='parent'}
    result['parent']=[[str(x) for x in row] for row in candidate['parent']]
    result['parent_signs']=signs
    result['parent_admissible']=signs==flow['parent_signs']
    result['bracket_count']=len(b)
    result['normal_count']=len(n)
    result['blocks']=[]
    if not result['parent_admissible']:
        result['status']='EXACT_PARENT_REJECTED'
        return result
    for bi,sig in enumerate(SIGS):
        a=[[x*(1 if sig>>i&1 else -1) for x in row] for i,row in enumerate(n)]
        cert={'signature_index':bi,'signature':sig,'status':'UNKNOWN'}
        points=[];supports=[]
        if candidate['origin']=='current_structural_control' and candidate['control_signature']==sig:
            supports.append(candidate['control_support'])
        if candidate['origin']=='inherited_event_control':
            rec=next(e for e in event_cert['endpoint_records'] if e['side']==candidate['side'])
            if bi==0:
                points.append([Q(x) for x in rec['affine_primal_point']])
            supports.append(event['supports'][bi])
        proposal=numeric['blocks'][bi] if numeric['blocks'] else {}
        if 'point_proposal' in proposal:
            for bound in [10**3,10**6,10**9,10**12]:
                points.append([Q(float(x)).limit_denominator(bound) for x in proposal['point_proposal']])
        for point in points:
            point=primitive_point(point)
            if all(sum(x*y for x,y in zip(row,point))>0 for row in a):
                cert.update(status='GOOD',kind='primal',point=[str(x) for x in point]);break
        if cert['status']=='UNKNOWN':
            supports.append(flow['full_dual_witnesses'][bi]['support'])
            if proposal.get('support_proposal'):
                supports.append(proposal['support_proposal'])
            for sp in supports:
                if not (1<=len(sp)<=5):
                    continue
                w=null_vector([a[i] for i in sp])
                if w is not None:
                    nonzero=[(i,x) for i,x in zip(sp,w) if x>0]
                    cert.update(status='BAD',kind='gordan',support=[i for i,x in nonzero],
                                weights=[str(x) for i,x in nonzero]);break
        verify_block(a,cert)
        if cert['status']=='UNKNOWN':
            cert['reason']='No accepted exact primal or Gordan reconstruction; numeric status is not proof'
        result['blocks'].append(cert)
    result['label_pattern']=''.join({'GOOD':'G','BAD':'B','UNKNOWN':'?'}[c['status']] for c in result['blocks'])
    result['status']='EXACT_FULL_LABEL' if '?' not in result['label_pattern'] else 'EXACT_PARTIAL_LABEL'
    return result


def select_candidates(records, candidates, limit):
    """Known controls plus pattern diversity, then origin/chart diversity."""
    lookup={r['id']:r for r in records}
    # Source calibration parents were examined in the181-candidate smoke run;
    # retain them so the entire pilot exact-checks at most32distinct parents.
    selected=[0,1,2,3,176,164,37,13][:limit]
    selected += [c['id'] for c in candidates if c['origin']=='current_structural_control'
                 and c['id'] not in selected]
    groups=defaultdict(list)
    for r in records[3:]:
        if r['numerical_parent_sign_match']:
            pattern=tuple(b['proposal'] for b in r['blocks'])
            groups[pattern].append(r['id'])
    # Highest GOOD margin within each observed pattern avoids numerical boundary artifacts.
    for ids in groups.values():
        ids.sort(key=lambda i:(-sum(b.get('margin',0) for b in lookup[i]['blocks']),i))
    for pattern in sorted(groups):
        i=groups[pattern].pop(0)
        if i not in selected:
            selected.append(i)
    seen_charts={candidates[i]['chart'] for i in selected}
    for pattern in sorted(groups):
        for i in groups[pattern]:
            if len(selected)>=limit:
                break
            if candidates[i]['chart'] not in seen_charts:
                selected.append(i);seen_charts.add(candidates[i]['chart'])
    for pattern in sorted(groups):
        for i in groups[pattern]:
            if len(selected)>=limit:
                break
            if i not in selected:
                selected.append(i)
    return selected[:limit]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,default=HERE.parent/'source')
    parser.add_argument('--out',type=Path,default=HERE/'run')
    parser.add_argument('--backend',choices=['cpu','cuda'],default='cpu')
    parser.add_argument('--count',type=int,default=4096)
    parser.add_argument('--chunk-size',type=int,default=256)
    parser.add_argument('--exact-limit',type=int,default=32)
    parser.add_argument('--seed',type=int,default=20260909)
    parser.add_argument('--resume',action='store_true')
    parser.add_argument('--control',action='append',type=Path,default=[],
                        help='Optional frozen structural control JSON, at most2; included inside total candidate budget')
    args=parser.parse_args()
    require(181<=args.count<=4096, 'Candidate bound must be181..4096')
    require(3<=args.exact_limit<=32, 'Exact parent limit must be3..32')
    require(1<=args.chunk_size<=1024, 'Chunk size must be1..1024')
    started=perf_counter()
    xp,sync,to_cpu,backend_info=backend(args.backend)
    charts,flow,event,event_cert=load_source(args.source)
    require(not args.control or args.count>=183, 'Controls must not replace the178 source charts')
    candidates=make_candidates(charts,event,args.count-len(args.control),args.seed)
    controls=add_controls(candidates,args.control)
    config={'count':args.count,'chunk_size':args.chunk_size,'exact_limit':args.exact_limit,
            'seed':args.seed,'backend':args.backend,'source_pins':PINS,
            'code_sha256':sha256(Path(__file__).read_bytes()).hexdigest(),
            'current_structural_controls':controls,
            'candidate_domain':'3 inherited controls +178 source charts + hashed rational one-coordinate perturbations',
            'coordinate_indexing':'zero-based','triple_and_basis_order':'colex'}
    config_hash=digest(config)
    args.out.mkdir(parents=True,exist_ok=True)
    config_path=args.out/'config.json'
    if config_path.exists():
        require(args.resume, 'Output exists; use --resume or choose a fresh output directory')
        require(json.loads(config_path.read_text())==config, 'Resume configuration/code/source mismatch')
    else:
        dump(config_path,config)
    records=[];timings=Counter();resumed=0
    for start in range(0,len(candidates),args.chunk_size):
        chunk=candidates[start:start+args.chunk_size]
        path=args.out/f'chunk_{start:05d}.json'
        loaded_from_checkpoint=args.resume and path.exists()
        if loaded_from_checkpoint:
            data=json.loads(path.read_text())
            require(data['config_hash']==config_hash and data['candidate_ids']==[c['id'] for c in chunk],
                    'Resume chunk binding mismatch')
            require(data['payload_sha256']==digest(data['payload']), 'Resume chunk payload mismatch')
            resumed+=1
        else:
            payload=numerical_chunk(chunk,flow,xp,sync,to_cpu)
            data={'config_hash':config_hash,'candidate_ids':[c['id'] for c in chunk],
                  'payload':payload,'payload_sha256':digest(payload)}
            dump(path,data)
        records.extend(data['payload']['records'])
        timings.update(data['payload']['timing_seconds'])
        print(json.dumps({'chunk_start':start,'rows':len(chunk),'resumed':loaded_from_checkpoint,
                          'numeric_parent_sign_matches':sum(r['numerical_parent_sign_match'] for r in data['payload']['records'])}),flush=True)
    ids=select_candidates(records,candidates,args.exact_limit)
    lookup={r['id']:r for r in records}
    exact_started=perf_counter()
    exact=[]
    for i in ids:
        exact.append(certify_candidate(candidates[i],lookup[i],flow,event,event_cert))
        print(json.dumps({'exact_parent':i,'pattern':exact[-1].get('label_pattern'),
                          'origin':exact[-1]['origin']}),flush=True)
    exact_seconds=perf_counter()-exact_started
    output={'schema':'9dvl.actual_parent_point_certificates.v1','config_hash':config_hash,
            'source_revision':'59fec66666518257c585194b81061f60d91f439d','source_sha256':PINS,
            'signature_order':SIGS,'triple_order':[list(t) for t in TRIPLES],
            'normal_convention':'raw rational signed cofactors; no primitive-row gcd normalization',
            'current_structural_controls':controls,
            'basis_order':[list(t) for t in BASES],'expected_parent_signs':flow['parent_signs'],
            'scope':'Finite pointwise labels only. No covering, cohomology, injectivity or theorem claim.',
            'candidates':exact}
    dump(args.out/'exact_candidates.json',output)
    numerical_patterns=Counter(''.join({'GOOD':'G','BAD_CANDIDATE':'b','UNKNOWN':'?'}[b['proposal']]
                                      for b in r['blocks']) for r in records if r['blocks'])
    exact_patterns=Counter(r.get('label_pattern',r['status']) for r in exact)
    report={'classification':('BOUNDED_ACTUAL_PARENT_CPU_SEARCH_WITH_OPTIONAL_UNTESTED_CUDA'
                              if args.backend=='cpu' else 'BOUNDED_ACTUAL_PARENT_CUDA_NUMERICAL_SEARCH_CPU_EXACT_ACCEPTANCE'),
            'config_hash':config_hash,'generated_parent_count':len(candidates),
            'unique_literal_parent_count':len({tuple(x for row in c['parent'] for x in row) for c in candidates}),
            'inherited_control_count':3,'source_chart_count':178,
            'current_structural_control_count':len(controls),
            'new_perturbation_count':len(candidates)-181-len(controls),
            'numerical_parent_sign_matches':sum(r['numerical_parent_sign_match'] for r in records),
            'numerical_parent_rejections':sum(not r['numerical_parent_sign_match'] for r in records),
            'numerical_patterns_lowercase_b_unproved':dict(numerical_patterns),
            'exact_selected_parents':len(exact),'exact_patterns':dict(exact_patterns),
            'unknown_exact_blocks':sum(b['status']=='UNKNOWN' for r in exact for b in r['blocks']),
            'backend':backend_info,'source_charts_all_tested_numerically':True,
            'timing_seconds_original_numeric_chunks':dict(timings),'exact_seconds_this_run':exact_seconds,
            'wall_seconds_this_invocation':perf_counter()-started,'resumed_chunk_count':resumed,
            'peak_rss_mib':(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss /
                            (1024**2 if sys.platform=='darwin' else 1024)) if resource else None,
            'rss_measurement':'POSIX peak resident memory; unavailable on native Windows' if resource else 'unavailable',
            'versions':{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__},
            'gpu_speedup_measured':False,'global_coverage':False,'original_injectivity':'OPEN',
            'original_obligations_closed':0,'ledger':'2/9'}
    dump(args.out/'RUN_REPORT.json',report)
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    try:
        main()
    except (ValueError,RuntimeError) as exc:
        print('ERROR: '+str(exc),file=sys.stderr)
        sys.exit(2)
