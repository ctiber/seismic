"""
M-SEISMIC Baseline Comparison: LCOM4 + LSA-ACS per TrainTicket service.

Computes class-level LCOM4 and LSA-ACS for every valid Java class in each
ts-* service, then aggregates to service-level means. Merges with existing
m_seismic_results.csv to produce a unified comparison table.

This enables direct evaluation of whether M-SEISMIC produces different
assessments than structural (LCOM4) or semantic (LSA-ACS) baselines at
the microservice level.

Usage:
    python m_seismic_baselines.py \\
        --batch_dir     train-ticket \\
        --m_seismic_csv m_seismic_results.csv \\
        --output        m_seismic_comparison.csv
"""

import argparse
import csv
import os
import re

import numpy as np
import javalang
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics.pairwise import cosine_similarity as sk_cosine


# ── Helpers ────────────────────────────────────────────────────────────────────

def split_camel(name):
    if not name:
        return ''
    name = name.replace('.', ' ')
    return ' '.join(re.sub('([a-z])([A-Z])', r'\1 \2', name).split()).lower()


def is_domain_type(t):
    return t not in {
        'String', 'Integer', 'Double', 'Float', 'Long', 'Boolean',
        'List', 'Map', 'Set', 'int', 'double', 'float', 'void', 'boolean',
    }


def is_analysis_candidate(code):
    return ('interface ' not in code
            and '@Test' not in code
            and 'extends TestCase' not in code
            and 'abstract class' not in code)


def collect_java_files(directory):
    result = []
    for root, _, files in os.walk(directory):
        for f in files:
            if f.endswith('.java'):
                result.append(os.path.join(root, f))
    return result


# ── LCOM4 ──────────────────────────────────────────────────────────────────────

def _lcom4_normalized(tree):
    """Returns normalized LCOM4 (1 / #components) for first class in tree."""
    classes = [n for _, n in tree if isinstance(n, javalang.tree.ClassDeclaration)]
    if not classes:
        return None

    all_fields = {n.name for _, n in tree
                  if isinstance(n, javalang.tree.VariableDeclarator)}
    methods = [n for _, n in classes[0].filter(javalang.tree.MethodDeclaration)]
    if len(methods) < 2:
        return 1.0

    adj = {m.name: set() for m in methods}
    field_to_methods = {}

    for m in methods:
        refs = {c.member for _, c in m.filter(javalang.tree.MemberReference)
                if c.member in all_fields}
        for r in refs:
            field_to_methods.setdefault(r, set()).add(m.name)
        calls = {c.member for _, c in m.filter(javalang.tree.MethodInvocation)
                 if c.member in adj}
        for c in calls:
            if c in adj:
                adj[m.name].add(c)
                adj[c].add(m.name)

    for methods_set in field_to_methods.values():
        lst = list(methods_set)
        for i in range(len(lst)):
            for j in range(i + 1, len(lst)):
                adj[lst[i]].add(lst[j])
                adj[lst[j]].add(lst[i])

    visited = set()
    components = 0
    for m in list(adj):
        if m not in visited:
            components += 1
            stack = [m]
            while stack:
                cur = stack.pop()
                if cur in visited:
                    continue
                visited.add(cur)
                stack.extend(adj[cur] - visited)

    return 1.0 / components if components > 0 else 1.0


# ── LSA-ACS ────────────────────────────────────────────────────────────────────

def _method_doc(node, all_fields):
    terms = [split_camel(node.name)]
    for _, c in node.filter(javalang.tree.MemberReference):
        if c.member in all_fields:
            terms.append(split_camel(c.member))
    for p in node.parameters:
        terms.append(split_camel(p.name))
        if hasattr(p.type, 'name') and is_domain_type(p.type.name):
            terms.append(split_camel(p.type.name))
    if (hasattr(node, 'return_type') and node.return_type
            and is_domain_type(node.return_type.name)):
        terms.append(split_camel(node.return_type.name))
    return ' '.join(terms)


def _lsa_acs(tree):
    """Returns LSA average cosine similarity for first class in tree."""
    classes = [n for _, n in tree if isinstance(n, javalang.tree.ClassDeclaration)]
    if not classes:
        return None

    all_fields = {n.name for _, n in tree
                  if isinstance(n, javalang.tree.VariableDeclarator)}
    methods = [n for _, n in classes[0].filter(javalang.tree.MethodDeclaration)]
    if len(methods) < 2:
        return 1.0

    docs = [_method_doc(m, all_fields) for m in methods]
    try:
        n_comp = min(len(docs) - 1, 100)
        if n_comp < 1:
            return 1.0
        tfidf = TfidfVectorizer(min_df=1)
        X = tfidf.fit_transform(docs)
        if X.shape[1] < n_comp:
            n_comp = X.shape[1]
        if n_comp < 1:
            return 1.0
        svd = TruncatedSVD(n_components=n_comp, random_state=42)
        lsa = svd.fit_transform(X)
        sims = sk_cosine(lsa)
        n = len(docs)
        pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
        if not pairs:
            return 1.0
        return float(np.mean([sims[i, j] for i, j in pairs]))
    except Exception:
        return None


