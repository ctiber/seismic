"""
MLCQ Full Baseline Comparison: all 7 baselines vs SEISMIC.

Merges baselines_ext_god.csv + baselines_ext_normal.csv with SEISMIC results,
counts methods per file for size-matched filtering (≥15 methods), then runs
Mann-Whitney U, Cliff's delta, AUC, and Average Precision for each metric.

Outputs a LaTeX table row for each metric (full corpus + size-matched).

Usage:
    cd artifacts/
    python mlcq_fullbaselines.py
"""

import os
import re
import warnings
import argparse

import numpy as np
import pandas as pd
import javalang
from scipy import stats
from sklearn.metrics import roc_auc_score, average_precision_score

warnings.filterwarnings("ignore")

BASE = os.path.dirname(os.path.abspath(__file__))
MLCQ_DIR = os.path.join(BASE, "..", "dataset", "mlcq")


# ── Method counter ─────────────────────────────────────────────────────────────

def count_methods(file_path: str) -> int | None:
    try:
        with open(file_path, encoding="utf-8", errors="replace") as f:
            code = f.read()
        code = re.sub(r'^package\s+[^\n;]+;', '', code, count=1, flags=re.MULTILINE)
        tree = javalang.parse.parse(code)
        for _, cls in tree.filter(javalang.tree.ClassDeclaration):
            return len(cls.methods) + len(cls.constructors)
    except Exception:
        return None


# ── Effect sizes & stats ───────────────────────────────────────────────────────

def cliffs_delta(x, y):
    x, y = np.array(x), np.array(y)
    greater = np.sum(x[:, None] > y[None, :])
    less    = np.sum(x[:, None] < y[None, :])
    return float(greater - less) / (len(x) * len(y))


def interpret_delta(d):
    a = abs(d)
    if a < 0.147: return "negl."
    if a < 0.330: return "small"
    if a < 0.474: return "medium"
    return "large"


