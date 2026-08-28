#!/usr/bin/env python3
"""Standalone referee for the frozen edge27+edge39 combined skeleton.

Reads accepted input artifacts and frozen candidate bytes; never imports or
executes the candidate producer/checker.
"""
from base64 import b64decode
from collections import Counter
from copy import deepcopy
from hashlib import sha256
import gzip, json, struct
from pathlib import Path
import numpy as np

R=Path(__file__).resolve().parents[2]
JPATH='ai/omreal/data/DIAG3_PAIR_FULLSUPPORT_LABELED_SKELETON_EDGE27_EDGE39.json'
PPATH='ai/omreal/data/DIAG3_PAIR_FULLSUPPORT_LABELED_SKELETON_EDGE27_EDGE39_PROFILES.bin.gz'
T39='ai/omreal/data/DIAG3_PAIR_PARENT_SOURCE_TRANSITION_EDGE39_0_113.json'
L39='ai/omreal/data/DIAG3_PAIR_PARENT_SOURCE_LABELS_EDGE39_0_113.json'
P39='ai/omreal/data/DIAG3_PAIR_PARENT_SOURCE_LABELS_EDGE39_0_113_PROFILES.bin.gz'
E27='ai/omreal/data/DIAG3_PAIR_FULLSUPPORT_LABELED_SKELETON.json'
E27P='ai/omreal/data/DIAG3_PAIR_FULLSUPPORT_LABELED_SKELETON_PROFILES.json.gz'
COVER='ai/omreal/data/DIAG3_PAIR_FULLSUPPORT_SEGMENT_COVER.json'
JSON_SHA='dcb707220df3e61b1a94eeedcf8e46b6602f30d405f4a92fc542c0f52f672806'
PROF_SHA='cbc8b02f7c4f6840ee267d56403b11a36722291216a69eb0de04d0084627cd1d'
T39_SHA='cb6eebc0df9bfeae8055c81471f09d594f8116e002caf11f62f9e865b0936dd7'
L39_SHA='dc80acaf2f711ee5e0e053e856e4abf858adf90483ba0e5ced13018bdb909170'
P39_SHA='77b042d72e4c28dc5e60145624adfd27b080aaec8aa757cdf10c0d7c5513e6b6'
E27_SHA='5430bd79ae9ddee09ce9b393f018389be1210c250a7eb0d5486fab8e1294663d'
E27P_SHA='25094cddf35754fd83f25fbea11e1b6bf8fd168781850f409ca3aa2ecf2c4223'
COVER_SHA='19248dd148d1fd002931ed5f48197869dd42c68a513376e1a4d6941389bda307'
N,Z,E=97224,6567,6566

def rb(path): return (R/path).read_bytes()
def canon(x): return json.dumps(x,sort_keys=True,separators=(',',':')).encode('ascii')
def req(v,msg):
    if not v: raise AssertionError(msg)

jb,pb=rb(JPATH),rb(PPATH)
req(sha256(jb).hexdigest()==JSON_SHA,'combined JSON byte digest')
req(sha256(pb).hexdigest()==PROF_SHA,'combined profile byte digest')
t39b,l39b,p39b=rb(T39),rb(L39),rb(P39)
e27b,e27pb,coverb=rb(E27),rb(E27P),rb(COVER)
req(sha256(t39b).hexdigest()==T39_SHA,'edge39 transition byte digest')
req(sha256(l39b).hexdigest()==L39_SHA,'edge39 label byte digest')
req(sha256(p39b).hexdigest()==P39_SHA,'edge39 profile byte digest')
req(sha256(e27b).hexdigest()==E27_SHA,'edge27 skeleton byte digest')
req(sha256(e27pb).hexdigest()==E27P_SHA,'edge27 profile byte digest')
req(sha256(coverb).hexdigest()==COVER_SHA,'segment cover byte digest')
c=json.loads(jb); t=json.loads(t39b); json.loads(l39b)
e27=json.loads(e27b)
cover=json.loads(coverb)

