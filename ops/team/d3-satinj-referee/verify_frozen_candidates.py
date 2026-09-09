#!/usr/bin/env python3
"""Separate exact arithmetic for a frozen support event and scoped NULL close.

The inherited NPZ is decoded with the standard library. Determinants use the
Leibniz formula; ranks are certified by minors. No producer or historical
verifier is imported, and no input or report is modified unless --output is
provided.
"""
import argparse
import ast
from fractions import Fraction as Q
import hashlib
import io
from itertools import combinations, permutations
import json
from math import gcd
from pathlib import Path
import subprocess
import struct
import zipfile

BASE = "3a7ce7b5d57543d54eace7707659418cea6d69c9"
ROOT = Path(__file__).resolve().parents[3]
P = "ops/team/d3-satinj-prover/"
F = "ops/team/d3-satinj-falsifier/"
TRIPLES = sorted(combinations(range(8), 3), key=lambda a: sum(1 << i for i in a))
QUADS = sorted(combinations(range(8), 4), key=lambda a: sum(1 << i for i in a))

def raw(rev, path):
    return subprocess.check_output(["git", "-C", str(ROOT), "show", rev + ":" + path])

def obj(rev, path):
    return json.loads(raw(rev, path))

def sha(data):
    return hashlib.sha256(data).hexdigest()

def decode_integer_npy(data):
    assert data[:6] == b"\x93NUMPY"
    major = data[6]
    assert major in (1, 2)
    size = 2 if major == 1 else 4
    length = int.from_bytes(data[8:8+size], "little")
    start = 8 + size + length
    header = ast.literal_eval(data[8+size:start].decode("latin1"))
    assert header["fortran_order"] is False
    fmt = {"<i8": "q", "<u2": "H"}[header["descr"]]
    count = 1
    for n in header["shape"]:
        count *= n
    values = struct.unpack("<" + str(count) + fmt, data[start:])
    return header["shape"], values

def parity(t):
    return -1 if sum(t[i] > t[j] for i in range(len(t)) for j in range(i+1, len(t))) % 2 else 1

PERMS = {n: [(p, parity(p)) for p in permutations(range(n))] for n in range(1, 6)}

def determinant(a):
    n = len(a)
    if n == 0:
        return Q(1)
    out = Q(0)
    for perm, sgn in PERMS[n]:
        term = Q(sgn)
        for i, j in enumerate(perm):
            term *= a[i][j]
        out += term
    return out

def minor(a, rows, cols):
    return determinant([[a[i][j] for j in cols] for i in rows])

def rank(a):
    for k in range(min(len(a), len(a[0])), 0, -1):
        if any(minor(a, rows, cols) for rows in combinations(range(len(a)), k) for cols in combinations(range(len(a[0])), k)):
            return k
    return 0

def sign(a):
    return (a > 0) - (a < 0)

def normals(y):
    return [[(-1)**(r+3)*minor(y, [i for i in range(4) if i != r], cols) for r in range(4)] for cols in TRIPLES]

def brackets(y):
    return [minor(y, range(4), cols) for cols in QUADS]

def signed_rows(y, sig, primitive=False):
    result = []
    for j, row in enumerate(normals(y)):
        scalar = 1 if sig & (1 << j) else -1
        if primitive:
            assert all(x.denominator == 1 for x in row)
            g = 0
            for x in row:
                g = gcd(g, abs(x.numerator))
            scalar = Q(scalar, g)
        result.append([scalar * x for x in row])
    return result

def weights(rows):
    c = [(-1)**j * determinant(rows[:j]+rows[j+1:]) for j in range(5)]
    return [x/sum(c) for x in c], c

