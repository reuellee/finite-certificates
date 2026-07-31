import json
import gzip
import numpy as np

def verify():
    # 1. verify the primal witness for 516678
    with gzip.open('stage2b_gpt/symmetric_coverage.json.gz', 'rt') as f:
        sym_cov = json.load(f)
    print("sym_cov keys:", sym_cov.keys())
    # we don't have primal witnesses here! wait. "exact strict primal witnesses in symmetric_coverage.json.gz"
    # let's look at the schema or print the first few items.
    
    # 2. Re-verify the cert via check_cellwide.py
    # I'll call check_cellwide.py from bash, but I can also do it in python if I import it.

if __name__ == '__main__':
    verify()
