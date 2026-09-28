"""Original shared-refresh formulation solved by the OR-Tools CP-SAT engine.

The model decides edge delivery levels and refresh choices jointly. Sharing is
charged per producer and refresh type, rather than per consumer edge. Costs
are exact integers in units of 0.0001 ms. See docs/s2-method.md for equivalence
to the handout's six insertion chains and the scope of optimality claims.
"""

from dataclasses import dataclass
from decimal import Decimal
import math
import time

from ortools.sat.python import cp_model

from .audit import RULES, require
from .s2_placement import check_original

SCALE = 10000
METHOD = "shared-refresh-cp-sat-v1"


def scaled(value):
    """Convert a decimal latency to an exact integer, rejecting precision loss."""
    value = Decimal(str(value)) * SCALE
    require(value == value.to_integral_value(), "Latency exceeds supported precision")
    return int(value)


@dataclass
class Formulation:
    """Variables retained for extraction and independent reconstruction."""
    model: object
    input_levels: dict
    output_levels: dict
    deliveries: dict
    refreshes: dict
    activations: dict
    objective: object
    safe_absolute_bound: int


def formulate(nodes, edges, l_init, baseline=None):
    """Construct the complete finite-domain model for a fixed original block.

    baseline, when present, is an independently checked feasible placement. It
    supplies a non-worsening upper bound and hints, never a fabricated result.
    """
    require(type(l_init) is int and 0 <= l_init <= 14, "Invalid input level")
    order, pred, succ = check_original(nodes, edges)
    model = cp_model.CpModel()
    lin, lout, deliveries, refreshes, activations = {}, {}, {}, {}, {}
    terms, magnitude = [], 0
    for name, op, depth, _ in nodes:
        _, lower, a, b = RULES[op]
        lin[name] = model.new_int_var(lower, 14, f"in_{name}")
        lout[name] = model.new_int_var(0, 14, f"out_{name}")
        model.add(lout[name] == lin[name] - depth)
        if not pred[name]:
            model.add(lin[name] == l_init)
        ai, bi = scaled(a), scaled(b)
        terms.append(ai * lin[name] + bi)
        magnitude += abs(ai) * 14 + abs(bi)

    for u, v, ct in edges:
        key = (u, v)
        t = model.new_int_var(0, 14, f"delivery_{u}_{v}")
        choices = [model.new_bool_var(f"mode{k}_{u}_{v}") for k in range(3)]
        model.add_exactly_one(choices)
        model.add(t <= lout[u]).only_enforce_if(choices[0])
        model.add(t <= 13).only_enforce_if(choices[2])
        if ct not in (8, 16):
            model.add(choices[2] == 0)
        deliveries[key], refreshes[key] = t, choices

    for name in order:
        if pred[name]:
            model.add_min_equality(lin[name], [deliveries[u, name] for u, _ in pred[name]])
        if not succ[name]:
            continue
        ct = succ[name][0][1]
        for mode, per_unit in ((1, "1040.15"), (2, "1293.13")):
            if mode == 2 and ct not in (8, 16):
                continue
            active = model.new_bool_var(f"shared_B{mode}_{name}")
            model.add_max_equality(active, [refreshes[name, v][mode] for v, _ in succ[name]])
            activations[name, mode] = active
            cost = scaled(per_unit) * (ct if mode == 1 else ct // 2)
            terms.append(cost * active)
            magnitude += cost
    require(magnitude < 2**53, "Objective magnitude exceeds exact-double reporting range")
    objective = sum(terms)
    model.minimize(objective)
    if baseline is not None:
        model.add(objective <= scaled(baseline["latency_decimal_ms"]))
        by_edge = {(e["from"], e["to"]): e["level"] for e in baseline["edge_levels"]}
        chains = {(p["from"], p["to"]): p["inserted_nodes"] for p in baseline["placement_chains"]}
        node_ops = baseline["node_ops"]
        active_hints = {k: 0 for k in activations}
        for name in lin:
            model.add_hint(lin[name], baseline["l_in"][name])
            model.add_hint(lout[name], baseline["l_out"][name])
        for u, v, _ in edges:
            chain = chains.get((u, v), [])
            first = node_ops[chain[0]] if chain else None
            mode = {"Bootstrap1": 1, "Bootstrap2": 2}.get(first, 0)
            parent = chain[-1] if chain else u
            model.add_hint(deliveries[u, v], by_edge[parent, v])
            for k, var in enumerate(refreshes[u, v]):
                model.add_hint(var, int(k == mode))
            if mode:
                active_hints[u, mode] = 1
        for key, var in activations.items():
            model.add_hint(var, active_hints[key])
    problem = Formulation(model, lin, lout, deliveries, refreshes, activations, objective, magnitude)
    error = model.validate()
    require(not error, f"Invalid CP-SAT model: {error}")
    return problem


def solve_placement(nodes, edges, l_init, *, time_limit_seconds=60.0, workers=1,
                    seed=5491, baseline=None):
    """Run a bounded CPU search and return truthful status, bounds and decisions."""
    require(math.isfinite(time_limit_seconds) and time_limit_seconds > 0, "Invalid search time limit")
    require(type(workers) is int and workers > 0, "Invalid worker count")
    require(type(seed) is int and seed >= 0, "Invalid random seed")
    start = time.perf_counter()
    p = formulate(nodes, edges, l_init, baseline)
    build_seconds = time.perf_counter() - start
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit_seconds
    solver.parameters.num_search_workers = workers
    solver.parameters.random_seed = seed
    solver.parameters.relative_gap_limit = 0.0
    solver.parameters.absolute_gap_limit = 0.0
    start = time.perf_counter()
    status = solver.solve(p.model)
    elapsed = time.perf_counter() - start
    result = {
        "method": METHOD, "status": solver.status_name(status), "l_init": l_init, "l_max": 14,
        "cost_scale_per_ms": SCALE, "model_build_wall_seconds": build_seconds,
        "solve_wall_seconds": elapsed, "solver_reported_wall_seconds": solver.wall_time,
        "solver_reported_user_seconds": solver.user_time,
        "best_bound_scaled": solver.best_objective_bound,
        "branches": solver.num_branches, "conflicts": solver.num_conflicts,
        "model_variables": len(p.model.proto.variables), "model_constraints": len(p.model.proto.constraints),
        "objective_safe_absolute_bound": p.safe_absolute_bound,
        "settings": {"time_limit_seconds": time_limit_seconds, "workers": workers, "seed": seed,
                     "relative_gap_limit": 0, "absolute_gap_limit": 0,
                     "validated_baseline_hint_and_upper_bound": baseline is not None},
        "response_stats": solver.response_stats(),
        "has_solution": status in (cp_model.OPTIMAL, cp_model.FEASIBLE),
    }
    if not result["has_solution"]:
        return result
    obj = solver.value(p.objective)
    result.update({
        "objective_scaled": obj,
        "objective_decimal_ms": str(Decimal(obj) / SCALE),
        "relative_gap": max(0.0, (obj - solver.best_objective_bound) / max(1, abs(obj))),
        "optimality_proven_for_formulation": status == cp_model.OPTIMAL,
        "original_input_levels": {n: solver.value(v) for n, v in p.input_levels.items()},
        "original_output_levels": {n: solver.value(v) for n, v in p.output_levels.items()},
        "edge_decisions": [
            {"from": u, "to": v, "ciphertexts": ct,
             "refresh": next(k for k, var in enumerate(p.refreshes[u, v]) if solver.value(var)),
             "delivered_level": solver.value(p.deliveries[u, v])} for u, v, ct in edges
        ],
        "shared_refreshes": [{"after": n, "type": mode} for (n, mode), var in p.activations.items()
                             if solver.value(var)],
    })
    return result
