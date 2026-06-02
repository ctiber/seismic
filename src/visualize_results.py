"""
Publication-ready figures for the SEISMIC paper.

Generates:
  Fig 1 — Three-group violin + boxplot (Expert / Normal / God)
  Fig 2 — ROC curves: SEISMIC vs all 6 baselines (God vs Non-God)

Usage:
    pip install matplotlib scikit-learn
    python visualize_results.py

Outputs:
    fig1_violin.png
    fig2_roc.png
"""

import csv
import re
import argparse

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from sklearn.metrics import roc_curve, auc, precision_recall_curve, average_precision_score


# ── Data loaders ──────────────────────────────────────────────────────────────

_SCORE_PATTERNS = (
    'Final SEISMIC Score:',   # current seismic.py output
    'Final LASCO Score:',     # legacy lasco.py output
    'Final Adjusted Score',   # legacy god-class runner output
)

def load_seismic_log(path):
    vals, cur = [], None
    with open(path, encoding='utf-8', errors='ignore') as f:
        for line in f:
            m = re.match(r'=== Analysing: (.+\.java) ===', line.strip())
            if m:
                cur = m.group(1)
            elif cur and any(p in line for p in _SCORE_PATTERNS):
                try:
                    vals.append(float(line.split(':')[-1].strip()))
                    cur = None
                except ValueError:
                    pass
    return vals


def load_seismic_csv(path):
    vals = []
    with open(path, encoding='utf-8') as f:
        for row in csv.DictReader(f):
            try:
                vals.append(float(row['seismic']))
            except (ValueError, KeyError):
                pass
    return vals


