"""Certificate-corruption controls at the one frozen point; no new search."""
from copy import deepcopy
from pathlib import Path
import json
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CHECKER = HERE / 'verify_rank_closures.py'


def run(path):
    return subprocess.run([sys.executable, '-B', str(CHECKER), str(path)],
                          cwd=ROOT, capture_output=True, text=True, timeout=30)


def main():
    path = HERE / 'certificate.json'
    certificate = json.loads(path.read_text())
    good = run(path)
    assert good.returncode == 0, good.stderr
    report = json.loads(good.stdout)
    assert report['status'] == 'PASS'
    (HERE / 'VERIFICATION.json').write_text(json.dumps(report, indent=2) + '\n', newline='\n')
    variants = []

    omitted = deepcopy(certificate)
    first = next(r for r in omitted['coverage'] if len(r['closure']) == 6)
    removed = next(k for k in first['closure'] if k not in first['pair'])
    first['closure'].remove(removed)
    variants.append(('omitted_added_closure_row', omitted, 'Closure was not computed exactly'))

    # Choose an old valid two-row certificate that fails an added closure row.
    old = json.loads((ROOT / 'ops/team/ai-d3-shared-pencil-falsifier/upper_chart_0_flow.json').read_text())
    old_assignments = {(e, i, j): w for e, i, j, w in old['negative_certificate']['coverage_rows']}
    reused_wrong = deepcopy(certificate)
    selected_record = None
    for record in reused_wrong['coverage']:
        w = old_assignments[(record['label'], *record['pair'])]
        witness = certificate['witness_pool'][w]
        signature = certificate['signatures'][witness['signature_index']]
        added = [i for i in record['closure'] if i not in record['pair']]
        if any((1 if signature >> i & 1 else -1) * sum(a * b for a, b in zip(
                certificate['primitive_normals'][i], witness['point'])) <= 0 for i in added):
            record['witness'] = w
            selected_record = (record['label'], record['pair'], w)
            break
    assert selected_record is not None
    variants.append(('old_separator_fails_added_row', reused_wrong, 'Strict separator failed on retained row'))

    incomplete = deepcopy(certificate)
    incomplete['coverage'].pop()
    variants.append(('missing_indexed_pair', incomplete, 'assert seen == required'))

    wrong_parent = deepcopy(certificate)
    wrong_parent['parent'][0][0] += 1
    variants.append(('copied_parent_not_frozen_input', wrong_parent, "certificate['parent'] == parent"))

    outcomes = []
    temporary = HERE / '_rejection_control.json'
    assert temporary.parent.resolve() == HERE.resolve() and not temporary.exists()
    try:
        for name, data, expected in variants:
            temporary.write_text(json.dumps(data) + '\n', newline='\n')
            result = run(temporary)
            assert result.returncode != 0 and expected in result.stderr, (name, result.stdout, result.stderr)
            outcomes.append({'control': name, 'status': 'REJECTED_AS_REQUIRED',
                             'exit_code': result.returncode, 'expected_error_fragment': expected})
    finally:
        if temporary.exists():
            temporary.unlink()
    result = {'status': 'PASS', 'uncorrupted_certificate': 'PASS', 'controls': outcomes,
              'old_two_row_assignment_rejected': selected_record,
              'new_geometric_predicate_points': 0}
    (HERE / 'REJECTION_CONTROLS.json').write_text(json.dumps(result, indent=2) + '\n', newline='\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
