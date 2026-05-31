"""
SEISMIC Baseline Metrics — Extended Implementation
===================================================
Implements the seven cohesion baselines evaluated in Section 4 of the paper.
All public scorers accept a Java source file path and return a float in [0, 1],
or None on parse failure.  For files containing multiple classes the score is
the mean over all parsed classes.

Metric                Reference
------                ---------
LCOM4   (normalized)  Hitz & Montazeri (1995)
TCC                   Bieman & Kang (1995)
C3                    Marcus et al. (2005, 2008)
LSCC    (Dice)        Poshyvanyk & Marcus (2006)
LDA-CS               Bavota et al. (2010)
C3-Full              Marcus et al. (2008), full-AST variant (this study)
WSS                  0.5·LCOM4 + 0.5·C3  (this study)
"""

import re
import math
import warnings
import numpy as np
import javalang
import networkx as nx
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD, LatentDirichletAllocation
from sklearn.metrics.pairwise import cosine_similarity

warnings.filterwarnings("ignore")


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _camel_split(name: str) -> str:
    """Split camelCase identifiers into lowercase tokens."""
    if not name:
        return ""
    name = re.sub(r'[^a-zA-Z]', ' ', name)
    tokens = re.findall(r'[A-Z]?[a-z]+|[A-Z]+(?=[A-Z]|$)', name)
    return " ".join(tokens).lower()


def _parse(file_path: str):
    """Return (source, tree) or raise on failure."""
    with open(file_path, "r", encoding="utf-8", errors="replace") as fh:
        source = fh.read()
    return source, javalang.parse.parse(source)


def _instance_fields(class_decl) -> set:
    fields = set()
    for field in class_decl.fields:
        if "static" not in field.modifiers:
            for decl in field.declarators:
                fields.add(decl.name)
    return fields


def _instance_methods(class_decl) -> list:
    return [m for m in class_decl.methods if "static" not in m.modifiers]


def _field_access_map(methods, instance_fields) -> dict:
    """For each method, the set of instance fields it accesses."""
    access = {m.name: set() for m in methods}
    for method in methods:
        if method.body is None:
            continue
        for _, node in method:
            if isinstance(node, javalang.tree.MemberReference):
                if node.member in instance_fields:
                    access[method.name].add(node.member)
    return access


def _method_call_map(methods) -> dict:
    """For each method, the set of sibling methods it directly calls."""
    names = {m.name for m in methods}
    calls = {m.name: set() for m in methods}
    for method in methods:
        if method.body is None:
            continue
        for _, node in method:
            if isinstance(node, javalang.tree.MethodInvocation):
                if node.member in names and node.member != method.name:
                    calls[method.name].add(node.member)
    return calls


def _mean_over_classes(file_path: str, scorer_fn) -> float | None:
    """Parse the file, apply scorer_fn to each class, return the mean."""
    try:
        source, tree = _parse(file_path)
    except Exception:
        return None
    scores = []
    for _, cls in tree.filter(javalang.tree.ClassDeclaration):
        s = scorer_fn(cls, source)
        if s is not None:
            scores.append(s)
    return float(np.mean(scores)) if scores else None


def _avg_pairs(n: int) -> float:
    """Number of unique unordered pairs for n items."""
    return n * (n - 1) / 2


# ---------------------------------------------------------------------------
# 1. LCOM4 — Hitz & Montazeri (1995)
# ---------------------------------------------------------------------------
# Graph: methods = nodes; edge if they share an instance field access OR one
# directly calls the other.  Cohesion = 1 / number_of_connected_components.
# A fully connected class scores 1.0; each additional isolated sub-graph
# halves (or further reduces) the score.

def _lcom4_class(cls, _source) -> float | None:
    fields = _instance_fields(cls)
    methods = _instance_methods(cls)
    if len(methods) <= 1:
        return 1.0

    access = _field_access_map(methods, fields)
    calls  = _method_call_map(methods)

    G = nx.Graph()
    G.add_nodes_from(m.name for m in methods)
    names = [m.name for m in methods]
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            if access[names[i]] & access[names[j]]:
                G.add_edge(names[i], names[j])
    for caller, callees in calls.items():
        for callee in callees:
            G.add_edge(caller, callee)

    k = nx.number_connected_components(G)
    return round(1.0 / k, 4) if k > 0 else 0.0