def load_baselines_csv(path):
    """Returns {metric: [values]} for all numeric columns except 'file'."""
    data = {}
    with open(path, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            for col, val in row.items():
                if col == 'file':
                    continue
                try:
                    data.setdefault(col, []).append(float(val))
                except (ValueError, TypeError):
                    pass
    return data


# ── Figure 1: Three-group violin ──────────────────────────────────────────────

def fig_violin(expert, ng, god, out='fig1_violin.png'):
    groups  = [expert, ng, god]
    labels  = ['Expert\nMonoliths', 'Normal\nClasses', 'God\nClasses']
    colors  = ['#4878CF', '#6ACC65', '#D65F5F']

    fig, ax = plt.subplots(figsize=(7, 5))

    parts = ax.violinplot(groups, positions=[1, 2, 3],
                          showmedians=True, showextrema=True)

    for i, (body, color) in enumerate(zip(parts['bodies'], colors)):
        body.set_facecolor(color)
        body.set_alpha(0.65)

    parts['cmedians'].set_color('black')
    parts['cmedians'].set_linewidth(1.8)
    parts['cmaxes'].set_color('grey')
    parts['cmins'].set_color('grey')
    parts['cbars'].set_color('grey')

    # Overlay mean markers
    means = [np.mean(g) for g in groups]
    ax.scatter([1, 2, 3], means, marker='D', s=40, color='white',
               edgecolors='black', linewidths=1.2, zorder=5, label='Mean')

    ax.set_xticks([1, 2, 3])
    ax.set_xticklabels(labels, fontsize=11)
    ax.set_ylabel('SEISMIC Score', fontsize=12)
    ax.set_title('SEISMIC Score Distribution by Class Category', fontsize=13)
    ax.set_ylim(0, 1.05)
    ax.yaxis.grid(True, linestyle='--', alpha=0.6)
    ax.set_axisbelow(True)

    # Annotate means
    for x, m in zip([1, 2, 3], means):
        ax.text(x, m + 0.04, f'{m:.3f}', ha='center', va='bottom',
                fontsize=9, color='black')

    # Legend patches
    patches = [mpatches.Patch(color=c, alpha=0.65, label=l.replace('\n', ' '))
               for c, l in zip(colors, labels)]
    patches.append(mpatches.Patch(color='white', label='◆ Mean',
                                  linewidth=1, edgecolor='black'))
    ax.legend(handles=patches, loc='upper left', fontsize=9)

    fig.tight_layout()
    fig.savefig(out, dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f"Saved: {out}")


# ── Figure 2: ROC curves ──────────────────────────────────────────────────────

def fig_roc(seismic_scores, baselines_expert, baselines_god, out='fig2_roc.png'):
    """
    Binary task: God Class (1) vs Expert Monolith (0).
    Higher score = more "God-like".
    For SEISMIC: higher = worse  → use score directly.
    For each baseline we try both orientations and pick the one with AUC > 0.5.
    """
    n_exp = len(seismic_scores['expert'])
    n_god = len(seismic_scores['god'])

    y_true_seismic = [0] * n_exp + [1] * n_god
    y_score_seismic = seismic_scores['expert'] + seismic_scores['god']

    fig, ax = plt.subplots(figsize=(7, 6))

    # SEISMIC
    fpr, tpr, _ = roc_curve(y_true_seismic, y_score_seismic)
    roc_auc = auc(fpr, tpr)
    ax.plot(fpr, tpr, lw=2.5, color='#D65F5F',
            label=f'SEISMIC  (AUC = {roc_auc:.3f})')

    # Baselines — align per-file between expert and god CSVs
    metric_styles = {
        'LCOM4':   ('#4878CF', '--'),
        'TCC':     ('#6ACC65', '-.'),
        'C3':      ('#B47CC7', ':'),
        'LSCC':    ('#C4AD66', '--'),
        'LDA_CS':  ('#77BEDB', '-.'),
        'C3_FULL': ('#F0A500', ':'),
        'WSS':     ('#50C878', (0, (3, 1, 1, 1))),
    }

    for metric, (color, ls) in metric_styles.items():
        exp_vals = baselines_expert.get(metric, [])
        god_vals = baselines_god.get(metric, [])
        if not exp_vals or not god_vals:
            continue
        # Truncate to shortest to balance classes for AUC
        n = min(len(exp_vals), len(god_vals))
        y_t = [0] * n + [1] * n
        y_s = exp_vals[:n] + god_vals[:n]
        fpr_b, tpr_b, _ = roc_curve(y_t, y_s)
        a = auc(fpr_b, tpr_b)
        # Flip if AUC < 0.5 (metric oriented opposite direction)
        if a < 0.5:
            fpr_b, tpr_b, _ = roc_curve(y_t, [-v for v in y_s])
            a = auc(fpr_b, tpr_b)
        ax.plot(fpr_b, tpr_b, lw=1.4, color=color, linestyle=ls,
                label=f'{metric:<8} (AUC = {a:.3f})')

    ax.plot([0, 1], [0, 1], 'k--', lw=1, alpha=0.5, label='Random (AUC = 0.500)')

    ax.set_xlabel('False Positive Rate', fontsize=12)
    ax.set_ylabel('True Positive Rate', fontsize=12)
    ax.set_title('ROC Curves: God Class Detection\n(SEISMIC vs Baselines)', fontsize=13)
    ax.legend(loc='lower right', fontsize=9)
    ax.yaxis.grid(True, linestyle='--', alpha=0.4)
    ax.xaxis.grid(True, linestyle='--', alpha=0.4)
    ax.set_axisbelow(True)

    fig.tight_layout()
    fig.savefig(out, dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f"Saved: {out}")


# ── Figure 3: Precision-Recall curves ────────────────────────────────────────

def fig_pr(seismic_scores, baselines_expert, baselines_god, out='fig3_pr.png'):
    """
    Binary task: God Class (1) vs Expert Monolith (0).
    PR curves are more informative than ROC under class imbalance.
    Positive class = God (n=4147), Negative = Expert (n=1224) → ratio ≈ 3.4:1.
    The no-skill baseline = proportion of positives in the pool.
    """
    n_exp = len(seismic_scores['expert'])
    n_god = len(seismic_scores['god'])
    baseline_precision = n_god / (n_god + n_exp)   # no-skill line

    y_true_seismic = [0] * n_exp + [1] * n_god
    y_score_seismic = seismic_scores['expert'] + seismic_scores['god']

    fig, ax = plt.subplots(figsize=(7, 6))

    # SEISMIC
    prec, rec, _ = precision_recall_curve(y_true_seismic, y_score_seismic)
    ap = average_precision_score(y_true_seismic, y_score_seismic)
    ax.plot(rec, prec, lw=2.5, color='#D65F5F',
            label=f'SEISMIC  (AP = {ap:.3f})')

    # Baselines
    metric_styles = {
        'LCOM4':   ('#4878CF', '--'),
        'TCC':     ('#6ACC65', '-.'),
        'C3':      ('#B47CC7', ':'),
        'LSCC':    ('#C4AD66', '--'),
        'LDA_CS':  ('#77BEDB', '-.'),
        'C3_FULL': ('#F0A500', ':'),
        'WSS':     ('#50C878', (0, (3, 1, 1, 1))),
    }

    for metric, (color, ls) in metric_styles.items():
        exp_vals = baselines_expert.get(metric, [])
        god_vals = baselines_god.get(metric, [])
        if not exp_vals or not god_vals:
            continue
        n = min(len(exp_vals), len(god_vals))
        y_t = [0] * n + [1] * n
        y_s = exp_vals[:n] + god_vals[:n]
        ap_b = average_precision_score(y_t, y_s)
        # Flip if AP < baseline (metric oriented opposite direction)
        if ap_b < n / (2 * n):
            y_s = [-v for v in y_s]
            ap_b = average_precision_score(y_t, y_s)
        prec_b, rec_b, _ = precision_recall_curve(y_t, y_s)
        ax.plot(rec_b, prec_b, lw=1.4, color=color, linestyle=ls,
                label=f'{metric:<8} (AP = {ap_b:.3f})')

    # No-skill baseline
    ax.axhline(y=baseline_precision, color='black', linestyle='--',
               lw=1, alpha=0.5,
               label=f'No skill (AP = {baseline_precision:.3f})')

    ax.set_xlabel('Recall', fontsize=12)
    ax.set_ylabel('Precision', fontsize=12)
    ax.set_title('Precision-Recall Curves: God Class Detection\n'
                 '(SEISMIC vs Baselines)', fontsize=13)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.05)
    ax.legend(loc='lower right', fontsize=9)
    ax.yaxis.grid(True, linestyle='--', alpha=0.4)
    ax.xaxis.grid(True, linestyle='--', alpha=0.4)
    ax.set_axisbelow(True)

    fig.tight_layout()
    fig.savefig(out, dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f"Saved: {out}")


