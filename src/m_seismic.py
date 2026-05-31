"""
M-SEISMIC: Module-Level SEISMIC for Microservice Coherence.

Implements Equations 7–8 from Section III of the paper.

The Module Semantic Core (Φ_M) is defined as the set of terms that appear
in the Φ_core of MORE THAN ONE class in the service. This cross-class
frequency filter isolates the shared domain vocabulary from idiosyncratic
implementation details of individual classes.

Outlier Inflation Penalty (Ω_ext = 0.5): applied to any class whose core
shares no terms with Φ_M, identifying it as a Bounded Context Outlier.

Suggested TrainTicket services for Table XIII:
    ts-auth-service, ts-order-service, ts-station-service,
    ts-travel-service, ts-price-service, ts-route-service,
    ts-user-service, ts-admin-basic-info-service,
    ts-inside-payment-service, ts-notification-service

Usage:
    # Clone TrainTicket first:
    #   git clone https://github.com/FudanSELab/train-ticket.git

    # Score one service:
    python m_seismic.py --service_dir train-ticket/ts-order-service

    # Score all ts-* services under a root:
    python m_seismic.py --batch_dir train-ticket --output m_seismic_results.csv
"""

import argparse
import csv
import os
import sys
from collections import Counter

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# ── Re-use the enriched extraction logic from seismic.py ─────────────────────
# This ensures M-SEISMIC benefits from the same body enrichment (method
# invocations, object creations, local variable names/types, string tokens),
# the extended is_domain_type filter, and the TRIVIAL_METHODS guard that
# the class-level metric uses.
sys.path.insert(0, os.path.dirname(__file__))
from seismic import (
    split_camel,
    is_domain_type,
    _generic_args,
    extract_body_terms,
)
import javalang


def extract_class_core(code):
    """
    Extracts (domain_anchor, shared_terms) for the first ClassDeclaration
    found in `code`, using the same enriched phrase construction as the
    class-level SEISMIC metric (signature + body terms).

    domain_anchor — "{package} {ClassName}" split by camelCase
    shared_terms  — terms appearing in more than one method's semantic phrase

    Returns None if no ClassDeclaration is found or the class has no methods.
    Raises javalang.parser.JavaSyntaxError on unparseable input.
    """
    tree = javalang.parse.parse(code)

    class_nodes = [
        n for _, n in tree
        if isinstance(n, javalang.tree.ClassDeclaration)
    ]
    if not class_nodes:
        return None

    class_node    = class_nodes[0]
    package_name  = split_camel(tree.package.name) if tree.package else ""
    class_name    = split_camel(class_node.name)
    domain_anchor = f"{package_name} {class_name}".strip()

    all_fields = {
        n.name for _, n in tree
        if isinstance(n, javalang.tree.VariableDeclarator)
    }

    term_usage = {}
    num_methods = 0
    for _, node in tree.filter(javalang.tree.MethodDeclaration):
        num_methods += 1

        used_fields = [
            c.member for _, c in node.filter(javalang.tree.MemberReference)
            if c.member in all_fields
        ]
        params_info = []
        for param in node.parameters:
            params_info.append(split_camel(param.name))
            if hasattr(param.type, 'name') and is_domain_type(param.type.name):
                params_info.append(split_camel(param.type.name))
            params_info.extend(_generic_args(param.type))
        if (hasattr(node, 'return_type') and node.return_type
                and is_domain_type(node.return_type.name)):
            params_info.append(split_camel(node.return_type.name))
            params_info.extend(_generic_args(node.return_type))

        body_terms = extract_body_terms(node)

        phrase_terms = (
            [split_camel(node.name)]
            + [split_camel(f) for f in used_fields]
            + params_info
            + body_terms
        )
        for t in set(phrase_terms):
            term_usage[t] = term_usage.get(t, 0) + 1

    if num_methods == 0:
        return None

    shared_terms = frozenset(t for t, c in term_usage.items() if c > 1)
    return domain_anchor, shared_terms


