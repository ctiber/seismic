"""
Sensitivity Analysis for SEISMIC Parameters (tau_m, lambda_m).

Pre-computes per-class features (Phi, bonus, omega_s) once using the
all-MiniLM-L6-v2 transformer, then sweeps the (tau_m x lambda_m) grid
with pure arithmetic — no repeated embedding calls.

Grid:
    tau_m  in {10, 15, 20, 25, 30}   (Structural Stability Threshold)
    lambda_m in {0.05, 0.08, 0.10, 0.12, 0.15}  (Decay Rate)

tau_s and lambda_s are held fixed at the paper defaults (20 and 0.03).

Usage:
    # Expert Monoliths (default):
    python sensitivity_analysis.py

    # Custom directory and output:
    python sensitivity_analysis.py --java_dir dataset2/expert_java_files --output sensitivity.csv

    # Also compare against God Classes:
    python sensitivity_analysis.py --java_dir dataset2/expert_java_files \
                                   --god_dir  dataset/god_java_files
"""

import argparse
import csv
import math
import os
import re

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# ── Helpers (mirrored from lasco.py; kept here so this script is self-contained)

def split_camel(name):
    if not name:
        return ""
    name = name.replace('.', ' ')
    return " ".join(re.sub('([a-z])([A-Z])', r'\1 \2', name).split())


def is_domain_type(type_name):
    standard = {
        'String', 'Integer', 'Double', 'Float', 'Long', 'Boolean',
        'List', 'Map', 'Set', 'int', 'double', 'float', 'void', 'boolean',
    }
    return type_name not in standard


def extract_semantic_data(code):
    """
    Returns (domain_anchor, method_data, shared_terms, all_fields).
    Raises on parse error — callers should catch.
    """
    import javalang
    # Strip package declarations with hyphens (e.g. "bookkeeper-server.src...")
    # which are invalid Java identifiers and cause javalang to fail.
    code = re.sub(r'^package\s+[^\n;]+;', '', code, count=1, flags=re.MULTILINE)
    tree = javalang.parse.parse(code)

    package_name = split_camel(tree.package.name) if tree.package else ""
    class_nodes  = [n for _, n in tree if isinstance(n, javalang.tree.ClassDeclaration)]
    if not class_nodes:
        raise ValueError("No ClassDeclaration found")
    class_name    = split_camel(class_nodes[0].name)
    domain_anchor = f"{package_name} {class_name}".strip()

    all_fields = {
        n.name for _, n in tree
        if isinstance(n, javalang.tree.VariableDeclarator)
    }

    method_data, term_usage = {}, {}
    for _, node in tree.filter(javalang.tree.MethodDeclaration):
        used_fields = [
            c.member for _, c in node.filter(javalang.tree.MemberReference)
            if c.member in all_fields
        ]
        params_info = []
        for param in node.parameters:
            params_info.append(split_camel(param.name))
            if hasattr(param.type, 'name') and is_domain_type(param.type.name):
                params_info.append(split_camel(param.type.name))
        if (hasattr(node, 'return_type') and node.return_type
                and is_domain_type(node.return_type.name)):
            params_info.append(split_camel(node.return_type.name))

        phrase_terms = (
            [split_camel(node.name)]
            + [split_camel(f) for f in used_fields]
            + params_info
        )
        unique_terms = list(set(phrase_terms))
        method_data[node.name] = {
            "terms":          unique_terms,
            "accessed_fields": set(used_fields),
        }
        for t in unique_terms:
            term_usage[t] = term_usage.get(t, 0) + 1

    shared_terms = [t for t, c in term_usage.items() if c > 1]
    return domain_anchor, method_data, shared_terms, all_fields


# ── Grid definition

TAU_M_VALUES    = [10, 15, 20, 25, 30]
LAMBDA_M_VALUES = [0.05, 0.08, 0.10, 0.12, 0.15]

