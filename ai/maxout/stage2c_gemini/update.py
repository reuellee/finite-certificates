import json

def update_artifacts():
    with open('stage2c_gemini/symbolic_certs.json', 'r') as f:
        certs = json.load(f)
        
    # Deduplicate and downgrade
    dedup = {}
    for c in certs:
        key = (c['idx'], c['k'])
        if key not in dedup:
            c['status'] = 'equality_failed_due_to_sign_bug'
            dedup[key] = c
            
    generic_cert = {
        "idx": "GENERIC_SINGLE_CLASS",
        "sigma_bits": "ANY",
        "k": "ANY",
        "status": "proven_generic",
        "criterion": "sigma_{ij,+} = sigma_{ij,-} and sigma_{ij}*s_t = -1 for all 3 t not in {i,j}",
        "support": [
            "(i,j,+)",
            "(i,j,-)",
            "w_t1",
            "w_t2",
            "w_t3"
        ],
        "multipliers": {
            "(i,j,+)": "D_t1_t2_t3",
            "(i,j,-)": "D_t1_t2_t3",
            "w_t1": "D_t1_t2_t3 * D_t1_i_j",
            "w_t2": "D_t1_t2_t3 * D_t2_i_j",
            "w_t3": "D_t1_t2_t3 * D_t3_i_j"
        }
    }
    
    final_certs = list(dedup.values()) + [generic_cert]
    
    with open('stage2c_gemini/symbolic_certs.json', 'w') as f:
        json.dump(final_certs, f, indent=2)
        
    with open('stage2c_gemini/call2_outcomes.json', 'r') as f:
        outcomes = json.load(f)
        
    for k, v in outcomes.items():
        if v['status'] == 'proven_cellwide':
            v['status'] = 'equality_failed_due_to_sign_bug'
    
    if "60552" in outcomes:
        outcomes["60552"]["status"] = "not_found_at_degree_2"
            
    with open('stage2c_gemini/call2_outcomes.json', 'w') as f:
        json.dump(outcomes, f, indent=2)

if __name__ == '__main__':
    update_artifacts()
