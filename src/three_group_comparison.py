"""
Three-Group SEISMIC Comparison.

Compares SEISMIC scores across Expert Monoliths, God Classes, and Normal Classes
using Mann-Whitney U tests and Cliff's delta effect sizes.

Usage:
    python three_group_comparison.py
    python three_group_comparison.py --expert_log results_expert_god_classes.log \
                                     --god_log    results_god_classes_v1.log     \
                                     --ng_csv     seismic_ng.csv                 \
                                     --output     three_group_results.csv
"""

import argparse
import csv
import re

import numpy as np
from scipy import stats


def load_seismic_log(path):
    """Load SEISMIC scores from a .log file (supports both score formats)."""
    vals, cur = [], None
    with open(path, encoding='utf-8', errors='ignore') as f:
        for line in f:
            m = re.match(r'=== Analysing: (.+\.java) ===', line.strip())
            if m:
                cur = m.group(1)
            elif ('Final SEISMIC Score:' in line or 'Final LASCO Score:' in line or 'Final Adjusted Score' in line) and cur:
                try:
                    vals.append(float(line.split(':')[-1].strip()))
                    cur = None
                except ValueError:
                    pass
    return vals


def load_seismic_csv(path):
    """Load SEISMIC scores from a CSV file with a 'seismic' column."""
    vals = []
    with open(path, encoding='utf-8') as f:
        for row in csv.DictReader(f):
            try:
                vals.append(float(row['seismic']))
            except (ValueError, KeyError):
                pass
    return vals


def cliffs_delta(a, b):
    """Unpaired Cliff's delta: positive means a > b."""
    n1, n2 = len(a), len(b)
    if n1 == 0 or n2 == 0:
        return float('nan')
    greater = sum(1 for x in a for y in b if x > y)
    less    = sum(1 for x in a for y in b if x < y)
    return (greater - less) / (n1 * n2)


def effect_label(d):
    ad = abs(d)
    if ad < 0.147: return 'negligible'
    if ad < 0.330: return 'small'
    if ad < 0.474: return 'medium'
    return 'large'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--expert_log', default='results_expert_god_classes.log')
    parser.add_argument('--god_log',    default='results_god_classes_v1.log')
    parser.add_argument('--ng_csv',     default='seismic_ng.csv')
    parser.add_argument('--output',     default='three_group_results.csv')
    args = parser.parse_args()

    print(f"Loading Expert Monoliths from '{args.expert_log}' …")
    expert = load_seismic_log(args.expert_log)
    print(f"Loading God Classes from '{args.god_log}' …")
    god    = load_seismic_log(args.god_log)
    print(f"Loading Normal Classes from '{args.ng_csv}' …")
    ng     = load_seismic_csv(args.ng_csv)

    # Guard: abort early with a clear message if any group is empty
    empty = [(label, n) for label, n in [('Expert', len(expert)), ('God', len(god)), ('Normal', len(ng))] if n == 0]
    if empty:
        for label, _ in empty:
            print(f"  ERROR: {label} group loaded 0 scores — check the file path or wait for seismic.py to finish.")
        raise SystemExit("Aborted: one or more groups are empty.")

    # ── Descriptive stats ────────────────────────────────────────────────────
    print()
    print("=" * 70)
    print("SEISMIC Descriptive Statistics")
    print("=" * 70)
    header = f"{'Group':<22} {'n':>5}  {'mean':>7}  {'median':>7}  {'std':>7}"
    print(header)
    print("-" * 70)
    groups = [('Expert Monoliths', expert), ('God Classes', god), ('Normal Classes', ng)]
    for label, vals in groups:
        print(f"{label:<22} {len(vals):>5}  {np.mean(vals):>7.4f}  {np.median(vals):>7.4f}  {np.std(vals):>7.4f}")

    # ── Pairwise Mann-Whitney + Cliff's delta ────────────────────────────────
    print()
    print("=" * 70)
    print("Pairwise Mann-Whitney U  +  Cliff's delta")
    print("=" * 70)
    pairs = [
        ('Expert vs God',    expert, god),
        ('Expert vs Normal', expert, ng),
        ('God vs Normal',    god,    ng),
    ]
    rows = []
    hdr = f"{'Comparison':<22}  {'U':>12}  {'p-value':>12}  {'Sig?':>5}  {'Cliff_d':>8}  {'Effect'}"
    print(hdr)
    print("-" * 70)
    for label, a, b in pairs:
        if len(a) < 2 or len(b) < 2:
            print(f"{label:<22}  SKIPPED (too few samples: n1={len(a)}, n2={len(b)})")
            continue
        u, p = stats.mannwhitneyu(a, b, alternative='two-sided')
        d    = cliffs_delta(a, b)
        sig  = 'YES' if p < 0.05 else 'NO'
        eff  = effect_label(d)
        print(f"{label:<22}  {u:>12.1f}  {p:>12.4e}  {sig:>5}  {d:>+8.4f}  {eff}")
        rows.append({'comparison': label, 'U': u, 'p_value': p,
                     'significant': sig, 'cliffs_d': round(d, 4), 'effect': eff})

    # ── CSV output ───────────────────────────────────────────────────────────
    with open(args.output, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['comparison', 'U', 'p_value', 'significant', 'cliffs_d', 'effect'])
        writer.writeheader()
        writer.writerows(rows)
    print(f"\nResults written to '{args.output}'.")

if __name__ == '__main__':
    main()