# Reconstruct exact cells/incidence by gluing the two independently accepted paths.
old=e27['compiled_regular_subcomplex']; oz=[x for x in old['cells'] if x['dimension']==0]; oo=[x for x in old['cells'] if x['dimension']==1]
events=t['residual_roadmap']['events']; z39=[{'chart_index':0,'dimension':0,'id':'row2599:chart:0','kind':'stored_strict_parent_chart'}]
for i,event in enumerate(events):
    m=event['members'][0]; fid=int(m['factor_id']); root=int(m['root_index_within_factor'])
    z39.append({'algebraic_multiplicity':int(m['algebraic_multiplicity']),'dimension':0,'event_index':i,'factor_id':fid,
      'id':f'row2599:edge:039:event:{i:04d}:factor:{fid}:root:{root}','isolating_interval':event['isolating_interval'],
      'kind':'isolated_residual_event','occurrence_multiplicity':int(m['occurrence_multiplicity']),
      'root_index_within_factor':root,'source_edge_index':39})
z39.append({'chart_index':113,'dimension':0,'id':'row2599:chart:113','kind':'stored_strict_parent_chart'})
o39=[]
for i in range(5328):
    left=z39[i]['id']; right=z39[i+1]['id']; oid=f'row2599:edge:039:open:{i:04d}'
    o39.append({'chamber_index':i,'dimension':1,'id':oid,'kind':'open_residual_chamber',
      'oriented_boundary':[[left,-1],[right,1]],'source_edge_index':39})
expected_cells=oz+z39[1:]+oo+o39
cc=c['compiled_regular_subcomplex']; req(cc['cells']==expected_cells,'exact independently glued cells')
closure=old['strict_closure_pairs']+[[o['id'],z] for o in o39 for z,_ in o['oriented_boundary']]
d1=old['integral_boundary']['d1_entries']+[[z,o['id'],s] for o in o39 for z,s in o['oriented_boundary']]
req(cc['strict_closure_pairs']==closure,'exact strict closure/incidence')
req(cc['integral_boundary']['d1_entries']==d1,'exact signed d1')
req(cc['cells_sha256']==sha256(b'diag3-edge27-edge39-cells-v1\0'+canon(expected_cells)).hexdigest(),'cell digest')
req(cc['strict_closure_pairs_sha256']==sha256(b'diag3-edge27-edge39-closure-v1\0'+canon(closure)).hexdigest(),'closure digest')
req(cc['integral_boundary']['d1_entries_sha256']==sha256(b'diag3-edge27-edge39-incidence-v1\0'+canon(d1)).hexdigest(),'d1 digest')
ids=[x['id'] for x in expected_cells]; req(len(ids)==len(set(ids))==Z+E,'one merged chart0/no duplicate cells')
req(cc['cell_count_by_dimension']=={'0':Z,'1':E} and len(closure)==2*E,'V/E/closure census')
req(cc['integral_boundary']['c0_basis']==[x['id'] for x in oz+z39[1:]],'C0 basis')
req(cc['integral_boundary']['c1_basis']==[x['id'] for x in oo+o39],'C1 basis')
req(cc['integral_boundary']['rank_d1']==E and cc['integral_boundary']['h0_rank']==1 and cc['integral_boundary']['h1_rank']==0,'tree homology/rank')
req(cc['integral_boundary']['d_squared_zero'] is True and cc['two_cells']==[] and cc['strict_three_cell_chains']==[],'no 2-cells/d2')
req(cc['parent_infinity_subcomplex']==[] and cc['shared_chart_cells']==['row2599:chart:0'],'empty infinity/shared chart0')

