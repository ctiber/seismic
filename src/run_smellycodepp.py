"""
SmellyCode++ Re-run Script.

Computes SEISMIC scores for all three groups (Expert Monoliths, God Classes,
Normal Classes) using the calibrated seismic.py (lambda_m=0.005).

Usage:
    python rerun_smellycodepp.py \
        --expert   /path/to/expert_monolith_java_files/ \
        --god      /path/to/god_classes_java_files/ \
        --normal   /path/to/sample_ng_classes/ \
        --out      smellycodepp_results.csv

Output:
    smellycodepp_results.csv   — one row per file (file, group, seismic, phi, omega, bonus)
    Printed: three-group descriptive stats + pairwise Mann-Whitney + Cliff's delta
"""

import argparse
import math
import os
import sys
import warnings

import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from scipy import stats

warnings.filterwarnings("ignore")

sys.path.insert(0, os.path.dirname(__file__))
from seismic import extract_semantic_data

TAU_M, LAMBDA_M = 15, 0.005   # calibrated
TAU_S, LAMBDA_S = 20, 0.030


# ── Score one file ──────────────────────────────────────────────────────────────

def score_file(file_path: str, model) -> dict:
    try:
        with open(file_path, encoding="utf-8", errors="replace") as fh:
            code = fh.read()
        domain_anchor, method_data, shared_terms, all_fields = extract_semantic_data(code)
    except Exception as e:
        return {"seismic": 0.0, "phi": 0.0, "omega": 0.0, "bonus": 0.0,
                "parse_ok": False, "error": str(e)[:120]}

    n_m = len(method_data)
    if n_m == 0:
        return {"seismic": 0.0, "phi": 0.0, "omega": 1.0, "bonus": 0.0,
                "parse_ok": True, "error": "no methods"}

    core_string = f"{domain_anchor} {' '.join(shared_terms)}"
    method_strings = [" ".join(data["terms"]) for data in method_data.values()]
    all_strings = [core_string] + method_strings
    all_embs = model.encode(all_strings, batch_size=64, show_progress_bar=False)
    core_emb = all_embs[0:1]
    method_embs = all_embs[1:]

    alignments = []
    for emb, data in zip(method_embs, method_data.values()):
        sim   = max(0.0, float(cosine_similarity(emb.reshape(1, -1), core_emb)[0][0]))
        score = math.sqrt(sim)
        if not any(t in shared_terms for t in data["terms"]):
            score *= 0.5
        alignments.append(score)

    phi    = float(np.mean(alignments))
    omega  = (math.exp(-LAMBDA_M * max(0, n_m         - TAU_M)) *
              math.exp(-LAMBDA_S * max(0, len(shared_terms) - TAU_S)))
    shared_attrs = [t for t in shared_terms if t.replace(" ", "") in all_fields]
    bonus  = min(0.15, (len(shared_attrs) / n_m) * 0.1)
    seismic = min(1.0, phi * omega + bonus)

    return {"seismic": round(seismic, 4), "phi": round(phi, 4),
            "omega": round(omega, 4), "bonus": round(bonus, 4),
            "parse_ok": True, "error": ""}


# ── Stats helpers ───────────────────────────────────────────────────────────────

def cliffs_delta(a, b):
    a, b = np.asarray(a), np.asarray(b)
    return float(np.sum(a[:, None] > b[None, :]) - np.sum(a[:, None] < b[None, :])) / (len(a) * len(b))

def effect_label(d):
    a = abs(d)
    if a < 0.147: return "negligible"
    if a < 0.330: return "small"
    if a < 0.474: return "medium"
    return "large"


# ── Score a directory ───────────────────────────────────────────────────────────

def score_directory(directory: str, group: str, model, limit: int = None) -> list:
    files = sorted(f for f in os.listdir(directory) if f.endswith(".java"))
    if limit:
        files = files[:limit]
    rows = []
    for i, fname in enumerate(files):
        fpath = os.path.join(directory, fname)
        s = score_file(fpath, model)
        rows.append({"file": fname, "group": group, **s})
        if (i + 1) % 100 == 0 or i + 1 == len(files):
            print(f"  [{group}] {i+1}/{len(files)} — {fname}  seismic={s['seismic']:.4f}", flush=True)
    return rows


# ── Main ────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--expert",  required=True, help="Directory of Expert Monolith .java files")
    parser.add_argument("--god",     required=True, help="Directory of God Class .java files")
    parser.add_argument("--normal",  required=True, help="Directory of Normal Class .java files")
    parser.add_argument("--out",     default="smellycodepp_results.csv")
    parser.add_argument("--model",   default="all-MiniLM-L6-v2")
    parser.add_argument("--limit",   type=int, default=None, help="Max files per group (for testing)")
    args = parser.parse_args()

    print(f"Loading SentenceTransformer '{args.model}' …")
    model = SentenceTransformer(args.model)

    all_rows = []
    for grp, path in [("expert", args.expert), ("god", args.god), ("normal", args.normal)]:
        print(f"\nScoring {grp} from {path}")
        rows = score_directory(path, grp, model, args.limit)
        all_rows.extend(rows)

    df = pd.DataFrame(all_rows)
    df.to_csv(args.out, index=False)
    print(f"\nResults saved to {args.out}")

    # ── Three-group stats ────────────────────────────────────────────────────
    ok = df[df["parse_ok"] == True]
    expert = ok[ok["group"] == "expert"]["seismic"].values
    god    = ok[ok["group"] == "god"   ]["seismic"].values
    normal = ok[ok["group"] == "normal"]["seismic"].values

    print(f"\n{'='*75}")
    print(f"SEISMIC Three-Group Statistics  (λ_m={LAMBDA_M}, λ_s={LAMBDA_S})")
    print(f"{'='*75}")
    for lbl, arr in [("Expert Monoliths", expert), ("God Classes", god), ("Normal Classes", normal)]:
        print(f"  {lbl:<22} n={len(arr):5d}  mean={np.mean(arr):.4f}  "
              f"median={np.median(arr):.4f}  std={np.std(arr):.4f}")

    print(f"\n{'Comparison':<25}  {'p-value':>12}  {'Sig?':>5}  {'δ':>8}  Effect")
    print("-"*65)
    for (la, a), (lb, b) in [
        (("Expert", expert), ("God",    god)),
        (("Expert", expert), ("Normal", normal)),
        (("God",    god),    ("Normal", normal)),
    ]:
        if len(a) < 2 or len(b) < 2:
            continue
        _, p = stats.mannwhitneyu(a, b, alternative="two-sided")
        d    = cliffs_delta(a, b)
        sig  = "YES" if p < 0.05 else "NO"
        print(f"  {la} vs {lb:<16}  {p:>12.4g}  {sig:>5}  {d:>+8.3f}  {effect_label(d)}")
    print(f"{'='*75}")


if __name__ == "__main__":
    main()
