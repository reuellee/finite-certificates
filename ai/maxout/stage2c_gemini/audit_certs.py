import json
import gzip

def audit():
    with gzip.open('stage2b_gpt/symmetric_coverage.json.gz', 'rt') as f:
        sym_cov = json.load(f)
    
    bits_not_both = set(sym_cov['classes_not_covered_for_both_splits_bits'])
    bits_neither = set(sym_cov['classes_covered_for_neither_split_bits'])
    
    with open('stage2c_gemini/symbolic_certs.json', 'r') as f:
        certs = json.load(f)
        
    seen = set()
    for cert in certs:
        bits = cert['sigma_bits']
        k = cert['k']
        idx = cert['idx']
        
        if (bits, k) in seen: continue
        seen.add((bits,k))
        
        in_not_both = bits in bits_not_both
        in_neither = bits in bits_neither
        status = "neither"
        if in_neither:
            status = "both splits"
        elif in_not_both:
            status = "one split"
            
        print(f"Target idx {idx}, bits {bits}, k {k}, residue status: {status}")

if __name__ == '__main__':
    audit()