# Paper defaults (shown as reference in output; lambda_m=0.02 is below the grid)
PAPER_TAU_M    = 15
PAPER_LAMBDA_M = 0.02
PAPER_TAU_S    = 20
PAPER_LAMBDA_S = 0.03


# ── Pre-computation phase

def precompute_class(file_path, model,
                     tau_s=PAPER_TAU_S, lambda_s=PAPER_LAMBDA_S):
    """
    Runs the expensive embedding step once per class.

    Returns a tuple (phi, num_methods, len_core, omega_s, bonus) where:
      phi        — Intrinsic Semantic Coherence (Φ), depends only on embeddings
      num_methods — |M|, used in omega_m computation during grid sweep
      len_core   — |Φ_core|, used to compute omega_s (fixed across grid)
      omega_s    — exp(-lambda_s * max(0, |Φ_core| - tau_s)), fixed across grid
      bonus      — Structural Integration Bonus B, fixed across grid

    Returns None on parse/analysis error.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        code = f.read()
    code = re.sub(r'^package\s+[^\n;]+;', '', code, count=1, flags=re.MULTILINE)

    domain_anchor, method_data, shared_terms, all_fields = extract_semantic_data(code)
    num_methods = len(method_data)
    if num_methods == 0:
        return None

    core_string = f"{domain_anchor} {' '.join(shared_terms)}"
    core_emb    = model.encode([core_string])

    alignments = []
    for data in method_data.values():
        m_emb  = model.encode([" ".join(data["terms"])])
        sim    = max(0.0, float(cosine_similarity(m_emb, core_emb)[0][0]))
        score  = math.sqrt(sim)
        if not any(t in shared_terms for t in data["terms"]):
            score *= 0.5          # Silo Penalty
        alignments.append(score)

    phi     = float(np.mean(alignments))
    omega_s = math.exp(-lambda_s * max(0, len(shared_terms) - tau_s))
    shared_attrs = [t for t in shared_terms if t.replace(" ", "") in all_fields]
    bonus   = min(0.15, (len(shared_attrs) / num_methods) * 0.1)

    return phi, num_methods, len(shared_terms), omega_s, bonus


def precompute_directory(java_dir, model, label=""):
    """Pre-computes features for every parseable .java file in java_dir."""
    features, errors = [], 0
    files = sorted(f for f in os.listdir(java_dir) if f.endswith('.java'))
    total = len(files)
    for i, filename in enumerate(files, 1):
        path = os.path.join(java_dir, filename)
        try:
            result = precompute_class(path, model)
            if result is not None:
                features.append(result)
        except Exception:
            errors += 1
        if i % 100 == 0 or i == total:
            print(f"  [{label}] {i}/{total} processed, {errors} skipped so far …")
    print(f"  [{label}] Done — {len(features)} classes, {errors} skipped.")
    return features


# ── Grid sweep (pure arithmetic after pre-computation)

def sweep_grid(features,
               tau_m_values=TAU_M_VALUES,
               lambda_m_values=LAMBDA_M_VALUES):
    """
    Returns a list of dicts, one per (tau_m, lambda_m) combination, containing
    mean, median, and std of final SEISMIC scores across all features.
    """
    rows = []
    for tau_m in tau_m_values:
        for lam in lambda_m_values:
            scores = []
            for phi, num_methods, _, omega_s, bonus in features:
                omega_m = math.exp(-lam * max(0, num_methods - tau_m))
                final   = min(1.0, phi * omega_m * omega_s + bonus)
                scores.append(final)
            rows.append({
                'tau_m':    tau_m,
                'lambda_m': lam,
                'mean':     round(float(np.mean(scores)),   4),
                'median':   round(float(np.median(scores)), 4),
                'std':      round(float(np.std(scores)),    4),
                'n':        len(scores),
            })
    return rows


def paper_default_scores(features):
    """Computes scores at the paper's own (tau_m=15, lambda_m=0.02) defaults."""
    scores = []
    for phi, num_methods, len_core, omega_s, bonus in features:
        omega_m = math.exp(-PAPER_LAMBDA_M * max(0, num_methods - PAPER_TAU_M))
        final   = min(1.0, phi * omega_m * omega_s + bonus)
        scores.append(final)
    return {
        'tau_m':  PAPER_TAU_M,
        'lambda_m': PAPER_LAMBDA_M,
        'mean':   round(float(np.mean(scores)),   4),
        'median': round(float(np.median(scores)), 4),
        'std':    round(float(np.std(scores)),    4),
        'n':      len(scores),
    }


