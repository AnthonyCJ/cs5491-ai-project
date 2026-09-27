"""Independent checks for the supplied baselines using the topic PDF rules.

This is S1 calibration code, not a model or optimiser. Decimal coefficients
are transcribed from Section 4, independently of the handout's float scorer.
All latency values are milliseconds; only Bootstrap costs scale with #ct.
"""

from collections import defaultdict
from decimal import Decimal
from graphlib import CycleError, TopologicalSorter

# operator: (level cost, minimum input level, slope, intercept), PDF pp. 3-4.
RULES = {
    "PCMM1": (2, 2, "366.20", "1797.71"),
    "PCMM2": (2, 2, "104.64", "2262.12"),
    "PCMM3": (2, 2, "443.12", "1581.48"),
    "PCMM4": (2, 2, "377.74", "2095.11"),
    "CCMM1": (4, 4, "529.58", "-159.50"),
    "CCMM2": (2, 2, "98.67", "1566.84"),
    "PolyEval1": (5, 5, "142.64", "-455.72"),
    "PolyEval2": (5, 5, "145.59", "-409.08"),
    "PolyEval3": (8, 8, "562.27", "819.37"),
    "PolyEval4": (8, 8, "460.34", "1311.36"),
    "Mul": (1, 1, "0.0663", "0.4192"),
    "Add": (0, 0, "0.0034", "0.0379"),
    "Conjugate": (0, 0, "0.16", "1.67"),
    "Conjugate back": (0, 0, "0.60", "2.02"),
    "Sum": (0, 0, "0", "4.06"),
    "Rotate": (0, 0, "0", "0"),
    "Identity": (0, 0, "0", "0"),
    "Bootstrap1": (0, 0, "0", "1040.15"),
    "Bootstrap2": (0, 0, "0", "1293.13"),
    "Modswitch": (None, 0, "0", "0"),
}
INSERTED = {"Bootstrap1", "Bootstrap2", "Modswitch"}


def require(condition, message):
    """Raise on a rule violation, including when Python assertions are disabled."""
    if not condition:
        raise ValueError(message)


