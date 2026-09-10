"""Independent finite applicability audit; no producer imports or stored-degree trust."""
from pathlib import Path
from collections import Counter
from copy import deepcopy
import hashlib
import json

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / 'checkpoint/checkpoint/coordinator/HARD_PAIR_RESIDUE.json'
SOURCE_SHA = '82434c6e07fe3290030b057f0eba2f50b522cfc25aabe66b8abf9a8495e55fc4'


def support(raw):
    assert isinstance(raw, list) and len(raw) == 4
    out = []
    for triple in raw:
        assert isinstance(triple, list) and len(triple) == 3
        assert all(type(e) is int and 1 <= e <= 8 for e in triple)
        assert triple == sorted(set(triple))
        out.append(tuple(triple))
    assert len(set(out)) == 4
    return tuple(out)


def audit(source, candidate):
    rows = source['residue']
    assert len(rows) == 574
    expect_good, expect_bad = {}, {}
    good_kinds, bad_kinds = Counter(), Counter()
    for i, row in enumerate(rows):
        A, B = support(row['anchor']), support(row['partner'])
        assert not (set(A) & set(B))
        ca = Counter(e for t in A for e in t)
        cb = Counter(e for t in B for e in t)
        pivots = [e for e in range(1, 9) if ca[e] == 1 and cb[e] == 1]
        degrees = [ca[e] + cb[e] for e in range(1, 9)]
        assert row['degree'] == degrees
        kinds = tuple(row['kinds'])
        assert kinds in ((50, 50), (50, 51), (51, 51))
        target = expect_good if pivots else expect_bad
        target[i] = (row, pivots, degrees)
        if pivots:
            good_kinds[kinds] += 1
        else:
            assert degrees == [3] * 8
            bad_kinds[kinds] += 1
    assert len(expect_good) == 529 and len(expect_bad) == 45
    assert candidate['newly_covered_count'] == len(expect_good)
    assert candidate['remaining_count'] == len(expect_bad)
    assert candidate['source'] == 'checkpoint/checkpoint/coordinator/HARD_PAIR_RESIDUE.json'
    for key, expected in [('newly_covered', expect_good), ('remaining', expect_bad)]:
        received = candidate[key]
        assert len(received) == len(expected)
        seen = set()
        for row in received:
            index = row['source_index']
            assert type(index) is int and index in expected and index not in seen
            seen.add(index)
            old, pivots, degrees = expected[index]
            assert row['anchor'] == old['anchor'] and row['partner'] == old['partner']
            assert row['kinds'] == old['kinds'] and row['degree'] == degrees
            if key == 'newly_covered':
                assert row['forgotten_label'] in pivots
            else:
                assert 'forgotten_label' not in row
        assert seen == set(expected)
    return {
        'verdict': 'ACCEPT_FINITE_AFFINE_PAIR_APPLICABILITY',
        'source_sha256': SOURCE_SHA,
        'source_rows': len(rows),
        'newly_covered': len(expect_good),
        'remaining': len(expect_bad),
        'by_kinds': [
            {'kinds': list(k), 'covered': good_kinds[k], 'remaining': bad_kinds[k]}
            for k in sorted(good_kinds)
        ],
        'all_remaining_union_degrees': [3] * 8,
        'stored_degree_recomputed': True,
        'complete_partition_and_pivots_checked': True,
        'inherited_stronger_pair_coverage': 8902,
        'updated_stronger_pair_coverage': 8902 + len(expect_good),
        'inherited_stronger_pair_denominator': 9476,
        'original_obligations_closed': 0,
        'scope': 'Finite applicability of separately reviewed affine-pair theorem to the authenticated inherited residue; no original D or component computation.'
    }


def main():
    raw = SOURCE.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SOURCE_SHA
    source = json.loads(raw)
    candidate = json.loads((ROOT / 'original/AFFINE_PAIR_COVERAGE.json').read_text())
    result = audit(source, candidate)
    mutations = {}
    bad = deepcopy(candidate); bad['newly_covered'][0]['forgotten_label'] = 1
    mutations['invalid_affine_label'] = bad
    bad = deepcopy(candidate); bad['newly_covered'][0]['degree'][0] += 1
    mutations['invented_degree'] = bad
    bad = deepcopy(candidate); bad['newly_covered'][0]['partner'][0][0] = 8
    mutations['changed_source_quartet'] = bad
    bad = deepcopy(candidate); bad['newly_covered'][1] = deepcopy(bad['newly_covered'][0])
    mutations['duplicate_coverage_row'] = bad
    bad = deepcopy(candidate); bad['remaining'].pop()
    mutations['omitted_residue_row'] = bad
    bad = deepcopy(candidate); bad['newly_covered_count'] = 574
    mutations['false_complete_count'] = bad
    controls = {}
    for name, bad in mutations.items():
        try:
            audit(source, bad)
        except (AssertionError, KeyError, IndexError, TypeError):
            controls[name] = True
        else:
            raise AssertionError('hostile mutation accepted: ' + name)
    result['hostile_controls'] = controls
    output = json.dumps(result, indent=2) + '\n'
    (ROOT / 'referee/AFFINE_PAIR_REPLAY.json').write_text(output)
    print(output, end='')


if __name__ == '__main__':
    main()
