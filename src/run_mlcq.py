"""
MLCQ Experiment: SEISMIC Evaluation on Developer-Validated God Class Oracle
============================================================================
Runs SEISMIC on all Java files produced by mlcq_prepare.py, writes a scored
results CSV, and prints a distribution summary with AUC / AP statistics.

Usage:
    python mlcq_experiment.py [options]

Options:
    --meta    PATH   metadata.csv from mlcq_prepare.py  (default: dataset/mlcq/metadata.csv)
    --out     DIR    output directory for results        (default: dataset/mlcq)
    --model   NAME   sentence-transformer model          (default: all-MiniLM-L6-v2)
    --resume         skip files already present in results.csv

Output:
    dataset/mlcq/results.csv     — one row per file: file, label, severity,
                                   seismic_score, phi, omega, bonus, parse_ok
    Printed: mean/median/std per group, Mann-Whitney U, Cliff's delta, AUC, AP
"""

import argparse
import math
import os
import sys
import warnings

import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer

warnings.filterwarnings("ignore")

# ---------------------------------------------------------------------------
# Lazy import of seismic internals (avoids the __main__ block executing)
# ---------------------------------------------------------------------------
sys.path.insert(0, os.path.dirname(__file__))
from seismic import extract_semantic_data
from sklearn.metrics.pairwise import cosine_similarity


def _score_file(file_path: str, model: SentenceTransformer) -> dict:
    """
    Compute SEISMIC sub-scores for a single Java file.
    Returns a dict with keys: seismic, phi, omega, bonus, parse_ok.
    """
    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as fh:
            code = fh.read()
        domain_anchor, method_data, shared_terms, all_fields = extract_semantic_data(code)
    except Exception as e:
        return {"seismic": 0.0, "phi": 0.0, "omega": 0.0, "bonus": 0.0,
                "parse_ok": False, "error": str(e)[:120]}

    num_methods = len(method_data)
    if num_methods == 0:
        return {"seismic": 0.0, "phi": 0.0, "omega": 1.0, "bonus": 0.0,
                "parse_ok": True, "error": "no methods"}

    core_string = f"{domain_anchor} {' '.join(shared_terms)}"
    core_emb = model.encode([core_string])

    alignments = []
    for data in method_data.values():
        m_emb = model.encode([" ".join(data["terms"])])
        sim = max(0.0, float(cosine_similarity(m_emb, core_emb)[0][0]))
        score = math.sqrt(sim)
        if not any(t in shared_terms for t in data["terms"]):
            score *= 0.5
        alignments.append(score)

    phi   = float(np.mean(alignments))
    omega = (math.exp(-0.005 * max(0, num_methods - 15)) *
             math.exp(-0.030 * max(0, len(shared_terms) - 20)))
    shared_attrs = [t for t in shared_terms if t.replace(" ", "") in all_fields]
    bonus = min(0.15, (len(shared_attrs) / num_methods) * 0.1)
    final = min(1.0, phi * omega + bonus)

    return {"seismic": round(final, 4), "phi": round(phi, 4),
            "omega": round(omega, 4), "bonus": round(bonus, 4),
            "parse_ok": True, "error": ""}


# ---------------------------------------------------------------------------
# Statistics helpers
# ---------------------------------------------------------------------------

def _mannwhitney(a, b):
    from scipy.stats import mannwhitneyu
    stat, p = mannwhitneyu(a, b, alternative="two-sided")
    return stat, p


def _cliffs_delta(a, b):
    a, b = np.asarray(a), np.asarray(b)
    greater = np.sum(a[:, None] > b[None, :])
    less    = np.sum(a[:, None] < b[None, :])
    return (greater - less) / (len(a) * len(b))