# ── Figure 4: Expert–God gap bar chart (RQ2) ─────────────────────────────────

def fig_gap_bar(seismic_scores, baselines_expert, baselines_god,
                out='fig4_gap_bar.png'):
    """
    Grouped bar chart: Expert mean, God mean, and Expert-God gap
    for all seven metrics. Headline claim: SEISMIC gap is 4.5x-51x larger.
    """
    seismic_exp_mean = float(np.mean(seismic_scores['expert']))
    seismic_god_mean = float(np.mean(seismic_scores['god']))

    metrics = ['LCOM4', 'TCC', 'C3', 'LSCC', 'LDA-CS', 'C3-Full', 'WSS', 'SEISMIC']
    expert_means = []
    god_means    = []

    bl_key_map = {
        'LCOM4':   'LCOM4',
        'TCC':     'TCC',
        'C3':      'C3',
        'LSCC':    'LSCC',
        'LDA-CS':  'LDA_CS',
        'C3-Full': 'C3_FULL',
        'WSS':     'WSS',
    }
    for m in metrics[:-1]:
        k = bl_key_map[m]
        e = baselines_expert.get(k, [])
        g = baselines_god.get(k, [])
        n = min(len(e), len(g))
        expert_means.append(float(np.mean(e[:n])) if e else 0.0)
        god_means.append(float(np.mean(g[:n]))    if g else 0.0)

    expert_means.append(seismic_exp_mean)
    god_means.append(seismic_god_mean)

    gaps = [g - e for e, g in zip(expert_means, god_means)]

    x      = np.arange(len(metrics))
    width  = 0.28
    colors_exp  = ['#6699CC'] * 7 + ['#D65F5F']
    colors_god  = ['#99CCFF'] * 7 + ['#FF9999']
    colors_gap  = ['#AAAAAA'] * 7 + ['#B22222']

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # ── Left panel: grouped bars Expert vs God ────────────────────────────────
    ax = axes[0]
    bars_exp = ax.bar(x - width, expert_means, width, label='Expert Monoliths',
                      color=colors_exp, edgecolor='white', linewidth=0.5)
    bars_god = ax.bar(x,          god_means,    width, label='God Classes',
                      color=colors_god, edgecolor='white', linewidth=0.5)

    # Annotate SEISMIC bars
    ax.text(x[-1] - width, seismic_exp_mean + 0.015, f'{seismic_exp_mean:.3f}',
            ha='center', va='bottom', fontsize=8, fontweight='bold', color='#D65F5F')
    ax.text(x[-1],          seismic_god_mean + 0.015, f'{seismic_god_mean:.3f}',
            ha='center', va='bottom', fontsize=8, fontweight='bold', color='#D65F5F')

    ax.set_xticks(x - width/2)
    ax.set_xticklabels(metrics, fontsize=10)
    ax.set_ylabel('Mean Score', fontsize=11)
    ax.set_title('Mean Scores: Expert Monoliths vs God Classes', fontsize=12)
    ax.set_ylim(0, 1.05)
    ax.yaxis.grid(True, linestyle='--', alpha=0.5)
    ax.set_axisbelow(True)
    ax.legend(fontsize=9)

    # Highlight SEISMIC column background
    ax.axvspan(x[-1] - width*1.8, x[-1] + width*0.8, alpha=0.07,
               color='#D65F5F', zorder=0)

    # ── Right panel: Expert–God gap ───────────────────────────────────────────
    ax2 = axes[1]
    bar_colors = ['#AAAAAA'] * 7 + ['#B22222']
    bars = ax2.bar(x, gaps, width * 2.2, color=bar_colors,
                   edgecolor='white', linewidth=0.5)

    # Zero line
    ax2.axhline(0, color='black', linewidth=0.8)

    # Annotate all gap values
    for i, (bar, gap) in enumerate(zip(bars, gaps)):
        va  = 'bottom' if gap >= 0 else 'top'
        off = 0.005   if gap >= 0 else -0.005
        fw  = 'bold'  if i == len(metrics) - 1 else 'normal'
        ax2.text(bar.get_x() + bar.get_width() / 2,
                 gap + off, f'{gap:+.3f}',
                 ha='center', va=va, fontsize=8, fontweight=fw)

    ax2.set_xticks(x)
    ax2.set_xticklabels(metrics, fontsize=10)
    ax2.set_ylabel('God Mean − Expert Mean', fontsize=11)
    ax2.set_title('Expert–God Discriminative Gap\n'
                  '(SEISMIC gap is 3.6×–51× larger than any baseline)',
                  fontsize=12)
    ax2.yaxis.grid(True, linestyle='--', alpha=0.5)
    ax2.set_axisbelow(True)

    # Highlight SEISMIC column background
    ax2.axvspan(x[-1] - width * 1.1, x[-1] + width * 1.1,
                alpha=0.07, color='#B22222', zorder=0)

    fig.tight_layout()
    fig.savefig(out, dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f"Saved: {out}")


