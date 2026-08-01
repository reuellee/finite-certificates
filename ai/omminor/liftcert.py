#!/usr/bin/env python3
"""Turn a non-realizable DELETION into a certificate for the 9-element class.

    python liftcert.py --sample 40            # sample from data/minors_sweep.jsonl
    python liftcert.py --sample 40 --canary   # + the sabotage canaries

THE LIFT
--------
Let phi: E \\ {e} -> {1..8} be the order-preserving bijection and delta =
chi \\ e, so delta(phi B) = chi(B) for every 4-subset B of E \\ {e}.

A biquadratic final polynomial for delta is a list of weighted strict
inequalities, each naming a three-term Grassmann-Plucker relation
(L; a,b,c,d) of delta, which of its three terms is the BIG one, and a
positive weight, such that the weighted sum of the vectors

    v = e_p + e_q - e_s - e_t   in Z^{C(8,4)}

vanishes.  Apply phi^{-1} to L and to (a,b,c,d).  Because phi^{-1} is
strictly increasing:

  * (phi^{-1}L; phi^{-1}a < phi^{-1}b < phi^{-1}c < phi^{-1}d) is a genuine
    three-term GP relation of chi, in the same normal form;
  * each of its three signed terms equals the corresponding signed term of
    the delta-relation, because the two brackets are equal by the definition
    of deletion and the two tuple-sorting signs are unchanged (an increasing
    map does not create inversions).  Hence the SAME term is the odd one
    out, so "big" and "small" carry over verbatim;
  * the induced map on bases, B -> phi^{-1}B, is injective from the C(8,4)
    bases of delta into the C(9,4) bases of chi, so the weighted
    combination still cancels -- coordinate by coordinate, in the image.

So the lift is a pure relabelling of the term indices.  No group element, no
LP, no arithmetic.  The lifted certificate is written in the schema
`ai/omreal/checkcert.py` accepts and is meant to be checked with it: that is
the proof that the lift is right, not this docstring.
"""

import argparse
import json
import os
import random
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import minorlib as ml                                       # noqa: E402
sys.path.insert(0, ml.OMREAL)

OUT = os.path.join(HERE, 'data')


def phi_inv(e):
    """{1..8} -> {1..9} \\ {e}, order preserving."""
    return lambda x: x if x < e else x + 1


def bfp_terms(chi8, gp):
    """Run the BFP search on an 8-element chirotope; return checkcert terms."""
    import bfp as bfpmod
    cert, info = bfpmod.find_bfp(chi8, gp)
    if cert is None:
        return None, info
    terms = []
    for (ri, big, small, w) in cert['terms']:
        L, abcd, _ = gp.rel[ri]
        terms.append({'L': list(L), 'abcd': list(abcd),
                      'big': int(big), 'small': int(small), 'w': int(w)})
    return terms, info


