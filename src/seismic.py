import javalang
import re
import math
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# --- Helper Utilities ---

def split_camel(name):
    if not name: return ""
    name = name.replace('.', ' ')
    return " ".join(re.sub('([a-z])([A-Z])', r'\1 \2', name).split())

def is_domain_type(type_name):
    # Ignore standard primitives, Java library types, and ubiquitous containers
    standard_types = {
        'String', 'Integer', 'Double', 'Float', 'Long', 'Boolean', 'Byte', 'Short', 'Character',
        'List', 'Map', 'Set', 'Collection', 'Iterable', 'Iterator', 'Queue', 'Deque',
        'ArrayList', 'HashMap', 'HashSet', 'LinkedList', 'TreeMap', 'TreeSet', 'LinkedHashMap',
        'int', 'double', 'float', 'void', 'boolean', 'long', 'byte', 'short', 'char',
        'Object', 'Exception', 'RuntimeException', 'Throwable', 'Error',
        # Common Java exception types (boilerplate, not domain vocabulary)
        'IllegalArgumentException', 'IllegalStateException', 'NullPointerException',
        'IndexOutOfBoundsException', 'UnsupportedOperationException', 'ClassCastException',
        'ArithmeticException', 'NumberFormatException', 'ArrayIndexOutOfBoundsException',
        'IOException', 'FileNotFoundException', 'SQLException',
        'Optional', 'Stream', 'Comparable', 'Serializable', 'Cloneable',
        'StringBuilder', 'StringBuffer', 'Number', 'Enum', 'Class',
        # Ubiquitous JDK utility types
        'Date', 'Calendar', 'LocalDate', 'LocalDateTime', 'LocalTime',
        'ZonedDateTime', 'Instant', 'Duration', 'Period',
        'BigDecimal', 'BigInteger', 'AtomicInteger', 'AtomicLong',
        'URL', 'URI', 'File', 'Path', 'InputStream', 'OutputStream',
        'UUID', 'Random', 'Scanner',
    }
    return type_name not in standard_types

# Method names that carry no domain semantics (accessors, standard library operations)
TRIVIAL_METHODS = {
    'toString', 'equals', 'hashCode', 'compareTo', 'getClass',
    'notify', 'notifyAll', 'wait', 'clone', 'finalize',
    'get', 'set', 'add', 'remove', 'put', 'contains', 'containsKey', 'containsValue',
    'size', 'length', 'isEmpty', 'clear', 'iterator', 'next', 'hasNext',
    'println', 'print', 'printf', 'format', 'append', 'insert', 'delete',
    'valueOf', 'parseInt', 'parseLong', 'parseDouble', 'parseFloat', 'parseBoolean',
    'trim', 'strip', 'split', 'join', 'substring', 'replace', 'replaceAll',
    'toLowerCase', 'toUpperCase', 'startsWith', 'endsWith', 'charAt', 'indexOf',
    'stream', 'map', 'filter', 'collect', 'toList', 'toArray', 'toSet',
    'sort', 'sorted', 'distinct', 'limit', 'skip', 'reduce', 'count',
    'read', 'write', 'flush', 'close', 'open',
    'now', 'of', 'from', 'to', 'with', 'at', 'by',
    'abs', 'max', 'min', 'pow', 'sqrt', 'round', 'ceil', 'floor', 'random',
    'asList', 'singletonList', 'unmodifiableList', 'emptyList',
    'getBytes', 'getChars', 'encode', 'decode',
    'newInstance', 'forName', 'invoke',
}

# Stop words for filtering tokens extracted from string literals
_STRING_STOP = {
    'this', 'that', 'with', 'from', 'into', 'null', 'true', 'false',
    'void', 'return', 'class', 'static', 'final', 'public', 'private',
    'error', 'exception', 'message', 'value', 'result', 'data', 'item',
    'object', 'type', 'name', 'info', 'util', 'helper', 'manager',
    'using', 'when', 'then', 'else', 'case', 'break', 'have', 'been',
}


def _generic_args(type_node):
    """Yield domain type names from generic type arguments (e.g. List<Order> -> 'Order')."""
    if not hasattr(type_node, 'arguments') or not type_node.arguments:
        return
    for arg in type_node.arguments:
        if hasattr(arg, 'type') and hasattr(arg.type, 'name') and is_domain_type(arg.type.name):
            yield split_camel(arg.type.name)


