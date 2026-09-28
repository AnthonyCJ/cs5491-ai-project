"""Independent exhaustive search on tiny graphs, never used for course blocks.

This oracle does not call CP-SAT, formulate(), or the DAG reconstructor. It
enumerates all legal edge modes and delivered levels in topological order,
charging each producer's distinct refresh types once. Necessary input-domain
pruning discards an edge level only when its consumer could never accept it.
"""

from decimal import Decimal
from itertools import product
import time

from .audit import RULES, require
from .s2_placement import check_original


def tiny_examples():
    """Small hand-checkable cases covering costs, fan-out, merges and #ct changes."""
    return [
        {"id": "one-cipher-refresh", "level": 0,
         "nodes": [("s", "Identity", 0, "input"), ("a", "Mul", 1, "multiply")],
         "edges": [("s", "a", 1)], "hand_cost_ms": "1040.6355"},
        {"id": "paired-refresh", "level": 0,
         "nodes": [("s", "Identity", 0, "input"), ("a", "Mul", 1, "multiply")],
         "edges": [("s", "a", 8)], "hand_cost_ms": "5173.0055"},
        {"id": "shared-refresh-and-modswitch", "level": 0,
         "nodes": [("s", "Identity", 0, "input"), ("a", "Mul", 1, "left"), ("b", "Mul", 1, "right")],
         "edges": [("s", "a", 8), ("s", "b", 8)], "hand_cost_ms": "5173.4910"},
        {"id": "minimum-level-merge", "level": 2,
         "nodes": [("s", "Identity", 0, "input"), ("a", "Mul", 1, "branch"), ("b", "Add", 0, "merge")],
         "edges": [("s", "a", 8), ("s", "b", 8), ("a", "b", 8)], "hand_cost_ms": "0.5234"},
        {"id": "shared-refresh-different-drops", "level": 0,
         "nodes": [("s", "Identity", 0, "input"), ("a", "Mul", 1, "left"), ("b", "PCMM3", 2, "right")],
         "edges": [("s", "a", 4), ("s", "b", 4)], "hand_cost_ms": "6628.8055"},
        {"id": "refresh-after-ciphertext-change", "level": 0,
         "nodes": [("s", "Identity", 0, "input"), ("a", "Conjugate", 0, "halve"), ("b", "Mul", 1, "multiply")],
         "edges": [("s", "a", 8), ("a", "b", 4)], "hand_cost_ms": "4162.7555"},
    ]


def enumerate_tiny(nodes, edges, l_init):
    """Enumerate the full finite choice space for at most four nodes/three edges."""
    require(len(nodes) <= 4 and len(edges) <= 3, "Exhaustive oracle is restricted to tiny examples")
    order, pred, succ = check_original(nodes, edges)
    by_name = {n[0]: n for n in nodes}
    best, complete, partial = None, 0, 0
    start = time.perf_counter()

    def visit(index, deliveries, cost):
        nonlocal best, complete, partial
        partial += 1
        if index == len(order):
            complete += 1
            best = cost if best is None else min(best, cost)
            return
        name = order[index]
        _, op, depth, _ = by_name[name]
        level = min((deliveries[u, name] for u, _ in pred[name]), default=l_init)
        _, lower, a, b = RULES[op]
        if not lower <= level <= 14 or level < depth:
            return
        out = level - depth
        node_cost = Decimal(a) * level + Decimal(b)
        choices = []
        for target, ct in succ[name]:
            low = RULES[by_name[target][1]][1]
            edge_options = [(0, t) for t in range(low, out + 1)]
            edge_options += [(1, t) for t in range(low, 15)]
            if ct in (8, 16):
                edge_options += [(2, t) for t in range(low, 14)]
            choices.append(edge_options)
        for selection in product(*choices):
            next_deliveries = dict(deliveries)
            used = {mode for mode, _ in selection}
            refresh_cost = Decimal(0)
            if succ[name]:
                ct = succ[name][0][1]
                if 1 in used:
                    refresh_cost += ct * Decimal("1040.15")
                if 2 in used:
                    refresh_cost += (ct // 2) * Decimal("1293.13")
            for (target, _), (_, target_level) in zip(succ[name], selection):
                next_deliveries[name, target] = target_level
            visit(index + 1, next_deliveries, cost + node_cost + refresh_cost)

    visit(0, {}, Decimal(0))
    return {"minimum_decimal_ms": None if best is None else str(best),
            "complete_placements": complete, "partial_states": partial,
            "enumeration_wall_seconds": time.perf_counter() - start}
