"""Retrieve three existing strict witnesses; produce exact comparison duals.

Binary search uses the historical extension ordering only to find candidates.
The returned candidate's actual determinant signs are checked for equality;
the independent verifier never trusts that ordering or the search algorithm.
No shared-pencil predicate is tested on an additional chart.
"""
import sys
sys.dont_write_bytecode = True
import numpy as np
import search_shared_pencil as search


def main():
    upper = np.load(search.ROOT / 'ai/omreal/data/seeat_parent2599_upper178.npz', allow_pickle=False)
    targets = [14988895318912, 3405195891438080, 40418075143643136]
    cached_rows = {}

    def lookup(index):
        chart = int(upper['assignment'][index])
        parent = upper['chart_matrix'][chart].tolist()
        if chart not in cached_rows:
            cached_rows[chart] = search.topes.derived_rows(parent)
        point = list(map(int, upper['point'][index]))
        rows = cached_rows[chart]
        products = [search.topes.dot(row, point) for row in rows]
        assert all(products)
        signature = sum((value > 0) << j for j, value in enumerate(products))
        return signature, chart, parent, point, rows

    def key(signature):
        return int(f'{signature:056b}'[::-1], 2)

    records = []
    for target in targets:
        left, right = 0, len(upper['assignment'])
        while left < right:
            middle = (left + right) // 2
            actual, *_ = lookup(middle)
            if key(actual) < key(target):
                left = middle + 1
            else:
                right = middle
        actual, chart, parent, point, rows = lookup(left)
        assert actual == target
        systems = []
        for signature in targets:
            primal = []
            dual = search.positive_kernel(rows, signature, primal_output=primal)
            systems.append({'signature': signature, 'dual': dual, 'primal': primal})
        assert [system['dual'] is None for system in systems] == [signature == target for signature in targets]
        records.append({'signature': target, 'upper_point_index': left, 'upper_chart_index': chart,
                        'parent': parent, 'point': point, 'other_systems': systems})
        print(target, 'stored point', left, 'chart', chart, 'strictly feasible here; other two bad')
    search.save({'records': records}, 'admissibility_flow.json')


if __name__ == '__main__':
    main()