def _auc_ap(scores_god, scores_normal):
    """
    Binary God Class detection: god=1, normal=0.
    AUC and AP are both orientation-corrected: if SEISMIC assigns lower scores
    to God Classes on average (inverted orientation), scores are negated before
    computing AP so that higher predicted score always means 'more likely God Class'.
    """
    from sklearn.metrics import roc_auc_score, average_precision_score
    y_true  = [1] * len(scores_god)  + [0] * len(scores_normal)
    y_score = list(scores_god) + list(scores_normal)
    auc = roc_auc_score(y_true, y_score)
    # If raw AUC < 0.5 scores are inverted — negate for consistent orientation
    if auc < 0.5:
        auc     = 1.0 - auc
        y_score = [-s for s in y_score]   # flip so high score = God Class
    ap = average_precision_score(y_true, y_score)
    return auc, ap


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run(meta_path: str, out_dir: str, model_name: str, resume: bool) -> None:
    meta = pd.read_csv(meta_path)
    print(f"Loaded {len(meta)} entries from {meta_path}")

    results_path = os.path.join(out_dir, "results.csv")
    already_done: set = set()
    if resume and os.path.exists(results_path):
        prev = pd.read_csv(results_path)
        already_done = set(prev["file"])
        print(f"Resuming: {len(already_done)} files already scored.")

    print(f"Loading SentenceTransformer '{model_name}' …")
    model = SentenceTransformer(model_name)

    rows = []
    total = len(meta)
    for i, (_, row) in enumerate(meta.iterrows()):
        fname = row["file"]
        if fname in already_done:
            continue
        label   = row["label"]
        subdir  = "god_classes" if label == "god_class" else "normal_classes"
        fpath   = os.path.join(out_dir, subdir, fname)

        if not os.path.exists(fpath):
            print(f"  [{i+1}/{total}] MISSING: {fname}")
            continue

        scores = _score_file(fpath, model)
        rows.append({
            "file":        fname,
            "label":       label,
            "severity":    row.get("severity", ""),
            "code_name":   row.get("code_name", ""),
            "seismic":     scores["seismic"],
            "phi":         scores["phi"],
            "omega":       scores["omega"],
            "bonus":       scores["bonus"],
            "parse_ok":    scores["parse_ok"],
            "error":       scores.get("error", ""),
        })

        if (i + 1) % 50 == 0 or i + 1 == total:
            print(f"  [{i+1}/{total}]  {fname}  seismic={scores['seismic']:.4f}"
                  f"  ({'OK' if scores['parse_ok'] else 'PARSE_ERR'})")

    # Merge with any previous results if resuming
    if resume and already_done:
        prev_rows = pd.read_csv(results_path).to_dict("records")
        rows = prev_rows + rows

    results_df = pd.DataFrame(rows)
    results_df.to_csv(results_path, index=False)
    print(f"\nResults saved to {results_path}  ({len(results_df)} rows)\n")

    # --- Analysis ---
    ok = results_df[results_df["parse_ok"] == True].copy()
    god    = ok[ok["label"] == "god_class"]["seismic"].values
    normal = ok[ok["label"] == "normal"]["seismic"].values

    if len(god) == 0 or len(normal) == 0:
        print("Not enough data for statistics.")
        return

    # Method count for size-stratified analysis
    def _count_methods(row):
        subdir = "god_classes" if row["label"] == "god_class" else "normal_classes"
        fpath  = os.path.join(out_dir, subdir, row["file"])
        try:
            import javalang
            code = open(fpath, encoding="utf-8", errors="replace").read()
            tree = javalang.parse.parse(code)
            return sum(1 for _, n in tree.filter(javalang.tree.MethodDeclaration))
        except Exception:
            return -1

    print("Computing method counts for size-stratified analysis …")
    ok["n_methods"] = ok.apply(_count_methods, axis=1)
    ok = ok[ok["n_methods"] >= 0]

    def _mag(d):
        return ("negligible" if abs(d) < 0.147 else
                "small"      if abs(d) < 0.33  else
                "medium"     if abs(d) < 0.474 else "large")

    def _report(god_arr, norm_arr, label=""):
        noskill = len(god_arr) / (len(god_arr) + len(norm_arr))
        stat, p = _mannwhitney(god_arr, norm_arr)
        delta   = _cliffs_delta(god_arr, norm_arr)
        auc, ap = _auc_ap(god_arr, norm_arr)
        print(f"  n_god={len(god_arr)}, n_norm={len(norm_arr)}")
        print(f"  God  mean={np.mean(god_arr):.4f}  median={np.median(god_arr):.4f}  std={np.std(god_arr):.4f}")
        print(f"  Norm mean={np.mean(norm_arr):.4f}  median={np.median(norm_arr):.4f}  std={np.std(norm_arr):.4f}")
        print(f"  Mann-Whitney: W={stat:.0f}, p={p:.3e}")
        print(f"  Cliff's δ   : {delta:+.3f}  ({_mag(delta)})")
        print(f"  AUC         : {auc:.3f}")
        print(f"  AP          : {ap:.3f}  (no-skill = {noskill:.3f})")

    print()
    print("=" * 65)
    print("SEISMIC — MLCQ Oracle (developer-validated God Class labels)")
    print("=" * 65)

    # Parse-error summary
    n_err_god  = (results_df["label"] == "god_class").sum() - len(god)
    n_err_norm = (results_df["label"] == "normal").sum() - len(normal)
    print(f"Parse errors: God={n_err_god}/{(results_df['label']=='god_class').sum()}, "
          f"Normal={n_err_norm}/{(results_df['label']=='normal').sum()}")
    print()

    print("── Full comparison (all Normal classes) ──")
    god_ok    = ok[ok["label"] == "god_class"]["seismic"].values
    norm_all  = ok[ok["label"] == "normal"]["seismic"].values
    _report(god_ok, norm_all)
    print()

    print("── Size-matched: Normal ≥ 15 methods (comparable to God Class median) ──")
    norm_large = ok[(ok["label"] == "normal") & (ok["n_methods"] >= 15)]["seismic"].values
    if len(norm_large) > 0:
        _report(god_ok, norm_large)
    else:
        print("  (not enough large Normal samples)")
    print()

    # Tier breakdown
    tiers = [("Functional Integrity (≥0.70)",  0.70, 1.01),
             ("Functional Breadth  (0.50–0.69)", 0.50, 0.70),
             ("SSI / Inflationary  (0.25–0.49)", 0.25, 0.50),
             ("Arch. Collapse      (<0.25)",      0.00, 0.25)]
    print(f"{'Tier':<38}  {'God%':>6}  {'Norm%':>6}  {'NormL%':>7}")
    print("-" * 56)
    for name, lo, hi in tiers:
        g  = ((god_ok     >= lo) & (god_ok     < hi)).mean() * 100
        n  = ((norm_all   >= lo) & (norm_all   < hi)).mean() * 100
        nl = ((norm_large >= lo) & (norm_large < hi)).mean() * 100 if len(norm_large) else float("nan")
        print(f"{name:<38}  {g:>5.1f}%  {n:>5.1f}%  {nl:>6.1f}%")
    print("=" * 65)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run SEISMIC on MLCQ files and report results."
    )
    _here = os.path.dirname(os.path.abspath(__file__))
    parser.add_argument("--meta",  default=os.path.join(_here, "..", "dataset", "mlcq", "metadata.csv"))
    parser.add_argument("--out",   default=os.path.join(_here, "..", "dataset", "mlcq"))
    parser.add_argument("--model", default="all-MiniLM-L6-v2")
    parser.add_argument("--resume", action="store_true",
                        help="Skip files already present in results.csv")
    args = parser.parse_args()

    run(args.meta, args.out, args.model, args.resume)