def mann_whitney(x, y):
    _, p = stats.mannwhitneyu(x, y, alternative="two-sided")
    return p


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--min_methods", type=int, default=15,
                        help="Minimum methods for size-matched normal classes")
    parser.add_argument("--out", default=os.path.join(MLCQ_DIR, "mlcq_fullbaselines.csv"))
    args = parser.parse_args()

    # 1. Load baselines (convert "ERROR" strings to NaN)
    god_bl  = pd.read_csv(os.path.join(MLCQ_DIR, "baselines_ext_god.csv"), na_values=["ERROR"])
    norm_bl = pd.read_csv(os.path.join(MLCQ_DIR, "baselines_ext_normal.csv"), na_values=["ERROR"])
    god_bl["label"]  = "god_class"
    norm_bl["label"] = "normal_class"
    baselines = pd.concat([god_bl, norm_bl], ignore_index=True)

    # 2. Load SEISMIC results; normalise label ("normal" -> "normal_class")
    seismic = pd.read_csv(os.path.join(MLCQ_DIR, "results.csv"),
                          usecols=["file", "label", "seismic", "parse_ok"])
    seismic = seismic[seismic["parse_ok"] == True].copy()
    seismic["label"] = seismic["label"].replace({"normal": "normal_class"})

    # 3. Merge on filename
    df = pd.merge(seismic[["file", "label", "seismic"]],
                  baselines.drop(columns=["label"]),
                  on="file", how="inner")

    print(f"Merged: {len(df)} files ({(df.label=='god_class').sum()} god, "
          f"{(df.label=='normal_class').sum()} normal)")

    # 4. Count methods for size filtering
    print("Counting methods for size filter...")
    method_counts = {}
    for _, row in df.iterrows():
        fname = row["file"]
        label = row["label"]
        subdir = "god_classes" if label == "god_class" else "normal_classes"
        fpath = os.path.join(MLCQ_DIR, subdir, fname)
        n = count_methods(fpath)
        method_counts[fname] = n

    df["n_methods"] = df["file"].map(method_counts)

    # 5. Size-matched subset: all god classes + normal classes with ≥ min_methods methods
    df_full = df.copy()
    df_size = df[
        (df["label"] == "god_class") |
        ((df["label"] == "normal_class") & (df["n_methods"] >= args.min_methods))
    ].copy()

    n_god_full  = (df_full["label"] == "god_class").sum()
    n_norm_full = (df_full["label"] == "normal_class").sum()
    n_god_size  = (df_size["label"] == "god_class").sum()
    n_norm_size = (df_size["label"] == "normal_class").sum()

    print(f"\nFull corpus:      {n_god_full} god, {n_norm_full} normal")
    print(f"Size-matched:     {n_god_size} god, {n_norm_size} normal (≥{args.min_methods} methods)")

    # 6. Metrics to evaluate
    metrics = ["seismic", "LCOM4", "TCC", "C3", "LSCC", "LDA_CS", "C3_FULL", "WSS"]
    label_binary = (df_size["label"] == "god_class").astype(int)
    label_binary_full = (df_full["label"] == "god_class").astype(int)

    results = []
    print("\n" + "="*105)
    print(f"{'Metric':<10} {'AUC_f':>8} {'d_f':>8} {'AUC_s':>8} {'p_size':>12} {'d_size':>8}           {'AP_size':>8}")
    print("="*105)

    for m in metrics:
        col = df_full[m].dropna()
        if len(col) == 0:
            continue

        # Full corpus
        god_f   = df_full.loc[df_full["label"] == "god_class", m].dropna()
        norm_f  = df_full.loc[df_full["label"] == "normal_class", m].dropna()

        # Size-matched
        god_s  = df_size.loc[df_size["label"] == "god_class", m].dropna()
        norm_s = df_size.loc[df_size["label"] == "normal_class", m].dropna()

        # Full corpus stats
        valid_full = df_full[m].notna()
        auc_full = roc_auc_score(label_binary_full[valid_full.values],
                                  df_full.loc[valid_full, m]) if len(god_f) > 0 else float("nan")
        ap_full  = average_precision_score(label_binary_full[valid_full.values],
                                            df_full.loc[valid_full, m]) if len(god_f) > 0 else float("nan")
        d_full   = cliffs_delta(god_f.values, norm_f.values) if len(god_f) > 0 and len(norm_f) > 0 else float("nan")

        # Size-matched stats
        valid_size = df_size[m].notna()
        auc_size = roc_auc_score(label_binary[valid_size.values],
                                   df_size.loc[valid_size, m]) if len(god_s) > 0 else float("nan")
        ap_size  = average_precision_score(label_binary[valid_size.values],
                                             df_size.loc[valid_size, m]) if len(god_s) > 0 else float("nan")

        p_size   = mann_whitney(god_s.values, norm_s.values) if len(god_s) > 0 and len(norm_s) > 0 else float("nan")
        d_size   = cliffs_delta(god_s.values, norm_s.values) if len(god_s) > 0 and len(norm_s) > 0 else float("nan")

        row = dict(metric=m, n_god_full=len(god_f), n_norm_full=len(norm_f),
                   n_god_size=len(god_s), n_norm_size=len(norm_s),
                   auc_full=auc_full, delta_full=d_full,
                   auc_size=auc_size, p_size=p_size, delta_size=d_size,
                   ap_full=ap_full, ap_size=ap_size)
        results.append(row)

        print(f"{m:<10} {auc_full:>8.3f} {d_full:>+8.3f} {auc_size:>8.3f} {p_size:>12.4g} "
              f"{d_size:>+8.3f} ({interpret_delta(d_size)})  {ap_size:>8.3f}")

    # No-skill AP
    noskill_full = n_god_full / (n_god_full + n_norm_full)
    noskill_size = n_god_size / (n_god_size + n_norm_size)
    print(f"{'No-skill':<10} {'---':>8} {'---':>8} {'---':>8} {'---':>12} {'---':>8}           {noskill_size:>8.3f}")
    print("="*105)
    print(f"\nNo-skill AP (full) = {noskill_full:.3f}   No-skill AP (size-matched) = {noskill_size:.3f}")

    # 7. LaTeX table rows (size-matched, for the paper)
    print("\n\n--- LaTeX rows (size-matched) ---")
    res_df = pd.DataFrame(results)
    for _, r in res_df.iterrows():
        d_str = f"${r['delta_size']:+.3f}$ ({interpret_delta(r['delta_size'])})"
        p_str = f"${r['p_size']:.3g}$"
        print(f"{r['metric']:<10} & {r['auc_size']:.3f} & {p_str} & {d_str} & {r['ap_size']:.3f} \\\\")

    # 8. Save full results
    pd.DataFrame(results).to_csv(args.out, index=False)
    print(f"\nFull results saved to {args.out}")


if __name__ == "__main__":
    main()
