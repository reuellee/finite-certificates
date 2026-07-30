import json
import sys
import itertools
from fractions import Fraction
import sympy
import random
import scipy.optimize as opt
from collections import defaultdict

# ---------------------------------------------------------------------------
# GP Ideal Setup
# ---------------------------------------------------------------------------
TRIPLES = list(itertools.combinations(range(5), 3))
p_vars = sympy.symbols(['p' + ''.join(map(str, t)) for t in TRIPLES])
p_dict = {t: v for t, v in zip(TRIPLES, p_vars)}

def p_var(a, b, c):
    """Return signed Pluecker variable."""
    t = tuple(sorted((a, b, c)))
    if len(set(t)) < 3:
        return sympy.Integer(0)
    seq = [a, b, c]
    inv = sum(1 for i in range(3) for j in range(i+1, 3) if seq[i] > seq[j])
    sign = -1 if inv % 2 else 1
    return sign * p_dict[t]

def generate_gp_relations():
    rels = []
    for a in range(5):
        others = [x for x in range(5) if x != a]
        i1, i2, i3, i4 = others
        rel = p_var(a, i1, i2) * p_var(a, i3, i4) - p_var(a, i1, i3) * p_var(a, i2, i4) + p_var(a, i1, i4) * p_var(a, i2, i3)
        rels.append(rel)
    return rels

GP_IDEAL = generate_gp_relations()
GP_GB = sympy.groebner(GP_IDEAL, p_vars, order='grevlex')

def check_ideal_membership(poly):
    if poly == 0:
        return True
    _, reduced_poly = sympy.reduced(poly, GP_GB, p_vars, order='grevlex')
    return sympy.expand(reduced_poly) == 0

# ---------------------------------------------------------------------------
# Configuration Setup
# ---------------------------------------------------------------------------
U_ints = [
    [-34, 43, 6],
    [-2, -31, -19],
    [-4, 43, 8],
    [5, -20, 2],
    [10, -6, 21]
]

def det3(a, b, c):
    return (
        a[0] * (b[1] * c[2] - b[2] * c[1]) -
        a[1] * (b[0] * c[2] - b[2] * c[0]) +
        a[2] * (b[0] * c[1] - b[1] * c[0])
    )

def sign_val(val):
    return 1 if val > 0 else (-1 if val < 0 else 0)

chi_dict = {}
for i, j, k in TRIPLES:
    val = det3(U_ints[i], U_ints[j], U_ints[k])
    chi_dict[(i, j, k)] = sign_val(val)

D_syms = sympy.symbols(['D' + ''.join(map(str, t)) for t in TRIPLES])
D_sym_dict = {str(d): d for d in D_syms}

def generate_gp_relations_D():
    rels = generate_gp_relations()
    D_rels = []
    for rel in rels:
        sub_dict = {}
        for t in TRIPLES:
            sub_dict[p_dict[t]] = chi_dict[t] * D_sym_dict[f"D{t[0]}{t[1]}{t[2]}"]
        D_rels.append(rel.subs(sub_dict))
    return D_rels

GP_D = generate_gp_relations_D()

# ---------------------------------------------------------------------------
# Polynomial Parsing & Positivity
# ---------------------------------------------------------------------------
def D_to_p(expr):
    sub_dict = {}
    for i, j, k in TRIPLES:
        d_name = f"D{i}{j}{k}"
        sub_dict[D_sym_dict[d_name]] = chi_dict[(i, j, k)] * p_dict[(i, j, k)]
    return expr.subs(sub_dict)

def total_degree(p):
    if p.is_constant():
        return 0
    return max([sum(monom) for monom in sympy.Poly(p, D_syms).monoms()] + [0])

def is_manifestly_positive(poly):
    poly_dict = poly.as_coefficients_dict()
    for coeff in poly_dict.values():
        if coeff < 0:
            return False
    return True