def audit_baseline(empty_nodes, empty_edges, nodes, edges, l_init, l_max=14):
    """Check graph preservation, chains, levels, charging and exact-decimal cost.

    The graph must be the supplied block plus legal inserted operations. Shared
    prefixes use a single node. Structural checks are independent of the
    reference scorer. The S2 optimiser will need its own model validation too.
    """
    require(type(l_init) is int and 0 <= l_init <= 14, "Invalid input level")
    require(l_max == 14, "S1 requires L_max = 14")
    base = {n[0]: n for n in empty_nodes}
    by_name = {n[0]: n for n in nodes}
    require(len(base) == len(empty_nodes), "Duplicate original node")
    require(len(by_name) == len(nodes), "Duplicate placed node")
    require(set(base) <= set(by_name), "Missing original operator")
    for name, node in base.items():
        require(tuple(by_name[name][:3]) == tuple(node[:3]), f"Changed original node: {name}")
    additions = set(by_name) - set(base)
    require(all(by_name[n][1] in INSERTED for n in additions), "Illegal inserted operator")
    pred, succ = defaultdict(list), defaultdict(list)
    seen_edges = set()
    for u, v, ct in edges:
        require(u in by_name and v in by_name, "Unknown edge endpoint")
        require(type(ct) is int and ct > 0, "Invalid ciphertext count")
        require((u, v) not in seen_edges, "Duplicate edge")
        seen_edges.add((u, v))
        pred[v].append((u, ct))
        succ[u].append((v, ct))
    for name in by_name:
        require(len({ct for _, ct in succ[name]}) <= 1, f"Inconsistent fan-out tensor: {name}")
        if name in additions:
            require(len(pred[name]) == 1 and len(succ[name]) > 0, f"Inserted node arity: {name}")
            require(all(ct == pred[name][0][1] for _, ct in succ[name]), f"Inserted node changes #ct: {name}")
    try:
        order = list(TopologicalSorter({n: [p for p, _ in pred[n]] for n in by_name}).static_order())
    except CycleError as exc:
        raise ValueError("Placed graph contains a cycle") from exc

    # Remove inserted chains virtually and compare the original graph exactly.
    collapsed = []
    chains = []
    used_insertions = set()
    for target in base:
        for parent, ct in pred[target]:
            cursor, chain = parent, []
            while cursor in additions:
                chain.append(cursor)
                used_insertions.add(cursor)
                cursor = pred[cursor][0][0]
            chain.reverse()
            collapsed.append((cursor, target, ct))
            chains.append((cursor, target, chain))
    require(sorted(collapsed) == sorted(tuple(e) for e in empty_edges), "Inserted DAG changes original edges")
    require(used_insertions == additions, "Unused inserted operation")

    lin_by, lout_by, depth_by = {}, {}, {}
    per_node, n_b1, n_b2 = {}, 0, 0
    for name in order:
        _, op, d, _ = by_name[name]
        require(op in RULES, f"Unknown operator: {op}")
        expected_d, lower, a, b = RULES[op]
        require(type(d) is int, f"Non-integer level cost: {name}")
        require(d > 0 if op == "Modswitch" else d == expected_d, f"Wrong level cost: {name}")
        level = min((lout_by[p] for p, _ in pred[name]), default=l_init)
        require(lower <= level <= l_max, f"Input outside valid range: {name}")
        multiplier = 1
        if op in ("Bootstrap1", "Bootstrap2"):
            require(len(pred[name]) == 1, f"Bootstrap arity: {name}")
            ct = pred[name][0][1]
            if op == "Bootstrap2":
                require(ct in (8, 16), f"Bootstrap2 requires #ct 8 or 16: {name}")
                multiplier = ct // 2
                n_b2 += multiplier
                out = l_max - 1
            else:
                multiplier = ct
                n_b1 += multiplier
                out = l_max
        else:
            out = level - d
        require(0 <= out <= l_max, f"Output outside valid range: {name}")
        lin_by[name], lout_by[name] = level, out
        depth_by[name] = max((depth_by[p] for p, _ in pred[name]), default=0) + (0 if op in INSERTED else d)
        per_node[name] = (Decimal(a) * level + Decimal(b)) * multiplier

    prefixes = {}
    allowed = {(), ("Bootstrap1",), ("Bootstrap2",), ("Modswitch",),
               ("Bootstrap1", "Modswitch"), ("Bootstrap2", "Modswitch")}
    placements = []
    for origin, target, chain in chains:
        ops = tuple(by_name[n][1] for n in chain)
        require(ops in allowed, f"Illegal operator chain: {origin} -> {target}")
        prefix = []
        for name in chain:
            op = by_name[name][1]
            prefix.append((op, lout_by[name] if op == "Modswitch" else None))
            key = (origin, tuple(prefix))
            require(key not in prefixes or prefixes[key] == name, "Identical inserted prefixes must share one node")
            prefixes[key] = name
        if chain:
            placements.append({"from": origin, "to": target, "inserted_nodes": chain})
    total = sum(per_node.values(), Decimal(0))
    depth = max(depth_by.values())
    budget = n_b1 * l_max + n_b2 * (l_max - 1) + l_init
    require(budget > 0, "Zero level budget")
    return {
        "latency_decimal_ms": str(total), "n_b1": n_b1, "n_b2": n_b2,
        "n_bootstrap": n_b1 + n_b2, "depth": depth, "budget": budget,
        "utilisation": depth / budget, "l_in": lin_by, "l_out": lout_by,
        "edge_levels": [{"from": u, "to": v, "ciphertexts": ct, "level": lout_by[u]} for u, v, ct in edges],
        "node_latency_decimal_ms": {n: str(v) for n, v in per_node.items()},
        "placement_chains": placements, "structural_and_level_checks_passed": True,
    }