def is_analysis_candidate(code):
    """
    Returns False for interfaces, abstract classes, JUnit test classes, and
    Spring framework infrastructure classes whose vocabulary is governed by
    the framework contract rather than domain semantics.

    Framework infrastructure classes (SecurityConfigurerAdapter subclasses,
    OncePerRequestFilter subclasses, @Configuration-only classes) contain
    method names and parameter types that belong entirely to the Spring/Jakarta
    API vocabulary.  Including them pollutes the Module Semantic Core with
    framework terms and wrongly flags domain classes as Bounded Context Outliers.
    """
    if 'interface ' in code:
        return False
    if '@Test' in code or 'extends TestCase' in code:
        return False
    if 'abstract class' in code:
        return False
    # Spring Security / Servlet filter infrastructure
    if ('WebSecurityConfigurerAdapter' in code
            or 'SecurityConfigurerAdapter' in code
            or 'OncePerRequestFilter' in code
            or 'extends HttpFilter' in code):
        return False
    # Pure @Configuration classes with no domain state (no instance fields)
    if '@Configuration' in code and 'private ' not in code:
        return False
    return True


def collect_java_files(directory):
    """Recursively collects all .java file paths under `directory`."""
    results = []
    for root, _, files in os.walk(directory):
        for filename in files:
            if filename.endswith('.java'):
                results.append(os.path.join(root, filename))
    return results


# ── M-SEISMIC core computation ─────────────────────────────────────────────────

def compute_m_seismic(service_dir, model, service_name=None):
    """
    Computes M-SEISMIC for a single microservice directory.

    Steps:
      1. Extract Φ_core(C_i) for each valid class in the service.
      2. Build Φ_M = {terms appearing in more than one class's Φ_core}.
         If Φ_M is empty (all classes have disjoint vocabularies), fall back
         to the full union of cores.
      3. Encode Φ_M and each class core as sentence embeddings.
      4. For each class: compute cosine similarity to Φ_M; halve if
         Φ_core(C_i) ∩ Φ_M = ∅ (Bounded Context Outlier).
      5. Average alignments -> M-SEISMIC score.

    Returns a dict with all intermediate metrics for reporting.
    """
    if service_name is None:
        service_name = os.path.basename(os.path.normpath(service_dir))

    java_files = collect_java_files(service_dir)
    class_cores = []   # list of (domain_anchor, frozenset of shared_terms)
    skipped = 0

    for path in java_files:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                code = f.read()
            if not is_analysis_candidate(code):
                continue
            result = extract_class_core(code)
            if result is None:
                continue
            class_cores.append(result)
        except Exception:
            skipped += 1

    num_classes = len(class_cores)
    if num_classes == 0:
        return {
            'service':     service_name,
            'num_classes': 0,
            'phi_m_size':  0,
            'score':       0.0,
            'outliers':    0,
            'skipped':     skipped,
            'verdict':     'No parseable classes found',
        }

    # ── Step 2: Build Φ_M via cross-class term frequency ─────────────────────
    term_class_count = Counter()
    for _, core_terms in class_cores:
        for t in core_terms:
            term_class_count[t] += 1

    phi_m = frozenset(t for t, cnt in term_class_count.items() if cnt > 1)

    # Fallback: if every class has a unique vocabulary, use the full union
    if not phi_m:
        phi_m = frozenset(t for _, core in class_cores for t in core)

    # ── Step 3: Encode Φ_M ───────────────────────────────────────────────────
    phi_m_str = " ".join(sorted(phi_m))
    phi_m_emb = model.encode([phi_m_str])

    # ── Step 4: Align each class to Φ_M ──────────────────────────────────────
    alignments   = []
    outlier_count = 0

    for domain_anchor, core_terms in class_cores:
        class_str = f"{domain_anchor} {' '.join(sorted(core_terms))}"
        class_emb = model.encode([class_str])
        sim = max(0.0, float(cosine_similarity(class_emb, phi_m_emb)[0][0]))
        score_i = sim ** 0.5  # Quadratic Coherence Boost (Algorithm 1, line 18)

        # Outlier Inflation Penalty Ω_ext (Algorithm 1, line 19)
        if not core_terms.intersection(phi_m):
            score_i *= 0.5
            outlier_count += 1

        alignments.append(score_i)

    score = round(float(np.mean(alignments)), 4)

    return {
        'service':     service_name,
        'num_classes': num_classes,
        'phi_m_size':  len(phi_m),
        'score':       score,
        'outliers':    outlier_count,
        'skipped':     skipped,
        'verdict':     _verdict(score),
    }