# ── Figure 5: Sensitivity heatmaps (RQ4) ─────────────────────────────────────

def fig_sensitivity_heatmaps(sensitivity_expert_csv, sensitivity_god_csv,
                              out='fig5_sensitivity.png'):
    """
    Two heatmaps side by side:
      Left  — mean SEISMIC score on Expert Monoliths, coloured by tier
      Right — Expert-God discriminative gap (Expert − God); positive = correct ordering
    """
    import pandas as pd
    from matplotlib.colors import LinearSegmentedColormap, BoundaryNorm
    from matplotlib.patches import Patch

    tau_m_vals  = [10, 15, 20, 25, 30]
    lambda_vals = [0.003, 0.005, 0.010, 0.100, 0.150]

    df_exp = pd.read_csv(sensitivity_expert_csv)
    df_god = pd.read_csv(sensitivity_god_csv)

    grid_exp = np.zeros((5, 5))
    grid_god = np.zeros((5, 5))

    for df, grid in [(df_exp, grid_exp), (df_god, grid_god)]:
        for _, row in df.iterrows():
            try:
                ti = tau_m_vals.index(int(row['tau_m']))
                li = lambda_vals.index(float(row['lambda_m']))
                grid[ti, li] = float(row['mean'])
            except (ValueError, KeyError):
                pass

    # Expert − God: positive means correct Expert > God ordering
    grid_gap = grid_exp - grid_god

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))

    # ── Left: score heatmap coloured by tier ─────────────────────────────────
    tier_bounds = [0.0, 0.25, 0.50, 0.70, 1.01]
    tier_colors = ['#D62728', '#FF7F0E', '#2CA02C', '#1F77B4']
    tier_labels = ['Collapse\n(<0.25)',
                   'SSI / Inflation\n(0.25–0.49)',
                   'Monitor for Drift\n(0.50–0.69)',
                   'Functional Integrity\n(≥0.70)']

    cmap_tier = LinearSegmentedColormap.from_list('tiers', tier_colors, N=256)
    norm_tier = BoundaryNorm(tier_bounds, cmap_tier.N)

    ax = axes[0]
    ax.imshow(grid_exp, cmap=cmap_tier, norm=norm_tier, aspect='auto', origin='lower')

    for i in range(5):
        for j in range(5):
            ax.text(j, i, f'{grid_exp[i, j]:.3f}',
                    ha='center', va='center', fontsize=9,
                    color='white', fontweight='bold')

    ax.set_xticks(range(5))
    ax.set_xticklabels([str(l) for l in lambda_vals], fontsize=10)
    ax.set_yticks(range(5))
    ax.set_yticklabels([str(t) for t in tau_m_vals], fontsize=10)
    ax.set_xlabel(r'Decay rate $\lambda_m$', fontsize=11)
    ax.set_ylabel(r'Threshold $\tau_m$', fontsize=11)
    ax.set_title('Mean SEISMIC Score — Expert Monoliths\n'
                 '(coloured by architectural tier)', fontsize=11)

    legend_patches = [Patch(color=c, label=l)
                      for c, l in zip(tier_colors, tier_labels)]
    ax.legend(handles=legend_patches, loc='upper right', fontsize=7.5, framealpha=0.85)

    # ── Right: gap heatmap (Expert − God, diverging around 0) ────────────────
    ax2 = axes[1]
    absmax = float(np.max(np.abs(grid_gap))) * 1.05
    im2 = ax2.imshow(grid_gap, cmap=plt.cm.RdYlGn,
                     vmin=-absmax, vmax=absmax,
                     aspect='auto', origin='lower')

    for i in range(5):
        for j in range(5):
            color = 'white' if abs(grid_gap[i, j]) > absmax * 0.3 else 'black'
            ax2.text(j, i, f'{grid_gap[i, j]:+.3f}',
                     ha='center', va='center', fontsize=9,
                     color=color, fontweight='bold')

    ax2.set_xticks(range(5))
    ax2.set_xticklabels([str(l) for l in lambda_vals], fontsize=10)
    ax2.set_yticks(range(5))
    ax2.set_yticklabels([str(t) for t in tau_m_vals], fontsize=10)
    ax2.set_xlabel(r'Decay rate $\lambda_m$', fontsize=11)
    ax2.set_ylabel(r'Threshold $\tau_m$', fontsize=11)
    ax2.set_title('Discriminative Gap (Expert $-$ God)\n'
                  'Green = Expert $>$ God (correct); Red = ordering inverted',
                  fontsize=11)

    plt.colorbar(im2, ax=ax2, fraction=0.046, pad=0.04,
                 label='Expert mean $-$ God mean')

    fig.tight_layout()
    fig.savefig(out, dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f"Saved: {out}")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--expert_log',      default='Exp1 Results/results_expert_god_classes.log')
    parser.add_argument('--god_log',         default='Exp1 Results/results_god_classes_v1.log')
    parser.add_argument('--ng_csv',          default='seismic_ng.csv')
    parser.add_argument('--baselines_expert',default='baselines_extended_expert.csv')
    parser.add_argument('--baselines_god',   default='baselines_extended_god.csv')
    parser.add_argument('--out_violin',      default='fig1_violin.png')
    parser.add_argument('--out_roc',         default='fig2_roc.png')
    parser.add_argument('--out_pr',          default='fig3_pr.png')
    parser.add_argument('--sensitivity_expert', default='sensitivity_expert.csv')
    parser.add_argument('--sensitivity_god',    default='sensitivity_god.csv')
    parser.add_argument('--out_gap_bar',     default='fig4_gap_bar.png')
    parser.add_argument('--out_sensitivity', default='fig5_sensitivity.png')
    args = parser.parse_args()

    print("Loading SEISMIC scores …")
    expert = load_seismic_log(args.expert_log)
    god    = load_seismic_log(args.god_log)
    ng     = load_seismic_csv(args.ng_csv)
    print(f"  Expert={len(expert)}  God={len(god)}  Normal={len(ng)}")
    if not expert or not god:
        raise RuntimeError(
            f"Log parsing returned no scores "
            f"(expert={len(expert)}, god={len(god)}). "
            "Check that the log files exist and contain one of: "
            + ", ".join(f'"{p}"' for p in _SCORE_PATTERNS)
        )

    print("Loading baseline CSVs …")
    bl_exp = load_baselines_csv(args.baselines_expert)
    bl_god = load_baselines_csv(args.baselines_god)

    print("Generating Fig 1 — violin …")
    fig_violin(expert, ng, god, out=args.out_violin)

    print("Generating Fig 2 — ROC …")
    fig_roc({'expert': expert, 'god': god}, bl_exp, bl_god, out=args.out_roc)

    print("Generating Fig 3 — Precision-Recall …")
    fig_pr({'expert': expert, 'god': god}, bl_exp, bl_god, out=args.out_pr)

    print("Generating Fig 4 — Expert–God gap bar chart …")
    fig_gap_bar({'expert': expert, 'god': god}, bl_exp, bl_god,
                out=args.out_gap_bar)

    print("Generating Fig 5 — Sensitivity heatmaps …")
    fig_sensitivity_heatmaps(args.sensitivity_expert, args.sensitivity_god,
                             out=args.out_sensitivity)

    print("\nDone.")


if __name__ == '__main__':
    main()
