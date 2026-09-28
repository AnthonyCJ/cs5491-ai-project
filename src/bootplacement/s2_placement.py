"""Canonical insertion chains and reconstruction of the original computation DAG."""

from collections import defaultdict
from graphlib import TopologicalSorter

from .audit import INSERTED, RULES, require


def check_original(nodes, edges):
    """Validate a fixed single-input block before constructing a search model."""
    by_name = {n[0]: n for n in nodes}
    require(len(by_name) == len(nodes) and bool(nodes), "Duplicate or empty original graph")
    pred, succ = defaultdict(list), defaultdict(list)
    seen = set()
    for name, op, depth, _ in nodes:
        require(op in RULES and op not in INSERTED, f"Invalid original operator: {name}")
        require(type(depth) is int and depth == RULES[op][0], f"Invalid original depth: {name}")
    for u, v, ct in edges:
        require(u in by_name and v in by_name, "Unknown original endpoint")
        require(type(ct) is int and ct > 0, "Invalid original ciphertext count")
        require((u, v) not in seen, "Duplicate original edge")
        seen.add((u, v))
        pred[v].append((u, ct))
        succ[u].append((v, ct))
    order = list(TopologicalSorter({n: [u for u, _ in pred[n]] for n in by_name}).static_order())
    sources = [n for n in order if not pred[n]]
    require(len(sources) == 1, "Expected one block input")
    require(by_name[sources[0]][1:3] == ("Identity", 0) or list(by_name[sources[0]][1:3]) == ["Identity", 0],
            "Block input must be Identity")
    for n in by_name:
        require(len({ct for _, ct in succ[n]}) <= 1, f"Inconsistent output tensor: {n}")
    return order, pred, succ


def reconstruct(nodes, edges, decisions, original_output_levels):
    """Build one real node per shared prefix, preserving all original operators.

    Each edge chooses refresh mode 0/1/2 and a delivered level. A strict drop
    from that mode's available level becomes a Modswitch. Equal levels need
    no Modswitch. Thus the representation covers exactly the six legal chains.
    """
    check_original(nodes, edges)
    original = {n[0] for n in nodes}
    indexed = {(d["from"], d["to"]): d for d in decisions}
    require(len(indexed) == len(decisions) == len(edges), "Decision coverage mismatch")
    require(set(indexed) == {(u, v) for u, v, _ in edges}, "Decision edges differ from original graph")
    require(set(original_output_levels) == original, "Original output level coverage mismatch")
    placed_nodes = [tuple(n) for n in nodes]
    inserted = {}
    placed_edges = {}

    def connect(u, v, ct):
        require((u, v) not in placed_edges or placed_edges[u, v] == ct, "Conflicting shared tensor")
        placed_edges[u, v] = ct

    def insert(key, name, op, depth, description):
        require(name not in original, "Inserted name conflicts with original node")
        if key not in inserted:
            inserted[key] = name
            placed_nodes.append((name, op, depth, description))
        return inserted[key]

    for u, v, ct in edges:
        d = indexed[u, v]
        mode, level = d["refresh"], d["delivered_level"]
        require(type(mode) is int and mode in (0, 1, 2), "Invalid refresh mode")
        require(type(level) is int and 0 <= level <= 14, "Invalid delivered level")
        require(d["ciphertexts"] == ct, "Decision changes ciphertext count")
        available = original_output_levels[u]
        require(type(available) is int and 0 <= available <= 14, "Invalid original output level")
        parent = u
        if mode:
            require(mode != 2 or ct in (8, 16), "B2 requires 8 or 16 ciphertexts")
            parent = insert((u, mode), f"s2_B{mode}_{u}", f"Bootstrap{mode}", 0,
                            f"Shared B{mode} after {u}")
            connect(u, parent, ct)
            available = 15 - mode
        require(level <= available, "Chain attempts to increase level without refresh")
        if level < available:
            down = insert((u, mode, level), f"s2_M{mode}_{level}_{u}", "Modswitch", available - level,
                          f"Level {available} to {level}")
            connect(parent, down, ct)
            parent = down
        connect(parent, v, ct)
    return placed_nodes, [(u, v, ct) for (u, v), ct in placed_edges.items()]
