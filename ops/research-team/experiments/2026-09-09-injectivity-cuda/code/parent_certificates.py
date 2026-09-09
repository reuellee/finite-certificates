#!/usr/bin/env python3
"""Independent literal-matrix certificate replay. No producer code imports.

The arithmetic core is stdlib rational permutation determinants. NPY parsing
uses only ast, struct and zipfile, and is restricted to fixed little-endian i8.
This checks finite witnesses, not chart coverage or compact-support topology.
"""
import argparse
import ast
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha1, sha256
from itertools import combinations, permutations
import json
from math import gcd, prod
from pathlib import Path
import struct
from time import perf_counter
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SIGS = [14988895318912, 3405195891438080, 40418075143643136]
TRIPLES = sorted(combinations(range(8), 3), key=lambda s: s[::-1])
BASES = sorted(combinations(range(8), 4), key=lambda s: s[::-1])
PERMS = {n: [(p, (-1)**sum(p[i] > p[j] for i in range(n) for j in range(i+1,n)))
              for p in permutations(range(n))] for n in (2,3,4)}

def require(test, msg):
    if not test:
        raise ValueError(msg)

def rational(x):
    require(type(x) in (int, str) or isinstance(x, Q), 'nonexact rational representation')
    return Q(x)

def det(a):
    return sum(s * prod(a[i][p[i]] for i in range(len(a)))
               for p, s in PERMS[len(a)])

def sign(x):
    return int(x > 0)-int(x < 0)

def matrix(value):
    require(isinstance(value,list) and len(value)==4 and
            all(isinstance(r,list) and len(r)==8 for r in value), 'parent shape')
    return [[rational(v) for v in row] for row in value]

def rank(a):
    a = [[rational(v) for v in r] for r in a]
    h = 0
    for j in range(len(a[0])):
        p = next((i for i in range(h,len(a)) if a[i][j]), None)
        if p is None: continue
        a[h],a[p]=a[p],a[h]
        z=a[h][j]
        a[h]=[v/z for v in a[h]]
        for i in range(h+1,len(a)):
            z=a[i][j]
            a[i]=[x-z*y for x,y in zip(a[i],a[h])]
        h+=1
        if h==len(a): break
    return h

def geometry(parent, parent_signs):
    p = matrix(parent)
    brackets = [det([[p[r][c] for c in b] for r in range(4)]) for b in BASES]
    require([sign(v) for v in brackets] == parent_signs, 'strict parent chirotope')
    normals = [[(-1)**(r+3)*det([[p[k][c] for c in t]
                 for k in range(4) if k!=r]) for r in range(4)] for t in TRIPLES]
    require(all(any(n) for n in normals), 'zero derived normal')
    return normals

def block(normals, cert):
    b=cert['signature_index']
    require(type(b)==int and 0<=b<3, 'signature index')
    require(cert['signature']==SIGS[b], 'source signature identity')
    a=[[x*(1 if SIGS[b]>>i&1 else -1) for x in row] for i,row in enumerate(normals)]
    status=cert['status']
    require(status in ('GOOD','BAD','UNKNOWN'), 'unrecognized status')
    if status=='UNKNOWN':
        require(not any(k in cert for k in ('point','support','weights')), 'UNKNOWN claims witness')
        return {'status':status}
    if status=='GOOD':
        require(cert['kind']=='primal', 'GOOD certificate kind')
        p=[rational(x) for x in cert['point']]
        require(len(p)==4, 'primal point dimension')
        margins=[sum(x*y for x,y in zip(row,p)) for row in a]
        require(all(x>0 for x in margins), 'full56 strict primal positivity')
        return {'status':status,'margin_min':str(min(margins))}
    require(cert['kind']=='gordan', 'BAD certificate kind')
    support=cert['support']
    weights=[rational(x) for x in cert['weights']]
    require(1<=len(support)<=56 and len(support)==len(weights), 'dual shape')
    require(all(type(i)==int and 0<=i<56 for i in support) and
            len(set(support))==len(support), 'dual support indices')
    require(all(x>=0 for x in weights) and any(x>0 for x in weights), 'nonnegative nonzero dual weights')
    require(all(sum(w*a[i][j] for i,w in zip(support,weights))==0
                for j in range(4)), 'exact Gordan equality')
    rr=rank([a[i] for i in support])
    if cert.get('circuit'):
        require(all(x>0 for x in weights) and rr==len(support)-1, 'positive circuit nullity')
    return {'status':status,'support_size':len(support),'rank':rr}