def lcom4(file_path: str) -> float | None:
    """LCOM4 normalized to [0,1] via 1/num_components."""
    return _mean_over_classes(file_path, _lcom4_class)


# ---------------------------------------------------------------------------
# 2. TCC — Bieman & Kang (1995)
# ---------------------------------------------------------------------------
# TCC = NDC / NP  where NDC is the number of directly connected method pairs
# (pairs sharing at least one instance field access) and NP = n*(n-1)/2.
# A class where every pair shares a field scores 1.0; a class with no shared
# fields scores 0.0.

def _tcc_class(cls, _source) -> float | None:
    fields  = _instance_fields(cls)
    methods = _instance_methods(cls)
    n = len(methods)
    if n <= 1:
        return 1.0

    access = _field_access_map(methods, fields)
    names  = [m.name for m in methods]
    ndc    = 0
    for i in range(n):
        for j in range(i + 1, n):
            if access[names[i]] & access[names[j]]:
                ndc += 1

    np_ = _avg_pairs(n)
    return round(ndc / np_, 4) if np_ > 0 else 0.0


def tcc(file_path: str) -> float | None:
    """Tight Class Cohesion (Bieman & Kang 1995)."""
    return _mean_over_classes(file_path, _tcc_class)


# ---------------------------------------------------------------------------
# 3. C3 — Marcus et al. (2005, 2008)
# ---------------------------------------------------------------------------
# Each method is represented as a TF-IDF vector over its lexical tokens
# (method name + parameter names/types + field accesses), projected into a
# latent semantic space via truncated SVD (LSA).  Cohesion is the average
# pairwise cosine similarity across all methods.

def _c3_method_doc(method) -> str:
    # Replicates baseline.py: str(child) for all AST nodes that have a .name
    # attribute, then clean_and_tokenize the full concatenation.  The string
    # representation of javalang nodes includes node-type tokens
    # (e.g. "MethodInvocation", "MemberReference") alongside identifier names,
    # giving the rich vocabulary that produces C3 ≈ 0.77 for Expert Monoliths.
    body_parts = " ".join(
        str(child)
        for _, child in method
        if hasattr(child, 'name')
    )
    return _camel_split(method.name + " " + body_parts)


def _c3_class(cls, _source) -> float | None:
    methods = cls.methods + cls.constructors
    if len(methods) < 2:
        return 1.0

    docs = [_c3_method_doc(m) for m in methods]
    try:
        vectorizer  = TfidfVectorizer(min_df=1)
        tfidf       = vectorizer.fit_transform(docs)
        n_comp      = min(10, tfidf.shape[1] - 1)
        if n_comp > 0:
            latent = TruncatedSVD(n_components=n_comp, random_state=0).fit_transform(tfidf)
        else:
            latent = tfidf.toarray()
        sim   = cosine_similarity(latent)
        n     = len(methods)
        total = np.sum(np.triu(sim, k=1))
        return round(float(total / _avg_pairs(n)), 4)
    except Exception:
        return None


def c3(file_path: str) -> float | None:
    """Conceptual Cohesion of Classes — TF-IDF + SVD (Marcus et al. 2005/2008)."""
    return _mean_over_classes(file_path, _c3_class)


# ---------------------------------------------------------------------------
# 4. LSCC — Sørensen-Dice field interaction
#    (Poshyvanyk & Marcus 2006, structural instantiation)
# ---------------------------------------------------------------------------
# For each pair of methods (mi, mj):
#   Dice(mi, mj) = 2 |Ai ∩ Aj| / (|Ai| + |Aj|)
# where Ai is the set of instance fields accessed by mi.
# Pairs where both methods access no fields contribute Dice = 0 (no bond).
# LSCC = mean Dice over all pairs.

