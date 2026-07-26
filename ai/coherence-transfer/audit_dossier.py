#!/usr/bin/env python3
"""Adversarial third-party audit of EMPIRICAL_VERIFICATION_DOSSIER.md.

Accompanies the report "Causal-Ontology Inversion in Overcomplete Sparse
Autoencoders" (120 SAEs, semi-real digits experiment).

This script is self-contained: it extracts everything it needs FROM the
dossier file itself (fenced appendix blocks), recomputes every registered
statistic from the raw 120-row run table (Appendix H), reimplements the
20,000-replicate paired-seed percentile bootstrap exactly per Appendix N,
re-applies the registered decision rules of Appendix A, and cross-checks the
integrity manifest.  Requires only python3 + numpy.  Exits nonzero on any
FAIL of a claim that is verifiable from the dossier alone.

Usage:  python3 audit_dossier.py [path/to/EMPIRICAL_VERIFICATION_DOSSIER.md]

What this script deliberately does NOT rely on:
  - the dossier author's own Section 3 / Appendix Q checkpoint replay
    (the binary checkpoints are not in the dossier; replay is an open item);
  - any claimed preregistration *timing* (no trusted timestamp exists here).
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from dataclasses import dataclass, field, replace

import numpy as np

DEFAULT_DOSSIER = (
    "/home/reuellee_gmail_com/.claude/uploads/"
    "55132645-4238-4c90-b903-da2ddf509bbe/"
    "2d0588ef-EMPIRICAL_VERIFICATION_DOSSIER.md"
)
# Optional: report PDF, if present next to this audit (its sha256 is in §10).
REPORT_PDF_CANDIDATES = [
    "/home/reuellee_gmail_com/.claude/uploads/"
    "55132645-4238-4c90-b903-da2ddf509bbe/"
    "c31faa34-Causal_Ontology_Coherence_Inversion_Report.pdf",
]

# Headline claims of the report PDF (transcribed; the PDF itself is binary).
REPORT_CLAIMS = {
    "l1": {"mean": -0.255, "ci": (-0.312, -0.206), "neg": 12, "family": 0.792},
    "topk": {"mean": -0.409, "ci": (-0.497, -0.327), "neg": 12, "family": 0.848},
}

RESULTS: list[tuple[str, bool, str]] = []
WARNINGS: list[str] = []


def check(name: str, ok: bool, detail: str = "") -> bool:
    RESULTS.append((name, bool(ok), detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))
    return bool(ok)


def warn(msg: str) -> None:
    WARNINGS.append(msg)
    print(f"[NOTE] {msg}")


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# 0. Extract appendix blocks from the dossier
# ---------------------------------------------------------------------------

def extract_appendices(dossier_text: str) -> tuple[dict[str, str], str]:
    """Return {appendix_letter: fenced_body} and the main-body text.

    Appendix headers are '# Appendix X — ...' lines; each is followed by one
    ````-fenced block containing the verbatim artifact.  The main body is
    everything before the first appendix header (Sections 1-10).  The
    duplicated skeleton inside Appendix Q's f-string template is inert
    because it sits inside Q's fence.
    """
    lines = dossier_text.split("\n")
    headers: list[tuple[int, str]] = []
    for i, line in enumerate(lines):
        m = re.match(r"^# Appendix ([A-Q]) — ", line)
        if m:
            headers.append((i, m.group(1)))
    # keep only the first occurrence of each letter (Q template repeats them,
    # but those are inside Q's fence and come after the real ones anyway)
    seen: dict[str, int] = {}
    for i, letter in headers:
        if letter not in seen:
            seen[letter] = i
    apps: dict[str, str] = {}
    for letter, i in seen.items():
        j = i
        while not lines[j].startswith("````"):
            j += 1
        k = j + 1
        while not lines[k].startswith("````"):
            k += 1
        apps[letter] = "\n".join(lines[j + 1 : k]) + "\n"
    main_body = "\n".join(lines[: min(seen.values())])
    return apps, main_body


# ---------------------------------------------------------------------------
# 1. Parse Appendix A (preregistration)
# ---------------------------------------------------------------------------

def parse_prereg(a_text: str) -> dict:
    hashes = dict(
        re.findall(
            r"`((?:experiments|analysis)/[\w./]+\.py)`\s*\n\s*SHA-256\s*\n\s*`([0-9a-f]{64})`",
            a_text,
        )
    )
    out = {
        "code_hashes": hashes,
        "has_lock_statement": "LOCKED BEFORE CONFIRMATORY SEEDS 0–11" in a_text,
        "betas_registered": bool(
            re.search(r"beta\\in\\\{0,0\.025,0\.0625,0\.25,0\.5\\\}", a_text)
            or "{0,0.025,0.0625,0.25,0.5}" in a_text.replace("\\", "")
        ),
        "seeds_registered": "SAE seeds 0–11" in a_text,
        "n120": "120 trained SAEs" in a_text,
        "bootstrap_20000": "20,000-replicate paired-seed percentile" in a_text,
        "gate_gram": r"\le0.80" in a_text or "≤0.80" in a_text,
        "gate_gain": "family gain at least 0.75" in a_text,
        "gate_cosine": "family cosine at least 0.95" in a_text,
        "gate_fvu": "FVU at most 0.10" in a_text,
        "gate_l0": "within 0.05 of" in a_text,
        "pilot_disclosed": "seeds 900–903" in a_text,
        "data_hash": re.search(r"`(d00e7d6c[0-9a-f]{56})`", a_text).group(1),
    }
    return out


# ---------------------------------------------------------------------------
# CSV parsing (stdlib-free of pandas)
# ---------------------------------------------------------------------------

def parse_csv(text: str) -> list[dict[str, str]]:
    lines = [ln for ln in text.strip("\n").split("\n")]
    header = lines[0].split(",")
    return [dict(zip(header, ln.split(","))) for ln in lines[1:]]


# ---------------------------------------------------------------------------
# Bootstrap reimplementation per Appendix N
# ---------------------------------------------------------------------------

BOOTSTRAP_REPS = 20_000
BOOTSTRAP_SEED = 8675309


def bootstrap_ci(differences: np.ndarray, salt: int) -> tuple[float, float]:
    rng = np.random.default_rng(BOOTSTRAP_SEED + salt)
    idx = rng.integers(0, differences.size, size=(BOOTSTRAP_REPS, differences.size))
    means = differences[idx].mean(axis=1)
    lo, hi = np.quantile(means, [0.025, 0.975])
    return float(lo), float(hi)


def field_salt(architecture: str, fld: str) -> int:
    return sum(ord(c) for c in architecture + fld)


# ---------------------------------------------------------------------------
# Gradient checker re-execution (pure-numpy parts of Appendix O,
# using functions transcribed verbatim from Appendix M/O extracted text)
# ---------------------------------------------------------------------------

def rerun_gradient_checks(m_src: str, o_src: str) -> dict[str, float]:
    """Execute _gram_penalty_and_grad/_apply_topk from Appendix M and the
    gram/directional checks from Appendix O without scipy/sklearn, by
    compiling only the needed defs from the embedded verbatim sources."""
    ns_m: dict = {"np": np}
    for fname in ("_gram_penalty_and_grad", "_apply_topk"):
        m = re.search(rf"(?ms)^def {fname}\(.*?(?=^\ndef |^class |\Z)", m_src)
        exec(compile(m.group(0), f"appendix_M:{fname}", "exec"), ns_m)

    @dataclass(frozen=True)
    class Config:
        l1_lambda: float = 0.2
        topk_k: int = 16

    ns_o: dict = {
        "np": np,
        "replace": replace,
        "Config": Config,
        "_gram_penalty_and_grad": ns_m["_gram_penalty_and_grad"],
        "_apply_topk": ns_m["_apply_topk"],
    }
    printed: list[str] = []
    ns_o["print"] = lambda *a, **k: printed.append(" ".join(str(x) for x in a))
    for fname in ("objective_and_gradients", "directional_check", "gram_check"):
        m = re.search(rf"(?ms)^def {fname}\(.*?(?=^\ndef |^class |\Z)", o_src)
        exec(compile(m.group(0), f"appendix_O:{fname}", "exec"), ns_o)
    out: dict[str, float] = {}
    out["gram_rel_err"] = ns_o["gram_check"]()
    out["l1_rel_err"] = ns_o["directional_check"]("l1")
    out["topk_rel_err"] = ns_o["directional_check"]("topk")
    out["printed"] = printed  # type: ignore[assignment]
    return out


# ---------------------------------------------------------------------------
# main audit
# ---------------------------------------------------------------------------

def replication_audit(repl_path: str, dossier_path: str) -> int:
    """--replication mode: compare an independently produced run_metrics.csv
    (and, if adjacent, weights_sha256.csv) against the dossier's Appendix
    H / E / L records and the registered decision rules.

    repl_path may be a results directory or a run_metrics.csv file."""
    text = open(dossier_path, encoding="utf-8").read()
    apps, body = extract_appendices(text)
    manifest = {m.group(1): m.group(3) for m in re.finditer(
        r"^\| ([\w./-]+) \| (\d+) \| ([0-9a-f]{64}) \|$", body, re.M)}
    if os.path.isdir(repl_path):
        metrics_path = os.path.join(repl_path, "run_metrics.csv")
    else:
        metrics_path, repl_path = repl_path, os.path.dirname(repl_path)

    print("=" * 78)
    print("REPLICATION MODE — independent rerun vs dossier registered records")
    print("=" * 78)
    raw = open(metrics_path, "rb").read()
    h_exact = hashlib.sha256(raw).hexdigest()
    recorded = manifest["results/coherence_transfer_semireal/run_metrics.csv"]
    exact = h_exact == recorded
    check("replication run_metrics.csv byte-identical to registered original",
          exact, f"sha256 {h_exact[:16]}… vs recorded {recorded[:16]}…")

    rrows = parse_csv(raw.decode("utf-8").replace("\r\n", "\n"))
    hrows = parse_csv(apps["H"])
    archs = ["l1", "topk"]

    def key(r: dict) -> tuple:
        return (r["architecture"], int(r["seed"]), float(r["beta"]))

    rmap = {key(r): r for r in rrows}
    hmap = {key(r): r for r in hrows}
    check("replication covers the exact 120 registered cells",
          set(rmap) == set(hmap) and len(rrows) == 120)
    if set(rmap) != set(hmap):
        return 1

    # per-cell numeric drift on all shared metric fields
    skip = {"seed", "beta", "architecture", "d", "m", "wall_seconds"}
    shared = [f for f in hrows[0] if f not in skip and f in rrows[0]
              and not f.endswith("faithful_geometry")]
    worst: dict[str, float] = {}
    for k in hmap:
        for f in shared:
            try:
                dv = abs(float(hmap[k][f]) - float(rmap[k][f]))
            except ValueError:
                dv = 0.0 if hmap[k][f] == rmap[k][f] else float("inf")
            worst[f] = max(worst.get(f, 0.0), dv)
    print("  per-run max |replication - registered| (selected fields):")
    for f in ("fvu", "l0", "gram_penalty", "mean_factor_max_positive_cosine",
              "mean_factor_causal_concentration", "mean_factor_causal_split_count",
              "mean_factor_family_gain", "mean_factor_family_cosine"):
        print(f"    {f:42s} {worst[f]:.3e}")
    worst_all = max(worst.values())
    if exact:
        check("per-run metrics numerically identical to registered rows",
              worst_all == 0.0)
    else:
        warn(f"per-run drift vs registered rows: max over all fields "
             f"{worst_all:.3e} (informational — environment-dependent float "
             f"paths make per-run trajectories diverge; the registered "
             f"claims are judged on the aggregate checks below)")

    # condition means / gates at report precision
    def cmean(rows_map, arch, beta, fld):
        return float(np.mean([float(rows_map[(arch, s, beta)][fld])
                              for s in range(12)]))
    gates_ok = True
    for arch in archs:
        ratio = cmean(rmap, arch, 0.5, "gram_penalty") / cmean(rmap, arch, 0.0, "gram_penalty")
        gain = cmean(rmap, arch, 0.5, "mean_factor_family_gain")
        cosv = cmean(rmap, arch, 0.5, "mean_factor_family_cosine")
        fvu = cmean(rmap, arch, 0.5, "fvu")
        print(f"  {arch}: gram_ratio={ratio:.6f} gain={gain:.6f} "
              f"cosine={cosv:.6f} fvu={fvu:.6f}")
        gates_ok &= ratio <= 0.80 and gain >= 0.75 and cosv >= 0.95 and fvu <= 0.10
    l0dev = max(abs(float(r["l0"]) - 16.0) for r in rrows if r["architecture"] == "topk")
    gates_ok &= l0dev <= 0.05
    check("replication: all registered gates pass", gates_ok,
          f"topk max|L0-16|={l0dev:.6f}")

    # 22 paired contrasts + bootstrap + sign counts vs Appendix E
    contrast_fields = [
        "mean_factor_max_positive_cosine", "mean_factor_causal_concentration",
        "mean_factor_causal_participation_ratio", "mean_factor_causal_split_count",
        "mean_factor_single_gain", "mean_factor_family_gain", "fvu", "l0",
        "dead_fraction", "gram_penalty", "max_absolute_coherence",
    ]
    erows = {(r["architecture"], r["field"]): r for r in parse_csv(apps["E"])}
    mean4 = ci4 = signs_ok = 0
    ci = {}
    for arch in archs:
        for fld in contrast_fields:
            d = np.array([float(rmap[(arch, s, 0.5)][fld])
                          - float(rmap[(arch, s, 0.0)][fld]) for s in range(12)])
            lo, hi = bootstrap_ci(d, field_salt(arch, fld))
            ci[(arch, fld)] = (lo, hi)
            e = erows[(arch, fld)]
            mean4 += abs(d.mean() - float(e["mean_difference"])) <= 5.1e-5
            ci4 += (abs(lo - float(e["ci95_lower"])) <= 5.1e-5
                    and abs(hi - float(e["ci95_upper"])) <= 5.1e-5)
            signs_ok += (int(np.sum(d < 0)), int(np.sum(d > 0)), int(np.sum(d == 0))) == (
                int(e["negative_seeds"]), int(e["positive_seeds"]), int(e["zero_seeds"]))
            if fld == "mean_factor_max_positive_cosine":
                print(f"  {arch} alignment: {d.mean():+.6f} CI [{lo:+.6f}, {hi:+.6f}] "
                      f"{int(np.sum(d<0))}/12 neg  (registered "
                      f"{float(e['mean_difference']):+.6f} "
                      f"[{float(e['ci95_lower']):+.6f}, {float(e['ci95_upper']):+.6f}])")
    print(f"  contrasts matching Appendix E at 4dp: means {mean4}/22, "
          f"CIs {ci4}/22, sign counts {signs_ok}/22")
    check("replication: all 22 mean differences match Appendix E at 4dp", mean4 == 22)
    check("replication: all 22 bootstrap CIs match Appendix E at 4dp", ci4 == 22)
    check("replication: all 22 seed sign counts match Appendix E", signs_ok == 22)

    # registered predictions from replication data
    p1 = all(ci[(a, "mean_factor_max_positive_cosine")][1] < 0 for a in archs)
    p2 = all(ci[(a, "mean_factor_causal_split_count")][0] > 0
             and ci[(a, "mean_factor_causal_participation_ratio")][0] > 0 for a in archs)
    p3 = {a: ci[(a, "mean_factor_causal_concentration")][1] < 0 for a in archs}
    check("replication: P1 SUPPORTED (both architectures)", gates_ok and p1)
    check("replication: P2 SUPPORTED (both architectures)", p2)
    check("replication: P3 outcome identical to registered (topk only)",
          p3 == {"l1": False, "topk": True}, str(p3))

    # checkpoint digests vs Appendix L
    wpath = os.path.join(repl_path, "weights_sha256.csv")
    if os.path.exists(wpath):
        lmap = {r["filename"]: r["sha256"] for r in parse_csv(apps["L"])}
        wmap = {r["filename"]: r["sha256"]
                for r in parse_csv(open(wpath).read().replace("\r\n", "\n"))}
        matches = sum(1 for k in lmap if wmap.get(k) == lmap[k])
        check("replication checkpoints digest-identical to Appendix L (120/120)",
              matches == 120,
              f"{matches}/120 exact digest matches"
              + ("" if matches == 120 else
                 " — expected only under a bit-identical environment "
                 "(same wheels, BLAS kernels, CPU dispatch)"))
    else:
        warn("no weights_sha256.csv next to replication metrics; "
             "checkpoint digest comparison skipped")

    nfail = sum(1 for _, ok, _ in RESULTS if not ok)
    print(f"REPLICATION TOTAL: {len(RESULTS)} checks, "
          f"{len(RESULTS) - nfail} PASS, {nfail} FAIL")
    return 1 if nfail else 0


def main() -> int:
    argv = list(sys.argv[1:])
    if argv and argv[0] == "--replication":
        dossier_path = argv[2] if len(argv) > 2 else DEFAULT_DOSSIER
        return replication_audit(argv[1], dossier_path)
    dossier_path = argv[0] if argv else DEFAULT_DOSSIER
    text = open(dossier_path, encoding="utf-8").read()
    apps, body = extract_appendices(text)

    print("=" * 78)
    print("SECTION 1 — preregistration (Appendix A) parsed")
    print("=" * 78)
    check("A: all appendices A-Q present", set(apps) == set("ABCDEFGHIJKLMNOPQ"))
    prereg = parse_prereg(apps["A"])
    for key in (
        "has_lock_statement", "seeds_registered", "n120", "bootstrap_20000",
        "gate_gram", "gate_gain", "gate_cosine", "gate_fvu", "gate_l0",
        "pilot_disclosed",
    ):
        check(f"A: prereg contains registered element '{key}'", prereg[key])
    check(
        "A: prereg records 3 analysis-code hashes",
        len(prereg["code_hashes"]) == 3,
        str(sorted(prereg["code_hashes"])),
    )
    warn(
        "Prereg temporal lock (hash lock 'before confirmatory seeds') cannot be "
        "verified from this file alone — no trusted timestamp/public commit. "
        "Open item, as the dossier itself concedes in Section 2."
    )

    print()
    print("=" * 78)
    print("SECTION 2 — frozen-source hash verification (Appendices M-Q vs A/§10)")
    print("=" * 78)
    # §10 manifest from main body
    manifest = dict()
    manifest_bytes = dict()
    for m in re.finditer(r"^\| ([\w./-]+) \| (\d+) \| ([0-9a-f]{64}) \|$", body, re.M):
        manifest[m.group(1)] = m.group(3)
        manifest_bytes[m.group(1)] = int(m.group(2))
    check("§10: integrity manifest parsed (20 files)", len(manifest) == 20,
          f"{len(manifest)} rows")

    embed_map = {
        "A": "notes/prereg-coherence-transfer-semireal.md",
        "B": "results/coherence_transfer_semireal/REGISTERED_ANALYSIS.md",
        "C": "results/coherence_transfer_semireal/condition_means.csv",
        "D": "results/coherence_transfer_semireal/metadata.json",
        "E": "results/coherence_transfer_semireal/paired_contrasts.csv",
        "F": "results/coherence_transfer_semireal/analysis_summary.json",
        "G": "results/coherence_transfer_semireal/POSTHOC_ROBUSTNESS.md",
        "H": "results/coherence_transfer_semireal/run_metrics.csv",
        "I": "results/coherence_transfer_semireal/posthoc_robustness_condition_means.csv",
        "J": "results/coherence_transfer_semireal/posthoc_robustness_summary.json",
        "K": "results/coherence_transfer_semireal/posthoc_robustness_metrics.csv",
        "L": "results/coherence_transfer_semireal/weights_sha256.csv",
        "M": "experiments/coherence_transfer_semireal.py",
        "N": "analysis/analyze_coherence_transfer_semireal.py",
        "O": "analysis/check_coherence_transfer_gradients.py",
        "P": "analysis/posthoc_coherence_transfer_robustness.py",
        "Q": "analysis/render_empirical_verification_dossier.py",
    }
    crlf_equivalent = []
    for letter, fname in embed_map.items():
        content = apps[letter]
        recorded = manifest[fname]
        h_lf = sha256_text(content)
        if h_lf == recorded:
            nbytes = len(content.encode("utf-8"))
            check(
                f"hash {letter} == §10 {fname.split('/')[-1]}",
                nbytes == manifest_bytes[fname],
                f"sha256 exact match; bytes {nbytes} vs recorded {manifest_bytes[fname]}",
            )
        else:
            # csv module writes \r\n; embedding via read_text() normalized to \n.
            h_crlf = sha256_text(content.replace("\n", "\r\n"))
            if h_crlf == recorded:
                crlf_equivalent.append(letter)
                check(
                    f"hash {letter} == §10 {fname.split('/')[-1]} (CRLF-restored)",
                    len(content.replace("\n", "\r\n").encode()) == manifest_bytes[fname],
                    "embedded copy is LF-normalized; restoring CRLF line endings "
                    "reproduces the recorded digest exactly — content-equivalent",
                )
            else:
                check(f"hash {letter} == §10 {fname.split('/')[-1]}", False,
                      f"recorded {recorded[:16]}…, got LF {h_lf[:16]}… / CRLF {h_crlf[:16]}…")

    # Appendix A's own three code hashes vs recomputed embedded source
    for fname, recorded in prereg["code_hashes"].items():
        letter = {v: k for k, v in embed_map.items()}[fname]
        check(
            f"prereg hash of {fname} matches embedded Appendix {letter}",
            sha256_text(apps[letter]) == recorded,
        )
    # cross-link: analysis_summary.json recorded the run_metrics.csv digest it read
    F = json.loads(apps["F"])
    check(
        "F: analysis ran on the same run_metrics.csv as §10/Appendix H",
        F["metrics_sha256"] == manifest[embed_map["H"]],
    )
    check("F: metadata digest cross-link", F["metadata_sha256"] == manifest[embed_map["D"]])

    # optional: report PDF digest
    for pdf in REPORT_PDF_CANDIDATES:
        if os.path.exists(pdf):
            h = hashlib.sha256(open(pdf, "rb").read()).hexdigest()
            check(
                "report PDF sha256 matches §10 manifest",
                h == manifest["output/pdf/Causal_Ontology_Coherence_Inversion_Report.pdf"],
                pdf.split("/")[-1],
            )
            break
    else:
        warn("report PDF not found locally; skipped optional PDF digest check")

    print()
    print("=" * 78)
    print("SECTION 3 — recompute all registered statistics from Appendix H")
    print("=" * 78)
    rows = parse_csv(apps["H"])
    for r in rows:
        r["seed_i"] = int(r["seed"])          # type: ignore[index]
        r["beta_f"] = float(r["beta"])        # type: ignore[index]
    betas = [0.0, 0.025, 0.0625, 0.25, 0.5]
    archs = ["l1", "topk"]
    cells = {(r["architecture"], r["seed_i"], r["beta_f"]) for r in rows}
    check("H: exactly 120 rows, 120 unique cells",
          len(rows) == 120 and len(cells) == 120)
    check("H: full 2x12x5 registered coverage, m=68",
          cells == {(a, s, b) for a in archs for s in range(12) for b in betas}
          and all(r["m"] == "68" for r in rows))

    def cell_rows(arch: str, beta: float) -> list[dict]:
        return [r for r in rows if r["architecture"] == arch and r["beta_f"] == beta]

    def cell_mean(arch: str, beta: float, fld: str) -> float:
        vals = [float(r[fld]) for r in cell_rows(arch, beta)]
        return float(np.mean(np.asarray(vals)))

    # --- condition means vs Appendix C (full precision)
    crows = parse_csv(apps["C"])
    max_cond_err = 0.0
    for cr in crows:
        arch, beta = cr["architecture"], float(cr["beta"])
        for fld, val in cr.items():
            if fld in ("architecture", "m", "beta"):
                continue
            err = abs(cell_mean(arch, beta, fld) - float(val))
            max_cond_err = max(max_cond_err, err)
    check("condition means recomputed from H match Appendix C",
          max_cond_err < 1e-9, f"max abs error {max_cond_err:.3e}")

    # --- Appendix B condition table (4-decimal print) spot check
    b_l1_row = re.search(r"^\| l1 \| 0\.5 \| (.+) \|$", apps["B"], re.M).group(1).split(" | ")
    b_vals = [float(x) for x in b_l1_row]
    expect = [cell_mean("l1", 0.5, f) for f in (
        "fvu", "l0", "dead_fraction", "gram_penalty", "max_absolute_coherence",
        "mean_factor_max_positive_cosine", "mean_factor_causal_concentration",
        "mean_factor_causal_split_count", "mean_factor_family_gain")]
    check("B: printed l1/beta=0.5 condition row matches recomputation (4dp)",
          all(abs(b - e) <= 5.0001e-5 for b, e in zip(b_vals, expect)))

    # --- gates recomputed
    gate_details = {}
    for arch in archs:
        gate_details[arch] = {
            "gram_ratio": cell_mean(arch, 0.5, "gram_penalty")
            / cell_mean(arch, 0.0, "gram_penalty"),
            "family_gain": cell_mean(arch, 0.5, "mean_factor_family_gain"),
            "family_cosine": cell_mean(arch, 0.5, "mean_factor_family_cosine"),
            "fvu": cell_mean(arch, 0.5, "fvu"),
        }
    topk_l0_dev = max(abs(float(r["l0"]) - 16.0) for r in rows if r["architecture"] == "topk")

    # compare to §4 table in main body
    sec4 = re.findall(
        r"^\| (l1|topk) \| ([\d.]+) \| ([\d.]+) \| ([\d.]+) \| ([\d.]+) \|$", body, re.M)
    sec4d = {t[0]: [float(x) for x in t[1:]] for t in sec4}
    ok4 = True
    for arch in archs:
        g = gate_details[arch]
        rec = sec4d[arch]
        ok4 &= all(abs(a - b) < 5e-10 for a, b in zip(
            [g["gram_ratio"], g["family_gain"], g["family_cosine"], g["fvu"]], rec))
    check("§4 recomputed-gates table matches recomputation", ok4,
          "; ".join(f"{a}: ratio={gate_details[a]['gram_ratio']:.6f} gain="
                    f"{gate_details[a]['family_gain']:.6f} cos="
                    f"{gate_details[a]['family_cosine']:.6f} fvu="
                    f"{gate_details[a]['fvu']:.6f}" for a in archs))
    m_dev = re.search(r"maximum observed deviation is\n([\d.]+?)\.?$", body, re.M)
    check("§4 TopK max |L0-16| matches", abs(topk_l0_dev - float(m_dev.group(1))) < 5e-10,
          f"recomputed {topk_l0_dev:.9f}")

    # gate PASS/FAIL per Appendix A rules
    gates_pass = {
        "conformance": len(rows) == 120 and len(cells) == 120,
        "manipulation": all(gate_details[a]["gram_ratio"] <= 0.80 for a in archs),
        "retention": all(
            gate_details[a]["family_gain"] >= 0.75
            and gate_details[a]["family_cosine"] >= 0.95
            and gate_details[a]["fvu"] <= 0.10
            for a in archs),
        "topk_fixed_l0": topk_l0_dev <= 0.05,
    }
    for gname, ok in gates_pass.items():
        check(f"registered gate '{gname}' (recomputed)", ok)
    all_gates = all(gates_pass.values())

    # --- paired per-seed differences and sign counts vs Appendix E and F
    contrast_fields = [
        "mean_factor_max_positive_cosine", "mean_factor_causal_concentration",
        "mean_factor_causal_participation_ratio", "mean_factor_causal_split_count",
        "mean_factor_single_gain", "mean_factor_family_gain", "fvu", "l0",
        "dead_fraction", "gram_penalty", "max_absolute_coherence",
    ]
    erows = {(r["architecture"], r["field"]): r for r in parse_csv(apps["E"])}
    fcon = {(c["architecture"], c["field"]): c for c in F["contrasts"]}
    diffs: dict[tuple[str, str], np.ndarray] = {}
    max_mean_err = 0.0
    sign_ok = True
    per_seed_ok = True
    for arch in archs:
        for fld in contrast_fields:
            d = np.array([
                float(next(r[fld] for r in rows if r["architecture"] == arch
                           and r["seed_i"] == s and r["beta_f"] == 0.5))
                - float(next(r[fld] for r in rows if r["architecture"] == arch
                             and r["seed_i"] == s and r["beta_f"] == 0.0))
                for s in range(12)
            ])
            diffs[(arch, fld)] = d
            e = erows[(arch, fld)]
            max_mean_err = max(max_mean_err, abs(d.mean() - float(e["mean_difference"])))
            sign_ok &= (int(np.sum(d < 0)), int(np.sum(d > 0)), int(np.sum(d == 0))) == (
                int(e["negative_seeds"]), int(e["positive_seeds"]), int(e["zero_seeds"]))
            ps = fcon[(arch, fld)]["per_seed_difference"]
            per_seed_ok &= all(abs(d[s] - ps[str(s)]) < 1e-12 for s in range(12))
    check("paired mean differences match Appendix E (all 22 contrasts)",
          max_mean_err < 1e-12, f"max abs error {max_mean_err:.3e}")
    check("per-seed sign counts match Appendix E (all 22 contrasts)", sign_ok)
    check("per-seed differences match Appendix F per_seed_difference", per_seed_ok)
    check("Appendix E and Appendix F contrasts are identical",
          all(abs(float(erows[k][c]) - fcon[k][c]) < 1e-12
              for k in erows for c in ("mean_difference", "ci95_lower", "ci95_upper")))

    # --- §6 per-seed table vs recomputed (printed 6dp)
    sec6 = re.findall(
        r"^\| (l1|topk) \| (\d+) \| ([+-][\d.]+) \| ([+-][\d.]+) \| ([+-][\d.]+) \|"
        r" ([+-][\d.]+) \| ([\d.]+) \| ([\d.]+) \| ([+-][\d.]+) \| ([+-][\d.]+) \|$",
        body, re.M)
    ok6 = len(sec6) == 24
    for t in sec6:
        arch, s = t[0], int(t[1])
        hi = next(r for r in rows if r["architecture"] == arch and r["seed_i"] == s
                  and r["beta_f"] == 0.5)
        vals = {
            2: diffs[(arch, "mean_factor_max_positive_cosine")][s],
            3: diffs[(arch, "mean_factor_causal_concentration")][s],
            4: diffs[(arch, "mean_factor_causal_participation_ratio")][s],
            6: float(hi["mean_factor_family_gain"]),
            7: float(hi["mean_factor_family_cosine"]),
            8: diffs[(arch, "fvu")][s],
            9: diffs[(arch, "l0")][s],
        }
        ok6 &= all(abs(float(t[i]) - v) <= 5.001e-7 for i, v in vals.items())
        ok6 &= abs(float(t[5]) - diffs[(arch, "mean_factor_causal_split_count")][s]) <= 5.1e-4
    check("§6 per-seed evidence table matches recomputation (24 rows)", ok6)

    print()
    print("=" * 78)
    print("SECTION 4 — bootstrap reproduction (Appendix N algorithm, seed 8675309)")
    print("=" * 78)
    max_ci_err = 0.0
    for (arch, fld), d in diffs.items():
        lo, hi = bootstrap_ci(d, field_salt(arch, fld))
        e = erows[(arch, fld)]
        max_ci_err = max(max_ci_err, abs(lo - float(e["ci95_lower"])),
                         abs(hi - float(e["ci95_upper"])))
    check("all 22 registered bootstrap CIs reproduced exactly",
          max_ci_err < 1e-12, f"max endpoint error {max_ci_err:.3e} "
          f"(numpy {np.__version__} here vs 2.3.5 recorded)")
    # retention-gate family-gain bootstrap (salt 1000 + arch)
    ret_err = 0.0
    for arch in archs:
        gains = np.array([float(next(r["mean_factor_family_gain"] for r in rows
                                     if r["architecture"] == arch and r["seed_i"] == s
                                     and r["beta_f"] == 0.5)) for s in range(12)])
        lo, hi = bootstrap_ci(gains, 1000 + sum(ord(c) for c in arch))
        ret = F["gates"]["retention"][arch]
        ret_err = max(ret_err, abs(lo - ret["family_gain_ci95_lower"]),
                      abs(hi - ret["family_gain_ci95_upper"]))
    check("retention-gate family-gain bootstrap CIs reproduced",
          ret_err < 1e-12, f"max endpoint error {ret_err:.3e}")

    # headline numbers, printed precision, vs §5 and Appendix B and the report
    headline = {}
    for arch in archs:
        d = diffs[(arch, "mean_factor_max_positive_cosine")]
        lo, hi = bootstrap_ci(d, field_salt(arch, "mean_factor_max_positive_cosine"))
        headline[arch] = (float(d.mean()), lo, hi, int(np.sum(d < 0)))
    sec5 = re.findall(r"−([\d.]+), 95% CI \[−([\d.]+), −([\d.]+)\], (\d+)/12 seeds", body)
    check("§5 contains two headline alignment result lines", len(sec5) == 2)
    for arch, t in zip(archs, sec5):
        mean, lo, hi, neg = headline[arch]
        ok = (abs(mean + float(t[0])) <= 5.1e-7 and abs(lo + float(t[1])) <= 5.1e-7
              and abs(hi + float(t[2])) <= 5.1e-7 and neg == int(t[3]))
        check(
            f"§5 {arch} headline matches registered Appendix E at printed 6dp",
            ok,
            f"§5 prints −{t[0]} CI [−{t[1]}, −{t[2]}]; recomputed/Appendix E "
            f"{mean:+.6f} CI [{lo:+.6f}, {hi:+.6f}]"
            + ("" if ok else " — REAL DISCREPANCY: these §5 digits are "
               "hard-coded literals in the Appendix Q template, not derived "
               "from the registered data"),
        )
        ok3 = (abs(mean + float(t[0])) <= 5.1e-4 and abs(lo + float(t[1])) <= 5.1e-4
               and abs(hi + float(t[2])) <= 5.1e-4 and neg == int(t[3]))
        check(f"§5 {arch} headline agrees with Appendix E at report precision (3dp)",
              ok3, "discrepancy immaterial to registered verdict" if ok3 else "")
    ok_rep = True
    for arch in archs:
        mean, lo, hi, neg = headline[arch]
        c = REPORT_CLAIMS[arch]
        ok_rep &= (abs(mean - c["mean"]) <= 5.1e-4 and abs(lo - c["ci"][0]) <= 5.1e-4
                   and abs(hi - c["ci"][1]) <= 5.1e-4 and neg == c["neg"]
                   and abs(gate_details[arch]["family_gain"] - c["family"]) <= 5.1e-4)
    check("report PDF headline claims (as transcribed) match recomputation (3dp)", ok_rep)

    print()
    print("=" * 78)
    print("SECTION 5 — registered decision rules applied to recomputed numbers")
    print("=" * 78)
    ci = {(a, f): bootstrap_ci(diffs[(a, f)], field_salt(a, f))
          for a in archs for f in contrast_fields}
    p1 = {a: ci[(a, "mean_factor_max_positive_cosine")][1] < 0.0 for a in archs}
    p2 = {a: ci[(a, "mean_factor_causal_split_count")][0] > 0.0
          and ci[(a, "mean_factor_causal_participation_ratio")][0] > 0.0 for a in archs}
    p3 = {a: ci[(a, "mean_factor_causal_concentration")][1] < 0.0 for a in archs}
    p1_verdict = ("SUPPORTED" if all_gates and all(p1.values())
                  else ("UNINTERPRETABLE" if not all_gates else "NOT SUPPORTED"))
    print(f"P1 (primary): gates={'PASS' if all_gates else 'FAIL'}, "
          f"CI upper<0: l1={p1['l1']}, topk={p1['topk']} -> {p1_verdict}")
    print(f"P2: l1={p2['l1']}, topk={p2['topk']}")
    print(f"P3: l1={p3['l1']}, topk={p3['topk']}")
    check("P1 primary: registered rule yields SUPPORTED", p1_verdict == "SUPPORTED")
    check("Appendix B primary verdict wording consistent with recomputed P1",
          F["primary_verdict"].startswith("SUPPORTED:") and all(p1.values()) and all_gates,
          F["primary_verdict"][:60] + "…")
    check("Appendix B splitting verdict consistent with recomputed P2",
          (F["splitting_verdict"] == "SUPPORTED IN BOTH ARCHITECTURES") == all(p2.values()))
    concentration_expected = ("SUPPORTED IN BOTH ARCHITECTURES" if all(p3.values())
                              else "SUPPORTED IN " + ", ".join(a for a in archs if p3[a])
                              if any(p3.values()) else "NOT SUPPORTED")
    check("Appendix B concentration verdict consistent with recomputed P3",
          F["concentration_verdict"] == concentration_expected,
          f"recomputed: {concentration_expected!r}; "
          f"P3 supported only in topk (l1 CI crosses zero: "
          f"[{ci[('l1','mean_factor_causal_concentration')][0]:+.4f}, "
          f"{ci[('l1','mean_factor_causal_concentration')][1]:+.4f}])")
    check("B gate lines all say PASS",
          all(f"- {g}: PASS" in apps["B"] for g in
              ("Conformance", "Coherence manipulation", "Family-retention gate",
               "TopK fixed-L0 gate")))
    # no-spin check: B verdict strings are exactly the frozen N templates
    # (N splits the template across adjacent string literals, so check each
    # fragment appears verbatim in N's source and their join equals the verdict)
    template_fragments = [
        "SUPPORTED: strong full-Gram regularization reduced one-atom ",
        "causal-direction alignment while the causal direction remained ",
        "recoverable at the decoder-family level in both architectures",
    ]
    check("B verdict strings are the frozen Appendix N templates (no editorializing)",
          all(f'"{frag}"' in apps["N"] for frag in template_fragments)
          and "".join(template_fragments) == F["primary_verdict"]
          and F["primary_verdict"] in apps["B"]
          and F["splitting_verdict"] in apps["B"]
          and F["concentration_verdict"] in apps["B"])

    print()
    print("=" * 78)
    print("SECTION 6 — checkpoint manifest internal consistency + local absence")
    print("=" * 78)
    lrows = parse_csv(apps["L"])
    ok_form = len(lrows) == 120 and all(
        re.fullmatch(r"[0-9a-f]{64}", r["sha256"]) and int(r["bytes"]) > 0 for r in lrows)
    names = {r["filename"] for r in lrows}
    def bfmt(b: float) -> str:
        return f"{b:.6g}"
    expected_names = {
        f"weights_{a}_m68_seed{s:03d}_beta{bfmt(b)}.npz"
        for a in archs for s in range(12) for b in betas}
    check("L: 120 well-formed checkpoint digests", ok_form)
    check("L: filenames exactly cover the 120 registered runs", names == expected_names)
    check("L: all 120 digests unique", len({r["sha256"] for r in lrows}) == 120)
    check("§10: archive digest recorded for checkpoint package",
          "output/Causal_Ontology_Coherence_Inversion_Research_Package.zip" in manifest)

    found: list[str] = []
    targets = {"run_metrics.csv", "weights_sha256.csv",
               "Causal_Ontology_Coherence_Inversion_Research_Package.zip"}
    for root, dirnames, filenames in os.walk("/home/reuellee_gmail_com"):
        dirnames[:] = [d for d in dirnames if d not in
                       {".cache", ".git", "node_modules", ".venv", "__pycache__"}]
        for fn in filenames:
            if fn in names or fn in targets or (
                    fn.startswith("weights_") and fn.endswith(".npz")):
                found.append(os.path.join(root, fn))
    check("checkpoints/raw artifacts NOT present on this machine "
          "(decoder-level replay remains an open item)", not found,
          "; ".join(found[:5]) if found else "searched /home/reuellee_gmail_com")

    print()
    print("=" * 78)
    print("SECTION 7 — frozen training source audit (Appendix M) + gradient checks")
    print("=" * 78)
    msrc = apps["M"]
    check("M: pure NumPy/SciPy/sklearn — no torch anywhere in frozen sources",
          all("torch" not in apps[x] for x in "MNOPQ"))
    check("M: init RNG depends only on seed (identical init across beta)",
          "np.random.default_rng(seed)" in msrc)
    check("M: batch RNG depends only on seed (identical minibatches across beta)",
          "np.random.default_rng(1_000_000 + seed)" in msrc)
    check("M: decoder columns renormalized after every update",
          "decoder /= np.linalg.norm(decoder, axis=0, keepdims=True).clip(1e-8)" in msrc
          and msrc.count("decoder /= np.linalg.norm(decoder, axis=0") >= 2)
    check("M: 10000 steps / batch 256 / lr 0.002 / k=16 / lambda=0.2 defaults",
          all(s in msrc for s in ("steps: int = 10000", "batch_size: int = 256",
                                  "learning_rate: float = 0.002", "topk_k: int = 16",
                                  "l1_lambda: float = 0.2")))
    check("M: lr decay 1/3 at steps//2, 1/10 at 4*steps//5 (5000/8000 as registered)",
          "steps // 2" in msrc and "(4 * steps) // 5" in msrc
          and "1.0 / 3.0" in msrc and "1.0 / 10.0" in msrc)
    check("M: no dead-latent resampling / no run exclusion code",
          "resampl" not in msrc.lower() and "exclude" not in msrc.lower())
    check("M: full squared-Gram penalty sum_{i<j}<di,dj>^2 (0.5*||offdiag||_F^2)",
          "penalty = 0.5 * float(np.sum(offdiag * offdiag))" in msrc)
    check("M: train/eval separation (split indices, train-only pixel stats & scaling)",
          "digits_x[train_idx].mean(axis=0)" in msrc
          and "np.linalg.norm(h_train, axis=1)" in msrc
          and "train_test_split" in msrc and "stratify=digits_y" in msrc)
    check("M: registered dataset seeds present (20260725/271828/314159)",
          all(s in msrc for s in ("20260725", "271828", "314159")))

    g = rerun_gradient_checks(msrc, apps["O"])
    printed = "\n".join(g.pop("printed"))
    print(printed)
    check("O: gradient checks re-executed locally, all rel. errors < 1e-7",
          max(g.values()) < 1e-7, f"max {max(g.values()):.3e}")
    sec3_vals = re.findall(r"analytic=([\d.-]+) numeric", body)
    got_vals = re.findall(r"analytic=([\d.-]+) numeric", printed)
    check("§3 gradient-checker printed analytic values reproduced bit-for-bit",
          sec3_vals and sorted(sec3_vals) == sorted(got_vals),
          f"recorded {sec3_vals} vs recomputed {got_vals}")

    print()
    print("=" * 78)
    print("SECTION 8 — cross-appendix consistency (exploratory vs registered)")
    print("=" * 78)
    # G/I (exploratory) planted alignment must equal registered C values
    irows = parse_csv(apps["I"])
    ok_gi = True
    for ir in irows:
        arch, beta = ir["architecture"], float(ir["beta"])
        ok_gi &= abs(float(ir["planted_max_positive_cosine"])
                     - cell_mean(arch, beta, "mean_factor_max_positive_cosine")) < 1e-9
        ok_gi &= abs(float(ir["split_count_rel_10"])
                     - cell_mean(arch, beta, "mean_factor_causal_split_count")) < 1e-9
    check("I/G exploratory planted-alignment & split-count agree with registered H/C",
          ok_gi)
    # G's high-minus-control planted mean should equal registered mean (means are
    # salt-free; only its CIs use different salts, which the dossier flags)
    g_l1 = re.search(r"`planted_max_positive_cosine`: ([+-][\d.]+),", apps["G"])
    check("G exploratory headline mean equals registered (-0.2553 l1)",
          abs(float(g_l1.group(1)) - headline["l1"][0]) <= 5.1e-5)
    krows = parse_csv(apps["K"])
    check("K: 120 exploratory rows with registered cell coverage",
          len(krows) == 120 and
          {(r["architecture"], int(r["seed"]), float(r["beta"])) for r in krows} == cells)
    # §7 load-bearing diagnostics vs recomputed
    ok7 = (abs(cell_mean("l1", 0.0, "l0") - 15.7147) <= 5.1e-5
           and abs(cell_mean("l1", 0.5, "l0") - 30.2113) <= 5.1e-5
           and abs(cell_mean("topk", 0.0, "dead_fraction") - 0.0331) <= 5.1e-5
           and abs(cell_mean("topk", 0.5, "dead_fraction") - 0.1814) <= 5.1e-5
           and abs(diffs[("l1", "fvu")].mean() - 0.0060) <= 5.1e-5
           and abs(diffs[("topk", "fvu")].mean() - 0.0639) <= 5.1e-5)
    check("§7 alternative-cost diagnostics match recomputation", ok7)
    # max-abs-coherence honesty: dossier admits coherence did NOT fall
    check("§7 reports max_absolute_coherence did not fall (adverse diagnostic disclosed)",
          "Maximum absolute coherence did not fall" in body
          and diffs[("l1", "max_absolute_coherence")].mean() > 0
          and diffs[("topk", "max_absolute_coherence")].mean() > 0)
    # metadata (D) consistency
    D = json.loads(apps["D"])
    check("D: metadata matches registered config & data hash",
          D["dataset"]["data_sha256"] == prereg["data_hash"]
          and D["config"]["steps"] == 10000 and D["config"]["topk_k"] == 16
          and D["config"]["l1_lambda"] == 0.2 and D["seeds"] == list(range(12))
          and D["betas"] == betas and D["steps_override"] is None
          and D["dataset"]["classifier_eval_accuracy"] >= 0.94)
    warn("D records numpy 2.3.5 / python 3.12; this audit ran numpy "
         f"{np.__version__} — bootstrap reproduction was exact regardless.")

    print()
    print("=" * 78)
    nfail = sum(1 for _, ok, _ in RESULTS if not ok)
    print(f"TOTAL: {len(RESULTS)} checks, {len(RESULTS) - nfail} PASS, {nfail} FAIL")
    print("NOT VERIFIABLE FROM THIS DOSSIER ALONE (open items):")
    print("  - decoder-level replay of the 120 binary checkpoints (files absent here);")
    print("  - preregistration temporal lock (no trusted timestamp/public commit);")
    print("  - full retraining reproduction (needs scipy+sklearn, absent in this env).")
    print("This audit does NOT rely on the dossier author's own Section 3 replay.")
    return 1 if nfail else 0


if __name__ == "__main__":
    sys.exit(main())