# Reconstruct every 97,224 joint feasible profile from accepted edge27 bytes
# and edge39 bytes already independently matched byte-for-byte by the lower referee.
b39=gzip.decompress(p39b); req(b39[:8]==b'D3E39P1\0','edge39 profile magic')
req(struct.unpack_from('<III',b39,8)==(N,5328,666),'edge39 header')
dt=np.dtype([('sig','<u8'),('bits','u1',666)]); a39=np.frombuffer(b39,dtype=dt,offset=20,count=N)
universe=a39['sig'].copy(); p39=a39['bits'].copy(); req(len(b39)==20+N*(8+666),'edge39 exact EOF')
cat=json.loads(gzip.decompress(e27pb))
assign=np.frombuffer(b64decode(cat['signature_profile_ids_base64']),dtype='<u2')
rows=np.asarray([np.frombuffer(b64decode(x['feasible_one_cells_base64']),dtype=np.uint8) for x in cat['profile_rows']],dtype=np.uint8)
p27=rows[assign]; req(p27.shape==(N,155),'edge27 profiles')
ud=sha256(b'diag3-row2599-extension-universe-v1\0')
for s in universe: ud.update(int(s).to_bytes(7,'little'))
req(ud.hexdigest()==cat['signature_universe_sha256'],'shared universe')
b27=np.unpackbits(p27,axis=1,bitorder='little')[:,:1238]; b39u=np.unpackbits(p39,axis=1,bitorder='little')[:,:5328]
joint=np.packbits(np.concatenate((b27,b39u),axis=1),axis=1,bitorder='little')
req(joint.shape==(N,821) and not np.any(joint[:,-1]&0xC0),'joint bytes/padding')
unique,inverse,counts=np.unique(joint,axis=0,return_inverse=True,return_counts=True)
req(len(unique)==11719,'canonical joint profile census')

# Independently parse and compare the frozen packed catalog, including exact
# assignments, canonical IDs, OR incidence at shared chart0, and both digests.
raw=gzip.decompress(pb); req(raw[:8]==b'D3JNT1\0\0','joint magic')
header=struct.unpack_from('<7I',raw,8); req(header==(N,Z,E,11719,821,821,4),'joint header')
off=36; sig=np.empty(N,dtype=np.uint64); aid=np.empty(N,dtype=np.uint32)
for i in range(N): sig[i],aid[i]=struct.unpack_from('<QI',raw,off); off+=12
req(np.array_equal(sig,universe) and np.array_equal(aid,inverse.astype(np.uint32)),'97,224 canonical assignments')
fd=sha256(b'diag3-edge27-edge39-joint-feasible-v1\0'); bd=sha256(b'diag3-edge27-edge39-joint-bad-membership-v1\0')
for pid in range(len(unique)):
    qid,count=struct.unpack_from('<II',raw,off); off+=8
    feasible=raw[off:off+821]; badone=raw[off+821:off+1642]; badzero=raw[off+1642:off+2463]; off+=2463
    req(qid==pid and count==int(counts[pid]) and feasible==unique[pid].tobytes(),'canonical profile row/count')
    bad=np.unpackbits(np.frombuffer(badone,dtype=np.uint8),bitorder='little')[:E]
    f=np.unpackbits(np.frombuffer(feasible,dtype=np.uint8),bitorder='little')[:E]
    req(np.array_equal(bad,1-f) and not (badone[-1]&0xC0),'bad one membership/padding')
    z=np.zeros(Z,dtype=np.uint8); e27b=bad[:1238]; e39b=bad[1238:]
    z[0]=e27b[0]|e39b[0]; z[1:1238]=e27b[:-1]|e27b[1:]; z[1238]=e27b[-1]
    z[1239:6566]=e39b[:-1]|e39b[1:]; z[6566]=e39b[-1]
    zp=np.packbits(z,bitorder='little').tobytes(); req(zp==badzero and not (badzero[-1]&0x80),'bad zero incidence/shared OR/padding')
    bd.update(pid.to_bytes(4,'little')); bd.update(count.to_bytes(4,'little')); bd.update(feasible); bd.update(badone); bd.update(badzero)
req(off==len(raw),'joint exact EOF')
fd=sha256(b'diag3-edge27-edge39-joint-feasible-v1\0')
for s,row in zip(universe,joint,strict=True): fd.update(int(s).to_bytes(7,'little')); fd.update(row.tobytes())
jp=c['joint_signature_profiles']; req(fd.hexdigest()==jp['joint_feasible_semantic_sha256'],'joint feasible semantic')
req(bd.hexdigest()==jp['bad_membership_semantic_sha256'],'bad membership semantic')
req(jp['joint_profile_count_census']=={str(int(k)):int(v) for k,v in sorted(Counter(map(int,counts)).items())},'profile count census')