def _lscc_class(cls, _source) -> float | None:
    fields  = _instance_fields(cls)
    methods = _instance_methods(cls)
    n = len(methods)
    if n <= 1:
        return 1.0

    access = _field_access_map(methods, fields)
    names  = [m.name for m in methods]
    scores = []
    for i in range(n):
        for j in range(i + 1, n):
            ai, aj = access[names[i]], access[names[j]]
            denom  = len(ai) + len(aj)
            if denom == 0:
                scores.append(0.0)
            else:
                scores.append(2 * len(ai & aj) / denom)

    return round(float(np.mean(scores)), 4) if scores else 0.0


def lscc(file_path: str) -> float | None:
    """LSCC — Sørensen-Dice field interaction (Poshyvanyk & Marcus 2006)."""
    return _mean_over_classes(file_path, _lscc_class)


# ---------------------------------------------------------------------------
# 5. LDA-CS — LDA-based Cohesion Score (Bavota et al. 2010)
# ---------------------------------------------------------------------------
# Each method is represented as a bag of lexical tokens (method name + body
# identifiers).  Latent Dirichlet Allocation produces a topic distribution
# for each method.  Cohesion is the average pairwise cosine similarity
# between per-method topic distributions.

def _lda_method_doc(method) -> str:
    terms = [_camel_split(method.name)]
    if method.body:
        for _, node in method:
            if isinstance(node, javalang.tree.MemberReference):
                terms.append(_camel_split(node.member))
            elif isinstance(node, javalang.tree.MethodInvocation):
                terms.append(_camel_split(node.member))
    return " ".join(t for t in terms if t.strip())


def _lda_class(cls, _source) -> float | None:
    methods = cls.methods + cls.constructors
    n = len(methods)
    if n < 2:
        return 1.0

    docs = [_lda_method_doc(m) for m in methods]
    try:
        vectorizer = TfidfVectorizer(min_df=1)
        dtm        = vectorizer.fit_transform(docs)
        if dtm.shape[1] == 0:
            return None
        n_topics   = min(max(2, n - 1), 10)
        lda        = LatentDirichletAllocation(
            n_components=n_topics, random_state=0,
            max_iter=20, learning_method="batch"
        )
        topic_dist = lda.fit_transform(dtm)
        sim        = cosine_similarity(topic_dist)
        total      = np.sum(np.triu(sim, k=1))
        return round(float(total / _avg_pairs(n)), 4)
    except Exception:
        return None


def lda_cs(file_path: str) -> float | None:
    """LDA-based Cohesion Score (Bavota et al. 2010)."""
    return _mean_over_classes(file_path, _lda_class)


# ---------------------------------------------------------------------------
# 6. C3-Full — full-identifier TF-IDF, no SVD (Marcus et al. 2008, variant)
# ---------------------------------------------------------------------------
# A full-identifier, vector-space variant of C3.  Each method is represented
# as a TF-IDF vector constructed from an exhaustive identifier vocabulary
# extracted via AST traversal: method name, parameter names and types, field
# accesses, method invocations, local variable declarators, and type
# references.  No latent semantic projection (SVD) is applied.

def _c3full_method_doc(method) -> str:
    terms = [_camel_split(method.name)]

    for param in method.parameters:
        terms.append(_camel_split(param.name))
        if hasattr(param.type, 'name'):
            terms.append(_camel_split(param.type.name))

    if hasattr(method, 'return_type') and method.return_type:
        terms.append(_camel_split(method.return_type.name))

    if method.body:
        for _, node in method:
            if isinstance(node, javalang.tree.MemberReference):
                terms.append(_camel_split(node.member))
            elif isinstance(node, javalang.tree.MethodInvocation):
                terms.append(_camel_split(node.member))
            elif isinstance(node, javalang.tree.LocalVariableDeclaration):
                if hasattr(node, 'type') and hasattr(node.type, 'name'):
                    terms.append(_camel_split(node.type.name))
                if hasattr(node, 'declarators'):
                    for var in node.declarators:
                        terms.append(_camel_split(var.name))
            elif isinstance(node, javalang.tree.ClassCreator):
                if hasattr(node, 'type') and hasattr(node.type, 'name'):
                    terms.append(_camel_split(node.type.name))
            elif isinstance(node, javalang.tree.ReferenceType):
                if hasattr(node, 'name'):
                    terms.append(_camel_split(node.name))

    return " ".join(t for t in terms if t.strip())