# ── Console output helpers

def print_heatmap(rows, label, tau_m_values, lambda_m_values):
    col_w = 10
    header = f"{'τ_m':>5} |" + "".join(f"  λ={l:.2f}  " for l in lambda_m_values)
    sep    = "-" * len(header)
    print(f"\n{label} — Mean SEISMIC Score")
    print(header)
    print(sep)
    for tau_m in tau_m_values:
        line = f"{tau_m:>5} |"
        for lam in lambda_m_values:
            cell = next(
                r['mean'] for r in rows
                if r['tau_m'] == tau_m and abs(r['lambda_m'] - lam) < 1e-9
            )
            line += f"  {cell:.4f}  "
        print(line)
    print()


def print_gap_heatmap(expert_rows, god_rows, tau_m_values, lambda_m_values):
    """Prints the inter-group discriminative gap (Expert mean − God mean)."""
    print("Discriminative Gap (Expert Monolith mean − God Class mean)")
    header = f"{'τ_m':>5} |" + "".join(f"  λ={l:.2f}  " for l in lambda_m_values)
    print(header)
    print("-" * len(header))
    for tau_m in tau_m_values:
        line = f"{tau_m:>5} |"
        for lam in lambda_m_values:
            e = next(r['mean'] for r in expert_rows
                     if r['tau_m'] == tau_m and abs(r['lambda_m'] - lam) < 1e-9)
            g = next(r['mean'] for r in god_rows
                     if r['tau_m'] == tau_m and abs(r['lambda_m'] - lam) < 1e-9)
            gap = round(e - g, 4)
            line += f"  {gap:+.4f} "
        print(line)
    print()


# ── CSV output

