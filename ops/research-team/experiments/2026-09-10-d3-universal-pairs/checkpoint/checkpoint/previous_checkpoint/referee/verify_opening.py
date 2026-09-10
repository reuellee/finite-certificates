"""Reconstruct the inherited three-row and near-singular fixtures independently."""
import copy
import json
from pathlib import Path
from exact import Q, matrix, colex, det, rank, normals, brackets, sign, verify_witness, reject

HERE=Path(__file__).resolve().parent
INP=HERE.parent/'inputs'/'certificates'


def main():
    w=json.loads((INP/'THREE_ROW_WITNESS.json').read_text())
    n=json.loads((INP/'NEAR_SINGULAR_CANARY.json').read_text())
    y=matrix(w['parent']); sig=w['signature']; sup=w['support']['indices']
    assert [list(colex(8,3)[i]) for i in sup] == w['support']['triples']
    a=normals(y,sig)
    assert [a[i] for i in sup] == matrix(w['signed_normals'])
    result=verify_witness(y,sig,sup,w['weights'],w['parent_signs'],2)
    assert all(rank([a[i],a[j]]) == 2 for i,j in [(sup[0],sup[1]),(sup[0],sup[2]),(sup[1],sup[2])])
    ny=matrix(n['parent']); na=normals(ny,sig)
    assert [sign(x) for x in brackets(ny)] == w['parent_signs']
    assert [sign(x) for x in brackets(ny)] == n['parent_signs']
    assert min(abs(x) for x in brackets(ny)) == Q(n['minimum_absolute_parent_bracket'])
    assert rank([na[i] for i in sup]) == 3
    cols=n['minor_columns']; minor=det([[na[i][j] for j in cols] for i in sup])
    assert minor == Q(n['nonzero_rank_three_minor'])
    row,col=w['coordinate']
    assert ny[row][col]-y[row][col] == Q(n['offset_from_witness'])
    assert all(ny[r][c] == y[r][c] for r in range(4) for c in range(8) if (r,c)!=(row,col))
    badw=list(w['weights']); badw[0]+=1
    zeros=[0]*len(sup)
    wrongy=copy.deepcopy(y); wrongy[0]=[-x for x in wrongy[0]]
    signs=list(w['parent_signs']); signs[0]*=-1
    checks={
        'altered_positive_weight':reject(lambda:verify_witness(y,sig,sup,badw,w['parent_signs'],2)),
        'duplicate_support':reject(lambda:verify_witness(y,sig,[sup[0],sup[0],sup[2]],w['weights'],w['parent_signs'],2)),
        'supported_signature_bit_flip':reject(lambda:verify_witness(y,sig^(1<<sup[0]),sup,w['weights'],w['parent_signs'],2)),
        'zero_weight_vector':reject(lambda:verify_witness(y,sig,sup,zeros,w['parent_signs'],2)),
        'near_singular_relation':reject(lambda:verify_witness(ny,sig,sup,w['weights'],w['parent_signs'],2)),
        'near_singular_rank':rank([na[i] for i in sup])!=2,
        'wrong_parent_chamber':reject(lambda:verify_witness(wrongy,sig,sup,w['weights'],w['parent_signs'],2)),
        'altered_expected_parent_sign':reject(lambda:verify_witness(y,sig,sup,w['weights'],signs,2)),
        'floating_input':reject(lambda:matrix([[1.0]])),
    }
    result.update({'all70_parent_signs':True,'all56_signed_normals_reconstructed':True,
                   'normal_convention':'raw cofactors, colex triples; bit1 positive',
                   'all_three_support_pairs_rank_two':True,'near_singular_exact_rank':3,
                   'near_singular_minor':str(minor),'hostile_controls':checks,
                   'scope':'finite literal inherited fixtures only; no global cohomology map'})
    out=HERE/'OPENING_REPLAY.json'
    out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    main()
