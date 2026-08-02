#!/usr/bin/env python3
"""Exact regression check for mutation-inherited deletion certificates.

For a mutation at basis B and an element e in B, deletion of e removes the
only changed chirotope coordinate.  If that deletion is non-realizable, the
same deletion certificate proves both endpoints non-realizable.

This script checks the statement on every valid mutation of the 40 pinned
rank-(4,9) lifted certificates in data/lifted_certs.jsonl.  Mutation
enumeration uses ai/omgamma/core.py; certificate verification uses the
independent standard-library checker ai/omreal/checkcert.py.
"""

import argparse
import json
import os
import sys


HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO, 'ai', 'omgamma'))
import core                                                    # noqa: E402
sys.path.insert(0, os.path.join(REPO, 'ai', 'omreal'))
import checkcert                                                # noqa: E402


PINNED = {
    'records': 40,
    'protected_edges': 271,
    'protected_accepted': 271,
    'control_accepted': 35,
    'control_rejected': 298,
    'protected_min': 4,
    'protected_max': 10,
}


def deletion_string(chi, bases, e):
    """Restriction of a colex sign string to bases avoiding e."""
    return ''.join(sign for sign, basis in zip(chi, bases) if e not in basis)


def flip(chi, j):
    replacement = '-' if chi[j] == '+' else '+'
    return chi[:j] + replacement + chi[j + 1:]


def load_records(path):
    records = []
    with open(path) as fh:
        for line_number, line in enumerate(fh, 1):
            if not line.strip():
                continue
            record = json.loads(line)
            if int(record['n']) == 9:
                if int(record['r']) != 4:
                    raise AssertionError('line %d is n=9 but not rank 4'
                                         % line_number)
                if 'lifted_from_deletion' not in record:
                    raise AssertionError('line %d has no deletion witness'
                                         % line_number)
                records.append(record)
    return records


def check(path):
    records = load_records(path)
    bases = core.bases_colex(9, 4)
    protected_edges = 0
    protected_accepted = 0
    control_accepted = 0
    control_rejected = 0
    protected_per_record = []

    for record_number, record in enumerate(records, 1):
        e = int(record['lifted_from_deletion'])
        chi = record['chi']
        bit_chi = core.from_string(9, 4, chi)

        if not core.is_uniform_chirotope(9, 4, bit_chi):
            raise AssertionError('record %d is not a chirotope'
                                 % record_number)
        ok, message = checkcert.check_record(record)
        if not ok:
            raise AssertionError('record %d original certificate: %s'
                                 % (record_number, message))

        # A certificate lifted from deletion e must mention only elements
        # surviving that deletion.  This makes the unchanged-certificate
        # check below transparent rather than merely empirical.
        for term_number, term in enumerate(record['bfp'], 1):
            support = set(term['L']) | set(term['abcd'])
            if e in support:
                raise AssertionError(
                    'record %d term %d contains deleted element %d'
                    % (record_number, term_number, e))

        before_deletion = deletion_string(chi, bases, e)
        protected_here = 0
        for j in core.mutable_bases(9, 4, bit_chi):
            mutated_chi = flip(chi, j)
            mutated = dict(record)
            mutated['chi'] = mutated_chi
            accepted, reason = checkcert.check_record(mutated)

            if e in bases[j]:
                protected_edges += 1
                protected_here += 1
                after_deletion = deletion_string(mutated_chi, bases, e)
                if after_deletion != before_deletion:
                    raise AssertionError(
                        'record %d mutation %s changed deletion %d'
                        % (record_number, bases[j], e))
                if not accepted:
                    raise AssertionError(
                        'record %d protected mutation %s rejected: %s'
                        % (record_number, bases[j], reason))
                protected_accepted += 1
            elif accepted:
                control_accepted += 1
            else:
                control_rejected += 1
        protected_per_record.append(protected_here)

    observed = {
        'records': len(records),
        'protected_edges': protected_edges,
        'protected_accepted': protected_accepted,
        'control_accepted': control_accepted,
        'control_rejected': control_rejected,
        'protected_min': min(protected_per_record),
        'protected_max': max(protected_per_record),
    }
    if observed != PINNED:
        raise AssertionError('pinned-corpus totals changed:\nexpected %r\nobserved %r'
                             % (PINNED, observed))

    mean = protected_edges / float(len(records))
    print('records: %d' % len(records))
    print('theorem-covered mutations: %d/%d accepted'
          % (protected_accepted, protected_edges))
    print('covered mutations per record: min %d, mean %.3f, max %d'
          % (min(protected_per_record), mean, max(protected_per_record)))
    print('control mutations outside theorem: %d accepted, %d rejected'
          % (control_accepted, control_rejected))
    print('PASS: every mutation basis containing the witness element '
          'preserved the deletion certificate')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '--certs',
        default=os.path.join(HERE, 'data', 'lifted_certs.jsonl'),
        help='lifted certificate JSONL (default: %(default)s)')
    args = parser.parse_args()
    check(args.certs)


if __name__ == '__main__':
    main()