def write_csv(rows, path, extra_fields=None):
    fieldnames = ['tau_m', 'lambda_m', 'mean', 'median', 'std', 'n']
    if extra_fields:
        fieldnames += extra_fields
    with open(path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Results written to '{path}'.")


# ── Log parser for existing SEISMIC result logs

def parse_log_scores(log_path, marker='Final LASCO Score:'):
    """
    Extracts all SEISMIC scores from a pre-computed .log file.
    Used when the source Java files are unavailable but a previous
    run's log exists (e.g. results_god_classes.log).
    """
    import re
    scores = []
    with open(log_path, encoding='utf-8', errors='ignore') as f:
        for line in f:
            m = re.search(r'Final LASCO Score:\s*([0-9.]+)', line)
            if m:
                try:
                    scores.append(float(m.group(1)))
                except ValueError:
                    pass
    return scores


def print_log_reference(expert_default, god_log_path):
    """
    Prints a reference gap row using paper-default scores extracted from
    an existing God Class log file, since the God Class Java files may not
    be available locally.
    """
    god_scores = parse_log_scores(god_log_path)
    if not god_scores:
        print(f"Warning: no scores found in '{god_log_path}'.")
        return

    god_mean   = round(float(np.mean(god_scores)),   4)
    god_median = round(float(np.median(god_scores)), 4)
    god_std    = round(float(np.std(god_scores)),    4)

    gap_mean   = round(expert_default['mean']   - god_mean,   4)
    gap_median = round(expert_default['median'] - god_median, 4)

    print(f"\nReference gap at paper defaults "
          f"(τ_m={PAPER_TAU_M}, λ_m={PAPER_LAMBDA_M}):")
    print(f"  {'Metric':10s}  {'Mean':>8}  {'Median':>8}  {'Std':>8}  {'N':>6}")
    print(f"  {'-'*50}")
    print(f"  {'Expert':10s}  {expert_default['mean']:>8.4f}  "
          f"{expert_default['median']:>8.4f}  {expert_default['std']:>8.4f}  "
          f"{expert_default['n']:>6}")
    print(f"  {'God Class':10s}  {god_mean:>8.4f}  "
          f"{god_median:>8.4f}  {god_std:>8.4f}  {len(god_scores):>6}")
    print(f"  {'Gap':10s}  {gap_mean:>+8.4f}  {gap_median:>+8.4f}")
    print(f"\n  Note: full grid gap analysis requires God Class .java files "
          f"(--god_dir).\n  The log-based reference above uses paper defaults only.")


# ── Entry point

def main():
    parser = argparse.ArgumentParser(
        description="Sensitivity analysis for SEISMIC (tau_m, lambda_m) grid."
    )
    parser.add_argument(
        '--java_dir', default='dataset2/expert_java_files',
        help='Directory of .java files (primary group, e.g. Expert Monoliths)',
    )
    parser.add_argument(
        '--god_dir', default=None,
        help='Optional: directory of God Class .java files for full grid gap analysis',
    )
    parser.add_argument(
        '--god_log', default='results_god_classes.log',
        help='Existing God Class log file for reference gap at paper defaults '
             '(used when --god_dir is unavailable; default: results_god_classes.log)',
    )
    parser.add_argument(
        '--output', default='sensitivity_results.csv',
        help='Output CSV file for the grid results',
    )
    parser.add_argument(
        '--god_output', default='sensitivity_god_results.csv',
        help='Output CSV file for the God Class grid results (if --god_dir supplied)',
    )
    args = parser.parse_args()

    print("Loading transformer model (all-MiniLM-L6-v2) …")
    model = SentenceTransformer('all-MiniLM-L6-v2')

    # ── Pre-compute expert / primary group
    print(f"\nPre-computing embeddings for '{args.java_dir}' …")
    expert_features = precompute_directory(args.java_dir, model, label="Expert")

    expert_default = paper_default_scores(expert_features)
    print(f"\nPaper defaults (τ_m={PAPER_TAU_M}, λ_m={PAPER_LAMBDA_M}) on this set:")
    print(f"  mean={expert_default['mean']:.4f}  "
          f"median={expert_default['median']:.4f}  "
          f"std={expert_default['std']:.4f}  n={expert_default['n']}")

    print("\nRunning grid sweep …")
    expert_rows = sweep_grid(expert_features)
    print_heatmap(expert_rows, "Expert Monoliths", TAU_M_VALUES, LAMBDA_M_VALUES)
    write_csv(expert_rows, args.output)

    # ── God Class comparison: full grid if Java files available,
    #    otherwise reference gap from existing log
    if args.god_dir and os.path.isdir(args.god_dir):
        print(f"\nPre-computing embeddings for '{args.god_dir}' …")
        god_features = precompute_directory(args.god_dir, model, label="God")
        god_rows     = sweep_grid(god_features)
        print_heatmap(god_rows, "General God Classes", TAU_M_VALUES, LAMBDA_M_VALUES)
        print_gap_heatmap(expert_rows, god_rows, TAU_M_VALUES, LAMBDA_M_VALUES)
        write_csv(god_rows, args.god_output)
    elif os.path.isfile(args.god_log):
        print_log_reference(expert_default, args.god_log)
    else:
        print(f"\nNo God Class source available "
              f"(--god_dir not found, --god_log '{args.god_log}' not found). "
              f"Skipping gap analysis.")

    print("\nDone.")
    print(f"Note: paper defaults (τ_m={PAPER_TAU_M}, λ_m={PAPER_LAMBDA_M}) are "
          "below the swept lambda range and shown above as a reference baseline.")


if __name__ == '__main__':
    main()