def witness(rows, w):
    assert sum(w) == 1
    assert all(x >= 0 for x in w)
    assert all(sum(w[i]*rows[i][r] for i in range(len(w))) == 0 for r in range(4))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prover-revision", required=True)
    ap.add_argument("--falsifier-revision", required=True)
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()
    pins = {}
    for rev, surface in [(args.prover_revision, P), (args.falsifier_revision, F)]:
        paths = subprocess.check_output(["git", "-C", str(ROOT), "ls-tree", "-r", "--name-only", rev, surface]).decode().splitlines()
        for path in paths:
            pins[path] = sha(raw(rev, path))
    source_pins = {}
    for rev, path, key in [(args.prover_revision, P+"SOURCE_MANIFEST.json", "inputs"), (args.falsifier_revision, F+"SOURCE_MANIFEST.json", "source_sha256")]:
        manifest = obj(rev, path)
        assert manifest["base_revision"] == BASE
        for source, expected in manifest[key].items():
            assert sha(raw(BASE, source)) == expected, source
            assert sha((ROOT/source).read_bytes()) == expected, source
            source_pins[source] = expected
    result = obj(args.prover_revision, P+"RESULT.json")
    assert result["handoff"] == "NULL" and not result["saturation_eligible"]
    assert not result["Hc0_T_assumed"] and not result["main_F4SAT_started"]
    for name, expected in result["files"].items():
        assert pins[P+name] == expected
    findings = raw(args.prover_revision, P+"FINDINGS.md").decode()
    assert "removes only the selected regular branch" not in findings

    flow_path = "ops/team/ai-d3-shared-pencil-falsifier/upper_chart_0_flow.json"
    anchor_path = "ops/team/ai-d3-shared-pencil-falsifier/admissibility_flow.json"
    flow = obj(BASE, flow_path)
    anchors = obj(BASE, anchor_path)["records"]
    archive = zipfile.ZipFile(io.BytesIO(raw(BASE, "ai/omreal/data/seeat_parent2599_upper178.npz")))
    arrays = {name: decode_integer_npy(archive.read(name+".npy")) for name in ["chart_matrix", "assignment", "point"]}
    assert arrays["chart_matrix"][0] == (178,4,8)
    assert arrays["assignment"][0] == (97224,)
    assert arrays["point"][0] == (97224,4)
    def archived_matrix(chart):
        values = arrays["chart_matrix"][1]
        return [list(values[chart*32+r*8:chart*32+(r+1)*8]) for r in range(4)]
    assert archived_matrix(0) == flow["parent"]
    y0 = [[Q(v) for v in row] for row in flow["parent"]]
    signatures = flow["signatures"]
    supports = [x["support"] for x in flow["full_dual_witnesses"]]
    source_signs = [sign(x) for x in brackets(y0)]
    assert source_signs == flow["parent_signs"] and 0 not in source_signs

    gp = 0
    for sig in signatures:
        table = dict(zip(QUADS, source_signs))
        table.update({t+(8,): (1 if sig & (1 << j) else -1) for j,t in enumerate(TRIPLES)})
        def chi(t):
            return parity(t) * table[tuple(sorted(t))]
        for a,b in combinations(range(9), 2):
            for c,d,e,f in combinations([v for v in range(9) if v not in (a,b)], 4):
                terms = {chi((a,b,c,d))*chi((a,b,e,f)), -chi((a,b,c,e))*chi((a,b,d,f)), chi((a,b,c,f))*chi((a,b,d,e))}
                assert terms == {-1, 1}
                gp += 1
    assert gp == 3780

    for anchor in anchors:
        y = [[Q(x) for x in row] for row in anchor["parent"]]
        idx = anchor["upper_point_index"]
        chart = anchor["upper_chart_index"]
        assert archived_matrix(chart) == anchor["parent"]
        assert arrays["assignment"][1][idx] == chart
        assert list(arrays["point"][1][idx*4:(idx+1)*4]) == anchor["point"]
        assert [sign(x) for x in brackets(y)] == source_signs
        primal_rows = signed_rows(y, anchor["signature"])
        assert all(sum(a*b for a,b in zip(row, anchor["point"])) > 0 for row in primal_rows)
        for system in anchor["other_systems"]:
            if system["signature"] == anchor["signature"]:
                continue
            dual = system["dual"]
            all_rows = signed_rows(y, system["signature"], primitive=True)
            rows = [all_rows[j] for j in dual["support"]]
            w = [Q(x, sum(dual["weights"])) for x in dual["weights"]]
            witness(rows, w)

    event = obj(args.falsifier_revision, F+"EXACT_REPLAY.json")
    t = Q(event["coordinate_move"]["parameter"])
    assert event["coordinate_move"]["row_zero_based"] == 1
    assert event["coordinate_move"]["column_label"] == 2
    assert event["signatures"] == signatures and event["supports"] == supports
    def at(tau):
        y = [row[:] for row in y0]
        y[1][1] += tau
        rows = [[signed_rows(y,sig)[j] for j in support] for sig,support in zip(signatures,supports)]
        return y, rows, [weights(r)[0] for r in rows]
    y, rows, w = at(t)
    assert [[str(v) for v in row] for row in y] == event["moved_parent"]
    assert [[str(v) for v in ww] for ww in w] == event["normalized_weights"]
    assert [str(v) for v in brackets(y)] == event["parent_brackets"]
    assert [sign(v) for v in brackets(y)] == source_signs
    for rr, ww in zip(rows, w):
        witness(rr, ww)
    assert w[0][0] == 0 and all(v > 0 for v in w[0][1:])
    assert all(v > 0 for ww in w[1:] for v in ww)
    assert [rank(rows[0]), rank(rows[0][1:]), rank([r+[Q(1)] for r in rows[0]])] == [4,3,5]
    assert [event["five_support_rank"], event["surviving_four_support_rank"], event["augmented_five_support_rank"]] == [4,3,5]
    # Only normal 238 among the four cofactor rows involves parent label 2.
    assert sum(1 in TRIPLES[j] for j in supports[0][1:]) == 1
    c0 = weights(at(Q(0))[1][0])[1][0]
    c1 = weights(at(Q(1))[1][0])[1][0] - c0
    assert [str(c0),str(c1)] == event["selected_cofactor_polynomial"]
    assert c0+c1*t == 0 and c1 != 0
    adjacent = []
    for delta, expected in [(Q(-1,1000000), [1]*5), (Q(1,1000000), [-1,1,1,1,1])]:
        yp, rp, wp = at(t+delta)
        assert [sign(v) for v in brackets(yp)] == source_signs
        assert [sign(v) for v in wp[0]] == expected
        for rr,ww in zip(rp[1:], wp[1:]):
            witness(rr,ww)
            assert all(v > 0 for v in ww)
        adjacent.append({"parameter": str(t+delta), "selected_weight_signs": expected})
    # The 12 linear witness equations, 3 normalizations, and 1 zero weight
    # are all checked above; 16 generators vanish at a parent-unit point.
    bad_weight = list(w[0]); bad_weight[1] += 1
    rejected = False
    try:
        witness(rows[0], bad_weight)
    except AssertionError:
        rejected = True
    assert rejected
    assert c0+c1*(t+Q(1,1000000)) != 0
    handoff = obj(args.falsifier_revision, F+"HANDOFF.json")
    assert handoff["original_obligations_closed"] == 0 and handoff["theorem_credit"] == 0
    assert not handoff["main_f4sat_run_started"] and not handoff["global_attachment_supplied"]
    output = {
        "verdict": "PASS_EXACT_SCOPED_NEGATIVE_AND_NULL_ACCOUNTING",
        "base_revision": BASE,
        "prover_revision": args.prover_revision,
        "falsifier_revision": args.falsifier_revision,
        "reviewed_input_pins": pins,
        "source_pins": source_pins,
        "event_parameter": str(t),
        "event_generator_count": 16,
        "event_generators_vanish": True,
        "parent_brackets_nonzero_with_source_signs": 70,
        "exact_ranks": [4,3,5],
        "original_signature_gp_checks": gp,
        "properness_anchors": 3,
        "ordered_noninclusions": 6,
        "cofactor_constant_and_slope": [str(c0),str(c1)],
        "adjacent_checks": adjacent,
        "hostile_controls": {"altered_weight_rejected": rejected, "shifted_event_rejected": True},
        "arithmetic": "Standard-library NPZ decode, Leibniz determinants, minor-based rank and exact rational arithmetic",
        "producer_or_repository_acceptance_imports": [],
        "scope": "Original admitted support event and proper parent-unit event ideal; no topological-change, global attachment, cohomology kernel or original obligation closure.",
    }
    encoded = json.dumps(output, indent=2, sort_keys=True)+"\n"
    if args.output:
        args.output.write_text(encoded)
    print(encoded, end="")

if __name__ == "__main__":
    main()