def try_rewrite_positive(poly, max_deg=3):
    p_deg = total_degree(poly)
    candidates = []
    for gp in GP_D:
        gp_deg = total_degree(gp)
        if gp_deg > p_deg:
            continue
        diff = p_deg - gp_deg
        if diff == 0:
            candidates.append(gp)
        else:
            for monom in itertools.combinations_with_replacement(D_syms, diff):
                m = sympy.prod(monom)
                candidates.append(m * gp)
                
    if not candidates:
        return False
        
    all_exprs = [poly] + candidates
    all_monoms = set()
    for expr in all_exprs:
        all_monoms.update(expr.as_coefficients_dict().keys())
        
    monom_list = list(all_monoms)
    A = []
    b = []
    for monom in monom_list:
        row = []
        for cand in candidates:
            row.append(float(cand.as_coefficients_dict().get(monom, 0)))
        A.append([-x for x in row])
        b.append(-float(poly.as_coefficients_dict().get(monom, 0)))
        
    res = opt.linprog(c=[0]*len(candidates), A_ub=A, b_ub=b, bounds=(None, None))
    return res.success

def generate_probes(num_probes=100, seed=42):
    rng = random.Random(seed)
    probes = [U_ints]
    for _ in range(num_probes // 2):
        scale_idx = rng.randint(0, 4)
        scale_val = Fraction(rng.randint(1, 100), rng.randint(1, 100))
        U_new = [list(u) for u in U_ints]
        U_new[scale_idx] = [x * scale_val for x in U_new[scale_idx]]
        probes.append(U_new)
        
    for _ in range(num_probes // 2):
        U_new = [list(u) for u in U_ints]
        row = rng.randint(0, 4)
        col = rng.randint(0, 2)
        U_new[row][col] += Fraction(rng.choice([-1, 1]), rng.randint(1, 10))
        valid = True
        for i, j, k in TRIPLES:
            if sign_val(det3(U_new[i], U_new[j], U_new[k])) != chi_dict[(i, j, k)]:
                valid = False
                break
        if valid:
            probes.append(U_new)
    return probes

PROBES = generate_probes()

def check_cellwide_eval(poly, probe_U):
    D_vals = {}
    for i, j, k in TRIPLES:
        val = abs(det3(probe_U[i], probe_U[j], probe_U[k]))
        D_vals[D_sym_dict[f"D{i}{j}{k}"]] = val
    return poly.subs(D_vals)

def classify_positivity(poly):
    if is_manifestly_positive(poly):
        return "PROVEN POSITIVE"
    if try_rewrite_positive(poly):
        return "PROVEN POSITIVE"
    
    for probe in PROBES:
        val = check_cellwide_eval(poly, probe)
        if val < 0:
            return "NOT CELL-WIDE (counterexample found)"
            
    return "UNDECIDED"

# ---------------------------------------------------------------------------
# Verifier
# ---------------------------------------------------------------------------
def verify_certificate(sigma_bits, k, support, cleared_hypotheses):
    split = [1]*k + [-1]*(5-k)
    T_eqs = [sympy.Integer(0)] * 5
    W_eqs = [sympy.Integer(0)] * 5
    PAIRS = list(itertools.combinations(range(5), 2))
    
    for s in support:
        poly_D = cleared_hypotheses[s]
        y_s = D_to_p(poly_D)
        if s.startswith('w_'):
            t = int(s[2:])
            W_eqs[t] += y_s
        else:
            i, j, sign_str = s.strip('()').split(',')
            i, j = int(i), int(j)
            pair_idx = PAIRS.index((i, j))
            
            is_plus = (sign_str == '+')
            side = 2 * pair_idx if is_plus else 2 * pair_idx + 1
            ray_orientation = 1 if is_plus else -1
            sigma_s = 1 if (sigma_bits & (1 << side)) else -1
            
            normal_scalar = sigma_s * ray_orientation
            
            for t in range(5):
                T_eqs[t] += y_s * normal_scalar * p_var(t, i, j)
                tup = tuple(sorted((t,i,j)))
                D_tij = chi_dict[tup] * p_dict[tup] if t not in (i,j) else sympy.Integer(0)
                W_eqs[t] += y_s * (sigma_s * split[t]) * D_tij

    t_pass = True
    for t in range(5):
        if not check_ideal_membership(T_eqs[t]):
            print(f"    T_eqs[{t}] failed: {sympy.reduced(T_eqs[t], GP_GB, p_vars, order='grevlex')[1]}")
            t_pass = False

    w_pass = True
    for t in range(5):
        if not check_ideal_membership(W_eqs[t]):
            print(f"    W_eqs[{t}] failed: {sympy.reduced(W_eqs[t], GP_GB, p_vars, order='grevlex')[1]}")
            w_pass = False
    
    pos_classes = {}
    for s in support:
        pos_classes[s] = classify_positivity(cleared_hypotheses[s])
        
    return t_pass, w_pass, pos_classes

def test_stage2a_5cycle():
    print("Running Self-Tests...")
    
    # 5-cycle identity from STAGE2A.md:
    # y_24 = c2, y_03 = c4, y_02 = c1, y_13 = c3
    # c1 = D013 D234, c2 = D013 D023, c3 = D024 D023, c4 = D024 D123
    
    sigma_bits = (1 << 16) | (1 << 17) | (1 << 4) | (1 << 5)
    k = 3
    support = ["(0,2,+)", "(0,2,-)", "(2,4,+)", "(2,4,-)", "(1,3,+)", "(1,3,-)", "(0,3,+)", "(0,3,-)"]
    hypotheses = {
        "(0,2,+)": D_sym_dict["D013"] * D_sym_dict["D234"],
        "(0,2,-)": D_sym_dict["D013"] * D_sym_dict["D234"],
        "(2,4,+)": D_sym_dict["D013"] * D_sym_dict["D023"],
        "(2,4,-)": D_sym_dict["D013"] * D_sym_dict["D023"],
        "(1,3,+)": D_sym_dict["D024"] * D_sym_dict["D023"],
        "(1,3,-)": D_sym_dict["D024"] * D_sym_dict["D023"],
        "(0,3,+)": D_sym_dict["D024"] * D_sym_dict["D123"],
        "(0,3,-)": D_sym_dict["D024"] * D_sym_dict["D123"]
    }
    
    t_pass, w_pass, pos_classes = verify_certificate(sigma_bits, k, support, hypotheses)
    
    print(f"(POS) 5-cycle exact identity:")
    print(f"  T equality: {'PASS' if t_pass else 'FAIL'}")
    print(f"  Positivity classes: {pos_classes}")
    
    if not t_pass:
        print("ERROR: POS test failed on T equality!")
        return False
        
    # NEG: deliberate corruption
    corrupt_hypo = dict(hypotheses)
    corrupt_hypo["(0,2,+)"] = D_sym_dict["D013"] * D_sym_dict["D234"] + 1
    
    t_pass, w_pass, pos_classes = verify_certificate(sigma_bits, k, support, corrupt_hypo)
    print(f"(NEG) Corrupted 5-cycle identity:")
    print(f"  T equality: {'PASS' if t_pass else 'FAIL'}")
    
    if t_pass:
        print("ERROR: NEG test failed (it passed equality)!")
        return False
        
    print("Self-Tests PASSED.")
    return True

def solve_undetermined_coefficients(sigma_bits, k, support, degree):
    monoms = []
    if degree == 1:
        monoms = list(D_syms)
    elif degree == 2:
        monoms = [D_syms[i]*D_syms[j] for i in range(10) for j in range(i, 10)]
    elif degree == 3:
        monoms = [D_syms[i]*D_syms[j]*D_syms[k] for i in range(10) for j in range(i, 10) for k in range(j, 10)]
    else:
        return None
        
    side_support = [s for s in support if not s.startswith('w_')]
    
    num_monoms = len(monoms)
    num_rows = len(side_support)
    total_vars = num_monoms * num_rows
    
    coeffs = sympy.symbols(f'c0:{total_vars}')
    hypotheses = {}
    
    var_idx = 0
    for s in side_support:
        poly = sympy.Integer(0)
        for m in monoms:
            poly += coeffs[var_idx] * m
            var_idx += 1
        hypotheses[s] = poly
        
    split = [1]*k + [-1]*(5-k)
    T_eqs = [sympy.Integer(0)] * 5
    mu_D = [sympy.Integer(0)] * 5
    PAIRS = list(itertools.combinations(range(5), 2))
    
    for s in side_support:
        poly_D = hypotheses[s]
        y_s = D_to_p(poly_D)
        
        i, j, sign_str = s.strip('()').split(',')
        i, j = int(i), int(j)
        pair_idx = PAIRS.index((i, j))
        
        is_plus = (sign_str == '+')
        side = 2 * pair_idx if is_plus else 2 * pair_idx + 1
        ray_orientation = 1 if is_plus else -1
        sigma_s = 1 if (sigma_bits & (1 << side)) else -1
        
        normal_scalar = sigma_s * ray_orientation
        
        for t in range(5):
            T_eqs[t] += y_s * normal_scalar * p_var(t, i, j)
            tup = tuple(sorted((t,i,j)))
            if t not in (i,j):
                D_sym = D_sym_dict[f"D{tup[0]}{tup[1]}{tup[2]}"]
                mu_D[t] += poly_D * (sigma_s * split[t]) * D_sym
                
    eqs_to_solve = []
    for eq in T_eqs:
        if eq == 0: continue
        _, reduced_eq = sympy.reduced(eq, GP_GB, p_vars, order='grevlex')
        poly = sympy.Poly(reduced_eq, p_vars)
        for coef_expr in poly.coeffs():
            if coef_expr != 0:
                eqs_to_solve.append(coef_expr)
                
    if not eqs_to_solve:
        print("      eqs_to_solve is empty!")
        return None
        
    print(f"      Solving {len(eqs_to_solve)} linear equations in {len(coeffs)} variables...")
    sol = sympy.linsolve(eqs_to_solve, coeffs)
    if not sol:
        print("      linsolve returned empty! (No solution in ideal)")
        return None
        
    sol = list(sol)[0]
    sol_dict = {c: val for c, val in zip(coeffs, sol)}
    
    free_symbols = set()
    for c in coeffs:
        free_symbols.update(sol_dict[c].free_symbols)
            
    free_vars = list(free_symbols)
    print(f"      Nullspace dimension: {len(free_vars)}")
    
    all_coeffs_to_check_dicts = []
    for c in coeffs:
        d = {}
        for k, v in sol_dict[c].as_coefficients_dict().items():
            d[k] = Fraction(v)
        all_coeffs_to_check_dicts.append(d)
        
    for t in range(5):
        poly = sympy.Poly(mu_D[t], D_syms)
        for coef_expr in poly.coeffs():
            if coef_expr != 0:
                d = defaultdict(Fraction)
                for k, v in coef_expr.as_coefficients_dict().items():
                    if k in sol_dict:
                        for fv, fv_v in sol_dict[k].as_coefficients_dict().items():
                            d[fv] += Fraction(v) * Fraction(fv_v)
                    else:
                        d[k] += Fraction(v)
                all_coeffs_to_check_dicts.append(d)
    
    if not free_vars:
        if all(d.get(1, 0) >= 0 for d in all_coeffs_to_check_dicts) and any(d.get(1, 0) > 0 for d in all_coeffs_to_check_dicts):
            sub_dict = {}
        else:
            print("      Unique solution is not strictly positive.")
            return None
    else:
        A_ub = []
        b_ub = []
        
        for d in all_coeffs_to_check_dicts:
            row = []
            for fv in free_vars:
                row.append(-float(d.get(fv, 0)))
            A_ub.append(row)
            b_ub.append(0.0)
            
        c_obj = [0] * len(free_vars)
        for d in all_coeffs_to_check_dicts:
            for i, fv in enumerate(free_vars):
                c_obj[i] -= float(d.get(fv, 0))
        A_ub.append(c_obj)
        b_ub.append(-1.0)
        
        res = opt.linprog(c=[0]*len(free_vars), A_ub=A_ub, b_ub=b_ub, bounds=(None, None), method='highs')
        if not res.success:
            print("      LP failed to find a positive vector in the nullspace.")
            return None
            
        sub_dict = {}
        for fv, val in zip(free_vars, res.x):
            sub_dict[fv] = Fraction(val).limit_denominator(100000)
            
    sol_numeric = {}
    for c in coeffs:
        val = Fraction(0)
        for fv, coef in sol_dict[c].as_coefficients_dict().items():
            if fv == 1:
                val += Fraction(coef)
            elif fv in sub_dict:
                val += Fraction(coef) * sub_dict[fv]
        sol_numeric[c] = val
        
    final_hypotheses = {}
    is_non_zero = False
    
    for s in side_support:
        poly_sub = hypotheses[s].subs(sol_numeric)
        if poly_sub != 0:
            is_non_zero = True
            final_hypotheses[s] = poly_sub
            
    for t in range(5):
        poly_sub = mu_D[t].subs(sol_numeric)
        if poly_sub != 0:
            final_hypotheses[f"w_{t}"] = poly_sub
        
    if not is_non_zero:
        print("      All hypotheses evaluated to 0!")
        return None
        
    denoms = []
    for p in final_hypotheses.values():
        for c in p.as_coefficients_dict().values():
            if isinstance(c, Fraction):
                denoms.append(c.denominator)
            elif isinstance(c, sympy.Rational):
                denoms.append(c.q)
    
    lcm = 1
    for d in denoms:
        import math
        lcm = abs(lcm * d) // math.gcd(lcm, d)
        
    for k in final_hypotheses:
        final_hypotheses[k] = sympy.expand(final_hypotheses[k] * lcm)
        
    return final_hypotheses

def process_target(target, catalogue):
    print(f"\nProcessing target: sigma={target['sigma']}, k={target['k']}, idx={target['idx']}")
    # Match support
    cert = target['cert']
    support_indices = [row[0] for row in cert]
    PAIRS = list(itertools.combinations(range(5), 2))
    
    def idx_to_str(idx):
        if idx >= 20:
            return f"w_{idx - 20}"
        else:
            c = idx // 2
            is_plus = (idx % 2 == 0)
            return f"({PAIRS[c][0]},{PAIRS[c][1]},{'+' if is_plus else '-'})"
            
    support_strs = [idx_to_str(idx) for idx in support_indices]
    
    ansatz = None
    for a in catalogue:
        if set(a["support"]) == set(support_strs):
            ansatz = a
            break
            
    if not ansatz:
        print("  No matching ansatz found. Trying undetermined coefficients directly...")
        hypotheses = None
        
        all_sides = []
        for pair_idx, (i, j) in enumerate(PAIRS):
            all_sides.append(f"({i},{j},+)")
            all_sides.append(f"({i},{j},-)")
            
        for deg in [1, 2]:
            print(f"    Trying degree {deg} with full 20-side support...")
            hyp = solve_undetermined_coefficients(target["sigma"], target["k"], all_sides, deg)
            if hyp:
                t_pass, w_pass, pos_classes = verify_certificate(target["sigma"], target["k"], list(hyp.keys()), hyp)
                if t_pass and w_pass:
                    print(f"    Success at degree {deg}!")
                    hypotheses = hyp
                    break
                    
        if hypotheses is None:
            return "not_attempted", None, None
            
        pos_classes = {}
        for s in hypotheses:
            pos_classes[s] = classify_positivity(hypotheses[s])
            
        print(f"  Equality PASSED. Positivity: {pos_classes}")
        
        if all(c == "PROVEN POSITIVE" for c in pos_classes.values()):
            status = "proven_cellwide"
        elif any("NOT CELL-WIDE" in c for c in pos_classes.values()):
            status = "subcell_only"
        else:
            status = "equality_ok_positivity_undecided"
            
        return status, pos_classes, hypotheses
        
    print(f"  Matched ansatz: {ansatz['id']}")
    
    # Try exact match first
    hypotheses = None
    if "NO SIMPLE MATCH (degree 3+ polynomial)" not in ansatz["coefficient_hypotheses"].values():
        from sympy.parsing.sympy_parser import parse_expr
        
        # parse and clear
        exprs = {}
        denoms = []
        for k_s, v in ansatz["coefficient_hypotheses"].items():
            e = parse_expr(v, local_dict=D_sym_dict)
            exprs[k_s] = e
            n, d = sympy.fraction(sympy.cancel(e))
            denoms.append(d)
            
        max_degrees = defaultdict(int)
        for d in denoms:
            if d == 1: continue
            factors = sympy.factor_list(d)
            for base, exp in factors[1]:
                max_degrees[base] = max(max_degrees[base], exp)
                
        common_d = sympy.Integer(1)
        for base, exp in max_degrees.items():
            common_d *= base**exp
            
        hypotheses = {}
        for k_s, e in exprs.items():
            hypotheses[k_s] = sympy.expand(sympy.cancel(e * common_d))
            
        t_pass, w_pass, pos_classes = verify_certificate(target["sigma"], target["k"], support_strs, hypotheses)
    else:
        t_pass, w_pass = False, False
        
    if not (t_pass and w_pass):
        print("  Direct equality failed. Trying undetermined coefficients...")
        hypotheses = None
        
        all_sides = []
        for pair_idx, (i, j) in enumerate(PAIRS):
            all_sides.append(f"({i},{j},+)")
            all_sides.append(f"({i},{j},-)")
            
        for deg in [1, 2]:
            print(f"    Trying degree {deg} with full 20-side support...")
            hyp = solve_undetermined_coefficients(target["sigma"], target["k"], all_sides, deg)
            if hyp:
                t_pass, w_pass, pos_classes = verify_certificate(target["sigma"], target["k"], list(hyp.keys()), hyp)
                if t_pass and w_pass:
                    print(f"    Success at degree {deg}!")
                    hypotheses = hyp
                    break
                    
    if not (t_pass and w_pass):
        print("  Equality failed completely.")
        return "equality_failed", None, None
        
    print(f"  Equality PASSED. Positivity: {pos_classes}")
    
    if all(c == "PROVEN POSITIVE" for c in pos_classes.values()):
        status = "proven_cellwide"
    elif any("NOT CELL-WIDE" in c for c in pos_classes.values()):
        status = "subcell_only"
    else:
        status = "equality_ok_positivity_undecided"
        
    return status, pos_classes, hypotheses

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        success = test_stage2a_5cycle()
        sys.exit(0 if success else 1)
        
    with open("extracted_certs.json") as f:
        data = json.load(f)
        
    with open("ansatz_catalogue.json") as f:
        catalogue = json.load(f)
        
    outcomes = {}
    try:
        with open("call2_outcomes.json", "r") as f:
            outcomes = json.load(f)
    except FileNotFoundError:
        pass
        
    symbolic_certs = []
    try:
        with open("symbolic_certs.json", "r") as f:
            symbolic_certs = json.load(f)
    except FileNotFoundError:
        pass
    
    TARGET_IDS = [53599, 50615, 53767, 55859, 32316, 60552]
    
    targets_to_run = []
    for t in data["targets"]:
        if t["idx"] in TARGET_IDS:
            targets_to_run.append(t)
            
    targets_to_run.sort(key=lambda t: TARGET_IDS.index(t["idx"]))
    
    for t in targets_to_run:
        status, pos_classes, hypotheses = process_target(t, catalogue)
        outcomes[str(t["idx"])] = {
            "status": status,
            "positivity_classes": pos_classes
        }
        
        with open("call2_outcomes.json", "w") as f:
            json.dump(outcomes, f, indent=2)
            
        if status in ("proven_cellwide", "subcell_only"):
            cert_data = {
                "sigma_bits": t["sigma"],
                "k": t["k"],
                "idx": t["idx"],
                "status": status,
                "support": list(hypotheses.keys()),
                "multipliers": {k: str(v) for k, v in hypotheses.items()}
            }
            symbolic_certs.append(cert_data)
            
            with open("symbolic_certs.json", "w") as f:
                json.dump(symbolic_certs, f, indent=2)
                
    print("\nSummary:")
    counts = defaultdict(int)
    for res in outcomes.values():
        counts[res["status"]] += 1
    for k, v in counts.items():
        print(f"{k}: {v}")
    print("Files updated: call2_outcomes.json, symbolic_certs.json")