def bank_read(path):
    with zipfile.ZipFile(path) as z:
        raw=z.read('chart_matrix.npy')
    require(raw[:6]==b'\x93NUMPY', 'NPY magic')
    ver=raw[6]
    require(ver in (1,2), 'NPY version')
    off=10 if ver==1 else 12
    size=struct.unpack('<H' if ver==1 else '<I',raw[8:off])[0]
    head=ast.literal_eval(raw[off:off+size].decode())
    require(head['descr']=='<i8' and head['fortran_order'] is False and
            head['shape']==(178,4,8), 'NPY chart schema')
    payload=raw[off+size:]
    require(len(payload)==178*4*8*8, 'NPY payload size')
    values=struct.unpack('<'+'q'*(178*4*8),payload)
    return [[[values[k*32+r*8+c] for c in range(8)] for r in range(4)] for k in range(178)]

def source_audit(source):
    manifest=json.loads((source/'FETCH_MANIFEST.json').read_text())
    require(manifest['base']=='59fec66666518257c585194b81061f60d91f439d','source revision')
    for rec in manifest['files']:
        data=(source/rec['path']).read_bytes()
        require(len(data)==rec['bytes'],'source length '+rec['path'])
        require(sha256(data).hexdigest()==rec['sha256'],'source SHA256 '+rec['path'])
        require(sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==rec['git_blob'],
                'source Git blob '+rec['path'])
    flow=json.loads((source/'FLOW.json').read_text())
    event=json.loads((source/'DISCOVERED_EVENT.json').read_text())
    old=json.loads((source/'EVENT_CERTIFICATE.json').read_text())
    charts=bank_read(source/'parent_bank.npz')
    require(charts[0]==flow['parent']==event['parent'],'literal chart0 source binding')
    require(flow['signatures']==event['signatures']==old['signatures']==SIGS,'fixed3 source signatures')
    for p in charts:
        # Strict chirotope certification of the bank only, no coverage claim.
        psg=[sign(det([[p[r][c] for c in b] for r in range(4)])) for b in BASES]
        require(psg==flow['parent_signs'],'bank chart strict parent signs')
    n=geometry(charts[0],flow['parent_signs'])
    prim=[[int(x)//gcd(*(int(y) for y in row)) for x in row] for row in n]
    for i,c in enumerate(flow['full_dual_witnesses']):
        block(prim,dict(c,signature_index=i,signature=SIGS[i],status='BAD',kind='gordan'))
    endpoint_results=[]
    for e in old['endpoint_records']:
        p=deepcopy(charts[0]);p[1][1]=Q(p[1][1])+rational(e['parameter'])
        n=geometry(p,flow['parent_signs'])
        statuses=[]
        for i,bad in enumerate(e['full_block_badness']):
            cert={'signature_index':i,'signature':SIGS[i]}
            if bad:
                pairs=[(s,rational(w)) for s,w in zip(event['supports'][i],e['selected_normalized_dual_weights'][i]) if rational(w)!=0]
                cert.update(status='BAD',kind='gordan',support=[s for s,w in pairs],weights=[w for s,w in pairs])
            else:
                cert.update(status='GOOD',kind='primal',point=e['affine_primal_point'])
            statuses.append(block(n,cert)['status'])
        endpoint_results.append({'side':e['side'],'block_status':statuses})
    return flow, {'source_files_bound':len(manifest['files']),
                  'all178_chart_parent_signs_checked':True,
                  'fixed_signatures':SIGS,
                  'flow_dual_normalization':'positive-gcd primitive integer normals',
                  'flow_duals_verified':3,'source_endpoints_replayed':endpoint_results,
                  'signature_validity_properness_and_antichain':'inherited, not re-proved',
                  'global_parent_coverage':'not certified'}

def rejects(fn):
    try:
        fn()
    except (ValueError,KeyError,TypeError,ZeroDivisionError):
        return True
    return False

def structural_audit(path, flow, source):
    data=json.loads(path.read_text())
    for name,digest in data['source_sha256'].items():
        require(sha256((source/name).read_bytes()).hexdigest()==digest,'structural source hash')
    charts=bank_read(source/'parent_bank.npz')
    require(len(data['attempts'])==data['targeted_exact_wall_solves']==128,'128 bounded attempts')
    require([a['attempt'] for a in data['attempts']]==list(range(128)),'attempt index coverage')
    accepted=[];counts=Counter();keys=set();parents=set();supports=set();signatures=Counter()
    for rec in data['attempts']:
        p=matrix(rec['parent'])
        original=matrix(charts[rec['chart_index']])
        row,col=rec['coordinate']
        original[row][col]+=rational(rec['delta'])
        require(original==p,'literal rational candidate identity')
        signs=[sign(det([[p[r][c] for c in b] for r in range(4)])) for b in BASES]
        failures=[i for i,(a,b) in enumerate(zip(signs,flow['parent_signs'])) if a!=b]
        require(signs==rec['parent_signs'] and failures==rec['parent_sign_failures'],'recorded parent failure set')
        require(rec['status']==('PARENT_SIGN_FAILURE' if failures else 'EXACT_POSITIVE_CIRCUIT'),
                'parent status classification')
        counts[rec['status']]+=1
        if failures: continue
        n=geometry(rec['parent'],flow['parent_signs'])
        ids=rec['support']['indices']
        require([list(TRIPLES[i]) for i in ids]==rec['support']['triples'],'colex support identity')
        cert={'signature_index':rec['signature_index'],'signature':rec['signature'],
              'status':'BAD','kind':'gordan','support':ids,'weights':rec['weights'],'circuit':True}
        ans=block(n,cert)
        require(len(ids)==3 and ans['rank']==rec['rank']==2,'three-row rank2')
        signed=[[v*(1 if rec['signature']>>i&1 else -1) for v in n[i]] for i in ids]
        require(signed==[[rational(v) for v in rr] for rr in rec['signed_normals']], 'literal signed normals')
        require(all(rank([signed[i],signed[j]])==2 for i,j in combinations(range(3),2)),
                'all support pairs independent')
        pk=tuple(tuple(str(x) for x in r) for r in p)
        sk=tuple(sorted(ids));keys.add((pk,sk,rec['signature']));parents.add(pk);supports.add(sk)
        signatures[rec['signature_index']]+=1
        accepted.append(rec)
    require(dict(counts)==data['counts'],'structural totals')
    require(accepted==data['witnesses'],'accepted witness list exactly bound to attempts')
    w=accepted[0];n=geometry(w['parent'],flow['parent_signs'])
    cert={'signature_index':w['signature_index'],'signature':w['signature'],'status':'BAD',
          'kind':'gordan','support':w['support']['indices'],'weights':w['weights'],'circuit':True}
    hostile={}
    c=deepcopy(cert);c['weights'][0]=str(rational(c['weights'][0])+1)
    hostile['altered_positive_weight']=rejects(lambda:block(n,c))
    c2=deepcopy(cert);c2['support'][0]=c2['support'][1]
    hostile['duplicate_support']=rejects(lambda:block(n,c2))
    c3=deepcopy(cert);c3['signature']^=1<<c3['support'][0]
    hostile['signature_bit_change']=rejects(lambda:block(n,c3))
    c4=deepcopy(cert);c4['weights']=[0]*3
    hostile['zero_dual']=rejects(lambda:block(n,c4))
    p=matrix(w['parent']);rr,cc=w['coordinate'];p[rr][cc]+=Q(1,10**20)
    # This remains in the strict parent chamber but leaves the exact wall.
    perturbed=geometry(p,flow['parent_signs'])
    hostile['tiny_rational_offwall_same_weights']=rejects(lambda:block(perturbed,cert))
    hostile['tiny_rational_offwall_rank_three']=rank([perturbed[i] for i in cert['support']])==3
    pf=deepcopy(w['parent']);pf[0][0]=float(pf[0][0])
    hostile['floating_parent_rejected']=rejects(lambda:geometry(pf,flow['parent_signs']))
    invalid=next(x for x in data['attempts'] if x['status']=='PARENT_SIGN_FAILURE')
    hostile['positive_relation_wrong_parent_chamber']=rejects(lambda:geometry(invalid['parent'],flow['parent_signs']))
    require(all(hostile.values()),'structural hostile canary')
    smallest=json.loads((path.parent/'WITNESS.json').read_text())
    require(smallest in accepted,'selected witness belongs to certified attempts')
    near=json.loads((path.parent/'NEAR_SINGULAR_CANARY.json').read_text())
    np=matrix(near['parent']);wp=matrix(smallest['parent'])
    row,col=near['coordinate'];wp[row][col]+=rational(near['offset_from_witness'])
    require(np==wp,'near-singular literal perturbation identity')
    nn=geometry(near['parent'],flow['parent_signs'])
    require(near['support_indices']==smallest['support']['indices'] and
            near['signature']==smallest['signature'],'near-singular support/signature')
    aa=[[v*(1 if near['signature']>>i&1 else -1) for v in nn[i]] for i in near['support_indices']]
    minor=det([[r[c] for c in near['minor_columns']] for r in aa])
    require(minor!=0 and minor==rational(near['nonzero_rank_three_minor']) and
            rank(aa)==near['exact_rank']==3,'near-singular exact rank3')
    return {'sha256':sha256(path.read_bytes()).hexdigest(),'attempts_checked':128,
            'exact_positive_three_row_circuits':len(accepted),'parent_sign_rejections':counts['PARENT_SIGN_FAILURE'],
            'unique_parent_support_signature':len(keys),'unique_literal_parents':len(parents),
            'unique_unordered_supports':len(supports),'signature_index_counts':dict(signatures),
            'normalization':'raw rational cofactor normals','all_support_pairs_rank_two':True,
            'selected_witness_attempt':smallest['attempt'],
            'near_singular_control':{'sha256':sha256((path.parent/'NEAR_SINGULAR_CANARY.json').read_bytes()).hexdigest(),
                                    'exact_rank':3,'nonzero_minor':str(minor),'float_SVD':'not a proof and not independently replayed'},
            'hostile_controls':hostile,'screening_order_or_completeness':'not independently reproduced',
            'consequence':'finite exact local badness witnesses only'}

def engineer_audit(path, flow, source):
    data=json.loads(path.read_text())
    config=json.loads((path.parent/'config.json').read_text())
    digest=lambda x:sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    require(digest(config)==data['config_hash'],'engineer configuration digest')
    require(sha256((path.parent.parent/'pilot.py').read_bytes()).hexdigest()==config['code_sha256'],
            'engineer frozen producer code digest')
    require(data['source_revision']=='59fec66666518257c585194b81061f60d91f439d','engineer source revision')
    for name,h in data['source_sha256'].items():
        require(sha256((source/name).read_bytes()).hexdigest()==h,'engineer source file hash')
    require(data['signature_order']==SIGS and data['triple_order']==[list(t) for t in TRIPLES] and
            data['basis_order']==[list(b) for b in BASES], 'engineer order conventions')
    require(data['expected_parent_signs']==flow['parent_signs'],'engineer parent signs')
    charts=bank_read(source/'parent_bank.npz');event=json.loads((source/'DISCOVERED_EVENT.json').read_text())
    counts=Counter();blockcounts=Counter();outputs=[];seen=set()
    for rec in data['candidates']:
        i=rec['id']; require(i not in seen and 0<=i<config['count'],'candidate unique ID range');seen.add(i)
        # Independent reconstruction from the declared deterministic domain.
        control=next((c for c in config.get('current_structural_controls',[]) if c['candidate_id']==i),None)
        if control is not None:
            raw=(path.parent.parent/'controls'/control['name']).read_bytes()
            require(sha256(raw).hexdigest()==control['sha256']==rec['control_sha256'],'frozen control hash')
            doc=json.loads(raw);expected=matrix(doc['parent'])
            require(rec['origin']=='current_structural_control' and rec['control_name']==control['name'],
                    'current control origin')
            require(rec['control_signature']==doc['signature'],'control signature')
            support=doc['support']['indices'] if isinstance(doc.get('support'),dict) else doc['support_indices']
            require(rec['control_support']==support,'control support')
        elif i<3:
            sides=['left','event','right'];offsets=[-Q(1,10**6),Q(0),Q(1,10**6)]
            require(rec['origin']=='inherited_event_control' and rec['side']==sides[i], 'event candidate origin')
            expected=matrix(charts[0]);expected[1][1]+=Q(event['root'])+offsets[i]
            require(Q(rec['parameter'])==Q(event['root'])+offsets[i],'event parameter identity')
        elif i<181:
            require(rec['origin']=='source_chart' and rec['chart']==i-3,'source chart candidate identity')
            expected=matrix(charts[i-3])
        else:
            require(rec['origin']=='rational_single_coordinate_perturbation','perturbation origin')
            raw=sha256(('9DVL-parent-pilot:'+str(config['seed'])+':'+str(i)).encode()).digest()
            chart=int.from_bytes(raw[:4],'big')%178;pos=int.from_bytes(raw[4:8],'big')%32
            possible=[sign*Q(n,d) for n,d in [(1,16),(1,4),(1,1),(4,1),(8,1),(16,1)] for sign in (-1,1)]
            off=possible[int.from_bytes(raw[8:12],'big')%12]
            require(chart==rec['chart'] and rec['coordinate']==[pos//8,pos%8] and Q(rec['offset'])==off,
                    'hashed perturbation metadata')
            expected=matrix(charts[chart]);expected[pos//8][pos%8]+=off
        require(expected==matrix(rec['parent']),'exact parent candidate identity')
        n=geometry(rec['parent'],flow['parent_signs'])
        require(rec['parent_admissible'] is True and rec['parent_signs']==flow['parent_signs'], 'accepted strict parent')
        require(rec['bracket_count']==70 and rec['normal_count']==56,'full geometry dimensions')
        require([b['signature_index'] for b in rec['blocks']]==[0,1,2],'complete3 blocks')
        results=[block(n,c) for c in rec['blocks']]
        pattern=''.join({'GOOD':'G','BAD':'B','UNKNOWN':'?'}[r['status']] for r in results)
        require(pattern==rec['label_pattern'],'exact pattern claim')
        require(rec['status']==('EXACT_FULL_LABEL' if '?' not in pattern else 'EXACT_PARTIAL_LABEL'),'exact completeness status')
        counts[pattern]+=1;blockcounts.update(r['status'] for r in results)
        outputs.append({'id':i,'pattern':pattern,'blocks':results})
    require(len(outputs)<=32 and {0,1,2}<=seen,'selected parent ceiling and event controls')
    rr=json.loads((path.parent/'RUN_REPORT.json').read_text())
    require(rr['exact_patterns']==dict(counts) and rr['exact_selected_parents']==len(outputs), 'runreport exact totals')
    require(rr['unknown_exact_blocks']==blockcounts['UNKNOWN'],'runreport unknown count')
    good=next(((r,b) for r in data['candidates'] for b in r['blocks'] if b['status']=='GOOD'),None)
    require(good is not None,'positive primal control available')
    rec,cert=good;n=geometry(rec['parent'],flow['parent_signs'])
    badpoint=deepcopy(cert);badpoint['point']=[str(-Q(x)) for x in badpoint['point']]
    hostile={'negated_primal_point':rejects(lambda:block(n,badpoint))}
    unknown={'signature_index':0,'signature':SIGS[0],'status':'UNKNOWN'}
    hostile['explicit_unknown_retained']=block(n,unknown)=={'status':'UNKNOWN'}
    impossible=deepcopy(unknown);impossible.update(status='GOOD',kind='primal',point=['0']*4)
    hostile['zero_margin_not_primal']=rejects(lambda:block(n,impossible))
    require(all(hostile.values()),'engineer hostile controls')
    family_witnesses={pat:next((r['id'] for r in outputs if r['pattern']==pat),None)
                      for pat in ('BBB','GBB','BGB','BBG')}
    return {'sha256':sha256(path.read_bytes()).hexdigest(),'selected_parents':len(outputs),
            'patterns':dict(counts),'block_status_counts':dict(blockcounts),
            'full_literal_geometry_and_candidate_identity':True,'hostile_controls':hostile,
            'fixed_family_nonempty_proper_and_pairwise_incomparable':all(i is not None for i in family_witnesses.values()),
            'family_property_witness_ids':family_witnesses,
            'certificates':outputs,'numerical_search':'heuristic, not independently proved coverage'}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--source',type=Path,default=ROOT/'source')
    parser.add_argument('--out',type=Path)
    parser.add_argument('--structural',type=Path)
    parser.add_argument('--engineer',type=Path)
    args=parser.parse_args()
    t=perf_counter()
    flow,out=source_audit(args.source)
    if args.structural:
        out['structural']=structural_audit(args.structural,flow,args.source)
    if args.engineer:
        out['engineer']=engineer_audit(args.engineer,flow,args.source)
        if out['engineer']['fixed_family_nonempty_proper_and_pairwise_incomparable']:
            out['signature_validity_properness_and_antichain']='independently established for the fixed three signatures by exact point witnesses; no universal-family claim'
    verdict=('ACCEPT_FINITE_LOCAL_CERTIFICATES_ONLY' if args.structural or args.engineer
             else 'ACCEPT_SOURCE_BINDING_AND_FINITE_CONTROLS_ONLY')
    out.update(verdict=verdict,ledger='2/9',
               original_obligations_closed=0,gpu_execution='UNTESTED',seconds=perf_counter()-t)
    text=json.dumps(out,indent=2)+'\n'
    if args.out: args.out.write_text(text)
    print(text,end='')

if __name__=='__main__':
    main()
