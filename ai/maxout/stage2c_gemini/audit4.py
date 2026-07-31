import json
import gzip

def get_witness():
    with gzip.open('stage2b_gpt/symmetric_coverage.json.gz', 'rt') as f:
        sym_cov = json.load(f)
    print("sym_cov keys:", sym_cov.keys())
    # Is there a list of witnesses? 
    # STAGE2B.md says: "Every residue pattern also carries an exact rational strict-primal witness for the restricted system"
    # But where is it? 
    if 'residues_k1' in sym_cov:
        # Let's just print keys again to be sure
        pass

    for k in sym_cov.keys():
        if isinstance(sym_cov[k], dict):
            print(f"Key {k} is a dict with keys:", list(sym_cov[k].keys())[:10])
        elif isinstance(sym_cov[k], list):
            print(f"Key {k} is a list of length", len(sym_cov[k]))
            if len(sym_cov[k]) > 0 and isinstance(sym_cov[k][0], dict):
                print(f"First item of {k} has keys:", list(sym_cov[k][0].keys()))

if __name__ == '__main__':
    get_witness()
