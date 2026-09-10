"""Independent incidence applicability audit of the two-column affine-fiber theorem."""
from pathlib import Path
from itertools import combinations
from copy import deepcopy
import hashlib,json

ROOT=Path(__file__).resolve().parent.parent
SHA='82434c6e07fe3290030b057f0eba2f50b522cfc25aabe66b8abf9a8495e55fc4'


def inspect(rows,data,final=None):
    expected=[];witnesses=[];left=[];full_covered=[];full_remaining=[]
    for idx,row in enumerate(rows):
        A,B=[list(map(set,row[k])) for k in ('anchor','partner')]
        if any(sum(e in t for t in A)==sum(e in t for t in B)==1 for e in range(1,9)):
            continue
        options=[];rich_options=[]
        for swapped in (False,True):
            P,Q=(B,A) if swapped else (A,B)
            for e,j in combinations(range(1,9),2):
                pe=[t for t in P if e in t];pj=[t for t in P if j in t]
                qe=[t for t in Q if e in t];qj=[t for t in Q if j in t]
                shared=[t for t in Q if e in t and j in t]
                if not (len(pe)==len(pj)==1 and pe==pj and len(qe)==len(qj)==2 and len(shared)==1):
                    continue
                moving={e,j}
                a=next(iter(pe[0]-moving))
                P0=[t for t in P if not(t&moving)]
                assert len(P0)==3
                rank_witness=[]
                for v in range(1,9):
                    included=[k for k,t in enumerate(P0) if v in t]
                    if len(included)==2:
                        excluded=next(k for k in range(3) if k not in included)
                        rank_witness.append([v,*included,excluded])
                assert rank_witness
                excluded_a=[k for k,t in enumerate(P0) if a not in t]
                assert excluded_a
                qeonly=[t for t in Q if e in t and j not in t]
                qjonly=[t for t in Q if j in t and e not in t]
                Q0=[t for t in Q if not(t&moving)]
                assert len(qeonly)==len(qjonly)==len(Q0)==1
                bcpair=qeonly[0]-{e};dfpair=qjonly[0]-{j}
                assert len(bcpair)==len(dfpair)==2
                options.append({'swapped':swapped,'moving':[e,j],
                                'P_triple':sorted(pe[0]),'Q_shared':sorted(shared[0])})
                rich_options.append({'swapped':swapped,'moving':[e,j],
                                     'P_shared':sorted(pe[0]),'Q_shared':sorted(shared[0]),
                                     'Q_only_e':sorted(qeonly[0]),'Q_only_j':sorted(qjonly[0]),
                                     'Q_free':sorted(Q0[0])})
                witnesses.append({'source_index':idx,'swapped':swapped,'moving':[e,j],
                                  'fixed_P_rank_witness':rank_witness[0],
                                  'P_concurrence_not_a_witness':excluded_a[0]})
        if options:
            expected.append({'source_index':idx,'kinds':row['kinds'],'options':options})
            full_covered.append(dict(row,source_index=idx,options=rich_options))
        else:
            left.append(idx)
            full_remaining.append(dict(row,source_index=idx))
    assert data==expected
    assert len(expected)==27 and len(left)==18
    assert sum(len(r['options']) for r in expected)==39
    if final is not None:
        assert final['new_covered_count']==27 and final['remaining_count']==18
        assert final['source_sha256']==hashlib.sha256((ROOT/'original/AFFINE_PAIR_COVERAGE.json').read_bytes()).hexdigest()
        assert final['covered']==full_covered and final['remaining']==full_remaining
    return {'verdict':'ACCEPT_TWO_COLUMN_INCIDENCE_APPLICABILITY',
            'source_sha256':SHA,'additional_pair_orbits':len(expected),'presentations':len(witnesses),
            'remaining_balanced_pairs':len(left),'remaining_source_indices':left,
            'fixed_three_P_planes_rank_and_distinct_concurrence_checked':True,
            'source_indices':[r['source_index'] for r in expected],
            'final_partition_checked':final is not None,
            'updated_stronger_pair_coverage':9458,
            'stronger_pair_denominator':9476,'original_obligations_closed':0,
            'scope':'Incidence applicability of the separately accepted conventional two-column theorem; no original injectivity or triple closure.'}


def main():
    p=ROOT/'checkpoint/checkpoint/coordinator/HARD_PAIR_RESIDUE.json'
    assert hashlib.sha256(p.read_bytes()).hexdigest()==SHA
    rows=json.loads(p.read_text())['residue']
    data=json.loads((ROOT/'original/TWO_COLUMN_PERSPECTIVE_CANDIDATES.json').read_text())
    final=json.loads((ROOT/'original/TWO_COLUMN_AFFINE_COVERAGE.json').read_text())
    result=inspect(rows,data,final)
    bad=deepcopy(data);bad[0]['options'][0]['moving']=[1,8]
    bad2=deepcopy(data);bad2.pop()
    bad3=deepcopy(data);bad3[1]=deepcopy(bad3[0])
    controls={}
    for key,b in [('wrong_moving_pair',bad),('missing_orbit',bad2),('duplicate_orbit',bad3)]:
        try:inspect(rows,b)
        except AssertionError:controls[key]=True
        else:raise AssertionError('accepted hostile mutation')
    wrong=deepcopy(final);wrong['covered'][0]['options'][0]['Q_free']=[1,2,8]
    try:inspect(rows,data,wrong)
    except AssertionError:controls['wrong_final_fixed_triple']=True
    else:raise AssertionError('accepted hostile final partition')
    result['hostile_controls']=controls
    text=json.dumps(result,indent=2)+'\n'
    (ROOT/'referee/TWO_COLUMN_REPLAY.json').write_text(text)
    print(text,end='')


if __name__=='__main__':main()