def _verdict(score):
    if score >= 0.70:
        return "Focused Bounded Context"
    if score >= 0.50:
        return "Coherent — Monitor for Drift"
    if score >= 0.25:
        return "Context Leakage Risk — Review"
    return "Distributed Monolith — Decompose"


# ── Batch runner ───────────────────────────────────────────────────────────────

# TrainTicket services selected to span a range of expected cohesion
# (from highly focused to utility-heavy / cross-domain)
TRAIN_TICKET_SERVICES = [
    'ts-auth-service',
    'ts-order-service',
    'ts-station-service',
    'ts-travel-service',
    'ts-price-service',
    'ts-route-service',
    'ts-user-service',
    'ts-admin-basic-info-service',
    'ts-inside-payment-service',
    'ts-notification-service',
]


def run_batch(batch_dir, output_csv, model, only_ts=True):
    """
    Scores every service directory under `batch_dir`.

    If `only_ts` is True, only directories whose name starts with 'ts-' are
    included, matching the TrainTicket naming convention.
    """
    results = []

    entries = sorted(os.listdir(batch_dir))
    for entry in entries:
        service_path = os.path.join(batch_dir, entry)
        if not os.path.isdir(service_path):
            continue
        if only_ts and not entry.startswith('ts-'):
            continue

        print(f"  Scoring '{entry}' …")
        result = compute_m_seismic(service_path, model, service_name=entry)
        results.append(result)
        print(
            f"    -> M-SEISMIC: {result['score']:.4f} | "
            f"{result['num_classes']} classes | "
            f"{result['outliers']} outliers | "
            f"{result['verdict']}"
        )

    if not results:
        print("No services found. Check --batch_dir and that services start with 'ts-'.")
        return

    fieldnames = ['service', 'num_classes', 'phi_m_size', 'score',
                  'outliers', 'skipped', 'verdict']
    with open(output_csv, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    scores = [r['score'] for r in results if r['num_classes'] > 0]
    if scores:
        print(f"\nSummary across {len(scores)} services:")
        print(f"  Mean   : {np.mean(scores):.4f}")
        print(f"  Median : {np.median(scores):.4f}")
        print(f"  Min    : {min(scores):.4f}  ({results[scores.index(min(scores))]['service']})")
        print(f"  Max    : {max(scores):.4f}  ({results[scores.index(max(scores))]['service']})")

    print(f"\nFull results written to '{output_csv}'.")


# ── Entry point ────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="M-SEISMIC: module-level coherence for microservices."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '--service_dir',
        help='Root directory of a single microservice (e.g. train-ticket/ts-order-service)',
    )
    group.add_argument(
        '--batch_dir',
        help='Root directory containing multiple ts-* service folders (e.g. train-ticket/)',
    )
    parser.add_argument(
        '--output', default='m_seismic_results.csv',
        help='Output CSV for batch mode',
    )
    parser.add_argument(
        '--all_services', action='store_true',
        help='In batch mode, include all subdirectories, not only ts-* ones',
    )
    args = parser.parse_args()

    print("Loading transformer model (all-MiniLM-L6-v2) …")
    model = SentenceTransformer('all-MiniLM-L6-v2')

    if args.service_dir:
        if not os.path.isdir(args.service_dir):
            print(f"Error: '{args.service_dir}' is not a directory.")
            return
        print(f"\nScoring service: {args.service_dir}")
        result = compute_m_seismic(args.service_dir, model)
        print(f"\n{'─'*50}")
        print(f"Service        : {result['service']}")
        print(f"Classes scored : {result['num_classes']}  (skipped: {result['skipped']})")
        print(f"Φ_M size       : {result['phi_m_size']} shared terms")
        print(f"Outlier classes: {result['outliers']}")
        print(f"M-SEISMIC      : {result['score']:.4f}")
        print(f"Verdict        : {result['verdict']}")
        print(f"{'─'*50}")
    else:
        if not os.path.isdir(args.batch_dir):
            print(f"Error: '{args.batch_dir}' is not a directory.")
            return
        print(f"\nBatch mode: scoring services under '{args.batch_dir}' …")
        run_batch(
            args.batch_dir,
            args.output,
            model,
            only_ts=not args.all_services,
        )


if __name__ == '__main__':
    main()
