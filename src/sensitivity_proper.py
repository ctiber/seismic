"""
Proper sensitivity analysis for SEISMIC (tau_m, lambda_m).

Uses pre-computed phi and bonus from smellycodepp_results.csv, then
re-extracts n_methods and n_shared_terms from the Java source files via
javalang (no transformer re-run). This ensures the sensitivity grid uses
the exact same phi values as the main RQ1/RQ2 results.

Grid:
    tau_m    in {10, 15, 20, 25, 30}
    lambda_m in {0.003, 0.005, 0.010, 0.100, 0.150}

tau_s and lambda_s are held fixed at paper defaults (20 and 0.03).
"""

import csv
import math
import os
import re
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from seismic import extract_semantic_data

TAU_M_VALUES    = [10, 15, 20, 25, 30]
LAMBDA_M_VALUES = [0.003, 0.005, 0.010, 0.100, 0.150]
TAU_S    = 20
LAMBDA_S = 0.03

BASE = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR   = os.path.join(BASE, '..', 'dataset', 'smellycodepp')
RESULTS_CSV   = os.path.join(BASE, '..', 'results', 'smellycodepp_results.csv')


# ── Structural extraction using full SEISMIC phrase extraction ────────────────

def extract_structural_counts(file_path):
    """Returns (n_methods, n_shared_terms) using the full SEISMIC phrase
    extraction (including body symbols) — no transformer needed."""
    try:
        with open(file_path, encoding='utf-8', errors='replace') as fh:
            code = fh.read()
        _, method_data, shared_terms, _ = extract_semantic_data(code)
        return len(method_data), len(shared_terms)
    except Exception:
        return None, None


# ── Load pre-computed phi/bonus ───────────────────────────────────────────────

def load_results(results_csv, group):
    """Returns list of (filename, phi, bonus) for the given group."""
    rows = []
    with open(results_csv, encoding='utf-8') as fh:
        for row in csv.DictReader(fh):
            if row.get('group') != group:
                continue
            if row.get('parse_ok', '').lower() != 'true':
                continue
            try:
                rows.append((row['file'], float(row['phi']), float(row['bonus'])))
            except (ValueError, KeyError):
                pass
    return rows


# ── Build feature list for a group ───────────────────────────────────────────

def build_features(group, results_csv, dataset_dir):
    """
    Returns list of (phi, bonus, n_methods, n_shared_terms) for each class
    where Java source is parseable.
    """
    group_dir_map = {'expert': 'expert_monoliths', 'god': 'god_classes', 'normal': 'normal_classes'}
    java_dir = os.path.join(dataset_dir, group_dir_map[group])
    entries  = load_results(results_csv, group)
    features = []
    errors   = 0
    total    = len(entries)

    for i, (filename, phi, bonus) in enumerate(entries, 1):
        java_path = os.path.join(java_dir, filename)
        if not os.path.isfile(java_path):
            errors += 1
            continue
        nm, ns = extract_structural_counts(java_path)
        if nm is None:
            errors += 1
            continue
        features.append((phi, bonus, nm, ns))
        if i % 200 == 0 or i == total:
            print(f"  [{group}] {i}/{total} processed, {errors} missing/failed …")

    print(f"  [{group}] Done — {len(features)} classes, {errors} skipped.")
    return features


# ── Grid sweep ────────────────────────────────────────────────────────────────

def sweep(features, tau_m_values=TAU_M_VALUES, lambda_m_values=LAMBDA_M_VALUES):
    rows = []
    for tau_m in tau_m_values:
        for lam in lambda_m_values:
            scores = []
            for phi, bonus, nm, ns in features:
                omega_m = math.exp(-lam * max(0, nm - tau_m))
                omega_s = math.exp(-LAMBDA_S * max(0, ns - TAU_S))
                s = min(1.0, phi * omega_m * omega_s + bonus)
                scores.append(s)
            rows.append({
                'tau_m':    tau_m,
                'lambda_m': lam,
                'mean':     round(float(np.mean(scores)),   4),
                'median':   round(float(np.median(scores)), 4),
                'std':      round(float(np.std(scores)),    4),
                'n':        len(scores),
            })
    return rows


def write_csv(rows, path):
    with open(path, 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=['tau_m','lambda_m','mean','median','std','n'])
        w.writeheader()
        w.writerows(rows)
    print(f"Saved: {path}")


def print_grid(rows, label, tau_m_values, lambda_m_values):
    header = f"{'τ_m':>5} |" + "".join(f"  λ={l:.3f} " for l in lambda_m_values)
    print(f"\n{label} — Mean SEISMIC Score")
    print(header)
    print("-" * len(header))
    for tau_m in tau_m_values:
        line = f"{tau_m:>5} |"
        for lam in lambda_m_values:
            cell = next(r['mean'] for r in rows
                        if r['tau_m'] == tau_m and abs(r['lambda_m'] - lam) < 1e-9)
            line += f"  {cell:.4f} "
        print(line)


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    print("Building Expert Monolith features (javalang only, no transformer) …")
    expert_features = build_features('expert', RESULTS_CSV, DATASET_DIR)

    print("\nBuilding God Class features …")
    god_features = build_features('god', RESULTS_CSV, DATASET_DIR)

    expert_rows = sweep(expert_features)
    god_rows    = sweep(god_features)

    print_grid(expert_rows, "Expert Monoliths", TAU_M_VALUES, LAMBDA_M_VALUES)
    print_grid(god_rows,    "God Classes",      TAU_M_VALUES, LAMBDA_M_VALUES)

    # Discriminative gap
    print(f"\nDiscriminative Gap (Expert − God)")
    header = f"{'τ_m':>5} |" + "".join(f"  λ={l:.3f} " for l in LAMBDA_M_VALUES)
    print(header)
    print("-" * len(header))
    for tau_m in TAU_M_VALUES:
        line = f"{tau_m:>5} |"
        for lam in LAMBDA_M_VALUES:
            e = next(r['mean'] for r in expert_rows
                     if r['tau_m'] == tau_m and abs(r['lambda_m'] - lam) < 1e-9)
            g = next(r['mean'] for r in god_rows
                     if r['tau_m'] == tau_m and abs(r['lambda_m'] - lam) < 1e-9)
            line += f"  {e-g:+.4f}"
        print(line)

    out_dir = os.path.join(BASE, '..', 'results')
    write_csv(expert_rows, os.path.join(out_dir, 'sensitivity_expert.csv'))
    write_csv(god_rows,    os.path.join(out_dir, 'sensitivity_god.csv'))
    print("\nDone.")


if __name__ == '__main__':
    main()