def extract_body_terms(method_node):
    """
    Extract semantic terms from a method body to enrich P_i beyond its signature:
      - Non-trivial method invocation names  (behavioral vocabulary)
      - Domain types instantiated via 'new'  (object creation context)
      - Local variable names and non-primitive types (including generics)
      - Meaningful tokens from String literals (domain event / query vocabulary)
    """
    body_terms = []

    # A. Non-trivial method invocations (e.g. calculateInterest, processOrder)
    for _, inv in method_node.filter(javalang.tree.MethodInvocation):
        if inv.member not in TRIVIAL_METHODS:
            body_terms.append(split_camel(inv.member))

    # B. Object creation types: new Order(), new PaymentRequest()
    for _, creator in method_node.filter(javalang.tree.ClassCreator):
        if hasattr(creator, 'type') and hasattr(creator.type, 'name'):
            if is_domain_type(creator.type.name):
                body_terms.append(split_camel(creator.type.name))

    # C. Local variable declarations: name + non-primitive type + generic args
    for _, decl in method_node.filter(javalang.tree.LocalVariableDeclaration):
        if hasattr(decl, 'type') and hasattr(decl.type, 'name'):
            if is_domain_type(decl.type.name):
                body_terms.append(split_camel(decl.type.name))
            body_terms.extend(_generic_args(decl.type))
        if hasattr(decl, 'declarators'):
            for var in decl.declarators:
                if len(var.name) > 2:          # skip loop indices i, j, k
                    body_terms.append(split_camel(var.name))

    # D. Meaningful tokens from String literals (domain events, SQL tables, codes)
    for _, lit in method_node.filter(javalang.tree.Literal):
        val = lit.value
        if val and val.startswith('"') and len(val) > 6:
            content = val.strip('"').replace('_', ' ').replace('-', ' ').replace('.', ' ')
            words = [w for w in re.findall(r'[A-Za-z]{5,}', content)
                     if w.lower() not in _STRING_STOP]
            body_terms.extend(words[:3])   # cap per literal to limit noise

    return body_terms


# --- Phase 1 & 2: Static Analysis and Core Extraction ---

def extract_semantic_data(code):
    """Extracts namespace, class name, methods, and shared attributes."""
    tree = javalang.parse.parse(code)

    # Domain Context (Namespace + Class)
    package_name = split_camel(tree.package.name) if tree.package else ""
    class_node = [node for _, node in tree if isinstance(node, javalang.tree.ClassDeclaration)][0]
    class_name = split_camel(class_node.name)
    domain_anchor = f"{package_name} {class_name}".strip()

    # Attributes Inventory
    all_fields = {node.name for _, node in tree if isinstance(node, javalang.tree.VariableDeclarator)}

    method_data = {}
    term_usage = {}

    for _, node in tree.filter(javalang.tree.MethodDeclaration):
        # A. Attribute Accesses (State Interaction)
        used_fields = [child.member for _, child in node.filter(javalang.tree.MemberReference)
                       if child.member in all_fields]

        # B. Parameters and Types (Domain Logic)
        params_info = []
        for param in node.parameters:
            params_info.append(split_camel(param.name))
            if hasattr(param.type, 'name') and is_domain_type(param.type.name):
                params_info.append(split_camel(param.type.name))
            params_info.extend(_generic_args(param.type))

        # C. Return Type (and its generic arguments)
        if hasattr(node, 'return_type') and node.return_type and is_domain_type(node.return_type.name):
            params_info.append(split_camel(node.return_type.name))
            params_info.extend(_generic_args(node.return_type))

        # D. Method body: invocations, object creations, locals, string tokens
        body_terms = extract_body_terms(node)

        # Construct Semantic Phrase
        phrase_terms = ([split_camel(node.name)]
                        + [split_camel(f) for f in used_fields]
                        + params_info
                        + body_terms)
        unique_terms = list(set(phrase_terms))

        method_data[node.name] = {
            "label": split_camel(node.name),
            "terms": unique_terms,
            "accessed_fields": set(used_fields)
        }

        # Count frequencies for Core extraction
        for term in unique_terms:
            term_usage[term] = term_usage.get(term, 0) + 1

    # Define Latent Semantic Core (Terms with frequency > 1)
    shared_terms = [t for t, count in term_usage.items() if count > 1]

    return domain_anchor, method_data, shared_terms, all_fields

# --- Phase 3 & 4: Scoring Engine ---

