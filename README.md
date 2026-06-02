# SEISMIC — Replication Package

This repository contains the implementation, datasets, and experimental scripts for:

> **SEISMIC: A Hybrid Structural-Semantic Inflation Metric for Detecting Design Instability**

---

## Repository Structure

```
seismic/
├── src/                        # All source code
│   ├── seismic.py              # Core SEISMIC metric (λ_m = 0.005)
│   ├── m_seismic.py            # M-SEISMIC for microservice evaluation
│   ├── baselines_extended.py   # 7 baseline cohesion metrics
│   ├── m_seismic_baselines.py  # Microservice baseline metrics
│   ├── run_smellycodepp.py     # RQ1/RQ2: SmellyCode++ experiment
│   ├── run_mlcq.py             # RQ2 (MLCQ): SEISMIC scoring
│   ├── run_mlcq_baselines.py   # RQ2 (MLCQ): all metrics + statistical comparison
│   ├── sensitivity_analysis.py # RQ3: (τ_m, λ_m) parameter grid (transformer)
│   ├── sensitivity_proper.py   # RQ3: grid sweep using pre-computed φ/bonus (fast)
│   ├── statistical_tests.py    # Non-parametric test helpers
│   ├── three_group_comparison.py # RQ1 three-group statistics
│   └── visualize_results.py    # Publication figures
├── dataset/
│   ├── smellycodepp/
│   │   ├── expert_monoliths/   # 1,224 Java files (Expert Monoliths)
│   │   ├── god_classes/        # 4,145 Java files (God Classes)
│   │   └── normal_classes/     # 1,481 Java files (Normal Classes)
│   └── mlcq/
│       ├── MLCQCodeSmellSamples.csv  # Human-annotated smell labels
│       ├── god_classes/        # 237 Java files (MLCQ God Classes)
│       └── normal_classes/     # 1,873 Java files (MLCQ Normal Classes)
├── results/
│   ├── smellycodepp_results.csv       # Three-group SEISMIC scores (RQ1/RQ2)
│   ├── mlcq_seismic_results.csv       # MLCQ SEISMIC scores
│   ├── mlcq_allmetrics_results.csv    # MLCQ all-metrics comparison table
│   ├── sensitivity_expert.csv         # RQ3 grid results — Expert Monoliths
│   ├── sensitivity_god.csv            # RQ3 grid results — God Classes
│   └── figures/                       # Generated paper figures
├── examples/
│   ├── GodClass_444.java      # Incoherent God Class (SEISMIC = 0.007)
│   ├── OrderProcessor.java    # Cohesive domain class (SEISMIC = 0.738)
│   └── BankAccount.java       # Cohesive domain class (SEISMIC = 0.738)
├── requirements.txt
└── README.md
```

---

## Environment Setup

**Python 3.9 or higher** is required.

```bash
pip install -r requirements.txt
```

The first run of any script that uses `seismic.py` will download the
`all-MiniLM-L6-v2` SentenceTransformer model (~80 MB) automatically.

---

## Quick Start: Score a Single Class

```bash
cd src/
python -c "from seismic import calculate_seismic_score; calculate_seismic_score('../examples/GodClass_444.java')"
python -c "from seismic import calculate_seismic_score; calculate_seismic_score('../examples/OrderProcessor.java')"
```

---

## Reproducing the Experiments

All commands below are run from the **package root** (the directory containing this README).

### RQ1 & RQ2 — Three-Group Discrimination and Baseline Comparison (SmellyCode++)

Scores all three groups with the calibrated λ_m = 0.005 and prints
descriptive statistics, Mann-Whitney U tests, and Cliff's delta.

```bash
python src/run_smellycodepp.py \
    --expert  dataset/smellycodepp/expert_monoliths/ \
    --god     dataset/smellycodepp/god_classes/ \
    --normal  dataset/smellycodepp/normal_classes/ \
    --out     results/smellycodepp_results.csv
```

