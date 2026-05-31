"""
Statistical Validation: SEISMIC vs Baseline Metrics.

Two test batteries:

A. PAIRED comparison (same Expert Monolith classes):
   - Wilcoxon signed-rank test (non-parametric paired test)
     H0: distribution of (SEISMIC_i - Baseline_i) is symmetric around 0
   - Paired Cliff's delta (effect size)
     |d| < 0.147 negligible | 0.147-0.33 small | 0.33-0.474 medium | > 0.474 large
   - Bonferroni correction: alpha = 0.05 / num_tests

B. INDEPENDENT comparison (Expert Monoliths vs God Classes on SEISMIC):
   - Mann-Whitney U test
   - Cliff's delta (unpaired)

Usage:
    python statistical_tests.py
    python statistical_tests.py \\
        --seismic_log   results_expert_god_classes.log \\
        --baselines_csv baselines_extended_expert.csv  \\
        --god_log       results_god_classes.log        \\
        --output        statistical_tests_results.csv
"""

import argparse
import csv
import os
import re

import numpy as np
from scipy import stats

BASELINES = ['LCOM4', 'TCC', 'C3', 'LSCC', 'LDA_CS', 'C3_FULL', 'WSS']


# ── Parsers ────────────────────────────────────────────────────────────────────

def parse_seismic_log(path):
    """Returns {filename: score} for all successfully scored files."""
    scores = {}
    current_file = None
    with open(path, encoding='utf-8', errors='ignore') as f:
        for line in f:
            m = re.match(r'=== Analysing: (.+\.java) ===', line.strip())
            if m:
                current_file = m.group(1)
            elif ('Final SEISMIC Score:' in line
                  or 'Final LASCO Score:' in line
                  or 'Final Adjusted Score' in line) and current_file:
                try:
                    for marker in ['Final SEISMIC Score:', 'Final LASCO Score:', 'Final Adjusted Score']:
                        if marker in line:
                            scores[current_file] = float(line.split(marker)[1].split(':')[-1].strip())
                            current_file = None
                            break
                except ValueError:
                    pass
    return scores


def parse_baselines_csv(path):
    """Returns {filename: {metric: score}} from baselines CSV."""
    data = {}
    with open(path, encoding='utf-8') as f:
        for row in csv.DictReader(f):
            fname = row['file']
            data[fname] = {}
            for col in BASELINES:
                try:
                    data[fname][col] = float(row[col])
                except (ValueError, KeyError):
                    pass
    return data


# ── Effect sizes ───────────────────────────────────────────────────────────────

def paired_cliffs_delta(s, b):
    """Paired Cliff's delta: d = (#{S>B} - #{S<B}) / n."""
    s, b = np.array(s), np.array(b)
    diff = s - b
    return float((np.sum(diff > 0) - np.sum(diff < 0)) / len(diff))


def unpaired_cliffs_delta(x, y):
    """Unpaired Cliff's delta: P(X>Y) - P(X<Y)."""
    x, y = np.array(x), np.array(y)
    greater = np.sum(x[:, None] > y[None, :])
    less    = np.sum(x[:, None] < y[None, :])
    return float(greater - less) / (len(x) * len(y))


def interpret_delta(d):
    a = abs(d)
    if a < 0.147: return 'negligible'
    if a < 0.330: return 'small'
    if a < 0.474: return 'medium'
    return 'large'


# ── Test battery A: paired ─────────────────────────────────────────────────────

def run_paired_tests(seismic_map, baselines_map):
    common = sorted(set(seismic_map) & set(baselines_map))

    # Count how many tests will run for Bonferroni correction
    active_baselines = [col for col in BASELINES
                        if sum(1 for f in common if col in baselines_map.get(f, {})) >= 20]
    num_tests = len(active_baselines)
    alpha_bonf = 0.05 / num_tests if num_tests > 0 else 0.05

    print(f"\n{'='*100}")
    print(f"A. PAIRED TESTS  (Wilcoxon signed-rank + Cliff's delta)")
    print(f"   Classes in intersection: {len(common)}")
    print(f"   Bonferroni-corrected alpha: {alpha_bonf:.4f}  ({num_tests} tests)")
    print(f"{'='*100}")
    print(f"{'Metric':8s}  {'SEISMIC_mean':>12s}  {'Baseline_mean':>13s}  "
          f"{'W':>12s}  {'p-value':>12s}  {'Sig?':>5s}  {'Bonf?':>5s}  "
          f"{'Cliff_d':>8s}  {'Effect':>10s}")
    print('-' * 100)

    results = []

    for col in BASELINES:
        paired = [(seismic_map[f], baselines_map[f][col])
                  for f in common if col in baselines_map[f]]
        if len(paired) < 20:
            print(f"{col:8s}  (insufficient data)")
            continue

        s_arr = np.array([p[0] for p in paired])
        b_arr = np.array([p[1] for p in paired])

        stat, p = stats.wilcoxon(s_arr, b_arr)
        d       = paired_cliffs_delta(s_arr, b_arr)
        sig     = 'YES' if p < 0.05 else 'NO'
        sig_b   = 'YES' if p < alpha_bonf else 'NO'
        effect  = interpret_delta(d)

        print(f"{col:8s}  {np.mean(s_arr):>12.4f}  {np.mean(b_arr):>13.4f}  "
              f"{stat:>12.1f}  {p:>12.4e}  {sig:>5s}  {sig_b:>5s}  "
              f"{d:>+8.4f}  {effect:>10s}")

        results.append({
            'comparison':        f'SEISMIC_vs_{col}',
            'n_classes':         len(paired),
            'seismic_mean':      round(float(np.mean(s_arr)), 4),
            'baseline_mean':     round(float(np.mean(b_arr)), 4),
            'test':              'Wilcoxon',
            'stat':              round(float(stat), 2),
            'p_value':           float(p),
            'significant_p05':   p < 0.05,
            'significant_bonf':  p < alpha_bonf,
            'cliffs_delta':      round(d, 4),
            'effect_size':       effect,
        })

    return results