def _c3full_class(cls, _source) -> float | None:
    methods = cls.methods + cls.constructors
    n = len(methods)
    if n < 2:
        return 1.0

    docs = [_c3full_method_doc(m) for m in methods]
    try:
        vectorizer = TfidfVectorizer(min_df=1)
        tfidf      = vectorizer.fit_transform(docs)
        sim        = cosine_similarity(tfidf)
        total      = np.sum(np.triu(sim, k=1))
        return round(float(total / _avg_pairs(n)), 4)
    except Exception:
        return None


def c3_full(file_path: str) -> float | None:
    """C3-Full — exhaustive-AST TF-IDF without SVD (Marcus et al. 2008, variant)."""
    return _mean_over_classes(file_path, _c3full_class)


# ---------------------------------------------------------------------------
# 7. WSS — Weighted Structural-Semantic (this study)
# ---------------------------------------------------------------------------
# A linear hybrid baseline: WSS = 0.5·LCOM4 + 0.5·C3.
# Constructed to represent the simplest possible structural-semantic
# combination.  Unlike SEISMIC's multiplicative formulation, the fixed linear
# blend cannot selectively penalise structurally inflated classes that
# maintain high semantic similarity.

def wss(file_path: str) -> float | None:
    """WSS = 0.5·LCOM4 + 0.5·C3 (hybrid baseline, this study)."""
    l = lcom4(file_path)
    c = c3(file_path)
    if l is None and c is None:
        return None
    if l is None:
        return c
    if c is None:
        return l
    return round(0.5 * l + 0.5 * c, 4)


# ---------------------------------------------------------------------------
# Batch scorer — returns a dict of all seven metrics for a file
# ---------------------------------------------------------------------------

def score_all(file_path: str) -> dict:
    """
    Score a single Java file with all seven baselines.
    Returns a dict with keys: lcom4, tcc, c3, lscc, lda_cs, c3_full, wss.
    Values are floats in [0,1] or None on parse failure.
    """
    l4 = lcom4(file_path)
    c  = c3(file_path)
    return {
        "lcom4":   l4,
        "tcc":     tcc(file_path),
        "c3":      c,
        "lscc":    lscc(file_path),
        "lda_cs":  lda_cs(file_path),
        "c3_full": c3_full(file_path),
        "wss":     (round(0.5 * l4 + 0.5 * c, 4)
                    if l4 is not None and c is not None else None),
    }


# ---------------------------------------------------------------------------
# CLI — quick sanity check on illustrative examples
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import os, sys

    targets = [
        "OrderProcessor.java",
        "UtilityManager.java",
        "GodClass_444.java",
    ]
    if len(sys.argv) > 1:
        targets = sys.argv[1:]

    header = f"{'File':<40} {'LCOM4':>6} {'TCC':>6} {'C3':>6} {'LSCC':>6} {'LDA':>6} {'C3F':>6} {'WSS':>6}"
    print(header)
    print("-" * len(header))
    for path in targets:
        if not os.path.exists(path):
            print(f"  [not found] {path}")
            continue
        s = score_all(path)
        fmt = lambda v: f"{v:6.3f}" if v is not None else "   n/a"
        print(
            f"{os.path.basename(path):<40}"
            f" {fmt(s['lcom4'])} {fmt(s['tcc'])} {fmt(s['c3'])}"
            f" {fmt(s['lscc'])} {fmt(s['lda_cs'])} {fmt(s['c3_full'])} {fmt(s['wss'])}"
        )