def calculate_seismic_score(file_path, model_name='all-MiniLM-L6-v2', verbose=True):
    if verbose:
        print(f"{'='*30} seismic Score Calculation {'='*30}")

    model = SentenceTransformer(model_name)

    with open(file_path, 'r', encoding='utf-8') as f:
        code = f.read()

    # 1. Extraction
    domain_anchor, method_data, shared_terms, all_fields = extract_semantic_data(code)
    num_methods = len(method_data)
    if num_methods == 0: return 0.0

    # 2. Build and Encode Core
    core_string = f"{domain_anchor} {' '.join(shared_terms)}"
    core_emb = model.encode([core_string])
    if verbose:
        print(f"--- seismic Analysis: Domain Core ({domain_anchor}) ---")

    # 3. Method Alignment (Phi)
    alignments = []
    for m_name, data in method_data.items():
        if verbose:
            print(f"-- Analyzing Method: {m_name}() with terms {data['terms']}")
        m_phrase = " ".join(data['terms'])
        m_emb = model.encode([m_phrase])

        # Cosine Similarity with Quadratic Boost
        sim = max(0, cosine_similarity(m_emb, core_emb)[0][0])
        boosted_score = math.sqrt(sim)

        # Silo Penalty (if method has no intersection with core)
        has_intersection = any(t in shared_terms for t in data['terms'])
        if not has_intersection:
            boosted_score *= 0.5

        alignments.append(boosted_score)
        if verbose:
            print(f"\t Method: {m_name:25} | Sim: {sim:.3f} | Boosted: {boosted_score:.4f}")

    phi = np.mean(alignments)
    if verbose:
        print(f"Average Alignment (Phi): {phi:.4f}")

    # 4. Complexity Penalties (Omega)
    # T_M: Method threshold, T_S: Core term threshold
    # lambda_m calibrated via cross-validation on SmellyCode++ training split
    omega_m = math.exp(-0.005 * max(0, num_methods - 15))
    omega_s = math.exp(-0.030 * max(0, len(shared_terms) - 20))
    omega = omega_m * omega_s
    if verbose:
        print(f"Complexity Penalties - Omega_m: {omega_m:.4f}, Omega_s: {omega_s:.4f}, Omega: {omega:.4f}")

    # 5. State Density Bonus (B)
    # Intersection of shared terms and actual class attributes
    shared_attrs = [t for t in shared_terms if t.replace(" ", "") in all_fields]
    bonus = min(0.15, (len(shared_attrs) / num_methods) * 0.1)
    if verbose:
        print(f"State Density Bonus (B): {bonus:.4f} based on {len(shared_attrs)} shared attribute(s)")

    # 6. Final Aggregation
    final_score = (phi * omega) + bonus
    if verbose:
        print(f"{'='*90}\n{' '*30}Final seismic Score: {final_score:.4f}")
        print(f"{'='*90}\n")
    return min(1.0, final_score)

if __name__ == "__main__":
    import shutil, os

    # --- Execution for some examples ---
    # Cohesive Class Examples: seismic score greater than 0.70
    #calculate_seismic_score("OrderProcessor.java") # seismic=0.7329
    #calculate_seismic_score("BankAccount.java")    # seismic=0.7333
    # Non-Cohesive Class Examples: seismic score less than 0.15
    #calculate_seismic_score("UtilityManager.java") # Non-Single Responsibility. seismic=0.0464
    #calculate_seismic_score("SystemManager.java")  # Non-Single Responsibility. seismic=0.1039
    #calculate_seismic_score("GodClass_444.java")   # Huge Class. seismic=0.0068
    #calculate_seismic_score("GodClass_2931.java")  # Huge Class. seismic=0.0152
    # Mixed:
    #calculate_seismic_score("GodClass_1642.java")  # Large but cohesive. seismic=0.0152

    # --- Batch Processing for the whole dataset with Error Handling ---
    JAVA_DIR = "dataset/sample_ng_classes"
    ERROR_DIR = "dataset/ng_error_classes"
    moved = 0

    os.makedirs(ERROR_DIR, exist_ok=True)

    for filename in os.listdir(JAVA_DIR):
        if filename.endswith(".java"):
            file_path = os.path.join(JAVA_DIR, filename)
            print(f"\n=== Analysing: {filename} ===")
            try:
                calculate_seismic_score(file_path)
            except Exception as e:
                print(f"ERROR: Could not parse {filename}. Reason: {e}")
                destination = os.path.join(ERROR_DIR, filename)
                shutil.move(file_path, destination)
                print(f"MOVED: {filename} -> {ERROR_DIR}")
                moved += 1

    print(f"\nTotal files moved to error folder: {moved}")
    print("\nProcessing complete.")