# ── Test battery B: Expert vs God ─────────────────────────────────────────────

def run_expert_vs_god(expert_log, god_log):
    expert_scores = list(parse_seismic_log(expert_log).values())
    god_scores    = list(parse_seismic_log(god_log).values())

    if not expert_scores or not god_scores:
        print("\nSkipping Expert vs God: one or both logs empty.")
        return None

    stat, p = stats.mannwhitneyu(expert_scores, god_scores, alternative='two-sided')
    d       = unpaired_cliffs_delta(expert_scores, god_scores)

    print(f"\n{'='*100}")
    print(f"B. DISCRIMINATIVE POWER  (Mann-Whitney U — Expert Monoliths vs God Classes)")
    print(f"{'='*100}")
    print(f"  Expert Monoliths  n={len(expert_scores):5d}  "
          f"mean={np.mean(expert_scores):.4f}  "
          f"median={np.median(expert_scores):.4f}  "
          f"std={np.std(expert_scores):.4f}")
    print(f"  God Classes       n={len(god_scores):5d}  "
          f"mean={np.mean(god_scores):.4f}  "
          f"median={np.median(god_scores):.4f}  "
          f"std={np.std(god_scores):.4f}")
    print(f"\n  Mann-Whitney U = {stat:.1f}  p = {p:.4e}  "
          f"{'*** SIGNIFICANT ***' if p < 0.05 else 'NOT significant'}")
    print(f"  Cliff's delta  = {d:+.4f}  effect = {interpret_delta(d)}")

    return {
        'comparison':       'Expert_vs_God_SEISMIC',
        'n_expert':         len(expert_scores),
        'n_god':            len(god_scores),
        'expert_mean':      round(float(np.mean(expert_scores)), 4),
        'god_mean':         round(float(np.mean(god_scores)), 4),
        'test':             'Mann-Whitney U',
        'stat':             round(float(stat), 2),
        'p_value':          float(p),
        'significant_p05':  p < 0.05,
        'cliffs_delta':     round(d, 4),
        'effect_size':      interpret_delta(d),
    }


# ── Entry point ────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description='Statistical validation: SEISMIC vs baseline metrics.'
    )
    parser.add_argument('--seismic_log',   default='results_expert_god_classes.log')
    parser.add_argument('--baselines_csv', default='baselines_extended_expert.csv')
    parser.add_argument('--god_log',       default='results_god_classes.log')
    parser.add_argument('--output',        default='statistical_tests_results.csv')
    args = parser.parse_args()

    print("Loading SEISMIC scores from log …")
    seismic_map = parse_seismic_log(args.seismic_log)
    print(f"  {len(seismic_map)} classes loaded.")

    print("Loading baseline scores from CSV …")
    baselines_map = parse_baselines_csv(args.baselines_csv)
    print(f"  {len(baselines_map)} classes loaded.")

    paired_results = run_paired_tests(seismic_map, baselines_map)

    god_result = None
    if os.path.isfile(args.god_log):
        god_result = run_expert_vs_god(args.seismic_log, args.god_log)
    else:
        print(f"\nGod Class log not found at '{args.god_log}' — skipping test B.")

    # Write output CSV
    fieldnames = ['comparison', 'n_classes', 'seismic_mean', 'baseline_mean',
                  'test', 'stat', 'p_value', 'significant_p05', 'significant_bonf',
                  'cliffs_delta', 'effect_size']

    rows = list(paired_results)
    if god_result:
        rows.append({
            'comparison':      god_result['comparison'],
            'n_classes':       f"{god_result['n_expert']}+{god_result['n_god']}",
            'seismic_mean':    god_result['expert_mean'],
            'baseline_mean':   god_result['god_mean'],
            'test':            god_result['test'],
            'stat':            god_result['stat'],
            'p_value':         god_result['p_value'],
            'significant_p05': god_result['significant_p05'],
            'significant_bonf': god_result['significant_p05'],
            'cliffs_delta':    god_result['cliffs_delta'],
            'effect_size':     god_result['effect_size'],
        })

    with open(args.output, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nAll results written to '{args.output}'.")


if __name__ == '__main__':
    main()