Expected output (after ~20–30 min depending on hardware):
```
  Normal Classes      n=1481  mean=0.464  median=0.498  std=0.261
  Expert Monoliths    n=1224  mean=0.420  median=0.419  std=0.217
  God Classes         n=4145  mean=0.382  median=0.351  std=0.225

  Expert vs God       p=1.89e-09  YES  δ=+0.113  negligible
  Expert vs Normal    p=9.63e-08  YES  δ=-0.119  negligible
  God vs Normal       p=1.77e-31  YES  δ=-0.204  small
```

### RQ2 (MLCQ) — Replication on Human-Labeled Oracle

**Step 1** — Compute SEISMIC scores on MLCQ (pre-computed results included in `results/`):
```bash
python src/run_mlcq.py
```

**Step 2** — Compute all 7 baselines and run the full comparison table:
```bash
python src/run_mlcq_baselines.py \
    --out results/mlcq_allmetrics_results.csv
```

### RQ3 — Parameter Sensitivity Analysis

Sweeps τ_m ∈ {10, 15, 20, 25, 30} × λ_m ∈ {0.003, 0.005, 0.010, 0.100, 0.150}.
The three lower λ_m values bracket the calibrated point; the two higher values
characterise robustness under aggressive decay.

**Recommended** — uses pre-computed φ/bonus from `smellycodepp_results.csv` and
re-extracts structural counts via javalang (no transformer re-run, ~2 min):

```bash
python src/sensitivity_proper.py
```

Outputs `results/sensitivity_expert.csv` and `results/sensitivity_god.csv`.

Alternatively, to re-run with full transformer embeddings (~30 min):

```bash
python src/sensitivity_analysis.py \
    --java_dir dataset/smellycodepp/expert_monoliths/ \
    --god_dir  dataset/smellycodepp/god_classes/ \
    --output   results/sensitivity_expert.csv \
    --god_output results/sensitivity_god.csv
```

### RQ4 — M-SEISMIC Microservice Evaluation (TrainTicket)

TrainTicket is not included in this repository due to its size.
Clone it first:

```bash
git clone https://github.com/FudanSELab/train-ticket.git
```

Then score all 42 parseable services:
```bash
python src/m_seismic.py \
    --batch_dir train-ticket/ \
    --output    results/m_seismic_results.csv
```

Compare against structural baselines:
```bash
python src/m_seismic_baselines.py \
    --batch_dir train-ticket/ \
    --output    results/m_seismic_baselines_results.csv
```

### Regenerate Paper Figures

Pre-generated figures are provided in `results/figures/`.

To regenerate after running the experiments above, pass the result files as
arguments. Run `python src/visualize_results.py --help` for the full list of
arguments.

---

## λ_m Calibration

The decay parameter λ_m = 0.005 was selected by grid search on a 70% training
split of SmellyCode++ (maximising the Kruskal-Wallis H statistic for three-group
separation), then evaluated on the held-out 30% test split. The calibration
script is not required to reproduce the paper results, as the calibrated value
is already set in `src/seismic.py`.

---

## Datasets

### SmellyCode++
Derived from 85 Apache open-source Java projects. The three groups are:

| Group | Definition | n |
|-------|-----------|---|
| Normal Classes | Randomly sampled non-flagged classes | 1,481 |
| Expert Monoliths | God Classes with zero Feature Envy (PMD) | 1,224 |
| God Classes | Flagged by PMD God Class detector | 4,145 |

### MLCQ
Human-annotated code smell dataset from Kafer et al. (2019).
The original annotation CSV (`MLCQCodeSmellSamples.csv`) is included.
Java source files are extracted from the repositories listed in the CSV.

Original paper: *A Study of the Occurrence of Code Smells in Open-Source Java Projects*,
available at https://github.com/iocseg/mlcq

---

## Citation

If you use this replication package, please cite:

```bibtex
@article{seismic2026,
  title   = {SEISMIC: A Hybrid Structural-Semantic Inflation Metric for Detecting
             Design Instability},
  author  = {Tibermacine, Chouki and Tibermacine, Okba},
  journal = {Submitted to a Journal},
  year    = {2026}
}
```