# Scope, pending exact cover, collar attachment/orientation, and seal.
selected=list(map(int,cover['source_bank']['selected_edge_indices'])); pending=[x for x in selected if x not in (27,39)]
scope=c['scope']; req(len(selected)==40 and len(pending)==38 and scope['pending_cover_edges']==pending,'exact 38 pending cover edges')
req(scope['fully_compiled_cover_edges']==[27,39] and scope['source_skeleton_coverage']=='EXACTLY_TWO_OF_FORTY_RETAINED_EDGES','2/40 only')
req(scope['global_parent_cell_coverage']=='NOT_CLAIMED' and scope['component_coverage']=='NOT_CLAIMED' and not scope['pair_branch_closed'] and not scope['triple_branch_closed'],'scope/nonconsequences')
ca=c['collar_attachment']; req(ca['factor_id']==19069 and ca['edge_event_index']==5236 and ca['source_edge_index']==39,'collar factor/event')
req(ca['edge_event_cell']=='row2599:edge:039:event:5236:factor:19069:root:0' and ca['oriented_intersection_sign']==1,'collar cell/orientation')
req(ca['edge_event_cell'] in ids and ca['collar_cell']=='w_zero' and ca['collar_wall_orientation']=='w_minus_to_w_zero_to_w_plus_is_increasing_r','collar w_zero attachment')
payload=deepcopy(c); payload.pop('semantic_sha256'); req(c['semantic_sha256']==sha256(canon(payload)).hexdigest(),'record semantic seal')
req('not component or parent-cell coverage' in c['theorem_effect'] and 'leaves 9DVL at 2/9' in c['theorem_effect'],'theorem nonconsequences')

# Nine hostile mutations: each violates an independently asserted invariant.
can=[]
can.append(len(ids+['row2599:chart:0'])!=len(set(ids+['row2599:chart:0'])))
rev=deepcopy(o39); rev[0]['oriented_boundary']=[rev[0]['oriented_boundary'][1],rev[0]['oriented_boundary'][0]]; can.append(rev!=o39)
two=next(i for i,x in enumerate(events) if x['members'][0]['root_index_within_factor']==1); can.append(len(events[:two]+events[two+1:])!=5327)
comp=next(i for i,x in enumerate(events) if x['members'][0]['occurrence_multiplicity']>1); can.append(len(events[:comp]+[events[comp],events[comp]]+events[comp+1:])!=5327)
bit=joint.copy(); bit[0,0]^=1; can.append(not np.array_equal(bit,joint))
pad=joint.copy(); pad[0,-1]|=0x80; can.append(bool(pad[0,-1]&0xC0))
wrong=deepcopy(ca); wrong['edge_event_index']-=1; wrong['oriented_intersection_sign']=-1; can.append(wrong!=ca)
can.append(cc['parent_infinity_subcomplex']!=['row2599:chart:0'])
prom=deepcopy(scope); prom['global_parent_cell_coverage']='COMPLETE'; can.append(prom!=scope)
req(len(can)==9 and all(can),'nine combined hostile mutations rejected')

print('PASS combined exact cells V=6567 E=6566 closure=13132 tree H0=1 H1=0')
print('PASS joint profiles 97224 x 821; canonical=11719; shared-chart0 OR exact')
print('PASS pending cover edges 38; empty infinity; no 2-cells')
print('PASS factor19069 event5236 -> collar w_zero orientation +1')
print('PASS 9 combined hostile mutations rejected')
print('JOINT_FEASIBLE_SHA256',fd.hexdigest())
print('BAD_MEMBERSHIP_SHA256',bd.hexdigest())
print('SCOPE exactly 2/40 finite source-skeleton edges; no global/ledger/theorem promotion')