# ── Per-service scoring ────────────────────────────────────────────────────────

def score_service_baselines(service_dir):
    lcom4_vals, lsa_vals = [], []
    skipped = 0

    for path in collect_java_files(service_dir):
        try:
            code = open(path, encoding='utf-8').read()
            if not is_analysis_candidate(code):
                continue
            tree = javalang.parse.parse(code)

            v4 = _lcom4_normalized(tree)
            if v4 is not None:
                lcom4_vals.append(v4)

            la = _lsa_acs(tree)
            if la is not None:
                lsa_vals.append(la)
        except Exception:
            skipped += 1

    return {
        'n_classes':    len(lcom4_vals),
        'lcom4_mean':   round(float(np.mean(lcom4_vals)), 4) if lcom4_vals else None,
        'lsa_acs_mean': round(float(np.mean(lsa_vals)),   4) if lsa_vals   else None,
        'skipped':      skipped,
    }


# ── Entry point ────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description='Compute LCOM4 + LSA-ACS per TrainTicket service for M-SEISMIC comparison.'
    )
    parser.add_argument('--batch_dir',     default='train-ticket',
                        help='Root of train-ticket repo')
    parser.add_argument('--m_seismic_csv', default='m_seismic_results.csv',
                        help='Existing m_seismic_results.csv to merge with')
    parser.add_argument('--output',        default='m_seismic_comparison.csv')
    args = parser.parse_args()

    # Load existing M-SEISMIC results
    m_seismic = {}
    if os.path.isfile(args.m_seismic_csv):
        with open(args.m_seismic_csv) as f:
            for row in csv.DictReader(f):
                m_seismic[row['service']] = row

    entries = sorted(os.listdir(args.batch_dir))
    results = []

    print(f"Scoring LCOM4 + LSA-ACS for ts-* services under '{args.batch_dir}' …\n")
    for entry in entries:
        path = os.path.join(args.batch_dir, entry)
        if not os.path.isdir(path) or not entry.startswith('ts-'):
            continue

        print(f"  {entry} …", end=' ', flush=True)
        bl  = score_service_baselines(path)
        ms  = m_seismic.get(entry, {})

        row = {
            'service':      entry,
            'num_classes':  bl['n_classes'],
            'm_seismic':    ms.get('score', 'N/A'),
            'lcom4_mean':   bl['lcom4_mean']   if bl['lcom4_mean']   is not None else 'N/A',
            'lsa_acs_mean': bl['lsa_acs_mean'] if bl['lsa_acs_mean'] is not None else 'N/A',
            'verdict':      ms.get('verdict', ''),
        }
        results.append(row)
        print(f"M-SEISMIC={row['m_seismic']}  LCOM4={row['lcom4_mean']}  LSA-ACS={row['lsa_acs_mean']}")

    if not results:
        print("No ts-* services found. Check --batch_dir.")
        return

    # Summary
    valid = [r for r in results if r['m_seismic'] not in ('N/A', '', '0.0')]
    if valid:
        ms_vals   = [float(r['m_seismic'])    for r in valid if r['m_seismic']   != 'N/A']
        lcom_vals = [float(r['lcom4_mean'])   for r in valid if r['lcom4_mean']  != 'N/A']
        lsa_vals  = [float(r['lsa_acs_mean']) for r in valid if r['lsa_acs_mean']!= 'N/A']
        print(f"\nSummary across {len(valid)} services with M-SEISMIC scores:")
        if ms_vals:
            print(f"  M-SEISMIC mean = {np.mean(ms_vals):.4f}")
        if lcom_vals:
            print(f"  LCOM4     mean = {np.mean(lcom_vals):.4f}")
        if lsa_vals:
            print(f"  LSA-ACS   mean = {np.mean(lsa_vals):.4f}")

    fieldnames = ['service', 'num_classes', 'm_seismic', 'lcom4_mean', 'lsa_acs_mean', 'verdict']
    with open(args.output, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"\nComparison written to '{args.output}'.")


if __name__ == '__main__':
    main()
