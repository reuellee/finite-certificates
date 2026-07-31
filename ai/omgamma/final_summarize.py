"""Assemble the final results table from all summaries on disk."""
import glob
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    rows = []
    for path in sorted(glob.glob(f"{HERE}/data/flip_*_summary.json")):
        s = json.load(open(path))
        rows.append((s['n'], s['r'], s['classes'],
                     s.get('catalog_matches_bfs'),
                     s['perm_holonomy_order'] == s['S_n_order'],
                     s['H_equals_Gbar'],
                     s.get('gamma_bar_connected'),
                     s.get('gamma_tilde_connected'), 'runflip'))
    for path in sorted(glob.glob(f"{HERE}/data/big_*/summary.json")):
        if any(x in path for x in (".orig", ".full", ".bak")):
            continue        # working backups, not results
        s = json.load(open(path))
        rows.append((s['n'], s['r'], s['classes'],
                     s.get('complete_by_mass'),
                     s.get('gamma_tilde_connected'),
                     s['H_equals_Gbar'],
                     s.get('gamma_bar_connected'),
                     s.get('gamma_tilde_connected'), 'runbig'))
    rows.sort()
    print(f"{'(n,r)':>8} {'classes':>9} {'complete':>9} {'H=Gbar':>7} "
          f"{'bar':>5} {'tilde':>6}  src")
    for (n, r, c, comp, pi, hf, gb, gt, src) in rows:
        print(f"({n},{r})".rjust(8) + f"{c:>10} {str(comp):>9} "
              f"{str(hf):>7} {str(gb):>5} {str(gt):>6}  {src}")
    # count files
    for path in sorted(glob.glob(f"{HERE}/data/mass_target_*.json")):
        s = json.load(open(path))
        print(f"mass target ({s['r']},{s['n']}): N_chi = {s['N_chi']} "
              f"(pairs {s['N_pairs']})")
    # in-flight campaigns and standalone holonomy certificates
    for path in sorted(glob.glob(f"{HERE}/data/big_*/meta.json")):
        if any(x in path for x in (".orig", ".full", ".bak")):
            continue
        m = json.load(open(path))
        if m.get('complete'):
            continue
        pct = 100 * int(m['total_mass']) / int(m['target_mass'])
        print(f"IN PROGRESS {os.path.basename(os.path.dirname(path))}: "
              f"level {m['level']}, {m['total_classes']} classes, "
              f"mass {pct:.4f}%, H=Gbar: {m.get('hol_full')}")
    for path in sorted(glob.glob(f"{HERE}/data/big_*/certA_dir/"
                                 "holonomy.json")):
        h = json.load(open(path))
        print(f"standalone holonomy certificate {path}: "
              f"pi {h['perm_order']}/{h['S_n']}, sign {h['sign_dim']}/"
              f"{h['n']}, H=Gbar: {h['H_equals_Gbar']}")


if __name__ == "__main__":
    main()
