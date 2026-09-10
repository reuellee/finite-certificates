"""Independent support-only forbidden-parent-marker audit; no producer imports."""
from pathlib import Path
from copy import deepcopy
import hashlib,json

ROOT=Path(__file__).resolve().parent.parent
SHA='82434c6e07fe3290030b057f0eba2f50b522cfc25aabe66b8abf9a8495e55fc4'


def check(rows,data):
    expected=[]
    for idx,r in enumerate(rows):
        A,B=[tuple(map(tuple,r[k])) for k in ('anchor','partner')]
        if any(sum(e in t for t in A)==sum(e in t for t in B)==1 for e in range(1,9)):
            continue
        choices=[]
        for swapped in (False,True):
            linear,quadratic=(B,A) if swapped else (A,B)
            for e in range(1,9):
                lin=[t for t in linear if e in t]
                mov=[t for t in quadratic if e in t]
                fix=[t for t in quadratic if e not in t]
                if len(lin)!=1 or len(mov)!=2 or len(fix)!=2:
                    continue
                pair=set(lin[0])-{e}
                forced=(set().union(*map(set,mov))-{e}) | (set(fix[0])&set(fix[1]))
                markers=pair&forced
                if markers:
                    choices.append({'swap':swapped,'moving_label':e,'linear_pair':sorted(pair),
                                    'quadratic_forced_labels':sorted(forced),'markers':sorted(markers),
                                    'quadratic_moving_triples':list(map(list,mov)),
                                    'quadratic_fixed_triples':list(map(list,fix))})
        expected.append({'source_index':idx,'kinds':r['kinds'],'anchor':r['anchor'],
                         'partner':r['partner'],'marker_choices':choices})
    assert data['pairs']==expected
    count=sum(bool(r['marker_choices']) for r in expected)
    choices=sum(len(r['marker_choices']) for r in expected)
    assert data['remaining_pairs']==len(expected)==45
    assert data['pairs_with_marker']==count==44
    assert data['total_marker_choices']==choices==285
    return {'verdict':'ACCEPT_SUPPORT_ONLY_FORBIDDEN_PARENT_MARKERS',
            'remaining_pairs':45,'pairs_with_marker':44,'ordered_marker_choices':285,
            'uncovered_source_indices':[r['source_index'] for r in expected if not r['marker_choices']],
            'scope':'A guaranteed excluded parent point on a plane-quadric intersection; no Hc1 vanishing or additional pair coverage.'}


def check_regulus(rows,data,markers):
    expected=set();actual=set()
    for idx,r in enumerate(rows):
        A,B=[list(map(set,r[k])) for k in ('anchor','partner')]
        if any(sum(e in t for t in A)==sum(e in t for t in B)==1 for e in range(1,9)):
            continue
        for swap in (False,True):
            E,F=(B,A) if swap else (A,B)
            for e in range(1,9):
                em=[x for x in E if e in x];fm=[x for x in F if e in x]
                if len(em)!=1 or len(fm)!=2:continue
                ep=[x for x in E if e not in x];fp=[x for x in F if e not in x]
                ab=em[0]-{e};lines=[x-{e} for x in fm]
                rank=any(sum(j in x for x in ep)==2 for j in range(1,9))
                linear=any(len(x&ab)==1 and any(not((x&ab)&y) for y in ep) for x in ep)
                skew=all(any(len(line&fp[k])==1 and not((line&fp[k])&fp[1-k]) for k in (0,1)) for line in lines)
                if rank and linear and len(lines[0]|lines[1])==4 and skew:
                    expected.add((idx,swap,e))
    for row in data['rows']:
        idx=row['source_index'];r=rows[idx]
        for o in row['choices']:
            key=(idx,o['swap'],o['moving_label'])
            assert key in expected and key not in actual
            actual.add(key)
            E,F=[list(map(set,r[k])) for k in (('partner','anchor') if o['swap'] else ('anchor','partner'))]
            e=o['moving_label'];ep=[x for x in E if e not in x];fp=[x for x in F if e not in x]
            em=next(x for x in E if e in x);lines=[x-{e} for x in F if e in x]
            assert o['linear_parent_pair']==sorted(em-{e})
            assert o['quadratic_parent_lines']==list(map(sorted,lines))
            assert o['linear_fixed_triples']==list(map(sorted,ep))
            assert o['quadratic_fixed_triples']==list(map(sorted,fp))
            a,b,c,j=o['linear_rank_witness'];assert len({a,b,c})==3 and j in ep[a]&ep[b] and j not in ep[c]
            a,b,j=o['linear_nonzero_witness'];assert ep[a]&(em-{e})=={j} and j not in ep[b]
            assert len(o['quadric_skew_witnesses'])==2
            for line,w in zip(lines,o['quadric_skew_witnesses']):
                a,b,j=w;assert {a,b}=={0,1} and line&fp[a]=={j} and j not in fp[b]
    assert actual==expected and len(actual)==306
    assert data['pairs']==len({i for i,s,e in actual})==45
    assert data['valid_ordered_presentations']==306 and data['every_pair_has_a_valid_presentation'] is True
    parentkeys={(r['source_index'],o['swap'],o['moving_label']) for r in markers['pairs'] for o in r['marker_choices']}
    shared=actual&parentkeys
    assert len(shared)==238 and len({i for i,s,e in shared})==44
    return {'valid_presentations':306,'pairs_with_smooth_split_quadric_presentation':45,
            'compatible_actual_parent_marker_presentations':238,'pairs_with_compatible_actual_parent_marker':44,
            'every_recorded_rank_skew_and_nonzero_witness_checked':True}


def main():
    p=ROOT/'checkpoint/checkpoint/coordinator/HARD_PAIR_RESIDUE.json'
    assert hashlib.sha256(p.read_bytes()).hexdigest()==SHA
    rows=json.loads(p.read_text())['residue']
    data=json.loads((ROOT/'alternative/CONIC_MARKER_GATE.json').read_text())
    result=check(rows,data)
    regulus=json.loads((ROOT/'alternative/REGULUS_GEOMETRY_GATE.json').read_text())
    result['regulus_gate']=check_regulus(rows,regulus,data)
    bad=deepcopy(data);bad['pairs'][0]['marker_choices'][0]['markers']=[8]
    bad2=deepcopy(data);bad2['pairs_with_marker']=45
    hostile={}
    for name,d in [('false_marker',bad),('false_full_coverage',bad2)]:
        try:check(rows,d)
        except AssertionError:hostile[name]=True
        else:raise AssertionError('accepted hostile mutation')
    badreg=deepcopy(regulus);badreg['rows'][0]['choices'][0]['linear_rank_witness'][3]=8
    badreg2=deepcopy(regulus);badreg2['rows'].pop()
    for name,d in [('false_rank_witness',badreg),('missing_regulus_pair',badreg2)]:
        try:check_regulus(rows,d,data)
        except AssertionError:hostile[name]=True
        else:raise AssertionError('accepted hostile regulus mutation')
    result['hostile_controls']=hostile
    text=json.dumps(result,indent=2)+'\n'
    (ROOT/'referee/CONIC_MARKER_REPLAY.json').write_text(text)
    print(text,end='')


if __name__=='__main__':main()