def lift(terms, e):
    """Relabel an 8-element certificate onto {1..9} \\ {e}."""
    f = phi_inv(e)
    out = []
    for t in terms:
        out.append({'L': [f(x) for x in t['L']],
                    'abcd': [f(x) for x in t['abcd']],
                    'big': t['big'], 'small': t['small'], 'w': t['w']})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--minors', default=os.path.join(OUT, 'minors_sweep.jsonl'))
    ap.add_argument('--sample', type=int, default=40)
    ap.add_argument('--seed', type=int, default=20260801)
    ap.add_argument('--canary', action='store_true')
    ap.add_argument('--out', default=os.path.join(OUT, 'lifted_certs.jsonl'))
    a = ap.parse_args()

    import bfp as bfpmod
    import time

    gp8 = bfpmod.GPSystem(8, 4)
    gp9 = bfpmod.GPSystem(9, 4)
    M = ml.Minors(9, 4)

    rows = []
    for line in open(a.minors):
        r = json.loads(line)
        if r['verdict'] == 'NON_REALIZABLE' and r['del_nonreal']:
            rows.append(r)
    print('%d classes with a non-realizable deletion available' % len(rows))
    rng = random.Random(a.seed)
    pick = rng.sample(rows, min(a.sample, len(rows)))

    t8 = t9 = 0.0
    n8 = n9 = 0
    nlift = 0
    with open(a.out, 'w') as fh:
        for r in pick:
            chi9 = ml.signs_from_string(r['chi'])
            S = ml.bits_from_string(r['chi'])[None, :]
            D = M.deletions_bits(S)[0]
            e = r['del_nonreal'][0]
            chi8 = np.where(D[e - 1] == 1, np.int8(1), np.int8(-1))
            t0 = time.time()
            terms, _ = bfp_terms(chi8, gp8)
            t8 += time.time() - t0
            n8 += 1
            if terms is None:
                raise SystemExit('a deletion identified as one of the 24 has '
                                 'no BFP: %s / e=%d' % (r['chi'], e))
            # the 8-element certificate must itself check out
            fh.write(json.dumps({'n': 8, 'r': 4,
                                 'chi': ml.string_from_signs(chi8),
                                 'verdict': 'NON_REALIZABLE',
                                 'bfp': terms}) + '\n')
            lt = lift(terms, e)
            fh.write(json.dumps({'n': 9, 'r': 4, 'chi': r['chi'],
                                 'verdict': 'NON_REALIZABLE', 'bfp': lt,
                                 'lifted_from_deletion': e}) + '\n')
            nlift += 1
            # cost of the direct 9-element BFP, for the payoff arithmetic
            t0 = time.time()
            c9, _ = bfpmod.find_bfp(chi9, gp9)
            t9 += time.time() - t0
            n9 += 1
    print('wrote %d lifted certificates (+ their 8-element originals) -> %s'
          % (nlift, a.out))
    print('mean (8,4) BFP: %.1f ms   mean (9,4) BFP: %.1f ms   ratio %.1fx'
          % (1000 * t8 / max(n8, 1), 1000 * t9 / max(n9, 1),
             (t9 / max(n9, 1)) / max(t8 / max(n8, 1), 1e-9)))

    if a.canary:
        cpath = os.path.join(OUT, 'lifted_canaries.jsonl')
        with open(cpath, 'w') as fh:
            r = pick[0]
            chi9 = r['chi']
            S = ml.bits_from_string(chi9)[None, :]
            D = M.deletions_bits(S)[0]
            e = r['del_nonreal'][0]
            chi8 = np.where(D[e - 1] == 1, np.int8(1), np.int8(-1))
            terms, _ = bfp_terms(chi8, gp8)
            good = lift(terms, e)
            # C1: lifted with the WRONG deleted element
            wrong = [x for x in range(1, 10) if x != e][0]
            fh.write(json.dumps({'n': 9, 'r': 4, 'chi': chi9,
                                 'verdict': 'NON_REALIZABLE',
                                 'bfp': lift(terms, wrong),
                                 'canary': 'lifted with the wrong element'}) + '\n')
            # C2: one weight corrupted
            bad = json.loads(json.dumps(good))
            bad[0]['w'] += 1
            fh.write(json.dumps({'n': 9, 'r': 4, 'chi': chi9,
                                 'verdict': 'NON_REALIZABLE', 'bfp': bad,
                                 'canary': 'one weight corrupted'}) + '\n')
            # C3: big/small swapped on one term
            bad = json.loads(json.dumps(good))
            bad[0]['big'], bad[0]['small'] = bad[0]['small'], bad[0]['big']
            fh.write(json.dumps({'n': 9, 'r': 4, 'chi': chi9,
                                 'verdict': 'NON_REALIZABLE', 'bfp': bad,
                                 'canary': 'big and small swapped'}) + '\n')
            # C4: a term dropped
            bad = json.loads(json.dumps(good))[1:]
            fh.write(json.dumps({'n': 9, 'r': 4, 'chi': chi9,
                                 'verdict': 'NON_REALIZABLE', 'bfp': bad,
                                 'canary': 'a term dropped'}) + '\n')
            # C5: the certificate attached to a DIFFERENT 9-element class
            other = [q for q in rows if q['chi'] != chi9][0]['chi']
            fh.write(json.dumps({'n': 9, 'r': 4, 'chi': other,
                                 'verdict': 'NON_REALIZABLE', 'bfp': good,
                                 'canary': 'attached to another class'}) + '\n')
        print('canaries -> %s  (checkcert must REJECT all 5)' % cpath)


if __name__ == '__main__':
    main()
