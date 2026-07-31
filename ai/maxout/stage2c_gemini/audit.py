import gzip
import json
import os
import sys

def main():
    with gzip.open('stage2b_gpt/symmetric_coverage.json.gz', 'rt') as f:
        sym_cov = json.load(f)
    print("symmetric_coverage.json.gz keys:", sym_cov.keys())
    
    bits1 = sym_cov.get('classes_not_covered_for_both_splits_bits', [])
    bits2 = sym_cov.get('classes_covered_for_neither_split_bits', [])
    print(f"len(classes_not_covered_for_both_splits_bits): {len(bits1)}")
    print(f"len(classes_covered_for_neither_split_bits): {len(bits2)}")
    if bits1: print("Sample bits1:", bits1[:5])
    if bits2: print("Sample bits2:", bits2[:5])
    
    with open('stage2b_gpt/reference_structure.json', 'r') as f:
        ref_struct = json.load(f)
        
    print("reference_structure k conventions:", ref_struct.get('k_values', 'Not found'))
    
if __name__ == '__main__':
    main()
